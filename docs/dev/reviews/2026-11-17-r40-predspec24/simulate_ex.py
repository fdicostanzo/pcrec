import sys; sys.path.insert(0, '.')
from ev import *

def show(tag, prog, w, s, f):
    W = whole(prog, w); S = searched(prog, s); F = findall(prog, f)
    print(tag, '| WHOLE', repr(w), 'HOLDS' if W is not None else 'FAILS', W if W else '',
          '| SEARCHED', repr(s), S, '| FIND-ALL', repr(f), [(x[0], x[1]) for x in F])

D1 = DIG
dplus = rep(DIG, 1)
B = grp('l', seq(DIG, DIG)); A = seq(grp('l', DIG), DIG)
show('B1 (B|A)&(l:<20)', ANDc(alt(B, A), T('l', lt(20))), '25', '25', '25 13')
Ba = grp('l', lit('aa')); Aa = seq(grp('l', lit('a')), lit('a'))
show('B3 L60', ANDc(alt(Ba, Aa), T('l', eq('a'))), 'aa', 'aa', 'aa aaaa')
P = seq(grp('a', rep(DIG, 1)), grp('b', rep(DIG, 1)))
show('B4 P&(a:"1")', ANDc(P, T('a', eq('1'))), '123', '123', '123 9 112')
show('B5', ANDc(alt(B, A), T('l', lt(10))), '12', '12', '12 25 13')
show('B6', ANDc(alt(ANDc(B, T('l', gt(50))), A), T('l', lt(10))), '12', '12', '12 25 13')
show('B8 atomic', ANDc(atomic(alt(B, A)), T('l', lt(20))), '25', '25', '25 13')
show('B9 atomic inner', atomic(ANDc(P, T('a', eq('1')))), '123', '123', '123 9 112')
show('K1 P&!(P&(a:"1"))', DIFF(P, ANDc(P, T('a', eq('1')))), '123', '123', '123')
X = seq(look(grp('x', rep(DIG, 1))), DIG)
show('K3 lookahead', ANDc(X, T('x', eq('1'))), '12', '12', '112 12 1')
U = seq(grp('b', rep(DIG, 1)), opt(grp('a', DIG)))
show('U1', ANDc(U, T('a', lt(5))), '12', '12', '12 1 19 3')
show('U2 NOT', ANDc(U, NOT(T('a', lt(5)))), '1', '1', '1 12 19 3')
# U3: NOT ((h:<5)|(k:<5)) on b7: need a pattern; guess /a(?<h>\d)|b(?<k>\d)|c/ ?  (not given in R.1.5)
HK = alt(seq(lit('a'), grp('h', DIG)), seq(lit('b'), grp('k', DIG)), lit('c'))
show('U3 (guess HK)', ANDc(HK, NOT(cor(T('h', lt(5)), T('k', lt(5))))), 'b7', 'b7', 'b7 a3 c')
L1 = rep(seq(grp('h', DIG), lit(';')))
show('L1 last pass', ANDc(L1, T('h', lt(5))), '7;3;', '7;3;', '7;3; 3;7;')
REP = rep(seq(opt(grp('h', DIG)), lit(';')))
show('R13;; REP&(h:<5)', ANDc(REP, T('h', lt(5))), '3;;', '3;;', '3;;')
# V10: inside loop
item = ANDc(seq(grp('h', DIG), lit(';')), T('h', lt(5)))
show('V10 item+', rep(item, 1), '3;7;', '3;7;', '3;7; 3;1;')
# R.1.4 THE LAW labels part, D4 etc later
# H1/H2 occurrences one-pattern lazy gap  (?:.*?(r))*.*
def occ(r, name='hit'):
    L = rep(seq(rep(ANY, 0, None, greedy=False), r))
    return seq(L, rep(ANY)), L
o1, _ = occ(ANDc(grp('n', dplus), T('n', lt(100))))
show('H1 occ(n & n<100)', o1, '1234', '1234', '1234')
o2, _ = occ(grp('hit', dplus))
show('H2 occ & (hit:<100)', ANDc(o2, T('hit', lt(100))), '1234', '1234', '1234')
for p2, st in seq(ANDc(o2, T('hit', lt(100))), END)('1234', 0, {}):
    print('  H2 first path hits:', [c for k, v in st.items() if isinstance(k, tuple) for c in v]); break
for p2, st in seq(o1, END)('1234', 0, {}):
    print('  H1 first path hits:', [c for k, v in st.items() if isinstance(k, tuple) for c in v]); break
