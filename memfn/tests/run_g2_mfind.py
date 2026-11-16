#!/usr/bin/env python3
# SPDX-License-Identifier: 0BSD
# Provenance: original pcrec-memory-functions text (G2's one-member family,
#   lane mfind).
"""memfn/tests/run_g2_mfind.py -- G2's ONE-MEMBER family: the inline
one-member finder (memfn/src/vrun.c, "THE INLINE ONE-MEMBER FINDER", lane
mfind), reached only through the test-only lever `mf_lever(art, "mfind")`,
at its site, the offset-skip FUNC site (memfn/src/ofsskip.c). Run by
run_g2.sh (both tiers) as its section 4z, and on its own:

    python3 memfn/tests/run_g2_mfind.py [--root TREE] [--lib LIBPCREC.A] [--seed N]
                                        [--sites N] [--keep] [--quick]

Written by the form's author (not D27-blinded): its independent controls
are G2's own scalar loop over the predicate AS DRAWN, the generated space,
the guard pages and the per-plant classes below.

WHAT IT CHECKS, AND AGAINST WHAT
  1. THE SPACE (g2/g2_mfind_gen.c): offset-skip FUNC sites whose scanned
     position is ONE exact byte (a scanned SET {a} at k 0..12, or the exact
     byte of a RUN at its position), 0..3 other terms (singleton SET,
     multi-member SET through a table, one RUN of 2..12 bytes, some
     caseless) at offsets 0..16; a fixed head (a = 0x00, 0x80, 0xFF, 0x7F,
     0x01, 0xFE, 'a', 'x', 0x20, 0xDF at four shapes) then random. Rendered
     per target (x86-64-v3, x86-64, generic) with the lever (LEVER 1) and
     without it (LEVER 0, the control: fn-memchr), one file each; the host's
     frame (family guard, `mf_includes` lines, region) is G2's. The site
     SHAPES (r2 F12): a pre-check composite's FUNC part, policy INLOOP and
     policy SIZE sites beside the plain FIND, census-floored. STRUCTURAL
     (literals written in the generator, not read from the kit): under the
     lever each site holds the helpers exactly per target (x86-64-v3: w16 +
     w32; x86-64: w16; generic: none; none on an INLOOP site), its __body holds `memcpy(&w` and no
     `memchr(`, no CPU conditional and no `#include`; without it the site's
     function holds `memchr(` and no `memcpy(&w`. The generator prints the
     alone maximum of guarded bytes per level (`G2M guarded <level> N`).
  2. ANSWERS, PER BUILD: each file compiled -O2 -Wall -Wextra -Werror (the
     x86-64-v3 file at -march=x86-64, where the region supplies the ISA, and
     at -march=x86-64-v3; the x86-64 file at -march=x86-64; the generic
     file at -mgeneral-regs-only; ASan+UBSan on the v3 file; the lever-0
     control files) and run by g2/g2_mfind_driver.c against ITS OWN scalar
     loop (the leftmost c with c + maxk < n at which every term holds): every
     n 0..73, a passing candidate at every position, the MASK STREAM (failing
     hits before and just below the passing one, in one block), the SWAR
     EXACTNESS TRAP (a failing hit followed by a ^ 1 where the other terms
     pass at the next position), every alignment, guard pages at s + n and
     below s + pos. A wrong answer or a fault is red; per-build floors on the
     checks and on the stream/trap populations (K35).
  3. PLANTS: the rendered lever-1 text mutated per helper (each edit counted
     and applied exactly the stated times per helper); each plant has an
     id and an expected class: FAULT (a signal: a read bound moved), LOUD
     (a wrong answer), SAME (the answers cannot move; the plant must stay
     GREEN, printed `SAME (expected)`). A plant that does not land in its
     expected class is a failure (`MISSED` where a red plant stayed green).
  4. INSTRUCTION CLASSES: no PDEP/PEXT and no gather in the x86-64-v3 driver.
On a host that cannot run a level, its builds are BUILT, not run: printed
`SKIPPED ARM <level>: <why>; N checks NOT run`, never a silent pass.

Prints `checks passed: N` / `checks failed: N`; exit 1 on any failure.
"""
import argparse
import concurrent.futures
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# --- the expectations and floors: literals, written here --------------------
# the register width of each level (and of the SWAR word), written HERE
VW = {'w16': 16, 'w32': 32, 'body': 8}
# the targets rendered at, and the levels each admits (target_seam_units.md §2)
TARGETS = {'x86-64-v3': {'w16', 'w32'}, 'x86-64': {'w16'}, 'generic': set()}
# a build: name, (target, lever) of the file it compiles, flags, host need
BUILDS = [
    ('v3-x86-64',   ('x86-64-v3', 1), ['-O2', '-march=x86-64'],       'x86-64-v3'),
    ('x86-64-v3',   ('x86-64-v3', 1), ['-O2', '-march=x86-64-v3'],    'x86-64-v3'),
    ('x86-64',      ('x86-64', 1),    ['-O2', '-march=x86-64'],       None),
    ('gpr-only',    ('generic', 1),   ['-O2', '-mgeneral-regs-only'], None),
    ('asan-x86-64-v3', ('x86-64-v3', 1), ['-O1', '-march=x86-64-v3', '-fsanitize=address,undefined',
                                          '-fno-sanitize-recover=all', '-fno-omit-frame-pointer'],
     'x86-64-v3'),
    # the lever-0 control: the same sites through fn-memchr, the driver's
    # reference unchanged
    ('l0-x86-64-v3', ('x86-64-v3', 0), ['-O2', '-march=x86-64-v3'],  'x86-64-v3'),
    ('l0-generic',  ('generic', 0),   ['-O2', '-mgeneral-regs-only'], None),
]
NEEDS = {'x86-64-v3': 'AVX2'}
# answer checks per build at 80 sites (--quick): 13,172,320 measured (Linux
# dev box, 2026-11-14, seed 20261114; 164,654 per site; the default 160
# sites doubles it); the floor is ~80% of it per 80 sites
CHECK_FLOOR_80 = 10500000
# r2 F10 (lane mfindfix2): subjects holding the scanned byte past the last
# valid candidate, every term that fits below n passing (the driver's
# `beyond`); ~80% of the measured count
BEYOND_FLOOR_80 = 2040000   # 2,553,909 measured (Linux dev box, 2026-11-15, seed
                            # 20261114); the old planter's chance population was 4,463
