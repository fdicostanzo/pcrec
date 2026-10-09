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

# K4's landing breakdown over the bench's throughput cells (default config):
# per pattern, land_calls vs nmatch and land_rev vs T_rev summed over subjects
agg = collections.defaultdict(lambda: [0, 0, 0, 0])
for r in csv.DictReader(open(sys.argv[3]), delimiter="\t"):
    if r["config"] != "default" or r["regime"] != "throughput" or r["rc"] in ("REFUSED", "BUILDFAIL", "TIMEOUT", ""):
        continue
    a = agg[r["pid"]]
    a[0] += int(r.get("land_calls") or 0); a[1] += int(r.get("nmatch") or 0)
    a[2] += int(r.get("land_rev") or 0); a[3] += int(r.get("T_rev") or 0)
cells = [a for a in agg.values() if a[1] > 0 and a[3] > 0]
print("== bench K4 landing breakdown: %d throughput cells (default) run a reverse pass on a match" % len(cells))
print("   every match lands: %d; >= 90%% land: %d; none lands: %d" % (
    sum(1 for a in cells if a[0] == a[1]), sum(1 for a in cells if a[0] >= 0.9 * a[1]),
    sum(1 for a in cells if a[0] == 0)))
print("   landing-start share of all reverse-pass bytes: %.1f%%" % (
    100.0 * sum(a[2] for a in cells) / max(1, sum(a[3] for a in cells))))
