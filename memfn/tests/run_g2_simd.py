#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (G2's SIMD family, lane
#   r13, R-13).
"""memfn/tests/run_g2_simd.py -- G2's SIMD FAMILY (R4e' batch 1, request R-13;
docs/design/memfn/integration.md §R4.9.7 "G2, the kit's own" and §R4.9.8's
"G2 per level" row). Run by run_g2.sh (both tiers) as its section 6, and on
its own:

    python3 memfn/tests/run_g2_simd.py [--root TREE] [--seed N] [--sites N] [--keep]

WHAT IT CHECKS, AND AGAINST WHAT
  1. THE SPACE (g2/g2_simd_gen.c): the batch-1 site shape and its negative
     controls, rendered through the kit at policy 0 with a sink that offers
     the bracket ops. Each class's MEMFN_FORMS value is held to CLASS_EXPECT
     (a table written HERE, sharing no source with the kit): the positive
     sites name the expected levels, every negative control (the OVER test's
     `fn-memchr` sites, a span proven short, -fno-memfn-simd's PORTABLE, two
     terms, a run past the shape bound, a sink without brackets) names none
     and writes 0 guarded bytes, and each row's own deny drops exactly its
     level. Population floors per class (K35).
  2. GUARDED_MAX: every rendering's guarded bytes, measured by G2's own
     counting sink at pcrec's placeholder prefix and longest FUNC name, are
     at most the sum of tests/memfn/simd_bounds.tsv's bounds of the levels
     its token names (Q-R9-9, D155 item 9). The maximum per token is printed.
  3. ANSWERS, PER LEVEL: the rendered file compiled at each level's
     `test_march` and around it (x86-64, x86-64-v3, x86-64-v4,
     -mgeneral-regs-only, and ASan+UBSan at x86-64 and x86-64-v3), with
     -Wall -Wextra -Werror, and run by g2/g2_simd_driver.c against G2's OWN
     scalar byte loop (exact returned position), guard pages at both ends,
     every span length 0..2*32+T+8, every alignment 0..31 (poisoned under
     ASan). Any failure or fault is red; checks per build >= a floor.
  4. PATHS: an instrumented copy (THIS script's text edits of the rendered
     file: a counter at each helper's entry fall-through, whole block, final
     block and verified return) at x86-64 and x86-64-v3; per live level each
     path >= PATH_FLOOR, and a compiled-out level's paths EXACTLY 0.
  5. PLANTS, per path and level: the rendered text mutated (the final block's
     guard off by one, the lane mask off by one, lanes highest first, the
     verify skipped, the reach one short); each must be RED where its level is
     live and GREEN where it is compiled out; the reach plant must FAULT.
  6. INSTRUCTION CLASSES: no PDEP/PEXT and no gather in any level's object
     (levels.def's `forbid`, [r9 M-11]), read with objdump.

Prints `checks passed: N` / `checks failed: N`; exit 1 on any failure.
"""
import argparse
import concurrent.futures
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# --- the expectations and floors: literals, written here --------------------
# The levels each class's FUNC must render (MEMFN_FORMS' token), given the
# rows that exist: vrun-w32 over vrun-w16, both over fn-pair only.
CLASS_EXPECT = {
    'pos': 'vrun@w32+w16',
    'deny-w32': 'vrun@w16',
    'deny-w16': 'vrun@w32',
    'neg-exact': 'none',
    'neg-short': 'none',
    'neg-portable': 'none',
    'neg-two': 'none',
    'neg-long': 'none',
    'neg-nobrackets': 'none',
}
CLASS_FLOOR = 8          # sites per class (each negative class is 1 in 20)
POS_FLOOR = 200          # positive sites
CHECK_FLOOR = 17000000   # answer checks per build: 19,167,946 measured
ASAN_CHECK_FLOOR = 17000000   # (Linux dev box, seed 20261009, 400 sites), ~90%
PATH_FLOOR = 1000        # executions of each path at a live level
# the level a build makes live (top first), and whether w16/w32 is live
BUILDS = [
    # name,        flags,                      live levels
    ('x86-64',     ['-march=x86-64'],          {'w16'}),
    ('x86-64-v3',  ['-march=x86-64-v3'],       {'w16', 'w32'}),
    ('x86-64-v4',  ['-march=x86-64-v4'],       {'w16', 'w32'}),
    ('gpr-only',   ['-mgeneral-regs-only'],    set()),
]
ASAN_BUILDS = [
    ('asan-x86-64',    ['-march=x86-64']),
    ('asan-x86-64-v3', ['-march=x86-64-v3']),
]

