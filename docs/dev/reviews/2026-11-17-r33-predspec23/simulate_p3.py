import sys; sys.path.insert(0, '.')
from ev import *
t2 = Pat(r"(?<h>\d{1,2})(?::(?<m>\d\d))?")
Rf = lambda h, m: (int(h), int(m)) >= (9, 30)
late = joint(['h', 'm'], {}, Rf)
q = Prog(t2, ('c', late))
progs = [('NOT', Prog(t2, ('c', NOT(late)))), ('!R', Prog(t2, ('c', joint(['h', 'm'], {}, lambda h, m: not Rf(h, m))))),
         ('diff', Prog(t2, ('diff', q))), ('m=0 !R', Prog(t2, ('c', joint(['h', 'm'], {'m': '0'}, lambda h, m: not Rf(h, m))))),
         ('!contains', Prog(t2, ('ncontains', q))), ('text.none', Prog(t2, ('textnone', q)))]
holes = {'q': q, 't2': Prog(t2)}
ra = Prog(Pat(r"(?![\s\S]*${q})${t2}", holes))
rb = Prog(Pat(r"\A(?![\s\S]*${q})[\s\S]*?${t2}", holes))
progs += [('(i)(a)', ra), ('(i)(b)', rb)]
for pool, pn in ((T2POOL, 'T2'), (T2PAIRS, 'T2PAIRS')):
    res = {}
    haslate = {x for x in pool if q.search(x) is not None}
    for n, p in progs:
        w = {x for x in pool if p.whole(x)}; s = {x for x in pool if p.search(x) is not None}
        res[n] = (w, s)
        fw = [x for x in pool if x in w][:1]; fs = [x for x in pool if x in s][:1]
        print(pn, '%-10s WHOLE %5d %s SEARCHED %5d %s | searched&late %d' % (n, len(w), fw, len(s), fs, len(s & haslate)))
    def dif(a, b):
        for k in (0, 1):
            d = [x for x in pool if (x in res[a][k]) != (x in res[b][k])]
            print(pn, ('WHOLE', 'SEARCHED')[k], a, 'vs', b, len(d), d[:1])
    dif('m=0 !R', 'diff'); dif('(i)(a)', 'text.none'); dif('(i)(b)', 'text.none'); dif('text.none', '!contains')
    for n in ('(i)(a)', 'text.none', 'diff'):
        fa = [x for x in pool if len(dict(progs)[n].findall(x)) >= 2]
        print(pn, 'findall 2+', n, len(fa))
for x in ['9:30', '9:15', '9:15 9:30', '9:30 9:15', 'a 9:15', '9:15 1', '9:30 1']:
    print(repr(x), 'a:', fmt(*ra.both(x)), [(r.stretch, r.i) for r in ra.findall(x)],
          '| b:', fmt(*rb.both(x)), [(r.stretch, r.i) for r in rb.findall(x)],
          '| ii:', fmt(*dict(progs)['text.none'].both(x)), [(r.stretch, r.i) for r in dict(progs)['text.none'].findall(x)])
print('whole (b) on "1 1"', rb.whole('1 1'))
