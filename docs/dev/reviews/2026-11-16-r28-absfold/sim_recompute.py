# Part (b): recompute every quoted count of 4G.1/4G.2/4G.6 with the OWN engine (eng.py), on the script's populations
# (population generators copied from absfold_check.py; answers from eng.py, never from part()).
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from drills import *
Dg = [str(i) for i in range(10)]
def cnt(name, subs, a, b):
    d = [s for s in subs if a[s] != b[s]]
    print('  %-62s %4d of %5d %s' % (name, len(d), len(subs), sorted(d, key=lambda s: (len(s), s))[:3]))
    return len(d)
def P(n): return G(n, D)
def run(pat, subs, forms, dom, opt_is_loop=True):
    out = {f: {} for f in forms}
    for s in subs:
        ctx = Ctx(pat, s, dom, 'F1', opt_is_loop)
        assert ctx.ok, s
        for f, fn in forms.items(): out[f][s] = fn(ctx)
    return out
def ctxs(pat, s, dom, oil=True): return Ctx(pat, s, dom, 'F1', oil)
S5, T37 = lt(5), rng(3, 7)

# ---------- (RZ), (Z1), (ZD a)
RZp = Seq(P('k'), Rep(Seq(L(';'), P('h')), 0, None))
SUBJ_RZ = [k + ''.join(';' + h for h in hs) for k in Dg for n in range(3) for hs in itertools.product(Dg, repeat=n)]
dom = {'h': Dg, 'k': Dg}
rec = lambda hc=None, hv=None, md='plain': (lambda c: record(c, [('h', hc, hv, S5), ('k', None, None, T37)], md))
ampf = lambda hc=None, hv=None, md='plain': (lambda c: amp(c, [('h', hc, hv, S5), ('k', None, None, T37)], md))
F = {'AR': rec(), 'today': rec(md='today'), '&': ampf(), 'h?': rec('mark'), 'h?&': ampf('mark'),
     'h=9': rec('def', '9'), 'h=9&': ampf('def', '9'), 'h=0': rec('def', '0'), 'today h=9': rec('def', '9', 'today'),
     'A2v': rec(md='A2v'), 'A2v&': ampf(md='A2v'), 'A2z': rec(md='A2z'), 'A2m': rec(md='A2m'), 'A2m&': ampf(md='A2m'),
     'Z1': lambda c: single(c, 'h', None, None, S5), 'Z1 today': lambda c: single(c, 'h', None, None, S5, 'today')}
R = run(RZp, SUBJ_RZ, F, dom)
print('(RZ) 1,110')
cnt('AR vs today [quoted 5]', SUBJ_RZ, R['today'], R['AR'])
cnt('AR record vs & [0]', SUBJ_RZ, R['AR'], R['&'])
cnt('h? record vs & [0]', SUBJ_RZ, R['h?'], R['h?&'])
cnt('h? vs today [0]', SUBJ_RZ, R['h?'], R['today'])
cnt('h=9 vs today(h=9) i.e. (ZD a) [5]', SUBJ_RZ, R['h=9'], R['today h=9'])
cnt('h=9 rec vs & [0]', SUBJ_RZ, R['h=9'], R['h=9&'])
cnt('h=0 vs today [0]', SUBJ_RZ, R['h=0'], R['today'])
cnt('all A2v rec vs & [5]', SUBJ_RZ, R['A2v'], R['A2v&'])
cnt('all A2m rec vs & [0]', SUBJ_RZ, R['A2m'], R['A2m&'])
cnt('all A2z vs today', SUBJ_RZ, R['A2z'], R['today'])
cnt('all A2m vs today', SUBJ_RZ, R['A2m'], R['today'])
print('  "9": AR %s today %s h? %s A2v %s A2z %s A2m %s' % tuple(R[k]['9'] for k in ('AR', 'today', 'h?', 'A2v', 'A2z', 'A2m')))
print('(Z1)'); cnt('(h: <5) AR vs today [10]', SUBJ_RZ, R['Z1'], R['Z1 today'])

# ---------- (ZN)
ZNp = Seq(P('c'), Rep(Seq(L(';'), P('h'), Rep(Seq(L(':'), P('k')), 0, None)), 0, None))
ITEMS = [(h, ks) for h in "0459" for ks in [(), ("2",), ("9",), ("3", "6"), ("6", "0")]]
SUBJ_ZN = [c + "".join(";%s%s" % (h, "".join(":" + k for k in ks)) for h, ks in its)
           for c in "023578" for n in range(3) for its in itertools.product(ITEMS, repeat=n)]
