import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate')
from ev import *
exec(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate/run2.py').read().split("p = C('k'")[0].split('from ev import *')[1])
p = C('k', between(3, 7))
for c in [C('h', lt(5)), C('h', lt(5), '0')]:
    q = And(KH, c); body = Or(And(KH, c, p), And(KH, Comp(q)))
    a = And(KH, body); b = And(KH, When(c, p))
    print(sum(W(a,t)!=W(b,t) or Sr(a,t)!=Sr(b,t) for t in KHP))
