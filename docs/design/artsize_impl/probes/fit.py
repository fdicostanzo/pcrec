#!/usr/bin/env python3
"""Fit and validate the [ART-SIZE] STEP 2 size model on the corpus measurement."""
import sys, statistics as st

PATH = "/tmp/claude-1001/-home-duxevents-pcrec/2118fa38-0a1c-4bbd-ba29-87aee486bb5b/scratchpad/artsize3/corpus.tsv"


def load(path=PATH):
    rows = []
    with open(path) as f:
        hdr = f.readline().rstrip("\n").split("\t")
        for line in f:
            p = line.rstrip("\n").split("\t")
            d = dict(zip(hdr, p))
            rows.append(d)
    return rows


def num(d, k):
    v = d.get(k, "")
    return int(v) if v not in ("", None) else None


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    i = min(len(xs) - 1, int(round(q * (len(xs) - 1))))
    return xs[i]


def ols(X, y):
    """Least squares via normal equations; X is list of feature rows (with 1.0 intercept)."""
    n = len(X[0])
    A = [[sum(X[r][i] * X[r][j] for r in range(len(X))) for j in range(n)] for i in range(n)]
    b = [sum(X[r][i] * y[r] for r in range(len(X))) for i in range(n)]
    # gaussian elimination
    M = [A[i][:] + [b[i]] for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[piv] = M[piv], M[c]
        if abs(M[c][c]) < 1e-12:
            continue
        for r in range(n):
            if r == c:
                continue
            f = M[r][c] / M[c][c]
            for k in range(c, n + 1):
                M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] if abs(M[i][i]) > 1e-12 else 0.0 for i in range(n)]


def report(name, rows, feats, featnames):
    X = [[1.0] + [f(d) for f in feats] for d in rows]
    y = [num(d, "bytes") for d in rows]
    co = ols(X, y)
    errs = []
    for r, d in zip(X, rows):
        pred = sum(c * v for c, v in zip(co, r))
        act = num(d, "bytes")
        errs.append(abs(pred - act) / act)
    print("\n=== %s  (n=%d) ===" % (name, len(rows)))
    print("  model: bytes = %.1f + " % co[0] +
          " + ".join("%.4f*%s" % (c, nm) for c, nm in zip(co[1:], featnames)))
    print("  |rel err|  median %.4f  p90 %.4f  p99 %.4f  max %.4f" %
          (pct(errs, .5), pct(errs, .9), pct(errs, .99), max(errs)))
    return co, errs


def main():
    rows = load()
    ok = [d for d in rows if d.get("err", "") == "" and d.get("bytes", "")]
    ref = [d for d in rows if d.get("err", "")]
    print("total %d  compiled %d  refused %d" % (len(rows), len(ok), len(ref)))
    vm = [d for d in ok if d["engine"] == "vm"]
    dfa = [d for d in ok if d["engine"] == "dfa"]
    print("vm %d  dfa %d" % (len(vm), len(dfa)))

    b = [num(d, "bytes") for d in ok]
    print("bytes: median %d p90 %d p99 %d max %d" % (pct(b, .5), pct(b, .9), pct(b, .99), max(b)))
    lb = [num(d, "labels") for d in vm]
    print("vm labels: median %d p90 %d p99 %d max %d" % (pct(lb, .5), pct(lb, .9), pct(lb, .99), max(lb)))

    L = lambda d: float(num(d, "labels") or 0)
    T = lambda d: float(num(d, "tables") or 0)
    G = lambda d: float(num(d, "gotos") or 0)

    report("VM: labels only", vm, [L], ["labels"])
    report("VM: labels + tables", vm, [L, T], ["labels", "tables"])
    co, errs = report("ALL: labels + tables", ok, [L, T], ["labels", "tables"])
    report("DFA: tables only", dfa, [T], ["tables"])

    # correlation labels vs bytes on vm
    xs = [L(d) for d in vm]; ys = [float(num(d, "bytes")) for d in vm]
    mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
    cov = sum((a-mx)*(c-my) for a, c in zip(xs, ys))
    sx = sum((a-mx)**2 for a in xs) ** .5
    sy = sum((c-my)**2 for c in ys) ** .5
    print("\nVM  r(labels, bytes) = %.4f" % (cov/(sx*sy)))

    # top by bytes
    print("\nTop 12 by comment-excluded bytes:")
    for d in sorted(ok, key=lambda d: -num(d, "bytes"))[:12]:
        print("  %8d B  %6s lab  %5s tbl  eng=%-3s rungs=%-6s  %s" %
              (num(d, "bytes"), d["labels"], d["tables"], d["engine"], d["rungs"], d["pattern"][:60]))
    return co


if __name__ == "__main__":
    main()
