import sys; sys.path.insert(0,'/var/tmp/pcrec-pcrec/scratch/crit-predspec22/simulate/w')
from eng import Prog
P=r'(?P<h>\d)?x'; pop=['x']+[d+'x' for d in '0123456789']
q=Prog(P,pop,[('c',{'h':'plain'},lambda v:int(v['h'])<5)])
q2=Prog(P,pop,[('c',{'h':'plain'},lambda v:int(v['h'])<5),('c',{'h':'plain'},lambda v:int(v['h'])<3)])
a=Prog(P,pop,[('not',q)]); b=Prog(P,pop,[('not',q2)])
print('FAIL->HOLD adding (h: <3) inside q:',[t for t in pop if not a.holds(t) and b.holds(t)])
