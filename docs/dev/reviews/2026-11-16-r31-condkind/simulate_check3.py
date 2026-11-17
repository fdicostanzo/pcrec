import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check1 import *  # noqa
out.clear()
LOOP = ('h',)
def both(name, pool, parse, prog):
    w = set(cnt(pool, parse, prog)); s = set(cnt(pool, parse, prog, 'searched'))
    mv = sorted(s ^ w, key=lambda x: (len(x), x))
    rep(f'SEARCH {name}', (len(w), len(s), len(mv), mv[:3]))
def bothc(name, pool, parse, prog, qprog):
    """prog & !q: searched: some span of prog, and NO span of q anywhere in the subject (per source row)"""
    w = set(x for x in pool if holds(prog, parse(x)) and not holds(qprog, parse(x)))
    s = set(x for x in pool if any(holds(prog, r) for r in spans(x, parse)) and not any(holds(qprog, r) for r in spans(x, parse)))
    mv = sorted(s ^ w, key=lambda x: (len(x), x))
    rep(f'SEARCH {name}', (len(w), len(s), len(mv), mv[:3]))
# pool A rows
both('A (h=0:<5)&(h=9:>7)', POOL_A, pA, [P(h0lt5), P(h9gt7)])
both('A (h=0:<5)&(h:<3)', POOL_A, pA, [P(h0lt5), P(hlt3)])
bothc('A S & !q1', POOL_A, pA, [P(h0lt9)], [P(hlt5)])
# AB rows
both('AB (a2) record (a=0:<10, b:>$a)', POOL_AB, pAB, [P(a0lt10), P(bgtA)])
both('AB joint ((a=0,b): a<10 & b>a)', POOL_AB, pAB, [P(joint)])
both('AB (a=0:<10)&(w:>=1)', POOL_AB, pABw, [P(a0lt10), P(wge1)])
both('AB (b:>$a)', POOL_AB, pAB, [P(bgtA)])
# RZ rows
hRZ = lambda d, S: Cond([('h', d)], S, LOOP)
both('RZ (h:<5)', POOL_RZ, pRZ, [P(hRZ(None, lt(5)))])
both('RZ (h=0:<5)', POOL_RZ, pRZ, [P(hRZ('0', lt(5)))])
both('RZ none((h=0:>7)) & (h:<5)', POOL_RZ, pRZ, [lambda r: none(hRZ('0', gt(7)), r), P(hRZ(None, lt(5)))])
both('RZ some((h=0:<5)) & (h:<5)', POOL_RZ, pRZ, [lambda r: some(hRZ('0', lt(5)), r), P(hRZ(None, lt(5)))])
k37 = Cond([('k', None)], lambda v, env: 3 <= int(v) <= 7)
both('RZ (h=0:<5, k:3..7)', POOL_RZ, pRZ, [P(hRZ('0', lt(5))), P(k37)])
both('RZ A2 all((h:<5))', POOL_RZ, pRZ, [lambda r: all_A2(hRZ(None, lt(5)), r)])
both('RZ A2 all((h=9:<5))', POOL_RZ, pRZ, [lambda r: all_A2(hRZ('9', lt(5)), r)])
# J: the two-defaults oddity
both('J (h=0:<$k)&(h=9:>$j)', POOL_J, pJ, [P(hlt_k('0')), P(hgt_j('9'))])
# T2 with default; check against rev 22's quoted 1,660 for m = 0 (whole vs searched differ)
both('T2 ((h, m=0): late)', POOL_T2, pT2, [P(Cond([('h', None), ('m', '0')], late))])
both('T2 ((h, m): late)', POOL_T2, pT2, [P(Cond([('h', None), ('m', None)], late))])
qT = [P(Cond([('h', None), ('m', None)], late))]
bothc('T2 t2 & !q', POOL_T2, pT2, [], qT)
print('\n'.join(out))
