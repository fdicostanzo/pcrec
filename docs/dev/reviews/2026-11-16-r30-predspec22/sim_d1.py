import sys; sys.path.insert(0,'/var/tmp/pcrec-pcrec/scratch/crit-predspec22/simulate/w')
from eng import Prog
P=r'(?P<h>\d)?x'; pop=['x']+[d+'x' for d in '0123456789']
lt=lambda n:(lambda v:int(v['h'])<n)
q=Prog(P,pop,[('c',{'h':'plain'},lt(5))])
a=Prog(P,pop,[('not',q),('c',{'h':'mark'},lt(3))])
b=Prog(P,pop,[('c',{'h':'mark'},lt(3))])
print('P & !q & (h?: <3): DOM', sorted(a.dom('h')), 'on x', a.holds('x'), '| P & (h?: <3): DOM', sorted(b.dom('h')),'on x', b.holds('x'))
# marked q: q := P & (h?: <5), program P & !q & (h?: >7)
qm=Prog(P,pop,[('c',{'h':'mark'},lt(5))])
c=Prog(P,pop,[('not',qm),('c',{'h':'mark'},lambda v:int(v['h'])>7)])
print('P & !qm & (h?: >7) on x', c.holds('x'), 'DOM', sorted(c.dom('h')))
