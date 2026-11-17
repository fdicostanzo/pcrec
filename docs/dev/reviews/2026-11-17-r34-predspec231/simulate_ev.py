"""simulate lens: an independent evaluator written from predicates_draft.md rev 23.1 §R.1 TEXT only.
Read-only design check; no import of the lane engines."""
import itertools

T, F, U = 'T', 'F', 'U'

# ---------------- regex engine (PCRE preference order, pass tables) ----------------
class Lit:
    def __init__(s, chars): s.chars = chars
class Seq:
    def __init__(s, *xs): s.xs = xs
class Alt:
    def __init__(s, *xs): s.xs = xs
class Rep:
    _id = itertools.count()
    def __init__(s, x, lo, hi, greedy=True):
        s.x, s.lo, s.hi, s.greedy = x, lo, hi, greedy; s.id = next(Rep._id)
class Grp:
    def __init__(s, name, x): s.name, s.x = name, x

DIG = set('0123456789')
def L(c): return Lit(set(c))
def D(): return Lit(DIG)
def S(*cs): return Seq(*[L(c) if isinstance(c, str) else c for c in cs])

def m(n, t, i, ev):
    if isinstance(n, Lit):
        if i < len(t) and t[i] in n.chars: yield i + 1, ev
    elif isinstance(n, Seq):
        def go(k, i, ev):
            if k == len(n.xs): yield i, ev; return
            for j, e2 in m(n.xs[k], t, i, ev): yield from go(k + 1, j, e2)
        yield from go(0, i, ev)
    elif isinstance(n, Alt):
        for x in n.xs: yield from m(x, t, i, ev)
    elif isinstance(n, Grp):
        for j, e2 in m(n.x, t, i, ev): yield j, e2 + (('set', n.name, i, j),)
    elif isinstance(n, Rep):
        def go(k, i, ev):
            def more():
                if n.hi is None or k < n.hi:
                    for j, e2 in m(n.x, t, i, ev + (('pass', n.id),)):
                        if j == i and k >= n.lo: continue  # empty iteration stops
                        yield from go(k + 1, j, e2)
            if k < n.lo: yield from more(); return
            if n.greedy:
                yield from more(); yield i, ev
            else:
                yield i, ev; yield from more()
        yield from go(0, i, ev)

def label_loops(n, cur=None, out=None):
    """label -> id of the innermost repeating loop (hi>1) around it, or None (set-once)."""
    if out is None: out = {}
    if isinstance(n, (Seq, Alt)):
        for x in n.xs: label_loops(x, cur, out)
    elif isinstance(n, Grp):
        out[n.name] = cur; label_loops(n.x, cur, out)
    elif isinstance(n, Rep):
        label_loops(n.x, n.id if (n.hi is None or n.hi > 1) else cur, out)
    return out

def build_row(rx, t, ev):
    loops = label_loops(rx)
    row = {'once': {}, 'loopof': {}, 'passes': {}}
    for name, lid in loops.items():
        if lid is None: row['once'][name] = None
        else: row['loopof'][name] = lid; row['passes'].setdefault(lid, [])
    cur = {}
    for e in ev:
        if e[0] == 'pass':
            if e[1] in row['passes']: row['passes'][e[1]].append({})
        else:
            _, name, a, b = e
            lid = loops[name]
            if lid is None: row['once'][name] = t[a:b]
            else: row['passes'][lid][-1][name] = t[a:b]
    return row

def merge(r1, r2):
    r = {'once': dict(r1['once']), 'loopof': dict(r1['loopof']), 'passes': dict(r1['passes'])}
    for k, v in r2['once'].items():
        if r['once'].get(k) is None: r['once'][k] = v
    r['loopof'].update(r2['loopof']); r['passes'].update(r2['passes'])
    return r

# ---------------- programs ----------------
class Rx:
    def __init__(s, rx): s.rx = rx