# WH1 when
KHloop = rep(seq(lit(';'), grp('h', DIG)))
KH = seq(grp('k', DIG), KHloop)
def when(x, c, p): return ANDc(x, cor(NOT(c), p))
show('WH1', when(KH, T('h', lt(5)), T('k', between(3, 7))), '5;1;9', '5;1;9', '3;0;5 5;1;9')
show('D11 KH&(h<5,k 3..7)', ANDc(KH, T('h', lt(5)), T('k', between(3, 7))), '3;5;0', '3;5;0', '3;5;0')
# R.3 table
Ph = seq(opt(grp('h', DIG)), lit('x'))
for tag, prog in [('NOT (h:<5)', ANDc(Ph, NOT(T('h', lt(5))))),
                  ('(h:!<5)', ANDc(Ph, T('h', comp(lt(5))))),
                  ('P&!(P&(h:<5))', DIFF(Ph, ANDc(Ph, T('h', lt(5))))),
                  ('(h="x":!<5)', ANDc(Ph, T('h', comp(lt(5)), default='x')))]:
    print('R.3', tag, ['HOLDS' if whole(prog, w) is not None else 'FAILS' for w in ('x', '3x', '7x')])
# R.1.4 E14b atomic(t2) & !q on 9:30 SEARCHED
t2 = seq(grp('h', rep(DIG, 1, 2)), opt(seq(lit(':'), grp('m', seq(DIG, DIG)))))
def R930(vs):
    h, m = vs
    return isnum(h) and isnum(m) and (int(h), int(m)) >= (9, 30)
q = ANDc(t2, TT(('h', 'm'), R930))
show('t2&!q', DIFF(t2, q), '9:30', '9:30', '9:30 1')
show('atomic(t2)&!q', DIFF(atomic(t2), q), '9:30', '9:30', '9:30 1')
# R.2 / polarity t2 & !(t2 & (h:<0))
show('E6b', DIFF(t2, ANDc(t2, T('h', lt(0)))), '9:30', 'x9:30', '9:30 1')
# R.8 sql-picture example
show('E8 ex', ANDc(alt(ANDc(B, T('l', gt(50))), A), T('l', lt(10))), '12', '12', '12 25 13')
# join-order example (P & Q) & ((a:"1")|(c:"1"))
Q = seq(grp('c', dplus), grp('d', dplus))
show('E5 ex', ANDc(AND(P, Q), cor(T('a', eq('1')), T('c', eq('1')))), '123', '123', '123 1121')
# lookahead-labels example
LA = seq(look(seq(rep(ANY, 0, None, greedy=False), DIG, DIG, lit(':'), grp('lm', seq(DIG, DIG)))),
         grp('h', rep(DIG, 1, 2)), opt(seq(lit(':'), DIG, DIG)))
show('E13 ex', ANDc(LA, T('lm', ge(30))), '10:45', '9:15 10:45', '9:15 10:45')
# three-valued example
show('E1 ex', ANDc(U, NOT(T('a', lt(5)))), '1', '1', '1 12 19 3')
# complement-place example: [\s\S]* & !q
show('E9 ex', DIFF(rep(ANY), q), '9:30', '9', '9 9:30 10')
# group-truth example REP & NOT some((h:<5))
REPl = rep(seq(opt(grp('h', DIG)), lit(';'))); LOOPED_NAMES[REPl.lid] = {'h'}
show('E12 ex', ANDc(REPl, NOT(some(REPl, T('h', lt(5))))), ';', '7;;', '; 3;7;; 3;')
# conditional-spelling example KH & when(c,p,q) = KH & ((c & p) | (NOT c & q))
KHl = rep(seq(lit(';'), grp('h', DIG))); KH2 = seq(grp('k', DIG), KHl)
c = T('h', lt(5)); pp = T('k', between(3, 7)); qq = T('k', lt(3))
show('E15 ex', ANDc(KH2, cor(seq(c, pp), seq(NOT(c), qq))), '5;1;9', '1;0;9', '1;0;9 5;1;9 3;0;5')
# repeated-means example
show('E11 ex', AND(rep(seq(grp('h', DIG), lit(';')), 1), seq(DIG, lit(';'))), '3;', '7;3;', '3; 7;3;')
show('E11 ex+cond', ANDc(AND(rep(seq(grp('h', DIG), lit(';')), 1), seq(DIG, lit(';'))), T('h', lt(5))), '3;', '7;3;', '3; 7;3;')
