import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate')
from ev import *
exec(open('/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate/run4.py').read().split("late = J")[0].split('from ev import *')[1])
P = T2P[::7]
for nm, p in [('t2 & NOT (h: <0)', And(t2, CNot(C('h', lt(0))))), ('t2 & (h: !<0)', And(t2, C('h', NOTS(lt(0))))),
              ('t2 & NOT (h: <0, m: <30)', And(t2, CNot(Rec(C('h', lt(0)), C('m', lt(30))))))]:
    print(nm, 'vs t2', diff(p, t2, P, True), len(P))
