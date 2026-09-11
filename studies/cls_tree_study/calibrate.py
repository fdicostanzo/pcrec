#!/usr/bin/env python3
"""calibrate.py — MEASURE what each kit member costs in `.text`, instead of
guessing it.

WHY THIS EXISTS.  The first version of the cost model priced a section by its
`.rodata` alone, on the reasoning that `.rodata` is where a class
representation's size lives.  The first full Pareto sweep refuted that
immediately: at the pure-size end (`lam=0`) `\\p{L}` came out at 9,672 object
bytes and 1,302 probe ops, while the middle policy came out at 4,311 bytes
and 111 ops — SMALLER AND FASTER AT ONCE.  A frontier point that is dominated
on both axes is not a trade-off, it is a modelling error: the range-compare
chains the size end piles up are free in `.rodata` and expensive in `.text`,
and the model could not see the bill.

So `.text` is measured and fed back. Each kit member's per-section `.text`
cost is recovered by ORDINARY LEAST SQUARES over the sweep rows already
collected — measured `.text` regressed on the per-form section counts, with
an intercept for the function's own fixed overhead:

    text  ~  c0 + sum over forms f of  n_f * text_f

The fit's residuals are reported per row; a member whose coefficient is not
stable across the population is called out rather than adopted, because a
cost model with a made-up constant in it is exactly what this file exists to
replace.

Input:  results/sweep_k53.tsv (and any other sweep_*.tsv given on the
        command line) — they carry `text`, `sections` and the form histogram.
Output: results/calibration.tsv, and the constants to paste into kit.py.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FORMS = ["ALL", "RANGES", "CUBES", "MASK64", "BITMAP", "PAGE64", "BSEARCH"]


def rows(paths):
    out = []
    for p in paths:
        for line in open(p, encoding="utf-8"):
            if line.startswith("#") or line.startswith("set\t"):
                continue
            f = line.rstrip("\n").split("\t")
            if len(f) < 16 or f[12] != "PASS":
                continue
            hist = {}
            for part in f[15].split(","):
                if ":" in part:
                    k, v = part.split(":")
                    hist[k] = int(v)
            out.append((f[0], f[5], float(f[7]), hist))
    return out


def lstsq(A, b):
    """Normal equations with Gauss-Jordan — no numpy on this box."""
    n = len(A[0])
    M = [[sum(A[r][i] * A[r][j] for r in range(len(A))) for j in range(n)]
         + [sum(A[r][i] * b[r] for r in range(len(A)))] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-9:
            continue
        M[c], M[p] = M[p], M[c]
        d = M[c][c]
        M[c] = [v / d for v in M[c]]
        for r in range(n):
            if r == c:
                continue
            fac = M[r][c]
            if fac:
                M[r] = [v - fac * w for v, w in zip(M[r], M[c])]
    return [M[i][n] for i in range(n)]


def main():
    paths = sys.argv[1:] or [os.path.join(HERE, "results", "sweep_k53.tsv")]
    data = rows(paths)
    if len(data) < len(FORMS) + 2:
        sys.exit("calibrate: only %d usable rows — run `make k53` first"
                 % len(data))

    A = [[1.0] + [float(h.get(f, 0)) for f in FORMS] for _, _, _, h in data]
    b = [t for _, _, t, _ in data]
    coef = lstsq(A, b)

    path = os.path.join(HERE, "results", "calibration.tsv")
    with open(path, "w") as out:
        out.write("# OLS: text ~ intercept + sum_f n_f * text_f\n")
        out.write("# rows=%d sources=%s\n" % (len(data), ",".join(
            os.path.basename(p) for p in paths)))
        out.write("term\tbytes_per_section\n")
        out.write("intercept\t%.1f\n" % coef[0])
        for f, c in zip(FORMS, coef[1:]):
            out.write("%s\t%.1f\n" % (f, c))
        out.write("#\n# per-row residuals\n")
        out.write("set\tpolicy\ttext_measured\ttext_fitted\tresidual\n")
        worst = 0.0
        ss_res = ss_tot = 0.0
        mean = sum(b) / len(b)
        for (name, pol, t, h), arow in zip(data, A):
            fit = sum(c * x for c, x in zip(coef, arow))
            r = t - fit
            worst = max(worst, abs(r))
            ss_res += r * r
            ss_tot += (t - mean) ** 2
            out.write("%s\t%s\t%.0f\t%.1f\t%+.1f\n" % (name, pol, t, fit, r))
        r2 = 1.0 - ss_res / ss_tot if ss_tot else float("nan")
        out.write("#\n# R2=%.4f worst_residual=%.1f bytes\n" % (r2, worst))

    print("wrote", path)
    print("R2=%.4f worst_residual=%.0f bytes over %d rows"
          % (r2, worst, len(data)))
    print("TEXT_BYTES = {")
    print("    # MEASURED by calibrate.py (OLS over %d sweep rows), not "
          "chosen." % len(data))
    print('    "_fixed": %.0f,' % coef[0])
    for f, c in zip(FORMS, coef[1:]):
        print('    "%s": %.0f,' % (f, c))
    print("}")


if __name__ == "__main__":
    main()
