# Critic simulate (absfold): an independent engine of the 14:31 absent-label rule,
# written from the note's TEXT (joint_condition.md 4G.1, table (AR), J1/J6/J7/J9) only.
import re, itertools

# ---- pattern AST -------------------------------------------------------
class C:  # char class
    def __init__(s, chars): s.chars = set(chars)
class L:  # literal string
    def __init__(s, t): s.t = t
class Seq:
    def __init__(s, *xs): s.xs = xs
class Alt:
    def __init__(s, *xs): s.xs = xs
class G:  # named group
    def __init__(s, name, x): s.name, s.x = name, x
class Rep:
    _n = 0
    def __init__(s, x, lo, hi, greedy=True):
        s.x, s.lo, s.hi, s.greedy = x, lo, hi, greedy
        Rep._n += 1; s.id = Rep._n

D = C('0123456789')

def rx(n):
    if isinstance(n, C):
        return '[' + ''.join(sorted(n.chars)) + ']'
    if isinstance(n, L): return re.escape(n.t)
    if isinstance(n, Seq): return ''.join(rx(x) for x in n.xs)
    if isinstance(n, Alt): return '(?:' + '|'.join(rx(x) for x in n.xs) + ')'
    if isinstance(n, G): return '(?P<%s>%s)' % (n.name, rx(n.x))
    if isinstance(n, Rep):
        hi = '' if n.hi is None else str(n.hi)
        q = '{%d,%s}' % (n.lo, hi)
        return '(?:' + rx(n.x) + ')' + q + ('' if n.greedy else '?')

# ---- matcher: first (PCRE-priority) full match, with a pass trace ----------
def m(n, s, i):
    """yield (j, events) in priority order"""
    if isinstance(n, C):
        if i < len(s) and s[i] in n.chars: yield i + 1, ()
        return
    if isinstance(n, L):
        if s.startswith(n.t, i): yield i + len(n.t), ()
        return
    if isinstance(n, Seq):
        def go(k, i, ev):
            if k == len(n.xs): yield i, ev; return
            for j, e in m(n.xs[k], s, i):
                yield from go(k + 1, j, ev + e)
        yield from go(0, i, ())
        return
    if isinstance(n, Alt):
        for x in n.xs: yield from m(x, s, i)
        return
    if isinstance(n, G):
        for j, e in m(n.x, s, i):
            yield j, e + (('cap', n.name, s[i:j]),)
        return
    if isinstance(n, Rep):
        def go(cnt, i, ev):
            more = n.hi is None or cnt < n.hi
            def take():
                if not more: return
                for j, e in m(n.x, s, i):
                    if j == i and cnt >= n.lo: continue  # empty iteration stops
                    yield from go(cnt + 1, j, ev + (('pass', n.id),) + e)
            def stop():
                if cnt >= n.lo: yield i, ev
            if n.greedy:
                yield from take(); yield from stop()
            else:
                yield from stop(); yield from take()
        for j, ev in go(0, i, ()):
            yield j, (('enter', n.id),) + ev + (('exit', n.id),)
        return
    raise TypeError(n)

def fullmatch(p, s):
    for j, ev in m(p, s, 0):
        if j == len(s): return ev
    return None

def frames(ev):
    root = {'caps': {}, 'loops': {}}
    stack = [root]   # frames
    inst = []        # (loop id, list of passes)
    for e in ev:
        if e[0] == 'enter':
            passes = []
            stack[-1]['loops'][e[1]] = passes
            inst.append(passes); stack.append(None)
        elif e[0] == 'pass':
            f = {'caps': {}, 'loops': {}}
            inst[-1].append(f); stack[-1] = f
        elif e[0] == 'exit':
            inst.pop(); stack.pop()
        else:
            f = stack[-1]
            assert f is not None
            f['caps'][e[1]] = e[2]
    return root

def chains(p, opt_is_loop=True):
    """label -> tuple of loop ids enclosing it (outer..inner)"""
    out = {}
    def walk(n, ch):
        if isinstance(n, (Seq, Alt)):
            for x in n.xs: walk(x, ch)
        elif isinstance(n, G):
            out[n.name] = ch; walk(n.x, ch)
        elif isinstance(n, Rep):
            isloop = opt_is_loop or not (n.hi == 1)
            walk(n.x, ch + ((n.id,) if isloop else ()))
    walk(p, ())
    return out

def group_lang(p, name, maxlen=3, alpha='0123456789x:;,-'):
    """standalone language of the group's own regex (the 'group' domain)"""
    out = []
    def find(n):
        if isinstance(n, G) and n.name == name: return n
        for x in getattr(n, 'xs', ()) + ((n.x,) if hasattr(n, 'x') and not isinstance(n, L) else ()):
            r = find(x)
            if r: return r
    g = find(p)
    r = re.compile(rx(g.x))
    lens = set()
    for L_ in range(0, maxlen + 1):
        for t in itertools.product(alpha, repeat=L_):
            t = ''.join(t)
            if r.fullmatch(t): out.append(t)
    return out

ABSENT = None

class SiblingError(Exception): pass

