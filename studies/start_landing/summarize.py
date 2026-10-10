#!/usr/bin/env python3
"""[START-LANDING] timing summary (STUDY): median +- sd per (cell, variant)
over all interleaved samples, the change, and whether |delta| > 2(sd_o + sd_t).
    summarize.py timing.txt"""
import statistics as st, sys, collections
S = collections.defaultdict(list); CK = collections.defaultdict(set)
for line in open(sys.argv[1]):
    if line.startswith("#") or line.startswith("=="): continue
    f = line.rstrip("\n").split("\t")
    if len(f) < 5: continue
    S[(f[0], f[1])] += [float(x) for x in f[4:]]
    CK[f[0]].add((f[2], f[3]))
print("%-8s %-18s %-18s %8s  %s" % ("cell", "today (o) us", "twin (t) us", "change", "|d| > 2(sa+sb)?"))
for cell in dict.fromkeys(k[0] for k in S):
    o, t = S[(cell, "o")], S[(cell, "t")]
    if len(CK[cell]) != 1:
        print("%-8s CHECKSUM MISMATCH %s" % (cell, CK[cell])); continue
    mo, so, mt, sd = st.median(o), st.stdev(o), st.median(t), st.stdev(t)
    d = mt - mo
    print("%-8s %8.1f +- %-6.1f %8.1f +- %-6.1f %+7.1f%%  %s (|d| %.1f vs %.1f; n=%d/%d)" %
          (cell, mo, so, mt, sd, 100 * d / mo, "YES" if abs(d) > 2 * (so + sd) else "no", abs(d), 2 * (so + sd), len(o), len(t)))
