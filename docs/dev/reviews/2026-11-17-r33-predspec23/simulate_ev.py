# Independent evaluator of rev 23 §R.1, written from the text (critic simulate).
import re as _re
T, F, U = 'T', 'F', 'U'
def kand(*vs):
    if F in vs: return F
    if U in vs: return U
    return T
def kor(*vs):
    if T in vs: return T
    if U in vs: return U
    return F
def knot(v): return {T: F, F: T, U: U}[v]

# ---------- tiny regex parser ----------
class P:
    def __init__(s, src): s.s = src; s.i = 0; s.rid = 0; s.holes = {}
def parse(src, holes=None):
    p = P(src); p.holes = holes or {}
    n = _alt(p, ())
    assert p.i == len(src), (src, p.i)
    return n
def _alt(p, loops):
    br = [_seq(p, loops)]
    while p.i < len(p.s) and p.s[p.i] == '|':
        p.i += 1; br.append(_seq(p, loops))
    return ('alt', br) if len(br) > 1 else br[0]
def _seq(p, loops):
    items = []
    while p.i < len(p.s) and p.s[p.i] not in '|)':
        items.append(_quant(p, loops))
    return ('seq', items)
def _quant(p, loops):
    # peek atom start, need loop id before parsing atom for capture paths
    save = p.i
    a = _atom(p, loops + (('?',),))  # placeholder
    if p.i < len(p.s) and p.s[p.i] in '*+?{':
        c = p.s[p.i]
        if c == '{':
            m = _re.match(r'\{(\d+)(?:,(\d*))?\}', p.s[p.i:]); p.i += m.end()
            lo = int(m.group(1)); hi = lo if m.group(2) is None else (int(m.group(2)) if m.group(2) else 10**9)
        else:
            p.i += 1; lo, hi = {'*': (0, 10**9), '+': (1, 10**9), '?': (0, 1)}[c]
        greedy = True
        if p.i < len(p.s) and p.s[p.i] == '?': p.i += 1; greedy = False
        p.rid += 1
        rid = p.rid
        # re-parse atom with real loop id
        end = p.i; p.i = save
        a = _atom(p, loops + ((rid, hi),))
        p.i = end
        return ('rep', a, lo, hi, greedy, rid)
    p.i = save
    return _atom(p, loops)
def _atom(p, loops):
    s = p.s; c = s[p.i]
    if s.startswith('${', p.i):
        j = s.index('}', p.i); name = s[p.i+2:j]; p.i = j + 1
        return ('hole', p.holes[name])
    if c == '(':
        if s.startswith('(?:', p.i): p.i += 3; n = _alt(p, loops); p.i += 1; return n
        if s.startswith('(?!', p.i): p.i += 3; n = _alt(p, loops); p.i += 1; return ('neg', n)
        if s.startswith('(?=', p.i): p.i += 3; n = _alt(p, loops); p.i += 1; return ('pos', n)
        m = _re.match(r'\(\?P?<(\w+)>', s[p.i:]); p.i += m.end()
        n = _alt(p, loops); p.i += 1
        return ('grp', m.group(1), n, tuple(l for l in loops if l != ('?',)))
    if c == '\\':
        d = s[p.i+1]; p.i += 2
        if d == 'd': return ('cls', lambda ch: ch.isdigit())
        if d == 'A': return ('bot',)
        if d == 'z': return ('eot',)
        if d == 's': return ('cls', lambda ch: ch.isspace())
        return ('cls', (lambda d: lambda ch: ch == d)(d))
    if c == '[':
        j = s.index(']', p.i); body = s[p.i+1:j]; p.i = j + 1
        if body == r'\s\S': return ('cls', lambda ch: True)
        neg = body.startswith('^')
        if neg: body = body[1:]
        chars = set(); k = 0
        while k < len(body):
            if body[k] == '\\' and body[k+1] == 'd': chars |= set('0123456789'); k += 2; continue
            if k + 2 < len(body) and body[k+1] == '-': chars |= {chr(x) for x in range(ord(body[k]), ord(body[k+2])+1)}; k += 3; continue
            chars.add(body[k]); k += 1
        return ('cls', (lambda chars, neg: lambda ch: (ch in chars) != neg)(chars, neg))
    if c == '.': p.i += 1; return ('cls', lambda ch: ch != '\n')
    p.i += 1
    return ('cls', (lambda c: lambda ch: ch == c)(c))

