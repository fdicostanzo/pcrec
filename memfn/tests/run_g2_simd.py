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
  1b. THE RANKING (D157): every site states a GENERATED position ranking
     (g2_simd_gen.c's modes: none, one entry on or off the scanned position,
     whole permutations, the second entry at the run's ends, partial; rate
     ties; entries past rank_n that a reader of them would choose). The
     filter positions the kit's rule gives (memfn/src/vrun.c, SECOND FILTER
     POSITION: KA, then at w32 ONLY the first STATED entry other than KA,
     none under `no-vrun-kb`; KB_LEVELS below, D147 addendum 16) are derived
     HERE from the generated entries and every rendered helper's loads, in
     its whole-block mask AND its final-block mask, are held to them, in
     order: a w16 helper reads KA alone, standalone or as the w32 helper's
     rung. Each malformed copy
     (rank_n past the run or MF_RANK_MAX, a position outside the run or twice)
     must be refused by mf_define. Floors per mode and per shape (K35).
  1c. THE VERIFY (R-14, vrun.c's VERIFY TRIM): every rendered helper's
     verify is parsed from its text into the set of positions it COMPARES
     (a byte under a nonzero mask byte), which must equal the rule's set
     derived HERE from the generated masks and the 1b filter: every
     position whose mask is not 0x00, less the filter's positions (all of
     them in the `deny-trim` class, `no-vrun-trim`); a helper has no verify
     (it returns the lowest lane) iff that set is empty. Floors per verify
     shape (K35).
  1d. THE PADDED VERIFY (R-14 follow-up, vrun.c's PADDED VERIFY): where the
     rule derived HERE gives one (a run of 3 or 5-7 bytes, no
     MF_D_RUN_OVERLAP in the meta, something left to verify, not
     `deny-pad`), the helper has TWO verifies: the main path's, ONE word at
     the run's offset of the width the rule gives (4 or 8), its mask
     (`pk`'s literal) compared nowhere past the run (the 1c set), and the
     final block's, the run compare loading nothing past the run; and the
     main guard is VW + T + E (E = width - L), VW + T elsewhere. A load past
     the run anywhere but the main path's padded word is red. The edge
     (a padded word ending at the subject's last byte, the guard page next)
     is counted per live level by the instrumented build, with floors.
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
     verify skipped, the reach one short, the padded verify's margin E one
     short); each must be RED where its level is live and GREEN where it is
     compiled out; the reach and pad-margin plants must FAULT.
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
    'deny-kb': 'vrun@w32+w16',
    'deny-trim': 'vrun@w32+w16',
    'deny-pad': 'vrun@w32+w16',
}
CLASS_FLOOR = 8          # sites per class (each negative class is 1 in 20)
POS_FLOOR = 200          # positive sites
CHECK_FLOOR = 17000000   # answer checks per build: 19,167,946 measured
ASAN_CHECK_FLOOR = 17000000   # (Linux dev box, seed 20261009, 400 sites), ~90%
PATH_FLOOR = 1000        # executions of each path at a live level
# the ranking's populations among rendered sites (K35), literals: 400 sites
# at seed 20261009 measured (Linux dev box, 2026-10-09) 36..48 rendered
# sites per ranking mode, and per filter shape the counts noted below; each
# floor is ~80% of its measurement
RMODE_FLOOR = 29         # rendered sites per ranking mode (min measured 36)
SHAPE_FLOOR = {          # rendered sites per filter shape
    'kb': 164,           # a KB read (205)
    'no-kb': 74,         # KA alone: no ranking, KA alone, or the deny (93)
    'kb-not-rank0': 65,  # KB is the FIRST entry: the ranking not led by KA (82)
    'kb-at-end': 87,     # KB at the run's first or last position (109)
    'ties': 108,         # a rate tie among the stated entries (135)
}
BADRANK_FLOOR = 64       # malformed copies refused (80)
# the levels whose helpers read KB (D147 addendum 16, Frank 2026-10-11: KB
# at w32 only, w16 filters on KA alone), a literal written HERE from the
# ruling, sharing no source with vrun.c's per-level table
KB_LEVELS = {'w32'}
# the per-level KB populations among rendered HELPERS (R-16), literals
# measured at the same seed and sites (Linux dev box, 2026-10-11), each
# floor ~80% of its measurement
KBLVL_FLOOR = {
    'kb-read-w32': 154,      # a w32 helper whose mask reads KB (192)
    'kb-dropped-w16': 153,   # a w16 helper of a site whose ranking gives a
                             # KB, reading KA alone (191)
    'kb-dropped-rung': 142,  # the same, where the site also rendered w32:
                             # the w32 helper's fall-through rung (178)
}
# the verify's shapes among rendered helpers (R-14, VERIFY TRIM), literals
# measured at the same seed and sites (Linux dev box, 2026-10-11), each floor
# ~80% of its measurement: a helper per rendered level of a rendered site.
# Re-measured at R-16 (lane r16b: KB at w32 only, so a w16 helper no longer
# covers a two-byte run whole): none 24 -> 10 (floor re-pinned 19 -> 8), gap
# 344 -> 342, bytes 67 -> 71, words 437 -> 447 (floors held)
VSHAPE_FLOOR = {
    'none': 8,       # nothing left to verify: the lowest lane is the hit (10)
    'gap': 275,      # the positions left are not contiguous: a filter position inside (342)
    'whole': 27,     # the whole run, deny-trim (34)
    'bytes': 53,     # trimmed, the bytes form under MF_D_RUN_OVERLAP (71)
    'words': 349,    # trimmed, the words form (447)
    'padded': 137,   # the main path verifies by one padded word (172)
}
# the padded verify's edge (R-14 follow-up, PADDED VERIFY): main-path padded
# verifies whose word ends at the subject's last byte, per live level, from
# the instrumented build (layout E puts the guard page right after it)
EDGE_FLOOR = (1650, 640)   # (evaluated, verified): min measured 2078 / 804 (w32 at x86-64-v3)
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
SKIPPED = {}   # -march level -> [reason, checks not run]: arms built but not run (host_skips)
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
    """Applies fn(body, lvl_index, helper name) to every helper of `level`
    ('w16', 'w32', or None for both)."""
    def sub(m):
        if level and m.group(2) != level:
            return m.group(0)
        return fn(m.group(0), 0 if m.group(2) == 'w16' else 1, m.group(1))
    return HELPER.sub(sub, text)


def pad_width(L):
    """The padded word's width the rule gives (memfn/src/vrun.c, PADDED
    VERIFY): the smallest of 4 and 8 that covers a run of 3 or 5-7 bytes;
    None where the rule takes no padded word."""
    return 4 if L == 3 else 8 if L in (5, 6, 7) else None


SITE_RUN = {}   # site id -> (off, L), from the generated meta (run(), below)
PADLINE = re.compile(r'^( +)if \((\(\(memcpy\(&pw, [^\n]*)\) return cand;$', re.M)


def instrument(body, li, name):
    b = 4 * li
    body, n0 = re.subn(r'(\) return )(\w+\(subject, n, pos\);)',
                       r') { g2v_path[%d]++; return \2 }' % b, body, count=1)
    body, n1 = re.subn(r'(        if \(i \+ \d+ <= n\) \{)', r'\1 g2v_path[%d]++;' % (b + 1), body)
    body, n2 = re.subn(r'( +size_t f = n - \d+;)', r'g2v_path[%d]++; \1' % (b + 2), body)
    # the padded verify's edge: its word [cand + off, cand + off + P) ends at
    # s[n - 1], P and off from the GENERATED run
    npad = 0
    if name.startswith('g2v_f') and int(name[5:]) in SITE_RUN:
        off, L = SITE_RUN[int(name[5:])]
        if pad_width(L):
            d = off + pad_width(L)
            body, npad = PADLINE.subn(
                r'\1if (cand + %d == n) g2v_edge[%d]++;\n'
                r'\1if (\2) { if (cand + %d == n) g2v_edge[%d]++; g2v_path[%d]++; return cand; }'
                % (d, 2 * li, d, 2 * li + 1, b + 3), body)
    body, n3 = re.subn(r'\) return (cand|i \+ \(size_t\)__builtin_ctz\(m\));',
                       r') { g2v_path[%d]++; return \1; }' % (b + 3), body)
    if (n0, n1, n2) != (1, 1, 1) or n3 + npad not in (1, 2) or npad > 1:
        raise RuntimeError('instrumentation found %r edit points, not one each (verified: one '
                           'or two, the padded one at most once)' % ((n0, n1, n2, n3, npad),))
    return body


PLANTS = [
    # name, the helper edit (regex, replacement), expectation: 'red' or 'fault'
    # (`no-verify` edits only the helpers that verify: a trimmed verify
    # that leaves nothing has none, VERIFY TRIM; it keeps the expression,
    # short-circuited, so the padded verify's locals stay used)
    ('final-guard', r'if \(i \+ (\d+) >= n\) return n;', r'if (i + \1 + 1 >= n) return n;', 'red'),
    ('lane-mask',   r'\(~0u << \(i - f\)\)', r'(~0u << (i - f + 1))', 'red'),
    ('lane-order',  r'__builtin_ctz\(m\)', r'(31 - __builtin_clz(m))', 'red'),
    ('no-verify',   r'if \(((?:\(|\w)[^\n]*)\) return cand;', r'if (1 || (\1)) return cand;', 'red'),
    ('reach-short', None, None, 'fault'),
    # the padded verify's margin E one short (PADDED VERIFY): the main path
    # then reads a byte past n at the top lane; helpers with no padded
    # verify are not edited
    ('pad-margin', None, None, 'fault'),
]


def pad_margin(body, li, fn):
    """The main guard one short in a helper with a padded verify."""
    if 'memcpy(&pw, ' not in body:
        return body
    return re.sub(r'if \(i \+ (\d+) <= n\)', lambda g: 'if (i + %d <= n)' % (int(g.group(1)) - 1),
                  body, count=1)


def reach_short(body, li, name):
    """Every use of the reach R (VW + T) becomes R - 1, and the main guard
    (R + E, PADDED VERIFY) one short too: the vector body then reads one
    byte past n at the shortest span it accepts."""
    m = re.search(r'n - pos < (\d+)\)', body)
    r = int(m.group(1))
    body = body.replace('n - pos < %d)' % r, 'n - pos < %d)' % (r - 1))
    body = re.sub(r'if \(i \+ (\d+) <= n\)', lambda g: 'if (i + %d <= n)' % (int(g.group(1)) - 1),
                  body, count=1)
    body = body.replace('size_t f = n - %d;' % r, 'size_t f = n - %d;' % (r - 1))
    return body


def plant_text(text, plant, level):
    name, pat, rep, _ = plant
    if name == 'pad-margin':
        out = edit_helpers(text, level, pad_margin)
        if out == text:
            raise RuntimeError('plant pad-margin: no helper edited')
        return out
    if pat is None:
        return edit_helpers(text, level, reach_short)
    edits = [0]
    def f(body, li, fn):
        nb, k = re.subn(pat, rep, body, count=1)
        if k != 1 and not (name == 'no-verify' and 'return cand;' not in body):
            raise RuntimeError('plant %s: no edit point' % name)
        edits[0] += k
        return nb
    out = edit_helpers(text, level, f)
    if not edits[0]:
        raise RuntimeError('plant %s: no helper edited' % name)
    return out


_CACHE = {}


def prefetch(work, root, jobs, nworkers):
    """Builds and runs every (name, path, flags, asan) job concurrently; the
    loops below read the results by name (build_run's cache)."""
    with concurrent.futures.ThreadPoolExecutor(nworkers) as ex:
        futs = {ex.submit(_build_run, work, root, *j): j[0] for j in jobs}
        for f in concurrent.futures.as_completed(futs):
            _CACHE[futs[f]] = f.result()


class Skip(str):
    """build_run's error slot when an arm compiled but was NOT run: the host lacks its level."""
    level = why = None


PROBE_C = '''#include <stdio.h>
int main(void)
{
    __builtin_cpu_init();
    printf("x86-64-v3 %d\\nx86-64-v4 %d\\n", __builtin_cpu_supports("x86-64-v3") != 0,
           __builtin_cpu_supports("x86-64-v4") != 0);
    return 0;
}
'''
HOST_SKIP = {}   # -march level -> why the host cannot run code built at it (host_skips)
NEEDS = {'x86-64-v3': 'AVX2', 'x86-64-v4': 'AVX-512'}


def host_skips(work):
    """Fills HOST_SKIP.  The gate is the compiler's own level definition
    (__builtin_cpu_supports("x86-64-vN"), gcc >= 12) in a probe built at plain
    -march=x86-64 so it cannot SIGILL itself; G2V_SKIP_ARMS=lvl[,lvl] forces a
    skip (the gate's test).  A probe that fails to build or run is a hard error."""
    src, exe = os.path.join(work, 'probe.c'), os.path.join(work, 'probe')
    open(src, 'w').write(PROBE_C)
    r = sh(['gcc', '-O0', '-march=x86-64', '-o', exe, src])
    if r.returncode:
        sys.exit('run_g2_simd: host-level probe failed to build: ' + r.stderr[-500:])
    r = sh([exe])
    host = dict(l.split() for l in r.stdout.splitlines())
    if r.returncode or set(host) != set(NEEDS):
        sys.exit('run_g2_simd: host-level probe failed to run: rc=%d %r' % (r.returncode, r.stdout))
    for lv, need in NEEDS.items():
        if host[lv] != '1':
            HOST_SKIP[lv] = 'host lacks %s' % need
    for lv in filter(None, os.environ.get('G2V_SKIP_ARMS', '').replace(' ', '').split(',')):
        if lv not in NEEDS:
            sys.exit('run_g2_simd: G2V_SKIP_ARMS=%s: only %s can be skipped' % (lv, sorted(NEEDS)))
        HOST_SKIP[lv] = 'forced by G2V_SKIP_ARMS (%s)' % NEEDS[lv]


def arm_skip(flags):
    for f in flags:
        if f.startswith('-march=') and f[7:] in HOST_SKIP:
            return f[7:], HOST_SKIP[f[7:]]
    return None


def skipped_or_bad(label, err, n=1):
    """True after counting n unrun checks for a Skip; else reports err as a failure."""
    if isinstance(err, Skip):
        ent = SKIPPED.setdefault(err.level, [err.why, 0])
        ent[1] += n
        return True
    bad('%s: %s' % (label, err))
    return False


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
    sk = arm_skip(flags)
    if sk:   # compiled (the build coverage stays), not run
        e = Skip('not run: ' + sk[1])
        e.level, e.why = sk
        return None, e
    env = dict(os.environ)
    if asan:
        env['ASAN_OPTIONS'] = 'detect_leaks=0:allow_user_segv_handler=1'
    r = sh(['taskset', '-c', pin_cpus(), exe], timeout=1800, env=env)
    return r, None


_PIN = None


def _cpu_list(spec):
    """The CPUs of a taskset list such as '0-3,8' as a set; ValueError if malformed."""
    out = set()
    for part in spec.split(','):
        lo, _, hi = part.strip().partition('-')
        out.update(range(int(lo), int(hi or lo) + 1))
    return out


def _cpu_str(cpus):
    return ','.join(map(str, sorted(cpus)))


def pin_cpus():
    """The taskset list the correctness drivers run on (not timing: it only keeps
    them off the busy cores).  G2V_CPUS is honoured as given, and an explicit
    setting naming a CPU outside this process's affinity set is a hard error,
    never a silent fallback.  Unset: 12-15 where all four are available (the
    dev box), else the highest up-to-4 CPUs of the affinity set (a 4-vCPU CI
    runner has no CPU 12-15), with one line saying which and why."""
    global _PIN
    if _PIN is not None:
        return _PIN
    avail = os.sched_getaffinity(0)
    spec = os.environ.get('G2V_CPUS')
    if spec:
        try:
            want = _cpu_list(spec)
        except ValueError:
            sys.exit('run_g2_simd: G2V_CPUS=%r is not a taskset CPU list' % spec)
        if not want <= avail:
            sys.exit("run_g2_simd: G2V_CPUS=%s names CPUs %s outside this process's affinity set %s"
                     % (spec, sorted(want - avail), _cpu_str(avail)))
        _PIN = spec
    elif {12, 13, 14, 15} <= avail:
        _PIN = '12-15'
    else:
        pick = sorted(avail)[-4:]
        _PIN = _cpu_str(pick)
        print('run_g2_simd: CPUs 12-15 are not all in the affinity set %s; pinning the drivers to %s '
              '(the highest %d available)' % (_cpu_str(avail), _PIN, len(pick)), flush=True)
    return _PIN


LOAD = re.compile(r'_loadu_si(?:128|256)\(\(const __m\d+i \*\)\(subject \+ [if](?: \+ (\d+))?\)\)')


def helper_loads(text):
    """{(site id, level): [[load offsets of one mask, in order] per mask
    line, the whole block's (`subject + i`) then the final block's
    (`subject + f`)]} over every rendered helper `g2v_f<id>__<lvl>`."""
    out = {}
    for m in HELPER.finditer(text):
        fn, lvl = m.group(1), m.group(2)
        if not fn.startswith('g2v_f'):
            continue
        out[(int(fn[5:]), lvl)] = [[int(k or 0) for k in LOAD.findall(l)]
                                   for l in m.group(0).splitlines() if 'm = (unsigned)' in l]
    return out


HELPER_TEXT = {}   # (site id, level) -> the helper's text (run(), below)
CSTR = re.compile(r'\\([0-7]{1,3}|.)|(.)', re.S)


def cstr_bytes(lit):
    """The bytes of a C string literal's body as the kit's cstr op writes it."""
    out = []
    for m in CSTR.finditer(lit):
        if m.group(1) is None:
            out.append(ord(m.group(2)))
        elif m.group(1)[0] in '01234567':
            out.append(int(m.group(1), 8))
        else:
            out.append(ord(m.group(1)))
    return out


WORD_M = re.compile(r'^\(\w+_w(\d)\(subject \+ cand(?: \+ (\d+))?\) & \w+_w\d\("((?:[^"\\]|\\.)*)"\)\) == ')
WORD_X = re.compile(r'^\w+_w(\d)\(subject \+ cand(?: \+ (\d+))?\) == ')
BYTE_M = re.compile(r'^\(\(subject \+ cand\)\[(\d+)\] & \d+\) == \d+$')
BYTE_X = re.compile(r'^\(subject \+ cand\)\[(\d+)\] == \d+$')


PAD_X = re.compile(r'^\(\(memcpy\(&pw, subject \+ cand(?: \+ (\d+))?, (\d)\), pw\) & pk\) == pt$')
PAD_K = re.compile(r'^    uint(\d+)_t pw, pk, pt;\n    memcpy\(&pk, "((?:[^"\\]|\\.)*)", (\d)\);$', re.M)


def verify_one(expr, body):
    """(shape, the set of offsets from cand one verify expression COMPARES
    (under a nonzero mask byte), the byte span [lo, hi) it LOADS) parsed
    from its text; shape 'words', 'bytes' or 'padded'."""
    w = PAD_X.match(expr)
    if w:
        o, width = int(w.group(1) or 0), int(w.group(2))
        k = PAD_K.search(body)
        if not k or int(k.group(1)) != 8 * width or int(k.group(3)) != width:
            return None, None, None
        kb = cstr_bytes(k.group(2))
        if len(kb) != width:
            return None, None, None
        return 'padded', {o + j for j, x in enumerate(kb) if x}, (o, o + width)
    reads, shape, lo, hi = set(), 'bytes', None, None
    for c in expr.split(' && '):
        w = WORD_M.match(c)
        if w:
            o, width = int(w.group(2) or 0), int(w.group(1))
            reads |= {o + j for j, k in enumerate(cstr_bytes(w.group(3))) if k}
        else:
            w = WORD_X.match(c)
            if w:
                o, width = int(w.group(2) or 0), int(w.group(1))
                reads |= set(range(o, o + width))
        if w:
            shape = 'words'
        else:
            w = BYTE_M.match(c) or BYTE_X.match(c)
            if w:
                o, width = int(w.group(1)), 1
                reads.add(o)
            elif c == '1':
                continue
            else:
                return None, None, None
        lo = o if lo is None else min(lo, o)
        hi = o + width if hi is None else max(hi, o + width)
    return shape, reads, (lo, hi) if lo is not None else None


def verify_reads(body):
    """The helper's verifies, in text order (the main path's padded one
    first where it has one), each (shape, compared offsets, loaded span),
    and its main guard's constant (`if (i + G <= n)`). A helper with no
    verify (it returns the lowest lane) gives [('none', set(), None)]."""
    g = re.search(r'^        if \(i \+ (\d+) <= n\) \{$', body, re.M)
    guard = int(g.group(1)) if g else None
    out = [verify_one(m.group(1), body)
           for m in re.finditer(r'^ +if \((.*)\) return cand;$', body, re.M)]
    if not out and re.search(r'^        if \(m\) return i \+ \(size_t\)__builtin_ctz\(m\);$',
                             body, re.M):
        out = [('none', set(), None)]
    return out, guard


def expect_pad(cls, L, overlap, vwant):
    """The rule (memfn/src/vrun.c, PADDED VERIFY), from the generated run:
    the main path verifies by one padded word where the run is 3 or 5-7
    bytes, the site states no MF_D_RUN_OVERLAP, something is left to verify
    and `no-vrun-pad` (deny-pad) is not given."""
    return cls != 'deny-pad' and pad_width(L) is not None and not overlap and bool(vwant)


def expect_verify(cls, off, masks, want_filter):
    """The rule (memfn/src/vrun.c, VERIFY TRIM), from the generated run: the
    verify compares every position whose mask is not 0x00 less the filter's
    positions; under `no-vrun-trim` (deny-trim) all of them."""
    every = {off + j for j, k in enumerate(masks) if k}
    return every if cls == 'deny-trim' else every - set(want_filter)


def verify_check(vlist, guard, vwant, pad, off, L, lvl):
    """'' if the helper's verifies are the rules' (VERIFY TRIM and PADDED
    VERIFY, memfn/src/vrun.c), else why not. Every expectation is derived
    here from the generated run (off, L, its masks via vwant)."""
    vw = 16 if lvl == 'w16' else 32
    t = off + L - 1
    e = pad_width(L) - L if pad else 0
    if guard != vw + t + e:
        return 'main guard i + %r, the rule gives i + %d (VW + T + E)' % (guard, vw + t + e)
    if any(v[0] is None for v in vlist):
        return 'a verify the parser does not know'
    if not vwant:
        return '' if [v[0] for v in vlist] == ['none'] else 'a verify where nothing is left'
    if len(vlist) != (2 if pad else 1):
        return '%d verifies, the rule gives %d' % (len(vlist), 2 if pad else 1)
    for j, (shape, got, span) in enumerate(vlist):
        main_pad = pad and j == 0
        if (shape == 'padded') != main_pad:
            return 'verify %d is %s, the rule gives %s' % (j, shape, 'padded' if main_pad else
                                                          'the run compare')
        if got != vwant:
            return 'verify %d compares %r, the rule gives %r' % (j, sorted(got), sorted(vwant))
        # a load past the run: the padded word in the main path only, and by
        # exactly its width (its padding compared nowhere: `got` above)
        hi = off + (pad_width(L) if main_pad else L)
        if span is None or span[0] < off or span[1] > hi:
            return 'verify %d loads %r, outside [%d, %d)' % (j, span, off, hi)
        if main_pad and span != (off, hi):
            return 'the padded word loads %r, the rule gives [%d, %d)' % (span, off, hi)
    return ''


def expect_filter(cls, off, pp, rank, lvl):
    """The rule, from the generated entries: KA, then at a KB_LEVELS level
    the first stated entry other than KA (none under the deny)."""
    want = [off + pp]
    if cls != 'deny-kb' and lvl in KB_LEVELS:
        kb = next((r for r in rank if r != pp), None)
        if kb is not None:
            want.append(off + kb)
    return want


def parse(out):
    m = re.search(r'G2V checks=(\d+) fail=(\d+) faults=(\d+)', out)
    paths = {}
    for p in re.finditer(r'G2V paths level=(w\d+) entry_fallthrough=(\d+) whole_block=(\d+) '
                         r'final_block=(\d+) verified=(\d+)', out):
        paths[p.group(1)] = tuple(int(x) for x in p.groups()[1:])
    for p in re.finditer(r'G2V edge level=(w\d+) evaluated=(\d+) verified=(\d+)', out):
        paths['edge-' + p.group(1)] = (int(p.group(2)), int(p.group(3)))
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
    for lv, (why, n) in sorted(SKIPPED.items()):
        print('SKIPPED ARM %s: %s; %d checks NOT run (built, not run)' % (lv, why, n))
    if SKIPPED:
        print('skipped arms: %d (%s)' % (len(SKIPPED), '; '.join(
            '%s: %s; %d checks not run' % (lv, w, n) for lv, (w, n) in sorted(SKIPPED.items()))))
    else:
        print('skipped arms: 0')
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
    sites_c = os.path.join(work, 'g2v_sites.c')
    text = open(sites_c).read()
    loads = helper_loads(text)
    for m in HELPER.finditer(text):
        if m.group(1).startswith('g2v_f'):
            HELPER_TEXT[(int(m.group(1)[5:]), m.group(2))] = m.group(0)
    rmodes, shapes, nbad, vshapes, kblvl = {}, {}, 0, {}, {}
    with open(os.path.join(work, 'g2v_meta.tsv')) as f:
        for line in f:
            if line.startswith('#'):
                continue
            (sid, cls, L, off, pp, forms, gb, a16, a32, rmode, rank, badrank,
             ties, masks, overlap) = line.rstrip('\n').split('\t')
            SITE_RUN[int(sid)] = (int(off), int(L))
            masks = bytes.fromhex(masks)
            gb = int(gb)
            # 1b: the malformed copy, and the filter the rule gives
            if badrank != '-':
                if badrank != 'refused':
                    bad('site %s: a malformed ranking was %s, not refused (control-refused: '
                        'its well-formed control was refused too, so the copy tests nothing)'
                        % (sid, badrank))
                else:
                    nbad += 1
            if forms != 'none':
                rank = [] if rank == '-' else [int(x) for x in rank.split(',')]
                # the site's KB as the ranking gives it (the w32 rule): the
                # filter shapes below are the ranking's, whatever rendered
                kbsite = expect_filter(cls, int(off), int(pp), rank, 'w32')
                lvls = forms.partition('@')[2].split('+')
                for lvl in lvls:
                    want = expect_filter(cls, int(off), int(pp), rank, lvl)
                    got = loads.get((int(sid), lvl))
                    if got != [want, want]:
                        bad('site %s (%s, %s, rank %s): %s filter loads %r (whole block, '
                            'final block), the rule gives %r in each'
                            % (sid, cls, rmode, rank, lvl, got, want))
                    else:
                        ok()
                        if len(want) > 1:
                            kblvl['kb-read-' + lvl] = kblvl.get('kb-read-' + lvl, 0) + 1
                        elif len(kbsite) > 1:
                            kblvl['kb-dropped-' + lvl] = kblvl.get('kb-dropped-' + lvl, 0) + 1
                            if lvl == 'w16' and 'w32' in lvls:
                                kblvl['kb-dropped-rung'] = kblvl.get('kb-dropped-rung', 0) + 1
                    # 1c: the verify compares exactly what the filter did not
                    # prove; 1d: the padded one, in the main path only, its
                    # padding masked out, the main guard holding what it reads
                    vlist, guard = verify_reads(HELPER_TEXT.get((int(sid), lvl), ''))
                    vwant = expect_verify(cls, int(off), masks, want)
                    pad = expect_pad(cls, int(L), int(overlap), vwant)
                    why = verify_check(vlist, guard, vwant, pad, int(off), int(L), lvl)
                    if why:
                        bad('site %s (%s, L=%s, rank %s): %s verify: %s; texts %r'
                            % (sid, cls, L, rank, lvl, why,
                               [(v[0], sorted(v[1]) if v[1] is not None else None, v[2])
                                for v in vlist]))
                    else:
                        ok()
                        vshape = vlist[-1][0]
                        k = ('whole' if cls == 'deny-trim' else vshape)
                        vshapes[k] = vshapes.get(k, 0) + 1
                        if vwant and max(vwant) - min(vwant) + 1 != len(vwant):
                            vshapes['gap'] = vshapes.get('gap', 0) + 1
                        if pad:
                            vshapes['padded'] = vshapes.get('padded', 0) + 1
                rmodes[rmode] = rmodes.get(rmode, 0) + 1
                kb = kbsite[1] - int(off) if len(kbsite) > 1 else None
                for shp, hit in (('kb', kb is not None), ('no-kb', kb is None),
                                 ('kb-not-rank0', kb is not None and kb == rank[0]),
                                 ('kb-at-end', kb in (0, int(L) - 1)),
                                 ('ties', int(ties) > 0)):
                    shapes[shp] = shapes.get(shp, 0) + hit
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
    for name, fl in sorted(rmodes.items()):
        print('ranking mode %-10s %4d rendered sites (floor %d)' % (name, fl, RMODE_FLOOR))
    for name in ('none', 'one-ka', 'one-other', 'full-ka', 'full-any', 'end', 'partial'):
        if rmodes.get(name, 0) < RMODE_FLOOR:
            bad('ranking mode %s: %d rendered sites < floor %d' % (name, rmodes.get(name, 0),
                                                                  RMODE_FLOOR))
        else:
            ok()
    for shp, fl in SHAPE_FLOOR.items():
        print('filter shape %-12s %4d rendered sites (floor %d)' % (shp, shapes.get(shp, 0), fl))
        if shapes.get(shp, 0) < fl:
            bad('filter shape %s: %d rendered sites < floor %d' % (shp, shapes.get(shp, 0), fl))
        else:
            ok()
    for shp, fl in KBLVL_FLOOR.items():
        print('kb per level %-15s %4d rendered helpers (floor %d)' % (shp, kblvl.get(shp, 0), fl))
        if kblvl.get(shp, 0) < fl:
            bad('kb per level %s: %d rendered helpers < floor %d' % (shp, kblvl.get(shp, 0), fl))
        else:
            ok()
    for k in sorted(kblvl):
        if k not in KBLVL_FLOOR:
            # a KB read at a level outside KB_LEVELS fails the filter check
            # above; a population this table does not name is a new level
            bad('kb per level: population %s (%d) has no floor' % (k, kblvl[k]))
    for shp, fl in VSHAPE_FLOOR.items():
        print('verify shape %-6s %4d rendered helpers (floor %d)' % (shp, vshapes.get(shp, 0), fl))
        if vshapes.get(shp, 0) < fl:
            bad('verify shape %s: %d rendered helpers < floor %d' % (shp, vshapes.get(shp, 0), fl))
        else:
            ok()
    print('malformed rankings refused: %d (floor %d)' % (nbad, BADRANK_FLOOR))
    if nbad < BADRANK_FLOOR:
        bad('malformed rankings refused: %d < floor %d' % (nbad, BADRANK_FLOOR))
    else:
        ok()
    for tok, g in sorted(maxg.items()):
        lim = bounds.get(tok[6:]) if tok.startswith('alone:') else token_bound(tok, bounds)
        print('guarded bytes: %s max %d (bound %s)' % (tok, g, lim))
    # every build of sections 3-5, prefetched concurrently (each driver run is
    # pinned to G2V_CPUS; the results are judged below in order)
    inst = os.path.join(work, 'g2v_sites_paths.c')
    try:
        open(inst, 'w').write(edit_helpers(text, None, instrument))
    except RuntimeError as e:   # a rendered shape the instrumentation does not know: red
        bad('instrumentation: %s' % e)
        inst = None
    host_skips(work)
    jobs = [(n, sites_c, f, False) for n, f, _ in BUILDS]
    jobs += [(n, sites_c, f, True) for n, f in (ASAN_BUILDS[1:] if a.quick else ASAN_BUILDS)]
    if inst:
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
            skipped_or_bad(name, err)
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
            skipped_or_bad(name, err)
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
    for name, flags, live in (BUILDS[:2] + BUILDS[3:]) if inst else ():
        r, err = build_run(work, root, 'paths-' + name, inst, flags)
        if err:
            skipped_or_bad('paths ' + name, err, 4)   # 2 levels x (path floor, edge floor)
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
            e = paths.get('edge-' + lv, (0, 0))
            print('edge  %-10s %s padded verify at the subject end: evaluated=%d verified=%d '
                  '(floor %d/%d)' % ((name, lv) + e + EDGE_FLOOR))
            if lv in live and (e[0] < EDGE_FLOOR[0] or e[1] < EDGE_FLOOR[1]):
                bad('edge %s %s: %r below floor %r' % (name, lv, e, EDGE_FLOOR))
            elif lv not in live and any(e):
                bad('edge %s %s: a compiled-out level ran: %r' % (name, lv, e))
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
                    skipped_or_bad('plant %s %s %s' % (plant[0], lv, name), err)
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
