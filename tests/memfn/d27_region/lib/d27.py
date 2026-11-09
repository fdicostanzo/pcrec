#!/usr/bin/env python3
"""d27region: spec-first (D27) tests of pcrec's CPU-target scaffolding.

Written from the promise only: docs/spec/match_api.md §6.3.10 (¶1-¶15),
§10.7, §6.3.12, docs/spec/tuning.md §2.43, docs/spec/limits.md §8.3 and
docs/spec/cli.md §1.24/§2.16. Every check carries the paragraph it holds the
compiler to. Run through d27/run.sh; prints one PASS/FAIL line per check and
the two totals. Exit 0 iff every check passed.

Environment: PCREC (default <cell>/build/pcrec), D27_OUT (default
/var/tmp/pcrec-pcrec/scratch/d27region/run), D27_JOBS (default 4),
D27_CONTROL=1 (also run the deliberately wrong expectation as an ordinary
check, so the run must report it failed), D27_QUICK=1 (gcc -O2 only).
"""
import difflib
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

LIB = os.path.dirname(os.path.abspath(__file__))
D27 = os.path.dirname(LIB)
CASES = os.path.join(D27, 'cases')
CELL = os.environ.get('D27_ROOT') or os.path.dirname(D27)   # landed: the tree's root (run.sh)
PCREC = os.environ.get('PCREC', os.path.join(CELL, 'build', 'pcrec'))
OUT = os.environ.get('D27_OUT', '/var/tmp/pcrec-pcrec/scratch/d27region/run')
JOBS = int(os.environ.get('D27_JOBS', '4'))
CONTROL = os.environ.get('D27_CONTROL') == '1'
QUICK = os.environ.get('D27_QUICK') == '1'
TMO = os.environ.get('TIMEOUT_BIN') or shutil.which('gnutimeout') or shutil.which('timeout')
CONSUMER = os.path.join(CASES, 'consumer.c')
STUBINC = os.path.join(CASES, 'stubinc')


lock = threading.Lock()
results = []


def check(ok, cid, cite, desc, detail=''):
    with lock:
        results.append((bool(ok), cid, cite, desc, detail))
    return bool(ok)


def run(cmd, secs=60, cwd=None):
    p = subprocess.run([TMO, '-k', '5', str(secs)] + [str(c) for c in cmd],
                       capture_output=True, cwd=cwd)
    return p.returncode, p.stdout.decode('latin1'), p.stderr.decode('latin1')


def tail(s, n=600):
    s = s.strip()
    return s if len(s) <= n else '...' + s[-n:]


# ---------------------------------------------------------------- cases

class Pat:
    def __init__(self, cols):
        self.id, opts, self.kind, self.pcrec, py, pieces = cols
        self.opts = [] if opts == '-' else opts.split()
        self.py = self.pcrec if py == '=' else py
        self.pieces = [p.encode('latin1').decode('unicode_escape').encode('latin1')
                       for p in pieces.split(',')]
        self.rx = re.compile(self.py.encode('latin1'))


def load_patterns():
    pats = []
    with open(os.path.join(CASES, 'patterns.tsv')) as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            pats.append(Pat(line.split('\t')))
    return pats


def gen_subjects(pat, seed):
    """My own alphabet: the pattern's pieces in random case, cut short,
    mutated, planted at offsets around the 16/32-byte block edges and at the
    subject's end, in fillers holding NUL, newline and high bytes."""
    rnd = random.Random(seed)
    filler = b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 -\n\x00\x80\xdf\xff'
    letters = bytes(sorted(set(b''.join(pat.pieces))))

    def fill(n):
        return bytes(rnd.choice(filler + letters * 2) for _ in range(n))

    def variant(p):
        v = bytes((c ^ 0x20) if (chr(c).isalpha() and rnd.random() < 0.5) else c for c in p)
        r = rnd.random()
        if r < 0.15 and len(v) > 1:
            return v[:-1]                         # cut short
        if r < 0.3 and len(v) > 1:
            i = rnd.randrange(len(v))
            return v[:i] + bytes([rnd.choice(filler)]) + v[i + 1:]   # one byte off
        return v

    subs = [b'']
    for p in pat.pieces:
        subs += [p, p.upper(), p.lower(), p + b'\n', b'\n' + p]
    for p in pat.pieces:
        for off in (0, 1, 7, 14, 15, 16, 17, 30, 31, 32, 33, 47, 63, 64):
            for extra in (0, 1, 5, 40):
                if rnd.random() < 0.35:
                    subs.append(fill(off) + variant(p) + fill(extra))
        subs.append(fill(rnd.randrange(0, 90)) + p)            # at the very end
        subs.append(p[:1] * 3 + p)                              # repeated first byte
    for _ in range(60):
        parts = []
        while sum(map(len, parts)) < rnd.randrange(0, 120):
            parts.append(variant(rnd.choice(pat.pieces)) if rnd.random() < 0.4 else fill(rnd.randrange(1, 20)))
        subs.append(b''.join(parts))
    out, seen = [], set()
    for s in subs:
        s = s[:400]
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def expected_answers(pat, subs):
    lines = []
    for i, s in enumerate(subs):
        for pos in range(len(s) + 1):
            m = pat.rx.search(s, pos)
            lines.append('%d %d %s' % (i, pos, '1 %d %d' % m.span() if m else '0 -1 -1'))
    return lines


def expected_consumer(subs):
    lines = []
    for i, s in enumerate(subs):
        q = s.count(b'q')
        nul = s.find(b'\x00')
        libc = min(len(s) if nul < 0 else nul, 255)
        lines.append('%d %d %d %d %d' % (i, q, q, libc, s.find(b'q')))
    return lines


# ---------------------------------------------------------------- listing

class Target:
    def __init__(self, row):
        self.name = row['name']
        self.family = row['family']
        self.features = row['features']

    @property
    def stamp(self):        # match_api.md §6.3.10¶14
        return '%s:%s' % (self.family or 'none', self.name)

    @property
    def tag(self):
        return re.sub(r'[^a-z0-9]', '', self.name.lower())


def read_listing():
    rc, out, err = run([PCREC, '--list-cpu-targets'])
    cite = 'cli.md §2.16¶1'
    check(rc == 0, 'list/rc', cite, '--list-cpu-targets exits 0', tail(err))
    lines = out.splitlines()
    head = None
    rows = []
    for l in lines:
        if l.startswith('#kind') or l.startswith('kind\t'):
            head = l.lstrip('#').split('\t')
        elif l and not l.startswith('#'):
            rows.append(l.split('\t'))
    want = ['kind', 'name', 'family', 'host', 'defaults', 'features', 'doc']
    check(head is not None and all(c in head for c in want), 'list/columns', cite,
          'the header row names kind,name,family,host,defaults,features,doc', str(head))
    recs = [dict(zip(head, r + [''] * (len(head) - len(r)))) for r in rows] if head else []
    kinds = [r['kind'] for r in recs]
    check(kinds == sorted(kinds, key=lambda k: k != 'family'), 'list/families-first', cite,
          'family rows come first', ' '.join(kinds))
    hosts = [r for r in recs if r['host'] == 'host']
    check(len(hosts) <= 1, 'list/one-host', cite, 'at most one row is marked host', str(len(hosts)))
    host = hosts[0] if hosts else None
    if platform.machine() == 'x86_64':
        # match_api.md §6.3.10¶14's example and cli.md §1.24¶3: on an amd64
        # host -fmemfn-simd alone is -fmemfn-simd=x86-64.
        check(host is not None and host['kind'] == 'family' and host['name'] == 'amd64'
              and host['defaults'] == 'x86-64', 'list/host-amd64',
              'cli.md §2.16¶1, §1.24¶3', 'this x86-64 build marks family amd64 host, defaults x86-64',
              str(host))
    for r in recs:
        if r['kind'] == 'target':
            check(r['family'] == '' or r['family'] in [x['name'] for x in recs if x['kind'] == 'family'],
                  'list/target-family/%s' % r['name'], cite, 'a target names a listed family or none', r['family'])
    for extra, what in ((['--pattern', 'x'], 'a pattern'), (['-o', os.path.join(OUT, 'x.c')], '-o')):
        rc2, o2, e2 = run([PCREC, '--list-cpu-targets'] + extra)
        check(rc2 != 0, 'list/refuses-%s' % ('pattern' if 'x' in extra else 'o'), cite,
              '--list-cpu-targets refuses %s' % what, 'rc=%d %s' % (rc2, tail(e2, 200)))
    targets = [Target(r) for r in recs if r['kind'] == 'target']
    portable = [t for t in targets if t.family == '']
    hostfam = host['name'] if host else None
    return targets, portable, hostfam, host


