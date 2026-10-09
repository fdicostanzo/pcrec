#!/usr/bin/env python3
"""tests/memfn/libc_census.py -- C11, the stamps' census ([MEMFN] R4a';
docs/design/memfn/integration.md §R4.3.3, §18.2, §10.5; D147 addendum 10).

WHAT IT CHECKS, per artifact of a corpus-wide population:
  presence  every artifact carries exactly one `<UP>_MEMFN_FORMS` and one
            `<UP>_MEMFN_LIBC` line (D81: presence never varies), counted
            per engine family;
  grammar   each value is "none" or sorted, distinct, comma-joined C
            identifiers with no space;
  LIBC      the line's names EQUAL the names the compile reports: `nm -u`
            of the artifact's `-O0 -fno-builtin -c` object, the platform's
            leading `_` removed, minus the record's one exclusion (a
            `memcpy` of a constant 1-8 bytes) and minus the C library's
            data objects (the stdio streams, which `--emit-main` and
            `--trace` artifacts reference);
  ROUTING   (R4e'.0b, D155) every offset-skip/pre-check function is routed:
            its loop under `<fn>__body`, the function itself a selector
            whose whole body is one call per arm, and no other function body
            holds a conditional directive (routing_shape.py, C18's routing
            leg); the functions counted are a population with its own floor
            (`funcs`), and the rule's planted controls run first;
  FORMS     the value is "none". Its "none implies identical to the
            SIMD-off compile" half RUNS from R4c, when the switch is born
            (R-4, Q5), at BOTH layers. The default IS -fno-memfn-simd, so
            every pattern-stream artifact is compiled twice more: (a) with
            -fno-memfn-simd stated, which must be byte-equal to the default
            (the deny of the default restates it); (b) with -fmemfn-simd,
            the SIMD-ON layer, which must ALSO be byte-equal to the default
            while FORMS reads "none" everywhere (R4c' item (e): (a) alone
            never compiled the ON side). Both reported "identical (no SIMD
            form)": identical by construction while no SIMD form exists, so
            they catch a non-inert switch and prove nothing about a SIMD
            form. At the first SIMD-on form (Q55, R4e') (b) is replaced by
            the movers half (FORMS names the forms an ON artifact differs
            by), which stays UNREACHED until then. Composition files are not
            re-compiled.

THE INDEPENDENT CONTROL (docs/dev/learnings.md §3). The names come from the
COMPILER's symbol table, not from text: no list here is shared with the
producer (src/gen/memfn_stamps.c), and this file reads none of its code.
The exclusion is applied by the COMPILER too: a prelude (`-include`) turns
every `memcpy` whose length the compiler folds to a constant 1-8 into a
call to `c11_idiom_memcpy`, so an idiom load and a real `memcpy` are two
different undefined symbols, and the idiom count is a population in its own
right (it must reach its floor, or the exclusion is untested).

THE POPULATION is deterministic: the corpus's `--list-source` patterns
(scripts/emit_sweep.py's enumeration), each kept iff a stable hash of its
text falls in the stream's sample, so a pattern added to the corpus never
reshuffles the rest. Five streams: the default engine, --engine=vm,
--emit-main, --trace, and every composition file (a FILE operand with
`-o DIR`, whose artifacts carry a separate header). Every population count
has a floor, passed in by run_libc_census.sh as literals (K35).

Exit 0 iff every check passed; prints `checks passed:`/`checks failed:`.
"""
import concurrent.futures
import hashlib
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import routing_shape  # noqa: E402

PRELUDE = r'''#include <string.h>
#undef memcpy
void *c11_idiom_memcpy(void *, const void *, size_t);
#define C11_K(n) (__builtin_constant_p(n) ? (unsigned long)(n) : 0ul)
#define memcpy(d, s, n) __builtin_choose_expr(C11_K(n) >= 1 && C11_K(n) <= 8, \
    c11_idiom_memcpy, memcpy)(d, s, n)
'''
IDIOM = 'c11_idiom_memcpy'
# The C library's DATA objects an artifact may reference: the stdio streams
# (glibc spells them stdin/stdout/stderr; darwin __stdinp/__stdoutp/__stderrp).
# A data symbol is not a call; any other undefined name is read as one.
DATA_OBJECTS = {'stdin', 'stdout', 'stderr', '__stdinp', '__stdoutp', '__stderrp'}
CFLAGS = ['-O0', '-fno-builtin', '-fno-stack-protector', '-U_FORTIFY_SOURCE',
          '-std=gnu11', '-w']

