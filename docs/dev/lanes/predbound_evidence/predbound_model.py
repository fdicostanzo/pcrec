#!/usr/bin/env python3
# Lane predbound (2026-11-22): the evidence for folding the owner's two rulings of 2026-11-22, bound-condition (b)
# and count-in-set (b), into the predicate documents, and for the manager's readings (a)..(h) named in the lane
# brief. DESIGN EVIDENCE ONLY; rules nothing. Python3 `re` and direct counts as controls.
#
# METHOD. Lane predfix77's lowerer and label matcher are COPIED below unchanged (the block between the two marks
# "copied from predfix77_model.py"), its own sabotage hooks renamed `x77sN` so none of them fires here, except
# s1 (CONTROL), kept. EXTENSIONS of this lane, after the copied block, each the ruled rule or a marked reading:
#   BINDING  the ruling: a binding whose body NAMES a label (left of `:`, a `$` read, a counted label) that no
#            pattern in the binding holds is a compile error AT THE BINDING, checked for every binding of the
#            program whether it is used or not (reading (e)); a pattern the body USES lends its public labels
#            (reading (g)); a SET bound alone names nothing (reading (b)); a condition on `0` alone bound to a
#            name is LEFT OPEN: OPT zero_bound = inplace (read where used) | sealed (its own `0`) | error.
#   VALUE    count-in-set (b): an entry's left part that is not a bare name or label path is a VALUE written in
#            place: a `$` read, arithmetic (`+ - * %` on canonical numerals; outside the domain nothing), a
#            `count(c)` over c's array; several strings there are a compile error, and a value that yields
#            nothing fails the entry (readings (d)). A value also stands where an rx stands (its one string).
#   SETS     `>= $x` style comparison against a value; `between(lo, hi)` read from library.md's body.
#   META     `[w = [a, b, ...]]`: the member that matched sets `w.index`, its 1-based position (core/values/metadata).
# Every three-mode line formatted for the documents must occur VERBATIM in them (DOC). The OLD printed lines are
# read from the starting commit 1e0384941 by `git show` (FIVE compares them, never typed by hand).
#
# Run (W = the worktree; any cwd):  timeout 300 python3 -I -B W/docs/dev/lanes/predbound_evidence/predbound_model.py
# PREDBOUND_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
#   s1  the matcher tries alternatives last first                                         -> CONTROL
#   s2  `+` adds one too many                                                             -> FIVE
#   s3  a set bound alone is refused like a condition                                     -> SETBOUND
#   s4  a condition bound alone naming a label is laid in place, not refused              -> REFUSE
#   s5  bindings are checked only where used                                              -> ATBINDING
#   s6  an argument is lowered (and checked) in the macro's scope                         -> INPLACE
#   s7  a used pattern lends the body no labels                                           -> LEGAL
#   s8  a value that yields nothing passes the entry                                      -> NOTHING
#   s9  `$h` left of `:` reads an unset label as `0`                                      -> SAMEREAD
#   s10 a value of several strings left of `:` takes the first                            -> SEVERAL
#   s11 the zero (a) line lowered as sealed                                               -> ZERO
#   s12 `10 - $b` computed as `9 - $b`                                                    -> SUMALT
#   s13 the sweep's checker skips condition bodies                                        -> SWEEP
#   s14 a quoted owner sentence altered (in memory)                                       -> QUOTES
#   s15 the bound-condition piece's status read back as open (in memory)                  -> MARKS
#   s16 one formatted line's subject altered before the document lookup                   -> DOC
#   s17 a member's `.index` 0-based                                                       -> META
# ---------------------------------------------------------------- copied from predfix77_model.py (begin)
import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
RECORD_PATH = os.path.join(W, "docs", "design", "plan_row_bodies", "COND-FAMILY.md")
SAB = set(x for x in os.environ.get("PREDBOUND_SABOTAGE", "").split(",") if x)
FAILED, CHECKS = [], []
sys.setrecursionlimit(50000)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rxmodel_evidence"))
import pcre2h as P                                           # noqa: E402


def sab(n):
    return n in SAB


def check(name, ok, detail=""):
    CHECKS.append(name)
    print("%-9s %s %s" % (name, "ok  " if ok else "FAIL", detail))
    if not ok:
        FAILED.append(name)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def ws(t):
    return re.sub(r"\s+", " ", t)


CORE = read(os.path.join(PRED, "core.md"))
LIB = read(os.path.join(PRED, "library.md"))
DOCS = "".join(read(os.path.join(PRED, f)) for f in
               ("core.md", "core_details.md", "library.md", "library_details.md", "parked.md", "parked_details.md"))
RECORD = read(RECORD_PATH)
RECORD_WS = ws(RECORD)


class CompileError(Exception):
    pass


# ================================================================== the label matcher (predarr's, extended)
DIG = frozenset("0123456789")
WORD = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
ANY = "ANY"
CANON = re.compile(r"0|[1-9][0-9]*")
NODES = {}                     # `${#n}` in matcher text -> a node built by the lowerer


class Src:
    def __init__(self, s):
        self.s, self.i, self.dotall, self.icase = s, 0, False, False

    def peek(self, n=0):
        return self.s[self.i + n] if self.i + n < len(self.s) else None

    def take(self):
        c = self.s[self.i]
        self.i += 1
        return c


def keys_of(name):
    """A group name `h@top,s1` sets the keys `h@top`, `h@s1`; a plain name `h` sets `h@top`."""
    base, _, sc = name.partition("@")
    return tuple("%s@%s" % (base, x) for x in (sc.split(",") if sc else ["top"]))


def names_in(node):
    k = node[0]
    out = set()
    if k == "grp":
        out |= set(keys_of(node[1]))
        out |= names_in(node[2])
    elif k in ("seq", "alt"):
        for x in node[1]:
            out |= names_in(x)
    elif k in ("rep", "look", "atomic"):
        out |= names_in(node[1])
    return out


def p_alt(p):
    alts = [p_seq(p)]
    while p.peek() == "|":
        p.take()
        alts.append(p_seq(p))
    if len(alts) == 1:
        return alts[0]
    return ("alt", alts, names_in(("alt", alts)))


def p_seq(p):
    items = []
    while p.peek() is not None and p.peek() not in "|)":
        items.append(p_quant(p))
    return ("seq", items)


def p_quant(p):
    a = p_atom(p)
    c = p.peek()
    lo = hi = None
    if c == "?":
        lo, hi = 0, 1
    elif c == "*":
        lo, hi = 0, None
    elif c == "+":
        lo, hi = 1, None
    elif c == "{":
        mm = re.match(r"\{(\d+)(?:,(\d*))?\}", p.s[p.i:])
        lo = int(mm.group(1))
        hi = lo if mm.group(2) is None else (int(mm.group(2)) if mm.group(2) else None)
        p.i += mm.end() - 1
    if lo is None:
        return a
    p.take()
    lazy = False
    if p.peek() == "?":
        p.take()
        lazy = True
    return ("rep", a, lo, hi, names_in(a), lazy)


def p_class(p):
    mem = set()
    while p.peek() != "]":
        a = p.take()
        if a == "\\":
            e = p.take()
            mem |= DIG if e == "d" else {e}
            continue
        if p.peek() == "-" and p.peek(1) != "]":
            p.take()
            b = p.take()
            mem |= set(chr(x) for x in range(ord(a), ord(b) + 1))
        else:
            mem.add(a)
    p.take()
    if p.icase:
        mem |= set(c.swapcase() for c in mem)
    return ("cls", frozenset(mem))


def p_atom(p):
    c = p.take()
    if c == "$" and p.peek() == "{":
        j = p.s.index("}", p.i)
        body = p.s[p.i + 1:j]
        p.i = j + 1
        assert body.startswith("#"), body
        return NODES[int(body[1:])]
    if c == "(":
        if p.s.startswith("?:", p.i):
            p.i += 2
            n = p_alt(p)
        elif p.s.startswith("?s:", p.i) or p.s.startswith("?i:", p.i):
            fl = p.s[p.i + 1]
            p.i += 3
            old = (p.dotall, p.icase)
            if fl == "s":
                p.dotall = True
            else:
                p.icase = True
            n = p_alt(p)
            p.dotall, p.icase = old
        elif p.s.startswith("?>", p.i):
            p.i += 2
            n = ("atomic", p_alt(p))
        elif p.s.startswith("?<", p.i) and p.s[p.i + 2] not in "=!":
            j = p.s.index(">", p.i)
            name = p.s[p.i + 2:j]
            p.i = j + 1
            n = ("grp", name, p_alt(p))
        elif p.s.startswith("?=", p.i):
            p.i += 2
            n = ("look", p_alt(p))
        else:
            raise CompileError("unsupported group")
        assert p.take() == ")"
        return n
    if c == "\\":
        e = p.take()
        if e == "d":
            return ("cls", DIG)
        if e == "w":
            return ("cls", WORD)
        if e == "A":
            return ("bos",)
        if e == "z":
            return ("eos",)
        return ("lit", e, p.icase)
    if c == "[":
        return p_class(p)
    if c == ".":
        return ("cls", ANY) if p.dotall else ("dot",)
    return ("lit", c, p.icase)


class St:
    __slots__ = ("lab", "log", "marks", "seen")

    def __init__(self, lab, log, marks, seen):
        self.lab, self.log, self.marks, self.seen = lab, log, marks, seen


def reset(st, keys):
    if not keys:
        return st
    lab = {k: v for k, v in st.lab.items() if k not in keys}
    return St(lab, st.log + (("reset", tuple(sorted(keys))),), st.marks, st.seen)


