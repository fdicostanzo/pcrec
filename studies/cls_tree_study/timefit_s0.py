#!/usr/bin/env python3
"""timefit_s0.py — [CLS-TREE] S0: fit CT-2's PER-PROBE time model on the
ubuntubudu `bench2` run, and read the whole-set/kit tables off it
(docs/design/cls_tree_design.md §1.7; lane clsfit, 2026-09-29).

INPUT (committed, citable Linux timing — provenance lines in each file):
  results/bench2_ubuntubudu_20260929.tsv        12 K53 sets x 5 regimes x
                                                7 arms x 11 rounds
  results/bench_ubuntubudu_20260911.tsv          [T], the 09-11 run: used
                                                ONLY as a held-out transfer
                                                test (never fitted on)
  results/sweep_k53.tsv                          the old `model_ops` column

THE MODEL (design note §1.2, CT-2):
    T = t_bound + t_disp + sum_s p_s * t_leaf(form_s)
is not fitted as three opaque constants.  Every arm the harness timed is
REPLAYED here, probe by probe, over the harness's own subject stream (its
xorshift generator reproduced exactly, the first --nprobe probes of each
regime), and each probe is costed in four counted quantities:

    mispredicts  every conditional branch the arm's C executes (the global
                 bound test, each dispatch-tree `if`, the bsearch loop's
                 three branches) run through a 2-bit saturating counter per
                 static branch site — a deliberately simple predictor; on
                 random subjects nothing better exists, on `runs` it is the
                 "same way as last time" a real predictor also learns
    branches     conditional branches executed
    loads        table loads, first in a chain
    deploads     loads whose ADDRESS is a previous load's value

and ns/char = b0 + b1*mispredicts + b2*branches + b3*loads + b4*deploads is
fitted by OLS over EVERY (set, regime, arm) median at once — one model for
all seven arms, the kit's three policies, the flat bsearch and the three
whole-set tables alike.  p_s is not an input: the replay IS the regime's
distribution.  Nothing here times anything, so it runs anywhere.

It reports:
  1. the OLD term (`model_ops`) re-read on the new run — does the 09-11
     refutation replicate?
  2. the fitted coefficients, and per regime r / rho / pairwise ordering
     of the kit policies within a set (timefit.py's own three statistics),
     in-sample and leave-one-SET-out, with and without ^C;
  3. the same coefficients applied, unrefitted, to the 09-11 run;
  4. the whole-set vs kit tables (median ns/char above the harness floor).
"""
import argparse
import bisect
import collections
import csv
import math
import statistics as st

import clsets
import section

M64 = (1 << 64) - 1
ARMS = ("refbs", "bitmap1", "lam0", "lam16", "lam256", "page2w", "page3w")
KIT_ARMS = ("lam0", "lam16", "lam256")
REGIMES = ("member", "mixed", "full", "ascii", "runs")
FEATS = ("mispredicts", "branches", "loads", "deploads")


def rows(path):
    with open(path) as f:
        return list(csv.DictReader((l for l in f if not l.startswith("#")),
                                   delimiter="\t"))


def medians(path):
    ns = collections.defaultdict(list)
    for r in rows(path):
        ns[(r["set"], r["regime"], r["arm"])].append(float(r["ns_per_char"]))
    return {k: st.median(v) for k, v in ns.items()}


# ------------------------------------------------ the harness's subject stream

class Rng:
    """bench.py DRIVER's xorshift64, bit for bit."""
    def __init__(self):
        self.s = 88172645463325252

    def __call__(self):
        s = self.s
        s ^= (s << 13) & M64
        s ^= s >> 7
        s ^= (s << 17) & M64
        self.s = s
        return s


