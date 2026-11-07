# span_cards rev 1.2 drill (lane s2rev12; rev 1.1's by s2rev11): the per-event resolution of a `delta` row
# (review 2026-11-06 r5 FLOOR / meas-6; review r6 MEAS-5, MEAS-8), under the paired NULL rule (§3.5):
#   rev 1.1: priced iff EVERY launch's per-call delta D_l > 0 and med(D_l) > aa_D = med |c(KEY#b) - c(KEY)|;
#   rev 1.2: the sign rule over the SIX launches left after dropping the one farthest from med(D_l) (ties: the
#            later launch; §3.4 step 6's trim), the same med(D_l) > aa_D;
# and against rev 1's floor FRG x base (FRG = grid1's 3.09 %).
# Model per launch: c(base) = C (1 + s e_b), c(arm) = (C + E h)(1 + s e_a), c(arm#b) likewise, each e
# standard normal and independent (run noise and per-launch placement, both arm-specific; the launch
# state cancels in the same-launch difference). C = the base's per-call cost in walkbytes over a 1 Mi
# subject, E = hits per call = 1 Mi / g, h = the per-hit cost (walkbytes) the row prices.
# INPUTS: byte ratios walk 1.0 and walk-set 1.0 (the unit), libc 0.06 and pair 0.12 (span_pick rev 5.2's
# smp20 STAND-INS: byte(memchr) 0.06, byte(PAIR) 2x); s in {0.25, 0.5, 1} % of a call; row 1's hit range
# h1 5-40 wb (smp20's grid). OUTPUT: h50 / h90 = the least h on a 0.25-wb grid priced in >= 50 % / 90 % of
# N runs. RESOLUTION (review r6 MEAS-8): at N = 2,000 a crossing near 90 % has a binomial s.e. of ~0.7 %, so a
# first-crossing h90 is uncertain by about a grid step or two; quote it rounded UP to 0.5 wb, one figure for
# the walk and walk-set pair (the larger), never to 0.25.
# Part 2 (MEAS-5): a one-sided cell SPIKE (probability q per cell, size k of the call) on the walk g 1024
# row at h 20, s 0.5 %, under both rules. The spike model (q, k) is ILLUSTRATIVE, not measured.
# python3 -I floor_drill.py
import math, random

def med(v):
    s = sorted(v)
    return s[(len(s) - 1) // 2]
def trimmed(v):
    m = med(v)
    idx = max(range(len(v)), key=lambda i: (abs(v[i] - m), i))
    return [v[i] for i in range(len(v)) if i != idx]
def priced(C, E, h, s, rule, q=0.0, k=0.0):
    def cell(x):
        y = x * (1 + s * random.gauss(0, 1))
        return y * (1 + k) if q and random.random() < q else y
    D, Db = [], []
    for _ in range(7):
        b = cell(C)
        a = cell(C + E * h)
        ab = cell(C + E * h)
        D.append(a - b)
        Db.append(ab - b)
    aaD = med([abs(Db[i] - D[i]) for i in range(7)])
    signs = D if rule == "rev11" else trimmed(D)
    return all(d > 0 for d in signs) and med(D) > aaD

random.seed(13)
LEN, FRG, N = 1048576, 0.0309, 2000
H = [0.25 * k for k in range(1, 400)]                   # 0.25 .. 99.75 wb per hit
print("%-9s %-6s %-7s %-25s %-25s %s" % ("form", "g", "s", "h50 / h90 wb (rev 1.1)", "h50 / h90 wb (rev 1.2)",
                                         "rev 1 floor FRG x C / E"))
def cross(C, E, s, rule):
    h50 = h90 = None
    for h in H:
        p = sum(priced(C, E, h, s, rule) for _ in range(N)) / N
        if h50 is None and p >= 0.5:
            h50 = h
        if p >= 0.9:
            h90 = h
            break
    return h50, h90
for form, ratio in (("walk", 1.0), ("walk-set", 1.0), ("pair", 0.12), ("libc", 0.06)):
    C = ratio * LEN
    for g in (256, 1024):
        E = LEN // g
        for s in (0.0025, 0.005, 0.01):
            a50, a90 = cross(C, E, s, "rev11")
            b50, b90 = cross(C, E, s, "rev12")
            print("%-9s %-6d %-7s %-25s %-25s %.2f" % (form, g, "%.2f%%" % (100 * s), "%s / %s" % (a50, a90),
                                                       "%s / %s" % (b50, b90), FRG * C / E))

random.seed(19)
NS = 6000
print("\n== Part 2 (MEAS-5): walk g 1024, h 20 wb, s 0.5 %%; a spike of +k on a cell with probability q; %d runs" % NS)
C, E = LEN, LEN // 1024
for q, k in ((0.0, 0.0), (0.02, 0.03), (0.05, 0.08)):
    r11 = sum(priced(C, E, 20, 0.005, "rev11", q, k) for _ in range(NS)) / NS
    r12 = sum(priced(C, E, 20, 0.005, "rev12", q, k) for _ in range(NS)) / NS
    print("q %.0f%% k %.0f%%: priced rev 1.1 %.1f%%, rev 1.2 %.1f%%" % (100 * q, 100 * k, 100 * r11, 100 * r12))