class And:
    def __init__(s, *ops): s.ops = ops
class Or:   # program-level | : branch-major (branch-order)
    def __init__(s, *bs): s.bs = bs
class Comp:
    def __init__(s, p): s.p = p
class Cond: pass

def rows(p, t, s):
    """surviving rows at start s, in preference order, first row per end kept"""
    out, seen = [], set()
    for e, r in _rows(p, t, s):
        if e in seen: continue
        seen.add(e); out.append((e, r))
    return out

def _rows(p, t, s):
    if isinstance(p, Rx):
        for e, ev in m(p.rx, t, s, ()): yield e, build_row(p.rx, t, ev)
    elif isinstance(p, Or):
        for b in p.bs: yield from rows(b, t, s)
    elif isinstance(p, And):
        pats = [o for o in p.ops if not isinstance(o, (Comp, Cond))]
        comps = [o for o in p.ops if isinstance(o, Comp)]
        conds = [o for o in p.ops if isinstance(o, Cond)]
        assert pats, 'complement chain needs a non-complement operand'
        lead, rest = pats[0], pats[1:]
        for e, r in rows(lead, t, s):
            st = t[s:e]; ok = True
            for q in rest:
                w = whole(q, st)
                if w is None: ok = False; break
                r = merge(r, w)
            if not ok: continue
            if any(whole(c.p, st) is not None for c in comps): continue
            if all(c.ev(r) == T for c in conds): yield e, r
    else:
        raise TypeError(p)

def whole(p, txt):
    for e, r in rows(p, txt, 0):
        if e == len(txt): return r
    return None

def searched(p, t, start=0):
    for s in range(start, len(t) + 1):
        rs = rows(p, t, s)
        if rs: return s, rs[0][0], rs[0][1]
    return None

def findall(p, t):
    out, i = [], 0
    while i <= len(t):
        r = searched(p, t, i)
        if r is None: break
        s, e, _ = r; out.append((s, e))
        i = e if e > s else e + 1
    return out

def W(p, t): return whole(p, t) is not None
def Sr(p, t):
    r = searched(p, t); return None if r is None else (t[r[0]:r[1]], r[0])

# ---------------- conditions (three-valued) ----------------
def kand(vs):
    vs = list(vs)
    if F in vs: return F
    if U in vs: return U
    return T
def kor(vs):
    vs = list(vs)
    if T in vs: return T
    if U in vs: return U
    return F
def knot(v): return {T: F, F: T, U: U}[v]

def getval(row, name, pas):
    if name in row['once']: return row['once'][name]
    if pas is not None: return pas.get(name)
    raise KeyError(name)

def passes_for(row, names, pas, real=False):
    """for a test on looped labels: the pass rows; zero passes -> one null pass row (unless real)"""
    lids = {row['loopof'][n] for n in names if n in row['loopof']}
    if pas is not None or not lids: return [pas]
    assert len(lids) == 1, names
    ps = row['passes'][lids.pop()]
    if not ps and not real: return [{}]
    return ps

class C(Cond):
    """(name [= dflt]: S); S a predicate on text, or ('prog', P) / ('notprog', P) nested whole-value program"""
    def __init__(s, name, S, dflt=None): s.name, s.S, s.d = name, S, dflt
    def names(s): return [s.name]
    def test(s, v):
        if isinstance(s.S, tuple):
            k, P = s.S; h = whole(P, v) is not None
            return T if (h if k == 'prog' else not h) else F
        return T if s.S(v) else F
    def ev(s, row, pas=None):
        res = []
        for ps in passes_for(row, [s.name], pas):
            v = getval(row, s.name, ps)
            if v is None: v = s.d
            res.append(U if v is None else s.test(v))
        return kand(res)

