#!/usr/bin/env python3
"""summarize.py RAW.tsv [--bands cell=lo,hi ...] : per (cell, pad, arm) the
median over rounds of the cell total (sum of the per-subject best-of-I ns),
the gain vs base (positive = the arm is faster), the null (base_b vs base),
and the pad-pooled figure.  Rows: cell regime pad arm round subject ns ck."""
import sys, collections, statistics as st

def main():
    rows = [l.rstrip('\n').split('\t') for l in open(sys.argv[1])]
    # total per (cell, regime, pad, arm, round)
    tot = collections.defaultdict(float)
    for c, rg, pad, arm, rnd, s, ns, ck in rows:
        tot[(c, rg, pad, arm, int(rnd))] += float(ns)
    keys = sorted({t[:4] for t in tot})
    med = {}
    for k in keys:
        v = [tot[k + (r,)] for r in sorted({t[4] for t in tot}) if k + (r,) in tot]
        med[k] = (st.median(v), min(v), st.pstdev(v) / st.mean(v) * 100 if len(v) > 1 else 0, len(v))
    cells = sorted({(c, rg) for c, rg, _, _ in keys})
    print('cell\tregime\tpad\tarm\tmedian_ns\tmin_ns\tcv%\tn\tgain_vs_base%')
    for c, rg in cells:
        for k in keys:
            if k[:2] != (c, rg): continue
            b = med[(c, rg, k[2], 'base')][0]
            m = med[k]
            print('%s\t%s\t%s\t%s\t%.0f\t%.0f\t%.2f\t%d\t%+.2f' % (c, rg, k[2], k[3], m[0], m[1], m[2], m[3], (b - m[0]) / b * 100))
main()