Cs, Hs, Ks = rng(3, 7), rng(0, 4), rng(2, 6)
parts = [('c', None, None, Cs), ('h', None, None, Hs), ('k', None, None, Ks)]
def pooled(c):
    ks = [e[2] for e in c.ev if e[0] == 'cap' and e[1] == 'k']
    return single(c, 'c', None, None, Cs) and single(c, 'h', None, None, Hs) and bool(ks) and all(Ks(c.env)(k) for k in ks)
R = run(ZNp, SUBJ_ZN, {'AR': lambda c: record(c, parts), 'today': lambda c: record(c, parts, 'today'),
                       '&': lambda c: amp(c, parts), 'pool': pooled}, {'c': Dg, 'h': Dg, 'k': Dg})
print('(ZN) %d' % len(SUBJ_ZN))
cnt('AR vs today [69]', SUBJ_ZN, R['AR'], R['today'])
cnt('record vs & per pass [0]', SUBJ_ZN, R['AR'], R['&'])
cnt('record vs & pooled [48]', SUBJ_ZN, R['AR'], R['pool'])

# ---------- (NL)
NLp = Rep(Seq(P('h'), L(':'), Rep(Seq(P('k'), L(',')), 0, None), L(';')), 0, None)
SUBJ_NL = ["".join("%s:%s;" % (a, "".join(k + "," for k in ks)) for a, ks in its) for n in range(3)
           for its in itertools.product([("4", ()), ("4", ("9",)), ("5", ()), ("5", ("3",)), ("5", ("2",)),
                                         ("5", ("3", "4")), ("6", ("0", "1")), ("5", ("4", "2"))], repeat=n)]
JNT = lambda env: (lambda t: isnum(t[0]) and isnum(t[1]) and (int(t[0]), int(t[1])) >= (5, 3))
J = lambda hc, kc, md='plain': (lambda c: joint(c, [('h', hc, None), ('k', kc, None)], JNT, md))
R = run(NLp, SUBJ_NL, {'AR': J(None, None), 'jcfold(vacuous)': J(None, None, 'A2v'), 'jcfold2(12:45)': J(None, None, 'today'),
                       'k?': J(None, 'mark'), 'h?k?': J('mark', 'mark')}, {'h': Dg, 'k': Dg})
print('(NL) %d' % len(SUBJ_NL))
cnt('AR vs jcfold [19]', SUBJ_NL, R['AR'], R['jcfold(vacuous)'])
cnt('AR vs jcfold2 [9]', SUBJ_NL, R['AR'], R['jcfold2(12:45)'])
cnt('(h, k?) vs jcfold2 [1: 72 of 73 equal]', SUBJ_NL, R['k?'], R['jcfold2(12:45)'])
cnt('(h?, k?) vs jcfold2 [0]', SUBJ_NL, R['h?k?'], R['jcfold2(12:45)'])

# ---------- (ZJ), (ZJ-E)
print('(ZJ) zero-pass subjects of (RZ)')
zs = Dg
ZJ = [("((h, k): >= (5, 3))", lambda t: t[0] != "x" and (int(t[0]), int(t[1])) >= (5, 3)),
      ("((k, h): >= (5, 3))", lambda t: t[0] != "x" and (int(t[1]), int(t[0])) >= (5, 3)),
      ("((h, k): (0|1|2, 3|4) | (5, 5))", lambda t: (t[0] in "012" and t[1] in "34") or (t[0] == "5" and t[1] == "5")),
      ("((h, k): (\"x\", 3) | (0, 5))", lambda t: (t[0] == "x" and t[1] == "3") or (t[0] == "0" and t[1] == "5")),
      ("((h, k): < (0, 3))", lambda t: t[0] != "x" and (int(t[0]), int(t[1])) < (0, 3))]
for name, Rf in ZJ:
    for dn, dd in (('\\d', Dg), ('\\d+x', Dg + ['x']), ('ANY', ANY)):
        safe = lambda t, Rf=Rf: (t[0] == 'x' or isnum(t[0])) and Rf(t) if t[0] != '' else False
        a = [s for s in zs if joint(ctxs(RZp, s, {'h': dd, 'k': Dg}), [('h', None, None), ('k', None, None)], lambda env: safe)]
        b = [s for s in zs if joint(ctxs(RZp, s, {'h': dd, 'k': Dg}), [('h', 'mark', None), ('k', None, None)], lambda env: safe)]
        print('  %-34s dom %-4s unmarked holds %s ; h? holds %s' % (name, dn, a, b))