def val_ok(v, val, lab):
    if v is None:
        return False
    if val[0] == "eq":
        return v == val[1]
    if val[0] == "read":
        return v == lab.get(val[1]) if lab.get(val[1]) is not None else False
    if val[0] == "cmp":
        if not CANON.fullmatch(v):
            return False
        a, b = int(v), int(val[2])
        return {">=": a >= b, "<=": a <= b, "<": a < b, ">": a > b, "==": a == b}[val[1]]
    if val[0] == "rx":
        return m(val[1], v, 0, St({}, (), {}, frozenset()), lambda q, st: True if q == len(v) else None) is not None
    raise ValueError(val)


def cond_holds(node, s, pos, st):
    _, neg, entries = node
    res = True
    for key, val in entries:
        if key[0] == "zero":
            v = s[st.marks[key[1]]:pos] if key[1] in st.marks else None
        else:
            v = st.lab.get(key[1])
        if not val_ok(v, val, st.lab):
            res = False
            break
    return (not res) if neg else res


def settings(log, key, scope):
    """The array: every setting of `key` on the path so far, in the order made, after the scope's last entry."""
    out = []
    for e in log:
        if e[0] == "enter" and e[1] == scope:
            out = []
        elif e[0] == "set" and e[1] == key:
            out.append((e[3], e[2]))
    if sab("x77s13"):
        out = sorted(out, key=lambda x: x[0])
    return [v for _, v in out]


def gq_holds(node, s, pos, st):
    _, fn, neg, key, scope, val, k, ineg = node
    arr = settings(st.log, key, scope)
    if fn == "index":
        r = len(arr) >= k and val_ok(arr[k - 1], val, st.lab)
    else:
        hits = [val_ok(x, val, st.lab) for x in arr]
        hits = [(not h) if ineg else h for h in hits]
        if fn == "some":
            r = any(hits)
        elif fn == "none":
            r = not any(hits)
        else:
            r = val_ok(str(sum(hits)), k, st.lab)
    return (not r) if neg else r


def m(node, s, pos, st, k):
    t = node[0]
    if t == "lit":
        ok = pos < len(s) and (s[pos] == node[1] or (node[2] and s[pos].lower() == node[1].lower()))
        return k(pos + 1, st) if ok else None
    if t == "cls":
        ok = pos < len(s) and (node[1] == ANY or s[pos] in node[1])
        return k(pos + 1, st) if ok else None
    if t == "dot":
        return k(pos + 1, st) if pos < len(s) and s[pos] != "\n" else None
    if t == "bos":
        return k(pos, st) if pos == 0 else None
    if t == "eos":
        return k(pos, st) if pos == len(s) else None
    if t == "seq":
        return mseq(node[1], 0, s, pos, st, k)
    if t == "alt":
        st2 = reset(st, node[2])
        for a in (node[1][::-1] if sab("s1") else node[1]):
            r = m(a, s, pos, st2, k)
            if r is not None:
                return r
        return None
    if t == "grp":
        name = node[1]

        def close(p2, st2):
            lab = dict(st2.lab)
            log = st2.log
            for key in keys_of(name):
                lab[key] = s[pos:p2]
                log = log + (("set", key, s[pos:p2], pos),)
            return k(p2, St(lab, log, st2.marks, st2.seen))
        return m(node[2], s, pos, st, close)
    if t == "rep":
        _, sub, lo, hi, names, lazy = node
        branching = not (lo == 1 and hi == 1)
        st0 = reset(st, names) if branching else st

        def it(i, p, stc):
            def more():
                if hi is None or i < hi:
                    def after(p2, st2):
                        if p2 == p and i >= lo:
                            return None
                        return it(i + 1, p2, st2)
                    return m(sub, s, p, stc, after)
                return None

            def stop():
                return k(p, stc) if i >= lo else None
            for f in ((stop, more) if lazy else (more, stop)):
                r = f()
                if r is not None:
                    return r
            return None
        return it(0, pos, st0)
    if t in ("look", "atomic"):
        r = m(node[1], s, pos, st, lambda p2, st2: (p2, st2))
        if r is None:
            return None
        return k(pos if t == "look" else r[0], r[1])
    if t == "cond":
        return k(pos, st) if cond_holds(node, s, pos, st) else None
    if t == "gq":
        return k(pos, st) if gq_holds(node, s, pos, st) else None
    if t == "mark":
        mk = dict(st.marks)
        mk[node[1]] = pos
        return k(pos, St(st.lab, st.log, mk, st.seen))
    if t == "enter":
        sc = node[1]
        if node[2] and sc in st.seen:                # reading (c), withdrawn: a re-entered piece keeps its view
            return k(pos, st)
        lab = {kk: v for kk, v in st.lab.items() if not kk.endswith("@" + sc)}
        return k(pos, St(lab, st.log + (("enter", sc),), st.marks, st.seen | {sc}))
    if t == "andpat":                                # `P & Q`: Q matched whole on P's stretch, from the mark
        a = st.marks[node[1]]
        piece = s[a:pos]
        r = m(node[2], piece, 0, St({}, (), {}, frozenset()), lambda q, st2: True if q == len(piece) else None)
        return k(pos, st) if r is not None else None
    raise ValueError(t)


def mseq(items, i, s, pos, st, k):
    if i == len(items):
        return k(pos, st)
    return m(items[i], s, pos, st, lambda p2, st2: mseq(items, i + 1, s, p2, st2, k))


class Prog:
    def __init__(self, rx):
        self.rx = rx
        self.node = p_alt(Src(rx))

    def at(self, s, start, need_end=None, nonempty=False):
        def fin(p, st):
            if need_end is not None and p != need_end:
                return None
            if nonempty and p == start:
                return None
            return (start, p, st)
        return m(self.node, s, start, St({}, (), {"top": start}, frozenset()), fin)

    def whole(self, s):
        return self.at(s, 0, need_end=len(s)) is not None

    def search(self, s, frm=0):
        for i in range(frm, len(s) + 1):
            r = self.at(s, i)
            if r:
                return r
        return None

    def findall(self, s):
        out, pos = [], 0
        while pos <= len(s):
            r = self.search(s, pos)
            if not r:
                break
            a, b, _ = r
            out.append((s[a:b], a))
            if b > a:
                pos = b
                continue
            r2 = self.at(s, b, nonempty=True)
            if r2:
                out.append((s[r2[0]:r2[1]], r2[0]))
                pos = r2[1]
            else:
                pos = b + 1
        return out


def fmt(Pg, whole, srch, fa):
    w = ", ".join("`%s` %s" % (t, "HOLDS" if Pg.whole(t) else "FAILS") for t in whole)
    r = Pg.search(srch)
    sm = "`%s`@%d" % (srch[r[0]:r[1]], r[0]) if r else "FAILS"
    f = ", ".join("`%s`@%d" % x for x in Pg.findall(fa))
    return "WHOLE %s / SEARCHED `%s` %s / FIND-ALL `%s` [%s]" % (w, srch, sm, fa, f)


def answers(Pg, texts):
    out = []
    for t in texts:
        r = Pg.search(t)
        out.append((Pg.whole(t), (r[0], r[1]) if r else None, tuple(Pg.findall(t))))
    return out


class Re:
    """python `re` with the same three modes (FIND-ALL as above)."""

    def __init__(self, rx, flags=0):
        self.c = re.compile(rx, flags)

    def whole(self, s):
        return self.c.fullmatch(s) is not None

    def search(self, s, frm=0):
        mm = self.c.search(s, frm)
        return (mm.start(), mm.end(), None) if mm else None

    def at(self, s, i, nonempty=False):
        mm = self.c.match(s, i)
        if mm and (not nonempty or mm.end() > i):
            return (mm.start(), mm.end(), None)
        return None

    def findall(self, s):
        return Prog.findall(self, s)


def ndiff(a, b):
    return tuple(sum(1 for x, y in zip(a, b) if x[i] != y[i]) for i in range(3))


def pop(alpha, n):
    return [""] + ["".join(t) for k in range(1, n + 1) for t in itertools.product(alpha, repeat=k)]


# ================================================================== the lowerer (expression text -> matcher text)
def split_top(text, sep):
    """Split at `sep` outside (), [], {}, /../ and "..".."""
    out, depth, i, last, in_rx, in_q = [], 0, 0, 0, False, False
    while i < len(text):
        c = text[i]
        if in_rx:
            if c == "\\":
                i += 2
                continue
            if c == "/":
                in_rx = False
            elif text.startswith("${", i):
                j = close_hole(text, i)
                i = j + 1
                continue
        elif in_q:
            if c == '"':
                in_q = False
        elif c == "/":
            in_rx = True
        elif c == '"':
            in_q = True
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif depth == 0 and text.startswith(sep, i):
            out.append(text[last:i])
            i += len(sep)
            last = i
            continue
        i += 1
    out.append(text[last:])
    return [x.strip() for x in out]


def close_hole(rx, i):
    """index of the `}` closing the hole `${` at i (nested /../, (), "..", ${..} skipped)."""
    j, depth = i + 2, 1
    in_rx, in_q = False, False
    while j < len(rx):
        c = rx[j]
        if in_q:
            if c == '"':
                in_q = False
        elif c == '"':
            in_q = True
        elif c == "\\":
            j += 2
            continue
        elif rx.startswith("${", j):
            depth += 1
            j += 2
            continue
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    raise CompileError("unclosed hole")


BINDS, MACROS = {}, {}
COUNTER = [0]
OPT = {}
CAPTURES = []                  # (definition, name) of every group written in rx TEXT (a capture by pure-label)


def fresh(prefix):
    COUNTER[0] += 1
    return "%s%d" % (prefix, COUNTER[0])


