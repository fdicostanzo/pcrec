# the check scripts' THE RULE (predspec21_check.py doms(var="MANAGER")): a condition is evaluated with a POISON DOM and
# is TRANSPARENT only if it actually CONSULTS a DOM; mirror it for the joint ((h?, k): (<5, <5)) written two ways
import re
P=r'(?P<h>\d)?-(?P<k>\d)(?:(?<=[5-9])-(?P<j>\d))?'
D='0123456789'
pop=[h+'-'+k+j for h in ['']+list(D) for k in D for j in ['']+(['-'+x for x in D] if k>='5' else [])]
G={t:re.fullmatch(P,t).groupdict() for t in pop}
class Consult(Exception): pass
class Poison:
    def __iter__(self): raise Consult()
def mk(v,S,dom): return S(v) if v is not None else any(S(d) for d in dom)
def joint_hfirst(s,Dm): g=G[s]; return mk(g['h'],lambda x:int(x)<5,Dm['h']) and g['k'] is not None and int(g['k'])<5
def joint_kfirst(s,Dm): g=G[s]; return g['k'] is not None and int(g['k'])<5 and mk(g['h'],lambda x:int(x)<5,Dm['h'])
def jcond(s,Dm): return mk(G[s]['j'],lambda x:int(x)<3,Dm['j'])
def dom(facs,lab):
    out=set()
    for s in pop:
        if G[s][lab] is None: continue
        ok=True
        for f in facs:
            try: r=f(s,{'h':Poison(),'j':Poison()})
            except Consult: r=True
            if not r: ok=False;break
        if ok: out.add(G[s][lab])
    return out
for name,jf in [('h first',joint_hfirst),('k first',joint_kfirst)]:
    facs=[jf,jcond]; Dm={'h':dom(facs,'h'),'j':dom(facs,'j')}
    print('script-style THE RULE, joint written',name,': DOM(j)',sorted(Dm['j']),'; `-1` holds:',all(f('-1',Dm) for f in facs))
