#!/usr/bin/env python3
"""docs/design/memfn/probes/r4e0b/routing_timing.py -- R4e'.0b's G1 timing
pair (integration.md §R4.9.2.6 item 3): ONLY for movers whose assembly is not
identical to the parent's (routing_census.py --nonid-out), plus named control
movers whose assembly IS identical (the null population: they must read
null, or the instrument is measuring placement, not the routing).

Per pattern: the parent (abi 68, PARENT pcrec) and the routed (this tree's
pcrec) artifacts, each linked into its OWN executable with the same driver
(one TU cannot hold two abis: the shared block's guard refuses it), compiled
at one recipe (default `-O2`). Two regimes on one fixed text (TEXT, a
committed document of the tree, read whole and cut to 64 KiB):
  thr  find-all over the 64 KiB (match_api.md §3.1's loop through
       <p>_next_pos), ns/byte;
  call one <p>_search from 0 on each of 64 short windows (64 B), ns/call.
Each executable calibrates its own repetition count to ~50 ms, then the two
run ALTERNATED, REPS times each, one core (`taskset -c CORE`); the report is
the median of each and the routed/parent ratio, with the run-to-run spread
(max/min of each side) beside it as the noise floor. Answers are compared
too (match count per regime): a timing pair whose answers differ is red.

Scratch tier: one box, no bench (D144 addendum 4).

Usage: routing_timing.py --parent PCREC --tree PCREC --movers nonid.tsv
       [--control PATTERN ...] [--stream c-default] [--recipe -O2]
       [--reps 7] [--core 13] [--out DIR]
"""
import argparse
import os
import re
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(TREE, 'scripts'))
import emit_sweep as es  # noqa: E402

TEXT = os.path.join(TREE, 'APPROACH.md')

DRIVER = r'''
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "rx.h"
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec * 1e-9; }
static ptrdiff_t caps[RX_NCAPS > 0 ? RX_NCAPS : 1][2];
static long findall(const unsigned char *s, size_t n) {
    long k = 0; size_t p = 0;
    while (p <= n) {
        int r = rx_search(s, n, p, caps);
        if (r != 1) break;
        k++;
        size_t b = (size_t)caps[0][0], e = (size_t)caps[0][1];
        p = e > b ? e : rx_next_pos(s, n, e);
        if (e == n && e == b) break;
    }
    return k;
}
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "rb"); static unsigned char buf[65536];
    size_t n = fread(buf, 1, sizeof buf, f); fclose(f);
    const char *mode = argv[2]; long reps = atol(argv[3]);
    volatile long sink = 0; long ans = 0;
    double t0 = now();
    for (long r = 0; r < reps; r++) {
        if (mode[0] == 't') { long k = findall(buf, n); sink += k; ans = k; }
        else { long k = 0; for (int w = 0; w < 64; w++) k += rx_search(buf + w * 997 % (n - 64), 64, 0, caps) == 1; sink += k; ans = k; }
    }
    double dt = now() - t0;
    printf("%ld %.6f %ld\n", ans, dt, (long)sink);
    return 0;
}
'''


def build(pcrec, pat, argv_extra, d, recipe, cc):
    os.makedirs(d, exist_ok=True)
    r = subprocess.run([pcrec, '-p', 'rx', '--features', 'all'] + argv_extra +
                       ['-o', os.path.join(d, 'rx.c')] + es._pattern_argv(pcrec, pat),
                       capture_output=True)
    if r.returncode:
        return None
    with open(os.path.join(d, 'drv.c'), 'w') as fh:
        fh.write(DRIVER)
    r = subprocess.run([cc] + recipe.split() + ['-o', os.path.join(d, 'x'), os.path.join(d, 'drv.c'),
                        os.path.join(d, 'rx.c')], capture_output=True)
    return os.path.join(d, 'x') if r.returncode == 0 else None