def node_ref(n):
    NODES[len(NODES)] = n
    return "${#%d}" % (len(NODES) - 1)


class Ctx:
    def __init__(self, scopes=("top",), zero="top", chain=None, name="top", held=None, params=None, caller=None):
        self.scopes, self.zero, self.chain, self.name = tuple(scopes), zero, chain, name
        self.held = held if held is not None else set()
        self.params = params or {}
        self.caller = caller

    @property
    def cur(self):
        return self.scopes[-1]

    def sub(self, **kw):
        d = dict(scopes=self.scopes, zero=self.zero, chain=self.chain, name=self.name, held=self.held,
                 params=self.params, caller=self.caller)
        d.update(kw)
        return Ctx(**d)


IS_COND = re.compile(r"^(NOT )?\(\(?[\w.]+(?:\[\d+\])?(?:, \w+)*\)?(?: = \"[^\"]*\")?: ")
GQ = re.compile(r"^(NOT )?(some|occurs\.none|count)\((.*)\)$")
ENTRY = re.compile(r"([\w.]+)(?:\[(\d+)\])?: ?(.*)$")
NAMED = []                     # (scope, base name) of every label a condition or a read names


def parse_value(v, ctx):
    v = v.strip()
    mm = re.fullmatch(r'"([^"]*)"', v)
    if mm:
        return ("eq", mm.group(1))
    mm = re.fullmatch(r"(>=|<=|<|>|==) ?(\d+)", v)
    if mm:
        return ("cmp", mm.group(1), mm.group(2))
    if re.fullmatch(r"\d+", v):
        return ("eq", v)
    mm = re.fullmatch(r"\$(\w+)", v)
    if mm:
        NAMED.append((ctx.cur, mm.group(1)))
        return ("read", "%s@%s" % (mm.group(1), ctx.cur))
    if v.startswith("/") and v.endswith("/"):
        return ("rx", p_alt(Src(v[1:-1])))
    if v in BINDS:
        return parse_value(BINDS[v], ctx)
    if v in ctx.params:
        return parse_value(ctx.params[v][0], ctx)
    raise CompileError("unknown value " + v)


def lower_cond(text, ctx, zero_key=None):
    """`(e1, e2)` or `NOT (e)` -> a matcher node reference."""
    text = text.strip()
    neg = text.startswith("NOT ")
    if neg:
        text = text[4:].strip()
    assert text.startswith("(") and text.endswith(")"), text
    entries = []
    for e in split_top(text[1:-1], ","):
        em = ENTRY.fullmatch(e.strip())
        name, val = em.group(1), parse_value(em.group(3), ctx)
        if name == "0":
            entries.append((("zero", zero_key or ctx.zero), val))
        else:
            NAMED.append((ctx.cur, name))
            sc = "top" if OPT.get("names") == "shared" else ctx.cur     # the SHARED reading (rejected) reads the user's
            entries.append((("lab", "%s@%s" % (name, sc)), val))
    return node_ref(("cond", neg, entries))


def array_scope(ctx):
    """Which settings a group question reads: OPT['array'] in composed / own / chain."""
    a = OPT.get("array", "own")
    if a == "composed":
        return "top"
    if a == "chain" and ctx.chain:
        return ctx.chain
    if sab("x77s2") and a == "own":
        return "top"
    return ctx.cur


def lower_gq(text, ctx):
    mm = re.fullmatch(r"(NOT )?\((\w+)\[(\d+)\]: (.*)\)", text)
    if mm:
        neg, name, k, v = bool(mm.group(1)), mm.group(2), int(mm.group(3)), parse_value(mm.group(4), ctx)
        NAMED.append((ctx.cur, name))
        sc = array_scope(ctx)
        return node_ref(("gq", "index", neg, "%s@%s" % (name, sc), sc, v, k, False))
    mm = GQ.match(text)
    neg, fn, arg = bool(mm.group(1)), mm.group(2), mm.group(3).strip()
    ineg = arg.startswith("NOT ")
    if ineg:
        arg = arg[4:].strip()
    if arg.startswith("(("):
        raise CompileError("a joint entry inside a group question")
    entries = split_top(arg[1:-1], ",")
    if len(entries) > 1:                       # the reading: the product of one group question per entry
        assert not neg and not ineg
        return "".join(lower_gq("%s((%s))" % (fn, e), ctx) for e in entries)
    em = ENTRY.fullmatch(arg[1:-1].strip())
    name, v = em.group(1), parse_value(em.group(3), ctx)
    NAMED.append((ctx.cur, name))
    sc = array_scope(ctx)
    fnn = {"some": "some", "occurs.none": "none"}[fn]
    return node_ref(("gq", fnn, neg, "%s@%s" % (name, sc), sc, v, None, ineg))


def is_gq(text):
    return bool(GQ.match(text) or re.fullmatch(r"(NOT )?\(\w+\[\d+\]: .*\)", text))


def lower(expr, ctx):
    expr = expr.strip()
    alts = split_top(expr, " | ")
    if len(alts) > 1:
        return "|".join("(?:%s)" % lower(a, ctx) for a in alts)
    parts = split_top(expr, " & ")
    if len(parts) > 1:
        return lower_and(parts, ctx)
    seq = split_top(expr, " SEQ ")
    if len(seq) > 1:
        return "".join("(?:%s)" % lower(x, ctx) for x in seq)
    return lower_atom(expr, ctx)


def lower_and(parts, ctx):
    """`P & C1 & C2 ...`: the pattern operands first, each condition or group question at the stretch's end."""
    pats = [x for x in parts if not (IS_COND.match(x) or is_gq(x) or (x in BINDS and IS_COND.match(BINDS[x])))]
    rest = [x for x in parts if x not in pats]
    mk = fresh("k")
    chain = fresh("c") if OPT.get("array") == "chain" else None
    sub = ctx.sub(scopes=ctx.scopes + ((chain,) if chain else ()), chain=chain or ctx.chain)
    if sab("x77s3") and chain:
        sub = sub.sub(scopes=ctx.scopes, chain=ctx.cur)
    out = node_ref(("mark", mk)) + "(?:%s)" % lower(pats[0], sub)
    for q in pats[1:]:
        out += node_ref(("andpat", mk, p_alt(Src(lower(q, Ctx())))))
    zk = ctx.zero if (sab("x77s4") or sab("x77s20") or OPT.get("and_zero") == "definition") else mk
    for c in rest:
        if c in BINDS:
            c = BINDS[c]
        if is_gq(c):
            out += lower_gq(c, sub)
        else:
            out += lower_cond(c, ctx, zero_key=zk)
    return out


def use_definition(body, ctx, dname, params=None, mark=True):
    """A binding or macro body USED here: a scope of its own (reading (d)), entered afresh (reading (c) withdrawn)."""
    sc = fresh("s")
    held = set()
    sub = Ctx(scopes=ctx.scopes + (sc,), zero=sc, chain=None, name=dname, held=held, params=params or {}, caller=ctx)
    start = len(NAMED)
    text = lower(body, sub)
    for scope, nm in NAMED[start:]:
        if scope == sc and nm not in held and OPT.get("names", "sealed") == "sealed":
            raise CompileError("%s names a label it does not hold: %s" % (dname, nm))
    pre = node_ref(("enter", sc, sab("x77s7") or OPT.get("loop_c", False)))
    if mark:
        pre += node_ref(("mark", sc))
    ctx.held |= held
    return pre + "(?:%s)" % text


def parse_call(expr):
    mm = re.fullmatch(r"([\w.]+)\((.*)\)", expr, re.S)
    if not mm:
        return None
    pos, kw = [], {}
    for a in split_top(mm.group(2), ","):
        km = re.fullmatch(r"(\w+) = (.*)", a)
        if km and not a.startswith("("):
            kw[km.group(1)] = km.group(2)
        else:
            pos.append(a)
    return mm.group(1), pos, kw


def pick_macro(name, pos, kw):
    forms = MACROS.get(name)
    if not forms:
        return None
    for heads, body in forms:
        req = [h for h, d in heads if d is None]
        opt = {h: d for h, d in heads if d is not None}
        names = req + list(opt)
        given = names[:len(pos)]
        if len(pos) > len(names) or any(k not in names or k in given for k in kw):
            continue
        bound = dict(zip(given, pos))
        bound.update(kw)
        if all(h in bound for h in req) and set(bound) == set(names) - set(h for h in opt if h not in bound):
            for h, d in opt.items():
                bound.setdefault(h, d)
            if set(bound) == set(names):
                return bound, body
    raise CompileError("no body of %s fits the call" % name)


def lower_atom(expr, ctx):
    mm = re.fullmatch(r"\((.*)\)([+*?])", expr, re.S)
    if mm and not IS_COND.match(expr):
        return "(?:%s)%s" % (lower(mm.group(1), ctx), mm.group(2))
    mm = re.fullmatch(r"\[(\w+) = (.*)\]([+*?]?)", expr, re.S)
    if mm:
        name, e, q = mm.groups()
        ctx.held.add(name)
        return "(?<%s@%s>%s)%s" % (name, ",".join(ctx.scopes), lower(e, ctx), q)
    if is_gq(expr):
        return lower_gq(expr, ctx)
    if IS_COND.match(expr):
        return lower_cond(expr, ctx)
    if expr.startswith("(") and expr.endswith(")"):
        return lower(expr[1:-1], ctx)
    if expr.startswith("/") and expr.endswith("/"):
        return lower_literal(expr[1:-1], ctx)
    if expr.startswith('"') and expr.endswith('"'):
        return re.escape(expr[1:-1])
    if expr in ctx.params:
        return use_param(expr, ctx)
    call = parse_call(expr)
    if call and call[0] in MACROS:
        bound, body = pick_macro(*call)
        params = {h: (v, ctx) for h, v in bound.items()}
        if IS_COND.match(body) and OPT.get("bound", "inplace") == "inplace" and not sab("x77s9"):
            return lower_cond(body, ctx.sub(params=params))
        return use_definition(body, ctx, call[0], params)
    if expr in BINDS:
        body = BINDS[expr]
        if IS_COND.match(body) and OPT.get("bound", "inplace") == "inplace" and not sab("x77s9"):
            return lower_cond(body, ctx)                 # candidate (a): laid against the pattern it meets
        return use_definition(body, ctx, expr)
    raise CompileError("an undeclared name: " + expr)


