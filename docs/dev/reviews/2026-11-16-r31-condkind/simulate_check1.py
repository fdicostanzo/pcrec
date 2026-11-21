import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim import *; from pools import *
def lt(c): return lambda v, env: v.isdigit() and int(v) < c
def gt(c): return lambda v, env: v.isdigit() and int(v) > c
def holds(prog, row):  # prog: list of fns row->T/F/U ; whole value
    return row is not None and all(f(row) == T for f in prog)
def cnt(pool, parse, prog, mode='whole'):
    hs = []
    for s in pool:
        if mode == 'whole': ok = holds(prog, parse(s))
        else: ok = any(holds(prog, r) for r in spans(s, parse))
        if ok: hs.append(s)
    return hs
P = lambda c: (lambda row: plain(c, row))
out = []
def rep(name, got, want=None):
    out.append(f"{name}: {got}" + ('' if want is None else f"   [note: {want}] {'OK' if str(got)==str(want) else 'DIFF'}"))
# ---------------- pool A
h0lt5 = Cond([('h','0')], lt(5)); h9gt7 = Cond([('h','9')], gt(7)); h0gt7 = Cond([('h','0')], gt(7))
hlt3 = Cond([('h',None)], lt(3)); hlt5 = Cond([('h',None)], lt(5)); h0lt9 = Cond([('h','0')], lt(9)); h0lt10 = Cond([('h','0')], lt(10))
rep('A (h=0:<5)&(h=0:>7)', len(cnt(POOL_A, pA, [P(h0lt5), P(h0gt7)])), 0)
x = cnt(POOL_A, pA, [P(h0lt5), P(h9gt7)]); rep('A (h=0:<5)&(h=9:>7)', (len(x), 'c' in x), (11, True))
x = cnt(POOL_A, pA, [P(h0lt5), P(hlt3)]); rep('A (h=0:<5)&(h:<3)', (len(x), 'c' in x), (3, False))
a = set(cnt(POOL_A, pA, [P(h0lt10), P(hlt5)])); b = set(cnt(POOL_A, pA, [P(hlt5)])); rep('A (h=0:<10)&(h:<5) vs (h:<5) differ', len(a ^ b), 0)
rep('A (h:<5) ; + (h=0:<9)', (len(b), len(cnt(POOL_A, pA, [P(h0lt9), P(hlt5)]))), (5, 5))
q1 = lambda row: T if holds([P(hlt5)], row) else F
notq1 = lambda row: F if holds([P(hlt5)], row) else T
both = [s for s in POOL_A if holds([P(h0lt9), q1], pA(s)) and holds([P(h0lt9), notq1], pA(s))]
rep('A S&q1 and S&!q1 both', len(both), 0)
hnot5 = Cond([('h',None)], lambda v, env: not (v.isdigit() and int(v) < 5))
a = set(cnt(POOL_A, pA, [P(h0lt9), P(hnot5)])); b = set(cnt(POOL_A, pA, [P(h0lt9), notq1])); rep('A two nots S&(h:!(<5)) vs S&!q1 differ', (len(a ^ b), 'c' in b, 'c' in a), (11, True, False))
qq = [P(h0lt5)]
rep('A q&(h:<3); q&(h=9:>7); P&!q', (len(cnt(POOL_A, pA, qq+[P(hlt3)])), len(cnt(POOL_A, pA, qq+[P(h9gt7)])), len([s for s in POOL_A if not holds(qq, pA(s))])), (3, 11, 5))
# ---------------- AB
a0lt10 = Cond([('a','0')], lt(10))
bgtA = Cond([('b',None)], lambda v, env: int(v) > int(dollar(env, 'a')))
rec = cnt(POOL_AB, pAB, [P(a0lt10), P(bgtA)])
rep('AB (a2) record (a=0:<10, b:>$a) = &', len(rec), 45)
joint = Cond([('a','0'), ('b',None)], lambda a, b, env: int(a) < 10 and int(b) > int(a))
x = cnt(POOL_AB, pAB, [P(joint)]); rep('AB joint ((a=0,b): a<10 & b>a)', (len(x), '-1' in x), (54, True))
def pABw(s):
    r = pAB(s)
    if r: r['cols']['w'] = None if r['cols']['a'] is None else str(int(r['cols']['a'])+1)
    return r
wge1 = Cond([('w',None)], lambda v, env: int(v) >= 1)
rep('AB (a=0:<10)&(w:>=1)', len(cnt(POOL_AB, pABw, [P(a0lt10), P(wge1)])), 100)
def when_hold(s):
    r = pAB(s)
    c = plain(a0lt10, r) == T
    return (c and plain(bgtA, r) == T) or (not c)