class J(Cond):
    def __init__(s, names, R, dflts=None): s.ns, s.R, s.d = names, R, dflts or {}
    def names(s): return list(s.ns)
    def ev(s, row, pas=None):
        res = []
        for ps in passes_for(row, s.ns, pas):
            vs = []
            for n in s.ns:
                v = getval(row, n, ps)
                if v is None: v = s.d.get(n)
                vs.append(v)
            res.append(U if None in vs else (T if s.R(*vs) else F))
        return kand(res)

class CAnd(Cond):
    def __init__(s, *cs): s.cs = cs
    def names(s): return [n for c in s.cs for n in c.names()]
    def ev(s, row, pas=None):
        # a record on looped labels: per pass (same iteration), Kleene AND, then AND over passes
        lp = [n for n in s.names() if n in row['loopof']]
        if pas is None and lp:
            return kand(kand(c.ev(row, ps) for c in s.cs) for ps in passes_for(row, lp, None))
        return kand(c.ev(row, pas) for c in s.cs)
Rec = CAnd

class COr(Cond):
    def __init__(s, *cs): s.cs = cs
    def names(s): return [n for c in s.cs for n in c.names()]
    def ev(s, row, pas=None): return kor(c.ev(row, pas) for c in s.cs)

class CNot(Cond):
    def __init__(s, c): s.c = c
    def names(s): return s.c.names()
    def ev(s, row, pas=None): return knot(s.c.ev(row, pas))

class Some(Cond):
    def __init__(s, c): s.c = c
    def names(s): return s.c.names()
    def ev(s, row, pas=None):
        return T if any(s.c.ev(row, ps) == T for ps in passes_for(row, s.c.names(), None, real=True)) else F

class None_(Cond):
    def __init__(s, c): s.c = c
    def names(s): return s.c.names()
    def ev(s, row, pas=None):
        return F if any(s.c.ev(row, ps) == T for ps in passes_for(row, s.c.names(), None, real=True)) else T

class When(Cond):
    """filter form: keeps rows on which c & p is TRUE or which are not rows of x & c (c not TRUE)"""
    def __init__(s, c, p): s.c, s.p = c, p
    def names(s): return s.c.names() + s.p.names()
    def ev(s, row, pas=None):
        cv = s.c.ev(row, pas)
        if cv != T: return T
        return T if kand([cv, s.p.ev(row, pas)]) == T else F

# ---------------- sets ----------------
import os
CANON = os.environ.get("SIM_INT") is None
def num(v): return v.isdigit() and (not CANON or v == "0" or v[0] != "0")
def lt(k): return lambda v: num(v) and int(v) < k
def ge(k): return lambda v: num(v) and int(v) >= k
def between(a, b): return lambda v: num(v) and a <= int(v) <= b
def NOTS(S): return lambda v: not S(v)
ANY = lambda v: True
def tup_ge(a, b): return lambda h, m: num(h) and num(m) and (int(h), int(m)) >= (a, b)
def prod(Sh, Sm): return lambda h, m: Sh(h) and Sm(m)

def texts(alpha, n):
    for k in range(n + 1):
        for tt in itertools.product(alpha, repeat=k): yield ''.join(tt)
def both(p, t):
    w = 'HOLDS' if W(p, t) else 'FAILS'
    s = Sr(p, t)
    return w + ' / ' + ('FAILS' if s is None else 'HOLDS %r@%d' % s)

def cnt(p, pool):
    return sum(W(p, t) for t in pool), sum(Sr(p, t) is not None for t in pool)
def diff(p1, p2, pool, report=False):
    dw = [t for t in pool if W(p1, t) != W(p2, t)]
    ds = [t for t in pool if (Sr(p1, t) is None) != (Sr(p2, t) is None)]
    out = (len(dw), len(ds), dw[:1], ds[:1])
    if report:
        dr = [t for t in pool if Sr(p1, t) != Sr(p2, t)]
        out = out + (len(dr), dr[:1])
    return out

SVrx = Seq(Rep(Grp('h', D()), 0, 1), L('x')); SV = Rx(SVrx)
