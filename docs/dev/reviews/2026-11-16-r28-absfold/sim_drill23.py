import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drills import *

def c_(): return G('c', D)
def h_(): return G('h', D)
def k_(): return G('k', D)
def a_(): return G('a', D)
# nested: c once, h per outer pass, k per inner pass
NEST = Seq(c_(), Rep(Seq(L(';'), h_(), Rep(Seq(L(':'), k_()), 0, None)), 0, None))
def nest_subs():
    out = []
    inner = [''] + [':' + x for x in '0369'] + [':' + x + ':' + y for x in '27' for y in '05']
    for c in '0359':
        out.append(c)
        for h in '05':
            for i in inner:
                out.append(c + ';' + h + i)
        for h1 in '27':
            for i1 in ('', ':3'):
                for h2 in '4':
                    for i2 in ('', ':6', ':1'):
                        out.append(c + ';' + h1 + i1 + ';' + h2 + i2)
    return out
NS = nest_subs()
ZE = Seq(a_(), L('-'), k_(), Rep(Seq(L(';'), h_()), 0, None))
ZES = [a + '-' + k + ''.join(';' + h for h in hs) for a in '0159' for k in '0359' for n in range(3) for hs in itertools.product('0369', repeat=n)]

EMPTY = lambda env: (lambda t: False)
def emptyx(env): return lambda t: isnum(t) and int(t) < 0
CTLS = [(None, None), ('mark', None), ('def', '0'), ('def', '9')]
ANYD = {l: ANY for l in 'achk'}

def evals(p, subs, F, dom='ANY'):
    """drill 3: record vs & vs joint-of-product, at every depth; drill 2: equal sets, different spellings."""
    out = {'d3': 0, 'd3n': 0, 'd2': 0, 'd2n': 0}
    ex3, ex2 = [], []
    labsets = [('c', 'h', 'k'), ('h', 'k'), ('c', 'k'), ('c', 'h')] if p is NEST else [('h', 'k'), ('a', 'h'), ('a', 'k')]
    sets = {'c': rng(3, 7), 'h': lt(5), 'k': rng(2, 6), 'a': rng(0, 9)}
    d = ANYD if dom == 'ANY' else {l: [str(i) for i in range(10)] for l in 'achk'}
    for s in subs:
        ctx = Ctx(p, s, d, F)
        if not ctx.ok: continue
        for labs in labsets:
            for ctls in itertools.product(CTLS, repeat=len(labs)):
                for md in ('plain', 'A2m'):
                    parts = [(l, c, v, sets[l]) for l, (c, v) in zip(labs, ctls)]
                    r = record(ctx, parts, md)
                    a = amp(ctx, parts, md)
                    j = joint(ctx, [(l, c, v) for l, (c, v) in zip(labs, ctls)],
                              lambda env: (lambda t, Ss=[sets[l](env) for l in labs]: all(S(x) for S, x in zip(Ss, t))), md)
                    out['d3n'] += 1
                    if not (r == a == j):
                        out['d3'] += 1; ex3.append((s, labs, ctls, md, r, a, j))
        # drill 2: an empty set in ONE coordinate, three spellings: constant <0, never-true, joint empty
        for labs in labsets:
            for ctls in itertools.product(CTLS, repeat=len(labs)):
                for md in ('plain', 'A2m'):
                    res = []
                    for emp in (emptyx, EMPTY):
                        parts = [(labs[0], ctls[0][0], ctls[0][1], emp)] + [(l, c, v, sets[l]) for l, (c, v) in zip(labs[1:], ctls[1:])]
                        res.append(record(ctx, parts, md))
                        res.append(amp(ctx, parts, md))
                    res.append(joint(ctx, [(l, c, v) for l, (c, v) in zip(labs, ctls)], EMPTY, md))
                    out['d2n'] += 1
                    if len(set(res)) > 1:
                        out['d2'] += 1; ex2.append((s, labs, ctls, md, res))
    return out, ex3[:6], ex2[:6]

def ze_dollar(F):
    """ZE: the set empty through $a: (h?: <$a, k: 3) vs ((h?, k): <($a, 0)) vs (h?: <0, k: 3) vs (h?: <$a) & (k: 3)"""
    diff = 0; n = 0; ex = []
    for s in ZES:
        ctx = Ctx(ZE, s, ANYD, F)
        if not ctx.ok or not s.startswith('0'): continue
        for hc, hv in CTLS:
            for md in ('plain', 'A2m'):
                r1 = record(ctx, [('h', hc, hv, lt_label('a')), ('k', None, None, eq('3'))], md)
                r2 = joint(ctx, [('h', hc, hv), ('k', None, None)],
                           lambda env: (lambda t, A=int(env['a']): isnum(t[0]) and int(t[0]) < A), md)
                r3 = record(ctx, [('h', hc, hv, lt(0)), ('k', None, None, eq('3'))], md)
                r4 = amp(ctx, [('h', hc, hv, lt_label('a')), ('k', None, None, eq('3'))], md)
                n += 1
                # r2 is a different set unless k=3; compare on k=3 subjects only for r2
                vals = [r1, r3, r4] + ([r2] if s[2] == '3' else [])
                if len(set(vals)) > 1:
                    diff += 1; ex.append((s, hc, hv, md, vals))
    return n, diff, ex[:5]

for F in ('F1', 'F2'):
    for name, p, subs in (('NEST', NEST, NS), ('ZE', ZE, ZES)):
        for dom in ('ANY', 'GROUP'):
            o, e3, e2 = evals(p, subs, F, dom)
            print(F, name, dom, len(subs), o)
            for x in e3[:3]: print('   d3', x)
            for x in e2[:3]: print('   d2', x)
    print(F, 'ZE $a', ze_dollar(F))
