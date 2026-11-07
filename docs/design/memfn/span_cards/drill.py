# span_cards rev 1.2 §3.4-§3.5 drill (lane s2rev12; rev 1.1's by s2rev11): the estimator, gates, NULL rule and
# drift, implemented LITERALLY from the note's text, on (1) the constructed per-launch outcomes of §3.5's table
# and (2) one end-to-end example built from CELLS (steps 1-4 with the `events` column, a delta row's base
# named on its CELLS (the cell id's fifth field, rev 1.2 READY-1; rows carry `inputs` `-`), the control's slope
# over its own cells' lengths, and the anchor). Rev 1.2: the NULL rule's sign test over the trimmed six
# (MEAS-5); drift's threshold in standard errors of the statistic (MEAS-4, K_MED from place_drill.py B).
# The outcome table (FULL/PARTIAL/REFUSED/HELD) is outcome_drill.py's. Every input is printed beside its
# result. [rev1.4 r10-REV14-4] Rev 1.4's §3.5¶3a (sub-resolution delta rows) under review r10's rule: a row negative
# on all six trimmed launches stays `null` whatever r is; r is capped at policy.tsv's r_max_e6 (R_MAX below); the
# branch also needs the row's paired A/A within r. The table's delta rows are read as anchored values x_l (E = 1,
# the unit at 10^6), their twins' as xb_l. python3 -I drill.py
import random

