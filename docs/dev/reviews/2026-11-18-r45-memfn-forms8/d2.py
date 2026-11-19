import sys, random
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms8/work")
import cards as C
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
def run(name, iv=True, win=None, seed=1200, **kw):
    old = C._flags(INTERACTION_VOID=iv)
    try:
        rng = random.Random(seed)
        hit = flag = off = vf = 0
        for _ in range(N):
            cw = C.power_cells(8, "hit-dense", win) if win else None
            v = C.synth_night(rng, 0.01, cellwins=cw, **kw)
            flag += v.get("inter_flagged", 0) > 0
            hit += v["hstar"] == 8
            off += v["hstar"] != 64
            vf += v["voided_first"] > 0
    finally:
        C._flags(**old)
    print("%-58s void=%-5s win=%s: flagged %3d/%d, first-void %3d, h*=8 %3d, P(h*!=64) %.3f" % (name, iv, win, flag, N, vf, hit, off / N), flush=True)
for tau in (0.02, 0.03, 0.05):
    for iv in (True, False):
        run("onereg hit-dense heads tau %g" % tau, iv=iv, layout=dict(model="onereg", tau=tau, rg="hit-dense"))
for tau, ti in ((0.02, 0.01), (0.03, 0.015), (0.03, 0.02)):
    for iv in (True, False):
        run("mix heads main %g x regime %g" % (tau, ti), iv=iv, layout=dict(model="mix", tau=tau, ti=ti))
for tau, ti in ((0.01, 0.005), (0.0, 0.005)):
    for iv in (True, False):
        run("POWER mix heads main %g x regime %g" % (tau, ti), iv=iv, win=0.95, layout=dict(model="mix", tau=tau, ti=ti))
