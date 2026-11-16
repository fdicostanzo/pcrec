import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drills import *
def K(): return G('k', D)
def H(): return G('h', D)
pats = {
  '(?:k-)?(?:;h)*':  lambda: Seq(Rep(Seq(K(), L('-')), 0, 1), Rep(Seq(L(';'), H()), 0, None)),
  '(?:k-|)(?:;h)*':  lambda: Seq(Alt(Seq(K(), L('-')), L('')), Rep(Seq(L(';'), H()), 0, None)),
  'k?h? (set-once pair)': lambda: Seq(Rep(K(), 0, 1), L('-'), Rep(H(), 0, 1)),
  '(?:k|)(?:h|)':    lambda: Seq(Alt(K(), L('')), L('-'), Alt(H(), L(''))),
}
subs = ['', '3-', '3-;1', ';1', ';1;2', '3-;1;7', '-', '3-', '-1', '3-1']
for opt_loop in (True, False):
    print('### opt_is_loop =', opt_loop)
    for name, f in pats.items():
        p = f()
        out = []
        for s in subs:
            ctx = Ctx(p, s, {'h': ANY, 'k': ANY}, 'F1', opt_loop)
            if not ctx.ok: continue
            row = []
            for cn, fn in (('rec', lambda c: record(c, [('h', None, None, lt(5)), ('k', 'mark', None, rng(3, 7))])),
                           ('amp', lambda c: amp(c, [('h', None, None, lt(5)), ('k', 'mark', None, rng(3, 7))])),
                           ('joint', lambda c: joint(c, [('h', None, None), ('k', 'mark', None)], lambda env: lambda t: isnum(t[0]) and int(t[0]) < 5 and isnum(t[1]) and 3 <= int(t[1]) <= 7))):
                try: row.append((cn, fn(ctx)))
                except SiblingError: row.append((cn, 'SIBLING-ERROR'))
            out.append((s, row))
        print(name, out)
