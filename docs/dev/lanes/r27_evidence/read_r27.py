#!/usr/bin/env python3
# docs/dev/lanes/r27_evidence/read_r27.py — lane r27: r27_results.tsv -> the table, by the 650
# harness's reading rule (docs/dev/lanes/covertime_report.md) applied per arm X in COV, PRO, SHF:
#   R = med(X)/med(DEF); AA = med(AA)/med(DEF);
#   floor = max(|AA - 1|, IQR(DEF)/med(DEF), IQR(X)/med(X), 0.02 (UNMEASURED DEFAULT, D149));
#   FASTER if R < 1 - floor, SLOWER if R > 1 + floor, else NULL.
# R-27.1's bar, read here: no real/none throughput or search_short cell SLOWER, and the dense class
# not slower than COV (X/COV within COV's own floor or below).
import csv
import statistics
import sys
from collections import defaultdict


def q(v):
    v = sorted(v)
    m = statistics.median(v)
    qs = statistics.quantiles(v, n=4, method="inclusive") if len(v) >= 4 else [v[0], m, v[-1]]
    return m, qs[2] - qs[0]


out = sys.argv[1]
d = defaultdict(list)
cells = []
for r in csv.DictReader(open(out + "/r27_results.tsv"), delimiter="\t"):
    d[(r["cell"], r["regime"], r["class"], r["arm"])].append(float(r["ns"]))
    if r["cell"] not in cells:
        cells.append(r["cell"])
print("| cell | regime | class | COV/DEF | PRO/DEF | SHF/DEF | AA/DEF | floor(PRO) | PRO | SHF | dense: PRO/COV SHF/COV |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
bad = {"PRO": [], "SHF": []}
for c in cells:
    for g in ("throughput", "search_short", "match"):
        for cl in ("real", "none", "dense"):
            md, idf = q(d[(c, g, cl, "DEF")])
            ma, _ = q(d[(c, g, cl, "AA")])
            mc, ic = q(d[(c, g, cl, "COV")])
            AA = ma / md
            cols, reads = {}, {}
            for x in ("COV", "PRO", "SHF"):
                mx, ix = q(d[(c, g, cl, x)])
                fl = max(abs(AA - 1), idf / md, ix / mx, 0.02)
                R = mx / md
                cols[x] = (R, fl, mx, ix)
                reads[x] = "FASTER" if R < 1 - fl else "SLOWER" if R > 1 + fl else "NULL"
            dn = ""
            for x in ("PRO", "SHF"):
                mx, ix = cols[x][2], cols[x][3]
                if g == "match":
                    continue
                if cl == "dense":
                    flc = max(abs(AA - 1), ic / mc, ix / mx, 0.02)
                    if mx / mc > 1 + flc:
                        bad[x].append("%s/%s/%s %s/COV %.3f" % (c, g, cl, x, mx / mc))
                elif reads[x] == "SLOWER":
                    bad[x].append("%s/%s/%s %s/DEF %.3f" % (c, g, cl, x, cols[x][0]))
            if cl == "dense":
                dn = "%.3f %.3f" % (cols["PRO"][2] / mc, cols["SHF"][2] / mc)
            print("| %s | %s | %s | %.3f | %.3f | %.3f | %.3f | %.3f | %s | %s | %s |" % (
                c, g, cl, cols["COV"][0], cols["PRO"][0], cols["SHF"][0], AA, cols["PRO"][1],
                reads["PRO"], reads["SHF"], dn))
for x in ("PRO", "SHF"):
    print("\n%s against R-27.1's bar: %d miss(es)%s" % (x, len(bad[x]), "".join("\n- " + b for b in bad[x])))
