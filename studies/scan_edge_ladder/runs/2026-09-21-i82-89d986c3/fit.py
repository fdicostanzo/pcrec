#!/usr/bin/env python3
"""
edgefit — [OPT-EDGE] I-82 (pin 89d986c3) fit + mechanism analysis.

Reads the three verbatim logs committed beside this script
(ladder_run1.log, floor_run1.log, floor_run2.log) and computes:

  (1) the ladder's t(k) = a + b*k fit per arm, over per-rung MEDIANS
      (k=1..4), plus a per-round fit (15 independent 4-point fits) whose
      b-distribution (median, IQR) is reported for stability;
  (2) the per-edge cost the README names -- before minus after, the
      two arms the isolation is built on, never noedge;
  (3) the floor's m x family gap test (|median-1| vs IQR vs the
      round-to-round min..max range), both runs;
  (4) the m=2 exact / m=2 nullable per-round mode classification and
      the edge-vs-noedge attribution of which arm moves.

No third-party packages; plain statistics module + manual OLS/percentile
(type-7, matching run_floor.sh's own awk implementation) so this
reproduces exactly, with nothing to install.
"""
import re
import statistics as stats
from pathlib import Path

HERE = Path(__file__).parent

# ---------------------------------------------------------------- helpers --

def pct(sorted_vals, p):
    """Linear-interpolated percentile, type-7 (numpy/run_floor.sh's own)."""
    n = len(sorted_vals)
    idx = p * (n - 1)  # 0-based
    lo = int(idx)
    hi = min(lo + 1, n - 1)
    frac = idx - lo
    return sorted_vals[lo] + frac * (sorted_vals[hi] - sorted_vals[lo])


def median_iqr(vals):
    s = sorted(vals)
    med = pct(s, 0.50)
    q1 = pct(s, 0.25)
    q3 = pct(s, 0.75)
    return med, q3 - q1, s[0], s[-1], len(s)