def subject(regime, iv, nprobe):
    """The first `nprobe` code points bench.py's build_subject() writes for
    `regime` — same generator, same draw order, same clamps."""
    cum, acc = [], 0
    for l, h in iv:
        acc += h - l + 1
        cum.append(acc)
    nmem = acc
    rnd = Rng()

    def member():
        r = rnd() % nmem
        k = bisect.bisect_right(cum, r)
        k = min(k, len(iv) - 1)
        prev = cum[k - 1] if k else 0
        return iv[k][0] + (r - prev)

    out = []
    if regime == "runs":
        while len(out) < nprobe:
            blk = member() & ~0xFF
            ln = 1 + rnd() % 32
            for _ in range(ln):
                if len(out) >= nprobe:
                    break
                cp = blk + (rnd() & 0xFF)
                out.append(min(cp, 0x10FFFF))
        return out
    for _ in range(nprobe):
        if regime == "member" or (regime == "mixed" and (rnd() & 1)):
            out.append(member())
        elif regime == "ascii":
            out.append(rnd() % 128)
        else:
            out.append(rnd() % 0x110000)
    return out


def verify_subjects(pop, path):
    """The replay is only as good as its subject stream: regenerate ALL
    2^20 probes of every (set, regime) and compare the member count and
    the positional checksum against the harness's own refbs row (round 0).
    A mismatch aborts -- features from a different stream fit nothing."""
    want = {(r["set"], r["regime"]): (int(r["hits"]), int(r["chk"]))
            for r in rows(path) if r["arm"] == "refbs" and r["round"] == "0"}
    n = 0
    for name, iv in pop:
        lo = [l for l, _ in iv]
        for reg in REGIMES:
            if (name, reg) not in want:
                continue
            h = c = 0
            for i, cp in enumerate(subject(reg, iv, 1 << 20)):
                k = bisect.bisect_right(lo, cp) - 1
                if k >= 0 and cp <= iv[k][1]:
                    h += 1
                    c += i + 1
            if (h, c) != want[(name, reg)]:
                raise SystemExit("timefit_s0: SUBJECT MISMATCH %s/%s: %s vs %s"
                                 % (name, reg, (h, c), want[(name, reg)]))
            n += 1
    print("subject streams verified: %d/%d (set, regime) streams reproduce the"
          " harness's hits+chk over all 2^20 probes" % (n, len(want)))


# ------------------------------------------------------------- the replay

class Counter:
    """Per-arm tallies over one probe stream, with one 2-bit counter per
    static branch site."""
    def __init__(self):
        self.pred = {}
        self.t = dict.fromkeys(FEATS, 0)

    def br(self, site, taken):
        c = self.pred.get(site, 2)
        if (c >= 2) != taken:
            self.t["mispredicts"] += 1
        self.pred[site] = min(3, c + 1) if taken else max(0, c - 1)
        self.t["branches"] += 1
        return taken

    def load(self, dep=0):
        self.t["loads"] += 1
        self.t["deploads"] += dep


def bsearch(c, site, lo, hi, x):
    """emit.PRELUDE's cls_bsearch, branch for branch."""
    a, b = 0, len(lo) - 1
    while c.br((site, "loop"), a <= b):
        m = (a + b) >> 1
        c.load()
        if c.br((site, "lt"), x < lo[m]):
            b = m - 1
            continue
        c.load()
        if c.br((site, "gt"), x > hi[m]):
            a = m + 1
            continue
        return 1
    return 0


class KitArm:
    """emit.emit()'s matcher: global bound, balanced dispatch tree, leaf."""
    def __init__(self, iv, lam):
        secs, _, _, forms = section.partition_c(iv, lam)
        self.iv = iv
        self.secs = [(iv[i][0], iv[j][1]) for i, j in secs]
        self.forms = forms
        self.lo, self.hi = iv[0][0], iv[-1][1]
        self.sub = [iv[i:j + 1] for i, j in secs]
        self.nsec = len(secs)

    def probe(self, c, cp):
        if c.br("bound", not (self.lo <= cp <= self.hi)):
            return 0
        a, b = 0, self.nsec - 1
        while a != b:
            m = (a + b) // 2
            if c.br((a, b, "le"), cp <= self.secs[m][1]):
                b = m
                continue
            if c.br((a, b, "gap"), cp < self.secs[m + 1][0]):
                return 0
            a = m + 1
        f = self.forms[a]
        if f == "BITMAP":
            c.load()
        elif f == "PAGE64":
            c.load()
            c.load(dep=1)
        elif f == "BSEARCH":
            sub = self.sub[a]
            return bsearch(c, ("leaf", a), [l for l, _ in sub],
                           [h for _, h in sub], cp)
        return 1


