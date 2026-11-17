import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate')
from ev import *
SV = Rx(Seq(Rep(Grp('h', D()), 0, 1), L('x'))); REP = Rx(Rep(Seq(Rep(Grp('h', D()), 0, 1), L(';')), 0, None))
SVP = list(texts('37x ', 4)); REPP = list(texts('37;', 5))
for nm, P, pool, d in [('SV', SV, SVP, '9'), ('REP', REP, REPP, 'x')]:
    a = And(P, Comp(And(P, C('h', lt(5), d)))); b = And(P, Comp(And(P, C('h', lt(5)))))
    print(nm, 'pattern complement P & !(P & (h = %s: <5)) vs without default' % d, diff(a, b, pool, True))
    a = And(P, C('h', NOTS(lt(5)), '3')); b = And(P, C('h', NOTS(lt(5))))
    print(nm, 'set complement (h = 3: !<5) vs (h: !<5)', diff(a, b, pool, True))
    a = And(P, CNot(CNot(C('h', lt(5), d)))); b = And(P, CNot(CNot(C('h', lt(5)))))
    print(nm, 'NOT NOT (h = d: <5) vs NOT NOT (h: <5)', diff(a, b, pool, True))
