#!/usr/bin/env python3
"""span_pick rev 5: smp20 `(?i)x/1234` priced with the design's OWN formula (§The pick: no `streams`
factor, byte(m) = the method's cost per subject byte over all its streams) under ONE rate model per
compile (D186 add. 2 as amended 2026-11-03, the rate-source table): a BLIND compile prices under P,
the default prior for its encoding, alone; a WITH-DATA compile under the named bundle B alone.

    python3 -I smp20.py WITNESS.out PRIOR.list -- NAME=BUNDLE.list ...

WITNESS.out is witness.sh's output: its default-arm and DEF-deny lines are TODAY's picks (the
incumbents) per rate source. Each .list is `pcrec --list-analysis NAME [-I DIR]` output (its
`#section freq` rows: key, count, ppm).

The rule (§The pick): a candidate QUALIFIES when it is cheaper than the incumbent under the one
model; the pick is the cheapest qualifier, else the incumbent. Arms: default (all six stops; the
two-member stop {X,x} by PAIR) and the DEF deny (PAIR filtered: the five one-member stops).

What this script does NOT compute (review B5): the band (no card has a noise, so the real rule
keeps the incumbent at every point: the picks printed are what it would choose once noise exists
and is smaller than the printed gap); TIE rows among qualifiers within band; KEY/M (the incumbents
are READ from WITNESS.out, never recomputed); walk and Horspool lines; SIMD-form cards.

Constants are STAND-INS, none measured for these methods: byte(memchr) 0.06 = plan_cost.def
C_MEMCHR (Zen 1); byte(PAIR) = k x byte(memchr), k 2 = two memchr streams (ASSUMPTION, t588tri (a));
hit 20 c per candidate returned (R-33's H_HIT ASSUMPTION, not a plan_cost.def row); cmp 2.5 =
C_VERIFY at pass 0 (cmp(form, pass) flat here); enter 20 = C_ENTER. Exact rationals, rounded half
away from zero once at the end (measure_sets §1.7).

BOUNDARIES are EXACT, not swept: every price is linear in k and in hit(PAIR), so the k (and the
hit(PAIR)) at which {X,x} and the cheapest one-member stop cost the same is solved in rationals at
each point of the stated hit grid (review B1: a region quoted from a sweep must state its grid).
"""
import sys
from fractions import Fraction as Q

PPM = 10**6
PAT = [b"xX", b"/", b"1", b"2", b"3", b"4"]          # offsets 0..5, the core positions' sets
BM = Q(6, 100)                                       # byte(memchr), per subject byte
CMP, ENTER = Q(5, 2), Q(20)
ARMS = {"default": list(range(6)), "DEF": list(range(1, 6))}
WARM = {"default": "[default]", "DEF": "[--memfn=no-window-search,no-window-skip]"}


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


def today(path):
    """{(arm, source): offset or None}: the stop set each compile's memchr calls search."""
    out = {}
    for line in open(path):
        for arm, tag in WARM.items():
            if not line.startswith(tag + " "):
                continue
            src = line[len(tag):].split()[0]
            stops = set(line.split("memchr on:")[1].split("RX_FINDINGS")[0].replace("'", "").split())
            hit = [i for i, s in enumerate(PAT) if set(chr(c) for c in s) == stops]
            out[(arm, src)] = hit[0] if hit else None
    return out


def mass(model, s):
    return Q(sum(model.get(b, 0) for b in s))


def price(model, stop, k=Q(2), hit_pair=Q(20), hit_one=Q(20)):
    """k = byte(PAIR) / byte(memchr); hit_pair, hit_one = hit(PAIR), hit(memchr)."""
    s = PAT[stop]
    byte, hit = (BM * k, hit_pair) if len(s) == 2 else (BM, hit_one)
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
    return "?" if stop is None else "@%d {%s}" % (stop, ",".join(chr(c) for c in sorted(PAT[stop])))


def pick(model, arm, inc, **kw):
    """(pick, qualifiers): cheapest candidate cheaper than the incumbent, else the incumbent."""
    p = {c: price(model, c, **kw) for c in ARMS[arm]}
    q = [c for c in ARMS[arm] if c != inc and p[c] < p[inc]]
    return (min(q, key=lambda c: (p[c], c)) if q else inc), q, p


