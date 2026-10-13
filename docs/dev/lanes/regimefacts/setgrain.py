#!/usr/bin/env python3
"""regimefacts: set-grain cell counts (pattern x regime; the bench's front-page grain)
by the LARGEST subject length in the cell, same bands as classify.py.
Usage: python3 -I setgrain.py population.tsv"""
import csv, sys, collections
R = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
mx = collections.defaultdict(int)
for r in R:
    k = (r["subbench"], r["regime"], r["pattern"]); mx[k] = max(mx[k], int(r["len"]))
c = collections.defaultdict(lambda: [0]*4)
for (sb, rg, p), n in mx.items():
    c[(sb, rg)][0 if n < 47 else 1 if n < 527 else 2 if n < 5270 else 3] += 1
print("subbench\tregime\tset_cells\tD0(max len<47)\tD1(47..526)\tM(527..5269)\tL(>=5270)")
t = [0]*4
for k in sorted(c):
    print(k[0], k[1], sum(c[k]), *c[k], sep="\t")
    for i in range(4): t[i] += c[k][i]
print("TOTAL", "", sum(t), *t, sep="\t")