def rhafz(n, d):                      # measure_sets §1.7: round half away from zero, exact integers
    s = -1 if (n < 0) != (d < 0) else 1
    n, d = abs(n), abs(d)
    return s * ((n + d // 2) // d)

def isqrt_rn(N):
    import math
    r = math.isqrt(N)
    return r + 1 if N - r * r > r else r

def med(v):                           # the LOWER median
    s = sorted(v)
    return s[(len(s) - 1) // 2]

K_TRIM_E6 = 1723000                   # DERIVED, coverage_drill.py
GATE = 30000                          # the card's gate_e6; the unit gates at GATE // 2
K_MED_E6 = 210300                     # DERIVED, place_drill.py B: var(lower median of 7) / one launch's var

def sp2(x):                           # step 6: drop the one launch farthest from the median (ties: the later)
    m = med(x)
    k = max(range(len(x)), key=lambda i: (abs(x[i] - m), i))
    w = [x[i] for i in range(len(x)) if i != k]
    n = len(w)
    Q = n * sum(t * t for t in w) - sum(w) ** 2
    return rhafz(K_TRIM_E6 * Q, 10**6 * n * (n - 1))

def row(x, xb):                       # steps 4-7 on the anchored per-launch values x_l and the twin's xb_l
    aa = med([abs(xb[i] - x[i]) for i in range(len(x))])
    return med(x), aa, isqrt_rn(aa * aa + sp2(x))

def cost_gate(value, noise, gate=GATE):
    return value > 0 and noise * 10**6 <= gate * value

def bimodal(xu, gate=GATE):           # the unit's anchored values (10^6 = the unit), sorted; k in 2..5
    s = sorted(xu)
    return any(s[k] - s[k - 1] > gate // 2 for k in range(2, 6))

def trim(x):                          # step 6's trim: drop the one launch farthest from the median (ties: later)
    m = med(x)
    k = max(range(len(x)), key=lambda i: (abs(x[i] - m), i))
    return [x[i] for i in range(len(x)) if i != k]

def null(D, Db):                      # delta rows: priced iff every D_l > 0 over the TRIMMED six (rev 1.2) and
    aaD = med([abs(Db[i] - D[i]) for i in range(len(D))])        # med(D_l) > aa_D (paired floor), med over 7
    return not (all(d > 0 for d in trim(D)) and med(D) > aaD), med(D), aaD

R_MAX = 53751                        # memfn/data/policy.tsv r_max_e6 (rmax_drill.py; UNMEASURED DEFAULT, D149)

def subres(x, xb):                    # [rev1.4 r10] §3.5¶3a over a row that FAILS the NULL rule: its status
    if all(d < 0 for d in trim(x)):
        return "null (negative on all six trimmed launches: a defect, whatever r)"
    own = 3 * isqrt_rn(rhafz(K_MED_E6 * sp2(x), 10**6))
    r = min(own, R_MAX)
    m, aa = med(x), med([abs(xb[i] - x[i]) for i in range(len(x))])
    if abs(m) <= r and aa <= r:
        return "sub-resolution: measured, value %d, noise max(r %d, noise %d)" % (max(0, m), r, row(x, xb)[2])
    return "null (|med| %d, aa %d, r %d = min(own %d, R_MAX): %s above r)" % (abs(m), aa, r, own, "|med|" if abs(m) > r else "A/A")

def drift(Cref, Cj, gate=GATE):       # per job: the control medians, relative; rev 1.2's threshold: the unit
    def rel(v):                       # card's half gate, or 3 standard errors of the statistic if larger
        M = med(v)
        return [rhafz(t * 10**6, M) for t in v]
    d = rhafz(abs(med(Cj) - med(Cref)) * 10**6, med(Cref))
    T = max(gate // 2, 3 * isqrt_rn(rhafz(K_MED_E6 * (sp2(rel(Cref)) + sp2(rel(Cj))), 10**6)))
    return d, T, d > T

print("== (1) the §3.5 table: constructed anchored per-launch values (unit = 10^6), L = 7")
base = [59900, 59950, 60000, 60000, 60050, 60100, 60020]
def show(name, x, xb, gate=GATE):
    v, aa, nz = row(x, xb)
    print("%-26s x=%s twin=x%+d -> value %d aa %d noise %d (%.3f%%) gate %s"
          % (name, x, xb[0] - x[0], v, aa, nz, 100.0 * nz / v, "PASS" if cost_gate(v, nz, gate) else "REFUSED"))
show("clean", base, [t + 60 for t in base])
o = list(base); o[5] = 64800
show("one outlier +8%", o, [t + 60 for t in o])
b = [60000, 63000, 60000, 63000, 60000, 63000, 60000]
show("bimodal 4/3 (5%)", b, [t + 60 for t in b])
show("A/A above spread (+600)", base, [t + 600 for t in base])
show("A/A above gate (+2000)", base, [t + 2000 for t in base])
u_clean = [999800, 999750, 1000000, 1000050, 999900, 1000100, 1000200]
u_bi = [1000000, 1030000, 999800, 1030200, 1000100, 1029900, 999900]
u_out = [1000000, 999800, 1000100, 1000050, 999900, 1000200, 1080000]
for name, u in (("unit clean", u_clean), ("unit 4/3 at +3%", u_bi), ("unit one outlier +8%", u_out)):
    print("%-26s x=%s -> bimodal %s" % (name, u, bimodal(u)))
for name, D, Db in (
        ("delta signs mixed", [1500, -2000, 3000, 500, -500, 2500, 1000], [1700, -1500, 2600, 900, -300, 2000, 1500]),
        ("delta negative", [-30000, -29000, -31000, -30500, -29500, -30200, -30100],
         [-29000, -30000, -30500, -31000, -30000, -29900, -30500]),
        ("delta clean 40 us/call", [40000000, 41000000, 39000000, 40000000, 40500000, 39500000, 40200000],
         [33000000, 46000000, 35000000, 44000000, 41000000, 37000000, 45000000])):
    n, m, aaD = null(D, Db)
    print("%-26s D=%s -> med %d aa_D %d: %s" % (name, D, m, aaD, subres(D, Db) if n else "priced"))
print("[rev1.4 r10] §3.5¶3a, R_MAX %d; per-event values x, the twin x + 3 unless named" % R_MAX)
for name, x, xb in (
        ("at zero, signs mixed", [40, -30, 10, -50, 20, -10, 30], None),
        ("all six trimmed negative", [-20, -60, -10, -40, -30, -90, -25], None),
        ("signs mixed, negative med", [-20, 30, -10, -40, 25, -90, -25], None),
        ("signs mixed above r", [1000, 1000, 1000, 1000, -50, -600, 1000], None),
        ("above R_MAX within own r", [80626, -161253, 215004, 80626, -107502, 268755, 75251], None),
        ("A/A above r", [40, -30, 10, -50, 20, -10, 30], [40, 170, -190, 150, -180, 190, -170])):
    xb = xb or [t + 3 for t in x]
    n, m, aaD = null(x, xb)
    print("%-26s x=%s -> %s" % (name, x, subres(x, xb) if n else "priced"))
Cref = [189200, 189150, 189300, 189250, 189180, 189220, 189400]
print("drift none        ", drift(Cref, [t + 50 for t in Cref]))
print("drift 3% tight     ", drift(Cref, [int(t * 1.03) for t in Cref]))
Wd = [189200, 191000, 187500, 190500, 188000, 192000, 186800]   # -1.27 %..+1.48 % about its median
print("drift 2%% in a wide spread (series %s)" % Wd, drift(Wd, [int(t * 1.02) for t in Wd]))

print("delta one spike, else clean", null([40000000, 41000000, -2000000, 40000000, 40500000, 39500000, 40200000],
                                         [41000000, 40000000, 39000000, 41000000, 40000000, 40500000, 40000000]))
print("\n== (2) end to end from cells: job J2 (ctl, unit, libc) and job J3 (ctl, base.walk, one hit row)")
# Inputs (a synthetic box): ctl and walk 0.19 ns/B, libc 0.012 ns/B, a walk hit 3.8 ns per hit at g 1024
# (20 walkbytes), launch state x(1 + 0.5 % N(0,1)), each cell x(1 + 0.2 % N(0,1)), seed 11.
random.seed(11)
LEN = (65536, 262144, 1048576)
cells = []                            # (group, arm, length, launch, events, ns_e6, cell id): `round` is `med`
def put(job, group, arm, length, l, events, ns_per_call, launch, base=None):
    ns_e6 = int(round(ns_per_call * launch * (1 + 0.002 * random.gauss(0, 1)) * 10**6))
    g = "J%d.%s" % (job, group)
    cid = "%s/%s/%d/%d" % (g, arm, length, l) + ("/" + base if base else "")   # rev 1.2: the cell id grammar
    cells.append((g, arm, length, l, events, ns_e6, cid))
for l in range(1, 8):
    for job in (2, 3):
        st = 1 + 0.005 * random.gauss(0, 1)
        for x in LEN:
            put(job, "ctl", "ctl", x, l, "-", 0.19 * x, st)
        if job == 2:
            for x in LEN:
                for arm in ("kit.find_byte.walk", "kit.find_byte.walk#b"):
                    put(2, "unit", arm, x, l, "-", 0.19 * x, st)
                for arm in ("kit.find_byte.libc", "kit.find_byte.libc#b"):
                    put(2, "byte", arm, x, l, "-", 0.012 * x, st)
        else:
            put(3, "base", "base.walk", 1048576, l, 0, 0.19 * 1048576, st)
            for arm in ("kit.find_hit.walk.random.one.1024", "kit.find_hit.walk.random.one.1024#b"):
                put(3, "hit.random.1024", arm, 1048576, l, 1024, 0.19 * 1048576 + 1024 * 3.8, st, base="base.walk")

def c(job, arm, length, l):
    hit = [t for t in cells if t[0].split(".")[0] == "J%d" % job and t[1] == arm and t[2] == length and t[3] == l]
    assert len(hit) == 1
    return hit[0][5]

def slope(job, arm, l):               # step 2, slope X1,X2,X3: S/D exact; the control's X are its own cells'
    xs = LEN if arm != "ctl" else tuple(sorted({t[2] for t in cells if t[0] == "J%d.ctl" % job and t[1] == "ctl"}))
    assert len(xs) == 3
    ys = [c(job, arm, x, l) for x in xs]
    n = 3
    S = n * sum(x * y for x, y in zip(LEN, ys)) - sum(LEN) * sum(ys)
    D = n * sum(x * x for x in LEN) - sum(LEN) ** 2
    return rhafz(S, D)

def events(job, arm):                 # one E over the arm's AND its twin's cells, else the set is refused
    E = {t[4] for t in cells if t[0].split(".")[0] == "J%d" % job and t[1] in (arm, arm + "#b")}
    assert len(E) == 1
    return E.pop()

def base_of(job, arm):                # rev 1.2 READY-1: the base named on the row's cells (id field 5), one
    B = {t[6].split("/")[4] for t in cells if t[0].split(".")[0] == "J%d" % job and t[1] in (arm, arm + "#b")}
    assert len(B) == 1                # base over the arm's and the twin's cells; its cells in J<j>.base
    b = B.pop()
    assert all(any(t[0] == "J%d.base" % job and t[1] == b and t[3] == l for t in cells) for l in range(1, 8))
    return b

def v(job, abs_l, l):                 # step 3: per launch, by the job's control
    return rhafz(abs_l * 10**6, slope(job, "ctl", l))

L = range(1, 8)
vw = [v(2, slope(2, "kit.find_byte.walk", l), l) for l in L]
W = med(vw)                           # step 4's anchor: the unit row's median
def anchored(job, arm, est):
    out = []
    for l in L:
        if est == "slope":
            a = slope(job, arm, l)
        else:                         # delta 1048576, base from the cells' ids, E from the arm's own cells
            key = arm[:-2] if arm.endswith("#b") else arm
            a = rhafz(c(job, arm, 1048576, l) - c(job, base_of(job, key), 1048576, l), events(job, key))
        out.append(rhafz(v(job, a, l) * 10**6, W))
    return out
for key, job, est in (("kit.find_byte.walk", 2, "slope"), ("kit.find_byte.libc", 2, "slope"),
                      ("kit.find_hit.walk.random.one.1024", 3, "delta")):
    x, xb = anchored(job, key, est), anchored(job, key + "#b", est)
    val, aa, nz = row(x, xb)
    extra = ""
    if est == "delta":
        base_arm = base_of(job, key)
        D = [c(job, key, 1048576, l) - c(job, base_arm, 1048576, l) for l in L]
        Db = [c(job, key + "#b", 1048576, l) - c(job, base_arm, 1048576, l) for l in L]
        n, m, aaD = null(D, Db)
        extra = " base %s (from its cells' ids) NULL rule: med D %d aa_D %d -> %s" % (base_arm, m, aaD, "null" if n else "priced")
    else:
        g = GATE // 2 if key == "kit.find_byte.walk" else GATE
        extra = " gate_e6 %d -> %s" % (g, "PASS" if cost_gate(val, nz, g) else "REFUSED")
    print("%-36s value_e6 %d aa %d noise_e6 %d%s" % (key, val, aa, nz, extra))
print("anchor W = %d; unit bimodal %s; drift J3 vs J2 %s" % (
    W, bimodal(anchored(2, "kit.find_byte.walk", "slope")),
    drift([slope(2, "ctl", l) for l in L], [slope(3, "ctl", l) for l in L])))
print("a delta cell id: %s" % [t[6] for t in cells if t[1].startswith("kit.find_hit")][0])
print("cells %d (expected (3 ctl + 6 unit + 6 libc + 3 ctl + 1 base + 2 hit) x 7 = %d)" % (len(cells), 21 * 7))
