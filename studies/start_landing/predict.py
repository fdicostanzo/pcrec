#!/usr/bin/env python3
"""[START-LANDING] predicted bench values for the top cells (STUDY).

    predict.py CENSUS.tsv CELLS.tsv [N]

For the N cells (default config, the bench's auto-caps testee) with the most
K3+K4 weight that a design row takes: the bench's own set-grain pcrec median
(`bench_ns`, walk_survey's bench_times.py: older pins, Ryzen 1600), the best
other engine's median, the walk weight G/T, and two predictions:
  pred_GT    bench_ns x (1 - G/T)       the uniform-per-byte model (upper:
                                       a reverse byte costs about a forward one)
  pred_twin  bench_ns x (twin/today)   where the SHAPE was timed by
                                       run_timing.sh (both runs' median ratios
                                       averaged, 7700X), else blank
Directional only: the medians are older-pin, another box, and the twin ratio
is a find-all over the bench's own 1 MiB subject on a loaded box.
"""
import csv, sys
cen = {(r["pid"], r["config"]): r for r in csv.DictReader(open(sys.argv[1]), delimiter="\t")}
N = int(sys.argv[3]) if len(sys.argv) > 3 else 15
# twin/today median ratios, run 1 and run 2 (results/timing_run*.txt)
TWIN = {"syntax/cls-w": (0.696, 0.712), "syntax/mod-a": (0.696, 0.712),
        "utf8/cls-dot": (0.579, 0.579), "utf8/prp-l": (0.650, 0.647),
        "litrun/lit-l4": (0.620, 0.633)}
rows = []
for c in csv.DictReader(open(sys.argv[2]), delimiter="\t"):
    if c["config"] != "default": continue
    r = cen.get((c["pid"], "default"))
    if not r or r["row"] not in ("landing", "end-minus-width"): continue
    try:
        g = float(c["G_K3"] or 0) + float(c["G_K4"] or 0); T = float(c["T"]); b = float(c["bench_ns"])
    except ValueError:
        continue
    if g <= 0 or b <= 0: continue
    bo = float(c["best_other_ns"] or 0)
    rows.append((b * g / T, c["pid"], c["regime"], r["row"], b, bo, g / T))
print("%-34s %-12s %-15s %9s %6s %9s %9s" % ("cell", "regime", "row", "today ms", "G/T", "pred_GT", "pred_twin"))
for est, pid, reg, row, b, bo, gt in sorted(rows, reverse=True)[:N]:
    tw = TWIN.get(pid) if reg == "throughput" else None
    pt = "%9.2f" % (b * sum(tw) / 2 / 1e6) if tw else "%9s" % "-"
    print("%-34s %-12s %-15s %9.2f %6.2f %9.2f %s" % (pid, reg, row, b / 1e6, gt, b * (1 - gt) / 1e6, pt))