args = sys.argv[1:]
cut = args.index("--") if "--" in args else len(args)
inc = today(args[0])
P = rates(args[1])
data = [(a.split("=", 1)[0], rates(a.split("=", 1)[1])) for a in args[cut + 1:]]
sources = [("blind", "P", P)] + [(n, "B:" + n, d) for n, d in data]

for hp in (Q(20), Q(40)):
    print("== prices, byte(PAIR) 0.12 (k 2), hit(PAIR) %s, hit(memchr) 20" % hp)
    for _s, mn, md in sources:
        row = [(rnd(price(md, i, hit_pair=hp)), i) for i in range(len(PAT))]
        print("%-10s %s  least %s" % (mn, "  ".join("%s %d" % (name(i), v) for v, i in row),
                                      name(min(row)[1])))
    print("-- the pick per rate source and arm (incumbent = today's compiled pick, WITNESS.out)")
    for src, mn, md in sources:
        for arm in ARMS:
            i = inc.get((arm, src))
            if i is None:
                print("%-10s %-7s incumbent not one modelled stop (WITNESS.out); not priced" % (mn, arm))
                continue
            c, q, p = pick(md, arm, i, hit_pair=hp)
            gap = "" if c == i else "  gap %d (%.3fx)" % (rnd(p[i] - p[c]), float(p[i] / p[c]))
            print("%-10s %-7s incumbent %s %d -> pick %s %d  qualifiers %s%s" % (
                mn, arm, name(i), rnd(p[i]), name(c), rnd(p[c]),
                ",".join(name(x) for x in q) or "none", gap))

print("== blind (P), default arm: EXACT boundary of {X,x} vs P's cheapest one-member stop")
print("   grid: hit(memchr) h1 in 5,10,20,40; hit(PAIR) = 1,2,4,8 x h1; k = byte(PAIR)/byte(memchr) solved")
for h1 in (Q(5), Q(10), Q(20), Q(40)):
    one = min(range(1, 6), key=lambda c: (price(P, c, hit_one=h1), c))
    po = price(P, one, hit_one=h1)
    cells = []
    for mult in (1, 2, 4, 8):
        rest = price(P, 0, k=Q(0), hit_pair=h1 * mult, hit_one=h1)  # {X,x} without its byte term
        ks = (po - rest) / (BM * PPM)
        cells.append("hit(PAIR) %s: %s" % (h1 * mult, "k* %.4f" % float(ks) if ks >= 1
                                           else "departs at every k >= 1 (k* %.4f)" % float(ks)))
    m = mass(P, PAT[0])
    rest_h = price(P, 0, k=Q(2), hit_pair=Q(0), hit_one=h1)
    hs = (po - rest_h) / m
    at2 = ("departs iff hit(PAIR) > %.3f (%.3fx h1)" % (float(hs), float(hs / h1)) if hs > 0
           else "departs at every hit(PAIR)")
    print("h1 %-3s cheapest one-member %s %d; {X,x} kept for k < k*, departs above: %s; at k 2 %s"
          % (h1, name(one), rnd(po), "; ".join(cells), at2))

print("== blind (P), DEF arm: P's cheapest one-member stop per hit(memchr) (k, hit(PAIR) do not enter)")
print("   " + "; ".join("h1 %s: %s" % (h1, name(min(range(1, 6), key=lambda c: (price(P, c, hit_one=h1), c))))
                      for h1 in (Q(5), Q(10), Q(20), Q(40))))
for n, d in data:
    print("== with data %s: B's cheapest stop over the grid (h1 5..40, hit(PAIR) 1-8 x h1, k 1.00-12.00 by 0.05)" % n)
    seen = {}
    for h1 in (Q(5), Q(10), Q(20), Q(40)):
        for mult in (1, 2, 4, 8):
            for kk in range(100, 1201, 5):
                b = min(range(6), key=lambda c: (price(d, c, k=Q(kk, 100), hit_pair=h1 * mult,
                                                       hit_one=h1), c))
                seen[b] = seen.get(b, 0) + 1
    print("   " + "; ".join("%s at %d points" % (name(b), v) for b, v in sorted(seen.items())))