# the driver's census populations per build at 80 sites, ~80% of measured
# (each measurement in a comment); they scale with the sites
DRV_FLOOR_80 = {
    'hits':    4800000,    # an answer found: 6,065,850 measured
    'stream1': 1500000,    # >= 1 failing hit within 7 below the answer: 1,902,986
    'stream2': 440000,     # >= 2 of them: 557,955
    'trap':    1800000,    # the exactness trap present AND the answer not the trap: 2,235,092
    'late':    1300000,    # the answer in the last 8 candidate positions: 1,687,120
    'beyond':  BEYOND_FLOOR_80,   # r2 F10: a scanned byte in [e, n) whose fitting terms pass
}
# the space's populations at 80 sites per file (the same space at each of
# three targets, so x3; lever 1 only unless stated): ~80% of measured
# (each measurement in a comment); they do not scale up (the fixed head is
# 40 of the sites)
POP_FLOOR = {
    'sites': 384,          # 480: lever 1 and lever 0 files, three targets
    'scan-set': 146,       # 183
    'scan-run': 45,        # 57
    'd0': 64,              # 81: maxk == k, the scanned byte is the farthest read
    'dpos': 127,           # 159: maxk > k
    'k0': 36,              # 45: the scanned offset 0
    'k8plus': 72,          # 90: the scanned offset >= 8
    'multi': 81,           # 102: a table (multi-member SET) term
    'run': 110,            # 138: a RUN term anywhere
    'caseless': 26,        # 33: a caseless RUN
    'nterm1': 28, 'nterm2': 110, 'nterm3': 33, 'nterm4': 19,   # 36 / 138 / 42 / 24
    'a00': 16, 'a80': 12, 'aff': 14, 'a7f': 21, 'a01': 16, 'afe': 16,   # 21 15 18 27 21 21
    # r2 F12 (lane mfindfix2): the site shapes beyond FIND/FUNC (g2_mfind_gen.c
    # THE SITE SHAPES; by id, no RNG draw, x3 targets)
    'pre': 4,              # 6: a pre-check composite's FUNC part (odd RUN-scanned ids: 2 per file)
    'inloop': 12,          # 15: policy INLOOP (the SIMD rows decline; helpers absent)
    'size': 12,            # 15: policy SIZE (served; helpers render)
}
# PLANTS: id, name, expected class, {helper kind: (mode, old, new, per)}
# (mode 'str': plain text, 'rx': a regex over the helper; `per` = exactly
# this many matches in each helper of the kind it is applied to; a NEGATIVE
# per = 0 or -per matches in each, at least one helper matched: a spelling
# only some sites write).
# S3150/S3151 are RUNAWAY witnesses (review 2026-11-15 r2 F9): their edit
# breaks the loop's exit (`i += VW` lands past e, `e - i` wraps), so they
# fault with no guard page at all and prove only that the exit test exists.
# The one-byte BOUND is S3173 (every spelling of e) and S3174 (the D > 0
# spelling `n - D` alone, r2 F10): the top bound moved by ONE byte with the
# loop still terminating, so only the guard page at s + n can see it (S3174
# through the verify chain's read past n, the driver's `beyond` subjects).
# S3153 is a SPECIFICITY CONTROL and a text pin (r2 F11), not a check of its
# property: a lane handed over twice is rejected again by the pure check, so
# the answers cannot move (SAME); the cost it saves is counted by nothing.
# A LOUD plant may also FAULT (r2 F13): a wrong lane can send the check's
# reads out of bounds first (S3158 measured 354 FAULT / 22 MOVE in 1,500).
PLANTS = [
    ('S3150', 'final-late', 'FAULT', {
        'w16': ('str', 'const size_t f = e - 16;', 'const size_t f = e - 16 + 1;', 1),
        'w32': ('str', 'const size_t f = e - 32;', 'const size_t f = e - 32 + 1;', 1),
        'body': ('str', 'const size_t f = e - 8;', 'const size_t f = e - 8 + 1;', 1)}),
    ('S3151', 'loop-past', 'FAULT', {
        'w16': ('str', 'if (e - i >= 16) {', 'if (e - i >= 15) {', 1),
        'w32': ('str', 'if (e - i >= 32) {', 'if (e - i >= 31) {', 1),
        'body': ('str', 'if (e - i >= 8) {', 'if (e - i >= 7) {', 1)}),
    ('S3152', 'entry-short', 'FAULT', {
        'w16': ('str', ' < 16)\n', ' < 15)\n', 1),
        'w32': ('str', ' < 32)\n', ' < 31)\n', 1)}),
    ('S3153', 'no-final-mask', 'SAME', {
        'w16': ('rx', r'^ *m &= ~0u << \(i - f\);\n', '', 1),
        'w32': ('rx', r'^ *m &= ~0u << \(i - f\);\n', '', 1),
        'body': ('rx', r'^ *m &= ~0ull << \(\(i - f\) << 3\);\n', '', 1)}),
    ('S3154', 'swar-classic', 'LOUD', {
        'body': ('str',
                 'm = ~(((w & 0x7f7f7f7f7f7f7f7full) + 0x7f7f7f7f7f7f7f7full) | w) & 0x8080808080808080ull;',
                 'm = (w - 0x0101010101010101ull) & ~w & 0x8080808080808080ull;', 2)}),
    ('S3155', 'high-lane', 'LOUD', {
        'w16': ('str', '__builtin_ctz(m)', '(31 - __builtin_clz(m))', 1),
        'w32': ('str', '__builtin_ctz(m)', '(31 - __builtin_clz(m))', 1),
        'body': ('str', '__builtin_ctzll(m)', '(63 - __builtin_clzll(m))', 1)}),
    ('S3156', 'stream-drop', 'LOUD', {
        'w16': ('str', 'm &= m - 1;', 'm = 0;', 1),
        'w32': ('str', 'm &= m - 1;', 'm = 0;', 1),
        'body': ('str', 'm &= m - 1;', 'm = 0;', 1)}),
    ('S3157', 'body-short', 'FAULT', {
        'body': ('str', 'if (e - i < 8) {', 'if (e - i < 7) {', 1)}),
    ('S3158', 'lane-shift', 'LOUD', {
        'body': ('str', '__builtin_ctzll(m) >> 3', '__builtin_ctzll(m) >> 2', 1)}),
    ('S3159', 'endian', 'LOUD', {
        'body': ('str', '__BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__',
                 '__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__', 2)}),
    ('S3173', 'top-one-byte', 'FAULT', {
        'w16': ('rx', r'^( *const size_t e = n(?: - \d+)?);', r'\1 + 1;', 1),
        'w32': ('rx', r'^( *const size_t e = n(?: - \d+)?);', r'\1 + 1;', 1),
        'body': ('rx', r'^( *const size_t e = n(?: - \d+)?);', r'\1 + 1;', 1)}),
    ('S3174', 'top-one-byte-dpos', 'FAULT', {
        'w16': ('rx', r'^( *const size_t e = n - \d+);', r'\1 + 1;', -1),
        'w32': ('rx', r'^( *const size_t e = n - \d+);', r'\1 + 1;', -1),
        'body': ('rx', r'^( *const size_t e = n - \d+);', r'\1 + 1;', -1)}),
]
# the classes each expected class accepts as RED (r2 F13)
ACCEPT = {'FAULT': {'FAULT'}, 'LOUD': {'LOUD', 'FAULT'}, 'SAME': {'SAME'}}
GREEN_STRIDE = '5'       # a SAME plant runs every 5th site

