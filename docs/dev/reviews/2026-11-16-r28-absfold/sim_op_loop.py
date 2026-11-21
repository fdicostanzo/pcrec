import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'recompute.py')).read().split('# ---------- (OP)')[0].split('# ---------- (RZ)')[0])
import itertools
OPp = Rep(Seq(G('h', Rep(D, 1, None)), Rep(Seq(L(':'), G('m', Seq(D, D))), 0, 1), L(',')), 0, None)
OP_ITEMS = [(h, m) for h in ("3", "12") for m in (None, "15", "45")]
SUBJ_OP = ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its) for n in range(4) for its in itertools.product(OP_ITEMS, repeat=n)]
od = {'h': [str(i) for i in range(13)], 'm': ["%02d" % i for i in range(100)]}
pp = [('h', None, None, lt(10)), ('m', None, None, lt(30))]
for oil in (True, False):
    R = run(OPp, SUBJ_OP, {md: (lambda md: lambda c: record(c, pp, md))(md) for md in ('A2v', 'A2z', 'A2m')}, od, oil)
    T = run(OPp, SUBJ_OP, {'today': lambda c: record(c, pp, 'today')}, od, False)
    print('? is a loop:', oil)
    for md in ('A2v', 'A2z', 'A2m'): cnt('today vs all %s' % md, SUBJ_OP, T['today'], R[md])
    for s in ('', '3,', '3:15,', '3,3:15,'): print('   ', repr(s), [R[md][s] for md in ('A2v', 'A2z', 'A2m')], T['today'][s])
