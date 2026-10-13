#!/usr/bin/env python3
"""regimefacts: constants from the kit's vecspike time.log/counts.tsv (read-only).
Usage: python3 -I fit_vecspike.py .../worktrees/memfn-slot/spike1   (numpy for the OLS part)
 (1) sparse whole-subject scan, dig/all, calls=1 uses=1, n=40/65536/1048576:
     2-point line through (40 B, 1 MiB), checked against the 64 KiB point.
 (2) per-match fixed cost, find-all, one match per call (hex-run, bounded) at 1 MiB.
 (3) 3-term OLS t = a*calls + u*uses + b*n, all-mode V0, relative-error weighted."""
import csv, sys
import numpy as np
D = sys.argv[1]
rows = [l.split() for l in open(D + "/time.log") if l[0] != "#" and not l.startswith("cell") and len(l.split()) >= 10]
d = {(r[0], r[1], r[2], r[3]): (float(r[4]), float(r[5]), float(r[7])) for r in rows}
cnt = {(r["cell"], r["var"], r["subject"], r["mode"]): r for r in csv.DictReader(open(D + "/counts.tsv"), delimiter="\t")}
def val(c, s, m, v): return d[(c, s, m, "V0b")][1] if v == "V0" else d[(c, s, m, v)][0]
print("(1) sparse scan dig/all: 2-pt (40 B, 1 MiB); F=intercept, c=slope, n*=F/c, check=pred-vs-meas at 64 KiB")
for v in ["V0", "V1", "S1", "A1"]:
    y = [val("dig", s, "all", v) for s in ("short", "prose64k", "prose1m")]
    c = (y[2] - y[0]) / (1048576 - 40); F = y[0] - 40 * c
    p = F + 65536 * c
    print(f"  {v}: F={F:.2f} ns  c={c:.5f} ns/B  n*={F/c:.0f} B  64K pred {p:.0f} vs {y[1]:.0f} ({100*(p-y[1])/y[1]:+.1f}%)")
print("(2) find-all, one match per call, 1 MiB: ns per call, minus gap*c_walk")
for cell, s in (("hex-run", "prose1m"), ("bounded", "prose1m"), ("hex-run", "docs1m"), ("bounded", "docs1m"), ("bounded", "code1m"), ("hex-run", "code1m")):
    k = cnt[(cell, "V1", s, "all")]; n = 1048576
    for v in ("V0", "V1", "A1"):
        t = val(cell, s, "all", v); per = t / int(k["calls"])
        print(f"  {cell} {s} {v}: calls={k['calls']} uses={k['uses']} ns/call={per:.2f}  gap={n/int(k['calls']):.1f} B  minus gap*0.19={per-0.19*n/int(k['calls']):.2f}")
print("(3) OLS t = a*calls + u*uses + b*n (V0, all-mode, reached subjects); rel-error weighted")
N = {"short": 40, "prose64k": 65536, "digits64k": 65536, "prose1m": 1048576, "mix64k": 65536, "docs64k": 65536, "docs1m": 1048576, "code64k": 65536, "code1m": 1048576}
for cell in ("dig", "dfa-hat", "vm-hat-1", "vm-hat"):
    X = []; Y = []
    for s in N:
        if (cell, s, "all", "V0b") not in d: continue
        c = cnt.get((cell, "V1", s, "all"))
        if not c or int(c["uses"]) == 0: continue
        X.append([int(c["calls"]), int(c["uses"]), N[s]]); Y.append(val(cell, s, "all", "V0"))
    X = np.array(X, float); Y = np.array(Y); w = 1 / Y
    co, _, rk, _ = np.linalg.lstsq(X * w[:, None], Y * w, rcond=None)
    rel = np.abs(X @ co - Y) / Y
    print(f"  {cell}: rows={len(Y)} rank={rk} calls={co[0]:.2f} uses={co[1]:.2f} ns/B={co[2]:.4f} medrel={np.median(rel):.2f} maxrel={rel.max():.2f}")
