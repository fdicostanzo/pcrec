"""adasim/fit.py -- per-stretch cost model for the producer arms as a DELTA to the walk (the DFA/match work is
common to every arm and cancels): delta_ns(arm) = arm_ns - walk_ns = sum over stretches of
a + b*[stretch empty] + c*members + d*qmiss  (qmiss = ideal order-6 context predictor misses on the member bit,
e8why's Q numerator; the walk's byte loop mispredicts where the member bit is unpredictable).
Fit on flat's 41 J1 subjects (relative to the walk, weights 1/walk); LOO by cell; hold-out = V1 on the e8-only cells.
usage: fit.py OUT.json"""
import sys, json, itertools
sys.path.insert(0, "/home/pcrec/projects/pcrec/worktrees/flat/docs/dev/lanes/adasim")
from common import *

FORMS = {"A:[e,k,q]": (1, 2, 3), "B:[1,e,k,q]": (0, 1, 2, 3), "C:[1,e,k]": (0, 1, 2), "D:[e,k]": (1, 2)}


def agg(cell, subj):
    k, t, q = feats(cell, subj)
    return np.array([len(k), (k == 0).sum(), k.sum(), q.sum()], float)


def ls(X, y, w):
    x, *_ = np.linalg.lstsq(X * w[:, None], y * w, rcond=None)
    return x


def main():
    have = subjects(); ft = flat_table(); e8 = e8_table()
    fl = [(c, s) for (c, s) in ft if not c.startswith("an-")]
    fcells = sorted({c for c, _ in fl})
    rows = [(c, resolve(have, c, s), ft[(c, s)]) for c, s in fl]
    X = np.array([agg(c, s) for c, s, _ in rows]); wk = np.array([d["walk"] for _, _, d in rows])
    out = {"forms": {}}
    for arm in ("M64", "V1"):
        d = np.array([r[2][arm] for r in rows]) - wk; w = 1 / wk
        for fn, cols in FORMS.items():
            x = ls(X[:, cols], d, w); err = np.abs(X[:, cols] @ x - d) / wk
            le = []
            for c in fcells:
                tr = np.array([r[0] != c for r in rows])
                xx = ls(X[tr][:, cols], d[tr], w[tr]); le += list(np.abs(X[~tr][:, cols] @ xx - d[~tr]) / wk[~tr])
            full = np.zeros(4); full[list(cols)] = x
            out["forms"][f"{arm} {fn}"] = dict(coef=full.tolist(), fit_med=float(np.median(err)), fit_max=float(err.max()),
                                               loo_med=float(np.median(le)), loo_max=float(max(le)))
            print(f"{arm} {fn:12s} coef(a,b,c,d)={np.round(full, 3)} fit med {np.median(err):.3f} max {err.max():.3f}"
                  f" | LOO-cell med {np.median(le):.3f} max {max(le):.3f}  (|err| as fraction of the walk's ns)")
    # the chosen form: B for both arms unless LOO says otherwise (printed above); hold-out of V1 on e8-only cells
    ho_all = [(c, resolve(have, c, s), v) for (c, s), v in e8.items() if c not in fcells]
    # early-exit cells (the scan stops long before the end: S03's non-gazetteer subjects, 14-500 us on 2-42 MB)
    # cannot be priced from whole-subject features; a full scan costs >= ~12 ns/stretch (N cells), so < 4 is early exit
    ho = [h for h in ho_all if h[2]["walk"] / len(feats(h[0], h[1])[0]) >= 4.0]
    print("hold-out cells:", len(ho), "of", len(ho_all), "e8-only; early-exit excluded:", [(h[0], h[1]) for h in ho_all if h not in ho])
    Xh = np.array([agg(c, s) for c, s, _ in ho]); wh = np.array([v["walk"] for _, _, v in ho])
    dh = np.array([v["V1"] for _, _, v in ho]) - wh
    for fn in ("A:[e,k,q]", "B:[1,e,k,q]", "D:[e,k]"):
        coef = np.array(out["forms"][f"V1 {fn}"]["coef"]); pred = Xh @ coef
        err = (pred - dh) / wh
        sgn = np.mean(np.sign(pred) == np.sign(dh))
        big = np.abs(dh) / wh > 0.05
        sgnbig = np.mean(np.sign(pred[big]) == np.sign(dh[big])) if big.any() else float("nan")
        print(f"hold-out V1 {fn}: {len(ho)} e8-only cells, |err| med {np.median(np.abs(err)):.3f} p90 {np.percentile(np.abs(err), 90):.3f}"
              f" max {np.abs(err).max():.3f}; sign right {sgn:.2f} (on |delta|>5% of walk: {sgnbig:.2f}, n={big.sum()})")
        out.setdefault("holdout", {})[fn] = dict(n=len(ho), med=float(np.median(np.abs(err))), p90=float(np.percentile(np.abs(err), 90)),
                                                 max=float(np.abs(err).max()), sign=float(sgn), sign_big=float(sgnbig), nbig=int(big.sum()))
    worst = sorted(zip(np.abs((X[:, :] @ np.array(out["forms"]["M64 B:[1,e,k,q]"]["coef"]) - (np.array([r[2]["M64"] for r in rows]) - wk)) / wk), [(r[0], r[1]) for r in rows]))[-5:]
    print("worst M64 fit cells (B):", [(round(e, 3), c, s) for e, (c, s) in worst])
    json.dump(out, open(sys.argv[1], "w"), indent=1)


main()