# ---------- backtracking matcher: yields (end, events) in preference order ----------
# events: tuple of ('cap', name, start, end, path) and ('pass', path)
def m(n, t, i, ev, path):
    k = n[0]
    if k == 'cls':
        if i < len(t) and n[1](t[i]): yield i + 1, ev
    elif k == 'seq':
        yield from mseq(n[1], 0, t, i, ev, path)
    elif k == 'alt':
        for b in n[1]: yield from m(b, t, i, ev, path)
    elif k == 'grp':
        for j, e in m(n[2], t, i, ev, path): yield j, e + (('cap', n[1], i, j, path),)
    elif k == 'rep':
        yield from mrep(n, t, i, ev, path, 0)
    elif k == 'bot':
        if i == 0: yield i, ev
    elif k == 'eot':
        if i == len(t): yield i, ev
    elif k == 'neg':
        for _ in m(n[1], t, i, ev, path): return
        yield i, ev
    elif k == 'pos':
        for j, e in m(n[1], t, i, ev, path): yield i, e; return
    elif k == 'hole':
        prog = n[1]
        for row in prog.rows_at(t, i):
            yield row.j, ev   # hole labels not exported (not needed)
def mseq(items, x, t, i, ev, path):
    if x == len(items): yield i, ev; return
    for j, e in m(items[x], t, i, ev, path):
        yield from mseq(items, x + 1, t, j, e, path)
def mrep(n, t, i, ev, path, cnt):
    _, body, lo, hi, greedy, rid = n
    def more():
        if cnt < hi:
            p2 = path + ((rid, cnt, i),)
            for j, e in m(body, t, i, ev, p2):
                e = e + (('pass', p2),)
                if j == i:   # empty iteration: loop stops here
                    if cnt + 1 >= lo: yield j, e
                    continue
                yield from mrep(n, t, j, e, path, cnt + 1)
    def stop():
        if cnt >= lo: yield i, ev
    if greedy: yield from more(); yield from stop()
    else: yield from stop(); yield from more()

def loops_of(n, acc=None):
    # name -> innermost enclosing loop id with hi>1 (or None)
    if acc is None: acc = {}
    k = n[0]
    if k == 'grp':
        rl = [l for l in n[3] if l[1] > 1]
        acc[n[1]] = rl[-1][0] if rl else None
        loops_of(n[2], acc)
    elif k in ('seq', 'alt'):
        for x in n[1]: loops_of(x, acc)
    elif k == 'rep': loops_of(n[1], acc)
    elif k in ('neg', 'pos'): loops_of(n[1], acc)
    return acc

class Row:
    def __init__(s, pat, t, i, j, ev):
        s.pat, s.t, s.i, s.j, s.ev = pat, t, i, j, ev
    @property
    def stretch(s): return s.t[s.i:s.j]
    def val(s, h):
        v = None
        for e in s.ev:
            if e[0] == 'cap' and e[1] == h: v = s.t[e[2]:e[3]]
        return v
    def passes(s, rid):
        ps = [e[1] for e in s.ev if e[0] == 'pass' and e[1][-1][0] == rid]
        out = []
        for p in ps:
            d = {}
            for e in s.ev:
                if e[0] == 'cap' and e[4][:len(p)] == p: d[e[1]] = s.t[e[2]:e[3]]
            out.append(d)
        return out

class Pat:
    def __init__(s, src, holes=None):
        s.src = src; s.node = parse(src, holes); s.loop = loops_of(s.node)
    def rows_at(s, t, i):
        seen = set()
        for j, ev in m(s.node, t, i, (), ()):
            if j not in seen:
                seen.add(j); yield Row(s, t, i, j, ev)

# ---------- conditions: functions row -> T/F/U ----------
def num(v):
    try: return int(v)
    except: return None
def S(op, k):
    def f(v):
        x = num(v)
        if op == '!':   # complement of a set (k is a set fn)
            return not k(v)
        if x is None: return False
        return {'<': x < k, '>=': x >= k, '>': x > k, '<=': x <= k, '==': x == k}[op]
    return f
def lit(*ss): return lambda v: v in ss
def comp(sf): return lambda v: not sf(v)
def between(a, b): return lambda v: num(v) is not None and a <= num(v) <= b

