# span_cards rev 1.2 drill (lane s2rev12; rev 1.1's by s2rev11): PLACEMENT and DRIFT (review 2026-11-06 r5
# PLACE, DRIFT; review 2026-11-06 r6 MEAS-1, MEAS-4, MEAS-9, MEAS-12).
# Part A: the UNIT row's refusal (half gate or bimodal test, §3.5) under the two readings of placement:
#   rev 1   -- one build per arm, the twin a FIXED perturbation: the twin sits at offset o, every launch;
#   rev 1.1 -- placement drawn PER LAUNCH for the arm and for its twin independently (s.d. tau), the
#              control one fixed executable.
#   Per-launch anchored value x_l = 10^6 (1 + e_l + p_l - c_l): e run noise (s), p placement, c the control's
#   own within-launch noise (s_c), common to the arm and its twin. Integer estimator = drill.py's.
#   Also: P(HELD) = two independent runs both refused; a two-class placement (phase classes), which is a
#   property of the text and SHOULD be held; and (rev 1.2) which test catches the two-class walk.
# Part A2 (rev 1.2, MEAS-1): HELD when the re-run re-links the SAME placements (rev 1.1's seed (job, l, arm))
#   against a re-run whose placements are drawn afresh (rev 1.2's seed (run id, job, l, arm)).
# Part B: the per-job drift check with a fixed control executable: job medians of the control's per-launch
#   values, launch-state s.d. s_L, a true drift d between jobs. K_MED (the variance of the lower median of 7
#   normal launches over one launch's variance) is DERIVED here; the power of rev 1.1's threshold
#   max(gate/2, 3 x isqrt(sp2_2 + sp2_j)) and of rev 1.2's max(gate/2, 3 s.e. of the statistic).
# python3 -I place_drill.py
import math, random

