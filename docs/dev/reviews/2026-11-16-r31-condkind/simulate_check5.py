import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check1 import *  # noqa
out.clear()
sets = {'<5': lambda v, env: v.isdigit() and int(v) < 5, '0..4': lambda v, env: v in '01234' and len(v) == 1,
        '!(>=5)': lambda v, env: not (v.isdigit() and int(v) >= 5), '!(5..9)': lambda v, env: not (len(v) == 1 and v in '56789')}
for dv in (None, '0', '9', 'x', ''):
    res = {}
    for nm, S in sets.items():
        res[nm] = tuple(sorted(cnt(POOL_A, pA, [P(Cond([('h', dv)], S))])))
    groups = {}
    for nm, r in res.items(): groups.setdefault(r, []).append(nm)
    rep(f'D7 pool A, h = {dv!r}: spellings of {{0..4}} -> counts', [(g, len(r)) for r, g in groups.items()])
# the (a2) record with a cross-entry $ vs Part I s3 / II.3.2 / II.5 text
rep('D8 AB (a2) record (a = 0: <10, b: >$a) on -1', holds([P(a0lt10), P(bgtA)], pAB('-1')))
print('\n'.join(out))