def use_param(name, ctx):
    text, caller = ctx.params[name]
    if re.fullmatch(r"\d+", text):
        return text
    if sab("x77s10"):
        caller = ctx
    zero = caller.zero
    occ = OPT.get("occ_zero")
    pre = ""
    if occ == "body":
        zero = ctx.zero
    elif occ == "hit":
        zero = fresh("h")
        pre = node_ref(("mark", zero))
    if sab("x77s5") and occ == "body":
        zero = fresh("h")
        pre = node_ref(("mark", zero))
    return pre + lower(text, caller.sub(zero=zero))


def lower_literal(rx, ctx):
    out, i = [], 0
    while i < len(rx):
        if rx.startswith("${", i):
            j = close_hole(rx, i)
            body = rx[i + 2:j].strip()
            i = j + 1
            if body in ctx.params and re.fullmatch(r"\d+", ctx.params[body][0]):
                out.append(ctx.params[body][0])
            else:
                out.append("(?:%s)" % lower(body, ctx))
            continue
        if rx.startswith("(?<", i) and rx[i + 3] not in "=!":
            j = rx.index(">", i)
            name = rx[i + 3:j]
            ctx.held.add(name)
            CAPTURES.append((ctx.name, name))
            out.append("(?<%s@%s>" % (name, ",".join(ctx.scopes)))
            i = j + 1
            continue
        if rx[i] == "\\":
            out.append(rx[i:i + 2])
            i += 2
            continue
        out.append(rx[i])
        i += 1
    return "".join(out)


# ---- the library bodies, read from library.md
def lib_body(pattern, text=LIB):
    mm = re.search(pattern, text)
    assert mm, pattern
    return mm.group(1)


OCC_BODY = re.search(r"`occurrences\(x, min = \d+\)` is the lazy-gap loop `(/.*?/)`", LIB).group(1)
REPEATS = re.findall(r"`repeat\((x(?:, \w+)+)\) :=\s+(/.*?/)`", ws(LIB))
RXDIGIT = lib_body(r"`rx\.digit := (/.*?/)`")
RXDIGITS = lib_body(r"`rx\.digits := (rx\.repeat\(rx\.digit, min = 1\))`")
ANYCASE_BODY = lib_body(r"`any_case\(rx\) := (/.*?/)`")


def base_binds():
    BINDS.clear()
    MACROS.clear()
    NODES.clear()
    CAPTURES.clear()
    del NAMED[:]
    COUNTER[0] = 0
    MACROS["occurrences"] = [([("x", None), ("min", "0")], OCC_BODY)]
    MACROS["rx.repeat"] = [([(h.strip(), None) for h in heads.split(",")], body) for heads, body in REPEATS]
    BINDS["rx.digit"] = RXDIGIT
    BINDS["rx.digits"] = RXDIGITS


def define(line):
    head, body = [x.strip() for x in line.split(":=", 1)]
    mm = re.fullmatch(r"([\w.]+)\((.*)\)", head)
    if mm:
        heads = []
        for h in split_top(mm.group(2), ","):
            hm = re.fullmatch(r"(\w+)(?: = (.*))?", h)
            heads.append((hm.group(1), hm.group(2)))
        MACROS[mm.group(1)] = [(heads, body)]
    else:
        BINDS[head] = body


def prog(expr, binds=(), **opts):
    base_binds()
    OPT.clear()
    OPT.update(opts)
    for b in binds:
        define(b)
    top = Ctx()
    text = lower(expr, top)
    Pg = Prog(text)
    Pg.expr = expr
    return Pg


def refused(expr, binds=(), **opts):
    try:
        prog(expr, binds, **opts)
        return None
    except CompileError as e:
        return str(e)


LINES = []


def doc_line(L, tag):
    LINES.append((tag, L))
    return L


def show(label, expr, binds, wh, sr, fa, tail, tag, **opts):
    try:
        Pg = prog(expr, binds, **opts)
    except CompileError as e:                    # a refused program prints as refused; its DOC lookup then fails
        L = (label + ": " if label else "") + "REFUSED (%s)" % e + tail
        return doc_line(L, tag) if tag else L
    L = (label + ": " if label else "") + fmt(Pg, wh, sr, fa) + tail
    return doc_line(L, tag) if tag else L


# ---------------------------------------------------------------- copied from predfix77_model.py (end)
import subprocess                                            # noqa: E402

START = "1e0384941"                                          # the lane's starting commit (lane/pred-rev28)


def git_show(rel):
    return subprocess.run(["git", "-C", W, "show", "%s:%s" % (START, rel)], capture_output=True, text=True,
                          check=True).stdout


OLD = {f: git_show("docs/design/predicates/" + f) for f in
       ("core.md", "library.md", "core_details.md", "library_details.md", "parked.md", "parked_details.md")}


# ================================================================== EXTENSIONS (lane predbound)
_m_base = m


def m(node, s, pos, st, k):                                  # noqa: F811
    t = node[0]
    if t == "setv":                                          # META: `w.index` set to the member's position
        lab, log = dict(st.lab), st.log
        for key in keys_of(node[1]):
            lab[key] = node[2]
            log = log + (("set", key, node[2], pos),)
        return k(pos, St(lab, log, st.marks, st.seen))
    if t == "valrx":                                         # a value where an rx stands: its one string
        v = node[1](s, pos, st)
        if v is None or not s.startswith(v, pos):
            return None
        return k(pos + len(v), st)
    return _m_base(node, s, pos, st, k)


def cond_holds(node, s, pos, st):                            # noqa: F811
    _, neg, entries = node
    res = True
    for key, val in entries:
        if key[0] == "zero":
            v = s[st.marks[key[1]]:pos] if key[1] in st.marks else None
        elif key[0] == "val":
            v = key[1](s, pos, st)
            if v is None and sab("s8"):
                continue
        else:
            v = st.lab.get(key[1])
        if not val_ok(v, val, st.lab):
            res = False
            break
    return (not res) if neg else res


_val_ok_base = val_ok
CMP = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, "<": lambda a, b: a < b, ">": lambda a, b: a > b,
       "==": lambda a, b: a == b}


def val_ok(v, val, lab):                                     # noqa: F811
    if val[0] == "cmpv":
        b = val[2](None, None, St(lab, (), {}, frozenset()))
        if v is None or b is None or not CANON.fullmatch(v) or not CANON.fullmatch(b):
            return False
        return CMP[val[1]](int(v), int(b))
    if val[0] == "all":
        return all(val_ok(v, x, lab) for x in val[1])
    return _val_ok_base(v, val, lab)


def top_split(text, ops):
    """[operand, op, operand, ...] at depth 0 (outside (), [], "..", /../)."""
    out, depth, last, i, in_q, in_rx = [], 0, 0, 0, False, False
    while i < len(text):
        c = text[i]
        if in_q:
            in_q = c != '"'
        elif in_rx:
            if c == "\\":
                i += 2
                continue
            in_rx = c != "/"
        elif c == '"':
            in_q = True
        elif c == "/":
            in_rx = True
        elif c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif depth == 0:
            hit = next((o for o in ops if text.startswith(o, i)), None)
            if hit:
                out += [text[last:i].strip(), hit.strip()]
                i += len(hit)
                last = i
                continue
        i += 1
    return out + [text[last:].strip()]


def strip_parens(t):
    while t.startswith("(") and t.endswith(")"):
        depth = 0
        for i, c in enumerate(t):
            depth += c == "("
            depth -= c == ")"
            if depth == 0 and i < len(t) - 1:
                return t
        t = t[1:-1].strip()
    return t


def arith(op, a, b):
    if a is None or b is None or not CANON.fullmatch(a) or not CANON.fullmatch(b):
        return None
    x, y = int(a), int(b)
    if op == "+":
        r = x + y + (1 if sab("s2") else 0)
    elif op == "-":
        r = x - y
    elif op == "*":
        r = x * y
    else:
        if y == 0:
            return None
        r = x % y
    return None if r < 0 else str(r)


def value_getter(text, ctx):
    """A VALUE expression -> getter(s, pos, st): its one string, or None (nothing)."""
    text = strip_parens(text.strip())
    for ops in ((" + ", " - "), (" * ", " % ")):
        parts = top_split(text, ops)
        if len(parts) > 1:
            gs = [value_getter(parts[0], ctx)]
            opl = []
            for j in range(1, len(parts), 2):
                opl.append(parts[j])
                gs.append(value_getter(parts[j + 1], ctx))
            if sab("s12") and opl == ["-"] and re.fullmatch(r"\d+", parts[0]):
                gs[0] = (lambda c: lambda s, pos, st: c)(str(int(parts[0]) - 1))

            def g(s, pos, st, gs=gs, opl=opl):
                v = gs[0](s, pos, st)
                for op, gg in zip(opl, gs[1:]):
                    v = arith(op, v, gg(s, pos, st))
                return v
            return g
    mm = re.fullmatch(r"\$([\w.]+)", text)
    if mm:
        name = mm.group(1)
        NAMED.append((ctx.cur, name))
        key = "%s@%s" % (name, ctx.cur)
        if sab("s9"):
            return lambda s, pos, st: st.lab.get(key, "0")
        return lambda s, pos, st: st.lab.get(key)
    if re.fullmatch(r"\d+", text):
        return lambda s, pos, st: text
    mm = re.fullmatch(r'"([^"]*)"', text)
    if mm:
        return lambda s, pos, st: mm.group(1)
    if text.startswith("[") and text.endswith("]"):
        mem = split_top(text[1:-1], ",")
        if len(mem) > 1 and not sab("s10"):
            raise CompileError("a value of several strings left of `:`: %s" % text)
        return value_getter(mem[0], ctx)
    mm = re.fullmatch(r"count\((.*)\)", text)
    if mm:
        return count_getter(mm.group(1).strip(), ctx)
    raise CompileError("not a value: " + text)


