#!/usr/bin/env python3
"""walk_survey: the per-class POPULATION counts the survey quotes, default
config, from analyze.py's cells files and run_pop's raw rows.

    counts.py CELLS_BENCH CELLS_CORPUS RES_BENCH RES_CORPUS > results/counts.txt
"""
import csv, collections, sys
csv.field_size_limit(1 << 30)
CL = ["K1", "K2", "K3", "K4", "K5", "K5m", "K5mb", "K6", "K7", "K8", "K9", "K10", "K11", "K12"]
for name, cells, res in (("bench", sys.argv[1], sys.argv[3]), ("corpus", sys.argv[2], sys.argv[4])):
    rows = [r for r in csv.DictReader(open(cells), delimiter="\t") if r["config"] == "default"]
    pats = {r["pid"] for r in rows}
    print("== %s: %d patterns with at least one live default-config cell" % (name, len(pats)))
    print("class\tpatterns\tshare\tcells\tby regime")
    for c in CL:
        hit = [r for r in rows if int(r.get("G_" + c) or 0) > 0]
        p = {r["pid"] for r in hit}
        print("%s\t%d\t%.1f%%\t%d\t%s" % (c, len(p), 100.0 * len(p) / max(1, len(pats)), len(hit),
              dict(collections.Counter(r["regime"] for r in hit))))
    # K5's cliff population: every artifact whose required run is CASE-FOLDED
    # (RX_REQ_RUN carries a /mask: the two-stream pair arm)
    pair = set(); allp = set()
    for r in csv.DictReader(open(res), delimiter="\t"):
        if r["config"] != "default" or r["rc"] in ("REFUSED", "BUILDFAIL", ""):
            continue
        allp.add(r["pid"])
        if "/" in (r.get("REQ_RUN") or ""):
            pair.add(r["pid"])
    print("K5 cliff population (RX_REQ_RUN folded, the pair arm): %d of %d patterns" % (len(pair), len(allp)))
    print("   " + " ".join(sorted(pair)[:40]))
