# span_cards rev 1.1 §6 drill (lane s2rev11; rev 1's by s2rev1): (1) the trimmed spread's consistency factor
# K_TRIM (§3.4 step 6); (2) the coverage factor z on the estimator AS WRITTEN, noise = sqrt(aa^2 + sp2)
# (review 2026-11-06 r5 Z / meas-4), for a within-launch share f of each launch's variance: a launch's
# value is sqrt(1-f) x (a part the arm's twin shares) + sqrt(f) x (a part the twin draws afresh).
# THE EVENT (the one §6 states): a NEW draw (one launch at a new placement) of an equal-price card lands
# more than z x noise below its stored value, the one-sided false departure of a one-card comparison.
# For reference only: the STORED-values event (two equal cards, a departure on the stored medians beyond
# z x the quadrature of their noise), which span_pick rev 5.2's "~16 % at 1 sigma" sentence described.
# python3 -I coverage_drill.py
import math, random

def med(v):
    s = sorted(v)
    return s[(len(s) - 1) // 2]
def trim(v):
    m = med(v)
    idx = max(range(len(v)), key=lambda i: (abs(v[i] - m), i))
    return [v[i] for i in range(len(v)) if i != idx]
def trsd(v):
    w = trim(v)
    mu = sum(w) / len(w)
    return math.sqrt(sum((x - mu) ** 2 for x in w) / (len(w) - 1))

random.seed(7)
N = 200000
S = []
for _ in range(N):
    S.append(trsd([random.gauss(0, 1) for _ in range(7)]))
rms = math.sqrt(sum(s * s for s in S) / N)
print("(1) trimmed s.d. of 7 normal launches, %d draws: rms %.4f -> K_TRIM = 1/rms^2 = %.4f" % (N, rms, 1 / rms ** 2))
K = 1.723

def card(f):
    common = [random.gauss(0, 1) for _ in range(7)]
    v = [math.sqrt(1 - f) * common[l] + math.sqrt(f) * random.gauss(0, 1) for l in range(7)]
    vb = [math.sqrt(1 - f) * common[l] + math.sqrt(f) * random.gauss(0, 1) for l in range(7)]
    aa = med([abs(vb[l] - v[l]) for l in range(7)])
    return med(v), math.sqrt(aa * aa + K * trsd(v) ** 2)

M = 100000
print("(2) z on the estimator as written, %d draws per f" % M)
for f in (0.0, 0.5, 1.0):
    rows = [card(f) for _ in range(M)]
    new = [random.gauss(0, 1) for _ in range(M)]
    mean_noise = sum(r[1] for r in rows) / M
    line = []
    for z in (2.0, 2.5, 3.0, 3.5):
        dep = sum(1 for i in range(M) if new[i] - rows[i][0] < -z * rows[i][1]) / M
        line.append("z %.1f new %.2f%%" % (z, 100 * dep))
    pair = [card(f) for _ in range(M)]
    st = sum(1 for i in range(M) if rows[i][0] - pair[i][0] > 3.0 * math.hypot(rows[i][1], pair[i][1])) / M
    print("f %.1f  mean noise %.2f sigma  %s  | stored-values event at z 3.0: %.3f%%" % (
        f, mean_noise, "  ".join(line), 100 * st))
