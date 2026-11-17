import sys; sys.path.insert(0, '.')
from ev import *
Y = Pat(r"(?:(?<h>\d)?;)*")
p = Prog(Y, ('c', none(test('h', comp(S('<', 10)), 'x'))))
for x in ['', ';', '7;', '7;;']: print(repr(x), fmt(*p.both(x)))