# ---------------------------------------------------------------- artifact text

def strip_c(text):
    """Comments and string/char literals blanked, newlines kept."""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if text.startswith('/*', i):
            j = text.find('*/', i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r'[^\n]', ' ', text[i:j]))
            i = j
        elif text.startswith('//', i):
            j = text.find('\n', i)
            j = n if j < 0 else j
            out.append(' ' * (j - i))
            i = j
        elif c in '"\'':
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == '\\' else 1
            j = min(j + 1, n)
            out.append(c + ' ' * (j - i - 2) + c if j - i >= 2 else text[i:j])
            i = j
        else:
            out.append(c)
            i += 1
    return ''.join(out)


def parse_stamps(text, P):
    d = {}
    for i, l in enumerate(text.split('\n')):
        m = re.match(r'#define (%s_[A-Z0-9_]+) (.*)$' % re.escape(P), l)
        if m:
            v = re.sub(r'/\*.*\*/', '', m.group(2)).strip()
            d.setdefault(m.group(1)[len(P) + 1:], []).append((i, v))
    return d


def unq(v):
    return v[1:-1] if v.startswith('"') and v.endswith('"') else v


class Text:
    """Where the target's text sits in one .c (match_api.md §6.3.10¶15)."""

    def __init__(self, path, P):
        self.path = path
        self.P = P
        self.text = open(path, encoding='latin1').read()
        self.lines = self.text.split('\n')
        self.code = strip_c(self.text).split('\n')
        L = self.lines
        self.includes = [i for i, l in enumerate(L) if re.match(r'\s*#\s*include\b', l)]
        self.errors = [i for i, l in enumerate(L) if re.match(r'\s*#\s*error\b', l)]
        self.push = [i for i, l in enumerate(L) if re.match(r'\s*#\s*pragma\b.*\bpush', l)]
        self.pop = [i for i, l in enumerate(L) if re.match(r'\s*#\s*pragma\b.*\bpop', l)]
        self.pragmas = [i for i, l in enumerate(L) if re.match(r'\s*#\s*pragma\b', l)]
        self.stamps = parse_stamps(self.text, P)
        # the guard: the #if directly above the first #error
        self.guard = None
        if self.errors:
            e = self.errors[0]
            if e > 0 and re.match(r'\s*#\s*if\b', L[e - 1]):
                end = e + 1 if e + 1 < len(L) and re.match(r'\s*#\s*endif', L[e + 1]) else None
                self.guard = (e - 1, e, end)
        # the region: the first push pragma's enclosing #if .. the last pop's #endif
        self.region = None
        if self.push and self.pop:
            o = self.push[0]
            while o > 0 and re.match(r'\s*#\s*(if|else|pragma)', L[o - 1]):
                o -= 1
            c = self.pop[-1]
            while c + 1 < len(L) and re.match(r'\s*#\s*(else|endif|pragma)', L[c + 1]):
                c += 1
            self.region = (o, c)

    def first_brace(self):
        for i, l in enumerate(self.code):
            if '{' in l and not l.lstrip().startswith('#'):
                return i
        return None

    def toplevel_after(self, k):
        """Top-level declarator lines after line k (not directives/blank/braces)."""
        out = []
        for i in range(k + 1, len(self.code)):
            l = self.code[i]
            if l and not l[0].isspace() and not l.startswith('#') and not l.startswith(('}', '{')) and l.strip():
                out.append((i, self.lines[i]))
        return out


def target_text_diff(off, on, P):
    """Lines of `on` (a family target's .c) beyond `off` (its SIMD-off .c).
    Allowed: the target's own text, which is all directives (the guard's
    #if/#error/#endif, the region's pragmas, #include lines; ¶15), blank
    lines, and the two stamp lines whose VALUE moves (¶14, ¶8)."""
    a = off.split('\n')
    b = on.split('\n')
    stamp = re.compile(r'#define %s_(TARGETS|SIMD_GUARDED_BYTES) ' % re.escape(P))
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    bad, ins = [], 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            continue
        for l in a[i1:i2]:
            if not stamp.match(l):
                bad.append('-' + l)
        for l in b[j1:j2]:
            if stamp.match(l):
                continue
            if l.lstrip().startswith('#') or not l.strip():
                ins += len(l.encode('latin1')) + 1
            else:
                bad.append('+' + l)
    return bad, ins


# ---------------------------------------------------------------- generation

def gen(dirpath, prefix, opts, pat, extra=(), emit_main=False):
    os.makedirs(dirpath, exist_ok=True)
    out = os.path.join(dirpath, prefix + '.c')
    cmd = [PCREC, '-p', prefix] + pat.opts + list(opts) + list(extra) + \
        (['--emit-main'] if emit_main else []) + ['-o', out, '--pattern', pat.pcrec]
    rc, o, e = run(cmd, 120)
    return rc, out, e


def cfg_opts(t):
    """A canonical target's spelling: the default artifact for the portable
    target, -fmemfn-simd=NAME otherwise."""
    return [] if t.family == '' else ['-fmemfn-simd=%s' % t.name]


# ---------------------------------------------------------------- stamp + text checks

