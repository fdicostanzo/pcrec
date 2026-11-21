import sys, random
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms9/work")
import cards as C
rng = random.Random(5140)
for i in range(300):
    v = C.synth_night(rng, 0.01, layout=dict(model="regime", tau=0.03, heads=True))
    if v["hstar"] != 64:
        ls = [l for l in v.get("lines", []) if "R0" in l or "grid top" in l or "h = " in l][:3]
        print(i, v["hstar"], v.get("inter_flagged"), sorted(k for k in v.keys())[:40] if i < 0 else "", " || ".join(x[:220] for x in ls), flush=True)
