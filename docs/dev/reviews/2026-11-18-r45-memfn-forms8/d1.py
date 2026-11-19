import sys, random, statistics
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms8/work")
import cards as C
print(C.CARD_PATS, C.REGIMES, C.GRID, flush=True)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 100
def run(name, tscale=None, iv=True, win=0.95, seed=900, **kw):
    C.TSCALE = tscale
    old = C._flags(INTERACTION_VOID=iv)
    try:
        rng = random.Random(seed)
        hit = flag = off = 0
        for _ in range(N):
            cw = C.power_cells(8, "hit-dense", win) if win else None
            v = C.synth_night(rng, 0.01, cellwins=cw, **kw)
            flag += v.get("inter_flagged", 0) > 0
            hit += v["hstar"] == 8
            off += v["hstar"] != 64
    finally:
        C._flags(**old); C.TSCALE = None
    print("%-60s void=%s win=%s: nights flagged %d/%d, h*=8 %d, h*!=64 %d" % (name, iv, win, flag, N, hit, off), flush=True)
ph1 = dict(model="phase", tau=0.01)
for iv in (True, False):
    run("baseline phase 1%", layout=ph1, iv=iv)
    run("hex? one pattern's head arms 2x sigma", tscale=lambda k: 2.0 if k[1] == C.CARD_PATS["C1"][0] and k[2] != "I" else 1.0, layout=ph1, iv=iv)
    run("every head arm 1.5x sigma (I, aa at 1x)", tscale=lambda k: 1.5 if k[2].startswith("h") else 1.0, layout=ph1, iv=iv)
    run("A/A 0.7x", layout=ph1, aascale=0.7, iv=iv)
    run("t5 launches", layout=ph1, noise="t5", iv=iv)
    run("one regime 3x (not-warm)", layout=ph1, rscale={"not-warm": 3.0}, iv=iv)