def check_artifact_text(cid, path, P, t, pat, emit_main):
    """¶1 ¶8 ¶12 ¶14 ¶15 on one artifact's .c."""
    T = Text(path, P)
    st = T.stamps
    c = cid
    # ¶14: once, value FAMILY:TARGET, after _COMPOUND
    tv = st.get('TARGETS', [])
    check(len(tv) == 1, c + '/targets-once', 'match_api.md §6.3.10¶14', '<PREFIX>_TARGETS appears exactly once', str(tv))
    if tv:
        check(unq(tv[0][1]) == t.stamp, c + '/targets-value', 'match_api.md §6.3.10¶14',
              '<PREFIX>_TARGETS is %s' % t.stamp, tv[0][1])
        cp = st.get('COMPOUND', [])
        check(cp and cp[0][0] < tv[0][0], c + '/targets-after-compound', 'match_api.md §6.3.10¶14',
              '<PREFIX>_TARGETS is written after <PREFIX>_COMPOUND', 'COMPOUND@%s TARGETS@%d' % (cp[:1], tv[0][0]))
    others = [k for k in re.findall(r'#define (\w+_TARGETS) ', T.text) if k != P + '_TARGETS']
    check(not others, c + '/parts-no-targets', 'match_api.md §6.3.10¶14',
          'no other *_TARGETS macro (a compound\'s parts carry none)', ' '.join(others))
    cp = st.get('COMPOUND', [])
    if cp:
        want_cmp = (unq(cp[0][1]) != 'none') if pat.kind == 'compound' else (unq(cp[0][1]) == 'none')
        check(want_cmp, c + '/compound-kind', 'match_api.md §6.3.12¶1, §3.7¶2',
              'the case\'s compound class (%s)' % pat.kind, cp[0][1])
    # ¶1: the five in order; ¶8 GUARDED directly after LIBC; ¶12 MEASURES directly after FINDINGS
    order = ['RUN_WORDS', 'MEMFN_FORMS', 'MEMFN_LIBC', 'SIMD_GUARDED_BYTES', 'FINDINGS', 'MEASURES']
    pos = [st.get(k, [(None, None)])[0][0] for k in order]
    ok = all(p is not None for p in pos) and pos == sorted(pos) and all(len(st.get(k, [])) == 1 for k in order)
    check(ok, c + '/stamp-order', 'match_api.md §6.3.10¶1, ¶12',
          'RUN_WORDS, MEMFN_FORMS, MEMFN_LIBC, SIMD_GUARDED_BYTES, FINDINGS, MEASURES once each, in order',
          str(dict(zip(order, pos))))
    if ok:
        check(pos[3] == pos[2] + 1, c + '/guarded-after-libc', 'match_api.md §6.3.10¶8',
              'SIMD_GUARDED_BYTES directly after MEMFN_LIBC', str(pos))
        check(pos[5] == pos[4] + 1, c + '/measures-after-findings', 'match_api.md §6.3.10¶12',
              'MEASURES right after FINDINGS', str(pos))
    g = st.get('SIMD_GUARDED_BYTES', [(0, '')])[0][1]
    gm = re.fullmatch(r'0x([0-9a-f]{16})ULL', g, re.I)
    check(gm, c + '/guarded-format', 'match_api.md §6.3.10¶8',
          'SIMD_GUARDED_BYTES is 16 hex digits with ULL', g)
    gval = int(gm.group(1), 16) if gm else None
    forms = unq(st.get('MEMFN_FORMS', [(0, '""')])[0][1])
    libc = unq(st.get('MEMFN_LIBC', [(0, '""')])[0][1])
    check(libc == 'none' or (libc.split(',') == sorted(set(libc.split(','))) and ' ' not in libc and libc),
          c + '/libc-format', 'match_api.md §6.3.10¶5', 'MEMFN_LIBC is "none" or sorted, distinct, comma-joined, no space', libc)
    if t.family == '':
        check(gval == 0, c + '/guarded-zero', 'match_api.md §6.3.10¶9, limits.md §8.3¶3',
              'zero at the portable target', g)
        check(forms == 'none', c + '/forms-none-portable', 'match_api.md §6.3.10¶4',
              'MEMFN_FORMS "none" at the default', forms)
        check(T.guard is None and T.region is None and not T.pragmas and not T.errors,
              c + '/no-target-text', 'match_api.md §6.3.10¶15 (last sentence)',
              'no guard, region or pragma at the portable target',
              'errors=%s pragmas=%s' % (T.errors, T.pragmas))
        return T, gval, forms, libc
    # a family target
    check(gval is not None and gval > 0, c + '/guarded-nonzero', 'match_api.md §6.3.10¶9, limits.md §8.3¶3',
          'nonzero at a target with a family', g)
    ntok = 0 if forms == 'none' else len(forms.split(','))
    # limits.md §8.3¶3: target text <= 700, each vrun row <= 2,400 (w16) / 2,800 (w32).
    # Ids are opaque (¶4), so each FORMS token is allowed both rows' bounds.
    bound = 700 + ntok * (2400 + 2800)
    check(gval is not None and gval <= bound, c + '/guarded-bound', 'limits.md §8.3¶3',
          'SIMD_GUARDED_BYTES <= 700 + 5,200 per MEMFN_FORMS token (%d)' % bound, str(gval))
    if t.family == 'amd64' and t.name == 'x86-64':
        check('w32' not in forms, c + '/no-w32-at-baseline', 'match_api.md §6.3.10¶4',
              'the 32-byte level is x86-64-v3\'s, never the baseline\'s', forms)
    if t.family != 'amd64':
        check(forms == 'none', c + '/forms-none-other-family', 'tuning.md §2.43¶3a',
              'no level is admitted outside amd64 (16-byte: x86-64, 32-byte: x86-64-v3)', forms)
    # ¶15 the guard
    check(T.guard is not None, c + '/guard-present', 'match_api.md §6.3.10¶15',
          'the family guard (#if .. #error) is present', 'errors=%s' % T.errors)
    if T.guard:
        gi, ge, gend = T.guard
        check(T.includes and gi < T.includes[0] and (gend or ge) < T.includes[0],
              c + '/guard-before-includes', 'match_api.md §6.3.10¶15',
              'the guard is at file scope ahead of every #include',
              'guard@%d includes@%s' % (gi, T.includes[:3]))
        m = re.match(r'\s*#\s*if\s+!\s*\((.*)\)\s*$', T.lines[gi])
        cond = m.group(1) if m else T.lines[gi]
        check(m and cond in T.lines[ge], c + '/guard-names-condition', 'match_api.md §6.3.10¶15',
              'the #error names the guard\'s condition', T.lines[ge][:160])
        check(not T.code[gi].startswith((' ', '\t')) and all(not T.code[k].strip() or T.code[k].lstrip().startswith('#')
                                                             for k in range(0, gi)),
              c + '/guard-file-scope', 'match_api.md §6.3.10¶15', 'nothing but directives precede the guard', '')
    # ¶15 the region
    no_region = (t.family == 'arm64' and t.name == 'armv8-a')   # ¶15: "(armv8-a)" has no region
    if no_region:
        check(T.region is None and not T.pragmas, c + '/no-region', 'match_api.md §6.3.10¶15, tuning.md §2.43¶3a',
              'armv8-a (the family baseline) carries the guard alone, no region', 'pragmas@%s' % T.pragmas)
        return T, gval, forms, libc
    check(T.region is not None, c + '/region-present', 'match_api.md §6.3.10¶15',
          'a region is present for %s' % t.name, 'push=%s pop=%s' % (T.push, T.pop))
    if not T.region:
        return T, gval, forms, libc
    ro, rc_ = T.region
    inside = [i for i in T.includes if ro < i < rc_]
    check(not inside, c + '/region-holds-no-include', 'match_api.md §6.3.10¶15',
          'the region holds no #include',
          '; '.join('line %d: %s' % (i + 1, T.lines[i].strip()) for i in inside[:4]))
    fb = T.first_brace()
    check(fb is None or ro < fb, c + '/region-before-first-function', 'match_api.md §6.3.10¶15',
          'the region opens before the artifact\'s first function',
          'open@%d first{@%s' % (ro + 1, None if fb is None else fb + 1))
    info = [i for i, l in enumerate(T.lines) if re.match(r'const struct \w+ %s_info\b' % re.escape(P.lower()), l)]
    check(info and ro < info[0] < rc_, c + '/region-closes-after-info', 'match_api.md §6.3.10¶15',
          'rx_info sits inside the region (closed after rx_info)',
          'info@%s close@%d' % ([i + 1 for i in info], rc_ + 1))
    after = T.toplevel_after(rc_)
    if emit_main:
        mains = [i for i, l in enumerate(T.lines) if re.match(r'int main\s*\(', l)]
        check(mains and mains[0] > rc_, c + '/main-after-region', 'match_api.md §6.3.10¶15',
              'an --emit-main main() is after the region closes', 'main@%s close@%d' % ([m + 1 for m in mains], rc_ + 1))
        check(all(re.match(r'int main\s*\(', l) for i, l in after), c + '/only-main-after-region',
              'match_api.md §6.3.10¶15', 'nothing but main() after the region', str(after[:3]))
    else:
        check(not after, c + '/nothing-after-region', 'match_api.md §6.3.10¶15',
              'no definition after the region closes', str(after[:3]))
    # ¶15: the region is the only CPU-specific text; no CPU #if in the text (¶4, §2.43¶3a)
    cpu_if = [i for i, l in enumerate(T.lines)
              if re.match(r'\s*#\s*(if|elif|ifdef|ifndef)\b.*__(AVX|SSE|x86_64|aarch64|ARM_NEON|BMI)', l)
              and not (T.guard and i == T.guard[0])]
    check(not cpu_if, c + '/no-cpu-if', 'match_api.md §6.3.10¶4, tuning.md §2.43¶3a',
          'the text carries no CPU #if (the guard aside)', '; '.join(T.lines[i].strip() for i in cpu_if[:3]))
    return T, gval, forms, libc


