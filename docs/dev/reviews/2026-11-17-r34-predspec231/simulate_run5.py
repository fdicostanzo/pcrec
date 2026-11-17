import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate')
from ev import *
ITEMS = [h + (":" + m if m else "") + "," for h in ["3", "12"] for m in [None, "15", "45", "05", "99"]]
SUBO = [""] + ITEMS + [a + b for a in ITEMS for b in ITEMS] + [a + b + c for a in ITEMS for b in ITEMS for c in ITEMS]
LST = Rx(Rep(Seq(Grp('h', Rep(D(), 1, None)), Rep(Seq(L(':'), Grp('m', Seq(D(), D()))), 0, 1), L(',')), 0, None))
import re
def items(t): return re.findall(r'(\d+)(?::(\d\d))?,', t)
I1 = lambda t: all(m and int(h) < 10 and int(m) < 30 for h, m in items(t))
I2a = lambda t: all((not m) or (int(h) < 10 and int(m) < 30) for h, m in items(t))
I2b = lambda t: all(int(h) < 10 and ((not m) or int(m) < 30) for h, m in items(t))
R = prod(lt(10), lt(30)); NR = lambda h, m: not R(h, m)
cands = [('plain', J(('h','m'), R)), ('none !R', None_(J(('h','m'), NR))), ('none NOT joint', None_(CNot(J(('h','m'), R)))),
         ('none NOT record', None_(CNot(Rec(C('h', lt(10)), C('m', lt(30)))))),
         ('none m=99 !R', None_(J(('h','m'), NR, {'m': '99'}))), ('none m=00 !R', None_(J(('h','m'), NR, {'m': '00'}))),
         ('h=0,m=00 R', J(('h','m'), R, {'h': '0', 'm': '00'})), ('m=00 R', J(('h','m'), R, {'m': '00'}))]
for n, c in cands:
    p = And(LST, c); w = {t: W(p, t) for t in SUBO}
    d = [sum(w[t] != I(t) for t in SUBO) for I in (I1, I2a, I2b)]
    first = [next((t for t in SUBO if w[t] != I(t)), None) for I in (I1, I2a, I2b)]
    print(n, 'holdsW', sum(w.values()), 'diff I1/I2a/I2b', d, first, 'SEARCHED', sum(Sr(p, t) is not None for t in SUBO))
print('== H')
F3 = list(texts('1xy ', 4)); assert len(F3) == 341
OX = Rx(Alt(Seq(Grp('o', D()), L('x')), L('y'))); Y = Rx(L('y'))
base = And(OX, Y); wd = And(OX, Y, C('o', lt(5), '1')); wn = And(OX, Y, CNot(C('o', lt(5), '9')))
print(cnt(base, F3), cnt(wd, F3), diff(base, wd, F3, True), diff(base, wn, F3, True) if False else cnt(wn, F3))
print('== R.2 NOT (n:<0) vs some(any)')
NL = Rx(Rep(Seq(Grp('n', D()), L(',')), 0, None)); NLP = list(texts('37,', 4))
a = And(NL, CNot(C('n', lt(0)))); b = And(NL, Some(C('n', ANY)))
print(len(NLP), cnt(a, NLP), cnt(b, NLP), diff(a, b, NLP, True))
print('n=0:<5 on 7,', both(And(NL, C('n', lt(5), '0')), '7,'))
print('== R.6 F17 nullable B')
B = And(NL, C('n', ge(5), '9'))
for t in ['', '1,', 'a', '7,']: print(repr(t), 'B has a row:', searched(B, t) is not None)
print('== R.1.9')
N = And(Rx(Grp('n', Rep(D(), 1, None))), C('n', lt(100)))
print(findall(N, '1234'), findall(Rx(Grp('n', Rep(D(), 1, None))), '1234'), findall(N, '123456'))