def passrows(row, names):
    lp = {row.pat.loop.get(h) for h in names}
    lp.discard(None)
    if not lp: return [None]   # set-once: the row itself
    assert len(lp) == 1, names
    ps = row.passes(lp.pop())
    return ps if ps else [{}]   # zero passes: one null pass row
def getv(row, pr, h):
    if pr is None: return row.val(h)
    return pr.get(h)
def test(h, sf, default=None):
    def c(row):
        out = []
        for pr in passrows(row, [h]):
            v = getv(row, pr, h)
            if v is None: v = default
            out.append(U if v is None else (T if sf(v) else F))
        return kand(*out)
    c.names = [h]; c.pertest = lambda row, pr: (lambda v: U if v is None else (T if sf(v) else F))(getv(row, pr, h) if getv(row, pr, h) is not None else default)
    return c
def joint(names, defaults, rf):
    def per(row, pr):
        vs = []
        for h in names:
            v = getv(row, pr, h)
            if v is None: v = defaults.get(h)
            if v is None: return U
            vs.append(v)
        return T if rf(*vs) else F
    def c(row): return kand(*[per(row, pr) for pr in passrows(row, names)])
    c.names = names; c.pertest = per
    return c
def NOT(c):
    f = lambda row: knot(c(row)); f.names = c.names
    f.pertest = lambda row, pr: knot(c.pertest(row, pr)); return f
def AND(*cs):
    f = lambda row: kand(*[c(row) for c in cs]); f.names = sum((c.names for c in cs), [])
    f.pertest = lambda row, pr: kand(*[c.pertest(row, pr) for c in cs]); return f
def realpasses(row, names):
    lp = {row.pat.loop.get(h) for h in names}; lp.discard(None)
    assert len(lp) == 1
    return row.passes(lp.pop())
def count(c): return lambda row: sum(1 for pr in realpasses(row, c.names) if c.pertest(row, pr) == T)
def some(c):
    f = lambda row: T if count(c)(row) > 0 else F; f.names = c.names; return f
def none(c):
    f = lambda row: F if count(c)(row) > 0 else T; f.names = c.names; return f

# ---------- programs ----------
class Prog:
    """base pattern & filters. filter kinds: ('c', cond) | ('and', Prog) | ('diff', Prog)
       | ('contains', Prog) | ('ncontains', Prog) | ('textnone', Prog)"""
    def __init__(s, pat, *filters):
        s.pat = pat if isinstance(pat, Pat) else Pat(pat); s.f = filters
    def ok(s, row, subject):
        for k, x in s.f:
            if k == 'c':
                if x(row) != T: return False
            elif k == 'and':
                if not x.whole(row.stretch): return False
            elif k == 'diff':
                if x.whole(row.stretch): return False
            elif k == 'contains':
                if x.search(row.stretch) is None: return False
            elif k == 'ncontains':
                if x.search(row.stretch) is not None: return False
            elif k == 'textnone':
                if x.search(subject) is not None: return False
        return True
    def rows_at(s, t, i, subject=None):
        for r in s.pat.rows_at(t, i):
            if s.ok(r, t if subject is None else subject): yield r
    def whole(s, t):
        for r in s.rows_at(t, 0):
            if r.j == len(t): return True
        return False
    def search(s, t, frm=0):
        for i in range(frm, len(t) + 1):
            for r in s.rows_at(t, i): return r
        return None
    def findall(s, t):
        out = []; k = 0
        while k <= len(t):
            r = s.search(t, k)
            if r is None: break
            out.append(r); k = r.j if r.j > r.i else r.j + 1
        return out
    def both(s, t):
        r = s.search(t)
        return (s.whole(t), None if r is None else (r.stretch, r.i))
def fmt(w, sr):
    return ('HOLDS' if w else 'FAILS') + ' / ' + ('FAILS' if sr is None else 'HOLDS `%s`@%d' % sr)
def strings(alpha, n):
    out, cur = [''], ['']
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
D = "0123456789"
H12 = list(D) + [a + b for a in D for b in D]
T2POOL = H12 + [h + ":" + a + b for h in H12 for a in D for b in D]
TOK = [h + mm for h in ["1", "9", "10", "21"] for mm in ["", ":00", ":15", ":30", ":45", ":50"]]
T2PAIRS = TOK + [a + " " + b for a in TOK for b in TOK]
