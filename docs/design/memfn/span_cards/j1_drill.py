# span_cards rev 1.2 §3.6 drill (lane s2rev12; rev 1.1's by s2rev11, rev 1's by s2rev1): J1's pre-registered
# sweep rule, with PLACEMENT (review 2026-11-06 r5 PLACE / meas-2), and (rev 1.2, review r6 MEAS-6) the
# SWEEP that chooses the rule's margin m and cell count k. Units: the launch effect and each arm's within-launch
# noise are unit normal. 8 cells = 2 patterns x 4 (subject, regime) cells; a width's artifact is linked
# once per launch, so its placement is shared by its pattern's 4 cells within a launch. Placement s.d. tau:
#   fixed    -- rev 1's reading: ONE draw per (pattern, width) for the whole run (one build per width);
#   launch   -- rev 1.1: a fresh draw per (pattern, width, launch), the twin 128#b its own draw.
# Rule (§3.6): r_l = t_l(w) - t_l(128); w beats 128 on a cell iff every r_l < 0 and |med r| > 2 x
# sqrt(aa^2 + sp2(r)) (aa = med |t(128#b) - t(128)|, sp2 trimmed and scaled by K_TRIM); loses symmetrically.
# (b) iff some w beats on >= 5 of 8 cells and loses on none (several such w: (b) naming each); (a) iff no w
# beats on any cell; (c) otherwise. Model note (review r6 text-vs-script 5): r_l and aa are ABSOLUTE
# differences in unit-normal noise, the text's rule is RELATIVE (per-launch fractions of t_l(128)); equal to
# first order at small relative noise, not an integer drill of the text.
# Part 1 is rev 1.1's rule (m 2, k 5). Part 2 (rev 1.2): every (m, k) in M x K over one shared set of trials;
# the CHOICE RULE (stated before the run): among the (m, k) whose false (b) with no effect is at most 0.1 %
# at EVERY tau in {0, 1, 2, 4}, take the one with the highest power (effect 4, tau 1); ties go to the larger
# m, then the larger k. python3 -I j1_drill.py
import math, random