def count_getter(arg, ctx):
    ineg = arg.startswith("NOT ")
    if ineg:
        arg = arg[4:].strip()
    entries = split_top(arg[1:-1], ",")
    if len(entries) != 1:
        raise CompileError("count of several entries: not stated")
    em = ENTRY.fullmatch(entries[0])
    name, v = em.group(1), parse_value(em.group(3), ctx)
    NAMED.append((ctx.cur, name))
    sc = array_scope(ctx)
    key = "%s@%s" % (name, sc)

    def g(s, pos, st):
        hits = [val_ok(x, v, st.lab) for x in settings(st.log, key, sc)]
        return str(sum((not h) if ineg else h for h in hits))
    return g


_parse_value_base = parse_value
BETWEEN = lib_body(r"`between\(lo, hi\)` is the comparison set `(.*?)`")


def parse_value(v, ctx):                                     # noqa: F811
    v = v.strip()
    parts = split_top(v, " & ")
    if len(parts) > 1:
        return ("all", [parse_value(x, ctx) for x in parts])
    mm = re.fullmatch(r"(>=|<=|<|>|==) ?(.+)", v)
    if mm and not re.fullmatch(r"\d+", mm.group(2)):
        return ("cmpv", mm.group(1), value_getter(mm.group(2), ctx))
    mm = re.fullmatch(r"between\((\d+), (\d+)\)", v)
    if mm:
        return parse_value(BETWEEN.replace("lo", mm.group(1)).replace("hi", mm.group(2)), ctx)
    try:
        return _parse_value_base(v, ctx)
    except CompileError:
        if OPT.get("lenient"):                               # the sweep: an owner placeholder (`blah`) as a set
            return ("eq", v)
        raise


def split_colon(e):
    """An entry `left: right` split at its top-level `: ` (None when there is none)."""
    parts = top_split(e, (": ",))
    if len(parts) < 3:
        return None
    return parts[0], ": ".join(parts[2::2])


LABEL_LEFT = re.compile(r"[\w.]+")


def is_cond(x):
    """A condition: `(left: S, ...)` or `NOT (...)`, its first entry with a top-level `: `."""
    x = x.strip()
    if _IS_COND0.match(x):
        return True
    if x.startswith("NOT "):
        x = x[4:].strip()
    if not (x.startswith("(") and x.endswith(")")) or strip_parens(x) == x:
        return False
    inner = x[1:-1]
    first = split_top(inner, ",")[0]
    return split_colon(first) is not None


class _IsCond:
    def match(self, x):
        return is_cond(x)


_IS_COND0 = IS_COND
IS_COND = _IsCond()


def lower_cond(text, ctx, zero_key=None):                    # noqa: F811
    text = text.strip()
    neg = text.startswith("NOT ")
    if neg:
        text = text[4:].strip()
    assert text.startswith("(") and text.endswith(")"), text
    entries = []
    for e in split_top(text[1:-1], ","):
        left, right = split_colon(e.strip())
        if left == "0":
            entries.append((("zero", zero_key or ctx.zero), parse_value(right, ctx)))
        elif LABEL_LEFT.fullmatch(left):                     # reading (d): a bare name or path stays a LABEL
            NAMED.append((ctx.cur, left))
            entries.append((("lab", "%s@%s" % (left, ctx.cur)), parse_value(right, ctx)))
        else:                                                # count-in-set (b): any other expression is a VALUE
            entries.append((("val", value_getter(left, ctx)), parse_value(right, ctx)))
    return node_ref(("cond", neg, entries))


def is_value_expr(expr):
    return (len(top_split(expr, (" + ", " - ", " * ", " % "))) > 1 or re.fullmatch(r"\$[\w.]+", expr) is not None
            or re.fullmatch(r"count\(.*\)", expr) is not None)


def is_set_body(body):
    """A SET bound alone (reading (b)): a comparison, a string, `between`, an `&` of sets; names no label."""
    if body.startswith("/") or body.startswith("["):
        return False
    lenient = OPT.pop("lenient", None)
    try:
        v = parse_value(body, Ctx())
    except (CompileError, AttributeError, AssertionError, KeyError, ValueError):
        return False
    finally:
        if lenient:
            OPT["lenient"] = lenient
    return v[0] in ("eq", "cmp", "all") and not sab("s3")


def use_definition(body, ctx, dname, params=None, mark=True):    # noqa: F811
    """As predfix77's, the label check reading a path by its base name (`mname.index` is mname's)."""
    sc = fresh("s")
    held = set()
    sub = Ctx(scopes=ctx.scopes + (sc,), zero=sc, chain=None, name=dname, held=held, params=params or {}, caller=ctx)
    start = len(NAMED)
    text = lower(body, sub)
    for scope, nm in NAMED[start:]:
        base = nm.split(".")[0]
        if scope == sc and base not in held:
            raise CompileError("%s names a label it does not hold: %s" % (dname, nm))
    pre = node_ref(("enter", sc, False))
    if mark:
        pre += node_ref(("mark", sc))
    if not sab("s7"):
        ctx.held |= held
    return pre + "(?:%s)" % text


_lower_atom_base = lower_atom


def lower_atom(expr, ctx):                                   # noqa: F811
    expr = expr.strip()
    mm = re.fullmatch(r"\[(\w+) = \[(.*)\]\]", expr, re.S)
    if mm:                                                   # META: an array under a part label
        name, members = mm.group(1), split_top(mm.group(2), ",")
        ctx.held.add(name)
        full = ",".join(ctx.scopes)
        alts = []
        for i, x in enumerate(members):
            idx = str(i if sab("s17") else i + 1)
            alts.append("(?:%s)%s" % (lower(x, ctx), node_ref(("setv", "%s.index@%s" % (name, full), idx))))
        return "(?<%s@%s>%s)" % (name, full, "|".join(alts))
    if expr.startswith("[") and expr.endswith("]") and not re.match(r"\[\w+ = ", expr):
        return "|".join("(?:%s)" % lower(x, ctx) for x in split_top(expr[1:-1], ","))
    if is_value_expr(expr) and not is_cond(expr):
        return node_ref(("valrx", value_getter(expr, ctx)))
    if expr in BINDS and is_cond(BINDS[expr]):
        body = BINDS[expr]
        if sab("s4"):
            return lower_cond(body, ctx)
        zb = OPT.get("zero_bound", "inplace")
        if sab("s11") and OPT.get("which") == "zero-a":
            zb = "sealed"
        before = len(NAMED)
        lower_cond(body, Ctx(scopes=("probe",)))                 # what the body names
        named = [n for sc, n in NAMED[before:] if sc == "probe"]
        del NAMED[before:]
        if named:                                            # the ruling (normally refused at the binding)
            return use_definition(body, ctx, expr)
        if zb == "error":
            raise CompileError("%s: a condition on `0` bound alone (zero-condition-binding, candidate)" % expr)
        if zb == "inplace":
            return lower_cond(body, ctx)
        return use_definition(body, ctx, expr)
    call = parse_call(expr)
    if call and call[0] in MACROS and is_cond(pick_macro(*call)[1]):
        bound, body = pick_macro(*call)
        params = {h: (v, ctx) for h, v in bound.items()}
        return use_definition(body, ctx, call[0], params)
    return _lower_atom_base(expr, ctx)


_lower_and_base = lower_and


def lower_and(parts, ctx):                                   # noqa: F811
    """As predfix77's; a pattern operand after the first also lends its labels to the binding's HELD set (the
    ruling's "no references in the binding"); the model does not read those labels (no printed line needs it)."""
    pats = [x for x in parts if not (IS_COND.match(x) or is_gq(x) or (x in BINDS and IS_COND.match(BINDS[x])))]
    for q in pats[1:]:
        keep = len(NAMED)
        lower(q, ctx.sub())
        del NAMED[keep:]
    return _lower_and_base(parts, ctx)


_use_param_base = use_param


def use_param(name, ctx):                                    # noqa: F811
    if sab("s6"):
        text, _ = ctx.params[name]
        return lower(text, ctx)
    return _use_param_base(name, ctx)


HEADS = {}


def define(line):                                            # noqa: F811
    head, body = [x.strip() for x in line.split(":=", 1)]
    mm = re.fullmatch(r"([\w.]+)\((.*)\)", head)
    if mm:
        heads = []
        for h in split_top(mm.group(2), ","):
            hm = re.fullmatch(r"(\w+)(?: = (.*))?", h)
            heads.append((hm.group(1), hm.group(2)))
        MACROS[mm.group(1)] = [(heads, body)]
        HEADS[line] = (mm.group(1), heads, body)
    else:
        BINDS[head] = body
        HEADS[line] = (head, None, body)


