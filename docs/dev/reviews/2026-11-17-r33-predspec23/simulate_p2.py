import sys; sys.path.insert(0, '.')
from ev import *
def tally(pool, progs):
    res = {}
    for name, pr in progs:
        w = [x for x in pool if pr.whole(x)]; s = [x for x in pool if pr.search(x) is not None]
        res[name] = (set(w), set(s))
        print('  %-28s WHOLE %5d first %r | SEARCHED %5d first %r' % (name, len(w), w[0] if w else None, len(s), s[0] if s else None))
    return res
def differ(pool, res, a, b):
    for k, mode in ((0, 'WHOLE'), (1, 'SEARCHED')):
        d = [x for x in pool if (x in res[a][k]) != (x in res[b][k])]
        print('  %s [%s] vs [%s] differ %d first %r' % (mode, a, b, len(d), d[0] if d else None))
lt5 = S('<', 5); nlt5 = comp(lt5); ge5 = S('>=', 5)
# --- SV
X = Pat(r"(?<h>\d)?x")
c = test('h', lt5)
pc = Prog(X, ('c', c))
SV = strings('37x ', 4); print('SV', len(SV))
svp = [('NOT c', Prog(X, ('c', NOT(c)))), ('(h: !S)', Prog(X, ('c', test('h', nlt5)))),
       ('diff', Prog(X, ('diff', pc))), ('NOT (h=9: c)', Prog(X, ('c', NOT(test('h', lt5, '9'))))),
       ('NOT (h=0: c)', Prog(X, ('c', NOT(test('h', lt5, '0'))))),
       ('(h="x": !S)', Prog(X, ('c', test('h', nlt5, 'x')))), ('(h="x": >=5)', Prog(X, ('c', test('h', ge5, 'x'))))]
r = tally(SV, svp)
differ(SV, r, 'NOT c', '(h: !S)'); differ(SV, r, 'NOT c', 'diff'); differ(SV, r, '(h: !S)', 'diff')
for x in ['x', '3x', '7x']:
    print('  ROW', repr(x), ' ; '.join('%s=%s' % (n, fmt(*p.both(x))) for n, p in svp))
# --- REP
Y = Pat(r"(?:(?<h>\d)?;)*")
c = test('h', lt5); pc = Prog(Y, ('c', c))
REP = strings('37;', 5); print('REP', len(REP))
rp = [('plain c', pc), ('NOT c', Prog(Y, ('c', NOT(c)))), ('(h: !S)', Prog(Y, ('c', test('h', nlt5)))),
      ('diff', Prog(Y, ('diff', pc))), ('(h=0: c)', Prog(Y, ('c', test('h', lt5, '0')))),
      ('narrower', Prog(Y, ('c', none(test('h', nlt5, 'x'))))), ('NOT some(c)', Prog(Y, ('c', NOT(some(c))))),
      ('occurs.none(c)', Prog(Y, ('c', none(c))))]
r = tally(REP, rp)
differ(REP, r, 'NOT c', '(h: !S)'); differ(REP, r, 'NOT c', 'diff'); differ(REP, r, '(h: !S)', 'diff')
differ(REP, r, 'NOT some(c)', 'occurs.none(c)')
for x in ['', '3;', '3;7;', '7;;', '3;;', ';']:
    print('  ROW', repr(x), ' ; '.join('%s=%s' % (n, fmt(*p.both(x))) for n, p in rp))