passed = failed = 0
SKIPPED = {}


def ok():
    global passed
    passed += 1


def bad(msg):
    global failed
    failed += 1
    print('FAIL: ' + msg)


def sh(cmd, timeout=300):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


PROBE_C = '''#include <stdio.h>
int main(void)
{
    __builtin_cpu_init();
    printf("x86-64-v3 %d\\n", __builtin_cpu_supports("x86-64-v3") != 0);
    return 0;
}
'''


def host_skips(work):
    """The levels this host cannot run: the compiler's own level definition,
    probed at plain -march=x86-64; G2M_SKIP_ARMS=x86-64-v3 forces a skip."""
    skip = {}
    src, exe = os.path.join(work, 'probe.c'), os.path.join(work, 'probe')
    open(src, 'w').write(PROBE_C)
    r = sh(['gcc', '-O0', '-march=x86-64', '-o', exe, src])
    if r.returncode:
        sys.exit('run_g2_mfind: host-level probe failed to build: ' + r.stderr[-500:])
    r = sh([exe])
    host = dict(l.split() for l in r.stdout.splitlines())
    if r.returncode or set(host) != set(NEEDS):
        sys.exit('run_g2_mfind: host-level probe failed to run: rc=%d %r' % (r.returncode, r.stdout))
    for lv, need in NEEDS.items():
        if host[lv] != '1':
            skip[lv] = 'host lacks %s' % need
    for lv in filter(None, os.environ.get('G2M_SKIP_ARMS', '').replace(' ', '').split(',')):
        if lv not in NEEDS:
            sys.exit('run_g2_mfind: G2M_SKIP_ARMS=%s: only %s can be skipped' % (lv, sorted(NEEDS)))
        skip[lv] = 'forced by G2M_SKIP_ARMS (%s)' % NEEDS[lv]
    return skip


