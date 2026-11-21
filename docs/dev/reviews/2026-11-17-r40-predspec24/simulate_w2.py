import sys; sys.path.insert(0, '.')
from cnt import *
U = seq(grp('b', rep(DIG, 1)), opt(grp('a', DIG)))
p1 = ANDc(U, NOT(T('a', lt(5)))); p2 = ANDc(U, T('a', comp(lt(5))))
print('E1 WHOLE holds-only', sum((whole(p1,t) is None) != (whole(p2,t) is None) for t in DSP), 'labels', sum(whole(p1,t) != whole(p2,t) for t in DSP))
c = cor(T('a', eq('1')), T('c', eq('1')))
l, r = ANDc(AND(P, Q), c), ANDc(AND(Q, P), c)
d = [t for t in DSP if whole(l,t) != whole(r,t)]
print('E5 WHOLE labels', len(d), d[:3], whole(l,'111'), whole(r,'111'))