STREAMS = [
    # name, extra argv, sample modulus (1 in N patterns)
    ('default', [], 6),
    ('vm', ['--engine=vm'], 12),
    ('emit-main', ['--emit-main'], 60),
    ('trace', ['--trace', '--engine=vm'], 60),
]

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


def sampled(pattern, modulus, salt):
    if isinstance(pattern, str):
        pattern = pattern.encode('utf-8', 'surrogateescape')
    h = hashlib.sha1(salt.encode() + b'\0' + pattern)
    return int.from_bytes(h.digest()[:4], 'big') % modulus == 0


# R-13: SIMD-on movers in the sampled pattern streams (the batch-1 rows reach
# only a FUNC whose predicate is one caseless-style run): a literal floor
MOVERS_FLOOR = 1
STAMP = re.compile(r'^#define (\w+)_(MEMFN_FORMS|MEMFN_LIBC) "([^"]*)"$', re.M)
ENGINE = re.compile(r'^#define \w+_ENGINE "(\w+)"$', re.M)
IDENT_LIST = re.compile(r'^[A-Za-z_]\w*(,[A-Za-z_]\w*)*$')


def parse_value(v):
    """The value's names, or None when it breaks the grammar."""
    if v == 'none':
        return []
    if not IDENT_LIST.match(v):
        return None
    names = v.split(',')
    if names != sorted(set(names)):
        return None
    return names


class Census:
    def __init__(self, cc, decor):
        self.cc = cc
        self.decor = decor
        self.n = 0
        self.family = {}
        self.calls = {}         # libc name -> artifacts calling it
        self.idiom = 0          # artifacts with >= 1 idiom memcpy load
        self.none = 0
        self.funcs = 0          # routed offset-skip/pre-check functions seen
        self.problems = []      # (key, message)

    def nm_names(self, cpath, workdir):
        obj = cpath[:-2] + '.o'
        r = subprocess.run([self.cc] + CFLAGS + ['-include', os.path.join(workdir, 'prelude.h'),
                            '-c', cpath, '-o', obj], capture_output=True, text=True)
        if r.returncode != 0:
            return None, 'does not compile: ' + r.stderr.strip()[:200]
        r = subprocess.run(['nm', '-u', obj], capture_output=True, text=True)
        os.remove(obj)
        if r.returncode != 0:
            return None, 'nm failed'
        names = set()
        for tok in r.stdout.split():
            if tok == 'U':
                continue
            if self.decor and tok.startswith(self.decor):
                tok = tok[len(self.decor):]
            names.add(tok)
        return names, None

    def one(self, key, text, cpath, workdir):
        """Checks one artifact; returns a result tuple for record()."""
        nfunc, why = routing_shape.check(text)
        if why:
            return (key, '?', None, None, 'routing: ' + '; '.join(why[:3]), nfunc)
        return self.stamps(key, text, cpath, workdir) + (nfunc,)

    def stamps(self, key, text, cpath, workdir):
        stamps = STAMP.findall(text)
        eng = ENGINE.findall(text)
        family = eng[0] if len(eng) == 1 else '?'
        kinds = [k for _, k, _ in stamps]
        if kinds.count('MEMFN_FORMS') != 1 or kinds.count('MEMFN_LIBC') != 1:
            return (key, family, None, None, 'presence: %d FORMS, %d LIBC lines'
                    % (kinds.count('MEMFN_FORMS'), kinds.count('MEMFN_LIBC')))
        vals = {k: v for _, k, v in stamps}
        if vals['MEMFN_FORMS'] != 'none':
            return (key, family, None, None,
                    'FORMS is "%s" on a default artifact (Q55: none until R4f)' % vals['MEMFN_FORMS'])
        line = parse_value(vals['MEMFN_LIBC'])
        if line is None:
            return (key, family, None, None, 'LIBC value breaks the grammar: "%s"' % vals['MEMFN_LIBC'])
        names, err = self.nm_names(cpath, workdir)
        if names is None:
            return (key, family, None, None, err)
        idiom = IDIOM in names
        control = sorted(names - {IDIOM} - DATA_OBJECTS)
        if control != line:
            return (key, family, line, idiom,
                    'LIBC "%s" but the compile calls "%s"'
                    % (vals['MEMFN_LIBC'], ','.join(control) or 'none'))
        return (key, family, line, idiom, None)

    def record(self, res):
        key, family, line, idiom, problem, nfunc = res
        self.n += 1
        self.funcs += nfunc
        self.family[family] = self.family.get(family, 0) + 1
        if problem:
            self.problems.append((key, problem))
            return
        if idiom:
            self.idiom += 1
        if not line:
            self.none += 1
        for name in line:
            self.calls[name] = self.calls.get(name, 0) + 1


