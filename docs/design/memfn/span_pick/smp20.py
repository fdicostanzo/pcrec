#!/usr/bin/env python3
"""span_pick rev 4: smp20 `(?i)x/1234` priced with the design's OWN formula (§The pick: no `streams`
factor, byte(m) = the method's cost per subject byte over all its streams), the BLIND pick read as
MINIMAX (D186 add. 2) over the subject kinds P (the prior), F (flat) and the shipped real-data
bundles, the WITH-DATA pick read under each named bundle alone, and the card values that make '/'
the minimax pick.

    python3 -I smp20.py PRIOR.list KIND=BUNDLE.list ... -- NAME=BUNDLE.list ...

Before `--`: the blind kinds beside P and F (rev 4: log, weblog). After it: with-data bundles.
Each .list is `pcrec --list-analysis NAME [-I DIR]` output (its `#section freq` rows: key, count, ppm).
loss_r(c) = price_r(c) / min over the candidates of price_r; worst(c) = max over the kinds of
loss_r(c); the minimax pick has the least worst. Constants are STAND-INS, none measured for these
methods: byte(memchr) 0.06 = plan_cost.def C_MEMCHR (Zen 1); byte(PAIR) 0.12 = 2 x C_MEMCHR
(ASSUMPTION: two memchr streams, t588tri (a)); hit 20 c per candidate returned (R-33's H_HIT
ASSUMPTION, not a plan_cost.def row); cmp 2.5 = C_VERIFY at pass 0 (no pass-0.5 point exists, so
cmp(form, pass) is flat here); enter 20 = C_ENTER. Exact rationals, rounded half away from zero once
at the end (measure_sets §1.7; the 1e-12 fixed-point scale moves no printed digit here). No card
has a measured noise, so guard (b) keeps today's pick at every point printed: the picks below are
what the rule would choose once noise exists and is smaller than the worst-case gap.
"""
import sys
from fractions import Fraction as Q

PPM = 10**6
PAT = [b"xX", b"/", b"1", b"2", b"3", b"4"]          # offsets 0..5, the core positions' sets
BM = Q(6, 100)                                       # byte(memchr), per subject byte
CMP, ENTER = Q(5, 2), Q(20)


def rates(path):
    r, on = {}, False
    for line in open(path):
        if line.startswith("#section"):
            on = line.strip() == "#section freq"
            continue
        if on and not line.startswith("#") and line.strip():
            k, _c, ppm = line.split()[:3]
            r[int(k, 16)] = int(ppm)
    return r


def mass(model, s):
    return Q(len(s) * PPM, 256) if model is None else Q(sum(model.get(b, 0) for b in s))


def price(model, stop, k=Q(2), hit_pair=Q(20), hit_one=Q(20)):
    """k = byte(PAIR) / byte(memchr); hit_pair, hit_one = hit(PAIR), hit(memchr)."""
    s = PAT[stop]
    two = len(s) == 2
    byte, hit = (BM * k, hit_pair) if two else (BM, hit_one)
    m = mass(model, s)
    others = sorted(mass(model, PAT[j]) for j in range(len(PAT)) if j != stop)  # ascending mass
    ver, pr = Q(0), Q(1)
    for mo in others:
        ver += CMP * pr
        pr *= mo / PPM
    return byte * PPM + m * (hit + ver) + m * pr * ENTER


def rnd(x):
    return int(x + Q(1, 2)) if x >= 0 else -int(-x + Q(1, 2))


def name(stop):
    return "@%d {%s}" % (stop, ",".join(chr(c) for c in sorted(PAT[stop])))


def worst(kinds, **kw):
    pr = {kn: [price(md, i, **kw) for i in range(len(PAT))] for kn, md in kinds}
    loss = {kn: [p / min(v) for p in v] for kn, v in pr.items()}
    w = [max(loss[kn][i] for kn, _ in kinds) for i in range(len(PAT))]
    return loss, w, min(range(len(PAT)), key=lambda i: (w[i], i))


args = sys.argv[1:]
cut = args.index("--") if "--" in args else len(args)
kinds = [("P", rates(args[0])), ("F", None)]
kinds += [(a.split("=", 1)[0], rates(a.split("=", 1)[1])) for a in args[1:cut]]
data = [(a.split("=", 1)[0], rates(a.split("=", 1)[1])) for a in args[cut + 1:]]

for hp in (Q(20), Q(40)):
    print("== prices, byte(PAIR) 0.12 (k 2), hit(PAIR) %s, hit(memchr) 20" % hp)
    for mn, md in kinds + [("B:" + n, d) for n, d in data]:
        row = [(rnd(price(md, i, hit_pair=hp)), i) for i in range(len(PAT))]
        print("%-10s %s  least %s" % (mn, "  ".join("%s %d" % (name(i), v) for v, i in row),
                                      name(min(row)[1])))
    loss, w, pick = worst(kinds, hit_pair=hp)
    print("-- blind minimax over %s: loss per kind, worst" % ",".join(kn for kn, _ in kinds))
    for i in range(len(PAT)):
        print("%-8s %s  worst %.3f" % (name(i), "  ".join(
            "%s %.3f" % (kn, float(loss[kn][i])) for kn, _ in kinds), float(w[i])))
    print("minimax pick %s (worst %.3f); today's {X,x} worst %.3f" % (
        name(pick), float(w[pick]), float(w[0])))
    for n, d in data:
        b = min(range(len(PAT)), key=lambda i: price(d, i, hit_pair=hp))
        print("with data %s: least under B alone %s %d vs the blind incumbent %s %d" % (
            n, name(b), rnd(price(d, b, hit_pair=hp)), name(pick), rnd(price(d, pick, hit_pair=hp))))

# Which card values make '/' the minimax pick: k from 1.00 to 12.00 in steps of 0.05, for
# hit(memchr) in 5, 10, 20, 40 and hit(PAIR) at 1x, 2x, 4x, 8x of it; the k intervals per pick.
print("== minimax pick by card values (k = byte(PAIR)/byte(memchr))")
for h1 in (Q(5), Q(10), Q(20), Q(40)):
    for mult in (1, 2, 4, 8):
        runs, prev = [], None
        for kk in range(100, 1201, 5):
            k = Q(kk, 100)
            p = worst(kinds, k=k, hit_pair=h1 * mult, hit_one=h1)[2]
            if p != prev:
                runs.append([p, k, k])
                prev = p
            runs[-1][2] = k
        print("hit(memchr) %-3s hit(PAIR) %-4s %s" % (h1, h1 * mult, "; ".join(
            "%s k %.2f-%.2f" % (name(p), float(a), float(b)) for p, a, b in runs)))
