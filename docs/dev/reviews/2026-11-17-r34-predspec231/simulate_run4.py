import sys; sys.path.insert(0, '/var/tmp/pcrec-pcrec/scratch/crit-predspec231/simulate')
from ev import *
Dg = "0123456789"; H12 = list(Dg) + [a + b for a in Dg for b in Dg]
T2P = H12 + [h + ":" + a + b for h in H12 for a in Dg for b in Dg]
TOK = [h + mm for h in ["1", "9", "10", "21"] for mm in ["", ":00", ":15", ":30", ":45", ":50"]]
T2PAIRS = TOK + [a + " " + b for a in TOK for b in TOK]
t2rx = Seq(Grp('h', Rep(D(), 1, 2)), Rep(Seq(L(':'), Grp('m', Seq(D(), D()))), 0, 1)); t2 = Rx(t2rx)
late = J(('h', 'm'), tup_ge(9, 30)); q = And(t2, late)
print('== R.3 t2 table')
for nm, p in [('NOT', And(t2, CNot(late))), ('!R', And(t2, J(('h','m'), lambda h,m: not tup_ge(9,30)(h,m)))),
              ('diff', And(t2, Comp(q))), ('m=0 !R', And(t2, J(('h','m'), lambda h,m: not tup_ge(9,30)(h,m), {'m': '0'})))]:
    print(nm, cnt(p, T2P))
print('m=0 !R vs diff', diff(And(t2, J(('h','m'), lambda h,m: not tup_ge(9,30)(h,m), {'m': '0'})), And(t2, Comp(q)), T2P))
print('== c4 L83')
jt = And(t2, CNot(J(('h','m'), prod(lt(9), lt(30))))); rc = And(t2, CNot(Rec(C('h', lt(9)), C('m', lt(30)))))
print('10', both(jt, '10'), '|', both(rc, '10'))
print('NOT', diff(jt, rc, T2P), 'noNOT', diff(And(t2, J(('h','m'), prod(lt(9), lt(30)))), And(t2, Rec(C('h', lt(9)), C('m', lt(30)))), T2P))
print('== c3 on T2: when, c = late, p = (m:<45)')
pm = C('m', lt(45)); body = Or(And(t2, late, pm), And(t2, Comp(q))); filt = And(t2, When(late, pm))
print('T2', diff(body, filt, T2P, True)); print('PAIRS', diff(body, filt, T2PAIRS, True))
print('A3 counts', cnt(body, T2P), cnt(body, T2PAIRS))
print('== fourth member')
X = Rx(Grp('x', Rep(Lit(DIG | {':'}), 1, None)))
cols = [('NOT(x:q)', And(X, CNot(C('x', ('prog', q))))), ('(x:!q)', And(X, C('x', ('notprog', q)))),
        ('(x: t2&NOT late)', And(X, C('x', ('prog', And(t2, CNot(late)))))), ('flat NOT', And(t2, CNot(late))), ('flat diff', And(t2, Comp(q)))]
for t in ['9', '9:30', '9:15']: print(t, [(n, both(p, t)) for n, p in cols])
print('== R.4 / R.4.1 unchanged counts: t2&!q SEARCHED holds and contains-late')