def binding_check(line):
    """THE RULING, at the binding: lower the body once in a scope of its own, every parameter a placeholder;
    a label it names that no pattern in it holds (nor a pattern it uses) is a compile error. None when legal."""
    name, heads, body = HEADS[line]
    if heads is None and is_set_body(body):
        return None
    params = {h: ("//", Ctx()) for h, _ in (heads or [])}
    keep = len(NAMED)
    try:
        use_definition(body, Ctx(), name, params)
        if heads is None and is_cond(body) and OPT.get("zero_bound") == "error":
            return "%s: a condition on `0` bound alone (zero-condition-binding, candidate)" % name
        return None
    except CompileError as e:
        return str(e)
    finally:
        del NAMED[keep:]


def prog(expr, binds=(), **opts):                            # noqa: F811
    base_binds()
    OPT.clear()
    OPT.update(opts)
    for b in binds:
        define(b)
    if not sab("s5") and not sab("s4"):
        for b in binds:
            r = binding_check(b)
            if r:
                raise CompileError("at the binding `%s`: %s" % (b, r))
    top = Ctx()
    text = lower(expr, top)
    Pg = Prog(text)
    Pg.expr = expr
    return Pg


def piece(text, tag):
    i = text.index("[%s]" % tag)
    i = text.rindex("\n### ", 0, i)
    j = text.find("\n### ", i + 1)
    k = text.find("\n## ", i + 1)
    j = min(x for x in (j, k, len(text)) if x > 0)
    return text[i:j]


def answer_part(L):
    mm = re.search(r"WHOLE .*?\] ", L + " ")
    return mm.group(0).strip() if mm else None


def printed(text, needle):
    """The one printed line of `text` holding `needle`."""
    ls = [x for x in text.split("\n") if needle in x and "WHOLE " in x]
    assert len(ls) == 1, (needle, ls)
    return ls[0]


def pop_whole(Pg, pop_, direct):
    return sum(1 for t in pop_ if Pg.whole(t) != direct(t)) if Pg is not None else -1


def safe_prog(expr, binds=(), **opts):
    """prog(), or None where the program is refused (a check then fails instead of stopping the run)."""
    try:
        return prog(expr, binds, **opts)
    except CompileError:
        return None


def safe_ndiff(Pg, R, pop_):
    return ndiff(answers(Pg, pop_), answers(R, pop_)) if Pg is not None else ("refused",)


# library bodies, read from library.md as it stands (the fold's)
CHARS = lib_body(r"`chars := (\(\[ch = .*?\]\)\*)`")
LENGTH = lib_body(r"`(length\(S\) := chars & .*?)`")
MONTHS = lib_body(r"`(months := \[mname = \[.*?\]\])`", ws(LIB))
MONTHNUM = lib_body(r"`(month_numbered\(S\) := months & .*?)`")
print("== library bodies (library.md): chars %s ; %s ; %s ; between: %s" % (CHARS, LENGTH, MONTHNUM, BETWEEN))
print("== %s" % MONTHS)


# ================================================================== the checks
# ---------------------------------------------------------------- CONTROL (predfix77's, re-run on the extended matcher)
print("== CONTROL: lowered programs without conditions against python `re` on hand regexes")
POPA = pop("ab;7", 4)
c1 = ndiff(answers(prog('"ab" | "a"'), POPA), answers(Re(r"ab|a"), POPA))
c2 = ndiff(answers(prog("/(?:a|ab)??;/"), POPA), answers(Re(r"(?:a|ab)??;"), POPA))
c3 = ndiff(answers(prog('rx.repeat("a" SEQ ";", min = 2, max = 2)'), POPA), answers(Re(r"(?:a;){2,2}"), POPA))
check("CONTROL", (c1, c2, c3) == ((0, 0, 0),) * 3,
      "of %d texts over `ab;7`: `\"ab\" | \"a\"` %s, `(?:a|ab)??;` %s, rx.repeat(.., min = 2, max = 2) %s"
      % (len(POPA), c1, c2, c3))

# ---------------------------------------------------------------- REFUSE: the ruling, each refused form
print("== REFUSE: a condition or computed value bound alone naming a label no pattern in its binding holds")
REF = [  # (binding, a program using it)
    ("late := (h: >5)", "/(?<h>\\d)/ & late"),                                   # his `A := (x: blah)`
    ("A := /x/ & (y: >5)", "/(?<y>\\d)/ SEQ A"),                                 # his `A := /x/ & (y: blah)`
    ("sum := $a + $b", "/(?<a>\\d)\\+(?<b>\\d)/ & (sum: <10)"),
    ('n := count((d: "7"))', "/(?:(?<d>\\d),)+/ & (n: ==2)"),
    ('n := count(NOT (d: "7"))', "/(?:(?<d>\\d)?,)+/ & (n: ==0)"),
    ("nchars := count((ch: /(?s:.)/))", "chars & (nchars: ==3)"),
    ("mnum := $mname.index", "months & (mnum: between(1, 6))"),
    ("c := NOT (h: /\\d/) | (n: >= $h)", "/(?:(?=(?<n>\\d))${c}(?<h>\\d);)*/"),
    ("lt5(S) := (h: S)", "/(?<h>\\d)${lt5(<5)}/"),                              # a macro whose body is one (a reading)
    ("inner := /x${(h: <5)}/", "/(?<h>\\d)${inner}/"),                          # case 1 (ruled 2026-11-21)
]
LIBB = ["chars := " + CHARS, MONTHS]
ref = []
for b, e in REF:
    r = refused(e, LIBB + [b])
    ref.append((b, r))
    print("   %-36s %s" % (b, r))
E_LATE = "/(?<h>\\d)/ & (h: >5)"
TL5 = ["7", "3"], "x3 7", "7 3 9 66"
L_INPL = show("Written in place", E_LATE, [], *TL5,
              " (`%s`; bound alone, `/(?<h>\\d)/ & late` with late := `(h: >5)` is a compile error at `late`)" % E_LATE,
              "bound-condition")
print("   " + L_INPL)
check("REFUSE", all(r and "at the binding" in r and "does not hold" in r for _, r in ref),
      "%d bindings, each refused at the binding naming its label: %s" % (len(ref), [b for b, r in ref if r]))

# ---------------------------------------------------------------- SETBOUND: reading (b)
print("== SETBOUND: a SET bound alone, `late := >5`, used `(h: late)` (reading (b))")
L_SET = show("A set bound alone", "/(?<h>\\d)/ & (h: late)", ["late := >5"], *TL5,
             " (`/(?<h>\\d)/ & (h: late)`, late := `>5`)", "bound-condition")
print("   " + L_SET)
REC_A = "WHOLE `7` HOLDS, `3` FAILS / SEARCHED `x3 7` `7`@3 / FIND-ALL `7 3 9 66` [`7`@0, `9`@4, `6`@6, `6`@7]"
POP5 = pop("37 9", 3)
sb = safe_ndiff(safe_prog("/(?<h>\\d)/ & (h: late)", ["late := >5"]), Re(r"[6-9]"), POP5)
check("SETBOUND", answer_part(L_SET) == answer_part(L_INPL) and ws(REC_A) in RECORD_WS and REC_A in L_SET
      and sb == (0, 0, 0),
      "the set bound alone answers as written in place and as the record's pasted `[6-9]` line; of %d texts over "
      "`37 9` against `[6-9]` %s" % (len(POP5), sb))

# ---------------------------------------------------------------- ATBINDING: reading (e)
print("== ATBINDING: the error is at the binding, an unused binding included (reading (e))")
r_unused = refused("/(?<h>\\d)/", ["late := (h: >5)"])
r_unused_sum = refused("/(?<a>\\d)\\+(?<b>\\d)/", ["sum := $a + $b"])
print("   unused `late`: %s ; unused `sum`: %s" % (r_unused, r_unused_sum))
check("ATBINDING", bool(r_unused) and "at the binding `late := (h: >5)`" in r_unused and bool(r_unused_sum)
      and "under construction" not in r_unused,
      "a program that never uses the binding is refused at it: %s" % r_unused)

# ---------------------------------------------------------------- INPLACE: reading (a)
print("== INPLACE: a condition written in place, an argument included, is unchanged (reading (a))")
BI = ["inner(c) := /x${c}/"]
L_PC = show("Passing the condition", "/(?<h>\\d)${inner((h: <5))}/", BI, ["3x", "7x"], "7x 3x", "3x 7x 4x",
            " (`/(?<h>\\d)${inner((h: <5))}/`, inner(c) := `/x${c}/`)", "nested-scope")
BZ = ["B(rx) := /${rx}xx/"]
EZ = "/\\d/ SEQ B((0: /\\d/))"
L_ZA = show("An argument", EZ, BZ, ["5xx", "xx"], "a5xx", "5xx 55xx", " (`%s`, B(rx) := `/${rx}xx/`)" % EZ,
            "match-so-far")
print("   " + L_PC)
print("   " + L_ZA)
check("INPLACE", "REFUSED" not in L_PC + L_ZA and L_PC in OLD["core.md"] and L_ZA in OLD["core.md"],
      "both lines legal and the same as printed at %s" % START)

# ---------------------------------------------------------------- LEGAL: reading (g)
print("== LEGAL: a binding whose body USES a pattern holding the label is legal (reading (g))")
YEAR = "year := /(?<_v>\\d{4})/ & (_v: >= 2000)"
L_YEAR = show("A binding that holds its label", "year", [YEAR], ["2001", "1999"], "x1999 2024", "2024 1999 2000",
              " (`year`, year := `/(?<_v>\\d{4})/ & (_v: >= 2000)`)", "bound-condition")
print("   " + L_YEAR)
base_binds()
OPT.clear()
for b in LIBB + [LENGTH, MONTHNUM, YEAR]:
    define(b)
