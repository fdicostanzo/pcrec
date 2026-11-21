import sys, random, time
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-memfn-forms9/work")
import cards as C
rng = random.Random(1)
t=time.time()
v = C.synth_night(rng, 0.01, layout=dict(model="phase", tau=0.01))
print(time.time()-t, v.get("inter_flagged"), v["hstar"])