class RefArm:
    def __init__(self, iv):
        self.lo = [l for l, _ in iv]
        self.hi = [h for _, h in iv]

    def probe(self, c, cp):
        return bsearch(c, "ref", self.lo, self.hi, cp)


class TableArm:
    """bitmap1 / page2w / page3w: one bound test, then a load chain."""
    def __init__(self, iv, chain):
        self.lo, self.hi, self.chain = iv[0][0], iv[-1][1], chain

    def probe(self, c, cp):
        if c.br("bound", not (self.lo <= cp <= self.hi)):
            return 0
        c.load()
        for _ in range(self.chain - 1):
            c.load(dep=1)
        return 1


def arms_for(iv):
    return {"refbs": RefArm(iv), "bitmap1": TableArm(iv, 1),
            "lam0": KitArm(iv, 0.0), "lam16": KitArm(iv, 16.0),
            "lam256": KitArm(iv, 256.0),
            "page2w": TableArm(iv, 2), "page3w": TableArm(iv, 3)}


def features(pop, nprobe, regimes):
    """{(set, regime, arm): {feat: per-probe mean}} and {(set, arm): nsec}."""
    out, nsec = {}, {}
    for name, iv in pop:
        arms = arms_for(iv)
        for a in KIT_ARMS:
            nsec[(name, a)] = arms[a].nsec
        for reg in regimes:
            subj = subject(reg, iv, nprobe)
            for an, arm in arms.items():
                c = Counter()
                for cp in subj:
                    arm.probe(c, cp)
                out[(name, reg, an)] = {k: v / nprobe for k, v in c.t.items()}
    return out, nsec


# ------------------------------------------------------------- statistics

def pearson(x, y):
    mx, my = st.mean(x), st.mean(y)
    sx = sum((a - mx) ** 2 for a in x) ** .5
    sy = sum((b - my) ** 2 for b in y) ** .5
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def ranks(v):
    s = sorted(v)
    return [s.index(a) for a in v]


def spearman(x, y):
    return pearson(ranks(x), ranks(y))


def ols(X, y):
    """Normal equations, Gauss-Jordan; X rows WITHOUT the intercept."""
    n, k = len(X), len(X[0]) + 1
    A = [[0.0] * (k + 1) for _ in range(k)]
    for row, t in zip(X, y):
        z = [1.0] + list(row)
        for i in range(k):
            for j in range(k):
                A[i][j] += z[i] * z[j]
            A[i][k] += z[i] * t
    for i in range(k):
        p = max(range(i, k), key=lambda r: abs(A[r][i]))
        A[i], A[p] = A[p], A[i]
        for r in range(k):
            if r != i and A[i][i]:
                f = A[r][i] / A[i][i]
                A[r] = [a - f * b for a, b in zip(A[r], A[i])]
    return [A[i][k] / A[i][i] for i in range(k)]


def predict(beta, row):
    return beta[0] + sum(b * x for b, x in zip(beta[1:], row))


def pairwise(pred, meas, sets, reg, arms):
    """Within a set, over pairs of `arms`: does the model order them the
    way the stopwatch does?  (timefit.py's statistic, generalized.)"""
    ok = n = 0
    for s in sets:
        for i, a in enumerate(arms):
            for b in arms[i + 1:]:
                pa, pb = pred[(s, reg, a)], pred[(s, reg, b)]
                ma, mb = meas[(s, reg, a)], meas[(s, reg, b)]
                if pa == pb:
                    continue
                n += 1
                ok += (pa > pb) == (ma > mb)
    return ok, n


