#!/usr/bin/env python3
"""tests/memfn/simd_floor_check.py -- C18, THE FLOOR RULE, its four legs and
the guard lint, plus C9-x86 ([MEMFN] R4e' batch 1, request R-13;
docs/design/memfn/integration.md §R4.9.2.3's floor rule and §R4.9.8's C18
and C9-x86 rows, as amended by D155). Driven by run_simd_floor.sh
(`make test-memfn-simdfloor`).

THE POPULATION, counted by pcrec's own compile: every corpus pattern (plus
named witnesses, one per batch-1 route bin) compiled at -fno-memfn-simd (OFF)
and -fmemfn-simd (ON), at the default engine and at --engine=vm. A MOVER is a
(pattern, engine) whose ON artifact differs from its OFF artifact; the SIMD
FUNCs of a mover are the FUNC selectors whose body holds a level arm. Movers
and SIMD FUNCs are printed with a literal floor (K35). On every mover:

  (a) PREPROCESSED-EQUAL off-target: `gcc -E -P` of ON and OFF at
      -mgeneral-regs-only AND at -mno-sse2 are byte-equal.
  (b) ONE REPLACED CALL PER SIMD FUNC on-target: at each level's test_march
      (mf_levels()), the -E -P diff OFF -> ON deletes exactly one line per
      SIMD FUNC, each `    return <fn>__body(<args>);`, and nothing else.
  (c) SOURCE-LEVEL INSERTION-ONLY: the raw diff OFF -> ON deletes no line
      but the two stamp lines the switch moves (`<P>_MEMFN_FORMS`,
      `<P>_SIMD_GUARDED_BYTES`: the named filter), and the inserted lines'
      bytes equal the ON artifact's `<P>_SIMD_GUARDED_BYTES` exactly (pcrec's
      sink counts what the kit bracketed; this script counts the diff: every
      inserted byte is inside a bracket, and nothing bracketed is missing).
  (d) NO DIRECTIVE IN A BODY EXCEPT THE SELECTOR'S: routing_shape.py
      (D155 addendum 1's rule, sharing no code with the kit) over the ON
      text.
  guard lint: every `#if`/`#elif` line the diff inserts is `#if`/`#elif`
      followed by a guard string from mf_levels(), and every inserted
      `#include` names a level's header.
  C9-x86: every mover's ON artifact compiles -Wall -Wextra -Werror at
      x86-64, x86-64-v2, sandybridge, x86-64-v3, x86-64-v4 and
      -mgeneral-regs-only; at -O0 its object defines the live arm's helper
      (`<fn>__w16` from x86-64 on, `<fn>__w32` from x86-64-v3 on, neither at
      -mgeneral-regs-only nor a w32 one at sandybridge, AVX without AVX2),
      read with nm.

Independent controls: the preprocessor and the compiler (a, b, C9), pcrec's
own stamp (c), and a rule read from the ruling's text (d). The kit's
`moved`, FORMS and trace are never read to find a mover. Prints
`checks passed: N` / `checks failed: N`.
"""
import argparse
import concurrent.futures
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TREE, 'scripts'))
sys.path.insert(0, HERE)
import emit_sweep as es  # noqa: E402
import routing_shape  # noqa: E402

MOVERS_FLOOR = 39      # (pattern, engine) movers, corpus + named: 44 measured at w16 (R-13), ~90%
SIMD_FUNC_FLOOR = 39   # SIMD FUNCs over the movers: 44 measured, ~90%
LEVELS_FLOOR = 2       # mf_levels() rows: w16, w32 (R-13)
NAMED = [
    ('mod-i (DFA, ASSIGN)', '(?i)cat', []),
    ('union-select (DFA)', '(?i)union.*?select.*?from', []),
    ('union-select (no-DFA, ON_MISS)', '(?i)union.*?select.*?from', ['--engine=vm']),
    ('no-DFA ON_MISS', '(?i)\\d+cat', ['--engine=vm']),
    ('VM hybrid', '(?i)(a|b)+cat', []),
]
STAMP_MOVES = re.compile(r'^#define \w+_(MEMFN_FORMS|SIMD_GUARDED_BYTES) ')
GUARDED = re.compile(r'^#define \w+_SIMD_GUARDED_BYTES (0x[0-9a-f]+)ULL$', re.M)
C9_MARCH = ['-march=x86-64', '-march=x86-64-v2', '-march=sandybridge', '-march=x86-64-v3',
            '-march=x86-64-v4', '-mgeneral-regs-only']


def sh(cmd, timeout=120, **kw):
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout, **kw)
    except subprocess.TimeoutExpired:
        return None


