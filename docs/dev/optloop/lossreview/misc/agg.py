#!/usr/bin/env python3
"""lossreview/misc: aggregate run_pop_mc.py rows per (pid, config, regime).

    agg.py RES.tsv [config] [regime]   -> TSV on stdout

Columns: pid config regime subjects n(bytes) calls(rx_search calls) nmatch
mc(memchr calls = scan stops+entries) mcmp(memcmp calls) T(subject loads)
T_scan(bytes the interposed scanners examine) and T_<phase> (loads per phase).
Loads are the -O0 instrumented artifact's, counted per phase (wsdrv_mc.c).
"""
import csv, collections, sys
rows = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
cfg = sys.argv[2] if len(sys.argv) > 2 else "default"
reg = sys.argv[3] if len(sys.argv) > 3 else None
PH = "pre skip fwd rev anc vm endw misc unk".split()
agg = collections.OrderedDict()
for r in rows:
    if r["config"] != cfg or (reg and r["regime"] != reg) or not r.get("n"): continue
    k = (r["pid"], r["config"], r["regime"])
    a = agg.setdefault(k, collections.Counter())
    a["subjects"] += 1
    for c in ["n", "calls", "nmatch", "mc", "mcmp", "T", "T_scan"] + ["T_" + p for p in PH]:
        a[c] += int(r.get(c) or 0)
print("\t".join(["pid", "config", "regime", "subjects", "n", "calls", "nmatch", "mc", "mcmp", "T", "T_scan"] + ["T_" + p for p in PH]))
for k, a in agg.items():
    print("\t".join(list(k) + [str(a[c]) for c in ["subjects", "n", "calls", "nmatch", "mc", "mcmp", "T", "T_scan"] + ["T_" + p for p in PH]]))