def rhafz(n, d):
    s = -1 if (n < 0) != (d < 0) else 1
    n, d = abs(n), abs(d)
    return s * ((n + d // 2) // d)
def isqrt_rn(N):
    r = math.isqrt(N)
    return r + 1 if N - r * r > r else r
def med(v):
    s = sorted(v)
    return s[(len(s) - 1) // 2]
K_TRIM_E6, GATE = 1723000, 30000
def sp2(x):
    m = med(x)
    k = max(range(len(x)), key=lambda i: (abs(x[i] - m), i))
    w = [x[i] for i in range(len(x)) if i != k]
    n = len(w)
    return rhafz(K_TRIM_E6 * (n * sum(t * t for t in w) - sum(w) ** 2), 10**6 * n * (n - 1))
def unit_causes(x, xb):
    aa = med([abs(xb[i] - x[i]) for i in range(7)])
    noise = isqrt_rn(aa * aa + sp2(x))
    s = sorted(x)
    bim = any(s[k] - s[k - 1] > GATE // 2 for k in range(2, 6))
    return noise * 10**6 > (GATE // 2) * med(x), bim
def unit_refused(x, xb):
    g, b = unit_causes(x, xb)
    return g or b

S_C = 0.001     # INPUT: the control's within-launch s.d. (0.1 %), UNMEASURED; the drill's figures barely move with it
N = 4000
def series(s, tau, mode, classes=False, o=None, pl=None):
    c = [random.gauss(0, S_C) for _ in range(7)]
    if o is not None:
        tau = o
    def p():
        if classes:
            return tau if random.random() < 0.5 else 0.0
        return random.gauss(0, tau)
    if pl is not None:                      # A2: the placements are given (a re-run of the same layout)
        pa, pb = pl
        x = [1 + random.gauss(0, s) + pa[l] - c[l] for l in range(7)]
        xb = [1 + random.gauss(0, s) + pb[l] - c[l] for l in range(7)]
    elif mode == "rev1":
        x = [1 + random.gauss(0, s) - c[l] for l in range(7)]
        xb = [1 + tau + random.gauss(0, s) - c[l] for l in range(7)]
    else:
        x = [1 + random.gauss(0, s) + p() - c[l] for l in range(7)]
        xb = [1 + random.gauss(0, s) + p() - c[l] for l in range(7)]
    return [int(round(t * 10**6)) for t in x], [int(round(t * 10**6)) for t in xb]
def run(*a, **k):
    return unit_refused(*series(*a, **k))

random.seed(5)
print("== A. unit refusal (half gate 1.5 %% or bimodal), %d runs each; s_c %.1f %%" % (N, 100 * S_C))
print("%-8s %-10s %-26s %-26s" % ("s", "o or tau", "rev 1 (fixed twin offset)", "rev 1.1 (drawn per launch)"))
for s in (0.0025, 0.005):
    for t in (0.0, 0.005, 0.01, 0.02):
        r1 = sum(run(s, t, "rev1") for _ in range(N)) / N
        r2 = sum(run(s, t, "rev11") for _ in range(N)) / N
        print("%-8s %-10s refused %6.2f%%  held %6.2f%%  refused %6.2f%%  held %6.2f%%" % (
            "%.2f%%" % (100 * s), "%.1f%%" % (100 * t), 100 * r1, 100 * r1, 100 * r2, 100 * r2 * r2))
print("(rev 1: a fixed offset refuses again on a re-run, so held = refused; rev 1.1: two independent runs)")
print("like for like: placement s.d. tau per build; rev 1's twin offset o = one draw of N(0, sqrt(2) tau) per run,")
print("the SAME o on its re-run (identical text, identical layout); rev 1.1 as above")
for s in (0.005,):
    for t in (0.005, 0.01, 0.02):
        ref = held = 0
        for _ in range(N):
            o = random.gauss(0, math.sqrt(2) * t)
            a, b = run(s, 0, "rev1", o=o), run(s, 0, "rev1", o=o)
            ref += a
            held += a and b
        print("s %.2f%% tau %.1f%%: rev 1 refused %.2f%% held %.2f%%" % (100 * s, 100 * t, 100.0 * ref / N, 100.0 * held / N))
for s, t in ((0.005, 0.01), (0.005, 0.02)):
    r = sum(run(s, t, "rev11", classes=True) for _ in range(N)) / N
    print("two phase classes 0/%.0f%% (p 1/2), s %.1f%%: refused %.2f%%, held %.2f%%" % (100 * t, 100 * s, 100 * r, 100 * r * r))

random.seed(17)
print("\n== A (rev 1.2). finer tau (MEAS-12) and which test catches a two-class walk (MEAS-9), %d runs each" % N)
for s in (0.0025, 0.005):
    print("s %.2f%%: " % (100 * s) + "  ".join(
        "tau %.1f%% -> %5.1f%%" % (100 * t, 100.0 * sum(run(s, t, "rev11") for _ in range(N)) / N)
        for t in (0.007, 0.01, 0.015, 0.02)))
for t in (0.015, 0.02):
    g = b = e = bo = 0
    for _ in range(N):
        gg, bb = unit_causes(*series(0.005, t, "rev11", classes=True))
        g += gg; b += bb; e += gg or bb; bo += bb and not gg
    print("two phase classes 0/%.1f%%, s 0.5%%: half gate %.1f%%, bimodal %.1f%%, either %.1f%%, bimodal ONLY %.1f%%"
          % (100 * t, 100.0 * g / N, 100.0 * b / N, 100.0 * e / N, 100.0 * bo / N))

NA2 = 20000
random.seed(23)
print("\n== A2 (rev 1.2, MEAS-1). HELD = both runs refuse; the re-run's placements the SAME (seed without a run id)")
print("   or drawn afresh (seed with the run id); s 0.5 %%, %d run pairs each" % NA2)
for t in (0.005, 0.007, 0.01):
    ref = same = fresh = 0
    for _ in range(NA2):
        pl = ([random.gauss(0, t) for _ in range(7)], [random.gauss(0, t) for _ in range(7)])
        a = run(0.005, t, "rev11", pl=pl)
        b_same = run(0.005, t, "rev11", pl=pl)
        b_fresh = run(0.005, t, "rev11")
        ref += a
        same += a and b_same
        fresh += a and b_fresh
    print("tau %.1f%%: refused %.2f%%; held, same layout %.2f%% (re-refuse | refused %.1f%%); "
          "held, fresh layout %.2f%% (%.1f%%)" % (100 * t, 100.0 * ref / NA2, 100.0 * same / NA2,
                                                 100.0 * same / max(ref, 1), 100.0 * fresh / NA2, 100.0 * fresh / max(ref, 1)))

print("\n== B. drift check")
random.seed(29)
NM = 400000
acc = acc2 = 0.0
for _ in range(NM):
    m = med([random.gauss(0, 1) for _ in range(7)])
    acc += m
    acc2 += m * m
kmed = acc2 / NM - (acc / NM) ** 2
print("K_MED: variance of the lower median of 7 normal launches over one launch's variance, %d draws: %.4f" % (NM, kmed))
K_MED_E6 = 210300
print("K_MED_E6 = %d (the integer the text writes); s.e. of |med_j - med_2| = sqrt(K_MED x 2) s_L = %.3f s_L"
      % (K_MED_E6, math.sqrt(2 * K_MED_E6 / 1e6)))
def rel(v):
    M = med(v)
    return [rhafz(t * 10**6, M) for t in v]
def refused(sL, d, rule):
    a = [int(round(10**9 * (1 + random.gauss(0, sL)))) for _ in range(7)]
    b = [int(round(10**9 * (1 + d + random.gauss(0, sL)))) for _ in range(7)]
    dd = rhafz(abs(med(b) - med(a)) * 10**6, med(a))
    v = sp2(rel(a)) + sp2(rel(b))
    if rule == "rev11":
        T = max(GATE // 2, 3 * isqrt_rn(v))
    else:
        T = max(GATE // 2, 3 * isqrt_rn(rhafz(K_MED_E6 * v, 10**6)))
    return dd > T
for rule, name in (("rev11", "rev 1.1's max(1.5 %, 3 x isqrt(sp2_ref + sp2_j))"),
                   ("rev12", "rev 1.2's max(1.5 %, 3 x isqrt(K_MED x (sp2_ref + sp2_j)))")):
    random.seed(9)
    print("%s, %d runs each" % (name, N))
    for sL in (0.002, 0.0035, 0.005, 0.01):
        print("  s_L %.2f%%: " % (100 * sL) + "  ".join(
            "d %.1f%% -> %5.1f%%" % (100 * d, 100 * sum(refused(sL, d, rule) for _ in range(N)) / N)
            for d in (0.0, 0.015, 0.02, 0.03, 0.05)))
random.seed(31)
print("rev 1.2's false refusal (d 0) WITHOUT the 1.5 %% floor (the s.e. term alone), %d runs each:" % (5 * N))
for sL in (0.005, 0.01, 0.02):
    f = 0
    for _ in range(5 * N):
        a = [int(round(10**9 * (1 + random.gauss(0, sL)))) for _ in range(7)]
        b = [int(round(10**9 * (1 + random.gauss(0, sL)))) for _ in range(7)]
        dd = rhafz(abs(med(b) - med(a)) * 10**6, med(a))
        f += dd > 3 * isqrt_rn(rhafz(K_MED_E6 * (sp2(rel(a)) + sp2(rel(b))), 10**6))
    print("  s_L %.1f%%: %.2f%%" % (100 * sL, 100.0 * f / (5 * N)))