def diff_lines(a, b):
    """(deleted, inserted) lines of a -> b, by `diff` (an outside tool)."""
    with tempfile.NamedTemporaryFile('w', delete=False, dir=os.environ.get('TMPDIR')) as fa, \
         tempfile.NamedTemporaryFile('w', delete=False, dir=os.environ.get('TMPDIR')) as fb:
        fa.write(a)
        fb.write(b)
    r = subprocess.run(['diff', '--unchanged-line-format=', '--old-line-format=-%L',
                        '--new-line-format=+%L', fa.name, fb.name], capture_output=True)
    os.unlink(fa.name)
    os.unlink(fb.name)
    out = r.stdout.decode('utf-8', 'surrogateescape').split('\n')
    dele = [l[1:] for l in out if l.startswith('-')]
    ins = [l[1:] for l in out if l.startswith('+')]
    return dele, ins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pcrec', required=True)
    ap.add_argument('--levels', required=True, help='the simd_levels binary')
    ap.add_argument('--every', type=int, default=1)
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    passed, failed = [0], []

    def ok(msg=None):
        passed[0] += 1
        if msg:
            print('PASS: ' + msg)

    def bad(msg):
        failed.append(msg)
        print('FAIL: ' + msg)

    lv = [l.split('\t') for l in subprocess.run([a.levels], capture_output=True, text=True,
                                                check=True).stdout.splitlines()]
    guards = {l[1] for l in lv}
    headers = {l[2] for l in lv}
    print('levels: %s' % ', '.join('%s (vw %s, %s)' % (l[5], l[3], l[4]) for l in lv))
    if len(lv) >= LEVELS_FLOOR:
        ok('mf_levels(): %d levels (floor %d)' % (len(lv), LEVELS_FLOOR))
    else:
        bad('mf_levels(): %d levels < floor %d' % (len(lv), LEVELS_FLOOR))
    marches = [l[4] for l in lv]

    corpus = es.enumerate_corpus(a.pcrec, TREE, 30)
    pats = sorted({p for _, _, p in corpus})
    pats = [p for i, p in enumerate(pats) if i % a.every == 0]
    pop = [('named:' + n, p, x) for n, p, x in NAMED]
    pop += [('corpus', p, x) for p in pats for x in ([], ['--engine=vm'])]
    print('== C18/C9: %d population cells (%d corpus patterns x 2 engines, %d named)'
          % (len(pop), len(pats), len(NAMED)))
    work = tempfile.mkdtemp(prefix='simdfloor.', dir=os.environ.get('TMPDIR'))

    def emit(p, extra, flag, d):
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, 'a.c')
        r = sh([a.pcrec, '-p', 'rx', '--features', 'all', flag] + extra + ['-o', out]
               + es._pattern_argv(a.pcrec, p), 60)
        if r is None or r.returncode:
            return None
        return out

    def one(job):
        idx, (key, p, extra) = job
        base = os.path.join(work, str(idx))
        off = emit(p, extra, '-fno-memfn-simd', base + '/off')
        on = emit(p, extra, '-fmemfn-simd', base + '/on')
        rec = {'key': key, 'p': p, 'extra': extra, 'issues': [], 'mover': False, 'nfunc': 0}
        if off is None or on is None:
            if (off is None) != (on is None):
                rec['issues'].append('ON and OFF disagree on refusing')
            subprocess.run(['rm', '-rf', base])
            return rec
        toff = open(off, encoding='utf-8', errors='surrogateescape').read()
        ton = open(on, encoding='utf-8', errors='surrogateescape').read()
        hoff = open(off[:-1] + 'h', 'rb').read()
        hon = open(on[:-1] + 'h', 'rb').read()
        if hoff != hon:
            rec['issues'].append('the .h moved under -fmemfn-simd (a level guard in the header?)')
        if toff == ton:
            subprocess.run(['rm', '-rf', base])
            return rec
        rec['mover'] = True
        # the SIMD FUNCs: selectors whose body holds a level arm
        simd_fns = re.findall(r'^static inline size_t (\w+)\([^)]*\)\n\{\n#if ', ton, re.M)
        rec['nfunc'] = len(simd_fns)
        if not simd_fns:
            rec['issues'].append('a mover with no SIMD FUNC selector')
        # (c) raw insertion-only, and the bytes are the bracketed bytes
        dele, ins = diff_lines(toff, ton)
        stray = [l for l in dele if not STAMP_MOVES.match(l)]
        if stray:
            rec['issues'].append('(c) %d deleted line(s), first %r' % (len(stray), stray[0][:80]))
        ins_code = [l for l in ins if not STAMP_MOVES.match(l)]
        m = GUARDED.search(ton)
        nbytes = sum(len(l.encode('utf-8', 'surrogateescape')) + 1 for l in ins_code)
        if not m or int(m.group(1), 16) != nbytes:
            rec['issues'].append('(c) inserted %d bytes, SIMD_GUARDED_BYTES %s'
                                 % (nbytes, m.group(1) if m else 'absent'))
        # guard lint
        for l in ins_code:
            mm = re.match(r'^#\s*(if|elif)\s+(.*)$', l)
            if mm and mm.group(2) not in guards:
                rec['issues'].append('guard lint: %r is no levels.def guard' % l[:100])
            mi = re.match(r'^#\s*include\s*<([^>]*)>$', l)
            if mi and mi.group(1) not in headers:
                rec['issues'].append('guard lint: %r is no level header' % l)
            if re.match(r'^#\s*(ifdef|ifndef|define|undef|pragma)\b', l):
                rec['issues'].append('guard lint: %r inserted' % l)
        # (d) the routing rule over the ON text
        nf, why = routing_shape.check(ton)
        for w in why:
            rec['issues'].append('(d) ' + w)
        # (a) off-target and (b) on-target, by the preprocessor
        def pp(path, flags):
            r = sh(['gcc', '-E', '-P'] + flags + [path], 60, cwd=os.path.dirname(path))
            return r.stdout.decode('utf-8', 'surrogateescape') if r and r.returncode == 0 else None
        for flags in (['-mgeneral-regs-only'], ['-mno-sse2']):
            x, y = pp(off, flags), pp(on, flags)
            if x is None or y is None or x != y:
                rec['issues'].append('(a) %s: preprocessed text differs' % flags[0])
        for march in marches:
            x, y = pp(off, ['-march=' + march]), pp(on, ['-march=' + march])
            if x is None or y is None:
                rec['issues'].append('(b) %s: preprocessing failed' % march)
                continue
            dele, _ = diff_lines(x, y)
            okdel = [l for l in dele
                     if re.match(r'^    return (\w+)__body\(.*\);$', l)
                     and re.match(r'^    return (\w+)__body', l).group(1) in simd_fns]
            if len(dele) != len(simd_fns) or len(okdel) != len(dele):
                rec['issues'].append('(b) -march=%s: %d deleted line(s) for %d SIMD FUNC(s): %r'
                                     % (march, len(dele), len(simd_fns), dele[:3]))
        # C9-x86: compile clean at every macro set; the live arm by nm at -O0
        for march in C9_MARCH:
            r = sh(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-c', march, '-o', base + '/c9.o', on],
                   120, cwd=os.path.dirname(on))
            if r is None or r.returncode:
                rec['issues'].append('C9 %s: does not compile -Werror: %s'
                                     % (march, (r.stderr.decode()[-300:] if r else 'timeout')))
                continue
            r = sh(['gcc', '-O0', '-c', march, '-o', base + '/c9o0.o', on], 120,
                   cwd=os.path.dirname(on))
            syms = subprocess.run(['nm', base + '/c9o0.o'], capture_output=True,
                                  text=True).stdout if r and r.returncode == 0 else ''
            w16 = bool(re.search(r' t \w+__w16$', syms, re.M))
            w32 = bool(re.search(r' t \w+__w32$', syms, re.M))
            want16 = march not in ('-mgeneral-regs-only',)
            want32 = march in ('-march=x86-64-v3', '-march=x86-64-v4') and '__w32(' in ton
            has16 = '__w16(' in ton
            if (has16 and w16 != want16) or w32 != want32:
                rec['issues'].append('C9 %s: live arms w16=%s w32=%s, expected w16=%s w32=%s'
                                     % (march, w16, w32, want16 and has16, want32))
        subprocess.run(['rm', '-rf', base])
        return rec

    movers = funcs = 0
    named_movers = set()
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for rec in ex.map(one, enumerate(pop)):
            for i in rec['issues']:
                bad('%s %r %s: %s' % (rec['key'], rec['p'][:50], ' '.join(rec['extra']), i))
            if rec['mover']:
                movers += 1
                funcs += rec['nfunc']
                if rec['key'].startswith('named:'):
                    named_movers.add(rec['key'])
                if not rec['issues']:
                    ok()
    subprocess.run(['rm', '-rf', work])
    print('movers: %d (pattern, engine) cells, %d SIMD FUNCs' % (movers, funcs))
    for n, _, _ in NAMED:
        if 'named:' + n in named_movers:
            ok('named witness %s is a mover' % n)
        else:
            bad('named witness %s is NOT a mover (its bin is unreached)' % n)
    if movers >= MOVERS_FLOOR and funcs >= SIMD_FUNC_FLOOR:
        ok('population: %d movers (floor %d), %d SIMD FUNCs (floor %d)'
           % (movers, MOVERS_FLOOR, funcs, SIMD_FUNC_FLOOR))
    else:
        bad('population: %d movers / %d SIMD FUNCs under floors %d / %d (K35)'
            % (movers, funcs, MOVERS_FLOOR, SIMD_FUNC_FLOOR))
    print('checks passed: %d' % passed[0])
    print('checks failed: %d' % len(failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