HELPER = re.compile(r'static inline size_t (g2m_\d+)__(w16|w32|body)\(.*?\n\}\n', re.S)


def plant_text(text, kind, mode, old, new, per):
    """The text with the edit applied inside every helper of `kind`; None
    unless it matched exactly `per` times in each, and in at least one."""
    out, last, nhelp = [], 0, 0
    for m in HELPER.finditer(text):
        if m.group(2) != kind:
            continue
        if mode == 'str':
            c = m.group(0).count(old)
            rep = m.group(0).replace(old, new)
        else:
            rep, c = re.subn(old, new, m.group(0), flags=re.M)
        if c != per and not (per < 0 and c in (0, -per)):
            return None
        if c == 0:
            continue
        nhelp += 1
        out.append(text[last:m.start()])
        out.append(rep)
        last = m.end()
    out.append(text[last:])
    return ''.join(out) if nhelp else None


def build(work, name, flags, sites, tag, extra=()):
    exe = os.path.join(work, 'drv-%s-%s' % (name, tag))
    r = sh(['gcc'] + flags + ['-Wall', '-Wextra', '-Werror'] + list(extra) +
           ['-DG2M_SITES="%s"' % sites, '-o', exe, os.path.join(HERE, 'g2', 'g2_mfind_driver.c')])
    return exe, r