def fit_report(meas, feats, sets, regimes, label, loso=True):
    keys = [(s, r, a) for s in sets for r in regimes for a in ARMS
            if (s, r, a) in meas]
    X = [[feats[k][f] for f in FEATS] for k in keys]
    y = [meas[k] for k in keys]
    beta = ols(X, y)
    pred = {k: predict(beta, x) for k, x in zip(keys, X)}
    cv = {}
    if loso:
        for s in sets:
            tr = [i for i, k in enumerate(keys) if k[0] != s]
            b = ols([X[i] for i in tr], [y[i] for i in tr])
            for i, k in enumerate(keys):
                if k[0] == s:
                    cv[k] = predict(b, X[i])
    print("\n## %s: ns/char = %.3f + %.3f*mispredicts + %.3f*branches"
          " + %.3f*loads + %.3f*deploads   (%d medians)"
          % ((label,) + tuple(beta) + (len(keys),)))
    print("regime   | all 7 arms: r   rho  (LOSO r) | kit 3 policies: r    rho"
          "  pairwise  (LOSO pairwise) | all-arm pairwise")
    for reg in regimes:
        ka = [k for k in keys if k[1] == reg]
        kk = [k for k in ka if k[2] in KIT_ARMS]
        pw = pairwise(pred, meas, sets, reg, KIT_ARMS)
        pwall = pairwise(pred, meas, sets, reg, ARMS)
        line = ("%-8s |          %+.2f %+.2f" %
                (reg, pearson([pred[k] for k in ka], [meas[k] for k in ka]),
                 spearman([pred[k] for k in ka], [meas[k] for k in ka])))
        line += ("  (%+.2f)" % pearson([cv[k] for k in ka],
                                        [meas[k] for k in ka])) if cv else ""
        line += (" |                %+.2f %+.2f  %2d/%2d" %
                 (pearson([pred[k] for k in kk], [meas[k] for k in kk]),
                  spearman([pred[k] for k in kk], [meas[k] for k in kk]),
                  pw[0], pw[1]))
        if cv:
            p2 = pairwise(cv, meas, sets, reg, KIT_ARMS)
            line += "     (%2d/%2d)" % p2
        line += "        | %3d/%3d" % pwall
        print(line)
    return beta


def old_term(meas, sets, regimes, label):
    """timefit.py's reading, on any run: r/rho of ns against model_ops."""
    cols = ("set intervals members span lam policy sections text rodata total "
            "model_ro model_ops verify mismatches discovery_s forms").split()
    with open("results/sweep_k53.tsv") as f:
        sw = {(r["set"], r["lam"]): r for r in csv.DictReader(
            (l for l in f if not l.startswith("#")), delimiter="\t",
            fieldnames=cols) if r["set"] != "set"}
    print("\n## OLD term (model_ops, the pinned λ's currency) on %s" % label)
    for reg in regimes:
        o, t = [], []
        wins = n = 0
        for s in sets:
            v, ops = {}, {}
            for lam in ("0", "16", "256"):
                ops[lam] = float(sw[(s, lam)]["model_ops"])
                v[lam] = meas[(s, reg, "lam" + lam)]
                o.append(ops[lam])
                t.append(v[lam])
            for a, b in (("0", "16"), ("16", "256"), ("0", "256")):
                if ops[a] != ops[b]:
                    n += 1
                    wins += (ops[a] > ops[b]) == (v[a] > v[b])
        print("%-7s r(ns,ops)=%+.2f rho=%+.2f fewer-ops-is-faster %d/%d"
              % (reg, pearson(o, t), spearman(o, t), wins, n))


