import sys, random
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms9/work")
import cards as C
which = sys.argv[1]
def go(pt, seed, win, **kw):
    old = C._flags(INTER_PE_PER_TEXT=pt)
    try:
        rng = random.Random(seed); hit = fl = 0; flh = 0; fltexts = {}
        for _ in range(C.NOISE_TRIALS):
            v = C.synth_night(rng, 0.01, cellwins=C.power_cells(8, "hit-dense", win), **kw)
            f = v.get("inter_flagged", 0) > 0
            hit += v["hstar"] == 8; fl += f
        return hit, fl
    finally:
        C._flags(**old)
if which == "loser":
    lose = dict(model="loser", tau=0.04, arms={"h1"})
    for pt in (True, False):
        print("loser seed 3440 pt=%s: h*=8 %d, nights flagged %d" % ((pt,) + go(pt, 3440, 0.95, layout=lose, wins={1: 1.20})), flush=True)
else:
    for pt in (True, False):
        print("phase tau 2%% 10%% win seed 3412 pt=%s: h*=8 %d, nights flagged %d" % ((pt,) + go(pt, 3412, 0.90, layout=dict(model="phase", tau=0.02))), flush=True)
