#!/usr/bin/env python3
"""lossreview/misc: pcrec medians out of a bench report .tsv (pin b8337c33).

    benchns.py REPORT.tsv > ns.tsv     pattern regime subject caps_ns nocaps_ns n

rank rows, metric median_ns, testee pcrec_b8337c33_auto-{caps,nocaps}-*;
subject '(set)' = the set-grain row (large-subject-throughput is one call
sequence over the set's throughput subjects)."""
import csv, sys, collections
d = collections.defaultdict(dict)
for r in csv.reader(open(sys.argv[1]), delimiter="\t"):
    if len(r) < 13 or r[0] != "rank" or r[10] != "median_ns" or "b8337c33" not in r[6]: continue
    caps = "auto-caps" in r[6]
    d[(r[1], r[3], r[2])]["caps" if caps else "nocaps"] = float(r[11]); d[(r[1], r[3], r[2])]["n"] = r[12]
print("pattern\tregime\tsubject\tcaps_ns\tnocaps_ns\tn")
for k in sorted(d):
    v = d[k]
    print("\t".join(list(k) + ["%.1f" % v.get("caps", -1), "%.1f" % v.get("nocaps", -1), v.get("n", "")]))