def run_drv(exe, args, asan):
    env = dict(os.environ)
    if asan:
        env['ASAN_OPTIONS'] = 'detect_leaks=0'
    r = subprocess.run([exe] + args, capture_output=True, text=True, timeout=300, env=env)
    cnt = dict((m.group(1), int(m.group(2))) for m in re.finditer(r'^(\w+) (\d+)$', r.stdout, re.M))
    return r, cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=os.path.dirname(os.path.dirname(HERE)))
    ap.add_argument('--seed', default='20261114')
    ap.add_argument('--sites', type=int, default=None)
    ap.add_argument('--lib', help='the kit library the generator links')
    ap.add_argument('--keep', action='store_true')
    ap.add_argument('--reach-err', help="write every generator process's stderr here (the MF_TRACE "
                    "kit's MFTRACE REACH lines join run_g2.sh's per-row sum, as the SIMD family's do)")
    ap.add_argument('--plants', dest='plants', action='store_true', default=True)
    ap.add_argument('--no-plants', dest='plants', action='store_false')
    ap.add_argument('--quick', action='store_true', help='a smaller space (80 sites per file, '
                    'one build per file for the plants); the tier default is 160')
    a = ap.parse_args()
    if a.sites is None:
        a.sites = 80 if a.quick else 160
    if a.sites < 80:
        # the population floors were measured at 80 sites and scale to 0 at 40
        # (every floor vacuous): below 80 no floor is a check (review r6 CHECKS-A3)
        ap.error('--sites %d: below 80 the population floors are not checks' % a.sites)
    root = os.path.abspath(a.root)
    work = tempfile.mkdtemp(prefix='g2mfind.', dir=os.environ.get('TMPDIR'))
    try:
        run(a, root, work)
    finally:
        if a.keep:
            print('kept: ' + work)
        else:
            shutil.rmtree(work, ignore_errors=True)
    for lv, (why, n) in sorted(SKIPPED.items()):
        print('SKIPPED ARM %s: %s; %d checks NOT run (built, not run)' % (lv, why, n))
    print('skipped arms: %d' % len(SKIPPED))
    print('checks passed: %d' % passed)
    print('checks failed: %d' % failed)
    return 1 if failed else 0


def population(meta, pop):
    for line in open(meta):
        kid, nterm, kind, k, maxk, av, ntbl, nrun, ncl, tg, lv, shape = line.rstrip('\n').split('\t')
        k, maxk, av = int(k), int(maxk), int(av)
        pop['sites'] += 1
        if lv != '1':
            continue
        pop['scan-' + kind.lower()] += 1
        pop['d0'] += maxk == k
        pop['dpos'] += maxk > k
        pop['k0'] += k == 0
        pop['k8plus'] += k >= 8
        pop['multi'] += int(ntbl) > 0
        pop['run'] += int(nrun) > 0
        pop['caseless'] += int(ncl) > 0
        pop['nterm' + nterm] += 1
        if shape != 'fn':
            pop[shape] += 1
        for key, v in (('a00', 0), ('a80', 0x80), ('aff', 0xFF), ('a7f', 0x7F), ('a01', 1), ('afe', 0xFE)):
            pop[key] += av == v


