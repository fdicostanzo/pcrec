import sys,re; sys.path.insert(0,'/var/tmp/pcrec-pcrec/scratch/crit-predspec22/simulate/w')
from eng import Prog
P=r'(?P<h>\d)?-(?:(?P<k>\d)|-(?P<j>\d))'
D='0123456789'
pop=[h+'-'+x for h in ['']+list(D) for x in list(D)+['-'+d for d in D]]
assert all(re.fullmatch(P,t) for t in pop)
G={t:re.fullmatch(P,t).groupdict() for t in pop}
joint=('c',{'h':'mark','k':'plain'},lambda v:int(v['h'])<int(v['k']))
jc=('c',{'j':'mark'},lambda v:int(v['j'])<3)
text=Prog(P,pop,[joint,jc])
# script mirror: predspec22 `fin` order: k None -> False before any DOM is consulted; consulted -> transparent
class Consult(Exception): pass
def fin(s,Dm):
    g=G[s]
    if g['k'] is None: return False
    hs=[g['h']] if g['h'] is not None else Dm['h']
    return any(int(x)<int(g['k']) for x in hs)
def fj(s,Dm):
    g=G[s]; return int(g['j'])<3 if g['j'] is not None else any(int(d)<3 for d in Dm['j'])
class Poison:
    def __iter__(self): raise Consult()
def dom(lab):
    out=set()
    for s in pop:
        if G[s][lab] is None: continue
        ok=True
        for f in (fin,fj):
            try: r=f(s,{'h':Poison(),'j':Poison()})
            except Consult: r=True
            if not r: ok=False; break
        if ok: out.add(G[s][lab])
    return out
Dm={'h':dom('h'),'j':dom('j')}
scr={s:fin(s,Dm) and fj(s,Dm) for s in pop}
d=[s for s in pop if scr[s]!=text.holds(s)]
print(len(pop),'subjects; text (whole condition transparent where h absent): DOM(j)',sorted(text.dom('j')),'| script-coded order: DOM(j)',sorted(Dm['j']),'| differ',len(d),d[:4])
