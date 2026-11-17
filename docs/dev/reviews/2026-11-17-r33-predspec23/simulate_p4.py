import sys; sys.path.insert(0, '.')
from ev import *
L = Pat(r"(?:(?<h>\d+)(?::(?<m>\d\d))?,)*")
ITEMS = [(h, mm) for h in ('3', '12') for mm in (None, '15', '45', '05', '99')]
def item(it): return it[0] + ('' if it[1] is None else ':' + it[1]) + ','
LISTS = {'': []}
cur = [[]]
for _ in range(3):
    cur = [c + [it] for c in cur for it in ITEMS]
    for c in cur: LISTS[''.join(item(i) for i in c)] = c
print('lists', len(LISTS))
inR = lambda h, m: int(h) < 10 and int(m) < 30
I1 = {s for s, its in LISTS.items() if all(m is not None and inR(h, m) for h, m in its)}
I2a = {s for s, its in LISTS.items() if all(m is None or inR(h, m) for h, m in its)}
I2b = {s for s, its in LISTS.items() if all((int(h) < 10) if m is None else inR(h, m) for h, m in its)}
notR = lambda h, m: not inR(h, m)
cands = [('((h=0,m=00):R)', joint(['h', 'm'], {'h': '0', 'm': '00'}, inR)),
         ('((h,m=00):R)', joint(['h', 'm'], {'m': '00'}, inR)),
         ('((h,m):R)', joint(['h', 'm'], {}, inR)),
         ('none(((h,m=00):!R))', none(joint(['h', 'm'], {'m': '00'}, notR))),
         ('none(((h,m=99):!R))', none(joint(['h', 'm'], {'m': '99'}, notR))),
         ('none(((h,m):!R))', none(joint(['h', 'm'], {}, notR))),
         ('none(NOT((h,m):R))', none(NOT(joint(['h', 'm'], {}, inR))))]
pool = list(LISTS)
for n, c in cands:
    p = Prog(L, ('c', c))
    w = {x for x in pool if p.whole(x)}; s = sum(1 for x in pool if p.search(x) is not None)
    def d(I):
        dd = [x for x in pool if (x in w) != (x in I)]
        return '%d %r' % (len(dd), dd[:1])
    print('%-22s WHOLE %4d I1 %s I2a %s I2b %s | SEARCHED %d' % (n, len(w), d(I1), d(I2a), d(I2b), s))
# PART 5 zero-pass
N = Pat(r"(?:(?<n>\d),)*")
lt5 = S('<', 5)
c = test('n', lt5)
for nm, cc in [('(n=0:<5)', test('n', lt5, '0')), ('(n:<5)', c), ('NOT (n:<5)', NOT(c)), ('some', some(c)), ('NOT some', NOT(some(c)))]:
    p = Prog(N, ('c', cc))
    print(nm, ' | '.join('%r %s' % (x, fmt(*p.both(x))) for x in ['', '3,', '3,7,', '7,']))
print('--- L83 record spelling of R = (<10, <30) in the closing example')
recR = AND(test('h', S('<', 10)), test('m', S('<', 30)))
for n, c in [('none(NOT (h:<10, m:<30))', none(NOT(recR))), ('none(NOT((h,m):R))', none(NOT(joint(['h', 'm'], {}, inR))))]:
    p = Prog(L, ('c', c))
    w = {x for x in pool if p.whole(x)}
    def d(I):
        dd = [x for x in pool if (x in w) != (x in I)]
        return '%d %r' % (len(dd), dd[:1])
    print('%-26s WHOLE %4d I1 %s I2a %s I2b %s | SEARCHED %d' % (n, len(w), d(I1), d(I2a), d(I2b), sum(1 for x in pool if p.search(x) is not None)))