rep('AB when((a=0:<10),(b:>$a))', sum(when_hold(s) for s in POOL_AB), 45)
# ---------------- RZ
LOOP = ('h',)
hRZ = lambda d, S: Cond([('h', d)], S, LOOP)
rep('RZ (h=0:<5)', len(cnt(POOL_RZ, pRZ, [P(hRZ('0', lt(5)))])), 310)
rep('RZ none((h=0:>7)) & (h:<5)', len(cnt(POOL_RZ, pRZ, [lambda r: none(hRZ('0', gt(7)), r), P(hRZ(None, lt(5)))])), 300)
rep('RZ some((h=0:<5)) & (h:<5)', len(cnt(POOL_RZ, pRZ, [lambda r: some(hRZ('0', lt(5)), r), P(hRZ(None, lt(5)))])), 300)
k37 = Cond([('k',None)], lambda v, env: 3 <= int(v) <= 7)
x = cnt(POOL_RZ, pRZ, [P(hRZ('0', lt(5))), P(k37)]); rep('RZ zero-pass-record (h=0:<5, k:3..7)', (len(x), '9' in x, '3' in x), (155, False, True))
for d in (None, '0', '9'):
    a = set(cnt(POOL_RZ, pRZ, [P(hRZ(d, lt(5)))])); b = set(cnt(POOL_RZ, pRZ, [lambda r, d=d: all_A2(hRZ(d, lt(5)), r)]))
    rep(f'RZ (h={d}:<5) vs A2 all differ', len(a ^ b), {None: 10, '0': 0, '9': 10}[d])
rep('RZ some((h=0:<5)) zero-pass holders', len([s for s in POOL_RZ if ';' not in s and some(hRZ('0', lt(5)), pRZ(s)) == T]), 0)
# ---------------- J
hlt_k = lambda d: Cond([('h', d)], lambda v, env: v.isdigit() and int(v) < int(dollar(env, 'k')))
hgt_j = lambda d: Cond([('h', d)], lambda v, env: v.isdigit() and int(v) > int(dollar(env, 'j')))
x = cnt(POOL_J, pJ, [P(hlt_k('0')), P(hgt_j('9'))]); xa = [s for s in x if len(s) == 2]
nofit = [s for s in xa if not any(int(s[0]) < v < int(s[1]) for v in range(10))]
rep('J (h=0:<$k)&(h=9:>$j) h-absent holders; no one value', (len(xa), len(nofit), min(nofit)), (81, 45, '01'))
dif = 0
for v in [str(i) for i in range(10)] + ['', 'x', '99']:
    a = set(cnt(POOL_J, pJ, [P(hlt_k(v)), P(hgt_j(v))]))
    b = set(cnt(POOL_J, pJ, [P(Cond([('h', v)], lambda h, env: h.isdigit() and int(dollar(env,'j')) < int(h) < int(dollar(env,'k'))))]))
    dif += len(a ^ b)
rep('J one default, two conds vs one cond, 13 values', dif, 0)
# ---------------- T2
def late(h, m, env=None): return h.isdigit() and m.isdigit() and (int(h), int(m)) >= (9, 30)
def late45(h, m, env=None): return h.isdigit() and m.isdigit() and (int(h), int(m)) >= (9, 45)
q = [P(Cond([('h',None),('m',None)], late))]
rep('T2 t2 & !q whole', len([s for s in POOL_T2 if not holds(q, pT2(s))]), 1970)
a = set(cnt(POOL_T2, pT2, [P(Cond([('h',None),('m','0')], late))])); b = set(cnt(POOL_T2, pT2, [P(Cond([('h',None),('m','x')], late))]))
rep('T2 (h, m=0) vs (h, m="x") late differ', len(a ^ b), 90)
c60 = set(cnt(POOL_T2, pT2, [P(Cond([('h',None),('m','60')], late))])); rep('T2 m=60 vs m=0 differ', len(a ^ c60), 2)
a = set(cnt(POOL_T2, pT2, [P(Cond([('h',None),('m','30')], late45))]))
def rev22mark(s):
    r = pT2(s)['cols']
    if r['m'] is not None: return late45(r['h'], r['m'])
    return int(r['h']) >= 9
b = set(s for s in POOL_T2 if rev22mark(s))
rep('T2 stale m=30 vs rev22 mark on late45 differ', (len(a ^ b), sorted(a ^ b)), None)
# ---------------- OCC (III.3)
intent = lambda s: all(m['g'] == 'a' for m in re.finditer(r'(?P<g>a)?b', s))
G = ('g',)
ga = Cond([('g', None)], lambda v, env: v == 'a', G)
gs_not = Cond([('g', '')], lambda v, env: v != 'a', G)
gnot = Cond([('g', None)], lambda v, env: v != 'a', G)
for nm, f, want in [('A2 all((g:"a"))', lambda r: all_A2(ga, r), 0), ('A1 plain (g:"a")', lambda r: plain(ga, r), 7),
                    ('none((g="":!"a"))', lambda r: none(gs_not, r), 0), ('none((g:!"a"))', lambda r: none(gnot, r), 94)]:
    rep(f'OCC {nm} vs intent differ', sum((f(pOCC(s)) == T) != intent(s) for s in POOL_OCC), want)
print('\n'.join(out))
