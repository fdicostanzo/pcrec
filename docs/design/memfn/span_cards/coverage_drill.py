# span_cards rev 1 §6 drill (lane s2rev1): the one-card equal-price departure rate of the band z x noise,
# noise by §3.4 (7 launches, trim the farthest, consistency factor), against a new run's draw. python3 -I coverage_drill.py
import math, random
random.seed(7)
def med(v): s=sorted(v); return s[(len(s)-1)//2]
def trsd(v):
    m=med(v); idx=max(range(len(v)), key=lambda i:(abs(v[i]-m), i)); w=[v[i] for i in range(len(v)) if i!=idx]
    mu=sum(w)/len(w); return math.sqrt(sum((x-mu)**2 for x in w)/(len(w)-1))
N=200000; S=[];X=[]
for _ in range(N):
    v=[random.gauss(0,1) for _ in range(7)]
    S.append(trsd(v)); X.append(random.gauss(0,1)-med(v))
print("E[trsd]", sum(S)/N, "rms", math.sqrt(sum(s*s for s in S)/N))
c=math.sqrt(sum(s*s for s in S)/N)
for k in (1.0, 1/c):
  for z in (2.0,2.5,2.9,3.0,3.3,3.5):
    d=sum(1 for i in range(N) if X[i] > z*k*S[i])/N
    print("k%.3f z%.1f dep %.4f"%(k,z,d))
