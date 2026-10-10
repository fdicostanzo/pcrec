#!/usr/bin/env python3
"""docs/design/memfn/probes/vmlazy/lazy_timing.py -- R-12 VMLAZY NORMALIZE's
G1 timing pair, ONLY for the movers whose assembly is not identical to the
parent's (lazy_census.py --nonid-out), plus named CONTROL patterns that do not
move at all beyond the abi digit (the null population: they must read null, or
the instrument is measuring placement, not the change).

It is r4e0b/routing_timing.py's method with the census's four .c streams
(that script knows three): per pattern, the parent (abi 70) and the
normalized (abi 72) artifacts each linked into their OWN executable with
routing_timing's driver, two regimes on one 64 KiB text (find-all, ns/B; 64
calls on 64-byte windows, ns/call), each side calibrated to ~50 ms, REPS
alternated runs, one core; median ratio beside each side's run-to-run spread.
Answers are compared per regime; a pair whose answers differ is red.

Scratch tier: one box, no bench (D144 addendum 4).

Usage: lazy_timing.py --parent PCREC --tree PCREC --movers nonid.tsv
       [--stream c-vm] [--control PATTERN ...] [--recipe -O2] [--reps 7]
       [--core 13] [--out DIR]
"""
import argparse
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(TREE, 'scripts'))
sys.path.insert(0, os.path.join(HERE, '..', 'r4e0b'))
import emit_sweep as es  # noqa: E402
import routing_timing as rt  # noqa: E402  (DRIVER, build, run, calibrate, TEXT)

ARGV = {'c-default': [], 'c-vm': ['--engine=vm'], 'c-utf8': ['-e', 'utf8'],
        'c-utf8-vm': ['-e', 'utf8', '--engine=vm']}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parent', required=True)
    ap.add_argument('--tree', default=os.path.join(TREE, 'build', 'pcrec'))
    ap.add_argument('--movers')
    ap.add_argument('--stream', default='c-vm')
    ap.add_argument('--control', action='append', default=[])
    ap.add_argument('--recipe', default='-O2')
    ap.add_argument('--reps', type=int, default=7)
    ap.add_argument('--core', type=int, default=13)
    ap.add_argument('--out', default=os.path.join(TREE, 'build-emitsweep', 'vmlazytiming'))
    a = ap.parse_args()
    cc = es.resolve_cc(TREE)
    jobs, seen = [], set()
    if a.movers:
        for ln in open(a.movers, encoding='utf-8', errors='surrogateescape'):
            if ln.startswith('#'):
                continue
            f = ln.rstrip('\n').split('\t')
            if f[0] != a.stream or f[1] != a.recipe:
                continue
            pat = es.decode_escape(f[3])
            if pat not in seen:
                seen.add(pat)
                jobs.append(('MOVER', pat))
    jobs += [('CONTROL', p) for p in a.control]
    os.makedirs(a.out, exist_ok=True)
    text = os.path.join(a.out, 'text.bin')
    with open(rt.TEXT, 'rb') as fh, open(text, 'wb') as out:
        out.write((fh.read() * 4)[:65536])
    print('== R-12 VMLAZY timing pair: stream %s, recipe %s, %d patterns, core %d, %d reps, cc %s =='
          % (a.stream, a.recipe, len(jobs), a.core, a.reps, cc))
    print('| kind | pattern | regime | parent | normalized | ratio | spread parent | spread normalized | answers |')
    print('|---|---|---|---|---|---|---|---|---|')
    bad = 0
    for i, (kind, pat) in enumerate(jobs):
        ea = rt.build(a.parent, pat, ARGV[a.stream], os.path.join(a.out, 'p%da' % i), a.recipe, cc)
        eb = rt.build(a.tree, pat, ARGV[a.stream], os.path.join(a.out, 'p%db' % i), a.recipe, cc)
        if not ea or not eb:
            print('| %s | `%r` | - | build failed |' % (kind, pat))
            bad += 1
            continue
        for mode, unit, scale in (('thr', 'ns/B', 65536), ('call', 'ns/call', 64)):
            reps = rt.calibrate(ea, text, mode, a.core)
            ta, tb, ans = [], [], set()
            for _ in range(a.reps):
                k, dt = rt.run(ea, text, mode, reps, a.core)
                ta.append(dt * 1e9 / reps / scale)
                ans.add(k)
                k, dt = rt.run(eb, text, mode, reps, a.core)
                tb.append(dt * 1e9 / reps / scale)
                ans.add(k)
            same = len(ans) == 1
            bad += not same
            ma, mb = statistics.median(ta), statistics.median(tb)
            print('| %s | `%r` | %s | %.4f %s | %.4f %s | %.3f | %.3f | %.3f | %s |'
                  % (kind, pat, mode, ma, unit, mb, unit, mb / ma if ma else 0.0,
                     max(ta) / min(ta), max(tb) / min(tb), 'same' if same else 'DIFFER %s' % sorted(ans)),
                  flush=True)
    print('timing: %s' % ('answers agree' if not bad else '%d FAIL' % bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
