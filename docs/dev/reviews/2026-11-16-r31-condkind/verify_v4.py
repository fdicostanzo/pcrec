import re, itertools
# (1) same strings + same captures for the two pairs named by RULING-2 and SIMULATE-2
def strings(alpha, n):
    for L in range(n + 1):
        for t in itertools.product(alpha, repeat=L): yield ''.join(t)
def table(rx, pool):
    r = re.compile(rx); out = {}
    for s in pool:
        m = r.fullmatch(s)
        if m: out[s] = m.groupdict()
    return out
P1 = list(strings('ab', 6))
a, b = table(r'(?P<g>a)?b', P1), table(r'(?:(?P<g>a)(?=b))*b', P1)
print('RULING-2 pair over {a,b}<=6: same strings+captures', a == b, sorted(a))
D = '0123456789;'
P2 = list(strings(D, 3))
a, b = table(r'(?P<k>\d)(?:;(?P<h>\d))?', P2), table(r'(?P<k>\d)(?:;(?P<h>\d)$)*', P2)
print('SIMULATE-2 pair over [0-9;]<=3: same strings+captures', a == b, len(a))
# can h / g be set more than once in some match of the loop forms? (rev 22's BEHAVIOURAL repetition, L2439)
def max_sets(rx, pool):
    # count iterations by matching with the loop body made capturing-each: use finditer of the body on the match
    r = re.compile(rx); mx = 0
    for s in pool:
        if r.fullmatch(s): mx = max(mx, s.count(';') if ';' in rx else s.count('a'))
    return mx
print('max loop passes, k(;h$)* :', max_sets(r'\d(?:;\d$)*', P2), '| (a(?=b))*b :', max_sets(r'(?:a(?=b))*b', P1))
# (2) RZ mixed record inside all, A2 = every pass passes c (k read from the row), none needed
RZ = [k + ''.join(';' + h for h in hs) for k in '0123456789' for n in range(3)
      for hs in itertools.product('0123456789', repeat=n)]
assert len(RZ) == 1110
def parse(s):
    p = s.split(';'); return p[0], p[1:]
A2_rec = A2_split = plain = 0; diff = []
for s in RZ:
    k, hs = parse(s); kin = 3 <= int(k) <= 7
    x = all(int(h) < 5 and kin for h in hs)                 # all((h: <5, k: 3..7)), vacuous on zero passes
    y = all(int(h) < 5 for h in hs) and kin                 # all((h: <5)) & (k: 3..7)
    z = all(int(h) < 5 for h in (hs or ['0'])) and kin      # plain (h = 0: <5, k: 3..7): LEFT JOIN row reads 0
    A2_rec += x; A2_split += y; plain += z
    if x != y: diff.append(s)
print('RZ all(record)', A2_rec, 'all(h)&k', A2_split, 'plain (h=0) record', plain, 'differ', diff)
# (3) A2 on the empty set: all((h: <0)) holds exactly on zero passes
print('RZ A2 all((h: <0)) holds on', sum(1 for s in RZ if not parse(s)[1]))
