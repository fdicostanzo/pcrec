import sys; sys.path.insert(0, '.')
from ev import *
t2 = Pat(r"(?<h>\d{1,2})(?::(?<m>\d\d))?")
Sh = S('<', 9); Tm = S('<', 30)
jointP = joint(['h', 'm'], {}, lambda h, m: Sh(h) and Tm(m))          # ((h, m): (<9, <30))
recP = AND(test('h', Sh), test('m', Tm))                               # (h: <9, m: <30)
for nm, (a, b) in {'plain': (jointP, recP), 'NOT': (NOT(jointP), NOT(recP))}.items():
    pa, pb = Prog(t2, ('c', a)), Prog(t2, ('c', b))
    for mode in ('W', 'S'):
        f = (lambda p, x: p.whole(x)) if mode == 'W' else (lambda p, x: p.search(x) is not None)
        d = [x for x in T2POOL if f(pa, x) != f(pb, x)]
        print('L83', nm, mode, 'differ', len(d), 'of', len(T2POOL), d[:3])
    for x in ['10', '9', '5:45']:
        print('   ', nm, repr(x), 'joint', fmt(*pa.both(x)), '| record', fmt(*pb.both(x)))
# repeated-label version (closing-example list)
L = Pat(r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*")
for x in ['12,', '3,']:
    print('L83 list NOT', repr(x), 'joint', fmt(*Prog(L, ('c', NOT(jointP))).both(x)), '| record', fmt(*Prog(L, ('c', NOT(recP))).both(x)))
