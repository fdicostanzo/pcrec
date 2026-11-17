# simulate lens: an independent path evaluator written from rev 24.2's TEXT (R.1.2 paths in PCRE order; R.1.7 (1)-(4)
# per-pass labels), with PCRE's capture carried alongside. Subset: literals, \d \w . [..], (?: ) (?<n> ) (?| ) (?J)
# (?= ) (?! ) (?> ), | , * + ? {m} {m,} {m,n} lazy ?, \k<n>, callout (?C"name") = a condition piece.
# Each path state: pos, caps {gid: (s,e)} (PCRE carry), labs {gid: (s,e)} (per-pass, reset at every pass start of a loop
# with upper bound >= 2), passes log.
import re as _re

class P:
    def __init__(s, pat):
        s.p, s.i, s.ng, s.names = pat, 0, 0, {}
        s.dup = False
        if s.p.startswith("(?J)"): s.dup = True; s.i = 4
        s.tree = s.alt(); assert s.i == len(s.p), (pat, s.i)
    def peek(s): return s.p[s.i] if s.i < len(s.p) else None
    def alt(s, reset=False):
        base = s.ng; br = []; mx = s.ng
        while True:
            if reset: s.ng = base
            br.append(s.seq()); mx = max(mx, s.ng)
            if s.peek() == "|": s.i += 1; continue
            break
        if reset: s.ng = mx
        return ("alt", br)
    def seq(s):
        items = []
        while s.peek() not in (None, "|", ")"):
            a = s.atom(); a = s.quant(a); items.append(a)
        return ("seq", items)
    def quant(s, a):
        c = s.peek()
        if c in ("*", "+", "?", "{"):
            if c == "{":
                m = _re.match(r"\{(\d+)(,(\d*))?\}", s.p[s.i:])
                if not m: return a
                lo = int(m.group(1)); hi = lo if m.group(2) is None else (int(m.group(3)) if m.group(3) else None)
                s.i += m.end()
            else:
                lo, hi = {"*": (0, None), "+": (1, None), "?": (0, 1)}[c]; s.i += 1
            lazy = False
            if s.peek() == "?": lazy = True; s.i += 1
            return ("rep", a, lo, hi, lazy)
        return a
    def atom(s):
        c = s.p[s.i]
        if c == "(":
            if s.p.startswith('(?C"', s.i):
                j = s.p.index('")', s.i); nm = s.p[s.i + 4:j]; s.i = j + 2; return ("call", nm)
            if s.p.startswith("(?:", s.i): s.i += 3; t = s.alt(); s.i += 1; return t
            if s.p.startswith("(?|", s.i): s.i += 3; t = s.alt(reset=True); s.i += 1; return t
            if s.p.startswith("(?=", s.i): s.i += 3; t = s.alt(); s.i += 1; return ("la", t, True)
            if s.p.startswith("(?!", s.i): s.i += 3; t = s.alt(); s.i += 1; return ("la", t, False)
            if s.p.startswith("(?>", s.i): s.i += 3; t = s.alt(); s.i += 1; return ("atomic", t)
            m = _re.match(r"\(\?<([A-Za-z_]\w*)>", s.p[s.i:])
            s.ng += 1; g = s.ng
            if m:
                s.names.setdefault(m.group(1), []).append(g); s.i += m.end()
            else: s.i += 1
            t = s.alt(); assert s.p[s.i] == ")"; s.i += 1
            return ("grp", g, t)
        if c == "\\":
            d = s.p[s.i + 1]
            if d == "k":
                m = _re.match(r"\\k<(\w+)>", s.p[s.i:]); s.i += m.end(); return ("bref", m.group(1))
            s.i += 2
            if d == "d": return ("set", lambda ch: ch.isdigit())
            if d == "w": return ("set", lambda ch: ch.isalnum() or ch == "_")
            if d == "s": return ("set", lambda ch: ch.isspace())
            return ("set", lambda ch, d=d: ch == d)
        if c == "[":
            j = s.p.index("]", s.i + 1); body = s.p[s.i:j + 1]; s.i = j + 1
            rx = _re.compile(body); return ("set", lambda ch, rx=rx: rx.fullmatch(ch) is not None)
        if c == ".": s.i += 1; return ("set", lambda ch: ch != "\n")
        if c == "$": s.i += 1; return ("end",)
        s.i += 1; return ("set", lambda ch, c=c: ch == c)

def groups_in(node, acc):
    k = node[0]
    if k == "grp": acc.add(node[1]); groups_in(node[2], acc)
    elif k in ("alt",): [groups_in(b, acc) for b in node[1]]
    elif k == "seq": [groups_in(b, acc) for b in node[1]]
    elif k == "rep": groups_in(node[1], acc)
    elif k in ("la", "atomic"): groups_in(node[1], acc)
    return acc