def med(v):
    s = sorted(v)
    return s[(len(s) - 1) // 2]
def trsd2(v):
    m = med(v)
    idx = max(range(len(v)), key=lambda i: (abs(v[i] - m), i))
    w = [v[i] for i in range(len(v)) if i != idx]
    mu = sum(w) / len(w)
    return 1.723 * sum((x - mu) ** 2 for x in w) / (len(w) - 1)

def j1(eff, tau, mode, trials):
    out = {"a": 0, "b": 0, "c": 0, "b2": 0}
    for _ in range(trials):
        beats, loses, anyb = [0] * 4, [0] * 4, False
        fixed = [[random.gauss(0, tau) for _ in range(6)] for _ in range(2)]   # widths 0..3, 128, 128#b
        for pat in range(2):
            pl = [[random.gauss(0, tau) for _ in range(6)] for _ in range(7)]
            P = (lambda l, k: fixed[pat][k]) if mode == "fixed" else (lambda l, k: pl[l][k])
            for _cell in range(4):
                lau = [random.gauss(0, 1) for _ in range(7)]
                t128 = [lau[l] + P(l, 4) + random.gauss(0, 1) for l in range(7)]
                tb = [lau[l] + P(l, 5) + random.gauss(0, 1) for l in range(7)]
                aa = med([abs(tb[l] - t128[l]) for l in range(7)])
                for w in range(4):
                    tw = [lau[l] + P(l, w) + random.gauss(0, 1) - (eff if w == 1 else 0) for l in range(7)]
                    r = [tw[l] - t128[l] for l in range(7)]
                    m, nz = med(r), math.sqrt(aa * aa + trsd2(r))
                    if all(x < 0 for x in r) and abs(m) > 2 * nz:
                        beats[w] += 1
                        anyb = True
                    if all(x > 0 for x in r) and abs(m) > 2 * nz:
                        loses[w] += 1
        nb = sum(1 for w in range(4) if beats[w] >= 5 and loses[w] == 0)
        if nb:
            out["b"] += 1
            out["b2"] += nb > 1
        elif not anyb:
            out["a"] += 1
        else:
            out["c"] += 1
    return {k: "%.2f%%" % (100.0 * v / trials) for k, v in out.items()}

random.seed(3)
print("no effect, tau 0 (20,000):", j1(0, 0, "launch", 20000))
for e in (2, 3, 4, 6):
    print("effect %d x within-sd, tau 0 (5,000):" % e, j1(e, 0, "launch", 5000))
for tau in (1, 2, 4):
    for mode in ("fixed", "launch"):
        print("tau %d %-6s no effect (4,000): %s | effect 4: %s" % (
            tau, mode, j1(0, tau, mode, 4000), j1(4, tau, mode, 4000)))

# ---- Part 2 (rev 1.2, MEAS-6): the (m, k) sweep -------------------------------------------------------------
M = (0.5, 1.0, 1.5, 2.0)
K = (4, 5, 6)
def cellstats(eff, tau):
    """one trial: per width w (0..3; w 1 carries the effect), per cell: (all r < 0, all r > 0, |med r| / nz)"""
    out = [[] for _ in range(4)]
    for pat in range(2):
        pl = [[random.gauss(0, tau) for _ in range(6)] for _ in range(7)]
        for _cell in range(4):
            lau = [random.gauss(0, 1) for _ in range(7)]
            t128 = [lau[l] + pl[l][4] + random.gauss(0, 1) for l in range(7)]
            tb = [lau[l] + pl[l][5] + random.gauss(0, 1) for l in range(7)]
            aa = med([abs(tb[l] - t128[l]) for l in range(7)])
            for w in range(4):
                tw = [lau[l] + pl[l][w] + random.gauss(0, 1) - (eff if w == 1 else 0) for l in range(7)]
                r = [tw[l] - t128[l] for l in range(7)]
                out[w].append((all(x < 0 for x in r), all(x > 0 for x in r),
                               abs(med(r)) / math.sqrt(aa * aa + trsd2(r))))
    return out
def sweep(eff, tau, trials):
    b = {(m, k): 0 for m in M for k in K}
    for _ in range(trials):
        st = cellstats(eff, tau)
        for m in M:
            beats = [sum(1 for neg, pos, q in st[w] if neg and q > m) for w in range(4)]
            loses = [sum(1 for neg, pos, q in st[w] if pos and q > m) for w in range(4)]
            for k in K:
                b[(m, k)] += any(beats[w] >= k and loses[w] == 0 for w in range(4))
    return {mk: 100.0 * v / trials for mk, v in b.items()}
random.seed(41)
NF, NP = 20000, 4000
false = {tau: sweep(0, tau, NF) for tau in (0, 1, 2, 4)}
power = {(e, tau): sweep(e, tau, NP) for e in (3, 4, 6) for tau in (0, 1, 2)}
print("\n== Part 2 (rev 1.2): (b) rates per (m, k); false = no effect (%d trials), power = one width truly "
      "better by e within-launch s.d. on every cell (%d trials)" % (NF, NP))
print("%-9s %s | %s" % ("m, k", "  ".join("false t%d" % t for t in (0, 1, 2, 4)),
                         "  ".join("e%d t%d" % (e, t) for e in (3, 4, 6) for t in (0, 1, 2))))
for m in M:
    for k in K:
        print("%-9s %s | %s" % ("%.1f, %d" % (m, k), "  ".join("%7.2f%%" % false[t][(m, k)] for t in (0, 1, 2, 4)),
                                 "  ".join("%5.1f%%" % power[(e, t)][(m, k)] for e in (3, 4, 6) for t in (0, 1, 2))))
ok = [(m, k) for m in M for k in K if all(false[t][(m, k)] <= 0.1 for t in (0, 1, 2, 4))]
best = max(ok, key=lambda mk: (power[(4, 1)][mk], mk[0], mk[1]))
print("CHOSEN by the stated rule: m %.1f, k %d (false <= 0.1 %% at every tau; power at effect 4, tau 1: %.1f %%)"
      % (best[0], best[1], power[(4, 1)][best]))
