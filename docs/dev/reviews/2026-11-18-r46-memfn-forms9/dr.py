# r46 crit-memfn-forms9 drills (scratch). usage: python3 -I dr.py NAME N
import sys, random, math, hashlib
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms9/work")
import cards as C
NAME, N = sys.argv[1], int(sys.argv[2])
orig = C.synth_layout_effect
def hsh(*a):
    return int(hashlib.sha256(repr(a).encode()).hexdigest(), 16)
def tdraw(rng, nu):
    return rng.gauss(0, 1) / math.sqrt(rng.gammavariate(nu / 2, 2.0) / nu) / math.sqrt(nu / (nu - 2))
def sle(lay, body, v, rg=None):
    m = lay["model"]
    st = lay["store"]
    if m == "x_phase_noisyvar":          # phase main effect x variant-0 launches carry extra fresh noise
        base = orig(dict(lay, model="phase"), body, v, rg)
        if v == 0 and body[0] not in ("I", "aa") or (v == 0 and lay.get("all")):
            r = st.setdefault("_nr", random.Random(hsh("nr", id(st))))
            e = tdraw(r, lay["nu"]) if lay.get("nu") else r.gauss(0, 1)
            return base * math.exp(lay["s"] * e)
        return base
    if m == "x_onerow":                  # interaction in ONE row of a head text: regime picked per body (hash)
        if body[0] in ("I", "aa"):
            return 1.0
        if lay.get("pat") and body[1] != lay["pat"]:
            return 1.0
        rgs = C.REGIMES
        want = lay.get("rg") or rgs[hsh("rg", body) % len(rgs)]
        if rg != want:
            return 1.0
        if (body, "or", v) not in st:
            st[(body, "or", v)] = math.exp(st["_rng"].gauss(0, lay["tau"]))
        return st[(body, "or", v)]
    return orig(lay, body, v, rg)
C.synth_layout_effect = sle
# instrument text_interaction: per-text pe df, texts read, excluded
ti_orig = C.text_interaction
REC = {"read": [], "excl": [], "dfp": []}
def ti(te, stats, regime_of, alpha=None, info=None):
    out = ti_orig(te, stats, regime_of, alpha, info)
    REC["read"].append(len(out)); REC["excl"].append(len(stats) - len(out))
    for t, st in stats.items():
        REC["dfp"].append(sum(df for _k, _n, _ss, df in st["rows"]))
    return out
C.text_interaction = ti
def rate(seed, win, iv, pt, **kw):
    old = C._flags(INTERACTION_VOID=iv, INTER_PE_PER_TEXT=pt)
    try:
        rng = random.Random(seed)
        hit = fl = off = 0
        for _ in range(N):
            v = C.synth_night(rng, 0.01, cellwins=C.power_cells(8, "hit-dense", win) if win else None, **kw)
            hit += v["hstar"] == 8; fl += v.get("inter_flagged", 0) > 0; off += v["hstar"] != C.GRID_TOP
    finally:
        C._flags(**old)
    return hit, fl, off
def row(label, seed, win=None, arms=((True, True), (False, True), (True, False)), **kw):
    out = []
    for iv, pt in arms:
        h, f, o = rate(seed, win, iv, pt, **kw)
        out.append("%s/%s: fl %d h8 %d P!=64 %.3f" % ("von" if iv else "voff", "pt" if pt else "pool", f, h, o / N))
    print("%-44s N=%d | %s" % (label, N, " | ".join(out)), flush=True)
