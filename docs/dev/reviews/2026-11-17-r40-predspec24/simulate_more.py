import sys; sys.path.insert(0, '.')
from cnt import *
L = grp('l', rep(DIG, 1))
plain = findall(L, ''); c = ANDc(L, T('l', lt(100)))
xs = [t for t in DSP if set((a[1], a[1]+len(a[0])) for a in findall(c, t)) - set((a[1], a[1]+len(a[0])) for a in findall(L, t))]
print('D3 resplit', len(xs), first(xs))
Ph = seq(opt(grp('h', DIG)), lit('x'))
cmp('R.3 set-once NOT vs complement', ANDc(Ph, NOT(T('h', lt(5)))), DIFF(Ph, ANDc(Ph, T('h', lt(5)))), SVPOOL)
cmp('R.3 NOT vs default form', ANDc(Ph, NOT(T('h', lt(5)))), ANDc(Ph, T('h', comp(lt(5)), default='x')), SVPOOL)
# R.1.8 repeated vs set once, labels compared
cmp('D10', ANDc(AND(rep(seq(grp('h', DIG), lit(';')), 1), seq(DIG, lit(';'))), T('h', lt(5))), ANDc(seq(grp('h', DIG), lit(';')), T('h', lt(5))), RG3)