c3 = ctxs(RZp, '3', {'h': ANY, 'k': Dg})
c3f2 = Ctx(RZp, '3', {'h': ANY, 'k': Dg}, 'F2')
E = lambda env: (lambda t: False)
for nm, cc in (('F1', c3), ('F2', c3f2)):
    print('  (ZJ-E) %s: (h?: <0, k: 3) %s ; ((h?, k): (<0, 3)) %s ; ((h?, k): < (0, 0)) %s ; unmarked %s %s %s' % (
        nm, record(cc, [('h', 'mark', None, lt(0)), ('k', None, None, eq('3'))]),
        joint(cc, [('h', 'mark', None), ('k', None, None)], E),
        joint(cc, [('h', 'mark', None), ('k', None, None)], lambda env: lambda t: isnum(t[0]) and (int(t[0]), int(t[1])) < (0, 0)),
        record(cc, [('h', None, None, lt(0)), ('k', None, None, eq('3'))]),
        joint(cc, [('h', None, None), ('k', None, None)], E),
        joint(cc, [('h', None, None), ('k', None, None)], lambda env: lambda t: isnum(t[0]) and (int(t[0]), int(t[1])) < (0, 0))))

# ---------- (ZE)
ZEp = Seq(P('a'), L('-'), P('k'), Rep(Seq(L(';'), P('h')), 0, None))
SUBJ_ZE = ["%s-%s" % (a, k) + "".join(";" + h for h in hs) for a in Dg for k in Dg for n in range(3)
           for hs in itertools.product(Dg, repeat=n)]
C2 = lambda env: (lambda t, A=int(env['a']): isnum(t[0]) and isnum(t[1]) and (int(t[0]), int(t[1])) < (A, 0))
out = {k: {} for k in ('C1', 'C1&', 'C2', 'C2rows', 'C1F1', 'C2F1', 'C1F2')}
for s in SUBJ_ZE:
    c = ctxs(ZEp, s, {'h': Dg, 'k': Dg, 'a': Dg}); c2 = Ctx(ZEp, s, {'h': Dg, 'k': Dg, 'a': Dg}, 'F2')
    p1 = lambda hc: [('h', hc, None, lt_label('a')), ('k', None, None, eq('3'))]
    out['C1'][s] = record(c, p1(None)); out['C1&'][s] = amp(c, p1(None))
    out['C2'][s] = joint(c, [('h', None, None), ('k', None, None)], C2)
    # hand expansion of < ($a, 0) into rows: (h: <$a) | (h: $a, k: <0)
    out['C2rows'][s] = single(c, 'h', None, None, lt_label('a')) or record(c, [('h', None, None, lambda env: (lambda t: t == env['a'])), ('k', None, None, lt(0))])
    out['C1F1'][s] = record(c, p1('mark')); out['C2F1'][s] = joint(c, [('h', 'mark', None), ('k', None, None)], C2)
    out['C1F2'][s] = record(c2, p1('mark'))
A0 = [s for s in SUBJ_ZE if s.startswith('0-')]
print('(ZE) %d; a=0: %d' % (len(SUBJ_ZE), len(A0)))
cnt('C1 record vs & [0]', SUBJ_ZE, out['C1'], out['C1&'])
cnt('C2 joint vs rows [0]', SUBJ_ZE, out['C2'], out['C2rows'])
cnt('a=0 C1 vs C2 unmarked [0]', A0, out['C1'], out['C2'])
cnt('a=0 C1 vs C2 F1 [0]', A0, out['C1F1'], out['C2F1'])
cnt('a=0 C1 vs C2 F2 [1]', A0, out['C1F2'], out['C2F1'])

# ---------- (ZD b) and (ZD c)
P2 = Seq(P('k'), Rep(Seq(L('-'), Rep(Seq(L(';'), P('h')), 0, None)), 0, 1))
for dv in (None, '9', '2'):
    r = [record(ctxs(P2, s, dom), [('h', 'def' if dv else None, dv, S5), ('k', None, None, T37)]) for s in ('5', '5-')]
    print('(ZD b) h%s: "5" %s "5-" %s' % ('' if dv is None else ' = ' + dv, *r))
