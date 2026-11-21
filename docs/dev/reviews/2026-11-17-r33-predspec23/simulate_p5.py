import sys; sys.path.insert(0, '.')
from ev import *
import re
lt5 = S('<', 5); nlt5 = comp(lt5)
# b1
t2 = Pat(r"(?<h>\d{1,2})(?::(?<m>\d\d))?")
pad = lambda h, m: (int(h), int(m)) >= (9, 30)
for nm, c in [('m=0', joint(['h', 'm'], {'m': '0'}, pad)), ('plain', joint(['h', 'm'], {}, pad))]:
    p = Prog(t2, ('c', c))
    d = [x for x in T2POOL if p.whole(x) != (p.search(x) is not None)]
    print('b1', nm, len(d), d[:1], fmt(*p.both('9:15')))
# O28 pool {1,7,comma}
N = Pat(r"(?:(?<n>\d)?,)*")
c = test('n', lt5)
POOL = strings('17,', 5)
ps = {'(n:!<5)': Prog(N, ('c', test('n', nlt5))), '(n:<5)': Prog(N, ('c', c)), 'NOT': Prog(N, ('c', NOT(c))),
      'diff': Prog(N, ('diff', Prog(N, ('c', c))))}
res = {}
for k, p in ps.items():
    w = {x for x in POOL if p.whole(x)}; s = {x for x in POOL if p.search(x) is not None}; res[k] = (w, s)
    print('O28', k, len(w), len(s), ' | '.join('%r %s' % (x, fmt(*p.both(x))) for x in ['', '1,7,', '7,', '7,,']))
for k in (0, 1):
    d = [x for x in POOL if (x in res['NOT'][k]) != (x in res['(n:!<5)'][k])]
    print('O28 differ', k, len(d), sorted(d, key=lambda s: (len(s), [ '17,'.index(ch) for ch in s]))[:1])
# WHEN
K = Pat(r"(?<k>\d)(?:;(?<h>\d))*")
WP = [a for a in D] + [a + ';' + b for a in D for b in D] + [a + ';' + b + ';' + cc for a in D for b in D for cc in D]
pk = test('k', between(3, 7))
for nm, cc in [('(h:<5)', test('h', lt5)), ('(h=0:<5)', test('h', lt5, '0'))]:
    body1a = Prog(K, ('c', cc), ('c', pk)); body1b = Prog(K, ('diff', Prog(K, ('c', cc))))
    body2b = Prog(K, ('c', NOT(cc)))
    def holds(t, mode, b2):
        if mode == 'W': return body1a.whole(t) or b2.whole(t)
        # searched alternation: PCRE's one parse of (A|B): leftmost start, A's rows first then B's at that start
        for i in range(len(t) + 1):
            if any(True for _ in body1a.rows_at(t, i)) or any(True for _ in b2.rows_at(t, i)): return True
        return False
    for mode in 'WS':
        h1 = {t for t in WP if holds(t, mode, body1b)}; h2 = {t for t in WP if holds(t, mode, body2b)}
        print('WHEN', nm, mode, len(WP), len(h1), 'differ', len(h1 ^ h2), sorted(h1 ^ h2)[:1])
# OCC127: occurrences(/(?<g>a)?b/) span; hits = find-all in the span; passes = hits
def occ_rows_whole(t):  # whole-value: the one row, passes = hits
    return [mm.group('g') for mm in re.finditer(r'(?P<g>a)?b', t)]
SP = strings('ab', 6)
every = lambda gs: all((g if g is not None else 'a') == 'a' for g in gs) if gs else ('a' == 'a')
narrow = lambda gs: not any(((g if g is not None else '') != 'a') for g in gs)
we = sum(1 for t in SP if every(occ_rows_whole(t))); wn = sum(1 for t in SP if narrow(occ_rows_whole(t)))
print('OCC127', len(SP), 'every', we, 'narrower', wn)