def platform_decoration(cc, workdir):
    """The leading decoration nm prints on an undefined C symbol: a probe
    object that calls one function with a name nothing else uses."""
    src = os.path.join(workdir, 'probe.c')
    with open(src, 'w') as f:
        f.write('void c11_probe_callee(void);\nvoid c11_probe(void) { c11_probe_callee(); }\n')
    obj = src[:-2] + '.o'
    subprocess.run([cc, '-c', src, '-o', obj], check=True)
    out = subprocess.run(['nm', '-u', obj], capture_output=True, text=True).stdout
    for tok in out.split():
        if tok.endswith('c11_probe_callee'):
            return tok[:-len('c11_probe_callee')]
    raise SystemExit('FAIL: the probe object has no undefined c11_probe_callee')


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--pcrec', required=True)
    ap.add_argument('--tree', required=True)
    ap.add_argument('--cc', default='gcc')
    ap.add_argument('--jobs', type=int, default=min(8, os.cpu_count() or 4))
    ap.add_argument('--floor', action='append', default=[],
                    help='NAME=N: a population floor (K35)')
    ap.add_argument('--quick', action='store_true',
                    help='the default stream only (a sabotage solo)')
    a = ap.parse_args()
    floors = dict((k, int(v)) for k, v in (f.split('=', 1) for f in a.floor))

    sys.path.insert(0, os.path.join(a.tree, 'scripts'))
    import emit_sweep
    corpus = emit_sweep.enumerate_corpus(a.pcrec, a.tree, 30)
    seen = set()
    patterns = []
    for _, _, p in corpus:
        if p not in seen:
            seen.add(p)
            patterns.append(p)

    workdir = tempfile.mkdtemp(prefix='c11.')
    with open(os.path.join(workdir, 'prelude.h'), 'w') as f:
        f.write(PRELUDE)
    decor = platform_decoration(a.cc, workdir)
    print('== C11: <PREFIX>_MEMFN_FORMS / _MEMFN_LIBC over %d distinct corpus patterns '
          '(cc %s, nm decoration "%s") ==' % (len(patterns), a.cc, decor))
    cen = Census(a.cc, decor)
    for name, good, why in routing_shape.selftest():
        if good:
            ok('routing control: %s' % name)
        else:
            bad('routing control: %s reads %s' % (name, why or 'clean'))
    refused = 0
    ident = []

    def emit_one(job):
        idx, sname, extra, p = job
        cpath = os.path.join(workdir, 'a%d.c' % idx)
        argv = [a.pcrec, '-p', 'cxi', '--features', 'all'] + extra + ['-o', '-', '--pattern', p]
        try:
            r = subprocess.run(argv, capture_output=True, timeout=60)
        except subprocess.TimeoutExpired:
            return None
        if r.returncode != 0:
            return None
        text = r.stdout.decode('utf-8', 'surrogateescape')
        # the FORMS identity half, both layers: the same compile with the
        # SIMD switch stated OFF (a deny of the default) and turned ON must
        # each be byte-equal to the default while no SIMD form exists
        # (R-13: since the first SIMD rows, the ON half is the MOVERS half:
        # an ON artifact equals the default iff its FORMS reads "none")
        same, onforms = [], None
        for flag in ('-fno-memfn-simd', '-fmemfn-simd'):
            try:
                r2 = subprocess.run(argv[:-4] + [flag] + argv[-4:],
                                    capture_output=True, timeout=60)
            except subprocess.TimeoutExpired:
                r2 = None
            same.append(r2 is not None and r2.returncode == 0 and r2.stdout == r.stdout)
            if flag == '-fmemfn-simd' and r2 is not None and r2.returncode == 0:
                m = re.search(r'^#define \w+_MEMFN_FORMS "([^"]*)"$',
                              r2.stdout.decode('utf-8', 'surrogateescape'), re.M)
                onforms = m.group(1) if m else None
        ident.append((sname, p, same[0], same[1], onforms))
        with open(cpath, 'wb') as f:
            f.write(r.stdout)
        res = cen.one('%s:%r' % (sname, p[:60]), text, cpath, workdir)
        os.remove(cpath)
        return res

    streams = STREAMS[:1] if a.quick else STREAMS
    jobs = []
    for sname, extra, mod in streams:
        for p in patterns:
            if sampled(p, mod, sname):
                jobs.append((len(jobs), sname, extra, p))
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for res in ex.map(emit_one, jobs):
            if res is None:
                refused += 1
            else:
                cen.record(res)

    ncomp = 0
    if not a.quick:
        files = emit_sweep.find_files(a.tree, ('.rxt', '.rxtin'))

        def comp_one(job):
            idx, path = job
            out = os.path.join(workdir, 'comp%d' % idx)
            os.makedirs(out)
            try:
                subprocess.run([a.pcrec, '--features', 'all', path, '-o', out],
                               capture_output=True, timeout=120)
            except subprocess.TimeoutExpired:
                return []
            res = []
            for fn in sorted(os.listdir(out)):
                if fn.endswith('.c'):
                    cpath = os.path.join(out, fn)
                    with open(cpath, 'rb') as f:
                        text = f.read().decode('utf-8', 'surrogateescape')
                    rel = os.path.relpath(path, a.tree)
                    res.append(cen.one('comp:%s:%s' % (rel, fn), text, cpath, workdir))
            return res

        with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
            for rs in ex.map(comp_one, list(enumerate(files))):
                for r in rs:
                    ncomp += 1
                    cen.record(r)

    print('population: %d artifacts checked (%d of them composition artifacts with '
          'a header), %d sampled patterns refused by pcrec (not artifacts)'
          % (cen.n, ncomp, refused))
    print('families: %s' % ', '.join('%s %d' % kv for kv in sorted(cen.family.items())))
    print('routing: %d offset-skip/pre-check functions, each routed through its __body'
          % cen.funcs)
    print('LIBC values: %d none; idiom-memcpy artifacts %d; calls: %s'
          % (cen.none, cen.idiom, ', '.join('%s %d' % kv for kv in sorted(cen.calls.items()))))

    for key, problem in cen.problems[:40]:
        bad('%s: %s' % (key, problem))
    if len(cen.problems) > 40:
        bad('... and %d more artifacts' % (len(cen.problems) - 40))
    if not cen.problems:
        ok('routing, presence, grammar and LIBC == compile on all %d artifacts' % cen.n)

    counts = {'artifacts': cen.n, 'dfa': cen.family.get('dfa', 0),
              'vm': cen.family.get('vm', 0), 'composition': ncomp,
              'none': cen.none, 'idiom': cen.idiom, 'funcs': cen.funcs}
    counts.update(('calls-' + k, v) for k, v in cen.calls.items())
    for name, floor in sorted(floors.items()):
        got = counts.get(name, 0)
        if got >= floor:
            ok('floor %s: %d >= %d' % (name, got, floor))
        else:
            bad('floor %s: %d < %d (a population nobody counted, K35)' % (name, got, floor))
    differ = [(t[0], t[1]) for t in ident if not t[2]]
    for sn, p in differ[:40]:
        bad('FORMS identity (SIMD-off): %s:%r differs under -fno-memfn-simd' % (sn, p[:60]))
    if ident and not differ:
        ok('FORMS identity (SIMD-off): identical -- %d pattern-stream artifacts, default vs '
           '-fno-memfn-simd' % len(ident))
    # the MOVERS half (R-13, LIVE since the first SIMD rows): an ON artifact
    # differs from the default exactly where its FORMS is not "none"
    movers, wrong = 0, []
    for t in ident:
        if t[4] is None:
            wrong.append((t[0], t[1], 'no FORMS line under -fmemfn-simd'))
        elif (t[4] == 'none') != t[3]:
            wrong.append((t[0], t[1], 'FORMS %r but the artifact %s the default'
                          % (t[4], 'equals' if t[3] else 'differs from')))
        elif t[4] != 'none':
            movers += 1
    for sn, p, why in wrong[:40]:
        bad('FORMS movers (SIMD-on): %s:%r: %s' % (sn, p[:60], why))
    if ident and not wrong:
        ok('FORMS movers (SIMD-on): FORMS is not "none" exactly on the %d movers of %d '
           'pattern-stream artifacts' % (movers, len(ident)))
    if movers < MOVERS_FLOOR:
        bad('FORMS movers: %d SIMD-on movers < floor %d (a population nobody counted, K35)'
            % (movers, MOVERS_FLOOR))
    if not ident:
        bad('FORMS identity: no artifact was compared (a population nobody counted, K35)')

    subprocess.run(['rm', '-rf', workdir])
    print('checks passed: %d' % passed)
    print('checks failed: %d' % failed)
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
