# Independent evaluator of predicates_draft.md rev 24 §R.1, written from the TEXT only.
# A program is a pattern with conditions as pieces; backtracking in PCRE preference order.
# Node = function(text, pos, st) -> generator of (pos, st). st = dict (labels) + '#cur' pass collector + ('#L',id) tables.
import itertools, re as _re

def lit(s):
    def m(t, p, st):
        if t.startswith(s, p): yield p+len(s), st
    return m
def cls(pred):
    def m(t, p, st):
        if p < len(t) and pred(t[p]): yield p+1, st
    return m
DIG = cls(str.isdigit)
ANY = cls(lambda c: True)
def seq(*ns):
    def m(t, p, st, i=0):
        if i == len(ns): yield p, st; return
        for p2, st2 in ns[i](t, p, st):
            yield from m(t, p2, st2, i+1)
    return lambda t, p, st: m(t, p, st)
def alt(*ns):
    def m(t, p, st):
        for n in ns: yield from n(t, p, st)
    return m
def grp(name, n):
    def m(t, p, st):
        for p2, st2 in n(t, p, st):
            s = dict(st2); s[name] = t[p:p2]
            if '#cur' in s: c = dict(s['#cur']); c[name] = t[p:p2]; s['#cur'] = c
            yield p2, s
    return m
_lid = itertools.count()
def rep(n, lo=0, hi=None, greedy=True, lid=None):
    lid = next(_lid) if lid is None else lid
    key = ('#L', lid)
    def it(t, p, st, k):
        def more():
            if hi is not None and k >= hi: return
            outer = st.get('#cur', None)
            s0 = dict(st); s0['#cur'] = {}
            for p2, s2 in n(t, p, s0):
                if p2 == p and k >= lo:  # empty iteration: PCRE stops the loop after it
                    continue
                s3 = dict(s2); cur = s3.pop('#cur')
                s3[key] = s3.get(key, ()) + (cur,)
                if outer is not None:
                    o = dict(outer); o.update(cur); s3['#cur'] = o
                yield from it(t, p2, s3, k+1)
        def stop():
            if k >= lo: yield p, st
        if greedy: yield from more(); yield from stop()
        else: yield from stop(); yield from more()
    def m(t, p, st):
        s = dict(st)
        if key not in s: s[key] = ()
        yield from it(t, p, s, 0)
    m.lid = lid
    return m
def opt(n, greedy=True): return rep(n, 0, 1, greedy)
def atomic(n):
    def m(t, p, st):
        for r in n(t, p, st): yield r; return
    return m
def look(n, neg=False):
    def m(t, p, st):
        for p2, s2 in n(t, p, st):
            if not neg: yield p, s2
            return
        if neg: yield p, st
    return m
def END(t, p, st):
    if p == len(t): yield p, st
# ---- conditions (two-valued; a test on an absent label fails) ----
def cond(f):
    def m(t, p, st):
        if f(st): yield p, st
    return m
def NOT(c):  # negative lookahead around the test
    return look(c, neg=True)
def cor(*cs): return alt(*cs)
NUM = _re.compile(r'0|[1-9]\d*\Z')
def isnum(v): return v is not None and _re.fullmatch(r'0|[1-9]\d*', v) is not None
def lt(n): return lambda v: isnum(v) and int(v) < n
def gt(n): return lambda v: isnum(v) and int(v) > n
def ge(n): return lambda v: isnum(v) and int(v) >= n
def between(a, b): return lambda v: isnum(v) and a <= int(v) <= b
def eq(s): return lambda v: v == s
def comp(S): return lambda v: not S(v)     # set complement over every text (present value)
def T(label, S, default=None):  # (label = default: S)
    def f(st):
        v = st.get(label, default)
        if v is None: return False
        return S(v)
    return cond(f)
def TT(labels, S, defaults=None):  # joint ((h, m): S) S on a tuple of values
    defaults = defaults or {}
    def f(st):
        vs = tuple(st.get(l, defaults.get(l)) for l in labels)
        if any(v is None for v in vs): return False
        return S(vs)
    return cond(f)
# ---- operators on patterns ----
def AND(P, Q):  # paths of P whose stretch Q matches whole; labels joined; P outer
    def m(t, p, st):
        for p2, s2 in P(t, p, st):
            sub = t[p:p2]
            for _, sq in seq(Q, END)(sub, 0, {}):
                s3 = dict(s2)
                for k, v in sq.items():
                    if isinstance(k, str) and k.startswith('#'): continue
                    if isinstance(k, tuple): s3[k] = v; continue
                    s3[k] = v
                yield p2, s3
    return m
def ANDc(P, *cs): return seq(P, *cs)   # P & condition: condition placed after P
def DIFF(A, B):  # A & !B : no path of B over A's stretch
    def m(t, p, st):
        for p2, s2 in A(t, p, st):
            sub = t[p:p2]
            if not any(True for _ in seq(B, END)(sub, 0, {})):
                yield p2, s2
    return m
# group questions over the pass table of loop L (labels set in loop: per-pass; others: outer value)
def _rows(st, L):
    passes = st.get(('#L', L.lid), ())
    looped = set().union(*[set(c) for c in passes]) if passes else set()
    base = {k: v for k, v in st.items() if isinstance(k, str) and not k.startswith('#')}
    rows = []
    for c in passes:
        r = {k: v for k, v in base.items() if k not in looped and k not in LOOPED_NAMES.get(L.lid, ())}
        r.update(c); rows.append(r)
    return rows
LOOPED_NAMES = {}
def _holds(c, row):
    return any(True for _ in c('', 0, row))
def some(L, c): return cond(lambda st: any(_holds(c, r) for r in _rows(st, L)))
def none(L, c): return cond(lambda st: not any(_holds(c, r) for r in _rows(st, L)))
def exactly(L, n, c): return cond(lambda st: sum(_holds(c, r) for r in _rows(st, L)) == n)
# ---- modes ----
def labels(st): return {k: v for k, v in st.items() if isinstance(k, str) and not k.startswith('#')}
def whole(prog, t):
    for p, st in seq(prog, END)(t, 0, {}): return labels(st)
    return None
def first_at(prog, t, p, nonempty=False):
    for p2, st in prog(t, p, {}):
        if nonempty and p2 == p: continue
        return p2, labels(st)
    return None
def searched(prog, t):
    for s in range(len(t)+1):
        r = first_at(prog, t, s)
        if r: return (t[s:r[0]], s, r[1])
    return None
def findall(prog, t):
    out = []; s = 0; ne = False
    while s <= len(t):
        r = first_at(prog, t, s, nonempty=ne)
        if r is None:
            if ne: ne = False; s += 1; continue
            s += 1; continue
        out.append((t[s:r[0]], s, r[1]))
        ne = (r[0] == s); s = r[0]
    return out
def fmt(r):
    return None if r is None else r
def texts(alpha, maxlen, minlen=0):
    for n in range(minlen, maxlen+1):
        for tup in itertools.product(alpha, repeat=n): yield ''.join(tup)
def ANDnl(P, Q):  # P & (0: Q): Q tests the whole stretch, its labels are not joined
    def m(t, p, st):
        for p2, s2 in P(t, p, st):
            if any(True for _ in seq(Q, END)(t[p:p2], 0, {})): yield p2, s2
    return m