passed = failed = 0
notes = []


def ok():
    global passed
    passed += 1


def bad(msg):
    global failed
    failed += 1
    notes.append(msg)
    print('FAIL: ' + msg)


def sh(cmd, timeout=900, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kw)


def load_bounds(root):
    b = {}
    with open(os.path.join(root, 'tests', 'memfn', 'simd_bounds.tsv')) as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            k, v = line.rstrip('\n').split('\t')
            b[k] = int(v)
    return b


def token_bound(tok, bounds):
    """The sum of the row bounds a MEMFN_FORMS token names
    (`form@lvl+lvl`: row `form-lvl` per level)."""
    form, _, levels = tok.partition('@')
    total = 0
    for lv in levels.split('+'):
        row = '%s-%s' % (form, lv)
        if row not in bounds:
            return None
        total += bounds[row]
    return total


# --- the instrumentation and the plants: text edits of the rendered file ----
HELPER = re.compile(r'^static inline size_t (\w+)__(w16|w32)\(.*?^\}\n', re.M | re.S)


def edit_helpers(text, level, fn):
    """Applies fn(body, lvl_index) to every helper of `level` ('w16', 'w32',
    or None for both)."""
    def sub(m):
        if level and m.group(2) != level:
            return m.group(0)
        return fn(m.group(0), 0 if m.group(2) == 'w16' else 1)
    return HELPER.sub(sub, text)


def instrument(body, li):
    b = 4 * li
    body, n0 = re.subn(r'(\) return )(\w+\(subject, n, pos\);)',
                       r') { g2v_path[%d]++; return \2 }' % b, body, count=1)
    body, n1 = re.subn(r'(        if \(i \+ \d+ <= n\) \{)', r'\1 g2v_path[%d]++;' % (b + 1), body)
    body, n2 = re.subn(r'(            size_t f = n - \d+;)', r'g2v_path[%d]++; \1' % (b + 2), body)
    body, n3 = re.subn(r'\) return cand;', r') { g2v_path[%d]++; return cand; }' % (b + 3), body)
    if (n0, n1, n2, n3) != (1, 1, 1, 1):
        raise RuntimeError('instrumentation found %r edit points, not one each' % ((n0, n1, n2, n3),))
    return body


PLANTS = [
    # name, the helper edit (regex, replacement), expectation: 'red' or 'fault'
    ('final-guard', r'if \(i \+ (\d+) >= n\) return n;', r'if (i + \1 + 1 >= n) return n;', 'red'),
    ('lane-mask',   r'\(~0u << \(i - f\)\)', r'(~0u << (i - f + 1))', 'red'),
    ('lane-order',  r'__builtin_ctz\(m\)', r'(31 - __builtin_clz(m))', 'red'),
    ('no-verify',   r'if \((?:\(|\w)[^\n]*\) return cand;', r'if (1) return cand;', 'red'),
    ('reach-short', None, None, 'fault'),
]


def reach_short(body, li):
    """Every use of the reach R (VW + T) becomes R - 1: the vector body then
    reads one byte past n at the shortest span it accepts."""
    m = re.search(r'n - pos < (\d+)\)', body)
    r = int(m.group(1))
    body = body.replace('n - pos < %d)' % r, 'n - pos < %d)' % (r - 1))
    body = body.replace('if (i + %d <= n)' % r, 'if (i + %d <= n)' % (r - 1))
    body = body.replace('size_t f = n - %d;' % r, 'size_t f = n - %d;' % (r - 1))
    return body