def tuples(fr, ch, labels):
    """Per J7 / item 5 (the lane's precise statement, part (1) RULED 13:29): pairing loop =
    deepest loop enclosing any named label; others same pass or outside. One tuple per pass;
    zero passes / never reached -> one tuple with the looped labels ABSENT (4G.1)."""
    deep = max((ch[l] for l in labels), key=len)
    for l in labels:
        if deep[:len(ch[l])] != ch[l]:
            raise SiblingError(labels)
    out = []
    def walk(f, d, acc, zero, kd=None):
        # f: frame at depth d (None = absent frame)
        acc = dict(acc); kd = dict(kd or {})
        for l in labels:
            if len(ch[l]) == d:
                acc[l] = f['caps'].get(l, ABSENT) if f is not None else ABSENT
                kd[l] = zero if f is None else 'P'
        if d == len(deep):
            out.append((tuple(acc[l] for l in labels), zero, tuple(kd[l] for l in labels))); return
        entered = f is not None and deep[d] in f['loops']
        passes = f['loops'].get(deep[d], []) if f is not None else []
        if not passes:
            walk(None, d + 1, acc, zero or ('Z' if entered else 'U'), kd)
        else:
            for p in passes: walk(p, d + 1, acc, zero, kd)
    walk(fr, 0, {}, False)
    return out

# ---- conditions --------------------------------------------------------
# A joint entry: labels = [(name, ctl, v)] ctl in {None,'mark','def'}; R(env)(tuple)->bool
# A record: list of (name, ctl, v, S) == joint over the product (J9).
class Ctx:
    def __init__(s, pat, subj, domain, F='F1', opt_is_loop=True):
        s.pat, s.subj = pat, subj
        s.ev = fullmatch(pat, subj)
        s.ok = s.ev is not None
        if s.ok:
            ev = s.ev
            if not opt_is_loop:
                ones = set()
                def wk(n):
                    if isinstance(n, Rep) and n.hi == 1: ones.add(n.id)
                    for x in getattr(n, 'xs', ()): wk(x)
                    if isinstance(n, (G, Rep)): wk(n.x)
                wk(pat)
                ev = tuple(e for e in ev if not (e[0] in ('enter', 'pass', 'exit') and e[1] in ones))
            s.fr = frames(ev)
            s.env = {}
            for e in s.ev:
                if e[0] == 'cap': s.env[e[1]] = e[2]   # last value, PCRE-like, for $a
        s.ch = chains(pat, opt_is_loop)
        s.domain = domain  # name -> list of candidate texts
        s.F = F

def joint(ctx, labels, R, mode='plain'):
    """mode: plain | A2m | A2v | A2z  (all() readings, 4G.6 (1))"""
    names = [l[0] for l in labels]
    if mode == 'A2m':
        labels = [(n, 'mark' if c is None else c, v) for n, c, v in labels]
    pred = R(ctx.env)
    for tup, zero, kinds in tuples(ctx.fr, ctx.ch, names):
        if mode == 'A2v' and zero and any(t is ABSENT for t in tup):
            continue  # pairing loop ran no pass: not tested
        choices = []
        for (n, c, v), t, kk in zip(labels, tup, kinds):
            if t is not ABSENT:
                choices.append([t])
            elif mode == 'today':
                if kk == 'Z': choices.append(ctx.domain[n])
                elif c == 'def': choices.append([v])
                else: return False
            elif c == 'def':
                choices.append([v])
            elif c == 'mark' or (mode == 'A2z' and zero == 'Z'):
                choices.append(ctx.domain[n])
            else:
                return False
        if not any(pred(x) for x in itertools.product(*choices)):
            return False
    return True

def record(ctx, parts, mode='plain'):
    """parts: [(name, ctl, v, S)], S(env)(text)->bool. J9: the product case.
    F2: a marked absent part is 'satisfied' outright (4G.6 (2))."""
    if ctx.F == 'F2':
        # F2: a marked absent label's part satisfied, regardless of its set; others tested jointly
        names = [p[0] for p in parts]
        lab = [(p[0], p[1], p[2]) for p in parts]
        Ss = [p[3](ctx.env) for p in parts]
        for tup, zero, kinds in tuples(ctx.fr, ctx.ch, names):
            if mode == 'A2v' and zero and any(t is ABSENT for t in tup):
                continue
            for (n, c, v), t, S in zip(lab, tup, Ss):
                if t is ABSENT:
                    if c == 'def': t = v
                    elif c == 'mark' or mode == 'A2m' or (mode == 'A2z' and zero == 'Z'): continue
                    else: return False
                if not S(t): return False
        return True
    lab = [(p[0], p[1], p[2]) for p in parts]
    Sf = [p[3] for p in parts]
    R = lambda env: (lambda t, Ss=[S(env) for S in Sf]: all(S(x) for S, x in zip(Ss, t)))
    return joint(ctx, lab, R, mode)

def single(ctx, name, ctl, v, S, mode='plain'):
    return record(ctx, [(name, ctl, v, S)], mode)

def amp(ctx, parts, mode='plain'):
    return all(single(ctx, *p, mode=mode) for p in parts)

def isnum(t): return t is not None and t != '' and t.isdigit()
def lt(b): return lambda env: (lambda t: isnum(t) and int(t) < b)
def rng(a, b): return lambda env: (lambda t: isnum(t) and a <= int(t) <= b)
def eq(x): return lambda env: (lambda t: t == x)
def lt_label(a): return lambda env: (lambda t, A=env.get(a): isnum(t) and A is not None and int(t) < int(A))