hexp = C.CARD_PATS["C1"][0]
ph1 = dict(model="phase", tau=0.01)
M = {
 "null": lambda: [row("null phase tau %g" % t, 4600 + i, layout=dict(model="phase", tau=t)) for i, t in enumerate((0.0, 0.01, 0.02))],
 "nullw": lambda: [row("null phase tau %g + 5%% win" % t, 4610 + i, win=0.95, layout=dict(model="phase", tau=t)) for i, t in enumerate((0.01, 0.02))],
 "perrow": lambda: [row("per-ROW sigma x%g on %d%% of arm cells, phase 1%%" % (s, p), 4620 + i, win=0.95, layout=ph1,
                        tscale=(lambda s, p: lambda key: s if hsh("row", key) % 100 < p else 1.0)(s, p))
                    for i, (s, p) in enumerate(((3.0, 5), (2.0, 20), (4.0, 2)))],
 "perrow_t5": lambda: [row("per-ROW x3 on 5%% + t(5), phase 1%%", 4630, win=0.95, layout=ph1, noise="t5",
                        tscale=lambda key: 3.0 if hsh("row", key) % 100 < 5 else 1.0)],
 "var": lambda: [row("variant-0 extra noise %s s=%g (heads)" % ("t(%d)" % nu if nu else "normal", s), 4640 + i, win=0.95,
                     layout=dict(model="x_phase_noisyvar", tau=0.01, s=s, nu=nu)) for i, (s, nu) in enumerate(((0.01, 0), (0.015, 0), (0.01, 3)))],
 "varall": lambda: [row("variant-0 extra noise t(3) s=0.01, ALL texts", 4650, win=0.95, layout=dict(model="x_phase_noisyvar", tau=0.01, s=0.01, nu=3, all=1))],
 "onerow1": lambda: [row("interaction ONE row (%s hit-dense) tau %g" % (hexp, t), 4660 + i, layout=dict(model="x_onerow", tau=t, pat=hexp, rg="hit-dense"))
                     for i, t in enumerate((0.03, 0.05, 0.10))],
 "onerowall": lambda: [row("interaction one row per head text (regime hashed) tau %g" % t, 4670 + i, layout=dict(model="x_onerow", tau=t))
                       for i, t in enumerate((0.02, 0.03, 0.05))],
 "onereg": lambda: [row("onereg hit-dense all heads tau %g" % t, 4680 + i, layout=dict(model="onereg", tau=t, rg="hit-dense"))
                    for i, t in enumerate((0.02, 0.03, 0.05))],
 "onerowpow": lambda: [row("POWER one row per head text tau %g + 5%% win" % t, 4690 + i, win=0.95, layout=dict(model="x_onerow", tau=t))
                       for i, t in enumerate((0.005, 0.01))],
}

M["t5oos"] = lambda: [row("t(5) + phase 1%% + 5%% win, seed %d (oos)" % sd, sd, win=0.95, layout=ph1, noise="t5") for sd in (5101, 5102)]
M["pat2x"] = lambda: [row("one pattern (%s) head arms 2x sigma, phase 1%%, win" % p, 5110 + i, win=0.95, layout=ph1,
                          tscale=(lambda p: lambda key: 2.0 if key[1] == p and key[2] != "I" else 1.0)(p))
                      for i, p in enumerate([C.CARD_PATS["C1"][1], C.CARD_PATS["C2"][0]])]
M["mask"] = lambda: [row("onereg hd tau %g + per-ROW x3 on 5%%" % t, 5120 + i, layout=dict(model="onereg", tau=t, rg="hit-dense"),
                         tscale=lambda key: 3.0 if hsh("row", key) % 100 < 5 else 1.0) for i, t in enumerate((0.03, 0.05))]
M["maskt5"] = lambda: [row("onereg hd tau %g + t(5)" % t, 5130 + i, layout=dict(model="onereg", tau=t, rg="hit-dense"), noise="t5")
                       for i, t in enumerate((0.03, 0.05))]
M["regoos"] = lambda: [row("r44 A regime heads tau 3%%, seed %d (oos)" % sd, sd, arms=((True, True),), layout=dict(model="regime", tau=0.03, heads=True)) for sd in (5140, 5141, 5142)]
M[NAME]()
import statistics
if REC["read"]:
    d = REC["dfp"]
    print("  texts read/night median %s, excluded median %s; per-text pure-error df: min %d median %s, share<4 %.3f" % (
        statistics.median(REC["read"]), statistics.median(REC["excl"]), min(d), statistics.median(d), sum(x < 4 for x in d) / len(d)))