def plant_text(text, plant, level):
    name, pat, rep, _ = plant
    if pat is None:
        return edit_helpers(text, level, reach_short)
    def f(body, li):
        nb, k = re.subn(pat, rep, body, count=1)
        if k != 1:
            raise RuntimeError('plant %s: no edit point' % name)
        return nb
    return edit_helpers(text, level, f)


_CACHE = {}


def prefetch(work, root, jobs, nworkers):
    """Builds and runs every (name, path, flags, asan) job concurrently; the
    loops below read the results by name (build_run's cache)."""
    with concurrent.futures.ThreadPoolExecutor(nworkers) as ex:
        futs = {ex.submit(_build_run, work, root, *j): j[0] for j in jobs}
        for f in concurrent.futures.as_completed(futs):
            _CACHE[futs[f]] = f.result()


def build_run(work, root, name, sites_c, flags, asan=False):
    if name in _CACHE:
        return _CACHE[name]
    return _build_run(work, root, name, sites_c, flags, asan)


def _build_run(work, root, name, sites_c, flags, asan=False, extra_cflags=()):
    g2 = os.path.join(HERE, 'g2')
    exe = os.path.join(work, 'drv-' + name)
    san = ['-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-g'] if asan else []
    cc = ['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', g2] + flags + san + list(extra_cflags)
    r = sh(cc + ['-o', exe, os.path.join(g2, 'g2_simd_driver.c'), sites_c])
    if r.returncode:
        return None, 'compile failed: ' + r.stderr[-2000:]
    env = dict(os.environ)
    if asan:
        env['ASAN_OPTIONS'] = 'detect_leaks=0:allow_user_segv_handler=1'
    r = sh(['taskset', '-c', os.environ.get('G2V_CPUS', '12-15'), exe], timeout=1800, env=env)
    return r, None


def parse(out):
    m = re.search(r'G2V checks=(\d+) fail=(\d+) faults=(\d+)', out)
    paths = {}
    for p in re.finditer(r'G2V paths level=(w\d+) entry_fallthrough=(\d+) whole_block=(\d+) '
                         r'final_block=(\d+) verified=(\d+)', out):
        paths[p.group(1)] = tuple(int(x) for x in p.groups()[1:])
    return (tuple(int(x) for x in m.groups()) if m else None), paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=os.path.dirname(os.path.dirname(HERE)))
    ap.add_argument('--seed', default='20261009')
    ap.add_argument('--sites', type=int, default=400)
    ap.add_argument('--keep', action='store_true')
    ap.add_argument('--lib', help='the kit library the generator links (run_g2.sh --rows: '
                    'build/libpcrec_mftrace.a)')
    ap.add_argument('--reach-err', help="write the generator's stderr here (its MFTRACE "
                    "REACH lines join run_g2.sh's per-row sum)")
    ap.add_argument('--quick', action='store_true',
                    help='the plants at the x86-64 / x86-64-v3 / gpr-only builds only, '
                    'ASan at x86-64-v3 only (run_g2.sh --quick)')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    work = tempfile.mkdtemp(prefix='g2simd.', dir=os.environ.get('TMPDIR'))
    try:
        run(a, root, work)
    finally:
        if a.keep:
            print('kept: ' + work)
        else:
            shutil.rmtree(work, ignore_errors=True)
    print('checks passed: %d' % passed)
    print('checks failed: %d' % failed)
    return 1 if failed else 0


