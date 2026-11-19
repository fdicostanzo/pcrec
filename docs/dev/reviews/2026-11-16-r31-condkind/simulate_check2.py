import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check1 import *  # noqa (re-runs check1 silently is fine)
out.clear()
LOOP = ('h',)
def allrec(conds, row):
    """A2 over a RECORD: every pass passes every entry, none needed (the pairing loop's passes; a record naming a
    looped label is tested per pass)."""
    looped = any(c.looped for c in conds)
    rs = inner_rows(row, looped)
    return T if all(all(c.one(r) == T for c in conds) for r in rs) else F
h5 = Cond([('h', None)], lt(5), LOOP); k37 = Cond([('k', None)], lambda v, env: 3 <= int(v) <= 7)
# D1: record = & inside all; zero-pass-record inside all
a = set(s for s in POOL_RZ if allrec([h5, k37], pRZ(s)) == T)
b = set(s for s in POOL_RZ if all_A2(h5, pRZ(s)) == T and all_A2(k37, pRZ(s)) == T)
pr = set(s for s in POOL_RZ if plain(h5, pRZ(s)) == T and plain(k37, pRZ(s)) == T)
rep('D1 RZ all((h:<5, k:3..7)) holds', len(a)); rep('D1 RZ all((h:<5)) & all((k:3..7)) holds', len(b))
rep('D1 differ', (len(a ^ b), sorted(a ^ b)))
rep('D1 all-record holders with k outside 3..7', sorted(s for s in a if not 3 <= int(s[0]) <= 7))
# D1b: the (h=0) default form: all((h=0:<5, k:3..7)) on zero passes
h05 = Cond([('h', '0')], lt(5), LOOP)
a0 = set(s for s in POOL_RZ if allrec([h05, k37], pRZ(s)) == T); p0 = set(s for s in POOL_RZ if plain(h05, pRZ(s)) == T and plain(k37, pRZ(s)) == T)
rep('D1b all((h=0:<5,k:3..7)) vs record (h=0:<5,k:3..7)', (len(a0), len(p0), sorted(a0 ^ p0)))
# D2: loop vs column, same strings, same captures
POOL_K1 = [k for k in D] + [k + ';' + h for k in D for h in D]
assert all(pRZ1(s) and pRZanch(s) for s in POOL_K1)
same_rows = all(pRZ1(s)['cols']['h'] == (pRZanch(s)['passes'][0]['h'] if pRZanch(s)['passes'] else None) for s in POOL_K1)
rep('D2 same strings and captures', same_rows)
hc = Cond([('h', None)], lt(5))            # column h (upper bound 1)
for nm, f1, f2 in [('plain (h:<5)', lambda r: plain(hc, r), lambda r: plain(h5, r)),
                   ('some((h:<5))', lambda r: some(hc, r), lambda r: some(h5, r)),
                   ('occurs.none((h:>=5))', lambda r: none(Cond([('h', None)], lambda v, env: int(v) >= 5), r), lambda r: none(Cond([('h', None)], lambda v, env: int(v) >= 5, LOOP), r)),
                   ('A2 all((h:<5))', lambda r: all_A2(hc, r), lambda r: all_A2(h5, r)),
                   ('A2 all((h=9:<5))', lambda r: all_A2(Cond([('h', '9')], lt(5)), r), lambda r: all_A2(Cond([('h', '9')], lt(5), LOOP), r))]:
    x = [s for s in POOL_K1 if f1(pRZ1(s)) != f2(pRZanch(s))]
    rep(f'D2 {nm}: /(?<k>\\d)(?:;(?<h>\\d))?/ vs /(?<k>\\d)(?:;(?<h>\\d)$)*/ differ', (len(x), x[:3]))
print('\n'.join(out))
