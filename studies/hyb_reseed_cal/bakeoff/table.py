#!/usr/bin/env python3
"""Renders the A2 bake-off table from bakeoff.sh's raw.tsv.

usage: table.py RAW CELLS FORMS
  RAW    work/raw.tsv: label role cc variant ns ans iters, one line per launch
  CELLS  the pack's cells.tsv (to say which rows were NOT timed)
  FORMS  the space-separated form list the run used

Split out of bakeoff.sh (lane a2build) so a run that dies part-way can be
re-rendered from its raw file with the kit's own code, and so bakeoff.sh's
EXIT trap renders whatever was timed.

Two noise floors per row, reported separately because round 1 showed they
are different things (clang lkapos/f: d2/d 0.1%, dL/d 31.5%, all fifteen
launches of each within 0.5%):
  launch  |d2/d - 1|: the same binary relaunched
  layout  the larger of |dL/d - 1| and |aL/a - 1|: the same source with the
          link order swapped, for the deny and (when present) the shipped arm
`floor` is the larger of the two. An IMPROVE row passes at form/d <= 1 +
floor. A KEEP row compares form against `a`, so its allowance is a's own
spread: max(launch, |aL/a - 1|) when aL was timed, else the old floor. A row
whose layout floor exceeds LAYOUT_UNMEASURED is marked UNMEASURED: a
deterministic layout swing that large swamps any form-vs-a difference, and
the row's verdict needs layout-perturbed copies of every arm, not more
launches.
"""
import math, statistics as st, sys

LAYOUT_UNMEASURED = 0.10
raw, cellsf, forms = sys.argv[1], sys.argv[2], sys.argv[3].split()

cells, order = {}, []
for ln in open(raw):
    label, role, cc, v, t, ans, it = ln.rstrip("\n").split("\t")
    k = (label, cc)
    if k not in cells:
        cells[k] = {"role": role, "ans": ans, "t": {}}
        order.append(k)
    cells[k]["t"].setdefault(v, []).append(float(t))

cols = ["a"] + forms
print("%-30s %-5s %-7s %10s  %s  %6s %6s  %s" % ("cell/regime:subjects", "cc", "role", "d ns",
      " ".join("%6s" % c for c in cols), "launch", "layout", "ans"))
summ, unmeasured = {}, []
for k in order:
    c = cells[k]
    med = {v: st.median(x) for v, x in c["t"].items()}
    d = med["d"]
    launch = abs(med["d2"] / d - 1)
    layout = abs(med["dL"] / d - 1)
    if "aL" in med: layout = max(layout, abs(med["aL"] / med["a"] - 1))
    floor = max(launch, layout)
    keep_floor = max(launch, abs(med["aL"] / med["a"] - 1)) if "aL" in med else floor
    r = {v: med[v] / d for v in med}
    flag = ""
    if layout > LAYOUT_UNMEASURED:
        flag = "  UNMEASURED (layout floor)"
        unmeasured.append(k)
    print("%-30s %-5s %-7s %10.0f  %s  %5.1f%% %5.1f%%  %s%s" % (k[0], k[1], c["role"], d,
          " ".join("%6.3f" % r[v] if v in r else "%6s" % "-" for v in cols),
          100 * launch, 100 * layout, c["ans"], flag))
    if k in unmeasured: continue
    for v in forms:
        if v not in r: continue
        s = summ.setdefault((k[1], v), {"imp": [], "worst_imp": (0, ""), "worst_keep": (-9, ""), "imp_over": 0})
        if c["role"] == "improve":
            s["imp"].append(r[v])
            if r[v] > s["worst_imp"][0]: s["worst_imp"] = (r[v], k[0])
            if r[v] > 1 + floor: s["imp_over"] += 1
        elif c["role"] == "keep":
            loss = r[v] / r["a"] - 1 - keep_floor
            if loss > s["worst_keep"][0]: s["worst_keep"] = (loss, k[0])
print()
print("per compiler and form: improve rows (geomean of form/d, the largest form/d, rows above 1+floor);"
      " keep rows (worst loss vs a beyond a's floor; <= 0 passes). UNMEASURED rows are excluded.")
for (cc, v), s in sorted(summ.items()):
    gm = math.exp(sum(map(math.log, s["imp"])) / len(s["imp"])) if s["imp"] else float("nan")
    keep = "keep worst %+.1f%% (%s)" % (100 * s["worst_keep"][0], s["worst_keep"][1]) if s["worst_keep"][1] else "keep: no measured row"
    print("  %-5s %-4s improve geomean x%.3f  worst x%.3f (%s)  above-floor %d/%d   %s" % (
        cc, v, gm, s["worst_imp"][0], s["worst_imp"][1], s["imp_over"], len(s["imp"]), keep))
bad = [k for k in order if cells[k]["ans"] != "same"]
print("\nanswers: %s" % ("same on every row" if not bad else "DIFF on %d row(s): %s" % (len(bad), bad)))
if unmeasured: print("UNMEASURED (layout floor > %d%%): %s" % (100 * LAYOUT_UNMEASURED, unmeasured))

# Completeness: every (cells.tsv row, compiler) the run should have timed. A
# label is id/mode:<first subject>[+N]; a glob with no wildcard names its
# subject, so rows sharing an id and mode (lbvar f x4) are told apart.
ccs = sorted({cc for _, cc in order}) or ["?"]
want = []
for ln in open(cellsf):
    if ln.startswith("#") or not ln.strip(): continue
    f = ln.rstrip("\n").split("\t")
    g = f[5]
    pre = "%s/%s:" % (f[0], f[4])
    if "*" not in g: pre += g.rsplit("/", 1)[-1][:-len(".bin")] if g.endswith(".bin") else g.rsplit("/", 1)[-1]
    want.append(pre)
missing = ["%s %s" % (w, cc) for w in want for cc in ccs
           if not any(lab == w or lab.startswith(w + "+") or (w.endswith(":") and lab.startswith(w))
                      for lab, c in order if c == cc)]
print("timed rows: %d of %d (cells.tsv rows x %d compilers)" % (len(want) * len(ccs) - len(missing), len(want) * len(ccs), len(ccs)))
if missing: print("NOT TIMED: " + ", ".join(missing))