def run(a, root, work):
    g2 = os.path.join(HERE, 'g2')
    gen = os.path.join(work, 'gen')
    r = sh(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', os.path.join(root, 'memfn', 'include'),
            '-o', gen, os.path.join(g2, 'g2_simd_gen.c'),
            a.lib or os.path.join(root, 'build', 'libpcrec.a')])
    if r.returncode:
        bad('generator build failed: ' + r.stderr[-2000:])
        return
    r = sh([gen, a.seed, str(a.sites), work])
    if a.reach_err:
        open(a.reach_err, 'w').write(r.stderr)
    if r.returncode:
        bad('generator failed: ' + r.stderr[-2000:])
        return
    ok()
    # 1-2: the classes and the bounds
    bounds = load_bounds(root)
    counts, maxg = {}, {}
    with open(os.path.join(work, 'g2v_meta.tsv')) as f:
        for line in f:
            if line.startswith('#'):
                continue
            sid, cls, L, off, pp, forms, gb, a16, a32 = line.rstrip('\n').split('\t')
            gb = int(gb)
            # each row rendered ALONE against its own bound
            for row, alone in (('vrun-w16', int(a16)), ('vrun-w32', int(a32))):
                if alone < 0:
                    continue
                maxg['alone:' + row] = max(maxg.get('alone:' + row, 0), alone)
                if row not in bounds or alone > bounds[row]:
                    bad('site %s (L=%s): %s alone writes %d guarded bytes > bound %s'
                        % (sid, L, row, alone, bounds.get(row)))
            counts[cls] = counts.get(cls, 0) + 1
            want = CLASS_EXPECT.get(cls)
            if forms != want:
                bad('site %s (%s, L=%s): MEMFN_FORMS %r, expected %r' % (sid, cls, L, forms, want))
                continue
            if forms == 'none':
                if gb != 0:
                    bad('site %s (%s): %d guarded bytes with no SIMD form' % (sid, cls, gb))
                    continue
            else:
                lim = token_bound(forms, bounds)
                if lim is None:
                    bad('site %s: token %r has an undeclared row in simd_bounds.tsv' % (sid, forms))
                    continue
                if gb > lim:
                    bad('site %s (L=%s): %d guarded bytes > bound %d (%s)' % (sid, L, gb, lim, forms))
                    continue
                maxg[forms] = max(maxg.get(forms, 0), gb)
            ok()
    for cls in CLASS_EXPECT:
        n = counts.get(cls, 0)
        fl = POS_FLOOR if cls == 'pos' else CLASS_FLOOR
        print('class %-15s %4d sites (floor %d), expect %s' % (cls, n, fl, CLASS_EXPECT[cls]))
        if n < fl:
            bad('class %s: %d sites < floor %d' % (cls, n, fl))
        else:
            ok()
    for tok, g in sorted(maxg.items()):
        lim = bounds.get(tok[6:]) if tok.startswith('alone:') else token_bound(tok, bounds)
        print('guarded bytes: %s max %d (bound %s)' % (tok, g, lim))
    sites_c = os.path.join(work, 'g2v_sites.c')
    text = open(sites_c).read()
    # every build of sections 3-5, prefetched concurrently (each driver run is
    # pinned to G2V_CPUS; the results are judged below in order)
    inst = os.path.join(work, 'g2v_sites_paths.c')
    open(inst, 'w').write(edit_helpers(text, None, instrument))
    jobs = [(n, sites_c, f, False) for n, f, _ in BUILDS]
    jobs += [(n, sites_c, f, True) for n, f in (ASAN_BUILDS[1:] if a.quick else ASAN_BUILDS)]
    jobs += [('paths-' + n, inst, f, False) for n, f, _ in BUILDS if n != 'x86-64-v4']
    levels = sorted({lv for _, _, live in BUILDS for lv in live})
    plant_files = {}
    for plant in PLANTS:
        for lv in levels:
            pt = os.path.join(work, 'plant-%s-%s.c' % (plant[0], lv))
            try:
                open(pt, 'w').write(plant_text(text, plant, lv))
            except RuntimeError as e:
                bad('plant %s %s: %s' % (plant[0], lv, e))
                continue
            plant_files[(plant[0], lv)] = pt
            for n, f, _ in BUILDS:
                if n != 'x86-64-v4':
                    jobs.append(('plant-%s-%s-%s' % (plant[0], lv, n), pt, f, False))
    prefetch(work, root, jobs, int(os.environ.get('G2V_JOBS', '4')))
    # 3: answers per level
    for name, flags, live in BUILDS:
        r, err = build_run(work, root, name, sites_c, flags)
        if err:
            bad('%s: %s' % (name, err))
            continue
        res, _ = parse(r.stdout)
        print('build %-15s %s' % (name, r.stdout.splitlines()[0] if r.stdout else r.stderr[-300:]))
        if not res or r.returncode or res[1] or res[2]:
            bad('%s: answers %s rc=%d %s' % (name, res, r.returncode, r.stderr[-1500:]))
        elif res[0] < CHECK_FLOOR:
            bad('%s: %d checks < floor %d' % (name, res[0], CHECK_FLOOR))
        else:
            ok()
    for name, flags in (ASAN_BUILDS[1:] if a.quick else ASAN_BUILDS):
        r, err = build_run(work, root, name, sites_c, flags, asan=True)
        if err:
            bad('%s: %s' % (name, err))
            continue
        res, _ = parse(r.stdout)
        print('build %-15s %s' % (name, r.stdout.splitlines()[0] if r.stdout else r.stderr[-300:]))
        if not res or r.returncode or res[1] or res[2]:
            bad('%s: answers %s rc=%d %s' % (name, res, r.returncode, r.stderr[-1500:]))
        elif res[0] < ASAN_CHECK_FLOOR:
            bad('%s: %d checks < floor %d' % (name, res[0], ASAN_CHECK_FLOOR))
        else:
            ok()
    # 4: paths
    for name, flags, live in BUILDS[:2] + BUILDS[3:]:
        r, err = build_run(work, root, 'paths-' + name, inst, flags)
        if err:
            bad('paths %s: %s' % (name, err))
            continue
        res, paths = parse(r.stdout)
        for lv in ('w16', 'w32'):
            p = paths.get(lv, (0, 0, 0, 0))
            print('paths %-10s %s entry=%d whole=%d final=%d verified=%d' % ((name, lv) + p))
            if lv in live and any(x < PATH_FLOOR for x in p):
                bad('paths %s %s: a path below floor %d: %r' % (name, lv, PATH_FLOOR, p))
            elif lv not in live and any(p):
                bad('paths %s %s: a compiled-out level ran: %r' % (name, lv, p))
            else:
                ok()
    # 5: plants
    for plant in PLANTS:
        for lv in levels:
            pt = plant_files.get((plant[0], lv))
            if not pt:
                continue
            for name, flags, live in BUILDS:
                if name == 'x86-64-v4':
                    continue
                r, err = build_run(work, root, 'plant-%s-%s-%s' % (plant[0], lv, name), pt, flags)
                if err:
                    bad('plant %s %s %s: %s' % (plant[0], lv, name, err))
                    continue
                res, _ = parse(r.stdout)
                # a w16 plant at x86-64-v3 is live through w32's fall-through
                # (spans between the two reaches): red there too
                red = bool(res and (res[1] or res[2]))
                fault = bool(res and res[2])
                if lv in live:
                    if not red or (plant[3] == 'fault' and not fault):
                        bad('plant %s (%s) at %s: NOT DETECTED %r' % (plant[0], lv, name, res))
                    else:
                        ok()
                else:
                    if red:
                        bad('plant %s (%s) at %s: red where the level is compiled out %r'
                            % (plant[0], lv, name, res))
                    else:
                        ok()
                print('plant %-12s %s at %-10s -> %s' % (plant[0], lv, name,
                      'RED' if red else 'green'))
    # 6: instruction classes
    for name, flags, live in BUILDS:
        obj = os.path.join(work, 'insn-%s.o' % name)
        r = sh(['gcc', '-O2', '-c', '-I', g2] + flags + ['-o', obj, sites_c])
        if r.returncode:
            bad('insn %s: compile failed' % name)
            continue
        d = sh(['objdump', '-d', '--no-show-raw-insn', obj]).stdout
        hits = re.findall(r'\b(pdep|pext|v?p?gather\w*)\b', d)
        if hits:
            bad('insn %s: forbidden instruction class used: %s' % (name, sorted(set(hits))))
        else:
            ok()


if __name__ == '__main__':
    sys.exit(main())
