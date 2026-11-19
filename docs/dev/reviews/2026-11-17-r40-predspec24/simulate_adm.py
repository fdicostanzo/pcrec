import sys; sys.path.insert(0, '.')
from cnt import *
n = grp('a', rep(DIG, 1))
base = AND(atomic(n), lit('1')); more = AND(atomic(ANDc(n, T('a', lt(10)))), lit('1'))
print('atomic & /1/ on 12: base', searched(base, '12'), 'with cond', searched(more, '12'))
admits('ADMIT atomic-inner, & /1/', base, more, DIG4)
hb = seq(atomic(n), lit('2')); hm = seq(atomic(ANDc(n, T('a', lt(10)))), lit('2'))
print('hole /${atomic(..)}2/ WHOLE 12: base', whole(hb, '12'), 'with cond', whole(hm, '12'))
admits('ADMIT atomic-inner in a hole', hb, hm, DIG4)
# positive lookahead place: /(?=${n & (a:<10)})\d\d/ ... lookahead then 2 digits and backref-free
lb = seq(look(n), lit('1')); lm = seq(look(ANDc(n, T('a', lt(10)))), DIG)
# dead branch drill
dead = alt(grp('a', DIG), grp('b', DIG)); live = grp('a', DIG)
print('dead-branch & (b:"1") WHOLE 1:', whole(ANDc(dead, T('b', eq('1'))), '1'), ' plain:', whole(ANDc(live, T('b', eq('1'))), '1'))
print('first-path labels equal:', whole(dead, '1'), whole(live, '1'))
cmp('DEAD-BRANCH spellings & (b:"1")', ANDc(dead, T('b', eq('1'))), ANDc(live, T('b', eq('1'))), DIG4)
A_ = rep(DIG, 1)
cmp('DEAD-BRANCH in complement', DIFF(DIG, ANDc(dead, T('b', eq('1')))), DIFF(DIG, ANDc(live, T('b', eq('1')))), DIG4)
cmp('DEAD-BRANCH under NOT', ANDc(dead, NOT(T('b', eq('1')))), ANDc(live, NOT(T('b', eq('1')))), DIG4)
# empty set two spellings: (a: <0) vs (a: !/[\s\S]*/) vs (a: "" & "1")  ; all empty sets
P2 = seq(grp('a', rep(DIG, 1)), grp('b', rep(DIG, 1)))
e1 = T('a', lambda v: False); e2 = T('a', lt(0))
cmp('EMPTY two spellings positive', ANDc(P2, e1), ANDc(P2, e2), DIG4)
cmp('EMPTY under NOT vs plain P', ANDc(P2, NOT(e2)), P2, DIG4)
cmp('EMPTY complement vs plain P', DIFF(P2, ANDc(P2, e2)), P2, DIG4)
# equal-behaviour pair built by a condition: P & (a:"1") vs narrowed rx /(?<a>1)(?<b>\d+)/
Nr = seq(grp('a', lit('1')), grp('b', rep(DIG, 1)))
cmp('PAIR P&(a:1) vs narrowed', ANDc(P2, T('a', eq('1'))), Nr, DIG4)
for extra, nm in ((T('b', lt(10)), '(b:<10)'), (NOT(T('b', eq('2'))), 'NOT (b:"2")')):
    cmp('PAIR + ' + nm, ANDc(P2, T('a', eq('1')), extra), ANDc(Nr, extra), DIG4)
    cmp('PAIR in complement + ' + nm, DIFF(rep(DIG,1), ANDc(P2, T('a', eq('1')), extra)), DIFF(rep(DIG,1), ANDc(Nr, extra)), DIG4)
cmp('PAIR atomic', atomic(ANDc(P2, T('a', eq('1')))), atomic(Nr), DIG4)
cmp('PAIR atomic then (b:<10)', ANDc(atomic(ANDc(P2, T('a', eq('1')))), T('b', lt(10))), ANDc(atomic(Nr), T('b', lt(10))), DIG4)