def nm_undefined(obj):
    rc, o, e = run(['nm', '-u', obj])
    return set(l.split()[-1] for l in o.splitlines() if l.strip())


def check_libc_census(cid, path, libc, tmpdir):
    """¶5: a SOURCE-LEVEL inventory, comments/strings excluded; constant
    1-8 byte memcpy excluded; data objects not listed. Held against the
    -O0 -fno-builtin object's undefined symbols (¶7's own method),
    excluding compiler-inserted __stack_chk_fail and data objects; memcpy
    is compared one-sided (a constant-size one is legitimately unlisted)."""
    obj = os.path.join(tmpdir, os.path.basename(path) + '.census.o')
    rc, o, e = run(['gcc', '-O0', '-fno-builtin', '-c', path, '-o', obj], 120)
    if not check(rc == 0, cid + '/census-compile', 'match_api.md §6.3.10¶7', 'gcc -O0 -fno-builtin -c', tail(e)):
        return
    und = nm_undefined(obj) - {'__stack_chk_fail', 'stderr', 'stdout', 'stdin'}
    listed = set() if libc == 'none' else set(libc.split(','))
    ok = (und - {'memcpy'}) == (listed - {'memcpy'}) and ('memcpy' not in listed or 'memcpy' in und)
    check(ok, cid + '/libc-census', 'match_api.md §6.3.10¶5, ¶7',
          'MEMFN_LIBC equals the object\'s undefined functions', 'listed=%s undefined=%s' % (sorted(listed), sorted(und)))


# ---------------------------------------------------------------- build + run

def cc_base(cc, opt):
    f = ['-std=gnu11', opt]
    if opt != '-O0':
        f.append('-D_FORTIFY_SOURCE=2')
    return [cc] + f


def predefined(cc, flags):
    rc, o, e = run([cc] + flags + ['-dM', '-E', '-x', 'c', '/dev/null'])
    ds = set(l.split()[1] for l in o.splitlines() if l.startswith('#define'))
    return '%d %d %d' % tuple(int(m in ds) for m in ('__AVX2__', '__SSE4_2__', '__BMI2__'))


def compare_run(out, arts, pats_by_id, exp_cache, subs, cflags_macros):
    """Parse consumer output; compare A<k> against python3 re, C against
    the subjects' plain facts, M against the consumer flags' own macros."""
    got = {}
    for l in out.splitlines():
        tag, _, rest = l.partition(' ')
        got.setdefault(tag, []).append(rest)
    problems = []
    for k, (pid, _) in enumerate(arts, 1):
        exp = exp_cache[pid]
        g = got.get('A%d' % k, [])
        if g != exp:
            bad = next((i for i, (x, y) in enumerate(zip(g, exp)) if x != y), min(len(g), len(exp)))
            problems.append('A%d(%s) line %d: got %r want %r (%d/%d lines)' % (
                k, pid, bad, g[bad] if bad < len(g) else None, exp[bad] if bad < len(exp) else None, len(g), len(exp)))
    ec = expected_consumer(subs)
    if got.get('C', []) != ec:
        g = got.get('C', [])
        bad = next((i for i, (x, y) in enumerate(zip(g, ec)) if x != y), min(len(g), len(ec)))
        problems.append('C line %d: got %r want %r' % (bad, g[bad] if bad < len(g) else None, ec[bad] if bad < len(ec) else None))
    if got.get('M', [None]) != [cflags_macros]:
        problems.append('M: got %r want %r (a target macro leaked out of a region?)' % (got.get('M'), cflags_macros))
    return problems


class Ctx:
    pass


def job_consumer(ctx, cid, cite, desc, cc, flags, arts, mode='include', novec=False):
    """Build one consumer program over one or two artifacts and check its
    answers. arts: [(pid, Artifact)], Artifact has .c .h .prefix."""
    d = os.path.join(OUT, 'bin', cid.replace('/', '__'))
    os.makedirs(d, exist_ok=True)
    defs = []
    objs = []
    for k, (pid, a) in enumerate(arts, 1):
        defs += ['-DPFX%d=%s' % (k, a.prefix)]
        if mode == 'separate':
            defs += ['-DHDR%d="%s"' % (k, a.h)]
            o = os.path.join(d, a.prefix + '.o')
            rc, so, se = run(flags + ['-c', a.c, '-o', o], 180)
            if not check(rc == 0, cid + '/compile-artifact%d' % k, 'match_api.md §6.3.10¶15, ¶4',
                         'the artifact compiles alone: ' + ' '.join(flags[:1] + flags[1:]), tail(se)):
                return
            objs.append(o)
        else:
            defs += ['-DART%d="%s"' % (k, a.c)]
    if mode == 'separate':
        defs.append('-DSEPARATE')
    if mode == 'headers-first':
        defs.append('-DHEADERS_FIRST')
    if novec:
        defs.append('-DNOVEC')
    exe = os.path.join(d, 'consumer')
    rc, so, se = run(flags + defs + [CONSUMER] + objs + ['-o', exe], 240)
    if not check(rc == 0, cid + '/compile', cite, desc + ' [compile: %s]' % ' '.join(flags), tail(se, 900)):
        return
    subsf = ctx.subjfile_for(arts)
    rc, so, se = run([exe, subsf], 120)
    if not check(rc == 0, cid + '/run', cite, desc + ' [run]', 'rc=%d %s' % (rc, tail(se))):
        return
    probs = compare_run(so, arts, ctx.pats, ctx.exp_for(arts), ctx.subs_for(arts), predefined(flags[0], flags[1:]))
    check(not probs, cid + '/answers', cite + '; answers: python3 re', desc + ' [answers]', ' | '.join(probs)[:900])


def job_emit_main(ctx, cid, cite, cc, flags, pat, a):
    d = os.path.join(OUT, 'bin', cid.replace('/', '__'))
    os.makedirs(d, exist_ok=True)
    exe = os.path.join(d, 'main')
    rc, so, se = run(flags + [a.c, '-o', exe], 240)
    if not check(rc == 0, cid + '/compile', cite, '--emit-main artifact compiles: ' + ' '.join(flags), tail(se, 900)):
        return
    subs = [s for s in ctx.subs[pat.id] if b'\x00' not in s][:30]
    bad = []
    for s in subs:
        p = subprocess.run([TMO, '-k', '5', '30', exe, s], capture_output=True)
        want = 0 if pat.rx.search(s) else 1
        if p.returncode != want:
            bad.append('%r: exit %d want %d' % (s, p.returncode, want))
    check(not bad, cid + '/answers', 'cli.md §1.10¶1; answers: python3 re',
          '--emit-main exit 0 on match / 1 on no-match over %d subjects' % len(subs), '; '.join(bad[:4]))
    p = subprocess.run([TMO, '-k', '5', '30', exe], capture_output=True)
    check(p.returncode == 2, cid + '/usage', 'cli.md §1.10¶1', '--emit-main exits 2 on wrong argc', 'rc=%d' % p.returncode)


