#!/usr/bin/env python3
"""Per-pattern inflation of the closure walk: prototype A over the shipped one.

Usage: inflation.py <base-stats.tsv> <proto-stats.tsv> [label]

Both files come from k18_stats.py, so the counters mean the same thing on both
sides. Patterns present in only one file are dropped and counted — the ratio
has to be over the same denominator to mean anything.
"""
import sys


def load(p):
    rows = {}
    with open(p) as fh:
        hdr = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) != len(hdr):
                continue
            d = dict(zip(hdr, f))
            rows[d["pattern"]] = d
    return rows


a = load(sys.argv[1])
b = load(sys.argv[2])
label = sys.argv[3] if len(sys.argv) > 3 else ""

common = [p for p in a if p in b]
print("== inflation: %s == (%d patterns compared, %d dropped as one-sided)"
      % (label, len(common), len(a) + len(b) - 2 * len(common)))

for metric in ("visits", "expansions"):
    ratios = []
    tot_a = tot_b = 0
    for p in common:
        va, vb = int(a[p][metric]), int(b[p][metric])
        tot_a += va
        tot_b += vb
        if va:
            ratios.append((vb / va, p, va, vb))
    ratios.sort()
    n = len(ratios)

    def q(f):
        return ratios[min(n - 1, int(f * (n - 1)))][0]

    print("  %-11s aggregate %d -> %d  (x%.3f)   per-pattern p50=%.2f p90=%.2f "
          "p99=%.2f max=%.2f  unchanged(=1.00)=%d"
          % (metric, tot_a, tot_b, tot_b / tot_a if tot_a else 0,
             q(.5), q(.9), q(.99), ratios[-1][0],
             sum(1 for r in ratios if abs(r[0] - 1.0) < 1e-9)))
    for r, p, va, vb in ratios[-5:][::-1]:
        print("      x%-6.2f %-7s -> %-9s %s" % (r, va, vb, p[:64]))
