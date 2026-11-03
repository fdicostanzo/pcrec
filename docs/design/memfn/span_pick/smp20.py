#!/usr/bin/env python3
"""span_pick rev 3: smp20 `(?i)x/1234` priced with the design's OWN formula (§The pick, rev 3 C1/C2:
no `streams` factor, byte(m) = the method's cost per subject byte over all its streams), read blind
(prior P and flat F) and with data (an analysis bundle B), plus the break-even byte(PAIR) under P.

    python3 -I smp20.py PRIOR.list [NAME=BUNDLE.list ...]

Each .list is `pcrec --list-analysis NAME [-I DIR]` output (its `#section freq` rows: key, count, ppm).
Constants are STAND-INS, none measured for these methods: byte(memchr) 0.06 = plan_cost.def C_MEMCHR
(Zen 1); byte(PAIR) 0.12 = 2 x C_MEMCHR (ASSUMPTION: two memchr streams, t588tri (a)); hit 20 c per
candidate returned (R-33's H_HIT ASSUMPTION, not a plan_cost.def row); cmp 2.5 = C_VERIFY at pass 0
(no pass-0.5 point exists, so cmp(form, pass) is flat here); enter 20 = C_ENTER. Exact rationals,
rounded half away from zero once at the end (measure_sets §1.7; the 1e-12 fixed-point scale of rev 3
moves no printed digit here).
"""
import sys
from fractions import Fraction as Q

PPM = 10**6
PAT = [b"xX", b"/", b"1", b"2", b"3", b"4"]          # offsets 0..5, the core positions' sets
BYTE = {1: Q(6, 100), 2: Q(12, 100)}                  # per subject byte, all streams, by |S|
HIT, CMP, ENTER = Q(20), Q(5, 2), Q(20)


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


def price(model, stop, byte_pair=None, hit_pair=None):
    s = PAT[stop]
    k = len(s)
    byte = BYTE[k] if k == 1 or byte_pair is None else byte_pair
    hit = HIT if k == 1 or hit_pair is None else hit_pair
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


models = [("P", rates(sys.argv[1])), ("F", None)]
for arg in sys.argv[2:]:
    n, p = arg.split("=", 1)
    models.append(("B:" + n, rates(p)))

for hp in (Q(20), Q(40)):
    print("== byte(PAIR) 0.12, hit(PAIR) %s" % hp)
    for mn, md in models:
        row = [(rnd(price(md, i, None, hp)), i) for i in range(len(PAT))]
        best = min(row)
        print("%-10s %s  least %s; {x,X}/'/' %.4f" % (
            mn, "  ".join("%s %d" % (name(i), v) for v, i in row), name(best[1]),
            float(price(md, 0, None, hp) / price(md, 1))))

# break-even byte(PAIR): '/' (memchr) cheaper than {x,X} (PAIR) under P iff byte(PAIR) exceeds it
P = models[0][1]
for hp in (Q(20), Q(40)):
    rest = price(P, 0, Q(0), hp)
    print("P break-even byte(PAIR) at hit(PAIR) %s: %.4f c/B (= %.3f x byte(memchr))" % (
        hp, float((price(P, 1) - rest) / PPM), float((price(P, 1) - rest) / PPM / BYTE[1])))