def guard_message(path):
    """The artifact's own #error text (its guard's message), unquoted."""
    T = Text(path, 'X')
    if not T.guard:
        return None
    m = re.search(r'#\s*error\s+"(.*)"', T.lines[T.guard[1]])
    return m.group(1) if m else T.lines[T.guard[1]].split('error', 1)[1].strip()


def job_refusal(cid, cite, desc, cmd, expect_guard, src=None):
    rc, so, se = run(cmd, 120)
    first_err = next((l for l in se.splitlines() if 'error' in l), '')
    if expect_guard:
        msg = guard_message(src) if src else None
        check(rc != 0 and msg is not None and msg[:60] in first_err, cid, cite, desc,
              'rc=%d first error: %s' % (rc, first_err[:300]))
    else:
        check(rc == 0, cid, cite, desc, 'rc=%d %s' % (rc, tail(se, 500)))


def job_frame_refusal(cid, cite, desc, cmd):
    rc, so, se = run(cmd, 120)
    first_err = next((l for l in se.splitlines() if 'error' in l), '')
    check(rc != 0 and '_FRAME_SIZE disagrees' in first_err, cid, cite, desc,
          'rc=%d first error: %s' % (rc, first_err[:300]))


# ---------------------------------------------------------------- main

class Artifact:
    def __init__(self, c, prefix):
        self.c = c
        self.h = c[:-2] + '.h'
        self.prefix = prefix