PL = Rep(Seq(P('h'), Rep(Seq(L(':'), P('m')), 0, 1), L(',')), 0, None)
GE53 = lambda env: (lambda t: isnum(t[0]) and isnum(t[1]) and (int(t[0]), int(t[1])) >= (5, 3))
SUBJ_L = [""] + ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its) for n in (1, 2)
                 for its in itertools.product([(h, m) for h in "456" for m in (None, "0", "3")], repeat=n)]
R = run(PL, SUBJ_L, {'AR': lambda c: joint(c, [('h', None, None), ('m', 'def', '0')], GE53),
                     'h?': lambda c: joint(c, [('h', 'mark', None), ('m', 'def', '0')], GE53)}, {'h': Dg, 'm': Dg})
Rt = run(PL, SUBJ_L, {'today': lambda c: joint(c, [('h', None, None), ('m', 'def', '0')], GE53, 'today')}, {'h': Dg, 'm': Dg}, False)
print('(ZD c) %d' % len(SUBJ_L)); cnt('AR vs today [1]', SUBJ_L, R['AR'], Rt['today']); cnt('h? vs today [0]', SUBJ_L, R['h?'], Rt['today'])

# ---------- (OP)
OPp = Rep(Seq(G('h', Rep(D, 1, None)), Rep(Seq(L(':'), G('m', Seq(D, D))), 0, 1), L(',')), 0, None)
OP_ITEMS = [(h, m) for h in ("3", "12") for m in (None, "15", "45")]
SUBJ_OP = ["".join("%s%s," % (h, "" if m is None else ":" + m) for h, m in its)
           for n in range(4) for its in itertools.product(OP_ITEMS, repeat=n)]
DH = [str(i) for i in range(13)]; DM2 = ["%02d" % i for i in range(100)]
od = {'h': DH, 'm': DM2}
pp = lambda hc, hv, mc, mv: [('h', hc, hv, lt(10)), ('m', mc, mv, lt(30))]
def pooledOP(c):
    ms = [e[2] for e in c.ev if e[0] == 'cap' and e[1] == 'm']
    return single(c, 'h', None, None, lt(10)) and bool(ms) and all(int(m) < 30 for m in ms)
R = run(OPp, SUBJ_OP, {'AR': lambda c: record(c, pp(None, None, None, None)), '&': lambda c: amp(c, pp(None, None, None, None)),
                       'pool': pooledOP, 'h?m?': lambda c: record(c, pp('mark', None, 'mark', None)),
                       'h?m=0': lambda c: record(c, pp('mark', None, 'def', '0')), 'hm=0': lambda c: record(c, pp(None, None, 'def', '0')),
                       'A2v': lambda c: record(c, pp(None, None, None, None), 'A2v'), 'A2m': lambda c: record(c, pp(None, None, None, None), 'A2m')}, od)
Rt = run(OPp, SUBJ_OP, {'today': lambda c: record(c, pp(None, None, None, None), 'today'),
                        'A2z': lambda c: record(c, pp(None, None, None, None), 'A2z')}, od, False)
print('(OP) %d' % len(SUBJ_OP))
cnt('AR vs today [1]', SUBJ_OP, R['AR'], Rt['today']); cnt('rec vs & per pass [0]', SUBJ_OP, R['AR'], R['&'])
cnt('rec vs & pooled [8]', SUBJ_OP, R['AR'], R['pool'])
for f, q in (('h?m?', 11), ('h?m=0', 11), ('hm=0', 12), ('A2v', 0), ('A2m', 11)):
    cnt('today vs %s [%d]' % (f, q), SUBJ_OP, Rt['today'], R[f])
cnt('today vs A2z [0]', SUBJ_OP, Rt['today'], Rt['A2z'])

# ---------- (UP)
UPp = Rep(Seq(P('h'), Rep(Seq(L('-'), Rep(Seq(P('k'), L(',')), 0, None)), 0, 1), L(';')), 0, None)
UP_ITEMS = [(h, ks) for h in "349" for ks in [None, (), ("2",), ("7",), ("2", "7")]]
SUBJ_UP = ["".join("%s%s;" % (h, "" if ks is None else "-" + "".join(k + "," for k in ks)) for h, ks in its)
           for n in range(3) for its in itertools.product(UP_ITEMS, repeat=n)]
