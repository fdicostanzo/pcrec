#!/usr/bin/env python3
"""pool.py RAW.tsv : the pad-pooled reading.  For every (cell, arm != base):
gain% = (base - arm)/base of the median-of-rounds cell total, per pad layout;
printed as pad-median [min .. max] over the layouts, with the null arm
(`base_b`, a second compile of today's artifact) read the same way, and the
implied ns saved per seam call (gain_ns / gcov-counted calls) where the cell
has a count.  Positive = the arm is FASTER than base."""
import sys, collections, statistics as st
CALLS = {'bak2': 794481, 'bak1': 726049, 'modj': 727369, 'phone': 240718,
         'bakpy': 726049, 'bakgrel': 726049}   # bak-py / bak-g-rel are NOT gcov'd: bak-1's count assumed   # vm/gcov_counts.tsv span_match_calls
BENCH_NS = {'bak2': 15484564, 'bak1': 16233361, 'modj': 25427031, 'phone': 8494735, 'bakpy': 16299360, 'bakgrel': 16286979}  # Zen 1 bench cells (vm/cells.tsv)
tot = collections.defaultdict(float)
for l in open(sys.argv[1]):
    c, rg, pad, arm, rnd, s, ns, ck = l.rstrip('\n').split('\t')
    tot[(c, pad, arm, int(rnd))] += float(ns)
med = collections.defaultdict(dict)
for (c, pad, arm, rnd), v in list(tot.items()):
    med[(c, pad, arm)].setdefault('v', []).append(v)
M = {k: st.median(d['v']) for k, d in med.items()}
cells = sorted({k[0] for k in M})
print('cell\tarm\tlayouts\tgain%_median\t[min .. max]\tbase_ns_median\tsaved_ns\tns_per_call\tbench_zen1_ns')
for c in cells:
    pads = sorted({k[1] for k in M if k[0] == c}, key=lambda s: int(s[1:]))
    for arm in sorted({k[2] for k in M if k[0] == c and k[2] != 'base'}):
        g = [(M[(c, p, 'base')] - M[(c, p, arm)]) / M[(c, p, 'base')] * 100 for p in pads]
        sv = [M[(c, p, 'base')] - M[(c, p, arm)] for p in pads]
        b = st.median([M[(c, p, 'base')] for p in pads])
        npc = st.median(sv) / CALLS[c] if (arm != 'base_b' and c in CALLS) else float('nan')
        print('%s\t%s\t%d\t%+.2f\t[%+.2f .. %+.2f]\t%.0f\t%.0f\t%.2f\t%d' % (c, arm, len(pads), st.median(g), min(g), max(g), b, st.median(sv), npc, BENCH_NS.get(c, 0)))
