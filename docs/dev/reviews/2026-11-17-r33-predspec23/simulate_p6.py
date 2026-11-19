import sys; sys.path.insert(0, '.')
from ev import *
t2 = Pat(r"(?<h>\d{1,2})(?::(?<m>\d\d))?")
late = joint(['h', 'm'], {}, lambda h, m: (int(h), int(m)) >= (9, 30))
hg = test('h', S('>', 20))
before = Prog(t2, ('diff', Prog(t2, ('c', late))))
after = Prog(t2, ('c', hg), ('diff', Prog(t2, ('c', hg), ('c', late))))
dd = Prog(r"\d:\d\d")
b2 = Prog(t2, ('diff', dd)); a2 = Prog(t2, ('c', test('m', S('<', 20), '0')), ('diff', dd))
for pool, pn in ((T2POOL, 'T2'), (T2PAIRS, 'T2PAIRS')):
    for (b, a, n) in ((before, after, 'h>20'), (b2, a2, 'm=0<20')):
        aw = sum(1 for x in pool if a.whole(x) and not b.whole(x))
        as_ = sum(1 for x in pool if a.search(x) is not None and b.search(x) is None)
        print(pn, n, 'admits WHOLE', aw, 'SEARCHED', as_)
AB = Pat(r"(?:(?<a>\d)?\/)(?<b>\d)")
pool = ['/' + d for d in D] + [a + '/' + b for a in D for b in D]
def gtA(row):
    a = row.val('a'); b = row.val('b')
    return U if a is None or b is None else (T if int(b) > int(a) else F)
gtA.names = ['b']
rec = Prog(AB, ('c', AND(test('a', S('<', 10), '0'), gtA)))
jt = Prog(AB, ('c', joint(['a', 'b'], {'a': '0'}, lambda a, b: int(a) < 10 and int(b) > int(a))))
print('AB', len(pool), sum(rec.whole(x) for x in pool), sum(jt.whole(x) for x in pool), [x for x in pool if rec.whole(x) != jt.whole(x)][:1])
