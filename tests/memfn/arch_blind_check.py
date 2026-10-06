#!/usr/bin/env python3
"""C4, the arch-blindness detector ([MEMFN], integration.md §10.4, §17.5).

Usage: arch_blind_check.py ROOT ALLOWLIST ALLOW_FLOOR [--census]

pcrec carries no architecture knowledge (D146/D147, Q12's refinement): the
kit owns every ISA choice, and pcrec sends one bit. C4 makes that a red test.

WHAT IT SCANS, per scope (the design's three):
  code   every non-markdown file under src/, cli/ and lib/;
  doc    the *.md files inside those three (CLAUDE.md among them);
  tests  everything under tests/ EXCEPT tests/memfn/ (the checks of the kit
         define the vocabulary and so spell it; their exemption is stated
         here, and memfn/ itself is EXEMPT by design: it is where the
         architecture knowledge lives).
Matching is CASE-INSENSITIVE and the boundary is any non-alphanumeric
character (so `MF_VEC_SSE2` is seen: `\\b` fails between `_` and a letter,
rev 2's slip). A match preceded by a backslash is a hex escape (`\\x86` in a
.rxt subject) and is excluded by rule.

THE NINE CLASSES (§10.4): 1 ISA names and levels; 2 predefined arch macros;
3 intrinsics and vector types; 4 intrinsic headers; 5 targeting; 6 arch
nouns; 7 kit-identity compares (form_id, mf_kit_version, mf_token_name, the
--isa= token; CODE scope only: tests and docs may discuss one); 8 pcrec reading kit OUTPUT (a function that holds an mf_sink
and string-searches); 9 the include graph (src/, cli/ and lib/ include
memfn/include/memfn.h and no other kit file).

THE ALLOWLIST (ALLOWLIST, counted at birth, D107's shape): one row per
(scope, path, class) with the hit COUNT it is allowed. More hits than allowed
is a new hit and FAILS; FEWER is a stale row and FAILS too (lower it in the
same change), so the list only descends. ALLOW_FLOOR is the K35 floor on the
allowlist's TOTAL count, passed in by the caller as a literal that shares no
source with the TSV.

THE CONTROLS (docs/dev/learnings.md §3):
  - positive, one per class, planted in a SCRATCH tree and required to hit
    in that class. Classes 1-6 take their plants from the compiler's own
    installation (§17.5): ISA macros are what `cc -dM -E` declares under an
    ISA flag and not at baseline; intrinsic names, vector types and header
    names are scraped from the compiler's resource include directory; arch
    nouns come from `-dumpmachine`, `uname -m` and the defined arch macros.
    The CLAIM is narrowed as the design narrows it: the plant is not chosen
    by the author of the regex; it is not complete and not box-independent
    (gcc-16 on the Mac and gcc on ubuntubudu declare different sets). The
    plant count per class is printed per box and a class with none is RED.
    A plant the regex misses is a FAIL: widen the class.
    Classes 7-9 are structural shapes and take SYNTHETIC plants (author-
    chosen, said so in the output).
  - negative: hex escapes in a .rxt subject and in a C string must not hit.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

passed = 0
failed = 0


def ok(msg):
    global passed
    passed += 1
    print('PASS: ' + msg)


def bad(msg):
    global failed
    failed += 1
    print('FAIL: ' + msg)


# A boundary is any non-alphanumeric, so `_` separates (the fix of rev 2's
# `\b` slip); a backslash before the match is a hex escape (`\x86`).
L = r'(?<![A-Za-z0-9\\])'
R = r'(?![A-Za-z0-9])'

CLASSES = {
    1: ('isa-name', re.compile(
        L + r'(?:sse[0-9]*(?:\.[0-9])?|ssse3|avx[0-9a-z]*|neon|sve2?|mmx|amx[a-z0-9_]*|'
        r'x86-64-v[1-4]|armv[0-9][a-z0-9.+-]*|bmi[12]?|fma[34]|pclmul[a-z]*|f16c|'
        r'movbe|lzcnt|popcnt|cx16|xsave[a-z]*|rdrand|rdseed|fsgsbase|sha-?ni|vnni|'
        r'altivec|rvv|aes(?:ni)?|crypto|sha[23]|fp16[a-z0-9_]*|dotprod|crc32[a-z0-9_]*|i8mm|bf16|'
        r'pmull|sm[34])' + R, re.I)),
    2: ('arch-macro', re.compile(
        L + r'(?:__(?:[A-Z0-9_]*_)?(?:SSE[A-Z0-9_]*|AVX[A-Z0-9_]*|NEON[A-Z0-9_]*|'
        r'SVE[A-Z0-9_]*|ARM_[A-Z0-9_]+|ARM[0-9]*_?[A-Z0-9_]*|AARCH64[A-Z0-9_]*|'
        r'X86_64[A-Z0-9_]*|I386|AMD64|BMI[A-Z0-9_]*|FMA[A-Z0-9_]*|AES[A-Z0-9_]*|'
        r'PCLMUL[A-Z0-9_]*|POPCNT[A-Z0-9_]*|LZCNT[A-Z0-9_]*|F16C[A-Z0-9_]*|'
        r'MOVBE[A-Z0-9_]*|XSAVE[A-Z0-9_]*|RDRND[A-Z0-9_]*|RDSEED[A-Z0-9_]*|'
        r'CRC32[A-Z0-9_]*|SHA[A-Z0-9_]*|MMX[A-Z0-9_]*|AMX[A-Z0-9_]*|CX16[A-Z0-9_]*|'
        r'CLFLUSH[A-Z0-9_]*|FSGSBASE[A-Z0-9_]*|VPCLMULQDQ[A-Z0-9_]*|VAES[A-Z0-9_]*|'
        r'GCC_HAVE_SYNC_COMPARE_AND_SWAP_16)|_M_(?:X64|ARM64|IX86))' + R, re.I)),
    3: ('intrinsic', re.compile(
        L + r'(?:_mm[0-9]*_\w+|__m(?:64|128|256|512)[a-z]*|v(?:ld|st)[1-4]q?_\w+|'
        r'vqtbl[0-9]*q?_\w+|v[a-z][a-z0-9]*q?(?:_[a-z]+)?_[sufp](?:8|16|32|64)|[a-z]+[0-9]+x[0-9]+(?:x[0-9]+)?_t|'
        r'__builtin_ia32_\w+|_pext_u[0-9]+|_pdep_u[0-9]+|_tzcnt_u[0-9]+|_lzcnt_u[0-9]+|'
        r'_mulx_u[0-9]+|_bzhi_u[0-9]+)', re.I)),
    4: ('intrin-header', re.compile(
        L + r'(?:[a-z0-9_]*intrin[0-9a-z_]*\.h|arm_[a-z0-9_]+\.h|[a-z0-9_]*cpuid[a-z0-9_]*\.h|'
        r'immintrin|x86intrin|sys/auxv\.h|asm/hwcap\.h)', re.I)),
    5: ('targeting', re.compile(
        r'(?:target\s*\(\s*"|-march=|-mcpu=|-mtune=|-m(?:avx|sse|bmi|neon|sve|popcnt|fma)[a-z0-9.]*|'
        r'__builtin_cpu_(?:supports|is|init)|getauxval|' + L + r'HWCAP2?(?:_\w+)?|hw\.optional|' +
        L + r'cpuid' + R + r')', re.I)),
    6: ('arch-noun', re.compile(
        L + r'(?:x86(?:_64)?|amd64|aarch64|arm64|pshufb|movemask|skylake|haswell|icelake|'
        r'sapphire\s*rapids|zen[2-5]|neoverse|cortex-a[0-9]+)' + R, re.I)),
    # 7: kit identity compared: a compare operator or function and an operand
    # naming form_id / mf_kit_version( / mf_token_name( / the --isa= token.
    7: ('kit-identity', re.compile(
        r'(?:(?:strn?cmp|memcmp|==|!=)[^;\n]{0,80}(?:form_id|mf_kit_version\s*\(|mf_token_name\s*\(|--isa=)|'
        r'(?:form_id|mf_kit_version\s*\(|mf_token_name\s*\(|--isa=)[^;\n]{0,80}(?:strn?cmp|memcmp|==|!=))')),
}
# 8 and 9 are structural (a function-level read-back; an include path).
KIT_INCLUDE = re.compile(r'^\s*#\s*include\s*"([^"]*memfn/[^"]*)"')
STR_SEARCH = re.compile(r'\b(?:strstr|strchr|strrchr|strcmp|strncmp|memchr|memcmp|strlen|strtok|sscanf)\s*\(')
KIT_HEADER_OK = 'memfn/include/memfn.h'

CODE_DIRS = ('src', 'cli', 'lib')
SKIP_SUFFIX = ('.o', '.a', '.png', '.gz', '.bin', '.pyc')


def read_text(path):
    try:
        with open(path, 'rb') as fh:
            data = fh.read()
    except OSError:
        return None
    if b'\0' in data:
        return None
    return data.decode('utf-8', errors='replace')


def files_of(root, rel_dirs, exclude=()):
    out = []
    for d in rel_dirs:
        for dp, dns, fns in os.walk(os.path.join(root, d)):
            rel_dp = os.path.relpath(dp, root)
            dns[:] = sorted(x for x in dns if os.path.join(rel_dp, x) not in exclude)
            for fn in sorted(fns):
                if fn.endswith(SKIP_SUFFIX):
                    continue
                out.append(os.path.relpath(os.path.join(dp, fn), root))
    return out


def strip_c(text):
    """C source with comments, string and char literals blanked (newlines kept)."""
    def blank(m):
        return re.sub(r'[^\n]', ' ', m.group(0))
    return re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'',
                  blank, text, flags=re.S)


def class8_functions(text):
    """Top-level function bodies that hold an mf_sink and string-search."""
    code = strip_c(text)
    hits, depth, start, head = [], 0, 0, 0
    for i, ch in enumerate(code):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                header = code[head:start]
                body = code[start:i + 1]
                if '(' in header and 'mf_sink' in code[head:i + 1] and STR_SEARCH.search(body):
                    hits.append(code.count('\n', 0, head + len(header) - len(header.lstrip())) + 1)
                head = i + 1
        elif ch == ';' and depth == 0:
            head = i + 1
    return hits


def scan_tree(root):
    """[(scope, path, line, cls, excerpt)] for the whole tree under ROOT."""
    hits = []
    code_files = files_of(root, CODE_DIRS)
    for rel in code_files:
        scope = 'doc' if rel.endswith('.md') else 'code'
        text = read_text(os.path.join(root, rel))
        if text is None:
            continue
        scan_text(hits, scope, rel, text, structural=(scope == 'code'))
    for rel in files_of(root, ('tests',), exclude=('tests/memfn',)):
        text = read_text(os.path.join(root, rel))
        if text is not None:
            scan_text(hits, 'tests', rel, text, structural=False)
    return hits


def scan_text(hits, scope, rel, text, structural):
    for n, line in enumerate(text.split('\n'), 1):
        for cls, (_name, rx) in CLASSES.items():
            if cls == 7 and scope != 'code':
                continue      # a compare in code; tests and docs may discuss one
            m = rx.search(line)
            if m:
                hits.append((scope, rel, n, cls, line.strip()[:60]))
        if structural:
            m = KIT_INCLUDE.match(line)
            if m and KIT_HEADER_OK not in os.path.normpath(m.group(1)):
                hits.append((scope, rel, n, 9, line.strip()[:60]))
    if structural and rel.endswith(('.c', '.h')):
        for n in class8_functions(text):
            hits.append((scope, rel, n, 8, '<function holding an mf_sink that string-searches>'))


def counts_of(hits):
    c = {}
    for scope, rel, _n, cls, _ex in hits:
        c[(scope, rel, cls)] = c.get((scope, rel, cls), 0) + 1
    return c


def read_allowlist(path):
    allow, total = {}, 0
    with open(path, encoding='utf-8') as fh:
        for n, raw in enumerate(fh, 1):
            line = raw.rstrip('\n')
            if not line.strip() or line.startswith('#'):
                continue
            f = line.split('\t')
            if len(f) != 5:
                bad('%s:%d: %d fields, want 5 (scope, path, class, count, reason)'
                    % (path, n, len(f)))
                continue
            key = (f[0], f[1], int(f[2]))
            if key in allow:
                bad('%s:%d: duplicate allowlist row %r' % (path, n, key))
            allow[key] = int(f[3])
            total += int(f[3])
    return allow, total


# -- the plants, derived from the compiler's own installation (§17.5) ---------

ISA_FLAGSETS = [['-march=native'], ['-mcpu=native'], ['-msse4.2'], ['-mavx2'],
                ['-mavx512f'], ['-mbmi2'], ['-march=x86-64-v2'], ['-march=x86-64-v3'],
                ['-march=armv8.2-a+sve'], ['-march=armv8-a+crc+crypto']]


def cc_run(cc, args, src=None):
    try:
        r = subprocess.run([cc] + args, input=src, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout if r.returncode == 0 else None


def macros(cc, flags):
    out = cc_run(cc, flags + ['-dM', '-E', '-x', 'c', '-'], '')
    if out is None:
        return None
    return {m.group(1) for m in re.finditer(r'^#define\s+(\S+)', out, re.M)}


def evenly(items, k):
    items = sorted(set(items))
    if len(items) <= k:
        return items
    step = len(items) / float(k)
    return [items[int(i * step)] for i in range(k)]


def derive_plants(cc):
    """{class: [plant text]} from compiler `cc`; also {class: why-empty}."""
    plants = {k: [] for k in range(1, 7)}
    notes = {}
    base = macros(cc, [])
    if base is None:
        return plants, {k: 'compiler %r does not run' % cc for k in plants}
    isa_macros, accepted = set(), []
    for fl in ISA_FLAGSETS:
        m = macros(cc, fl)
        if m is None:
            continue
        accepted.append(fl[0])
        isa_macros |= {x for x in m - base if x.startswith('__')}
    notes['flags'] = accepted
    plants[2] = evenly(isa_macros, 8)
    stems = set()
    for x in isa_macros:
        s = re.sub(r'^__(?:ARM_FEATURE_)?|__$', '', x)
        if re.fullmatch(r'[A-Z][A-Z0-9_]*', s) and len(s) >= 3:
            stems.add(s.split('_')[0] if s.startswith(('SSE', 'AVX')) else s)
    plants[1] = evenly(stems, 6)
    inc = (cc_run(cc, ['-print-file-name=include']) or '').strip()
    names, types, headers = [], [], []
    if inc and os.path.isdir(inc):
        for fn in sorted(os.listdir(inc)):
            if re.search(r'intrin|arm_|cpuid', fn) and fn.endswith('.h'):
                headers.append(fn)
                txt = read_text(os.path.join(inc, fn)) or ''
                names += re.findall(r'^\s*(_mm\w+|v[a-z]\w*_[a-z0-9]\w*)\s*\(', txt, re.M)
                types += re.findall(r'typedef[^;]*\s(__m\d+\w*|\w+x\d+_t)\s*;', txt)
    plants[3] = evenly(names, 5) + evenly(types, 3)
    plants[4] = evenly(headers, 4)
    # targeting: the flags the compiler ACCEPTED (the candidate list is ours),
    # and the cpu builtin when the compiler takes it
    plants[5] = ['%s' % f for f in accepted[:4]]
    if cc_run(cc, ['-fsyntax-only', '-x', 'c', '-'],
              'int f(void){return __builtin_cpu_supports("sse2");}\n') is not None:
        plants[5].append('__builtin_cpu_supports')
    nouns = set()
    dm = (cc_run(cc, ['-dumpmachine']) or '').strip().split('-')[0]
    if dm:
        nouns.add(dm)
    um = subprocess.run(['uname', '-m'], capture_output=True, text=True).stdout.strip()
    if um:
        nouns.add(um)
    for mac, noun in (('__aarch64__', 'aarch64'), ('__arm64__', 'arm64'), ('__x86_64__', 'x86_64'),
                      ('__amd64__', 'amd64')):
        if mac in base:
            nouns.add(noun)
    plants[6] = sorted(nouns)
    return plants, notes


SYNTH = {
    7: ['    if (strcmp(form->form_id, "swar") == 0) return 1;',
        '    if (mf_token_name(tok) == want) return 1;',
        '    if (opt_isa == NULL || strncmp(arg, "--isa=", 6) == 0) return 1;'],
    8: ['void render_it(mf_sink *s)\n{\n    if (strstr(s->buf, "memchr")) return;\n}'],
    9: ['#include "../../memfn/src/kit.h"', '#include "../../memfn/src/options.def"'],
}


def plant_lines(cls, p):
    if cls == 2:
        return '#if defined(%s)' % p
    if cls == 3:
        return '    x = %s(a);' % p
    if cls == 4:
        return '#include <%s>' % p
    return '/* %s */' % p


def scratch_controls(cc, tmpbase):
    """Positive controls (per class) and the negative control, in a scratch tree."""
    plants, notes = derive_plants(cc)
    print('plants derived from %r (box %s): flags accepted %s'
          % (cc, os.uname().machine, ' '.join(notes.get('flags', [])) or 'none'))
    root = tempfile.mkdtemp(prefix='c4scratch.', dir=tmpbase)
    try:
        os.makedirs(os.path.join(root, 'src/gen'))
        os.makedirs(os.path.join(root, 'tests/x'))
        expect = []        # (path, line, cls)
        for cls in range(1, 10):
            ps = plants.get(cls) or SYNTH.get(cls, [])
            synthetic = cls >= 7
            if not ps:
                bad('class %d (%s): ZERO plants derivable on this box (%s): the class is '
                    'unreachable here, not passed' % (cls, CLASSES[cls][0] if cls in CLASSES else
                                                       ('reads-kit-output' if cls == 8 else 'include-graph'),
                                                       notes.get(cls, 'compiler declares none')))
                continue
            rel = 'src/gen/plant_c%d.c' % cls
            lines, where = [], []
            for p in ps:
                text = p if synthetic else plant_lines(cls, p)
                where.append((len(lines) + 1, p))
                lines.append(text)
                if '\n' in text:
                    lines.extend([''] * 0)
            body = '\n'.join(lines) + '\n'
            # one plant per physical line start; multi-line synthetics are one plant
            with open(os.path.join(root, rel), 'w') as fh:
                fh.write(body)
            expect.append((cls, rel, ps, synthetic))
        # negative control: a hex escape is not an ISA word
        with open(os.path.join(root, 'tests/x/neg.rxt'), 'w') as fh:
            fh.write('ms 0 "\\x86\\xc5\\x86" 0 3\n')
        with open(os.path.join(root, 'src/gen/neg.c'), 'w') as fh:
            fh.write('static const char *s = "\\x86\\xAV";\n')
        hits = scan_tree(root)
        for cls, rel, ps, synthetic in expect:
            got = {n for (_s, r, n, c, _e) in hits if r == rel and c == cls}
            lines_of = []
            ln = 1
            for p in ps:
                text = p if synthetic else plant_lines(cls, p)
                lines_of.append((ln, p))
                ln += text.count('\n') + 1
            missed = [p for (ln_, p) in lines_of
                      if not any(ln_ <= g < ln_ + (p.count('\n') + 1 if synthetic else 1) for g in got)]
            tag = 'synthetic (author-chosen)' if synthetic else 'compiler-derived'
            nm = CLASSES[cls][0] if cls in CLASSES else ('reads-kit-output' if cls == 8 else 'include-graph')
            if missed:
                bad('class %d (%s): %d of %d %s plants MISSED by the regex: %s'
                    % (cls, nm, len(missed), len(ps), tag, '; '.join(m.replace('\n', ' ') for m in missed[:4])))
            else:
                ok('class %d (%s): %d/%d %s plants hit' % (cls, nm, len(ps), len(ps), tag))
        neg = [h for h in hits if h[1] in ('tests/x/neg.rxt', 'src/gen/neg.c')]
        if neg:
            bad('negative control: a hex escape was read as vocabulary: %r' % (neg[:2],))
        else:
            ok('negative control: hex escapes (\\x86 in a .rxt subject and a C string) are not hits')
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    census = '--census' in sys.argv
    if len(args) != 3:
        print('usage: arch_blind_check.py ROOT ALLOWLIST ALLOW_FLOOR [--census]', file=sys.stderr)
        return 2
    root, apath, afloor = args[0], args[1], int(args[2])
    hits = scan_tree(root)
    c = counts_of(hits)
    if census:
        for (scope, rel, cls), n in sorted(c.items()):
            print('%s\t%s\t%d\t%d\t' % (scope, rel, cls, n))
        return 0
    allow, atotal = read_allowlist(apath)
    by_scope = {}
    for (scope, _r, _c), n in c.items():
        by_scope[scope] = by_scope.get(scope, 0) + n
    print('scan: %d hits in %d (scope, file, class) groups (%s); allowlist %d rows, %d hits allowed'
          % (len(hits), len(c), ', '.join('%s %d' % kv for kv in sorted(by_scope.items())),
             len(allow), atotal))
    if atotal < afloor:
        bad('the allowlist holds %d hits, below its K35 floor of %d: a row was lowered or '
            'deleted without the floor being lowered in the same change' % (atotal, afloor))
    else:
        ok('allowlist total %d >= K35 floor %d' % (atotal, afloor))
    newhits = 0
    for key in sorted(c):
        scope, rel, cls = key
        have, want = c[key], allow.get(key, 0)
        if have > want:
            newhits += 1
            ex = [h for h in hits if (h[0], h[1], h[3]) == key][want]
            bad('NEW architecture vocabulary: %s %s class %d (%s): %d hit(s), %d allowed; '
                'first new at line %d: %r' % (scope, rel, cls,
                                              CLASSES[cls][0] if cls in CLASSES else
                                              ('reads-kit-output' if cls == 8 else 'include-graph'),
                                              have, want, ex[2], ex[4]))
    for key in sorted(allow):
        if c.get(key, 0) < allow[key]:
            bad('STALE allowlist row %r: %d hit(s) allowed, %d found: lower the row (the list '
                'only descends)' % (key, allow[key], c.get(key, 0)))
    if not newhits:
        ok('no architecture vocabulary outside the allowlist (%d hits all allowed)' % len(hits))
    tmpbase = os.environ.get('TMPDIR')
    cc = os.environ.get('CC', 'gcc')
    if shutil.which(cc) is None:
        bad('compiler %r not found: the plants cannot be derived' % cc)
    else:
        scratch_controls(cc, tmpbase)
    print('checks passed: %d' % passed)
    print('checks failed: %d' % failed)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