def run(exe, text, mode, reps, core):
    out = subprocess.run(['taskset', '-c', str(core), exe, text, mode, str(reps)],
                         capture_output=True, text=True, timeout=600).stdout.split()
    return int(out[0]), float(out[1])


def calibrate(exe, text, mode, core):
    reps = 1
    while True:
        _, dt = run(exe, text, mode, reps, core)
        if dt > 0.05 or reps > 1 << 24:
            return reps
        reps *= 4 if dt < 0.01 else 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parent', required=True)
    ap.add_argument('--tree', default=os.path.join(TREE, 'build', 'pcrec'))
    ap.add_argument('--movers')
    ap.add_argument('--stream', default='c-default')
    ap.add_argument('--control', action='append', default=[])
    ap.add_argument('--recipe', default='-O2')
    ap.add_argument('--reps', type=int, default=7)
    ap.add_argument('--core', type=int, default=13)
    ap.add_argument('--out', default=os.path.join(TREE, 'build-emitsweep', 'routingtiming'))
    a = ap.parse_args()
    cc = es.resolve_cc(TREE)
    argv_of = {'c-default': [], 'c-vm': ['--engine=vm'], 'c-utf8': ['-e', 'utf8']}
    jobs = []
    if a.movers:
        seen = set()
        for ln in open(a.movers, encoding='utf-8', errors='surrogateescape'):
            if ln.startswith('#'):
                continue
            f = ln.rstrip('\n').split('\t')
            if f[0] != a.stream or f[1] != a.recipe:
                continue
            pat = es.decode_escape(f[3])
            if pat not in seen:
                seen.add(pat)
                jobs.append(('MOVER', pat, f[2]))
    for pat in a.control:
        jobs.append(('CONTROL', pat, 'identical assembly'))
    text = os.path.join(a.out, 'text.bin')
    os.makedirs(a.out, exist_ok=True)
    with open(TEXT, 'rb') as fh, open(text, 'wb') as out:
        out.write((fh.read() * 4)[:65536])
    print('== R4e\'.0b timing pair: stream %s, recipe %s, %d patterns, core %d, %d reps, cc %s =='
          % (a.stream, a.recipe, len(jobs), a.core, a.reps, cc))
    print('| kind | pattern | regime | parent | routed | routed/parent | spread parent | spread routed | answers |')
    print('|---|---|---|---|---|---|---|---|---|')
    bad = 0
    for i, (kind, pat, why) in enumerate(jobs):
        ea = build(a.parent, pat, argv_of[a.stream], os.path.join(a.out, 'p%da' % i), a.recipe, cc)
        eb = build(a.tree, pat, argv_of[a.stream], os.path.join(a.out, 'p%db' % i), a.recipe, cc)
        if not ea or not eb:
            print('| %s | `%s` | - | build failed |' % (kind, pat))
            bad += 1
            continue
        for mode, unit, scale in (('thr', 'ns/B', 65536), ('call', 'ns/call', 64)):
            reps = calibrate(ea, text, mode, a.core)
            ta, tb, ans = [], [], set()
            for _ in range(a.reps):
                k, dt = run(ea, text, mode, reps, a.core)
                ta.append(dt * 1e9 / reps / scale)
                ans.add(('a', k))
                k, dt = run(eb, text, mode, reps, a.core)
                tb.append(dt * 1e9 / reps / scale)
                ans.add(('b', k))
            same = len({k for _, k in ans}) == 1
            bad += not same
            ma, mb = statistics.median(ta), statistics.median(tb)
            print('| %s | `%s` | %s | %.4f %s | %.4f %s | %.3f | %.3f | %.3f | %s |'
                  % (kind, pat, mode, ma, unit, mb, unit, mb / ma, max(ta) / min(ta), max(tb) / min(tb),
                     'same' if same else 'DIFFER %s' % sorted(ans)), flush=True)
    print('timing: %s' % ('answers agree' if not bad else '%d FAIL' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
