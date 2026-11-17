import sys; sys.path.insert(0, '.')
from ev import *

def strings(alpha, n):
    out, cur = [""], [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
DIG4 = strings("0129", 4); DSP = strings("129 ", 5); RG3 = strings("37;", 5); TP5 = strings("905: ", 5)
AHPOOL = strings("abc37", 3); OCCPOOL = strings("12 x", 4); SVPOOL = strings("37x ", 4)
KHPOOL = [k + "".join(";" + x for x in t) for k in "0123456789" for t in [()] + [(a,) for a in "0123456789"] + [(a, b) for a in "0123456789" for b in "0123456789"]]
def first(xs): return min(xs, key=lambda x: (len(x), x)) if xs else None
def W(p, t):
    r = whole(p, t); return None if r is None else tuple(sorted(r.items()))
def S(p, t):
    r = searched(p, t); return None if r is None else (r[0], r[1], tuple(sorted(r[2].items())))
def F(p, t): return tuple((x[0], x[1], tuple(sorted(x[2].items()))) for x in findall(p, t))
def strip(v, lab):
    if lab: return v
    if v is None: return None
    if isinstance(v, tuple) and v and isinstance(v[0], tuple) and len(v[0]) == 3: return tuple(x[:2] for x in v)
    if isinstance(v, tuple) and len(v) == 3 and isinstance(v[0], str): return v[:2]
    return True
def cmp(tag, p1, p2, pool, lab=True):
    res = []
    for mode in (W, S, F):
        d = [t for t in pool if strip(mode(p1, t), lab) != strip(mode(p2, t), lab)]
        res.append('%d (first %r)' % (len(d), first(d)))
    print(tag, ' / '.join(res), 'of', len(pool))
def admits(tag, base, more, pool):
    w = [t for t in pool if whole(more, t) is not None and whole(base, t) is None]
    s = [t for t in pool if searched(more, t) is not None and searched(base, t) is None]
    print(tag, 'admits WHOLE %d (first %r) SEARCHED %d (first %r)' % (len(w), first(w), len(s), first(s)), 'of', len(pool))

dplus = rep(DIG, 1)
B = grp('l', seq(DIG, DIG)); A = seq(grp('l', DIG), DIG)
P = seq(grp('a', rep(DIG, 1)), grp('b', rep(DIG, 1)))
Q = seq(grp('c', dplus), grp('d', dplus))
which = sys.argv[1] if len(sys.argv) > 1 else 'all'
def on(k): return which in ('all', k)
if on('D1'):
    cmp('D1 distrib', ANDc(alt(B, A), T('l', lt(20))), alt(ANDc(B, T('l', lt(20))), ANDc(A, T('l', lt(20)))), DIG4)
if on('D4'):
    cmp('D4 NOT vs complement', ANDc(P, NOT(T('a', eq('1')))), DIFF(P, ANDc(P, T('a', eq('1')))), DIG4)
if on('D2'):
    admits('D2 NOT', ANDc(P, NOT(T('b', eq('2')))), ANDc(P, NOT(seq(T('b', eq('2')), T('a', eq('1'))))), DIG4)
    admits('D2 compl', DIFF(P, ANDc(P, T('b', eq('2')))), DIFF(P, ANDc(P, T('b', eq('2')), T('a', eq('1')))), DIG4)
    admits('D2 top', P, ANDc(P, T('a', eq('1'))), DIG4)
    admits('D2 branch', ANDc(alt(B, A), T('l', lt(10))), ANDc(alt(ANDc(B, T('l', gt(50))), A), T('l', lt(10))), DIG4)
if on('E1'):
    U = seq(grp('b', rep(DIG, 1)), opt(grp('a', DIG)))
    kleene = T('a', comp(lt(5)))   # Kleene NOT: unknown on absent -> dropped
    cmp('E1 2v vs Kleene', ANDc(U, NOT(T('a', lt(5)))), ANDc(U, kleene), DSP)
if on('E5'):
    c = cor(T('a', eq('1')), T('c', eq('1')))
    cmp('E5 left vs right outer (labels)', ANDc(AND(P, Q), c), ANDc(AND(Q, P), c), DSP)
    cmp('E5 left vs right outer (no labels)', ANDc(AND(P, Q), c), ANDc(AND(Q, P), c), DSP, lab=False)
    cmp('E5 swap cond order', ANDc(AND(P, Q), c), ANDc(AND(P, Q), cor(T('c', eq('1')), T('a', eq('1')))), DSP)
if on('E14'):
    cmp('E14 atomic vs plain', ANDc(atomic(alt(B, A)), T('l', lt(20))), ANDc(alt(B, A), T('l', lt(20))), DSP)
if on('E8'):
    eng = ANDc(alt(ANDc(B, T('l', gt(50))), A), T('l', lt(10)))
    naive = ANDc(alt(B, A), T('l', gt(50)), T('l', lt(10)))
    cmp('E8 engine vs naive', eng, naive, DIG4)
    cmp('E8b atomic(P&a1) vs first-row-then-filter', atomic(ANDc(P, T('a', eq('1')))), ANDc(atomic(P), T('a', eq('1'))), DSP)
if on('E7'):
    L1 = rep(seq(grp('h', DIG), lit(';')))
    item = ANDc(seq(grp('h', DIG), lit(';')), T('h', lt(5)))
    cmp('E7 bare vs every-pass', ANDc(L1, T('h', lt(5))), rep(item, 1), RG3)
    L1b = rep(seq(grp('h', DIG), lit(';'))); LOOPED_NAMES[L1b.lid] = {'h'}
    W1b = ANDc(L1b, some(L1b, T('h', lt(5))), none(L1b, NOT(T('h', lt(5)))))
    cmp('W1a new vs W1b new', rep(item, 1), W1b, RG3)
if on('E12'):
    R1 = rep(seq(opt(grp('h', DIG)), lit(';'))); LOOPED_NAMES[R1.lid] = {'h'}
    cmp('E12 NOT some vs none', ANDc(R1, NOT(some(R1, T('h', lt(5))))), ANDc(R1, none(R1, T('h', lt(5)))), RG3)
    cmp('E12 NOT some vs none(NOT)', ANDc(R1, NOT(some(R1, T('h', lt(5))))), ANDc(R1, none(R1, NOT(T('h', lt(5))))), RG3)
    # W2 controls: bare REP & (h=0: <5) vs REP & occurs.none(NOT (h=0:<5))
    cmp('W2b control bare vs new', ANDc(R1, T('h', lt(5), default='0')), ANDc(R1, none(R1, NOT(T('h', lt(5), default='0')))), RG3)
    item2 = ANDc(seq(opt(grp('h', DIG)), lit(';')), T('h', lt(5), default='0'))
    cmp('W2a vs W2b new', rep(item2), ANDc(R1, none(R1, NOT(T('h', lt(5), default='0')))), RG3)
    item1c = ANDc(seq(opt(grp('h', DIG)), lit(';')), T('h', lt(5)))
    cmp('W1c vs W1d new', rep(item1c), ANDc(R1, some(R1, T('h', lt(5))), none(R1, NOT(T('h', lt(5))))), RG3)
    cmp('W1c(+) vs W1d new', rep(item1c, 1), ANDc(R1, some(R1, T('h', lt(5))), none(R1, NOT(T('h', lt(5))))), RG3)
    cmp('W5b vs W5b?', ANDc(R1, T('h', comp(lt(5)))), ANDc(R1, some(R1, T('h', comp(lt(5)))), none(R1, NOT(T('h', comp(lt(5)))))), RG3)
if on('E3'):
    HK = alt(seq(lit('a'), grp('h', DIG)), seq(lit('b'), grp('k', DIG)), lit('c'))
    # Kleene OR under NOT: NOT(U or U)=U -> dropped; NOT(F or U) = U dropped; holds only if both present-and-false
    def kl(st):
        h, k = st.get('h'), st.get('k')
        vh = None if h is None else lt(5)(h); vk = None if k is None else lt(5)(k)
        if vh is True or vk is True: return False
        if vh is None or vk is None: return False
        return True
    cmp('E3 one | vs Kleene OR', ANDc(HK, NOT(cor(T('h', lt(5)), T('k', lt(5))))), ANDc(HK, cond(kl)), AHPOOL)
if on('D5'):
    cmp('D5 law labels', ANDc(AND(dplus, P), T('a', eq('1'))), ANDc(ANDnl(dplus, P), T('a', eq('1'))), DIG4)
if on('KH'):
    KHl = rep(seq(lit(';'), grp('h', DIG))); KH = seq(grp('k', DIG), KHl); LOOPED_NAMES[KHl.lid] = {'h'}
    c = T('h', lt(5)); p = T('k', between(3, 7)); qq = T('k', lt(3))
    cmp('E15 else vs 2-arg', ANDc(KH, cor(seq(c, p), seq(NOT(c), qq))), ANDc(KH, cor(NOT(c), p)), KHPOOL)
    cmp('W4a control bare vs new', ANDc(KH, c, p), ANDc(KH, p, some(KHl, c), none(KHl, NOT(c))), KHPOOL)
    J = TT(('h', 'k'), lambda v: isnum(v[0]) and isnum(v[1]) and int(v[0]) > int(v[1]))
    print('KH holds WHOLE', sum(whole(ANDc(KH, cor(NOT(c), p)), t) is not None for t in KHPOOL))
if on('E13'):
    LA = seq(look(seq(rep(ANY, 0, None, greedy=False), DIG, DIG, lit(':'), grp('lm', seq(DIG, DIG)))),
             grp('h', rep(DIG, 1, 2)), opt(seq(lit(':'), DIG, DIG)))
    LA2 = seq(look(seq(rep(ANY, 0, None, greedy=False), DIG, DIG, lit(':'), seq(DIG, DIG))),
              grp('h', rep(DIG, 1, 2)), opt(seq(lit(':'), DIG, DIG)))
    cmp('E13 PCRE vs invisible', ANDc(LA, T('lm', ge(30))), ANDc(LA2, T('lm', ge(30))), TP5)
if on('T2'):
    t2 = seq(grp('h', rep(DIG, 1, 2)), opt(seq(lit(':'), grp('m', seq(DIG, DIG)))))
    def R930(vs):
        h, m = vs
        return isnum(h) and isnum(m) and (int(h), int(m)) >= (9, 30)
    q = ANDc(t2, TT(('h', 'm'), R930))
    cmp('E14b atomic(t2)&!q vs t2&!q', DIFF(atomic(t2), q), DIFF(t2, q), TP5)
    cmp('E6b', DIFF(t2, ANDc(t2, T('h', lt(0)))), t2, TP5)
    def rec_not(st):  # NOT (h:<9, m:<30): record = & of entries, two-valued
        return not (lt(9)(st['h']) if 'h' in st else False) or not (lt(30)(st['m']) if 'm' in st else False)
    joint = NOT(TT(('h', 'm'), lambda v: lt(9)(v[0]) and lt(30)(v[1])))
    cmp('E2 joint vs record', ANDc(t2, joint), ANDc(t2, NOT(seq(T('h', lt(9)), T('m', lt(30))))), TP5)
