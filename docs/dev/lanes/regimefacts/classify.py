#!/usr/bin/env python3
"""regimefacts: classify population.tsv cells by subject length against the
crossovers in regimefacts_report.md and by measured time against the bench's
own empty-call floor (floor pattern, 4-byte subject: 8.86 ns, Zen 1 box).
Usage: python3 -I classify.py population.tsv"""
import csv, sys, collections
F = 8.86           # bench-box floor: `floor` pattern, 4 B subject (altwide/floor f-*; derived in report 4.1)
N_STAR = 527       # F / 0.0168 ns/B (memchr-class slope at 1 MiB, report 4.1); 47 = F / 0.19 (walk slope, Zen 4 value, report 3.1)
BANDS = [("D0 <47 B", 0, 47), ("D1 47..526 B", 47, 527), ("M 527..5269 B", 527, 5270), ("L >=5270 B", 5270, 1<<40)]
R = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
tab = collections.defaultdict(lambda: [0]*4)
fx = collections.defaultdict(lambda: [0, 0])
for r in R:
    n = int(r["len"]); t = float(r["median_ns"])
    b = next(i for i, (_, lo, hi) in enumerate(BANDS) if lo <= n < hi)
    tab[(r["subbench"], r["regime"])][b] += 1
    fx[(r["subbench"], r["regime"])][0] += 1
    fx[(r["subbench"], r["regime"])][1] += (t <= 2 * F)
print("subbench\tregime\tcells\t" + "\t".join(b[0] for b in BANDS) + "\tT<=2F (time within 2x empty-call floor)")
tot = [0]*4; tn = 0; tf = 0
for k in sorted(tab):
    print(k[0], k[1], sum(tab[k]), *tab[k], "%d (%.0f%%)" % (fx[k][1], 100*fx[k][1]/fx[k][0]), sep="\t")
    for i in range(4): tot[i] += tab[k][i]
    tn += fx[k][0]; tf += fx[k][1]
print("TOTAL", "", tn, *tot, "%d (%.0f%%)" % (tf, 100*tf/tn), sep="\t")
