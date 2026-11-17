import sys,itertools; sys.path.insert(0,'/var/tmp/pcrec-pcrec/scratch/crit-predspec22/simulate/w')
from eng import Prog
import re
P=r'(?P<h>\d)?-(?P<k>\d)(?:(?<=[5-9])-(?P<j>\d))?'
D='0123456789'
pop=[h+'-'+k+j for h in ['']+list(D) for k in D for j in ['']+(['-'+x for x in D] if k>='5' else [])]
pop=[t for t in pop if re.fullmatch(P,t)]
lt=lambda l,n:(lambda v:int(v[l])<n)
amp=[('c',{'h':'mark'},lt('h',5)),('c',{'k':'plain'},lt('k',5))]
joint=[('c',{'h':'mark','k':'plain'},lambda v:int(v['h'])<5 and int(v['k'])<5)]
jc=('c',{'j':'mark'},lt('j',3))
a=Prog(P,pop,amp+[jc]); b=Prog(P,pop,joint+[jc])
d=[t for t in pop if a.holds(t)!=b.holds(t)]
print(len(pop),'subjects; `(h?: <5) & (k: <5) & (j?: <3)` vs `((h?, k): (<5, <5)) & (j?: <3)`: differ',len(d),d[:4],'DOM(j)',sorted(a.dom('j')),sorted(b.dom('j')))
qa=Prog(P,pop,amp+[jc]); qb=Prog(P,pop,joint+[jc])
na=Prog(P,pop,[('not',qa)]); nb=Prog(P,pop,[('not',qb)])
d2=[t for t in pop if na.holds(t)!=nb.holds(t)]
print('inside q: P & !q, the same two spellings: differ',len(d2),d2[:4])