def main():
    os.makedirs(OUT, exist_ok=True)
    print('# d27region: pcrec=%s out=%s jobs=%d timeout=%s' % (PCREC, OUT, JOBS, TMO))
    pats = load_patterns()
    P = {p.id: p for p in pats}
    targets, portable, hostfam, host = read_listing()
    canon = portable[:1] + [t for t in targets if t.family == hostfam]      # this host's family + generic
    foreign = [t for t in targets if t.family not in ('', hostfam)]
    print('# targets this family: %s; other families: %s' % (
        ' '.join(t.stamp for t in canon), ' '.join(t.stamp for t in foreign)))

    # subjects + expectations
    ctx = Ctx()
    ctx.pats = P
    ctx.subs = {p.id: gen_subjects(p, 1000 + i) for i, p in enumerate(pats)}
    ctx.exp = {p.id: expected_answers(p, ctx.subs[p.id]) for p in pats}
    sd = os.path.join(OUT, 'subj')
    os.makedirs(sd, exist_ok=True)
    ctx.files = {}
    for p in pats:
        f = os.path.join(sd, p.id + '.hex')
        with open(f, 'w') as fh:
            fh.write(''.join(s.hex() + '\n' for s in ctx.subs[p.id]))
        ctx.files[p.id] = f
    # a pair of artifacts runs on the FIRST artifact's pattern's subjects;
    # the second's expectations are computed over the same subjects
    pair_exp = {}

    def subjfile_for(arts):
        return ctx.files[arts[0][0]]

    def subs_for(arts):
        return ctx.subs[arts[0][0]]

    def exp_for(arts):
        base = arts[0][0]
        m = {}
        for pid, _ in arts:
            if pid == base:
                m[pid] = ctx.exp[pid]
            else:
                key = (base, pid)
                if key not in pair_exp:
                    pair_exp[key] = expected_answers(P[pid], ctx.subs[base])
                m[pid] = pair_exp[key]
        return m

    ctx.subjfile_for, ctx.subs_for, ctx.exp_for = subjfile_for, subs_for, exp_for

    # --- generation: one artifact per (pattern, canonical target), plain and --emit-main
    arts = {}       # (pid, tag, emit) -> Artifact
    gd = os.path.join(OUT, 'art')
    for p in pats:
        for t in canon + foreign:
            for em in (False, True):
                prefix = '%s_%s%s' % (p.id, t.tag, '_m' if em else '')
                rc, path, err = gen(os.path.join(gd, p.id), prefix, cfg_opts(t), p, emit_main=em)
                if check(rc == 0, 'gen/%s/%s%s' % (p.id, t.tag, '/main' if em else ''),
                         'tuning.md §2.43¶3, cli.md §1.24¶3', 'pcrec compiles %s for %s' % (p.pcrec, t.stamp), tail(err)):
                    arts[(p.id, t.tag, em)] = Artifact(path, prefix)

    # --- text + stamp checks on every generated artifact
    forms_of = {}
    for (pid, tag, em), a in sorted(arts.items()):
        t = next(x for x in canon + foreign if x.tag == tag)
        T, gval, forms, libc = check_artifact_text('text/%s/%s%s' % (pid, tag, '/main' if em else ''),
                                                   a.c, a.prefix.upper(), t, P[pid], em)
        forms_of[(pid, tag, em)] = forms
        if t.family in ('', hostfam):
            check_libc_census('census/%s/%s%s' % (pid, tag, '/main' if em else ''), a.c, libc, os.path.join(OUT, 'art', pid))

    # --- identity: one prefix (rx) across spellings (§2.43¶4, ¶4, ¶9; cli §1.24¶2-¶4)
    idd = os.path.join(OUT, 'ident')
    spell = [('default', []), ('nosimd', ['-fno-memfn-simd']), ('simd', ['-fmemfn-simd'])]
    for t in canon + foreign:
        spell.append(('t_' + t.tag, ['-fmemfn-simd=%s' % t.name]))
        spell.append(('tu_' + t.tag, ['-fmemfn-simd=%s' % t.name.upper()]))
    if hostfam:
        spell.append(('fam', ['-fmemfn-simd=%s' % hostfam]))
    spell += [('later_off', ['-fmemfn-simd=x86-64-v3', '-fno-memfn-simd']),
              ('later_on', ['-fno-memfn-simd', '-fmemfn-simd=x86-64-v3']),
              ('later_plain', ['-fmemfn-simd=x86-64-v3', '-fmemfn-simd']),
              ('repeat', ['-fmemfn-simd=x86-64,x86-64']),
              ('deny_w32_off', ['--memfn=no-vrun-w32']),
              ('deny_w32_v3', ['-fmemfn-simd=x86-64-v3', '--memfn=no-vrun-w32']),
              ('deny_w16_v3', ['-fmemfn-simd=x86-64-v3', '--memfn=no-vrun-w16']),
              ('nocom_v3', ['-fmemfn-simd=x86-64-v3', '-fno-comments']),
              ('nocom_x', ['-fmemfn-simd', '-fno-comments'])]
    ident = {}

    def gen_ident(job):
        p, name, opts, prefix = job
        rc, path, err = gen(os.path.join(idd, p.id, name), prefix, opts, p)
        return job, rc, path, err

    jobs = [(p, n, o, 'rx') for p in pats for n, o in spell]
    jobs += [(p, 'longp_v3', ['-fmemfn-simd=x86-64-v3'], 'averyveryverylongprefix') for p in pats]
    jobs += [(p, 'longp_x', ['-fmemfn-simd'], 'averyveryverylongprefix') for p in pats]
    with ThreadPoolExecutor(JOBS) as ex:
        for (p, n, o, pre), rc, path, err in ex.map(gen_ident, jobs):
            if check(rc == 0, 'ident-gen/%s/%s' % (p.id, n), 'cli.md §1.24¶1-¶4', 'pcrec %s' % ' '.join(o), tail(err)):
                ident[(p.id, n)] = (open(path, encoding='latin1').read(), open(path[:-2] + '.h', encoding='latin1').read(), path)

    def same(a, b):
        return a in ident and b in ident and ident[a][:2] == ident[b][:2]

    def stamp(key, name, pre='RX'):
        s = parse_stamps(ident[key][0], pre).get(name, [(0, '')])[0][1]
        return unq(s)

    for p in pats:
        k = lambda n: (p.id, n)
        c = 'ident/%s' % p.id
        check(same(k('default'), k('nosimd')), c + '/nosimd-equals-default', 'tuning.md §2.43¶4',
              '-fno-memfn-simd renders the default artifact byte for byte (.c and .h)')
        for t in portable:
            check(same(k('default'), k('t_' + t.tag)), c + '/generic-equals-default',
                  'match_api.md §6.3.10¶15 (last sentence), ¶9; tuning.md §2.43¶4',
                  '-fmemfn-simd=%s (the portable target: empty texts) equals the default byte for byte' % t.name)
        if hostfam:
            dl = host['defaults']
            dt = next((t for t in targets if t.name == dl), None)
            if dt:
                check(same(k('simd'), k('t_' + dt.tag)), c + '/plain-equals-defaults', 'cli.md §1.24¶1, ¶3',
                      '-fmemfn-simd alone equals -fmemfn-simd=%s (the host family\'s default list)' % dl)
                check(same(k('fam'), k('t_' + dt.tag)), c + '/family-token', 'cli.md §1.24¶2',
                      '-fmemfn-simd=%s (a family token) equals its default list %s' % (hostfam, dl))
                check(same(k('repeat'), k('t_' + dt.tag)), c + '/repeat-is-one', 'cli.md §1.24¶3',
                      'repeating a target is one target')
        for t in canon + foreign:
            check(same(k('tu_' + t.tag), k('t_' + t.tag)), c + '/case-blind/' + t.tag, 'cli.md §1.24¶2',
                  'token matching is ASCII-case-blind (%s)' % t.name.upper())
        check(same(k('later_off'), k('default')), c + '/later-off-wins', 'cli.md §1.24¶1, ¶4',
              '-fmemfn-simd=x86-64-v3 -fno-memfn-simd is off (later wins, list discarded)')
        check(same(k('later_on'), k('t_x8664v3')), c + '/later-on-wins', 'cli.md §1.24¶1, ¶4',
              '-fno-memfn-simd -fmemfn-simd=x86-64-v3 is x86-64-v3')
        check(same(k('later_plain'), k('simd')), c + '/later-plain-wins', 'cli.md §1.24¶1',
              '-fmemfn-simd=x86-64-v3 -fmemfn-simd is the host default list')
        check(same(k('deny_w32_off'), k('default')), c + '/simd-deny-inert-off', 'tuning.md §2.43¶3b',
              'a SIMD row\'s deny at the default is accepted and does nothing')
        # ¶4 / §2.43¶4: "none" iff identical to the SIMD-off compile, its target's text aside
        for t in [x for x in canon + foreign if x.family]:
            key = k('t_' + t.tag)
            if key not in ident or k('default') not in ident:
                continue
            on_c, on_h, _ = ident[key]
            bad, ins = target_text_diff(ident[k('default')][0], on_c, 'RX')
            forms = stamp(key, 'MEMFN_FORMS')
            g = int(stamp(key, 'SIMD_GUARDED_BYTES')[2:18] or '0', 16)
            ident_ok = not bad and on_h == ident[k('default')][1]
            check((forms == 'none') == ident_ok, c + '/forms-iff-identity/' + t.tag,
                  'match_api.md §6.3.10¶4, tuning.md §2.43¶4',
                  'MEMFN_FORMS is "none" iff the artifact equals its -fno-memfn-simd compile, target text aside',
                  'forms=%s extra-non-directive-lines=%d .h-equal=%s first=%r' % (
                      forms, len(bad), on_h == ident[k('default')][1], bad[:2]))
            if forms == 'none' and not bad:
                check(g == ins, c + '/guarded-counts-target-text/' + t.tag, 'match_api.md §6.3.10¶8-¶9, limits.md §8.3¶1',
                      'SIMD_GUARDED_BYTES equals the bytes of the target\'s own text (the added lines)',
                      'stamp=%d added=%d size-delta=%d' % (g, ins, len(on_c.encode('latin1')) - len(ident[k('default')][0].encode('latin1'))))
                check(g <= 700, c + '/target-text-bound/' + t.tag, 'limits.md §8.3¶3',
                      'the target\'s own text is at most 700 bytes', str(g))
        # ¶9: neither -fno-comments nor -p moves the count
        for tg, nc, lp in (('t_x8664v3', 'nocom_v3', 'longp_v3'), ('simd', 'nocom_x', 'longp_x')):
            if k(tg) in ident and k(nc) in ident:
                check(stamp(k(tg), 'SIMD_GUARDED_BYTES') == stamp(k(nc), 'SIMD_GUARDED_BYTES'),
                      c + '/guarded-ignores-comments/' + tg, 'match_api.md §6.3.10¶9',
                      '-fno-comments does not change SIMD_GUARDED_BYTES',
                      '%s vs %s' % (stamp(k(tg), 'SIMD_GUARDED_BYTES'), stamp(k(nc), 'SIMD_GUARDED_BYTES')))
            if k(tg) in ident and k(lp) in ident:
                check(stamp(k(tg), 'SIMD_GUARDED_BYTES') == stamp(k(lp), 'SIMD_GUARDED_BYTES', 'AVERYVERYVERYLONGPREFIX'),
                      c + '/guarded-ignores-prefix/' + tg, 'match_api.md §6.3.10¶9',
                      '-p does not change SIMD_GUARDED_BYTES',
                      '%s vs %s' % (stamp(k(tg), 'SIMD_GUARDED_BYTES'), stamp(k(lp), 'SIMD_GUARDED_BYTES', 'AVERYVERYVERYLONGPREFIX')))
        # §2.43¶3b: deny w32 at v3 -> no 32-byte level; deny w16 at v3 -> still a form
        if k('t_x8664v3') in ident and stamp(k('t_x8664v3'), 'MEMFN_FORMS') != 'none':
            f32 = stamp(k('deny_w32_v3'), 'MEMFN_FORMS')
            check('w32' not in f32 and f32 != 'none', c + '/deny-w32', 'tuning.md §2.43¶3b',
                  '--memfn=no-vrun-w32 at x86-64-v3: the 16-byte level is the top level', f32)
            f16 = stamp(k('deny_w16_v3'), 'MEMFN_FORMS')
            check('w16' not in f16 and f16 != 'none', c + '/deny-w16', 'tuning.md §2.43¶3b',
                  '--memfn=no-vrun-w16 at x86-64-v3: the 32-byte level falls straight to the scalar body', f16)

    # exemplar (match_api.md §6.3.10¶4's own spellings for the vrun shape)
    if ('n1', 'simd') in ident:
        check(stamp(('n1', 'simd'), 'MEMFN_FORMS') == 'vrun@w16', 'ident/n1/exemplar-w16', 'match_api.md §6.3.10¶4',
              '(?i)needle at -fmemfn-simd on amd64 reads vrun@w16', stamp(('n1', 'simd'), 'MEMFN_FORMS'))
        check(stamp(('n1', 't_x8664v3'), 'MEMFN_FORMS') == 'vrun@w32+w16', 'ident/n1/exemplar-w32w16',
              'match_api.md §6.3.10¶4', '(?i)needle at -fmemfn-simd=x86-64-v3 reads vrun@w32+w16',
              stamp(('n1', 't_x8664v3'), 'MEMFN_FORMS'))

    # CLI refusals (cli.md §1.24¶2-¶3)
    rp = P['n8']
    for name, opt, why in (('unknown', '-fmemfn-simd=bogus-cpu', 'an unknown token'),
                           ('empty', '-fmemfn-simd=', 'an empty token'),
                           ('empty-item', '-fmemfn-simd=x86-64,', 'an empty list item'),
                           ('two-targets', '-fmemfn-simd=x86-64,x86-64-v3', 'a list resolving to two targets'),
                           ('mixed', '-fmemfn-simd=x86-64,armv8-a', 'a list mixing families')):
        out = os.path.join(OUT, 'refuse', name + '.c')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if os.path.exists(out):
            os.remove(out)
        rc, so, se = run([PCREC, opt, '-o', out, '--pattern', rp.pcrec])
        check(rc == 1 and se.startswith('pcrec: ') and not os.path.exists(out), 'cli/refuse-' + name,
              'cli.md §1.24¶2-¶3', 'pcrec refuses %s with exit 1, "pcrec: " text, and writes no artifact' % why,
              'rc=%d exists=%s %s' % (rc, os.path.exists(out), tail(se, 200)))
    # tuning.md §2.43¶3e / ¶1 through the library: pcrec_options.memfn_simd
    lib = os.path.join(CELL, 'build', 'libpcrec.a')
    exe = os.path.join(OUT, 'lib_options')
    rc, so, se = run(['gcc', '-O1', '-I', os.path.join(CELL, 'lib'), os.path.join(CASES, 'lib_options.c'), lib, '-lm', '-o', exe], 180)
    if check(rc == 0, 'libopt/build', 'tuning.md §2.43¶3e', 'the library probe builds against build/libpcrec.a', tail(se)):
        rc, so, se = run([exe])
        got = {l.split(' ')[0]: l.split(' ')[1:3] for l in so.splitlines()}
        dl = (host or {}).get('defaults', 'x86-64')
        for case, want, why in (('off-nolist', ['0', 'none:generic'], 'SIMD off is the portable target'),
                                ('off-list', ['-1', '-'], 'SIMD off with a list is refused'),
                                ('deny-list', ['-1', '-'], 'the deny bit with a list is refused'),
                                ('deny-force-list', ['-1', '-'], 'deny + force is off (the deny wins, ¶1), so the list is refused'),
                                ('force-nolist', ['0', 'amd64:' + dl], 'SIMD on with no list is the host family\'s default list'),
                                ('force-list', ['0', 'amd64:x86-64-v3'], 'SIMD on with a list is exactly that list'),
                                ('force-generic', ['0', 'none:generic'], 'a list naming the portable target resolves to it')):
            check(got.get(case) == want, 'libopt/' + case, 'tuning.md §2.43¶1, ¶3e', why, '%s -> %s' % (case, got.get(case)))
    # generic mixed with a family target: the spec does not say (recorded, not judged)
    out = os.path.join(OUT, 'refuse', 'generic-mix.c')
    rc, so, se = run([PCREC, '-fmemfn-simd=generic,x86-64', '-o', out, '--pattern', rp.pcrec])
    tv = parse_stamps(open(out, encoding='latin1').read(), 'RX').get('TARGETS') if rc == 0 and os.path.exists(out) else None
    print('# OBSERVE cli.md §1.24¶3: -fmemfn-simd=generic,x86-64 -> rc=%d TARGETS=%s %s' % (rc, tv, tail(se, 200)))

    # --- consumer builds
    compilers = [c for c in ('gcc', 'clang') if shutil.which(c)]
    opts = ['-O2'] if QUICK else ['-O0', '-O2']
    if QUICK:
        compilers = compilers[:1]
    cpu_avx2 = 'avx2' in open('/proc/cpuinfo').read()
    runnable = [t for t in canon if t.family == '' or t.name != 'x86-64-v3' or cpu_avx2]
    work = []
    for p in pats:
        for t in runnable:
            a = arts.get((p.id, t.tag, False))
            am = arts.get((p.id, t.tag, True))
            for cc in compilers:
                for o in opts:
                    fl = cc_base(cc, o)
                    for mode in ('include', 'headers-first', 'separate'):
                        if a:
                            work.append((job_consumer, ctx, 'use/%s/%s/%s%s/%s' % (p.id, t.tag, cc, o, mode),
                                         'match_api.md §6.3.10¶15, ¶4',
                                         'consumer TU (%s) uses SSE/AVX intrinsics + fortified libc after %s artifact' % (mode, t.stamp),
                                         cc, fl, [(p.id, a)], mode))
                    if am:
                        work.append((job_emit_main, ctx, 'main/%s/%s/%s%s' % (p.id, t.tag, cc, o),
                                     'match_api.md §6.3.10¶15', cc, fl, p, am))
    # a second artifact for another target, both orders (¶15 "a second artifact ... for any target")
    for pa, pb in (('n1', 'n6'), ('c2', 'v1'), ('n3', 'n3'), ('v3', 'c3')):
        for ta in runnable:
            for tb in runnable:
                if pa == pb and ta.tag == tb.tag:
                    continue
                A = arts.get((pa, ta.tag, False))
                B = arts.get((pb, tb.tag, False))
                if not (A and B):
                    continue
                for cc in compilers:
                    for o in opts:
                        for mode in ('include',) if o == '-O0' else ('include', 'headers-first'):
                            work.append((job_consumer, ctx, 'pair/%s@%s+%s@%s/%s%s/%s' % (pa, ta.tag, pb, tb.tag, cc, o, mode),
                                         'match_api.md §6.3.10¶15',
                                         'one TU includes %s then %s, then uses intrinsics + libc' % (ta.stamp, tb.stamp),
                                         cc, cc_base(cc, o), [(pa, A), (pb, B)], mode))
    # consumer flags the region must not depend on (¶4 "whatever the consumer's -march", §10.7¶4)
    special = [('mno-sse2', ['-mno-sse2'], True, 'match_api.md §10.7¶4'),
               ('mgeneral-regs-only', ['-mgeneral-regs-only'], True, 'match_api.md §10.7¶4'),
               ('march-x86-64', ['-march=x86-64'], False, 'match_api.md §6.3.10¶4, ¶15'),
               ('march-x86-64-v2', ['-march=x86-64-v2'], False, 'match_api.md §6.3.10¶4, ¶15'),
               ('march-x86-64-v3', ['-march=x86-64-v3'], False, 'match_api.md §6.3.10¶4, ¶15'),
               ('march-native', ['-march=native'], False, 'match_api.md §6.3.10¶4, ¶15'),
               ('O3', ['-O3'], False, 'match_api.md §6.3.10¶15'),
               ('Os', ['-Os'], False, 'match_api.md §6.3.10¶15'),
               ('fPIC', ['-fPIC'], False, 'match_api.md §6.3.10¶15'),
               ('flto', ['-flto'], False, 'match_api.md §6.3.10¶15')]
    for pid in ('n1', 'n3', 'v1', 'c2', 'n7'):
        for t in runnable:
            a = arts.get((pid, t.tag, False))
            if not a:
                continue
            for cc in compilers:
                for name, fl, novec, cite in special:
                    for mode in ('include', 'separate'):
                        work.append((job_consumer, ctx, 'flags/%s/%s/%s/%s/%s' % (pid, t.tag, cc, name, mode), cite,
                                     'consumer %s with the %s artifact' % (' '.join(fl), t.stamp),
                                     cc, cc_base(cc, '-O2') + fl, [(pid, a)], mode, novec))
    # §2.43¶3b: the per-form denies keep the answers
    for pid in ('n1', 'n3', 'v1'):
        for deny in ('no-vrun-w32', 'no-vrun-w16', 'no-vrun-kb', 'no-vrun-trim', 'no-vrun-pad'):
            prefix = '%s_v3_%s' % (pid, deny.replace('-', '_'))
            rc, path, err = gen(os.path.join(OUT, 'deny', pid), prefix, ['-fmemfn-simd=x86-64-v3', '--memfn=' + deny], P[pid])
            if check(rc == 0, 'deny-gen/%s/%s' % (pid, deny), 'tuning.md §2.43¶3b', 'pcrec --memfn=%s at x86-64-v3' % deny, tail(err)) and cpu_avx2:
                work.append((job_consumer, ctx, 'deny/%s/%s' % (pid, deny), 'tuning.md §2.43¶3b (answers never change, ¶3a)',
                             '--memfn=%s at x86-64-v3' % deny, 'gcc', cc_base('gcc', '-O2'), [(pid, Artifact(path, prefix))], 'include'))

    # --- the guard's refusal (¶4 "-m32 stops at the guard", ¶15)
    gccinc = run(['gcc', '-print-file-name=include'])[1].strip()
    fam_targets = [t for t in canon if t.family]
    for pid in ('n1', 'c2', 'v1', 'n7'):
        for t in fam_targets:
            for em in (False, True):
                a = arts.get((pid, t.tag, em))
                if not a:
                    continue
                c = 'guard/%s/%s%s' % (pid, t.tag, '/main' if em else '')
                d = os.path.dirname(a.c)
                for name, cmd in (('gcc-m32', ['gcc', '-m32']), ('gcc-mx32', ['gcc', '-mx32']),
                                  ('clang-m32', ['clang', '-m32']),
                                  ('clang-aarch64', ['clang', '--target=aarch64-linux-gnu'])):
                    work.append((job_refusal, c + '/' + name, 'match_api.md §6.3.10¶4, ¶15',
                                 '%s artifact under %s stops at the guard (#error first)' % (t.stamp, name),
                                 cmd + ['-fsyntax-only', '-I', d, a.c], True, a.c))
        for t in foreign:
            a = arts.get((pid, t.tag, False))
            if not a:
                continue
            for cc in compilers:
                work.append((job_refusal, 'guard/%s/%s/host-%s' % (pid, t.tag, cc), 'match_api.md §6.3.10¶15',
                             '%s artifact under the host %s stops at the guard' % (t.stamp, cc),
                             [cc, '-fsyntax-only', a.c], True, a.c))
            if t.family == 'arm64':
                work.append((job_refusal, 'guard/%s/%s/clang-aarch64-passes' % (pid, t.tag), 'match_api.md §6.3.10¶15',
                             '%s artifact passes its own guard under clang --target=aarch64 (stub libc headers)' % t.stamp,
                             ['clang', '--target=aarch64-linux-gnu', '-ffreestanding', '-nostdlibinc', '-isystem', STUBINC,
                              '-fsyntax-only', a.c], False))
        for t in portable:
            a = arts.get((pid, t.tag, False))
            if not a:
                continue
            m32 = ['gcc', '-m32', '-ffreestanding', '-nostdinc', '-isystem', gccinc, '-isystem', STUBINC,
                   '-fsyntax-only', a.c]
            if '--engine=vm' in P[pid].opts:
                # F2's expectation, changed at landing (lane u3d27, manager ruling F2/S1): a VM
                # artifact is tied to the data model it was generated for and refuses another
                # cleanly, at its frame-size asserts
                work.append((job_frame_refusal, 'guard/%s/%s/gcc-m32-frame-refused' % (pid, t.tag),
                             'tuning.md §2.43¶2, match_api.md §6.3.10¶4, §10.4¶2',
                             'the default VM artifact under gcc -m32 stops at its frame-size asserts (stub libc headers)',
                             m32))
            else:
                work.append((job_refusal, 'guard/%s/%s/gcc-m32-passes' % (pid, t.tag), 'tuning.md §2.43¶2, match_api.md §6.3.10¶15',
                             'the default artifact has no guard: gcc -m32 compiles it (stub libc headers)',
                             m32, False))
            work.append((job_refusal, 'guard/%s/%s/clang-aarch64-passes' % (pid, t.tag), 'tuning.md §2.43¶2, match_api.md §6.3.10¶15',
                         'the default artifact has no guard: clang --target=aarch64 compiles it (stub libc headers)',
                         ['clang', '--target=aarch64-linux-gnu', '-ffreestanding', '-nostdlibinc', '-isystem', STUBINC,
                          '-fsyntax-only', a.c], False))

    print('# %d build/run jobs' % len(work))
    sys.stdout.flush()
    with ThreadPoolExecutor(JOBS) as ex:
        futs = [ex.submit(w[0], *w[1:]) for w in work]
        for f in futs:
            try:
                f.result()
            except Exception as e:      # a harness bug is a failed check, never a silent pass
                check(False, 'harness/exception', '-', 'a job raised', repr(e))

    # --- the self-checked control: one deliberately wrong expectation
    ctl = arts.get(('n1', portable[0].tag, False)) if portable else None
    if ctl:
        T = Text(ctl.c, ctl.prefix.upper())
        wrong = unq(T.stamps['TARGETS'][0][1]) == 'amd64:x86-64-v3'      # deliberately wrong
        check(not wrong, 'control/stamp-detects', 'control', 'the wrong expectation (default TARGETS == amd64:x86-64-v3) fails')
        flipped = list(ctx.exp['n1'])
        i = next(j for j, l in enumerate(flipped) if l.split()[2] == '1')
        flipped[i] = flipped[i].rsplit(' ', 1)[0] + ' 999'                 # deliberately wrong answer
        fake = 'M x\n' + ''.join('A1 %s\n' % l for l in ctx.exp['n1'])
        probs = compare_run(fake, [('n1', ctl)], P, {'n1': flipped}, ctx.subs['n1'], 'x')
        check(any(pr.startswith('A1') for pr in probs), 'control/answers-detect', 'control',
              'the comparator reports a deliberately wrong expected answer', ' | '.join(probs)[:300])
        if CONTROL:
            check(wrong, 'control/WRONG-EXPECTATION', 'control (D27_CONTROL=1)',
                  'DELIBERATELY WRONG: default artifact TARGETS == amd64:x86-64-v3', T.stamps['TARGETS'][0][1])

    # --- report
    npass = sum(1 for r in results if r[0])
    nfail = len(results) - npass
    for ok, cid, cite, desc, detail in sorted(results, key=lambda r: (r[0], r[1])):
        if not ok:
            print('FAIL %s [%s] %s :: %s' % (cid, cite, desc, detail))
    if os.environ.get('D27_VERBOSE') == '1':
        for ok, cid, cite, desc, detail in sorted(results, key=lambda r: r[1]):
            if ok:
                print('PASS %s [%s] %s' % (cid, cite, desc))
    with open(os.path.join(OUT, 'results.tsv'), 'w') as f:
        for ok, cid, cite, desc, detail in sorted(results, key=lambda r: r[1]):
            f.write('%s\t%s\t%s\t%s\t%s\n' % ('PASS' if ok else 'FAIL', cid, cite, desc, detail.replace('\n', ' ').replace('\t', ' ')))
    print('checks passed: %d' % npass)
    print('checks failed: %d' % nfail)
    return 0 if nfail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
