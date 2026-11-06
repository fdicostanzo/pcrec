# span_cards rev 1 §3.6 drill (lane s2rev1): J1's pre-registered sweep rule under no effect and under a true
# effect of one width on every cell. Units: launch effect and within-launch noise unit normal. python3 -I j1_drill.py
import math, random
random.seed(3)
def med(v): s=sorted(v); return s[(len(s)-1)//2]
def trsd(v):
    m=med(v); idx=max(range(len(v)), key=lambda i:(abs(v[i]-m), i)); w=[v[i] for i in range(len(v)) if i!=idx]
    mu=sum(w)/len(w); return math.sqrt(1.723*sum((x-mu)**2 for x in w)/(len(w)-1))
def j1(eff, trials=5000):
  out={'a':0,'b':0,'c':0}
  for _ in range(trials):
    beats=[0]*4; loses=[0]*4; anyb=False
    for c in range(8):
      lau=[random.gauss(0,1) for _ in range(7)]
      t128=[lau[l]+random.gauss(0,1) for l in range(7)]
      tb=[lau[l]+random.gauss(0,1) for l in range(7)]
      aa=med([abs(tb[l]-t128[l]) for l in range(7)])
      for w in range(4):
        tw=[lau[l]+random.gauss(0,1)-(eff if w==1 else 0) for l in range(7)]
        d=[tw[l]-t128[l] for l in range(7)]
        m=med(d); nz=math.sqrt(aa*aa+trsd(d)**2)
        if all(x<0 for x in d) and abs(m)>2*nz: beats[w]+=1; anyb=True
        if all(x>0 for x in d) and abs(m)>2*nz: loses[w]+=1
    if any(beats[w]>=5 and loses[w]==0 for w in range(4)): out['b']+=1
    elif not anyb: out['a']+=1
    else: out['c']+=1
  return {k:round(v/trials,4) for k,v in out.items()}
print("effect 0 x within-sd (20,000):", j1(0, 20000))
for e in (2,3,4,6): print("effect",e,"x within-sd:", j1(e))
