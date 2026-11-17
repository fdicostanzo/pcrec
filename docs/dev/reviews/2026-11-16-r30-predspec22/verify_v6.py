# own engine: P=/(?:(?<h>\d)(?::(?<m>\d))?,)*/, c=((h, m?): m < h); some(c) / occurs.none(c); three DOM-time readings
import itertools
items=[(h,m) for h in (1,6) for m in (None,0,7)]
L=[l for n in range(3) for l in itertools.product(items,repeat=n)]
R=lambda h,m: m<h
def dom(gq, mode):
    D=set()
    for l in L:
        if mode=='pass':      # lane's pv: a pass whose test would consult a DOM is skipped
            t=[R(h,m) for h,m in l if m is not None]
        elif mode=='match':   # whole condition transparent if any pass has m absent
            if any(m is None for h,m in l): D|={m for h,m in l if m is not None}; continue
            t=[R(h,m) for h,m in l]
        else:                 # 'regex': absent m ranges over the regex's values {0,7}
            t=[R(h,m) if m is not None else any(R(h,v) for v in (0,7)) for h,m in l]
        ok = any(t) if gq=='some' else not any(t)
        if ok: D|={m for h,m in l if m is not None}
    return D
def ans(gq,D,l):
    t=[R(h,m) if m is not None else any(R(h,v) for v in D) for h,m in l]
    return any(t) if gq=='some' else not any(t)
for mode in ('pass','match','regex'):
    Ds,Dn=dom('some',mode),dom('none',mode)
    both=[l for l in L if ans('some',Ds,l) and ans('none',Dn,l)]
    print(mode,'DOM(m) some',sorted(Ds),'none',sorted(Dn),'| both hold on',len(both),'of',len(L), both[:2])
