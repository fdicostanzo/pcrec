# HAND-BUILT SIMULATION (manager, 2026-11-21): byte reads to find the FIRST run of k bytes all in set S.
import itertools, random
def naive(t,k):            # check forward from each start, restart one byte later
    r=0
    for i in range(len(t)-k+1):
        for j in range(k):
            r+=1
            if not t[i+j]: break
        else: return i,r
    return -1,r
def fwd_skip(t,k):         # check forward; on a miss at p, next start is p+1
    r=0; i=0
    while i+k<=len(t):
        for j in range(k):
            r+=1
            if not t[i+j]: i=i+j+1; break
        else: return i,r
    return -1,r
def back_skip(t,k):        # Frank's: look at the LAST position first, verify backward; on a miss at p, next start p+1
    r=0; i=0
    while i+k<=len(t):
        for j in range(k-1,-1,-1):
            r+=1
            if not t[i+j]: i=i+j+1; break
        else: return i,r
    return -1,r
def first(t,k):
    for i in range(len(t)-k+1):
        if all(t[i:i+k]): return i
    return -1
k=32
near=([1]*31+[0])*1000            # 31 hex digits then a 'g', repeated
for name,t in [("near-miss 31+g",near),("g then 31 hex",([0]+[1]*31)*1000),("random 90% hex",[random.random()<.9 for _ in range(32000)]),("all hex (hit at 0)",[1]*32000)]:
    n=len(t); out=[]
    for f in (naive,fwd_skip,back_skip):
        p,r=f(t,k); assert p==first(t,k), (name,f.__name__)
        out.append(f"{f.__name__} {r/n:.3f}")
    print(f"{name:22s} reads per text byte: "+", ".join(out))
# exhaustive worst case for small k: every binary text of length 16
for kk in (3,4,5):
    worst={f.__name__:0 for f in (naive,fwd_skip,back_skip)}
    for bits in itertools.product([0,1],repeat=16):
        t=list(bits); p0=first(t,kk)
        for f in (naive,fwd_skip,back_skip):
            p,r=f(t,kk); assert p==p0
            worst[f.__name__]=max(worst[f.__name__],r/16)
    print(f"k={kk} worst reads/byte over all 65,536 texts of 16: "+", ".join(f"{a} {b:.2f}" for a,b in worst.items()))
