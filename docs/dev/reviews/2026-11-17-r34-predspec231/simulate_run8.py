import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate')
from ev import *
A = Rx(Seq(Grp('l', L('a')), L('a'))); Bp = Rx(Grp('l', S('a', 'a')))
c = C('l', lambda v: v == 'a')
BA = Rx(Alt(Grp('l', S('a','a')), Seq(Grp('l', L('a')), L('a'))))   # /(?<l>aa)|(?<l>a)a/ one regex
out = And(BA, c); out2 = And(Or(Bp, A), c); dist = Or(And(Bp, c), And(A, c))
for t in ['aa', 'xaa', 'aaa']:
    print(t, 'outside(one regex)', both(out, t), '| outside(program |)', both(out2, t), '| distributed', both(dist, t))
pool = list(texts('ab', 4))
print('differ (B|A)&c vs (B&c)|(A&c)', diff(out2, dist, pool, True))
