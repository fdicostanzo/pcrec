# The rev-1 estimator/gates, implemented literally from span_cards rev 1 §3.4-§3.5 (lane s2rev1 drill)
def rhafz(n,d):
    s = -1 if (n<0)!=(d<0) else 1
    n,d=abs(n),abs(d); return s*((n + d//2)//d)
def isqrt_rn(N):
    import math
    r=math.isqrt(N); return r+1 if N-r*r>r else r
def med(v): s=sorted(v); return s[(len(s)-1)//2]
K_TRIM=1723000
def sp(v):
    m=med(v); k=max(range(len(v)), key=lambda i:(abs(v[i]-m), i))
    w=[v[i] for i in range(len(v)) if i!=k]; n=len(w)
    Q=n*sum(x*x for x in w)-sum(w)**2
    return rhafz(K_TRIM*Q, 10**6*n*(n-1))   # sp^2
def noise(v, vb):
    aa=med([abs(vb[i]-v[i]) for i in range(len(v))])
    return aa, isqrt_rn(aa*aa+sp(v))
def gate(val, nz, g=30000): return val>0 and nz*10**6 <= g*val
def show(name, v, vb, g=30000):
    val=med(v); aa,nz=noise(v,vb)
    print("%-22s value %d aa %d noise %d (%.3f%%) gate %s"%(name,val,aa,nz,100*nz/val,gate(val,nz,g)))
base=[59900,59950,60000,60000,60050,60100,60020]
tw=[x+60 for x in base]
show("clean", base, tw)
o=list(base); o[5]=64800; show("one outlier +8%", o, [x+60 for x in o])
b=[60000,63000,60000,63000,60000,63000,60000]; show("bimodal 4/3 (5%)", b,[x+60 for x in b])
show("A/A 1% > spread", base, [x+600 for x in base])
show("A/A 3.3% > gate", base, [x+2000 for x in base])
# delta NULL rule: per-call D_l (ns_e6), base c, aa_D, FRG
def null(D, cbase, aaD, FRG):
    m=med(D); floor=max(aaD, rhafz(FRG*cbase,10**6))
    return not (all(d>0 for d in D) and m>floor), m, floor
for name,D in [("verify~0 (signs mix)",[1500,-2000,3000,500,-500,2500,1000]),
               ("verify<0 consistent",[-30000,-29000,-31000,-30500,-29500,-30200,-30100]),
               ("verify 40ns/cmp clean",[4.0e7,4.1e7,3.9e7,4.0e7,4.05e7,3.95e7,4.02e7])]:
    D=[int(x) for x in D]
    print("%-22s NULL %s med %d floor %d"%((name,)+null(D, 2_000_000_000, 400000, 3000)))
# unit bimodal
def bimodal(u, g=15000):
    s=sorted(u); U=med(u)
    return any(rhafz((s[k]-s[k-1])*10**6, U) > g for k in range(2,6))
print("unit clean bimodal", bimodal([189200,189150,189300,189250,189180,189220,189400]))
print("unit 4/3 3% bimodal", bimodal([189200,195000,189150,195100,189300,194900,189250]))
print("unit one outlier bimodal", bimodal([189200,189150,189300,189250,189180,189220,205000]))
# drift per job
def rel(v):
    M=med(v); return [rhafz(x*10**6, M) for x in v]
def drift(U, C, g=15000):
    Um, Cm = med(U), med(C); d=rhafz(abs(Cm-Um)*10**6, Um)
    T=max(g, 3*isqrt_rn(sp(rel(U))+sp(rel(C))))
    return d, T, d>T
U=[189200,189150,189300,189250,189180,189220,189400]
print("drift none", drift(U,[x+50 for x in U]))
print("drift 3% tight", drift(U,[int(x*1.03) for x in U]))
W=[189200,191000,187500,190500,188000,192000,186800]
print("drift 2% wide spread", drift(W,[int(x*1.02) for x in W]))
