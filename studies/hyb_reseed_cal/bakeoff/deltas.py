#!/usr/bin/env python3
"""Absolute per-call deltas from a bake-off raw.tsv (D144 addendum 1).

usage: deltas.py RAW FORMS
Short-search rows (`/s:`): d and every delta in ns PER CALL (the raw value is
summed over the row's subjects, so it is divided by the subject count the
label carries: `x+41` = 42 subjects). Find-all rows (`/f:`): microseconds per
find-all pass, summed over the row's subjects (ms-scale; a ratio is
meaningful there). `launch` is |d2-d|, `layout` is |dL-d| (and |aL-a| when
timed), in the same unit. A delta inside the larger of the two is NULL.
"""
import re, statistics as st, sys

raw, forms = sys.argv[1], sys.argv[2].split()
cells, order = {}, []
for ln in open(raw):
    label, role, cc, v, t, ans, it = ln.rstrip("\n").split("\t")
    k = (label, cc)
    if k not in cells: cells[k] = {"role": role, "t": {}}; order.append(k)
    cells[k]["t"].setdefault(v, []).append(float(t))
print("%-24s %-5s %-7s %9s %4s %7s %7s  %s" % ("row", "cc", "role", "d", "unit", "launch", "layout",
      "  ".join("%8s" % v for v in ["a"] + forms)))
for k in order:
    c = cells[k]; med = {v: st.median(x) for v, x in c["t"].items()}; d = med["d"]
    if "/s:" in k[0]:
        m = re.search(r"\+(\d+)$", k[0]); unit, u = (int(m.group(1)) + 1 if m else 1), "ns"
    else:
        unit, u = 1000.0, "us"
    launch = abs(med["d2"] - d) / unit
    layout = abs(med["dL"] - d) / unit
    if "aL" in med: layout = max(layout, abs(med["aL"] - med["a"]) / unit)
    print("%-24s %-5s %-7s %9.2f %4s %7.2f %7.2f  %s" % (k[0], k[1], c["role"], d / unit, u, launch, layout,
          "  ".join("%+8.2f" % ((med[v] - d) / unit) if v in med else "%8s" % "-" for v in ["a"] + forms)))