def tables(meas, sets, regimes, floor):
    print("\n## median ns/char ABOVE the harness floor (%.2f ns = the fastest"
          " cell in the run: call + loop + bound test)" % floor)
    for reg in regimes:
        print("-- %s" % reg)
        print("%-15s" % "set" + "".join("%9s" % a for a in ARMS)
              + "   page3w/bitmap1  best-kit/page3w")
        for s in sets:
            v = [meas[(s, reg, a)] - floor for a in ARMS]
            bk = min(meas[(s, reg, a)] for a in KIT_ARMS)
            print("%-15s" % s + "".join("%9.2f" % x for x in v)
                  + "   %14.2f  %15.2f" % (meas[(s, reg, "page3w")]
                                           / meas[(s, reg, "bitmap1")],
                                           bk / meas[(s, reg, "page3w")]))
        g = {}
        for a in ARMS:
            g[a] = math.exp(st.mean(math.log(meas[(s, reg, a)] /
                                             meas[(s, reg, "refbs")])
                                    for s in sets))
        print("%-15s" % "geo/refbs" + "".join("%9.3f" % g[a] for a in ARMS))


# --------------------------------------------- the dial, read off the fit

def sizes(pop):
    """Object bytes (.text + .rodata, the study's unit) per (set, arm):
    kit policies from results/sweep_k53.tsv (incl. lam4, the swept size
    minimum and today's -2 pin), page2w/page3w from results/whole_k53.tsv,
    bitmap1 as its exact rodata + the ~60 B of .text design note §1.3
    quotes."""
    import kit
    out = {}
    for r in rows("results/whole_k53.tsv"):
        out[(r["set"], "page2w")] = int(r["page2w_obj"])
        out[(r["set"], "page3w")] = int(r["page3w_obj"])
    cols = ("set intervals members span lam policy sections text rodata "
            "total model_ro model_ops verify mismatches discovery_s "
            "forms").split()
    with open("results/sweep_k53.tsv") as f:
        for r in csv.DictReader((l for l in f if not l.startswith("#")),
                                delimiter="\t", fieldnames=cols):
            if r["set"] != "set" and r["lam"] in ("0", "4", "16", "256"):
                out[(r["set"], "lam" + r["lam"])] = int(r["total"])
                out[(r["set"], "sections@lam" + r["lam"])] = int(r["sections"])
    for name, iv in pop:
        out[(name, "bitmap1")] = kit.FormBitmap(iv).rodata() + 60
    return out


MIN_SECTIONS = 16      # the gate's PLACEMENT: the timed K53 kits have 17-22
                       # sections at their size end; below 16 is unmeasured
Z_MID = 0.26           # opt_dial_design.md §3.2's z_mid


def first_match(sz, s, z_mid=Z_MID, min_sec=MIN_SECTIONS):
    """The PROPOSED per-position rule (design note §1.7.4), first match
    wins; K = the kit's size-minimal sectioning (lam4), P3/P2/B1 the
    whole-set tables.  Returns {position: arm}."""
    k, p3 = sz[(s, "lam4")], sz[(s, "page3w")]
    size_end = "page3w" if p3 < k else "lam4"
    if sz[(s, "sections@lam4")] >= min_sec and p3 <= (1 + z_mid) * k:
        mid = "page3w"
        fast = min(("page2w", "bitmap1"), key=lambda a: sz[(s, a)])
    else:
        mid = fast = "lam4"
    return {-2: size_end, -1: size_end, 0: mid, 1: mid, 2: fast}


