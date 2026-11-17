import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate')
from ev import *
A = Rx(Seq(Grp('l', L('a')), L('a'))); Bp = Rx(Grp('l', S('a', 'a')))
d = C('l', lambda v: v == 'a'); c = C('l', lambda v: v == 'zz')
p0 = And(Or(Bp, A), d); p1 = And(Or(And(Bp, c), A), d)
for t in ['aa', 'xaa']: print(t, both(p0, t), '|', both(p1, t))
# without any label trick: KH-style, the when body: adding c to branch 1 of x | x&... 
# a label-free version: (P | Q) & F where adding a condition in P's branch admits Q's labels -> only labels matter, so a condition outside is required
