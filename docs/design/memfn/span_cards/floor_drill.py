# span_cards rev 1.1 drill (lane s2rev11): the per-event resolution of a `delta` row (review 2026-11-06 r5
# FLOOR / meas-6), under rev 1.1's paired NULL rule (§3.5: priced iff every launch's per-call delta D_l > 0
# and med(D_l) > aa_D = med |c(KEY#b) - c(KEY)|), against rev 1's floor FRG x base (FRG = grid1's 3.09 %).
# Model per launch: c(base) = C (1 + s e_b), c(arm) = (C + E h)(1 + s e_a), c(arm#b) likewise, each e
# standard normal and independent (run noise and per-launch placement, both arm-specific; the launch
# state cancels in the same-launch difference). C = the base's per-call cost in walkbytes over a 1 Mi
# subject, E = hits per call = 1 Mi / g, h = the per-hit cost (walkbytes) the row prices.
# INPUTS: byte ratios walk 1.0 and walk-set 1.0 (the unit), libc 0.06 and pair 0.12 (span_pick rev 5.2's
# smp20 STAND-INS: byte(memchr) 0.06, byte(PAIR) 2x); s in {0.25, 0.5, 1} % of a call; row 1's hit range
# h1 5-40 wb (smp20's grid). OUTPUT: h50 / h90 = the least h on the grid priced in >= 50 % / 90 % of runs.
# python3 -I floor_drill.py
import random

def med(v):
    s = sorted(v)
    return s[(len(s) - 1) // 2]
def priced(C, E, h, s):
    D, Db = [], []
    for _ in range(7):
        b = C * (1 + s * random.gauss(0, 1))
        a = (C + E * h) * (1 + s * random.gauss(0, 1))
        ab = (C + E * h) * (1 + s * random.gauss(0, 1))
        D.append(a - b)
        Db.append(ab - b)
    aaD = med([abs(Db[i] - D[i]) for i in range(7)])
    return all(d > 0 for d in D) and med(D) > aaD

random.seed(13)
LEN, FRG, N = 1048576, 0.0309, 1000
H = [0.25 * k for k in range(1, 400)]                   # 0.25 .. 99.75 wb per hit
print("%-9s %-6s %-7s %-22s %-22s %s" % ("form", "g", "s", "h50 wb (rev 1.1)", "h90 wb (rev 1.1)", "rev 1 floor FRG x C / E"))
for form, ratio in (("walk", 1.0), ("walk-set", 1.0), ("pair", 0.12), ("libc", 0.06)):
    C = ratio * LEN
    for g in (256, 1024):
        E = LEN // g
        for s in (0.0025, 0.005, 0.01):
            h50 = h90 = None
            for h in H:
                p = sum(priced(C, E, h, s) for _ in range(N)) / N
                if h50 is None and p >= 0.5:
                    h50 = h
                if p >= 0.9:
                    h90 = h
                    break
            print("%-9s %-6d %-7s %-22s %-22s %.2f" % (form, g, "%.2f%%" % (100 * s), h50, h90, FRG * C / E))