def dial(meas, feats, sz, sets, beta):
    """Does the DP -- min bytes + lam*T over EVERY candidate, T the fitted
    per-probe model on member subjects -- pick anything the first-match
    table does not?  And what does each row cost, measured?"""
    cands = ("lam4", "lam0", "lam16", "lam256", "page3w", "page2w", "bitmap1")
    T = {}
    for s in sets:
        for a in cands:
            fa = "lam0" if a == "lam4" else a    # lam4 untimed: priced as lam0
            T[(s, a)] = predict(beta, [feats[(s, "member", fa)][f]
                                       for f in FEATS])
    print("\n## DIAL: first-match picks vs the DP objective min(bytes + lam*T),"
          " T = fitted member-subject ns (lam in BYTES PER NS)")
    fm = {s: first_match(sz, s) for s in sets}
    for pos in (-2, -1, 0, 1, 2):
        picks = collections.Counter(fm[s][pos] for s in sets)
        print("position %+d first-match: %s" % (pos, dict(picks)))
    print("lam(B/ns)  DP picks (12 sets)                         agrees with"
          " first-match at position")
    for lam in (0, 250, 500, 1000, 2000, 4000, 8000, 16000, 64000, 1e5, 1e6):
        pk = {s: min(cands, key=lambda a: sz[(s, a)] + lam * T[(s, a)])
              for s in sets}
        agree = [pos for pos in (-2, 0, 2)
                 if all(pk[s] == fm[s][pos] for s in sets)]
        print("%-10g %-45s %s" % (lam, dict(collections.Counter(pk.values())),
                                   agree or "-"))
    print("\nper set: bytes of K(lam4) / P3 / P2 / B1, P3/K, and the"
          " measured member ns of lam0 / lam16 / lam256 / P3 / P2 / B1")
    for s in sets:
        print("%-15s %6d %6d %7d %7d  %.3f   %s" % (
            s, sz[(s, "lam4")], sz[(s, "page3w")], sz[(s, "page2w")],
            sz[(s, "bitmap1")], sz[(s, "page3w")] / sz[(s, "lam4")],
            " ".join("%5.2f" % meas[(s, "member", a)] for a in
                     ("lam0", "lam16", "lam256", "page3w", "page2w",
                      "bitmap1"))))
    print("\nrow cost, geomean over the 12 sets (bytes; measured ns/char per"
          " regime; lam4 is untimed and read at lam0's time)")
    rowsets = {"today lam16 (pinned 0/-1)": lambda s: "lam16",
               "today lam256 (pinned +2)": lambda s: "lam256",
               "proposed -2/-1": lambda s: fm[s][-2],
               "proposed 0/+1": lambda s: fm[s][0],
               "proposed +2": lambda s: fm[s][2]}
    for lab, f in rowsets.items():
        b = math.exp(st.mean(math.log(sz[(s, f(s))]) for s in sets))
        t = []
        for reg in REGIMES:
            t.append(math.exp(st.mean(math.log(meas[(
                s, reg, "lam0" if f(s) == "lam4" else f(s))]) for s in sets)))
        print("%-28s %7.0f B  %s" % (lab, b, "  ".join(
            "%s %.2f" % (r, x) for r, x in zip(REGIMES, t))))


