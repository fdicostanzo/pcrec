import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drills import *

def N(): return G('n', D)
X = L('x')
opt = {
  'x?':      lambda: Seq(Rep(N(), 0, 1), X),
  '(?:x|)':  lambda: Seq(Alt(N(), L('')), X),
  'x{0,1}':  lambda: Seq(Rep(N(), 0, 1), X),
  'x??':     lambda: Seq(Rep(N(), 0, 1, False), X),
  '(?:|x)':  lambda: Seq(Alt(L(''), N()), X),
}
star = {
  'x*':      lambda: Seq(Rep(N(), 0, None), X),
  '(?:x+)?': lambda: Seq(Rep(Rep(N(), 1, None), 0, 1), X),
  '(?:x+|)': lambda: Seq(Alt(Rep(N(), 1, None), L('')), X),
  'x*?':     lambda: Seq(Rep(N(), 0, None, False), X),
  '(?:x+?)??': lambda: Seq(Rep(Rep(N(), 1, None, False), 0, 1, False), X),
}
S = subjects_over('037x', 4)
def conds1(lab='n'):
    c = {}
    for ctl, v in ((None, None), ('mark', None), ('def', '0'), ('def', '9')):
        for sn, Sf in (('<5', lt(5)), ('<0', lt(0)), ('x', eq('x'))):
            c['(%s %s %s: %s)' % (lab, ctl, v, sn)] = (lambda ctl, v, Sf: lambda ctx: single(ctx, lab, ctl, v, Sf))(ctl, v, Sf)
        for md in ('A2m', 'A2v', 'A2z'):
            for sn, Sf in (('<5', lt(5)), ('<0', lt(0))):
                c['all_%s(%s %s %s: %s)' % (md, lab, ctl, v, sn)] = (lambda ctl, v, Sf, md: lambda ctx: single(ctx, lab, ctl, v, Sf, mode=md))(ctl, v, Sf, md)
    return c
for fam, name in ((opt, 'OPT x?'), (star, 'STAR x*')):
    run({k: f() for k, f in fam.items()}, S, conds1(), ['n'], name)

# cross-family: x? vs x* agree on the subjects both match (one kind of absence): '', 'Dx'
both = [s for s in S if len(s) <= 2]
print('-- cross family x? vs x* on subjects both match')
run({'x?': opt['x?'](), 'x*': star['x*']()}, [s for s in S if s in ('x', '0x', '3x', '7x')], conds1(), ['n'], 'CROSS ?/*')

# RZ family: k outside, h looped
def K(): return G('k', D)
def H(): return G('h', D)
def item(): return Seq(L(';'), H())
rz = {
  '*':        lambda: Seq(K(), Rep(item(), 0, None)),
  '(?:+)?':   lambda: Seq(K(), Rep(Rep(item(), 1, None), 0, 1)),
  '(?:+|)':   lambda: Seq(K(), Alt(Rep(item(), 1, None), L(''))),
  '*?':       lambda: Seq(K(), Rep(item(), 0, None, False)),
}
RZS = [k + ''.join(';' + h for h in hs) for k in '0123456789' for n in range(3) for hs in itertools.product('0123456789', repeat=n)]
def condsRZ():
    c = {}
    for hc, hv in ((None, None), ('mark', None), ('def', '9'), ('def', '0')):
        for kc in (None, 'mark'):
            for Sn, Sf in (('<5', lt(5)), ('<0', lt(0))):
                parts = [('h', hc, hv, Sf), ('k', kc, None, rng(3, 7))]
                c['rec h%s%s:%s k%s' % (hc, hv, Sn, kc)] = (lambda parts: lambda ctx: record(ctx, parts))(parts)
                c['amp h%s%s:%s k%s' % (hc, hv, Sn, kc)] = (lambda parts: lambda ctx: amp(ctx, parts))(parts)
                for md in ('A2m', 'A2v', 'A2z'):
                    c['all%s rec h%s%s:%s k%s' % (md, hc, hv, Sn, kc)] = (lambda parts, md: lambda ctx: record(ctx, parts, md))(parts, md)
                    c['all%s amp h%s%s:%s k%s' % (md, hc, hv, Sn, kc)] = (lambda parts, md: lambda ctx: amp(ctx, parts, md))(parts, md)
    return c
run({k: f() for k, f in rz.items()}, RZS, condsRZ(), ['h', 'k'], 'RZ spellings')
