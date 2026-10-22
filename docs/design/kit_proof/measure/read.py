#!/usr/bin/env python3
# docs/design/kit_proof/measure/read.py — [KIT-VERIFY] `measure`: results.tsv -> the table.
#
# usage: python3 -I read.py OUT          (OUT = the directory measure.sh wrote)
#
# Reads OUT/results.tsv (launch, cell, regime, class, arm, ns, min, reps, ops, bytes),
# OUT/subjects.tsv's twin OUT/subj/subjects.tsv (match counts) and OUT/cover_stamps.tsv, and
# prints Markdown: the per-cell table, the per-regime summary and the READING RULE.
#
# THE READING RULE (also in docs/dev/lanes/covertime_report.md):
#   per (cell, regime, class) and arm, the 5 per-launch medians give  med  and  IQR
#   (statistics.quantiles, inclusive method).
#   R   = med(COV) / med(DEF)       < 1 means cover is faster
#   AA  = med(AA)  / med(DEF)       the A/A ratio: the same source, a separate compile+link
#   floor = max(|AA - 1|, IQR(DEF) / med(DEF), IQR(COV) / med(COV), FLOOR_MIN)
#   reading = FASTER   if R < 1 - floor
#             SLOWER   if R > 1 + floor      <- a FINDING (cover loses here, beyond the floor)
#             NULL     otherwise
# FLOOR_MIN is an UNMEASURED default (D149): the A/A arm normally sets the floor, and a launch
# count of 5 can make one cell's IQR and A/A tiny by luck; 2% is the least difference this
# instrument is asked to call.
import csv
import math
import statistics
import sys
from collections import defaultdict

FLOOR_MIN = 0.02
REGIMES = ["throughput", "search_short", "match"]
CLASSES = ["real", "none", "dense"]


def q(vals):
    v = sorted(vals)
    med = statistics.median(v)
    if len(v) >= 4:
        qs = statistics.quantiles(v, n=4, method="inclusive")
        iqr = qs[2] - qs[0]
    else:
        iqr = v[-1] - v[0]
    return med, iqr


def main():
    out = sys.argv[1]
    rows = list(csv.DictReader(open(out + "/results.tsv"), delimiter="\t"))
    subj = {}
    for r in csv.DictReader(open(out + "/subj/subjects.tsv"), delimiter="\t"):
        subj[(r["cell"], r["class"])] = r
    stamps = {}
    for r in csv.DictReader(open(out + "/cover_stamps.tsv"), delimiter="\t"):
        stamps[(r["cell"], r["arm"])] = r["stamp"]
    cells = []
    d = defaultdict(list)
    ops = {}
    for r in rows:
        k = (r["cell"], r["regime"], r["class"], r["arm"])
        d[k].append(float(r["ns"]))
        ops[(r["cell"], r["regime"], r["class"])] = int(r["ops"])
        if r["cell"] not in cells:
            cells.append(r["cell"])
    launches = len({r["launch"] for r in rows})

    res = []   # one dict per (cell, regime, class)
    for c in cells:
        for g in REGIMES:
            for cl in CLASSES:
                if (c, g, cl, "DEF") not in d:
                    continue
                md, idef = q(d[(c, g, cl, "DEF")])
                mc, icov = q(d[(c, g, cl, "COV")])
                ma, _ = q(d[(c, g, cl, "AA")])
                R = mc / md
                AA = ma / md
                fl = max(abs(AA - 1), idef / md, icov / mc, FLOOR_MIN)
                reading = "FASTER" if R < 1 - fl else "SLOWER" if R > 1 + fl else "NULL"
                res.append(dict(cell=c, regime=g, cls=cl, ops=ops[(c, g, cl)], md=md, idef=idef,
                                mc=mc, icov=icov, ma=ma, R=R, AA=AA, floor=fl, reading=reading))

    p = print
    p("# covertime: harness-routed `cover` against default (%d launches)\n" % launches)
    p("cover-stamped cells (RX_DFA_SCAN on the harness build): %s\n" %
      ", ".join(c for c in cells if stamps.get((c, "COV")) == "cover"))
    p("not cover on the harness build: %s\n" %
      (", ".join("%s (%s)" % (c, stamps.get((c, "COV"))) for c in cells if stamps.get((c, "COV")) != "cover") or "none"))
    p("ns = median over launches of the per-pass ns (a pass = one find-all for `throughput`, ")
    p("one call per record for the short regimes, so ns/op = ns / ops); [IQR] in brackets.\n")
    p("| cell | regime | class | matches | DEF ns [IQR] | COV ns [IQR] | AA ns | COV/DEF | AA/DEF | floor | reading |")
    p("|---|---|---|---|---|---|---|---|---|---|---|")
    for x in res:
        s = subj[(x["cell"], x["cls"])]
        m = {"throughput": s["throughput_matches"], "search_short": s["search_short_hits"],
             "match": s["match_hits"]}[x["regime"]]
        unit = "" if x["regime"] == "throughput" else "/%d" % x["ops"]
        p("| %s | %s | %s | %s%s | %.0f [%.0f] | %.0f [%.0f] | %.0f | %.3f | %.3f | %.3f | %s |" % (
            x["cell"], x["regime"], x["cls"], m, unit, x["md"], x["idef"], x["mc"], x["icov"], x["ma"],
            x["R"], x["AA"], x["floor"], x["reading"]))
    p("\n## per regime (geometric mean of COV/DEF; counts of readings)\n")
    p("| regime | class | cells | geomean COV/DEF | FASTER | NULL | SLOWER | geomean AA/DEF |")
    p("|---|---|---|---|---|---|---|---|")
    for g in REGIMES:
        for cl in CLASSES + ["all"]:
            xs = [x for x in res if x["regime"] == g and (cl == "all" or x["cls"] == cl)]
            if not xs:
                continue
            gm = math.exp(sum(math.log(x["R"]) for x in xs) / len(xs))
            ga = math.exp(sum(math.log(x["AA"]) for x in xs) / len(xs))
            cnt = {k: sum(1 for x in xs if x["reading"] == k) for k in ("FASTER", "NULL", "SLOWER")}
            p("| %s | %s | %d | %.3f | %d | %d | %d | %.3f |" % (
                g, cl, len(xs), gm, cnt["FASTER"], cnt["NULL"], cnt["SLOWER"], ga))
    p("\n## FINDINGS (cover SLOWER than default beyond the floor)\n")
    sl = [x for x in res if x["reading"] == "SLOWER"]
    if not sl:
        p("none.")
    for x in sl:
        p("- %s / %s / %s: COV/DEF %.3f, floor %.3f (DEF %.0f ns, COV %.0f ns)" % (
            x["cell"], x["regime"], x["cls"], x["R"], x["floor"], x["md"], x["mc"]))
    p("\n## the A/A noise floor\n")
    aa = sorted(abs(x["AA"] - 1) for x in res)
    p("|AA/DEF - 1| over %d rows: median %.3f, 90th percentile %.3f, max %.3f" % (
        len(aa), statistics.median(aa), aa[int(0.9 * (len(aa) - 1))], aa[-1]))


if __name__ == "__main__":
    main()