def run(a, root, work):
    gen = os.path.join(work, 'gen')
    r = sh(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', os.path.join(root, 'memfn', 'include'),
            '-o', gen, os.path.join(HERE, 'g2', 'g2_mfind_gen.c'),
            a.lib or os.path.join(root, 'build', 'libpcrec.a')])
    if r.returncode:
        bad('generator build failed: ' + r.stderr[-2000:])
        return
    x86 = platform.machine() in ('x86_64', 'AMD64')
    targets = list(TARGETS) if x86 else ['generic']
    files, metas, texts = {}, [], {}
    guarded = {}
    reach = []
    for lever in (1, 0):
        for tg in targets:
            d = os.path.join(work, 't-%s-%d' % (tg, lever))
            os.makedirs(d)
            r = sh([gen, a.seed, str(a.sites), d, tg, str(lever)])
            reach.append(r.stderr)
            if a.reach_err:   # the rows are chosen at lever 1 only; written as it goes so a failed run keeps what ran
                open(a.reach_err, 'w').write(''.join(reach))
            if r.returncode:
                bad('generator failed at %s lever %d: %s' % (tg, lever, (r.stderr + r.stdout)[-2000:]))
                return
            ok()    # the generator's structural checks (helpers per target, memcpy/memchr, no #if/#include)
            files[(tg, lever)] = os.path.join(d, 'g2m_sites.c')
            metas.append(os.path.join(d, 'g2m_meta.tsv'))
            texts[(tg, lever)] = open(files[(tg, lever)]).read()
            kit = texts[(tg, lever)].partition('/* G2M KIT TEXT BEGIN */')[2].partition('/* G2M KIT TEXT END */')[0]
            have = {m.group(2) for m in HELPER.finditer(kit)} - {'body'}
            want = TARGETS[tg] if lever else set()
            # the same literals again, read from the text (the generator holds them too)
            (ok() if have == want and bool(kit) else
             bad('target %s lever %d: helpers %s, expected %s' % (tg, lever, sorted(have), sorted(want))))
            print('target %-10s lever %d kit text %d bytes, helper levels %s'
                  % (tg, lever, len(kit), sorted(have)))
            if lever:
                for line in r.stdout.splitlines():
                    m = re.match(r'G2M guarded (\w+) (\d+)$', line)
                    if m:
                        guarded.setdefault((tg, m.group(1)), int(m.group(2)))
    for (tg, lv), v in sorted(guarded.items()):
        if v or lv in TARGETS[tg]:
            print('G2M guarded %s %s %d' % (lv, tg, v))
    # the alone maxima against the declared bound (tests/memfn/simd_bounds.tsv,
    # row mfind-<level>; the kit's guarded_max is pinned equal to it)
    bounds = {}
    for ln in open(os.path.join(root, 'tests', 'memfn', 'simd_bounds.tsv')):
        c = ln.rstrip('\n').split('\t')
        if len(c) == 2 and not ln.startswith('#'):
            bounds[c[0]] = int(c[1])
    for lv in ('w16', 'w32'):
        mx = max([v for (tg, l), v in guarded.items() if l == lv] + [0])
        print('G2M guarded %s %d' % (lv, mx))
        bd = bounds.get('mfind-' + lv)
        if bd is None:
            bad('simd_bounds.tsv declares no mfind-%s row' % lv)
        elif x86 and not mx:
            bad('guarded %s: no site rendered the level (the count is blind)' % lv)
        else:
            (ok() if mx <= bd else bad('guarded %s: alone maximum %d over the declared %d' % (lv, mx, bd)))

    # 1. the space's populations
    pop = dict.fromkeys(POP_FLOOR, 0)
    for m in metas:
        population(m, pop)
    # the floors were measured at 80 sites, of which the first 40 are a fixed
    # head: below 80 only the sites past the head scale (r5 CHECKS-7)
    scale = max(0.0, (a.sites - 40) / 40.0)
    for key, floor in POP_FLOOR.items():
        if not x86 and key not in ('sites',):
            continue
        fl = int(floor * min(scale, 1.0))
        (ok() if pop[key] >= fl else bad('population %s %d < floor %d' % (key, pop[key], fl)))
    print('space ' + ' '.join('%s=%d' % kv for kv in sorted(pop.items())))

    skip = host_skips(work) if x86 else {}
    builds = BUILDS if x86 else [('native', ('generic', 1), ['-O2'], None)]
    if not x86:
        for lv in ('w16', 'w32'):
            SKIPPED['level ' + lv] = ('host is %s, not x86-64' % platform.machine(), 0)

    # 2. answers per build
    jobs = int(os.environ.get('G2M_JOBS', '2'))

    def answer(b):
        name, key, flags, need = b
        exe, r = build(work, name, flags, files[key], 'plain')
        if r.returncode:
            return name, 'build', r.stderr[-1500:], {}
        if need in skip:
            return name, 'skip', skip[need], {}
        rr, cnt = run_drv(exe, [], 'asan' in name)
        return name, rr.returncode, rr.stdout[-1500:] + rr.stderr[-1500:], cnt
    with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(answer, builds))
    ran = [x for x in res if isinstance(x[1], int)]
    for name, rc, out, cnt in res:
        n = cnt.get('checks', -1)
        if rc == 'build':
            bad('%s: the rendered sites do not compile: %s' % (name, out))
        elif rc == 'skip':
            SKIPPED[name] = (out, max([x[3].get('checks', 0) for x in ran] + [0]))
        elif rc != 0:
            bad('%s: rc %s: %s' % (name, rc, out))
        elif n < CHECK_FLOOR_80 * a.sites // 80:
            bad('%s: %d answer checks < floor %d' % (name, n, CHECK_FLOOR_80 * a.sites // 80))
        else:
            ok()
            for key, fl in DRV_FLOOR_80.items():
                fl = fl * a.sites // 80
                (ok() if cnt.get(key, -1) >= fl else
                 bad('%s: population %s %d < floor %d' % (name, key, cnt.get(key, -1), fl)))
        if rc not in ('build', 'skip'):
            print('build %s: checks %d rc %s %s' % (name, n, rc,
                  ' '.join('%s=%d' % (k, cnt[k]) for k in DRV_FLOOR_80 if k in cnt)))

    # 3. plants, at the plain lever-1 builds of each file
    if a.plants:
        plain = [b for b in builds if 'asan' not in b[0] and b[1][1] == 1]
        if a.quick:                      # one build per file
            seen, one = set(), []
            for b in plain:
                if b[1] not in seen:
                    seen.add(b[1])
                    one.append(b)
            plain = one
        tasks = []
        for sid, pname, expect, edits in PLANTS:
            for kind, (mode, old, new, per) in edits.items():
                for tg in targets:
                    if kind != 'body' and kind not in TARGETS[tg]:
                        continue
                    t = plant_text(texts[(tg, 1)], kind, mode, old, new, per)
                    if t is None:
                        bad('plant %s %s@%s at %s: the edit does not apply %d time(s) in each helper'
                            % (sid, pname, kind, tg, abs(per)))
                        continue
                    ok()
                    path = os.path.join(work, 'plant-%s-%s-%s.c' % (sid, kind, tg))
                    open(path, 'w').write(t)
                    for b in plain:
                        if b[1] == (tg, 1):
                            tasks.append((sid, pname, expect, kind, path, b))

        def plant(task):
            sid, pname, expect, kind, path, (name, key, flags, need) = task
            exe, r = build(work, name, flags, path, '%s-%s' % (sid, kind))
            if r.returncode:
                return task, 'build', r.stderr[-800:]
            if need in skip:
                return task, 'skip', None
            # a FAULT plant runs to the end (`stop` would end it at its first
            # wrong answer, which can come before the read that faults); a
            # LOUD one stops at its first wrong answer; a SAME one samples
            args = [] if expect == 'FAULT' else ['1', 'stop'] if expect == 'LOUD' else [GREEN_STRIDE]
            rr, _ = run_drv(exe, args, False)
            return task, rr.returncode, (rr.stdout + rr.stderr)[-500:]
        with concurrent.futures.ThreadPoolExecutor(jobs) as ex:
            pres = list(ex.map(plant, tasks))
        obs = {}
        for (sid, pname, expect, kind, path, (name, key, flags, need)), rc, out in pres:
            tag = 'plant %s %s@%s at %s' % (sid, pname, kind, name)
            if rc == 'build':
                bad(tag + ': does not compile: ' + out)
                continue
            if rc == 'skip':
                n0 = SKIPPED.get(name, ('', 0))
                SKIPPED[name] = (skip[need], n0[1])
                continue
            cls = 'SAME' if rc == 0 else 'FAULT' if rc < 0 else 'LOUD'
            obs.setdefault((sid, pname, expect), set()).add(cls)
            (ok() if cls in ACCEPT[expect] else bad('%s: %s, expected %s: %s' % (tag, cls, expect, out)))
        for sid, pname, expect, edits in PLANTS:
            got = obs.get((sid, pname, expect))
            if not got:
                continue
            if got <= ACCEPT[expect]:
                cls = 'SAME (expected)' if expect == 'SAME' else '/'.join(sorted(got))
            elif 'SAME' in got and expect != 'SAME':
                cls = 'MISSED'
            else:
                cls = '/'.join(sorted(got)) + ' (expected %s)' % expect
            print('PLANT %s %s: %s' % (sid, pname, cls))
        print('plants: %d runs' % len(pres))

    # 4. instruction classes in the w32 builds
    if x86:
        for name in ('v3-x86-64', 'x86-64-v3'):
            exe = os.path.join(work, 'drv-%s-plain' % name)
            if not os.path.exists(exe):
                continue
            r = sh(['objdump', '-d', '--no-show-raw-insn', exe])
            hits = sorted(set(re.findall(r'\b(pdep|pext|v?p?gather\w*)\b', r.stdout)))
            (ok() if r.returncode == 0 and not hits else
             bad('instruction classes %s: objdump rc %d, forbidden %s' % (name, r.returncode, hits)))


if __name__ == '__main__':
    sys.exit(main())
