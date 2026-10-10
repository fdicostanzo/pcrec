#!/usr/bin/env python3
"""[START-LANDING] coverage of walk_survey's K3/K4 by the design's rows (STUDY).

    coverage.py CENSUS.tsv CELLS.tsv[.gz] [top]

CENSUS.tsv is census.py's output; CELLS is walk_survey's analyze.py
`cells_<pop>.tsv` (committed: studies/walk_survey/results/). Joins on
(pid, config) and reports, over the cells with G_K3 + G_K4 > 0: the bytes and
the bench-weighted est_ms each design row takes (`end-minus-width`,
`landing`), what stays on `reverse-pass` and WHY (the census's decline
reason), and the top cells. est is walk_survey's upper weight
(median x G/T, older-pin medians): a WEIGHT, not a prediction.
"""
import csv, gzip, sys, collections

cen = {}
for r in csv.DictReader(open(sys.argv[1]), delimiter="\t"):
    cen[(r["pid"], r["config"])] = r
op = gzip.open if sys.argv[2].endswith(".gz") else open
cells = list(csv.DictReader(op(sys.argv[2], "rt"), delimiter="\t"))
top = int(sys.argv[3]) if len(sys.argv) > 3 else 15


def f(x):
    try: return float(x)
    except Exception: return 0.0


for cfg in ("default", "nocaps"):
    by = collections.defaultdict(lambda: [0.0, 0.0, set(), 0])
    why = collections.defaultdict(lambda: [0.0, 0.0, set()])
    tops = []
    for c in cells:
        if c["config"] != cfg: continue
        g = f(c["G_K3"]) + f(c["G_K4"])
        if g <= 0: continue
        e = f(c.get("est_ns_K3")) + f(c.get("est_ns_K4"))
        r = cen.get((c["pid"], cfg))
        row = r["row"] if r else "?"
        b = by[row]; b[0] += g; b[1] += e; b[2].add(c["pid"]); b[3] += 1
        if row == "reverse-pass":
            k = "land=%s seeded=%s next=%s" % (r["land"], r["seeded"], r["next"]) if r["land"] == "OK" else "land=" + r["land"]
            w = why[k]; w[0] += g; w[1] += e; w[2].add(c["pid"])
        tops.append((e, c["pid"], c["regime"], row, g, f(c["n"]), c["G_K3"], c["G_K4"], f(c.get("bench_ns"))))
    G = sum(v[0] for v in by.values()); E = sum(v[1] for v in by.values())
    print("== config %s: K3+K4 cells, bytes %.0f, est %.2f ms" % (cfg, G, E / 1e6))
    for k, v in sorted(by.items(), key=lambda x: -x[1][0]):
        print("  %-16s cells %4d patterns %3d  bytes %12.0f (%5.1f%%)  est %7.2f ms (%5.1f%%)"
              % (k, v[3], len(v[2]), v[0], 100 * v[0] / G if G else 0, v[1] / 1e6, 100 * v[1] / E if E else 0))
    print("  -- reverse-pass residual by reason:")
    for k, v in sorted(why.items(), key=lambda x: -x[1][1]):
        print("     %-50s patterns %3d bytes %12.0f est %6.2f ms" % (k, len(v[2]), v[0], v[1] / 1e6))
    print("  -- top %d cells by est:" % top)
    for t in sorted(tops, reverse=True)[:top]:
        print("     %-34s %-13s %-16s est %6.2f ms  G %9.0f  n %8.0f  K3 %s K4 %s  bench %.2f ms"
              % (t[1], t[2], t[3], t[0] / 1e6, t[4], t[5], t[6], t[7], t[8] / 1e6))
