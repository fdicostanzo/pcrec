import sys,itertools; sys.path.insert(0,'/var/tmp/pcrec-pcrec/scratch/crit-predspec22/simulate/w')
from eng import Prog
A=r'a(?P<h>\d)|b(?P<k>\d)|c'; pop=['a'+d for d in '0123456789']+['b'+d for d in '0123456789']+['c']
q1=Prog(A,pop,[('c',{'h':'mark','k':'plain'},lambda v:int(v['h'])<int(v['k']))])
q2=Prog(A,pop,[('not',q1),('c',{'h':'mark'},lambda v:int(v['h'])>7)])
items=[('not',q2),('c',{'k':'mark'},lambda v:int(v['k'])<5),('c',{'h':'mark'},lambda v:int(v['h'])<5)]
res=set()
for perm in itertools.permutations(items):
    p=Prog(A,pop,list(perm)); res.add(tuple(p.holds(t) for t in pop))
p=Prog(A,pop,items)
print('q1 holds on',[t for t in pop if q1.holds(t)],'| q2 holds on',[t for t in pop if q2.holds(t)])
print('orders distinct answers',len(res),'| holds on',[t for t in pop if p.holds(t)],'| b1',p.holds('b1'), 'DOM h',sorted(p.dom('h')),'DOM k',sorted(p.dom('k')))
