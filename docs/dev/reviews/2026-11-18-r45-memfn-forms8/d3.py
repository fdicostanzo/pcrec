import sys, random
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms8/work")
import cards as C
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
def run(name, flags, win=None, seed=1300, **kw):
    old = C._flags(**flags)
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
        C._flags(**old)
    print("%-50s %s win=%s: flagged %3d/%d, h*=8 %3d, P(h*!=64) %.3f" % (name, flags, win, flag, N, hit, off / N), flush=True)
# B at the regime grouping: a head's layout in ONE regime (onereg) and the per-(text,regime) model, void OFF so B alone decides
for model in (dict(model="onereg", tau=0.03, rg="hit-dense"), dict(model="regime", tau=0.02, heads=True), dict(model="onereg", tau=0.04, rg="random")):
    for phf in (True, False):
        run("B grouping %s" % model, dict(INTERACTION_VOID=False, PER_HEAD_FLOOR=phf), layout=model)
