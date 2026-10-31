#!/usr/bin/env python3
"""rulepilot step 5, the SEARCH (docs/design/pricing_rulepilot.md §5). Pre-registered: every
constant below is FIXED before any timing exists; drill.py exercises it on synthetic truths.

INPUT, one dataset (JSON; read_slot.py makes it from the timing job, drill.py synthesises it):
  {"picks": [pick names, "default" first],
   "sites": [{"id", "stratum", "pieces": {piece: value},
              "picks": {pick: arm},                        # every pick lands on an arm
              "cells": {"DENS/LEN": {arm: [ns per launch, by round]}}}]}
  The default arm's three copies are arms "<base>", "<base>#b", "<base>#c" (grid2's base copies).

THE HEADLINE (the manager's ruling: an UNKNOWN length): per cell, an arm's time over the cell's
best arm; per arm, the mean of that ratio over the cell's lengths, then the mean over the density
regimes (equal weight per log-length point, equal weight per regime): H(arm) >= 1.
  site oracle o = argmin H;  a pick's SCORE s = H(o) / H(pick's arm) (fraction of oracle speed);
  its RATIO r = 1 / s. Both CROSS-FIT over launches (odd rounds choose the cell best and o, even
  rounds are read, then the other way round; the two readings are averaged) so the oracle's own
  winner's curse does not lower every score. A list's score = the reach-weighted mean of s over
  the sites (every J1 question is one pattern of reach 1: weight 1).
THE NOISE FLOOR: per cell phi = max(|base#b - base|, nu * base) / base, nu = the median over all
  cells of |base#c - base| / base (regime_eval's NULL_c, literally); a site's floor f = the rms of
  phi over its cells.
PASS (pre-registered, both required, on the HELD-OUT half, for the list CHOSEN ON TRAINING):
  (1) held-out score >= PASS_SCORE (0.95);
  (2) no held-out site with r > TAIL_RATIO * (1 + 2 f) (1.5, beyond twice the site's floor).
THE SPLIT: stratified by the site's differing-slot signature (strata under MIN_STRATUM merged into
  `other`), ordered inside each stratum by sha256(SALT || id), alternately TRAIN / HELD-OUT.
THE SEARCH: every decision list of 0..3 rules "if L1 -> p1; elif L2 -> p2; elif L3 -> p3; else p0",
  a literal L being a BOOL piece or its negation, or a NUM piece's `>= t` or `< t` with t from the
  TRAINING values only. Exhaustive: for a fixed literal sequence the buckets are disjoint, so each
  bucket's best pick is found independently (exact, not greedy). Objective on TRAINING: the summed
  score, then fewer tail sites, then fewer non-default picks (ties). Length k PASSES when its
  training-chosen list passes on held-out; the verdict is the smallest passing k, or FAIL.

usage: search.py DATASET.json [--json OUT.json]
"""
import hashlib, itertools, json, math, statistics, sys
import numpy as np

SALT = "rulepilot-split-2026-10-31"
PASS_SCORE = 0.95
TAIL_RATIO = 1.5
MIN_STRATUM = 4
MAX_THRESH = 12          # thresholds per NUM piece: every distinct TRAINING value, thinned to this many quantiles above it
KMAX = 3

# ---------------------------------------------------------------- the headline, cross-fit
def _half_val(v, h):
    x = [t for r, t in enumerate(v, 1) if (h is None) or (r % 2 == (1 if h == "A" else 0))]
    x = [t for t in x if t == t]
    return statistics.median(x) if x else float("nan")

def _H(cells, arms, h):
    """per arm: mean over regimes of mean over lengths of time / cell best (best chosen on h)."""
    best = {}
    for c, av in cells.items():
        vals = {a: _half_val(av[a], h) for a in arms if a in av}
        best[c] = min(vals, key=lambda a: vals[a])
    return best

def _ratios(cells, arms, best, h):
    by_reg = {}
    for c, av in cells.items():
        reg = c.split("/")[0]
        b = _half_val(av[best[c]], h)
        for a in arms:
            by_reg.setdefault(reg, {}).setdefault(a, []).append(_half_val(av[a], h) / b)
    return {a: statistics.fmean(statistics.fmean(v[a]) for v in by_reg.values()) for a in arms}

def site_scores(site):
    """-> (s, r) dicts over arms, cross-fit; plus the raw (all launches) H for reports."""
    cells = site["cells"]
    arms = sorted({a for av in cells.values() for a in av if "#" not in a})
    nr = min(len(av[a]) for av in cells.values() for a in arms)
    out_s = {a: [] for a in arms}
    dirs = [("A", "B"), ("B", "A")] if nr >= 2 else [(None, None)]
    for x, y in dirs:
        best = _H(cells, arms, x)
        Hx = _ratios(cells, arms, best, x)
        o = min(arms, key=lambda a: Hx[a])
        Hy = _ratios(cells, arms, best, y)
        for a in arms:
            out_s[a].append(Hy[o] / Hy[a])
    s = {a: statistics.fmean(v) for a, v in out_s.items()}
    return s, {a: 1 / v for a, v in s.items()}

