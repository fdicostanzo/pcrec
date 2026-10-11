#!/usr/bin/env python3
"""lossreview/misc: a COUNTED-WORK cost model for the bench's set-grain ns.

    fit.py AGG.tsv NS.tsv [regime]

AGG.tsv = agg.py output (per-cell counted work from the instrumented
artifacts), NS.tsv = benchns.py output (the bench's pcrec median ns at
b8337c33).  Non-negative least squares (coordinate descent) of

    ns = a*calls + b*memchr_calls + c*memcmp_calls + d*scan_bytes + e*stepped_bytes
          + f*skip_bytes   (scalar loads in the prefilter/skip/pre-check phases)

over the throughput cells of the set.  The coefficients are the BENCH BOX's
(Zen 1) costs implied by pcrec's own counted work; they are a calibration,
not a measurement of any one mechanism.  Prints coefficients, per-cell fit
and a residual summary so a reader can see where the model is blind.
"""
import csv, sys, math
agg = list(csv.DictReader(open(sys.argv[1]), delimiter="\t"))
ns = {}
for r in csv.DictReader(open(sys.argv[2]), delimiter="\t"):
    ns[(r["pattern"], r["regime"])] = r
reg = sys.argv[3] if len(sys.argv) > 3 else "large-subject-throughput"
FEAT = ["calls", "memchr", "memcmp", "scan_B", "step_B", "skip_B"]
X, y, names = [], [], []
for a in agg:
    if a["regime"] != "throughput": continue
    pat = a["pid"].split("/")[1]
    r = ns.get((pat, reg))
    if not r or float(r["caps_ns"]) < 0: continue
    X.append([float(a["calls"]), float(a["mc"]), float(a["mcmp"]), float(a["T_scan"]),
              float(a["T_fwd"]) + float(a["T_rev"]) + float(a["T_vm"]) + float(a["T_anc"]),
              max(0.0, float(a["T_pre"]) + float(a["T_skip"]) + float(a["T_endw"]) + float(a["T_misc"]) + float(a["T_unk"]) - float(a["T_scan"]))])
    y.append(float(r["caps_ns"])); names.append(pat)
n, p = len(X), len(FEAT)
# relative weighting: minimise sum ((pred-y)/y)^2 so small cells count
W = [1.0 / v for v in y]
w = [0.0] * p
for it in range(20000):
    for j in range(p):
        num = den = 0.0
        for i in range(n):
            pred = sum(w[k] * X[i][k] for k in range(p)) - w[j] * X[i][j]
            num += W[i] ** 2 * X[i][j] * (y[i] - pred); den += W[i] ** 2 * X[i][j] ** 2
        if den > 0: w[j] = max(0.0, num / den)
print("cells", n)
for f, c in zip(FEAT, w): print("  %-8s %.4f ns" % (f, c))
res = []
for i in range(n):
    pred = sum(w[k] * X[i][k] for k in range(p)); res.append((pred / y[i], names[i], y[i], pred))
rr = sorted(res)
print("pred/bench median %.3f  p10 %.3f  p90 %.3f" % (rr[n // 2][0], rr[n // 10][0], rr[9 * n // 10][0]))
for r_, nm, yy, pp in rr: print("%-24s bench %10.0f pred %10.0f  x%.2f" % (nm, yy, pp, r_))