up = lambda kc: [('h', None, None, S5), ('k', kc, None, S5)]
R = run(UPp, SUBJ_UP, {'AR': lambda c: record(c, up(None)), '&': lambda c: amp(c, up(None)),
                       'k?': lambda c: record(c, up('mark')), '&k?': lambda c: amp(c, up('mark'))}, dom)
Rt = run(UPp, SUBJ_UP, {'today': lambda c: record(c, up(None), 'today')}, dom, False)
print('(UP) %d' % len(SUBJ_UP))
cnt('AR vs today [15]', SUBJ_UP, R['AR'], Rt['today']); cnt('rec vs & [0]', SUBJ_UP, R['AR'], R['&'])
cnt('k? rec vs & [0]', SUBJ_UP, R['k?'], R['&k?'])

# ---------- (DL)
H2 = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
DLp = Rep(Seq(G('h', Rep(D, 1, 2)), Rep(Seq(L(':'), G('m', Seq(D, D))), 0, 1), L(',')), 0, None)
SUBJ_DL = ["".join(c + "," for c in combo) for n in range(4) for combo in itertools.product(["9", "10", "11", "12", "9:45", "9:15", "10:30", "11:30"], repeat=n)]
BTW = lambda env: (lambda t: isnum(t[0]) and isnum(t[1]) and (9, 30) <= (int(t[0]), int(t[1])) <= (11, 0))
R = run(DLp, SUBJ_DL, {'AR': lambda c: joint(c, [('h', None, None), ('m', 'def', '0')], BTW),
                       'h?': lambda c: joint(c, [('h', 'mark', None), ('m', 'def', '0')], BTW)}, {'h': H2, 'm': DM2})
Rt = run(DLp, SUBJ_DL, {'today': lambda c: joint(c, [('h', None, None), ('m', 'def', '0')], BTW, 'today')}, {'h': H2, 'm': DM2}, False)
print('(DL) %d' % len(SUBJ_DL)); cnt('AR vs today [1]', SUBJ_DL, R['AR'], Rt['today']); cnt('h? vs today [0]', SUBJ_DL, R['h?'], Rt['today'])

# ---------- (LI) and (D1) looped default
LIp = Rep(Seq(P('n'), L(',')), 0, None)
LIk = ["".join(x + "," for x in c) for k in range(4) for c in itertools.product(Dg, repeat=k)]
R = run(LIp, LIk, {'plain': lambda c: single(c, 'n', None, None, S5), 'A2m': lambda c: single(c, 'n', None, None, S5, 'A2m'),
                   'n?': lambda c: single(c, 'n', 'mark', None, S5),
                   'A2m<0': lambda c: single(c, 'n', None, None, lt(0), 'A2m'), 'n?<0': lambda c: single(c, 'n', 'mark', None, lt(0)),
                   'A2v<0': lambda c: single(c, 'n', None, None, lt(0), 'A2v'),
                   'n=0': lambda c: single(c, 'n', 'def', '0', S5), 'n=9': lambda c: single(c, 'n', 'def', '9', S5)}, {'n': Dg})
print('(LI) %d' % len(LIk))
cnt('plain vs all A2m [1]', LIk, R['plain'], R['A2m']); cnt('all A2m vs n? [0]', LIk, R['A2m'], R['n?'])
cnt('all((n:<0)) A2m vs (n?:<0) [note: 1]', LIk, R['A2m<0'], R['n?<0'])
cnt('all((n:<0)) A2v vs (n?:<0)', LIk, R['A2v<0'], R['n?<0'])
cnt('(n=0) vs plain [1]', LIk, R['n=0'], R['plain']); cnt('(n=9) vs plain [0]', LIk, R['n=9'], R['plain'])

# ---------- (D1)
T2 = Seq(G('h', Rep(D, 1, 2)), Rep(Seq(L(':'), G('m', Seq(D, D))), 0, 1))
SUBJ_T2 = H2 + [h + ":" + m for h in H2 for m in DM2]
for v in ('0', '45', '00'):
    same = sum(single(c, 'm', 'def', v, lt(30)) == single(c, 'm', None, None, lt(30)) for c in (ctxs(T2, s, {'m': DM2}) for s in SUBJ_T2))
    print('(D1) m = %s same on %d of %d [11,000 / 11,110 / 11,110]' % (v, same, len(SUBJ_T2)))

# ---------- (OG) 4G.6 (4): occurrences / some with a marked g
