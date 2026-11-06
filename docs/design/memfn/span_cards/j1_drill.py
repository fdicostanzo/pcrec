# span_cards rev 1.1 §3.6 drill (lane s2rev11; rev 1's by s2rev1): J1's pre-registered sweep rule, with
# PLACEMENT (review 2026-11-06 r5 PLACE / meas-2). Units: the launch effect and each arm's within-launch
# noise are unit normal. 8 cells = 2 patterns x 4 (subject, regime) cells; a width's artifact is linked
# once per launch, so its placement is shared by its pattern's 4 cells within a launch. Placement s.d. tau:
#   fixed    -- rev 1's reading: ONE draw per (pattern, width) for the whole run (one build per width);
#   launch   -- rev 1.1: a fresh draw per (pattern, width, launch), the twin 128#b its own draw.
# Rule (§3.6): r_l = t_l(w) - t_l(128); w beats 128 on a cell iff every r_l < 0 and |med r| > 2 x
# sqrt(aa^2 + sp2(r)) (aa = med |t(128#b) - t(128)|, sp2 trimmed and scaled by K_TRIM); loses symmetrically.
# (b) iff some w beats on >= 5 of 8 cells and loses on none (several such w: (b) naming each); (a) iff no w
# beats on any cell; (c) otherwise. python3 -I j1_drill.py
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
