# The lane's MANAGER machinery copied VERBATIM from evidence/predspec21_check.py (Fac, Consult, _Poison, no_dom,
# doms MANAGER branch), driven on RULING-2 / RULING-7 / SIMULATE-9 pools (Python re, (?J) emulated by 2 group names).
import re
class Fac:
    def __init__(self, names, fn, marks=None, negmark=False):
        self.names = frozenset(names); self.marks = frozenset(names[:1] if marks is None else marks)
        self.fn = fn; self.negmark = negmark
class Consult(Exception): pass
class _Poison:
    def __iter__(self): raise Consult()
class _PoisonDom(dict):
    def __getitem__(self, k): return _Poison()
POISON = _PoisonDom()
def no_dom(f, s, transparent):
    try: return f.fn(s, POISON)
    except Consult:
        if transparent: return True
        raise
def mk(v, S, dom): return S(v) if v is not None else any(S(d) for d in dom)
def doms_manager(pop, labels, vals, facs):
    return {h: {v for s in pop if vals(s, h) and all(no_dom(f, s, True) for f in facs) for v in vals(s, h)} for h in labels}
D='0123456789'
def mkpop(rx, pop):
    M={}
    for s in pop:
        m=rx.fullmatch(s)
        if m:
            g=m.groupdict(); M[s]={x:(g.get(x) or g.get(x+'2')) for x in 'hkj'}
    return M
def answer(M, facs):
    vals=lambda s,h: [M[s][h]] if M[s][h] is not None else []
    Dm=doms_manager(list(M), 'hkj', vals, facs)
    return Dm,{s: all(f.fn(s,Dm) for f in facs) for s in M}
lt=lambda n:(lambda v:int(v)<n)
def rep(tag,M1,M2,f1,f2,pop):
    D1,a1=answer(M1,f1(M1)); D2,a2=answer(M2,f2(M2))
    d=[s for s in pop if a1.get(s,False)!=a2.get(s,False)]
    print(tag,'DOM(j)',sorted(D1['j']),'vs',sorted(D2['j']),'| differ',len(d),'of',len(pop),sorted(d,key=lambda s:(len(s),s))[:3])
# ---- RULING-2
pop=sorted({h+'-'+k+t for h in ['']+list(D) for k in D for t in ['']+['+'+j for j in D]})
P=re.compile(r'(?P<h>\d)?-(?P<k>[1-9])(?:\+(?P<j>[5-9]))?|-(?P<k2>0)\+(?P<j2>[0-4])')
Q=re.compile(r'(?P<h>\d)?-(?P<k>[1-9])(?:\+(?P<j>[5-9]))?')
def r2(M):
    C1=Fac(['h','k'], lambda s,Dm: M[s]['k'] is not None and mk(M[s]['h'], lambda v:int(v)<int(M[s]['k']), Dm['h']))
    C2=Fac(['j'], lambda s,Dm: mk(M[s]['j'], lt(5), Dm['j']))
    return [C1,C2]
MP,MQ=mkpop(P,pop),mkpop(Q,pop)
# base equal behaviour check
_,bp=answer(MP,r2(MP)[:1]); _,bq=answer(MQ,r2(MQ)[:1])
print('RULING-2 base P&C1 == Q&C1 (accepted subjects+labels):', {s:tuple(MP[s].items()) for s in MP if bp[s]}=={s:tuple(MQ[s].items()) for s in MQ if bq[s]}, sum(bp.values()))
rep('RULING-2 MANAGER P&C1&C2 vs Q&C1&C2:',MP,MQ,r2,r2,pop)
# ---- RULING-7: product joint vs record=& (entries split), third marked label j
pop7=sorted({h+'-'+k+t for h in ['']+list(D) for k in D for t in ['']+['+'+j for j in D]})
P7=re.compile(r'(?P<h>\d)?-(?P<k>[0-4])(?:\+(?P<j>[5-9]))?|-(?P<k2>[5-9])\+(?P<j2>[0-4])')
M7=mkpop(P7,pop7)
J=lambda s,Dm,M: mk(M[s]['j'], lt(5), Dm['j'])
jointA=lambda M:[Fac(['h','k'],lambda s,Dm: mk(M[s]['h'],lt(5),Dm['h']) and int(M[s]['k'])<5), Fac(['j'],lambda s,Dm:J(s,Dm,M))]
jointB=lambda M:[Fac(['h','k'],lambda s,Dm: int(M[s]['k'])<5 and mk(M[s]['h'],lt(5),Dm['h'])), Fac(['j'],lambda s,Dm:J(s,Dm,M))]
record=lambda M:[Fac(['h'],lambda s,Dm: mk(M[s]['h'],lt(5),Dm['h'])), Fac(['k'],lambda s,Dm:int(M[s]['k'])<5), Fac(['j'],lambda s,Dm:J(s,Dm,M))]
print('RULING-7 subjects',len(M7))
rep('RULING-7 joint coded (h-test first) vs record=&:',M7,M7,jointA,record,sorted(M7))
rep('RULING-7 joint coded (k-test first) vs record=&:',M7,M7,jointB,record,sorted(M7))
rep('SIMULATE-9 same joint, two fn orders:',M7,M7,jointA,jointB,sorted(M7))
