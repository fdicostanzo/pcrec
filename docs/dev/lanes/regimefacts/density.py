#!/usr/bin/env python3
"""regimefacts: match-gap (subject bytes per expected match) for the bench's
large-subject-throughput pcrec cells, from the bench's oracle expectations
(bench/<set>/expectations.tsv, read-only; `nmatches` = oracle find-all count).
Bands from the report (3.2): gap < 100 B  = per-match fixed cost >= half for the scalar walk
(g* = 55..104 B); 100..845 B = fixed-dominated only for fast forms; >= 845 B (or 0 matches)
= per-byte dominated for every form (g* = 845 B, memchr-class, Zen 1 litrun floor).
Usage: python3 -I density.py population.tsv BENCH_ROOT"""
import csv, sys, collections
P = list(csv.DictReader(open(sys.argv[1]), delimiter="\t")); B = sys.argv[2]
ex = {}
for sb in sorted({r["subbench"] for r in P}):
    d = {"email": "email"}.get(sb, sb)
    try:
        for r in csv.DictReader(open(f"{B}/bench/{d}/expectations.tsv"), delimiter="\t"):
            if r["regime"] == "throughput" and r["nmatches"] not in ("-", ""):
                ex[(sb, r["pattern"], r["subject"])] = int(r["nmatches"])
    except FileNotFoundError:
        pass
bands = [("0 matches", None), ("gap>=845", 845), ("100..844", 100), ("<100", 0)]
tab = collections.defaultdict(lambda: [0]*4); miss = collections.Counter()
for r in P:
    if r["regime"] != "large-subject-throughput": continue
    k = (r["subbench"], r["pattern"], r["subject"])
    if k not in ex: miss[r["subbench"]] += 1; continue
    m = ex[k]; n = int(r["len"])
    i = 0 if m == 0 else 1 if n / m >= 845 else 2 if n / m >= 100 else 3
    tab[r["subbench"]][i] += 1
print("subbench\tthroughput cells joined\t" + "\t".join(b[0] for b in bands))
t = [0]*4
for sb in sorted(tab):
    print(sb, sum(tab[sb]), *tab[sb], sep="\t"); t = [a+b for a, b in zip(t, tab[sb])]
print("TOTAL", sum(t), *t, sep="\t"); print("unjoined (no expectation row):", dict(miss))
