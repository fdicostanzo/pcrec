import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate')
from ev import *
exec(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate/run4.py').read().split("late = J")[0].split('from ev import *')[1])
T30v = lambda v: v.isdigit() and int(v) < 30
for nm, Tm in [('canon <30', lt(30)), ('value <30 (engine)', T30v)]:
    jt = And(t2, CNot(J(('h','m'), prod(lt(9), Tm)))); rc = And(t2, CNot(Rec(C('h', lt(9)), C('m', Tm))))
    print(nm, diff(jt, rc, T2P))
# late under document DICT-DOMAIN vs value
lateC = J(('h','m'), tup_ge(9, 30))
qC = And(t2, lateC)
print('t2 & !q canonical late: W/S', cnt(And(t2, Comp(qC)), T2P))