def ols(xs, ys):
    """Simple least-squares fit y = a + b*x. Returns (a, b)."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    return a, b


# ------------------------------------------------------------- ladder log --

ladder_lines = (HERE / "ladder_run1.log").read_text().splitlines()
ladder_row_re = re.compile(
    r"^\s*(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+"
    r"([\d.]+)\s+([\d.]+)\s*$"
)
# ladder[arm][k] = list of 15 values, index = round order
ladder = {arm: {k: [] for k in (1, 2, 3, 4)} for arm in
          ("before", "after", "step11", "noedge")}
ladder_rounds = {k: [] for k in (1, 2, 3, 4)}  # k -> list of (round, before, after, step11, noedge)
for line in ladder_lines:
    m = ladder_row_re.match(line)
    if not m:
        continue
    r, k, before, after, step11, noedge, _ab, _sa = m.groups()
    k = int(k)
    before, after, step11, noedge = map(float, (before, after, step11, noedge))
    ladder["before"][k].append(before)
    ladder["after"][k].append(after)
    ladder["step11"][k].append(step11)
    ladder["noedge"][k].append(noedge)
    ladder_rounds[k].append((int(r), before, after, step11, noedge))

print("=" * 78)
print("PART 2 — THE LADDER FIT")
print("=" * 78)

print("\n-- per-rung MEDIANS (over 15 rounds) --")
ladder_medians = {arm: {} for arm in ladder}
for arm in ladder:
    print(f"  {arm}:")
    for k in (1, 2, 3, 4):
        med, iqr, lo, hi, n = median_iqr(ladder[arm][k])
        ladder_medians[arm][k] = med
        print(f"    k={k}: median={med:.4f}  IQR={iqr:.4f}  "
              f"min={lo:.4f}  max={hi:.4f}  n={n}")

print("\n-- fit t(k) = a + b*k over the per-rung MEDIANS (k=1..4) --")
fits = {}
for arm in ("before", "after", "step11", "noedge"):
    xs = [1, 2, 3, 4]
    ys = [ladder_medians[arm][k] for k in xs]
    a, b = ols(xs, ys)
    fits[arm] = (a, b)
    print(f"  {arm:8s}: a={a:.4f}  b={b:.4f}  (ns/byte fixed / per-edge)")

print("\n-- per-ROUND fits (15 independent 4-point fits per arm) --")
per_round_b = {arm: [] for arm in ladder}
for arm in ("before", "after", "step11", "noedge"):
    # index rounds 0..14 consistently across k using ladder_rounds
    for i in range(15):
        xs = [1, 2, 3, 4]
        ys = []
        ok = True
        for k in xs:
            entry = ladder_rounds[k][i]
            round_no = entry[0]
            val = {"before": entry[1], "after": entry[2],
                   "step11": entry[3], "noedge": entry[4]}[arm]
            ys.append(val)
        a, b = ols(xs, ys)
        per_round_b[arm].append(b)
    med, iqr, lo, hi, n = median_iqr(per_round_b[arm])
    print(f"  {arm:8s}: b median={med:.4f}  IQR={iqr:.4f}  "
          f"min={lo:.4f}  max={hi:.4f}  (n={n} rounds)")

print("\n-- per-edge cost: README's named isolation (before - after), "
      "never noedge --")
print("   diff(k) = before_median(k) - after_median(k):")
diff_ys = []
for k in (1, 2, 3, 4):
    d = ladder_medians["before"][k] - ladder_medians["after"][k]
    diff_ys.append(d)
    print(f"    k={k}: {d:.4f} ns/byte")
a_diff, b_diff = ols([1, 2, 3, 4], diff_ys)
print(f"   fit of diff(k) = a + b*k:  a={a_diff:.4f}  b={b_diff:.4f}")
print(f"   sanity: b_before - b_after = "
      f"{fits['before'][1] - fits['after'][1]:.4f} "
      f"(must equal b_diff above, OLS is linear)")

# ------------------------------------------------------------- floor logs --

print("\n" + "=" * 78)
print("PART 3 — THE m=2 FLOOR CELL, BY MECHANISM; THE D77 GAP TEST")
print("=" * 78)

floor_row_re = re.compile(
    r"^\s*(\d+)\s+(\d+)\s+(exact|nullable)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$"
)


def parse_floor(path):
    """Returns {(m, fam): [(round, edge, noedge, ratio), ...]} in FILE
    (= run) order, which is also cell-within-round run order."""
    cells = {}
    for line in Path(path).read_text().splitlines():
        m = floor_row_re.match(line)
        if not m:
            continue
        r, mm, fam, edge, noedge, ratio = m.groups()
        key = (int(mm), fam)
        cells.setdefault(key, []).append(
            (int(r), float(edge), float(noedge), float(ratio)))
    return cells


runs = {
    "run1": parse_floor(HERE / "floor_run1.log"),
    "run2": parse_floor(HERE / "floor_run2.log"),
}

CELLS = [(m, fam) for m in (2, 3, 4, 8) for fam in ("exact", "nullable")]

print("\n-- D77 gap test: |median-1| vs IQR, and vs whether 1.0 falls "
      "inside [min,max] --")
print(f"{'run':5s} {'m':2s} {'family':9s} {'median':8s} {'IQR':7s} "
      f"{'|med-1|':8s} {'min':7s} {'max':7s} {'1-in-range':11s} "
      f"{'separated':9s}")
gap_rows = []
for run_name, cells in runs.items():
    for (m, fam) in CELLS:
        rows = cells[(m, fam)]
        ratios = [r[3] for r in rows]
        med, iqr, lo, hi, n = median_iqr(ratios)
        diff = abs(med - 1.0)
        in_range = lo <= 1.0 <= hi
        separated = (diff > iqr) and (not in_range)
        gap_rows.append((run_name, m, fam, med, iqr, diff, lo, hi,
                          in_range, separated))
        print(f"{run_name:5s} {m:<2d} {fam:9s} {med:8.4f} {iqr:7.4f} "
              f"{diff:8.4f} {lo:7.4f} {hi:7.4f} "
              f"{'yes' if in_range else 'no':11s} "
              f"{'YES' if separated else 'no':9s}")

print("\n-- m=2 exact / m=2 nullable: per-round mode classification --")
print("   threshold: ratio > 1.20 => HIGH mode, else LOW mode "
      "(both modes' rough centers: ~1.0 low, ~1.8 high)")
for run_name, cells in runs.items():
    for fam in ("exact", "nullable"):
        rows = cells[(2, fam)]
        print(f"\n  {run_name} m=2 {fam}:")
        print(f"    {'round':5s} {'edge':8s} {'noedge':8s} {'ratio':7s} "
              f"{'mode':5s}")
        for (r, edge, noedge, ratio) in rows:
            mode = "HIGH" if ratio > 1.20 else "low"
            print(f"    {r:5d} {edge:8.4f} {noedge:8.4f} {ratio:7.4f} "
                  f"{mode:5s}")
        n_high = sum(1 for row in rows if row[3] > 1.20)
        edges_low = [row[1] for row in rows if row[3] <= 1.20]
        edges_high = [row[1] for row in rows if row[3] > 1.20]
        noedges_low = [row[2] for row in rows if row[3] <= 1.20]
        noedges_high = [row[2] for row in rows if row[3] > 1.20]
        print(f"    n_high={n_high}/15  n_low={15-n_high}/15")
        if edges_low:
            print(f"    edge   low-mode median={stats.median(edges_low):.4f}"
                  f"  (n={len(edges_low)})")
        if edges_high:
            print(f"    edge   high-mode median={stats.median(edges_high):.4f}"
                  f"  (n={len(edges_high)})")
        if noedges_low:
            print(f"    noedge low-mode median={stats.median(noedges_low):.4f}"
                  f"  (n={len(noedges_low)})")
        if noedges_high:
            print(f"    noedge high-mode median={stats.median(noedges_high):.4f}"
                  f"  (n={len(noedges_high)})")

print("\n-- adjacency: within-round cell order is "
      "(m2,exact)(m2,null)(m3,exact)(m3,null)(m4,exact)(m4,null)"
      "(m8,exact)(m8,null); a round's own m2-exact cell is measured "
      "IMMEDIATELY AFTER the PREVIOUS round's m8-nullable cell --")
for run_name, cells in runs.items():
    m2e = cells[(2, "exact")]
    m8n = cells[(8, "nullable")]
    print(f"\n  {run_name}: round r's m2-exact mode vs round (r-1)'s "
          f"m8-nullable ratio")
    print(f"    {'r':3s} {'m2exact_ratio':14s} {'m2exact_mode':6s} "
          f"{'prevm8null_ratio':16s}")
    for i, (r, edge, noedge, ratio) in enumerate(m2e):
        mode = "HIGH" if ratio > 1.20 else "low"
        prev = m8n[i - 1][3] if i > 0 else None
        prev_s = f"{prev:.4f}" if prev is not None else "  (round 1, n/a)"
        print(f"    {r:3d} {ratio:14.4f} {mode:6s} {prev_s:16s}")

print("\n-- adjacency: round-index correlation (does mode correlate with "
      "round number)? --")
for run_name, cells in runs.items():
    for fam in ("exact", "nullable"):
        rows = cells[(2, fam)]
        high_rounds = [r for (r, e, n, ratio) in rows if ratio > 1.20]
        low_rounds = [r for (r, e, n, ratio) in rows if ratio <= 1.20]
        print(f"  {run_name} m=2 {fam}: HIGH rounds={high_rounds}  "
              f"low rounds={low_rounds}")

print("\n-- cross-run consistency: is the split the SAME round numbers "
      "in run1 vs run2? --")
for fam in ("exact", "nullable"):
    r1 = runs["run1"][(2, fam)]
    r2 = runs["run2"][(2, fam)]
    r1_high = {r for (r, e, n, ratio) in r1 if ratio > 1.20}
    r2_high = {r for (r, e, n, ratio) in r2 if ratio > 1.20}
    print(f"  m=2 {fam}: run1 HIGH rounds={sorted(r1_high)}  "
          f"run2 HIGH rounds={sorted(r2_high)}  "
          f"intersection={sorted(r1_high & r2_high)}")
