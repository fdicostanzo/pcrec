import sys,itertools; sys.path.insert(0,'/var/tmp/pcrec-pcrec/scratch/crit-predspec22/simulate/w')
from eng import Prog
pop=['x']+[d+'x' for d in '0123456789']+['ax','bx']
sp={'plain':r'(?P<h>[0-4])?x','lookbehind':r'(?:(?P<h>\d)(?<=[0-4]))?x','dead':r'(?P<h>[0-4]|a(?!x)x)?x','setc':None}
S=[('<3',lambda v:int(v['h'])<3),('>=3',lambda v:int(v['h'])>=3),('<9',lambda v:int(v['h'])<9)]
n=0;bad=[]
for (sn,sf),(tn,tf) in itertools.product(S,S):
    for mk in ['plain','mark']:
        ans=set()
        for name,rx in sp.items():
            if rx is None: continue
            q=Prog(rx,pop,[('c',{'h':mk},sf)])
            prog=Prog(rx,pop,[('not',q),('c',{'h':'mark'},tf)])
            ans.add((tuple(q.holds(t) for t in pop),tuple(prog.holds(t) for t in pop)))
            n+=len(pop)
        if len(ans)!=1: bad.append((sn,tn,mk))
print('three spellings of one P (plain / lookbehind-restricted / dead branch), q and P & !q & (h?: T):',n,'cases; splits',bad)