def noise(sites):
    rel = []
    for st in sites:
        for c, av in st["cells"].items():
            b = [k for k in av if k.endswith("#c")]
            if not b:
                continue
            base = b[0][:-2]
            m0 = statistics.median(av[base]); mc = statistics.median(av[base + "#c"])
            rel.append(abs(mc - m0) / m0)
    nu = statistics.median(rel) if rel else 0.0
    floors = {}
    for st in sites:
        phis = []
        for c, av in st["cells"].items():
            b = [k for k in av if k.endswith("#b")]
            if not b:
                continue
            base = b[0][:-2]
            m0 = statistics.median(av[base]); mb = statistics.median(av[base + "#b"])
            phis.append(max(abs(mb - m0), nu * m0) / m0)
        floors[st["id"]] = math.sqrt(statistics.fmean(p * p for p in phis)) if phis else 0.0
    return nu, floors, rel

# ---------------------------------------------------------------- split and literals
def split(sites):
    strata = {}
    for s in sites:
        strata.setdefault(s["stratum"], []).append(s)
    merged = {}
    for k, v in strata.items():
        merged.setdefault(k if len(v) >= MIN_STRATUM else "other", []).extend(v)
    train, test = [], []
    for k in sorted(merged):
        v = sorted(merged[k], key=lambda s: hashlib.sha256((SALT + s["id"]).encode()).hexdigest())
        for j, s in enumerate(v):
            (train if j % 2 == 0 else test).append(s)
    return train, test

def literals(train, piece_types):
    L = []
    for name, typ in piece_types.items():
        if typ == "BOOL":
            L.append((name, "==", 1)); L.append((name, "==", 0))
        else:
            vals = sorted({s["pieces"][name] for s in train})[1:]       # >= min is always true
            if len(vals) > MAX_THRESH:
                vals = sorted({vals[int(round(q * (len(vals) - 1) / (MAX_THRESH - 1)))] for q in range(MAX_THRESH)})
            for t in vals:
                L.append((name, ">=", t)); L.append((name, "<", t))
    return L

def holds(lit, s):
    n, op, t = lit; v = s["pieces"][n]
    return v == t if op == "==" else (v >= t if op == ">=" else v < t)

def lit_str(lit):
    n, op, t = lit
    if op == "==":
        return n if t else "not " + n
    return f"{n} {op} {t} (FITTED)"

# ---------------------------------------------------------------- scoring a site set
def matrices(sites, picks, floors):
    S = np.zeros((len(sites), len(picks))); R = np.zeros_like(S); T = np.zeros_like(S)
    for i, st in enumerate(sites):
        s, r = st["_s"], st["_r"]
        for j, p in enumerate(picks):
            a = st["picks"].get(p) or st["picks"]["default"]
            S[i, j] = s[a]; R[i, j] = r[a]
            T[i, j] = r[a] > TAIL_RATIO * (1 + 2 * floors[st["id"]])
    return S, R, T

def apply(lst, s):
    for lit, p in lst["rules"]:
        if holds(lit, s):
            return p
    return lst["default"]

def evaluate(lst, sites, picks, floors):
    if not sites:
        return dict(score=float("nan"), tail=0, worst=float("nan"), n=0, tail_sites=[], passed=False)
    sc, tl, wr, bad = [], 0, 0.0, []
    for st in sites:
        p = apply(lst, st); a = st["picks"].get(p) or st["picks"]["default"]
        sc.append(st["_s"][a]); r = st["_r"][a]; wr = max(wr, r)
        if r > TAIL_RATIO * (1 + 2 * floors[st["id"]]):
            tl += 1; bad.append((st["id"], round(r, 3)))
    score = statistics.fmean(sc)
    return dict(score=score, tail=tl, worst=wr, n=len(sites), tail_sites=bad,
                passed=bool(score >= PASS_SCORE and tl == 0))

