import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate')
from ev import *

def both(p, t):
    w = 'HOLDS' if W(p, t) else 'FAILS'
    s = Sr(p, t)
    return w + ' / ' + ('FAILS' if s is None else 'HOLDS %r@%d' % s)

def cnt(p, pool):
    return sum(W(p, t) for t in pool), sum(Sr(p, t) is not None for t in pool)
def diff(p1, p2, pool, report=False):
    dw = [t for t in pool if W(p1, t) != W(p2, t)]
    ds = [t for t in pool if (Sr(p1, t) is None) != (Sr(p2, t) is None)]
    out = (len(dw), len(ds), dw[:1], ds[:1])
    if report:
        dr = [t for t in pool if Sr(p1, t) != Sr(p2, t)]
        out = out + (len(dr), dr[:1])
    return out

SVrx = Seq(Rep(Grp('h', D()), 0, 1), L('x')); SV = Rx(SVrx)
REPrx = Rep(Seq(Rep(Grp('h', D()), 0, 1), L(';')), 0, None); REP = Rx(REPrx)
SVP = list(texts('37x ', 4)); REPP = list(texts('37;', 5))
assert len(SVP) == 341 and len(REPP) == 364

print('== §R.3 set-once')
c = C('h', lt(5))
progs = {'NOT': And(SV, CNot(c)), '!S': And(SV, C('h', NOTS(lt(5)))), 'diff': And(SV, Comp(And(SV, c))),
         'NOT h=9': And(SV, CNot(C('h', lt(5), '9'))), 'h=x !S': And(SV, C('h', NOTS(lt(5)), 'x')),
         'h=x >=5': And(SV, C('h', ge(5), 'x'))}
for t in ['x', '3x', '7x']:
    print(t, {k: both(p, t) for k, p in progs.items()})
for k in ['NOT', '!S', 'diff']: print(k, cnt(progs[k], SVP))
print('NOT vs !S', diff(progs['NOT'], progs['!S'], SVP), 'NOT vs diff', diff(progs['NOT'], progs['diff'], SVP))

print('== §R.3 repeated')
progs = {'plain': And(REP, c), 'NOT': And(REP, CNot(c)), '!S': And(REP, C('h', NOTS(lt(5)))),
         'diff': And(REP, Comp(And(REP, c)))}
for t in ['', '3;', '3;7;', '7;;', '3;;']:
    print(repr(t), {k: both(p, t) for k, p in progs.items()})
for k in ['NOT', '!S', 'diff']: print(k, cnt(progs[k], REPP))
print('NOT vs !S', diff(progs['NOT'], progs['!S'], REPP), 'NOT vs diff', diff(progs['NOT'], progs['diff'], REPP),
      '!S vs diff', diff(progs['!S'], progs['diff'], REPP))

print('== c6: default under NOT')
print('SV NOT(h=9:<5) vs NOT(h:<5)', diff(And(SV, CNot(C('h', lt(5), '9'))), And(SV, CNot(c)), SVP))
print('REP NOT(h=x:<5) vs NOT(h:<5)', diff(And(REP, CNot(C('h', lt(5), 'x'))), And(REP, CNot(c)), REPP))
print('SV (h=9:<5) vs (h:<5)', diff(And(SV, C('h', lt(5), '9')), And(SV, c), SVP))
print('REP (h=x:<5) vs (h:<5)', diff(And(REP, C('h', lt(5), 'x')), And(REP, c), REPP))
print('REP some((h=x:<5)) vs some', diff(And(REP, Some(C('h', lt(5), 'x'))), And(REP, Some(c)), REPP))

print('== R.2 sentinel and L30 edges')
sen = And(REP, None_(C('h', NOTS(lt(10)), 'x')))
print('sentinel', both(sen, ''), both(sen, '7;'), both(sen, ';'), cnt(sen, REPP))
for P, pool, nm in [(SV, SVP, 'SV'), (REP, REPP, 'REP')]:
    print(nm, 'edge empty', diff(And(P, CNot(C('h', lt(0)))), And(P, C('h', NOTS(lt(0)))), pool),
          'edge full', diff(And(P, CNot(C('h', lt(10)))), And(P, C('h', NOTS(lt(10)))), pool))

print('== pass-and alternative (R.8 item 2b)')
class CAlt(Cond):
    def __init__(s, name, S): s.name, s.S = name, S
    def names(s): return [s.name]
    def ev(s, row, pas=None):
        ps = passes_for(row, [s.name], pas)
        vs = [p.get(s.name) for p in ps]
        if None in vs: return U
        return T if all(s.S(v) for v in vs) else F
alt = And(REP, CNot(CAlt('h', lt(5))))
print('7;;', both(And(REP, CNot(c)), '7;;'), both(alt, '7;;'))
print('differ', diff(And(REP, CNot(c)), alt, REPP))

print('== condition-or (R.8 item 5)')
ABC = Rx(Alt(Seq(L('a'), Grp('h', D())), Seq(L('b'), Grp('k', D())), L('c')))
class COr2(Cond):
    def __init__(s, *cs): s.cs = cs
    def names(s): return []
    def ev(s, row, pas=None): return T if any(c.ev(row, pas) == T for c in s.cs) else F
k1 = And(ABC, CNot(COr(C('h', lt(5)), C('k', lt(5)))))
k2 = And(ABC, CNot(COr2(C('h', lt(5)), C('k', lt(5)))))
P156 = list(texts('abc37', 3)); assert len(P156) == 156
print('b7', both(k1, 'b7'), both(k2, 'b7'), 'differ', diff(k1, k2, P156))
