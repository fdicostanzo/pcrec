#!/usr/bin/env python3
"""[K87] summarize time_<cc>.txt from k87twin.sh: per cell, NEW vs OLD at every
pad, the base-vs-base floor, the layout spread, and a per-cell reading."""
import sys, collections, statistics as st
rows = collections.defaultdict(lambda: collections.defaultdict(list))
for fn in sys.argv[1:]:
    for ln in open(fn):
        if ln.startswith("#") or ln.startswith("ANSWER"):
            if ln.startswith("ANSWER"): print(ln.strip())
            continue
        cc, n, mode, s, i, v, val = ln.split()
        rows[(cc, n, mode, s)][v].append(float(val))
pads = sorted({int(v[3:]) for k in rows for v in rows[k] if v[:3] in ("new", "old") and not v.endswith("b")})
print("%-6s %-5s %-4s %-15s %9s %9s %9s %9s %9s %9s %9s  %s" % ("cc", "pat", "mode", "subject", "newMed", "oldMed", "NEW-OLD", "floor", "newSprd", "oldSprd", "pairsNEWslower", "reading"))
for k in sorted(rows):
    d = rows[k]; med = {v: st.median(x) for v, x in d.items()}
    nw = [med["new%d" % p] for p in pads]; od = [med["old%d" % p] for p in pads]
    diff = [a - b for a, b in zip(nw, od)]
    floor = abs(med["new0"] - med["new0b"])
    ns, os_ = max(nw) - min(nw), max(od) - min(od)
    mean = st.mean(diff); slower = sum(1 for x in diff if x > 0)
    lay = max(ns, os_, floor)
    if abs(mean) <= lay / 2 or slower in range(2, len(pads) - 1): rd = "layout/NULL"
    else: rd = "NEW slower" if mean > 0 else "NEW faster"
    f = "%.5f" if k[2] == "t" else "%.3f"
    print("%-6s %-5s %-4s %-15s %9s %9s %9s %9s %9s %9s %5d/%d  %s" % (k[0], k[1], k[2], k[3], f % st.mean(nw), f % st.mean(od), ("%+.5f" if k[2]=="t" else "%+.3f") % mean, f % floor, f % ns, f % os_, slower, len(pads), rd))