class St:
    __slots__ = ("pos", "caps", "labs", "log")
    def __init__(s, pos, caps, labs, log): s.pos, s.caps, s.labs, s.log = pos, caps, labs, log
    def cp(s, **kw):
        n = St(s.pos, s.caps, s.labs, s.log)
        for k, v in kw.items(): setattr(n, k, v)
        return n

class M:
    """paths(text, start): every path from `start`, PCRE order (a generator of final states)."""
    def __init__(s, pat, calls=None, inner_reset=True):
        s.P = P(pat); s.calls = calls or {}; s.reset = inner_reset
    def m(s, node, st, k):
        t = s.txt; kind = node[0]
        if kind == "seq":
            items = node[1]
            def go(i, st):
                if i == len(items): yield from k(st); return
                yield from s.m(items[i], st, lambda st2: go(i + 1, st2))
            yield from go(0, st); return
        if kind == "alt":
            for b in node[1]: yield from s.m(b, st, k)
            return
        if kind == "set":
            if st.pos < len(t) and node[1](t[st.pos]): yield from k(st.cp(pos=st.pos + 1))
            return
        if kind == "end":
            if st.pos == len(t): yield from k(st)
            return
        if kind == "grp":
            g, b = node[1], node[2]; s0 = st.pos
            def close(st2):
                c = dict(st2.caps); c[g] = (s0, st2.pos); l = dict(st2.labs); l[g] = (s0, st2.pos)
                yield from k(st2.cp(caps=c, labs=l))
            yield from s.m(b, st, close); return
        if kind == "bref":
            gs = s.P.names[node[1]]
            sp = next((st.caps[g] for g in gs if g in st.caps), None)
            if sp is None: return
            v = t[sp[0]:sp[1]]
            if t.startswith(v, st.pos): yield from k(st.cp(pos=st.pos + len(v)))
            return
        if kind == "call":
            if s.calls[node[1]](s, st): yield from k(st)
            return
        if kind == "la":
            r = next(s.m(node[1], st, lambda st2: iter([st2])), None)
            if node[2]:
                if r is not None: yield from k(r.cp(pos=st.pos))
            else:
                if r is None: yield from k(st)
            return
        if kind == "atomic":
            r = next(s.m(node[1], st, lambda st2: iter([st2])), None)
            if r is not None: yield from k(r)
            return
        if kind == "rep":
            body, lo, hi, lazy = node[1], node[2], node[3], node[4]
            isloop = hi is None or hi >= 2
            inner = s.ginner.setdefault(id(node), groups_in(body, set()))
            def it(n, st):
                # n passes done
                def one():
                    s0 = st.pos
                    st1 = st
                    if isloop and s.reset:
                        st1 = st.cp(labs={g: v for g, v in st.labs.items() if g not in inner})
                    st1 = st1.cp(log=st1.log + (("pass", id(node), s0),))
                    def after(st2):
                        if st2.pos == s0 and n + 1 > lo:
                            # PCRE: an iteration that matched empty ends the loop (it counts)
                            yield from k(st2)
                        else:
                            yield from it(n + 1, st2)
                    yield from s.m(body, st1, after)
                can_more = hi is None or n < hi
                if n < lo: yield from one(); return
                if lazy:
                    yield from k(st)
                    if can_more: yield from one()
                else:
                    if can_more: yield from one()
                    yield from k(st)
            yield from it(0, st); return
        raise ValueError(kind)
    def paths(s, txt, start=0, end=None):
        s.txt = txt; s.ginner = {}
        st = St(start, {}, {}, ())
        def fin(st2):
            if end is None or st2.pos == end: yield st2
        yield from s.m(s.P.tree, st, fin)
    def val(s, st, name, which="labs"):
        d = getattr(st, which)
        for g in s.P.names[name]:
            if g in d: return s.txt[d[g][0]:d[g][1]]
        return None
    def lab(s, st, name):
        # a duplicate label inside a loop: the value from whichever duplicate group the pass set (§4.3); outside, lowest set
        return s.val(st, name, "labs")
    def cap(s, st, name): return s.val(st, name, "caps")

def run(mk, cond, txt):
    """mk: M; cond(M, st) -> bool, the bare condition after the pattern. Returns WHOLE, SEARCHED, FIND-ALL."""
    def first(start, end=None):
        for st in mk.paths(txt, start, end):
            if cond(mk, st): return st
        return None
    w = first(0, len(txt))
    srch = None
    for i in range(len(txt) + 1):
        r = first(i)
        if r is not None: srch = (i, r); break
    fa = []; pos = 0
    while pos <= len(txt):
        r = None
        for i in range(pos, len(txt) + 1):
            r = first(i)
            if r is not None: r = (i, r); break
        if r is None: break
        fa.append(r); i, st = r
        pos = st.pos if st.pos > i else st.pos + 1
    return w, srch, fa

def num(v): return v is not None and _re.fullmatch(r"0|[1-9]\d*", v) is not None
