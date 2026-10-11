#!/usr/bin/env python3
"""Reduce timing_pad.py's per-launch rows: per (row, mode, regime, arm) the
median over all launches, and the layout band (min..max over pads of the
per-pad median). Ratios are against `today`.

usage: summarize.py TIMING_PAD_TSV
"""
import collections, csv, statistics, sys

d = collections.defaultdict(list)
pad = collections.defaultdict(lambda: collections.defaultdict(list))
loads = []
for r in csv.DictReader(open(sys.argv[1]), delimiter="\t"):
    k = (r["row"], r["mode"], r["regime"], r["arm"])
    d[k].append(float(r["ns"]))
    pad[k][r["pad"]].append(float(r["ns"]))
    loads.append(float(r["load1"]))
print("launches=%d load1 %.2f..%.2f (median %.2f)" % (len(loads), min(loads), max(loads), statistics.median(loads)))
print("%-22s %-6s %-5s | %-19s | %-19s | %-19s | %-19s | %6s %6s %6s" %
      ("row", "mode", "reg", "today med [band]", "twin med [band]", "norevend [band]", "twininl [band]", "tw/td", "nr/td", "ti/td"))
rows = sorted({k[:3] for k in d}, key=lambda k: (list(dict.fromkeys(x[0] for x in d)).index(k[0]), k[1], k[2] != "short"))
for k in rows:
    out = []
    for arm in ("today", "twin", "norevend", "twininl"):
        kk = k + (arm,)
        pm = [statistics.median(v) for v in pad[kk].values()]
        out.append((statistics.median(d[kk]), min(pm), max(pm)) if pm else (float("nan"),) * 3)
    t = out[0][0]
    print("%-22s %-6s %-5s | %5.2f [%5.2f-%5.2f] | %5.2f [%5.2f-%5.2f] | %5.2f [%5.2f-%5.2f] | %5.2f [%5.2f-%5.2f] | %6.3f %6.3f %6.3f" %
          (k[0], k[1], k[2], *out[0], *out[1], *out[2], *out[3], out[1][0] / t, out[2][0] / t, out[3][0] / t))