def population_rows(z_mids=(0.26, 0.20)):
    """The first-match rows over ALL 312 uprops sets (sizes only -- no set
    outside K53 was timed): how many sets each row sends to P3 / P2, and
    the row's total bytes against the kit's.  Joined by ROW ORDER, not by
    name: two uprops sets share a name (design note §1.3 [r1 MEAS-1])."""
    def body(path):
        return [l.rstrip("\n").split("\t") for l in open(path)
                if not l.startswith("#") and not l.startswith("set\t")]
    w = body("results/whole_uprops.tsv")
    sw = body("results/sweep_uprops.tsv")
    k0 = [r for r in sw if r[4] == "0"]
    k16 = [r for r in sw if r[4] == "16"]
    assert len(w) == len(k0) == len(k16) and all(
        a[0] == b[0] and a[1] == b[1] for a, b in zip(w, k0))
    print("\n## POPULATION (312 uprops sets, bytes only; K = kit lam0, the"
          " size end of results/sweep_uprops.tsv, which has no lam4)")
    tk0 = sum(int(r[9]) for r in k0)
    tk16 = sum(int(r[9]) for r in k16)
    print("kit lam0 total %d B, kit lam16 total %d B, page3w total %d B"
          % (tk0, tk16, sum(int(r[5]) for r in w)))
    for min_sec in (2, MIN_SECTIONS):
        for z in z_mids:
            n3 = tot = tot2 = 0
            for a, b in zip(w, k0):
                k, p3, p2 = int(b[9]), int(a[5]), int(a[4])
                if int(b[6]) >= min_sec and p3 <= (1 + z) * k:
                    n3 += 1
                    tot += p3
                    tot2 += p2
                else:
                    tot += k
                    tot2 += k
            print("gate sections>=%-2d z_mid %.2f: middle sends %3d/312 sets"
                  " to page3w, row total %6d B (%+.1f%% vs kit lam16);"
                  " +2 (page2w there) %6d B (%.2fx kit lam16)"
                  % (min_sec, z, n3, tot, 100.0 * (tot - tk16) / tk16, tot2,
                     tot2 / tk16))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--nprobe", type=int, default=16384)
    ap.add_argument("--bench2", default="results/bench2_ubuntubudu_20260929.tsv")
    ap.add_argument("--t0911", default="results/bench_ubuntubudu_20260911.tsv")
    args = ap.parse_args()

    pop = clsets.k53()
    meas = medians(args.bench2)
    sets = sorted({k[0] for k in meas})
    no_c = [s for s in sets if s != "^C"]
    floor = min(meas.values())
    verify_subjects(pop, args.bench2)

    old_term(meas, sets, REGIMES, "bench2 (2026-09-29)")
    old_term(meas, no_c, REGIMES, "bench2 without ^C")

    feats, nsec = features(pop, args.nprobe, REGIMES)
    print("\n## replayed features, first %d probes per regime" % args.nprobe)
    print("set\tregime\tarm\t" + "\t".join(FEATS) + "\tmeasured_ns")
    for s in sets:
        for r in REGIMES:
            for a in ARMS:
                f = feats[(s, r, a)]
                print("%s\t%s\t%s\t%s\t%.2f" % (s, r, a, "\t".join(
                    "%.3f" % f[k] for k in FEATS), meas[(s, r, a)]))

    beta = fit_report(meas, feats, sets, REGIMES, "FIT, bench2, all 12 sets")
    fit_report(meas, feats, no_c, REGIMES, "FIT, bench2, without ^C")

    t0 = medians(args.t0911)
    t_regs = ("member", "mixed", "full", "ascii")
    keys = [k for k in t0 if k[2] in ARMS and k[1] in t_regs]
    print("\n## TRANSFER: bench2's coefficients, unrefitted, on the 09-11 run"
          " [T] (%d medians, 5 arms)" % len(keys))
    pred = {k: predict(beta, [feats[k][f] for f in FEATS]) for k in keys}
    t_arms = ("refbs", "bitmap1", "lam0", "lam16", "lam256")
    for reg in t_regs:
        ka = [k for k in keys if k[1] == reg]
        kk = [k for k in ka if k[2] in KIT_ARMS]
        for lab, ss in (("12 sets", sets), ("no ^C", no_c)):
            ka2 = [k for k in ka if k[0] in ss]
            kk2 = [k for k in kk if k[0] in ss]
            print("%-7s %-8s all-arm r %+.2f rho %+.2f | kit r %+.2f rho %+.2f"
                  " pairwise %d/%d | all-arm pairwise %d/%d"
                  % ((reg, lab,
                      pearson([pred[k] for k in ka2], [t0[k] for k in ka2]),
                      spearman([pred[k] for k in ka2], [t0[k] for k in ka2]),
                      pearson([pred[k] for k in kk2], [t0[k] for k in kk2]),
                      spearman([pred[k] for k in kk2], [t0[k] for k in kk2]))
                     + pairwise(pred, t0, ss, reg, KIT_ARMS)
                     + pairwise(pred, t0, ss, reg, t_arms)))

    tables(meas, sets, REGIMES, floor)
    dial(meas, feats, sizes(pop), sets, beta)
    population_rows()


if __name__ == "__main__":
    main()