leg = [(b, binding_check(b)) for b in LIBB + [LENGTH, MONTHNUM, YEAR]]
for b, r in leg:
    print("   %-60s %s" % (b[:60], r or "legal"))
POPY = ["".join(t) for t in itertools.product("1290", repeat=4)]
yd = pop_whole(prog("year", [YEAR]), POPY, lambda t: int(t) >= 2000)
check("LEGAL", all(r is None for _, r in leg) and yd == 0 and "REFUSED" not in L_YEAR,
      "chars, months, length, month_numbered, year legal at their bindings ; `year` WHOLE against the direct "
      "`>= 2000` over %d four-digit texts: %d differ" % (len(POPY), yd))

# ---------------------------------------------------------------- FIVE: reading (c), the five definitions in place
print("== FIVE: the refused definitions written in place; every printed line unchanged")
FIVES = [  # (piece, the old line's needle in the OLD file, the file, the new program, new tail, direct WHOLE)
    ("pass-start-read", "c := `NOT (h: /\\d/) | (n: >= $h)`", "core.md",
     "/(?:(?=(?<n>\\d))${NOT (h: /\\d/) | (n: >= $h)}(?<h>\\d);)*/", None,
     (pop("3471;", 6), lambda t: re.fullmatch(r"(?:\d;)*", t) is not None
      and all(a <= b for a, b in zip(re.findall(r"\d", t), re.findall(r"\d", t)[1:])))),
    ("computed-labels", "sum := `$a + $b`", "core.md", "/(?<a>\\d)\\+(?<b>\\d)/ & (($a + $b): <10)", None,
     (["%d+%d" % (a, b) for a in range(10) for b in range(10)] + pop("1+9", 3),
      lambda t: re.fullmatch(r"\d\+\d", t) is not None and int(t[0]) + int(t[2]) < 10)),
    ("array-vs-passes", 'n := `count(NOT (d: "7"))`', "core.md", '/(?:(?<d>\\d)?,)+/ & (count(NOT (d: "7")): ==0)',
     None, (pop("17,", 5), lambda t: re.fullmatch(r"(?:\d?,)+", t) is not None and set(re.findall(r"\d", t)) <= {"7"})),
    ("count", 'n := `count((d: "7"))`', "library.md", '/(?:(?<d>\\d),)+/ & (count((d: "7")): ==2)', None,
     (pop("17,", 6), lambda t: re.fullmatch(r"(?:\d,)+", t) is not None and t.count("7") == 2)),
    ("length", "as a program: `chars & (nchars: ==3)`", "library.md", "length(==3)",
     " (`length(==3)` as a program: `chars & (count((ch: /(?s:.)/)): ==3)`)",
     (pop("ab\n", 4), lambda t: len(t) == 3)),
    ("month-numbered", "(`month_numbered(between(1, 6))`)", "library.md", "month_numbered(between(1, 6))", None,
     (["Jan", "January", "Jun", "June", "Jul", "July", "Dec", "Ma", "May", "Mar", "March", "Sept", "Sep"],
      lambda t: re.fullmatch(r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?", t) is not None)),
]
L_FIVE, five = {}, []
for tag, needle, f, expr, tail, (popf, direct) in FIVES:
    old = printed(OLD[f], needle)
    pre = old[:old.index("WHOLE ")]
    mm = re.search(r"WHOLE (.*?) / SEARCHED `(.*?)` .*? / FIND-ALL `(.*?)` \[", old)
    wh = re.findall(r"`([^`]*)` (?:HOLDS|FAILS)", mm.group(1))
    sr, fa = mm.group(2), mm.group(3)
    binds = LIBB + [LENGTH, MONTHNUM]
    if tail is None:
        tail = " (`%s`)" % expr
    L = show(pre[:-2] if pre else "", expr, binds, wh, sr, fa, tail, tag)
    if tag == "length":                                         # the program form, also run
        L2 = show(pre[:-2] if pre else "", "chars & (count((ch: /(?s:.)/)): ==3)", binds, wh, sr, fa, tail, None)
    else:
        L2 = L
    Pg = safe_prog(expr, binds)
    d = pop_whole(Pg, popf, direct)
    same = answer_part(L) == answer_part(old) == answer_part(L2)
    five.append((tag, same, d))
    L_FIVE[tag] = L
    print("   [%s] old: %s" % (tag, old.strip()))
    print("   [%s] new: %s" % (tag, L))
    print("   [%s] answers the same: %s ; WHOLE against the direct rule: %d of %d differ" % (tag, same, d, len(popf)))
check("FIVE", all(s and d == 0 for _, s, d in five) and len(five) == 6,
      "six printed lines (five definitions; `n` printed twice): %s" % five)

# ---------------------------------------------------------------- SUMALT: `(a: <(10 - $b))`, re-run
print("== SUMALT: `(a: <(10 - $b))` against `(($a + $b): <10)` on the 100 digit pairs")
PAIRS = ["%d+%d" % (a, b) for a in range(10) for b in range(10)]
PA = prog("/(?<a>\\d)\\+(?<b>\\d)/ & (a: <(10 - $b))")
PS = prog("/(?<a>\\d)\\+(?<b>\\d)/ & (($a + $b): <10)")
sa = sum(1 for t in PAIRS if PA.whole(t) != PS.whole(t))
held = sum(1 for t in PAIRS if PS.whole(t))
check("SUMALT", sa == 0 and held == 55, "%d of %d pairs differ ; the sum form holds on %d (direct count 55)"
      % (sa, len(PAIRS), held))

# ---------------------------------------------------------------- NOTHING: reading (d), a value that yields nothing
print("== NOTHING: a value that yields nothing fails the entry, as an unset label does; NOT holds on it")
EN1 = "/(?<a>\\d)/ & (($a - 5): >= 0)"
EN2 = "/(?<a>\\d)/ & NOT (($a - 5): >= 0)"
TN = ["7", "3"], "x3 7", "3 7 5 1"
L_N1 = show("Nothing fails the entry", EN1, [], *TN, " (`%s`: `3 - 5` is nothing)" % EN1, "value-left")
L_N2 = show("NOT holds on nothing", EN2, [], *TN, " (`%s`)" % EN2, "value-left")
print("   " + L_N1)
print("   " + L_N2)
POPN = pop("0357x", 2)
n1 = ndiff(answers(prog(EN1), POPN), answers(Re(r"[5-9]"), POPN))
n2 = ndiff(answers(prog(EN2), POPN), answers(Re(r"[0-4]"), POPN))
un = prog("/(?<a>\\d)?x/ & (($a + 1): >= 0)").whole("x"), prog("/(?<a>\\d)?x/ & NOT (($a + 1): >= 0)").whole("x")
check("NOTHING", n1 == n2 == (0, 0, 0) and un == (False, True),
      "of %d texts over `0357x`: against `[5-9]` %s, NOT against `[0-4]` %s ; an unset input on `x`: the entry %s, "
      "NOT %s" % (len(POPN), n1, n2, un[0], un[1]))

# ---------------------------------------------------------------- SAMEREAD: reading (d), `($h: S)` and `(h: S)`
print("== SAMEREAD: `($h: S)` and `(h: S)` answer alike in every mode")
sr_ = []
POPR = pop("37x;", 4)
for P0 in ("/(?<h>\\d)?x/", "/(?:(?<h>\\d)?;)+/", "/(?:${(h: <5)}(?<h>\\d)?;)+/"):
    for S in ("<5", '"3"', "/[0-4]/"):
        for neg in ("", "NOT "):
            a = answers(prog("%s & %s($h: %s)" % (P0, neg, S)), POPR)
            b = answers(prog("%s & %s(h: %s)" % (P0, neg, S)), POPR)
            sr_.append(ndiff(a, b))
EH = "/(?<h>\\d)?x/ & ($h: <5)"
L_SR = show("A read on the left", EH, [], ["3x", "x", "7x"], "7x 3x", "3x x 7x", " (`%s`, as `(h: <5)`)" % EH,
            "value-left")
print("   " + L_SR)
check("SAMEREAD", all(x == (0, 0, 0) for x in sr_) and len(sr_) == 18,
      "18 programs (3 patterns, 3 sets, with and without NOT) over %d texts of `37x;`: every pair 0 / 0 / 0" % len(POPR))

# ---------------------------------------------------------------- SEVERAL: reading (d), a value of several strings
print("== SEVERAL: a value of several strings left of `:` is a compile error for now")
r_sev = refused('/(?<h>\\d)/ & (($h + ["1", "2"]): <5)')
r_one = refused('/(?<h>\\d)/ & (($h + ["1"]): <5)')
print("   several: %s ; one: %s" % (r_sev, r_one))
check("SEVERAL", bool(r_sev) and "several strings" in r_sev and r_one is None, "refused: %s" % r_sev)

# ---------------------------------------------------------------- ZERO: the open zero-condition-binding
print("== ZERO: `c := (0: rx.digit)` bound alone (zero-condition-binding: LEFT OPEN), both candidates")
BC = ["c := (0: rx.digit)"]
TB = ["7x", "77x"], "a7x", "7x 12x 8x"
L_BA = show("(a) where it is used", "/\\d${c}x/", BC, *TB, " (`/\\d${c}x/`, c := `(0: rx.digit)`)", "zero-binding",
            zero_bound="inplace", which="zero-a")
L_BB = show("(b) sealed, its own `0`", "/\\d${c}x/", BC, *TB, " (the same program)", "zero-binding",
            zero_bound="sealed")
r_ze = refused("/\\d${c}x/", BC, zero_bound="error")
HX1, HX2 = "/\\d${(0: 5)}/", "/.${A & (0: 5)}/"
L_HX1 = show("His first example", HX1, [], ["5", "7"], "x75", "5 7 55", " (`A := %s`)" % HX1, "zero-binding")
L_HX2 = show("His second example", HX2, ["A := /\\d/"], ["x5", "x7", "55"], "a7 b5", "x5 y7 55",
             " (`C := %s`, A := `/\\d/`)" % HX2, "zero-binding")
for L in (L_BA, L_BB, L_HX1, L_HX2):
    print("   " + L)
print("   (b) as asked, a compile error: %s" % r_ze)
POPB = pop("17x", 4)
b1 = ndiff(answers(prog("/\\d${c}x/", BC, zero_bound="inplace", which="zero-a"), POPB), answers(Re(r"\dx"), POPB))
b2 = ndiff(answers(prog("/\\d${c}x/", BC, zero_bound="sealed"), POPB), answers(Re(r"(?!)"), POPB))
check("ZERO", b1 == b2 == (0, 0, 0) and bool(r_ze) and L_BA in OLD["core.md"] and L_BB in OLD["core.md"]
      and L_HX1 in OLD["core.md"] and L_HX2 in OLD["core.md"],
      "of %d texts over `17x`: (a) against `\\dx` %s, sealed against `(?!)` %s ; the lines as printed at %s"
      % (len(POPB), b1, b2, START))

# ---------------------------------------------------------------- META: a path left of `:` stays a label
print("== META: `.index` read as a label path (core/values/metadata), unchanged")
EM = "/${days}/ & (w.index: >= 2)"
L_ME = show("", EM, ["days := [w = [/Mon/, /Tue/, /Wed/]]"], ["Tue", "Mon"], "Mon Wed", "Tue Mon Wed",
            " (`%s`, days := `[w = [/Mon/, /Tue/, /Wed/]]`)" % EM, "metadata")
print("   " + L_ME)
check("META", L_ME in OLD["core.md"] and L_FIVE["month-numbered"].startswith("WHOLE `Jun` HOLDS, `Jul` FAILS"),
      "the metadata line as printed at %s, and month_numbered's" % START)

# ---------------------------------------------------------------- SWEEP: reading (h)
print("== SWEEP: every binding printed in the six files, checked at its binding (start tree and now)")
B1 = re.compile(r"`([A-Za-z_][\w.]*(?:\([^`()]*\))?) := ([^`]+)`")
B2 = re.compile(r"\b([A-Za-z_][\w.]*(?:\([^`()]*\))?) := `([^`]+)`")
ENV = LIBB + [LENGTH, MONTHNUM, "isodate := /(?<year>\\d{4})-(?<month>\\d\\d)-(?<day>\\d\\d)/",
              "A := /(?<c>\\d)/", "item := /(?<h>\\d)(?::(?<m>\\d))?,/"]


def sweep(texts):
    out = []
    for f, text in texts.items():
        for ln, line in enumerate(text.split("\n"), 1):
            for mm in list(B1.finditer(line)) + list(B2.finditer(line)):
                b = "%s := %s" % (mm.group(1), mm.group(2).strip())
                base_binds()
                OPT.clear()
                OPT["lenient"] = True
                try:
                    for e in ENV:
                        define(e)
                    define(b)
                    r = binding_check(b) if not (sab("s13") and is_cond(HEADS[b][2])) else None
                except Exception as e:                       # noqa: BLE001  an owner placeholder the model cannot parse
                    r = "unparsed: %s" % type(e).__name__
                if r and "does not hold" in r:
                    out.append((f, ln, b, line))
    return out


S_OLD = sweep({f: OLD[f] for f in ("core.md", "library.md", "parked.md")})
S_NEW = sweep({f: read(os.path.join(PRED, f)) for f in ("core.md", "library.md", "parked.md")})
D_NEW = sweep({f: read(os.path.join(PRED, f)) for f in ("core_details.md", "library_details.md", "parked_details.md")})
for tag_, lst in (("start", S_OLD), ("now", S_NEW), ("now, details", D_NEW)):
    print("   %s: %d refused bindings" % (tag_, len(lst)))
    for f, ln, b, line in lst:
        print("      %s:%d  %s" % (f, ln, b))
OK_NOW = re.compile(r"compile error|refused|illegal|is incorrect|\"")       # printed AS refused, or an owner quote
bad_now = [(f, ln, b) for f, ln, b, line in S_NEW if not OK_NOW.search(line)]
old_names = sorted(set(b.split(" :=")[0] for _, _, b, _ in S_OLD))
check("SWEEP", {"c", "sum", "n", "nchars", "mnum", "lt5(S)"} <= set(old_names) and not bad_now,
      "start tree: %s ; in the base files now, refused bindings not printed as refused: %s" % (old_names, bad_now))

# ---------------------------------------------------------------- QUOTES
print("== QUOTES: the owner's words this lane quotes, verbatim in the record")
QUOTED = [
    "bound-condition: the form A := (x: blah) has to be illegal. x has no references in the binding. further A := /x/ "
    "& (y: blah) is also illegal as y has no target. this is the only read consistent with the earlier binding "
    "decisions. this is my read. please respond. alternatives: 1. macro variables A(x:) := (x: < 2100) 2. macro types "
    "B(d & isodate) := B(year: < 2100) (spellings tbd)",
    "bound-condition: correction to rx: B(d & isodate) := (year: < 2100)",
    "cound-condition: mostly confirmed. i leave the c := (0: 5) open",
    "illegal meaning a compiler error",
    "count-in-set: ok, thats fine. i think your value in the left part of condition as a fantastic addition so b. it "
    "suggests $h could go there which is also new. aside: perhaps we will need a syntax to declare the ch in chars. i "
    "am wonderings not for correctness but clarity. also, it suggests that bindings could be used under certain rules "
    "as label prefixes like chars.ch as that is clear here. chars seq \":\" seq chars & (chars.ch: blah) would need "
    "defining. respond",
    "count-in-set: i don't understand your length(S) example: where do you define label ch?",
    "A . B & (A.h: blah) error. A is a binding not a label and could be ambigous if its used multiple times in an "
    "expression",
    "we note that l is a label variable",
    "bound-condition: A := /\\d${(0: 5)}/ binds the literal to 5. A := /\\d/ C := /.${A & (0: 5)}/ the 0: is bound to A "
    "only",
]
if sab("s14"):
    QUOTED[2] = QUOTED[2].replace("cound", "bound")
qmiss = [q for q in QUOTED if ws(q) not in RECORD_WS]
check("QUOTES", not qmiss, "%d quoted passages; missing from the record: %s" % (len(QUOTED), qmiss))

# ---------------------------------------------------------------- MARKS: the documents' state after the fold
print("== MARKS: statuses, the withdrawn binding forms, the new pieces")
CORE_N, LIB_N, PARK_N = (read(os.path.join(PRED, f)) for f in ("core.md", "library.md", "parked.md"))
if sab("s15"):
    CORE_N = CORE_N.replace("[core/holes/bare-condition/bound-condition]   ruled", "[core/holes/bare-condition/bound-condition]   open bound-condition")
HEAD = lambda tag, st: re.search(r"\[%s\]\s+%s 2026-11-22" % (re.escape(tag), st), CORE_N + LIB_N + PARK_N) is not None
marks = {
    "bound-condition ruled": HEAD("core/holes/bare-condition/bound-condition", "ruled"),
    "value-left ruled": HEAD("core/conditions/form/value-left", "ruled"),
    "zero-binding open": HEAD("core/holes/bare-condition/zero-binding", "open zero-condition-binding"),
    "label-variables u-c": HEAD("core/operators/bindings/label-variables", "under-construction"),
    "macro-types u-c": HEAD("core/operators/bindings/macro-types", "under-construction"),
    "declared-labels parked": HEAD("parked/ideas/declared-labels", "parked"),
    "binding-prefix parked": HEAD("parked/ideas/binding-prefix", "parked"),
    "computed-labels a reading": HEAD("core/values/computed-labels", "reading"),
    "no open marks": "depends on the open bound-condition" not in CORE_N + LIB_N,
    "never an expression gone": "never an expression" not in piece(CORE_N, "core/conditions/form"),
    "count not bound": "may be bound and read" not in piece(LIB_N, "lib/counting/count"),
    "no binding form": not re.search(r"\bn := `count|\bsum := `\$|`nchars := |`mnum := |\bc := `NOT", CORE_N + LIB_N),
    "path rule kept": "A binding's name is not a path" in piece(CORE_N, "core/labels/flow"),
    "both meanings": "(i) literally the intersection" in piece(CORE_N, "core/operators/bindings/macro-types")
    and "(ii) a promise checked at the call" in piece(CORE_N, "core/operators/bindings/macro-types"),
}
check("MARKS", all(marks.values()), "%s" % [k for k, v in marks.items() if not v] if not all(marks.values())
      else "%d marks hold" % len(marks))

# ---------------------------------------------------------------- DOC
print("== DOC: every formatted line occurs verbatim in the documents")
DOCS_N = "".join(read(os.path.join(PRED, f)) for f in
                 ("core.md", "core_details.md", "library.md", "library_details.md", "parked.md", "parked_details.md"))
lines = list(LINES)
if sab("s16"):
    lines[0] = (lines[0][0], lines[0][1].replace("`7`", "`8`", 1))
missing = [(t, L) for t, L in lines if L not in DOCS_N]
for t, L in lines:
    print("   [%s] %s" % (t, L))
check("DOC", not missing, "%d lines; missing: %s" % (len(lines), missing))

print("predbound_model: %d checks, %d failed%s" % (len(CHECKS), len(FAILED), (" (" + ", ".join(FAILED) + ")") if FAILED else ""))
