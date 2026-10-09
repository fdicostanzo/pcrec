#!/usr/bin/env python3
"""Per-cell run-to-run spread for results/r2_timing.tsv (Frank, 2026-10-09:
"do a std dev and see"). For each (pattern, subject) cell: the mean and
stdev of each arm's per-pass median over the 7 passes, the coefficient of
variation, and whether each comparison's gap exceeds 2*(sd_x + sd_y).
Arms: o = today's artifact, c = form C walk-only, a = form A, b = form B."""
import csv, statistics as st, collections, sys, os
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "results/r2_timing.tsv")
g = collections.defaultdict(lambda: collections.defaultdict(list))
for r in csv.DictReader(open(path), delimiter="\t"):
    for a in "ocab":
        if r[a + "_med"] != "-":
            g[(r["name"], r["subject"])][a].append(float(r[a + "_med"]))
print("cells", len(g))
for a in "ocab":
    c = sorted(st.stdev(d[a]) / st.mean(d[a]) for d in g.values() if len(d[a]) > 1 and st.mean(d[a]))
    print(f"{a}: n {len(c)} CV median {c[len(c)//2]:.3f} p90 {c[int(len(c)*.9)]:.3f} max {c[-1]:.3f}")
for x, y in (("c", "o"), ("c", "b"), ("c", "a")):
    fast = slow = noise = 0; lines = []
    for k, d in sorted(g.items()):
        if len(d[x]) < 2 or len(d[y]) < 2:
            continue
        mx, my, sx, sy = st.mean(d[x]), st.mean(d[y]), st.stdev(d[x]), st.stdev(d[y])
        if abs(mx - my) > 2 * (sx + sy):
            if mx < my: fast += 1
            else: slow += 1; lines.append(f"    slower {k} {mx:.1f} vs {my:.1f}")
        else:
            noise += 1; lines.append(f"    inside-noise {k} {mx:.1f}±{sx:.2f} vs {my:.1f}±{sy:.2f}")
    print(f"{x} vs {y}: {x} faster {fast}, {x} slower {slow}, inside noise {noise}")
    print("\n".join(lines))