# ---------------------------------------------------------------- the exhaustive search
def search(train, picks, floors, L):
    S, R, T = matrices(train, picks, floors)
    obj = S - 1e-6 * T - 1e-9 * (np.arange(len(picks)) > 0)[None, :]
    M = np.array([[holds(l, s) for s in train] for l in L], dtype=float)   # L x n
    N = 1.0 - M
    best = {}
    def better(k, val, rules_lits, picks_idx):
        if k not in best or val > best[k][0] + 1e-12:
            best[k] = (val, rules_lits, picks_idx)
    col = obj.sum(0); better(0, col.max(), (), (int(col.argmax()),))
    A = M @ obj; B = N @ obj
    for l1 in range(len(L)):
        better(1, A[l1].max() + B[l1].max(), (l1,), (int(A[l1].argmax()), int(B[l1].argmax())))
    for l1 in range(len(L)):
        R1 = N[l1]; b1 = A[l1].max(); p1 = int(A[l1].argmax())
        B2 = (M * R1) @ obj; RE = (N * R1) @ obj
        tot = b1 + B2.max(1) + RE.max(1); tot[l1] = -1e18
        l2 = int(tot.argmax())
        better(2, tot[l2], (l1, l2), (p1, int(B2[l2].argmax()), int(RE[l2].argmax())))
        for l2 in range(len(L)):
            if l2 == l1:
                continue
            R12 = R1 * N[l2]; b2v = (M[l2] * R1) @ obj
            B3 = (M * R12) @ obj; RE3 = (N * R12) @ obj
            tot3 = b1 + b2v.max() + B3.max(1) + RE3.max(1); tot3[[l1, l2]] = -1e18
            l3 = int(tot3.argmax())
            better(3, tot3[l3], (l1, l2, l3), (p1, int(b2v.argmax()), int(B3[l3].argmax()), int(RE3[l3].argmax())))
    out = {}
    for k, (val, ls, ps) in best.items():
        out[k] = dict(rules=[(L[l], picks[p]) for l, p in zip(ls, ps[:-1])], default=picks[ps[-1]])
    return out

def count_lists(nl, K):
    return {k: math.perm(nl, k) * K ** (k + 1) for k in range(KMAX + 1)}

def list_str(lst):
    parts = [f"if {lit_str(l)} -> {p}" for l, p in lst["rules"]]
    return "; ".join(parts + [f"else -> {lst['default']}"])

def run(ds, piece_types, quiet=False):
    sites = ds["sites"]; picks = ds["picks"]
    for st in sites:
        st["_s"], st["_r"] = site_scores(st)
    nu, floors, rel = noise(sites)
    train, test = split(sites)
    L = literals(train, piece_types)
    lists = search(train, picks, floors, L)
    base = dict(rules=[], default="default")
    res = dict(nu=nu, floor_median=statistics.median(floors.values()) if floors else 0,
               n_train=len(train), n_test=len(test), n_literals=len(L), n_picks=len(picks),
               counts=count_lists(len(L), len(picks)),
               baseline=dict(train=evaluate(base, train, picks, floors), test=evaluate(base, test, picks, floors)),
               lists={}, verdict=None)
    for k in sorted(lists):
        lst = lists[k]
        res["lists"][k] = dict(text=list_str(lst), train=evaluate(lst, train, picks, floors),
                               test=evaluate(lst, test, picks, floors))
    passing = [k for k in sorted(res["lists"]) if res["lists"][k]["test"]["passed"]]
    res["verdict"] = f"PASS at {passing[0]} rule(s)" if passing else "FAIL (no list of <= 3 rules passes held-out)"
    if not quiet:
        report(res)
    return res

def report(res):
    p = print
    p(f"noise: nu (median |base#c - base| / base) = {100 * res['nu']:.2f}%, median site floor f = {100 * res['floor_median']:.2f}%")
    p(f"split: train {res['n_train']} / held-out {res['n_test']} sites; literals {res['n_literals']}, picks {res['n_picks']}")
    p("distinct lists by length: " + ", ".join(f"{k}: {v:,}" for k, v in res["counts"].items()))
    b = res["baseline"]
    p(f"baseline cand_rows (default everywhere): train {b['train']['score']:.4f} tail {b['train']['tail']}; "
      f"held-out {b['test']['score']:.4f} tail {b['test']['tail']} worst {b['test']['worst']:.3f}")
    for k, v in res["lists"].items():
        tr, te = v["train"], v["test"]
        p(f"k={k}: {v['text']}")
        p(f"      train {tr['score']:.4f} tail {tr['tail']} | held-out {te['score']:.4f} tail {te['tail']} "
          f"worst {te['worst']:.3f} | over-fit {tr['score'] - te['score']:+.4f} | {'PASS' if te['passed'] else 'fail'}")
    p("VERDICT: " + res["verdict"])

if __name__ == "__main__":
    sys.path.insert(0, __import__("os").path.dirname(__file__))
    from pieces import PIECES
    ds = json.load(open(sys.argv[1]))
    pt = {n: t for n, (t, _, _) in PIECES.items() if n in ds["sites"][0]["pieces"]}
    res = run(ds, pt)
    if "--json" in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, default=str)
