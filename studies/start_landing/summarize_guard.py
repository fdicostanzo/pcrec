#!/usr/bin/env python3
"""[START-LANDING] rev 2: the guard timing summary (STUDY). Per (cell,
variant): median +- sd over every interleaved sample; each variant against
today (`o`): the change and whether |delta| > 2(sd_o + sd_v). A cell whose
span checksums differ across its variants is refused; a TIMEOUT line is
reported as such (the wall bound fired).
    summarize_guard.py timing_guard.txt"""
import statistics as st, sys, collections
S = collections.defaultdict(list); CK = collections.defaultdict(set); TO = collections.defaultdict(int)
order = []
for line in open(sys.argv[1]):
    if line.startswith("#") or line.startswith("=="): continue
    f = line.rstrip("\n").split("\t")
    if len(f) < 3: continue
    if f[0] not in order: order.append(f[0])
    if f[2] == "TIMEOUT":
        TO[(f[0], f[1])] += 1; S.setdefault((f[0], f[1]), []); continue
    S[(f[0], f[1])] += [float(x) for x in f[4:]]
    CK[f[0]].add((f[2], f[3]))
print("%-11s %-3s %22s %9s  %s" % ("cell", "v", "median +- sd (us)", "vs today", "|d| > 2(sa+sb)?"))
for cell in order:
    if len(CK[cell]) > 1:
        print("%-11s CHECKSUM MISMATCH %s" % (cell, CK[cell])); continue
    o = S[(cell, "o")]; mo, so = st.median(o), st.stdev(o)
    for v in ("o", "s", "i", "r"):
        if (cell, v) not in S: continue
        x = S[(cell, v)]
        if TO[(cell, v)]:
            print("%-11s %-3s %22s" % (cell, v, "TIMEOUT x%d" % TO[(cell, v)])); continue
        mx, sx = st.median(x), st.stdev(x)
        if v == "o":
            print("%-11s %-3s %12.1f +- %-7.1f" % (cell, v, mx, sx)); continue
        d = mx - mo
        print("%-11s %-3s %12.1f +- %-7.1f %+8.1f%%  %s (|d| %.1f vs %.1f; n=%d)" %
              (cell, v, mx, sx, 100 * d / mo, "YES" if abs(d) > 2 * (so + sx) else "no", abs(d), 2 * (so + sx), len(x)))
