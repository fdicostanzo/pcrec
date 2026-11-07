# span_cards rev 1.1 drill (lane s2rev11): PLACEMENT and DRIFT (review 2026-11-06 r5 PLACE, DRIFT).
# Part A: the UNIT row's refusal (half gate or bimodal test, §3.5) under the two readings of placement:
#   rev 1   -- one build per arm, the twin a FIXED perturbation: the twin sits at offset o, every launch;
#   rev 1.1 -- placement drawn PER LAUNCH for the arm and for its twin independently (s.d. tau), the
#              control one fixed executable.
#   Per-launch anchored value x_l = 10^6 (1 + e_l + p_l - c_l): e run noise (s), p placement, c the control's
#   own within-launch noise (s_c), common to the arm and its twin. Integer estimator = drill.py's.
#   Also: P(HELD) = two independent runs both refused; a two-class placement (phase classes), which is a
#   property of the text and SHOULD be held.
# Part B: the per-job drift check's power (§3.5, rev 1's threshold) with a fixed control executable:
#   job medians of the control's per-launch values, launch-state s.d. s_L, a true drift d between jobs.
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
def unit_refused(x, xb):
    aa = med([abs(xb[i] - x[i]) for i in range(7)])
    noise = isqrt_rn(aa * aa + sp2(x))
    s = sorted(x)
    bim = any(s[k] - s[k - 1] > GATE // 2 for k in range(2, 6))
    return noise * 10**6 > (GATE // 2) * med(x) or bim

S_C = 0.001     # INPUT: the control's within-launch s.d. (0.1 %), UNMEASURED; the drill's figures barely move with it
N = 4000
def run(s, tau, mode, classes=False, o=None):
    c = [random.gauss(0, S_C) for _ in range(7)]
    if o is not None:
        tau = o
    def p():
        if classes:
            return tau if random.random() < 0.5 else 0.0
        return random.gauss(0, tau)
    if mode == "rev1":
        x = [1 + random.gauss(0, s) - c[l] for l in range(7)]
        xb = [1 + tau + random.gauss(0, s) - c[l] for l in range(7)]
    else:
        x = [1 + random.gauss(0, s) + p() - c[l] for l in range(7)]
        xb = [1 + random.gauss(0, s) + p() - c[l] for l in range(7)]
    return unit_refused([int(round(t * 10**6)) for t in x], [int(round(t * 10**6)) for t in xb])

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

print("\n== B. drift check power (rev 1's threshold max(1.5 %%, 3 x isqrt(sp2_ref + sp2_j))), %d runs each" % N)
def rel(v):
    M = med(v)
    return [rhafz(t * 10**6, M) for t in v]
def refused(sL, d):
    a = [int(round(10**9 * (1 + random.gauss(0, sL)))) for _ in range(7)]
    b = [int(round(10**9 * (1 + d + random.gauss(0, sL)))) for _ in range(7)]
    dd = rhafz(abs(med(b) - med(a)) * 10**6, med(a))
    return dd > max(GATE // 2, 3 * isqrt_rn(sp2(rel(a)) + sp2(rel(b))))
random.seed(9)
for sL in (0.002, 0.0035, 0.005, 0.01):
    print("s_L %.2f%%: " % (100 * sL) + "  ".join(
        "d %.1f%% -> %5.1f%%" % (100 * d, 100 * sum(refused(sL, d) for _ in range(N)) / N)
        for d in (0.0, 0.015, 0.03, 0.05)))
