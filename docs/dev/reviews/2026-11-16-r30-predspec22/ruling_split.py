# Own engine from rev 22 TEXT (§4.2 THE DOMAIN + WHICH CONDITIONS NARROW DOM): DOM(x) = x's values over matches where x
# is present that pass every UNMARKED condition and every MARKED condition whose marked label is PRESENT
# (a marked condition is TRANSPARENT where its marked label is absent). An absent marked label: some DOM value does (F1).
import re, itertools
D='0123456789'
P=re.compile(r'(?<h>\d)?-(?<k>[1-9])(?:\+(?<j>[5-9]))?|-(?<k2>0)\+(?<j2>[0-4])'.replace('(?<','(?P<'))
Q=re.compile(r'(?<h>\d)?-(?<k>[1-9])(?:\+(?<j>[5-9]))?'.replace('(?<','(?P<'))
pop=sorted({h+'-'+k+t for h in ['']+list(D) for k in D for t in ['']+['+'+j for j in D]})
def labs(rx,s):
    m=rx.fullmatch(s)
    if not m: return None
    g=m.groupdict()
    return {'h':g.get('h'),'k':g.get('k') or g.get('k2'),'j':g.get('j') or g.get('j2')}
# conditions: (marked label, fn(labels, DOM) -> bool)
def C1(L,Dm):   # ((h?, k): h < k)
    if L['k'] is None: return False
    xs=[L['h']] if L['h'] is not None else Dm['h']
    return any(int(x)<int(L['k']) for x in xs)
def C2(L,Dm):   # (j?: <5)
    xs=[L['j']] if L['j'] is not None else Dm['j']
    return any(int(x)<5 for x in xs)
conds=[('h',C1),('j',C2)]
def run(rx,conds):
    M={s:labs(rx,s) for s in pop}; M={s:L for s,L in M.items() if L}
    Dm={}
    for x in 'hkj':
        Dm[x]={L[x] for L in M.values() if L[x] is not None and
               all(c(L,None) for (mk,c) in conds if L.get(mk) is not None)}
    ans={s:all(c(L,Dm) for _,c in conds) for s,L in M.items()}
    return M,Dm,ans
for name,rx in (('P',P),('Q',Q)):
    # base program = rx & C1 (the program the condition C2 is added to)
    Mb,Db,ab=run(rx,[conds[0]])
    base={s:tuple(sorted((k,v) for k,v in Mb[s].items())) for s in Mb if ab[s]}
    M,Dm,a=run(rx,conds)
    print(name,'base matches',len(base),'DOM with C2',{k:''.join(sorted(v)) for k,v in Dm.items()},'on -5:',a.get('-5'))
    globals()['base_'+name]=base; globals()['ans_'+name]=a
print('base programs P&C1 and Q&C1 equal behaviour (same subjects, same labels):', base_P==base_Q)
d=[s for s in set(ans_P)|set(ans_Q) if ans_P.get(s,False)!=ans_Q.get(s,False)]
print('P&C1&C2 vs Q&C1&C2 differ on',len(d),'of',len(pop),'smallest',sorted(d,key=lambda s:(len(s),s))[:5])
# self-consistency: is DOM(j) witnessed only by matches the program rejects?
acc={s for s,v in ans_P.items() if v}
held={labs(P,s)['j'] for s in acc if labs(P,s)['j']}
print('P program: j values in ACCEPTED matches',sorted(held))
