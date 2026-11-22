#!/usr/bin/env python3
# Lane predfix77 (2026-11-22): the evidence for the fix revision that applies review r77's ruled dispositions
# (predfold1121) to the predicate documents, and for the manager's five readings named in the lane brief. DESIGN
# EVIDENCE ONLY; rules nothing. Python3 `re`, plus libpcre2-8 as a LIBRARY through ../rxmodel_evidence/pcre2h.py
# (run, never read: the D181 wall).
#
# METHOD. Every program is LOWERED MECHANICALLY from its text as the documents print it, by a small lowerer (the
# expression language: `|`, `&`, `SEQ`, postfix `+ * ?`, `( )`, `[x = E]`, `/rx/` with `${...}` holes, `"s"`, a bound
# name, a macro call with positional and keyword arguments; library bodies READ from library.md: `occurrences`,
# `rx.repeat`'s call forms, `rx.digit`, `rx.digits`, `chars`, `nchars`, `any_case`), into the text of a backtracking
# label matcher (lane predarr's, copied, which is predfix61's): a group's close sets its name, a branching resets the
# labels inside it, a condition reads the labels as they stand, an unset label fails a test and NOT of it holds;
# PCRE's order of paths. ADDED HERE, each a reading the documents state or a candidate they print:
#   SCOPES   every definition USE (a binding or a macro body) is a scope of its own (reading (d): two uses are two
#            pieces); a group sets its label for every scope that encloses it, so the program (scope `top`) reads
#            the last mention (the user's view: core/labels/flow, export) and a piece reads only the settings made
#            inside it (core/holes/bare-condition/nested-scope, case 2: b). Entering a piece resets the piece's own
#            view (reading (c) withdrawn: a user's loop around a piece makes each pass a fresh use). An argument is
#            lowered in its CALLER's scope (reading (e)). A piece that names a label it does not hold is a compile
#            error at its definition (case 1).
#   ZERO     `0` is the text from a MARK to the condition's point; the mark of a definition is set where it starts
#            (zero-in-definition); a condition joined by `&` reads its left operand's mark (bare-condition's ruled
#            "`${A & (0: S)}` ... only A", and reading (1) of the brief for the sequence operand).
#   ARRAYS   a group question (`some`, `occurs.none`, `count`, the index `h[k]`) is evaluated AT ITS POINT on the
#            path's log: the array of a name's settings, read in one of the candidate scopes (composed: the whole
#            program; own: the piece it is written in; chain: the `&` operand's own stretch).
#   FLAGS    `(?i:..)` case-insensitive literals and classes (for any_case only).
# Every three-mode line formatted for the documents must occur VERBATIM in them (DOC). Controls that do not share
# the matcher: python `re` on independent hand regexes (CONTROL and each answer check), libpcre2-8 (DUPNAME), the
# record's words (QUOTES).
#
# Run (W = the worktree; any cwd):  timeout 300 python3 -I -B W/docs/dev/lanes/predfix77_evidence/predfix77_model.py
# PREDFIX77_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
#   s1  the matcher tries alternatives last first                                         -> CONTROL
#   s2  a bound piece's group question reads the composed array (array-in-piece (a))     -> ARRPIECE
#   s3  the `&` operand's own stretch read without the definition's settings      -> ARRREAD
#   s4  a condition joined by `&` reads the definition's mark, not its left operand's    -> SEQZERO
#   s5  occurrences' body reading puts the mark at the hit, not at the body's start      -> OCCZERO
#   s6  the duplicate-name expectation reversed (the LAST set group in pattern order)    -> DUPNAME
#   s7  entering a piece does not reset its own view (reading (c) kept)                   -> LOOPPIECE
#   s8  a piece reads the user's labels (the SHARED reading, rejected)                    -> SEALED
#   s9  a bound condition is sealed under candidate (a)                                   -> BOUND
#   s10 an argument is lowered in the macro's scope, not its caller's                     -> ZEROARG
#   s11 the re-spelled `chars` counts one setting fewer                                   -> CHARS
#   s12 any_case's body applies the flag after the intersection                           -> ANYCASE
#   s13 the array is kept in text order where the time order is the reading               -> ARRORDER
#   s14 a loop with no pass counted as one setting                                        -> EVERYNONE
#   s15 the class-hole values sorted before the lift                                      -> LIFTORDER
#   s16 a quoted owner sentence altered (in memory)                                       -> QUOTES
#   s17 pass-start-read's pointer to the bound-condition piece dropped (in memory)       -> MARKS
#   s18 one formatted line's subject altered before the document lookup                  -> DOC
#   s19 the joint spelling inside a group question accepted                               -> RECORD
#   s20 `0` of a hole condition joined by `&` read from the definition's start            -> HISEX
import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
RECORD_PATH = os.path.join(W, "docs", "design", "plan_row_bodies", "COND-FAMILY.md")
SAB = set(x for x in os.environ.get("PREDFIX77_SABOTAGE", "").split(",") if x)
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
    if sab("s13"):
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
            entries.append((("lab", "%s@%s" % (name, ctx.cur)), val))
    return node_ref(("cond", neg, entries))


def array_scope(ctx):
    """Which settings a group question reads: OPT['array'] in composed / own / chain."""
    a = OPT.get("array", "own")
    if a == "composed":
        return "top"
    if a == "chain" and ctx.chain:
        return ctx.chain
    if sab("s2") and a == "own":
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
    if sab("s3") and chain:
        sub = sub.sub(scopes=ctx.scopes, chain=ctx.cur)
    out = node_ref(("mark", mk)) + "(?:%s)" % lower(pats[0], sub)
    for q in pats[1:]:
        out += node_ref(("andpat", mk, p_alt(Src(lower(q, Ctx())))))
    zk = ctx.zero if (sab("s4") or sab("s20") or OPT.get("and_zero") == "definition") else mk
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
    pre = node_ref(("enter", sc, sab("s7") or OPT.get("loop_c", False)))
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
        if IS_COND.match(body) and OPT.get("bound", "inplace") == "inplace" and not sab("s9"):
            return lower_cond(body, ctx.sub(params=params))
        return use_definition(body, ctx, call[0], params)
    if expr in BINDS:
        body = BINDS[expr]
        if IS_COND.match(body) and OPT.get("bound", "inplace") == "inplace" and not sab("s9"):
            return lower_cond(body, ctx)                 # candidate (a): laid against the pattern it meets
        return use_definition(body, ctx, expr)
    raise CompileError("an undeclared name: " + expr)


def use_param(name, ctx):
    text, caller = ctx.params[name]
    if re.fullmatch(r"\d+", text):
        return text
    if sab("s10"):
        caller = ctx
    zero = caller.zero
    occ = OPT.get("occ_zero")
    pre = ""
    if occ == "body":
        zero = ctx.zero
    elif occ == "hit":
        zero = fresh("h")
        pre = node_ref(("mark", zero))
    if sab("s5") and occ == "body":
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
CHARS_DOC = lib_body(r"`chars := (.*?)`, `nchars")
NCHARS_DOC = lib_body(r"`nchars := (count\(\(ch: /\(\?s:\.\)/\)\))`")
ANYCASE_BODY = lib_body(r"`any_case\(rx\) := (/.*?/)`")
CHARS_OLD = "/(?:(?<ch>(?s:.)))*/"


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
    Pg = prog(expr, binds, **opts)
    L = (label + ": " if label else "") + fmt(Pg, wh, sr, fa) + tail
    return doc_line(L, tag) if tag else L


# ================================================================== the checks
print("== library bodies read from library.md: occurrences %s ; repeat %s ; rx.digit %s ; rx.digits %s ; chars %s ; "
      "nchars %s ; any_case %s" % (OCC_BODY, REPEATS, RXDIGIT, RXDIGITS, CHARS_DOC, NCHARS_DOC, ANYCASE_BODY))
print("== libpcre2-8 %s" % P.version())

# ---------------------------------------------------------------- CONTROL
print("== CONTROL: lowered programs without conditions against python `re` on hand regexes")
POPA = pop("ab;7", 4)
c1 = ndiff(answers(prog('"ab" | "a"'), POPA), answers(Re(r"ab|a"), POPA))
c2 = ndiff(answers(prog("/(?:a|ab)??;/"), POPA), answers(Re(r"(?:a|ab)??;"), POPA))
c3 = ndiff(answers(prog('rx.repeat("a" SEQ ";", min = 2, max = 2)'), POPA), answers(Re(r"(?:a;){2,2}"), POPA))
c4 = ndiff(answers(prog("/(?i:a[b7])/"), POPA), answers(Re(r"(?i:a[b7])"), POPA))
check("CONTROL", (c1, c2, c3, c4) == ((0, 0, 0),) * 4,
      "of %d texts over `ab;7`: `\"ab\" | \"a\"` %s, `(?:a|ab)??;` %s, rx.repeat(.., min = 2, max = 2) %s, `(?i:a[b7])` %s"
      % (len(POPA), c1, c2, c3, c4))

# ---------------------------------------------------------------- ARRPIECE (A1; array-in-piece RULED (b), R-1, R-2)
print("== ARRPIECE: array-in-piece (b): a bound piece's group question reads what the piece sees; in place, A's too")
BA = ["A := /(?<h>\\d)/", 'B := /(?:;(?<h>\\d))*${some((h: "7"))}/']
E_IN = 'A SEQ /(?:;(?<h>\\d))*${some((h: "7"))}/'
WA, SA, FA_ = ["7", "7;1", "1;7", "1;2"], "x7;1 1;7", "7;1 1;7 3;4 7 2;7;5"
L_A_B = show("Bound first", "A SEQ B", BA, WA, SA, FA_,
             ' (`A SEQ B`, A := `/(?<h>\\d)/`, B := `/(?:;(?<h>\\d))*${some((h: "7"))}/`)', "labels-vs-captures")
L_A_I = show("Written in place", E_IN, BA[:1], WA, SA, FA_, ' (`%s`, A := `/(?<h>\\d)/`)' % E_IN, "labels-vs-captures")
print("   " + L_A_B)
print("   " + L_A_I)
# the record's pasted lines ("2026-11-22 OWNER RULING — array-in-piece: b ..."): own = bound first, entire = in place
def rec_answers(label):
    mm = re.search(r"^%s: (WHOLE .*)$" % label, RECORD[RECORD.index("### 2026-11-22 OWNER RULING — array-in-piece"):], re.M)
    t = mm.group(1)
    wh = re.findall(r"WHOLE `([^`]*)` (HOLDS|FAILS)", t)
    sr = re.search(r"SEARCHED `[^`]*` (`[^`]*`@\d+|FAILS)", t).group(1)
    fa = re.search(r"FIND-ALL `[^`]*` (\[.*?\])", t).group(1)
    return wh, sr, fa
def my_answers(L):
    wh = re.findall(r"`([^`]*)` (HOLDS|FAILS)", L.split(" / SEARCHED")[0])
    sr = re.search(r"SEARCHED `[^`]*` (`[^`]*`@\d+|FAILS)", L).group(1)
    fa = re.search(r"FIND-ALL `[^`]*` (\[.*?\])", L).group(1)
    return wh, sr, fa
r_own, r_ent = rec_answers("own"), rec_answers("entire")
POP1 = pop("71;x", 5)
cb = ndiff(answers(prog("A SEQ B", BA), POP1), answers(Re(r"\d(?:;\d)*;7(?:;\d)*"), POP1))
ci = ndiff(answers(prog(E_IN, BA[:1]), POP1), answers(Re(r"(?:7|\d(?:;\d)*;7)(?:;\d)*"), POP1))
check("ARRPIECE", my_answers(L_A_B) == r_own and my_answers(L_A_I) == r_ent and cb == ci == (0, 0, 0),
      "bound first = the record's `own` line: %s ; in place = its `entire` line: %s ; of %d texts over `71;x`: bound "
      "first against `\\d(?:;\\d)*;7(?:;\\d)*` %s, in place against `(?:7|\\d(?:;\\d)*;7)(?:;\\d)*` %s"
      % (my_answers(L_A_B) == r_own, my_answers(L_A_I) == r_ent, len(POP1), cb, ci))

# ---------------------------------------------------------------- ARRREAD: the entry's readings (b), (c), (d)
print("== ARRREAD: readings (b) a piece using A sees A's settings, (c) count and h[k] alike, (d) an `&` operand in place")
BU = ["A := /(?<h>\\d)/", 'U := A SEQ /(?:;(?<h>\\d))*${some((h: "7"))}/']
ru = ndiff(answers(prog("U", BU), POP1), answers(prog(E_IN, BA[:1]), POP1))
BK = ["A := /(?<h>\\d)/", 'K := /(?:;(?<h>\\d))*${(h[1]: "7")}/']
EK_IN = 'A SEQ /(?:;(?<h>\\d))*${(h[1]: "7")}/'
rk = (ndiff(answers(prog("A SEQ K", BK), POP1), answers(Re(r"\d;7(?:;\d)*"), POP1)),
      ndiff(answers(prog(EK_IN, BK[:1]), POP1), answers(Re(r"7(?:;\d)*"), POP1)))
E2 = '/(?<h>\\d)${/(?:;(?<h>\\d))*/ & some((h: "7"))}/'
L_C_D = show("In an `&` operand, one definition (a reading)", E2, [], WA, SA, FA_, " (`%s`)" % E2, "array-vs-passes")
L_C_C = show("The operand's own stretch only (not the reading)", E2, [], WA, SA, FA_, " (the same program)", "report",
             array="chain")
print("   " + L_C_D)
print("   " + L_C_C)
cd = ndiff(answers(prog(E2), POP1), answers(Re(r"(?:7|\d(?:;\d)*;7)(?:;\d)*"), POP1))
cc = ndiff(answers(prog(E2, array="chain"), POP1), answers(Re(r"\d(?:;\d)*;7(?:;\d)*"), POP1))
check("ARRREAD", ru == (0, 0, 0) and rk == ((0, 0, 0), (0, 0, 0)) and cd == (0, 0, 0) and cc == (0, 0, 0),
      "of %d texts: (b) `U := A SEQ /..some../` against the in-place line's program %s ; (c) `h[1]` bound first "
      "against `\\d;7(?:;\\d)*` and in place against `7(?:;\\d)*` %s ; (d) the definition's settings against "
      "`(?:7|\\d(?:;\\d)*;7)(?:;\\d)*` %s, the operand-only rival against `\\d(?:;\\d)*;7(?:;\\d)*` %s"
      % (len(POP1), ru, rk, cd, cc))

# ---------------------------------------------------------------- SEQZERO (A5; the brief's reading 1)
print("== SEQZERO: `0` of a condition joined by `&` written as a sequence operand, and in a hole")
E5 = "/\\d/ SEQ (/\\d/ & (0: /\\d/))"
E5H = "/\\d${/\\d/ & (0: /\\d/)}/"
E5B = "/\\d/ SEQ (/\\d/ & /\\d/)"
W5, S5, F5 = ["12"], "x12", "12 34 5"
L_Z_S = show("As a sequence operand", E5, [], W5, S5, F5, " (`%s`)" % E5, "match-so-far")
L_Z_H = show("", E5H, [], W5, S5, F5, " (`%s`)" % E5H, None)
L_Z_B = show("", E5B, [], W5, S5, F5, " (`%s`)" % E5B, None)
L_Z_D = show("Definition-wide `0` (not the reading)", E5, [], W5, S5, F5, " (the same program)", "report",
             and_zero="definition")
print("   " + L_Z_S)
print("   hole spelling: " + L_Z_H)
print("   `A & B` form:  " + L_Z_B)
print("   " + L_Z_D)
POP5 = pop("12x", 4)
z1 = ndiff(answers(prog(E5), POP5), answers(Re(r"\d\d"), POP5))
z2 = ndiff(answers(prog(E5H), POP5), answers(prog(E5B), POP5))
z3 = ndiff(answers(prog(E5), POP5), answers(prog(E5H), POP5))
check("SEQZERO", z1 == (0, 0, 0) and z2 == (0, 0, 0) and z3 == (0, 0, 0) and "FAILS" in L_Z_D.split(" / ")[0],
      "of %d texts over `12x`: the sequence operand against `\\d\\d` %s ; the hole spelling against `A & B` %s ; "
      "sequence against hole %s ; definition-wide `0` would FAIL on `12`" % (len(POP5), z1, z2, z3))

# ---------------------------------------------------------------- OCCZERO (A6; the brief's reading 5)
print("== OCCZERO: `0` in an `occurrences` argument, three candidate marks (caller's definition, the body, the hit)")
E6 = "/x?/ SEQ occurrences(/\\d/ SEQ (0: /\\d/), min = 1)"
L_O = {}
for rd, word in (("caller", "The caller's definition (the reading today)"), ("body", "The body of `occurrences`"),
                 ("hit", "The hit's own text")):
    L_O[rd] = show(word, E6, [], ["a5", "x5", "5"], "-x5", "a5 x5", " (`%s`)" % E6, "report", occ_zero=rd)
    print("   " + L_O[rd])
parts = len({L_O[r].split(": ", 1)[1] for r in ("caller", "body", "hit")})
o_hit = ndiff(answers(prog(E6, occ_zero="hit"), POP5), answers(Re(r"x?(?:(?s:.*?)\d){1,}(?s:.*)"), POP5))
o_body = ndiff(answers(prog(E6, occ_zero="body"), POP5), answers(Re(r"x?\d(?s:.*)"), POP5))
o_call = ndiff(answers(prog(E6, occ_zero="caller"), POP5), answers(Re(r"\d(?s:.*)"), POP5))
check("OCCZERO", parts == 3 and o_hit == o_body == o_call == (0, 0, 0),
      "the three readings print %d different lines ; of %d texts over `12x`: the caller's against `\\d(?s:.*)` %s, "
      "the body's against `x?\\d(?s:.*)` %s, the hit's against `x?(?:(?s:.*?)\\d){1,}(?s:.*)` %s"
      % (parts, len(POP5), o_call, o_body, o_hit))

# ---------------------------------------------------------------- DUPNAME (A8): libpcre2, a name two groups carry
print("== DUPNAME: libpcre2-8: `\\k<h>` and the by-name capture of a name two groups carry")
import ctypes                                                # noqa: E402
P.L.pcre2_substring_copy_byname_8.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p,
                                              ctypes.POINTER(ctypes.c_size_t)]


class Dup:
    """A pattern compiled by libpcre2 with no callout (pcre2h's Pcre resolves names one by one, which a
    duplicated name refuses); the three modes as pcre2h.Pcre gives them."""

    def __init__(self, pat):
        err, off = ctypes.c_int(0), P.SIZE(0)
        pb = pat.encode()
        self.code = P.L.pcre2_compile_8(pb, len(pb), P.BASE_OPTS, ctypes.byref(err), ctypes.byref(off), None)
        self.err = None if self.code else P.errmsg(err.value)
        if self.code:
            self.md = P.L.pcre2_match_data_create_from_pattern_8(self.code, None)

    def match(self, s, start=0, opts=0):
        self._buf = ctypes.create_string_buffer(s.encode())
        rc = P.L.pcre2_match_8(self.code, self._buf, len(s), start, opts, self.md, None)
        if rc < 0:
            return None
        ov = P.L.pcre2_get_ovector_pointer_8(self.md)
        return (ov[0], ov[1], None)

    def whole(self, s):
        return self.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED) is not None

    def search(self, s):
        return self.match(s)

    def findall(self, s):
        out, pos = [], 0
        while pos <= len(s):
            r = self.match(s, pos)
            if r is None:
                break
            out.append((s[r[0]:r[1]], r[0]))
            pos = r[1] if r[1] > r[0] else r[1] + 1
        return out

    def byname(self, s, name):
        if self.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED) is None:
            return None
        buf, n = ctypes.create_string_buffer(16), ctypes.c_size_t(16)
        rc = P.L.pcre2_substring_copy_byname_8(self.md, name.encode(), buf, ctypes.byref(n))
        return buf.value.decode() if rc == 0 else "rc %d" % rc


DPAT = "(?J)(?<h>\\d)(?:;(?<h>\\d))?\\k<h>"
D = Dup(DPAT)
L_DUP = doc_line("Two groups of one name: " + fmt(D, ["7;37", "7;33", "77"], "x7;37", "7;37 7;33 33") +
                 " (`/%s/`: `\\k<h>` reads the first set group in pattern order)" % DPAT, "labels-vs-captures")
print("   " + L_DUP)
DC = Dup("(?J)(?<h>\\d)(?:;(?<h>\\d))?")
by73, by7 = DC.byname("7;3", "h"), DC.byname("7", "h")
noj = Dup("(?<h>\\d)(?:;(?<h>\\d))?").err
expect = ([True, False, True], "7") if not sab("s6") else ([False, True, True], "3")
got = [D.whole(t) for t in ["7;37", "7;33", "77"]]
lab73 = prog("/(?<h>\\d)(?:;(?<h>\\d))?/").at("7;3", 0, need_end=3)[2].lab.get("h@top")
check("DUPNAME", got == expect[0] and by73 == expect[1] and by7 == "7" and noj is not None and lab73 == "3",
      "WHOLE `7;37` `7;33` `77`: %s ; by-name `h` on `7;3`: %s, on `7`: %s ; without `(?J)` libpcre2 refuses: %s ; "
      "the label h on `7;3` (last mention): %s" % (got, by73, by7, noj, lab73))

# ---------------------------------------------------------------- LOOPPIECE (A12; the brief's reading 2)
print("== LOOPPIECE: a user's loop around a piece against its written-out form, B reading its label before its group")
BB = ["B := /${NOT (c: >= 5)}(?<c>\\d)/"]
TAIL_B = ", B := `/${NOT (c: >= 5)}(?<c>\\d)/`)"
E12L = 'rx.repeat(B SEQ ";", min = 2, max = 2)'
E12W = 'B SEQ ";" SEQ B SEQ ";"'
E12O = '/(?:${NOT (c: >= 5)}(?<c>\\d);){2}/'
W12, S12, F12 = ["7;3;", "3;7;"], "x7;3;", "7;3; 3;7;"
L_L = show("A user's loop", E12L, BB, W12, S12, F12, " (`%s`%s" % (E12L, TAIL_B), "nested-scope")
L_W = show("Written out", E12W, BB, W12, S12, F12, " (`%s`%s" % (E12W, TAIL_B), "nested-scope")
L_O1 = show("One definition, looped", E12O, [], W12, S12, F12, " (`%s`)" % E12O, "nested-scope")
L_LC = show("A user's loop under the withdrawn reading", E12L, BB, W12, S12, F12, "", "report", loop_c=True)
for L in (L_L, L_W, L_O1, L_LC):
    print("   " + L)
POP12 = pop("37;", 5)
l1 = ndiff(answers(prog(E12L, BB), POP12), answers(prog(E12W, BB), POP12))
l2 = ndiff(answers(prog(E12L, BB), POP12), answers(Re(r"\d;\d;"), POP12))
l3 = ndiff(answers(prog(E12O), POP12), answers(Re(r"[0-4];\d;"), POP12))
check("LOOPPIECE", l1 == (0, 0, 0) and l2 == (0, 0, 0) and l3 == (0, 0, 0)
      and L_L.split(": ", 1)[1].split(" (`")[0] == L_W.split(": ", 1)[1].split(" (`")[0]
      and L_L.split(": ", 1)[1].split(" (`")[0] != L_LC.split(": ", 1)[1],
      "of %d texts over `37;`: the loop against the written-out form %s, against `\\d;\\d;` %s ; one definition "
      "against `[0-4];\\d;` %s ; under the withdrawn reading the loop parts" % (len(POP12), l1, l2, l3))

# ---------------------------------------------------------------- SEALED: the manager's hand folds (D9)
print("== SEALED: the nested-scope and bare-condition/labels lines the manager folded by hand, lowered here")
BS = ["A := /(?<c>\\d)/", "B := /${(c: >= 5)}(?<c>\\d)/"]
T2 = ["73", "37"], "37 73", "73 37 51"
L_2D = show("Two definitions", "A SEQ B", BS, *T2,
            " (`A SEQ B`, A := `/(?<c>\\d)/`, B := `/${(c: >= 5)}(?<c>\\d)/`)", "nested-scope", names="sealed")
L_1D = show("One definition", "/(?<c>\\d)${(c: >= 5)}(?<c>\\d)/", [], *T2,
            " (`/(?<c>\\d)${(c: >= 5)}(?<c>\\d)/`)", "nested-scope")
BI = ["inner(c) := /x${c}/"]
L_PC = show("Passing the condition", "/(?<h>\\d)${inner((h: <5))}/", BI, ["3x", "7x"], "7x 3x", "3x 7x 4x",
            " (`/(?<h>\\d)${inner((h: <5))}/`, inner(c) := `/x${c}/`)", "nested-scope")
BM = ["inner := /x${(0: /\\dx/)}/"]
L_MS = show("Match so far", "/(?<h>\\d)${inner}/", BM, ["3x", "7x"], "a3x", "3x 7x",
            " (`/(?<h>\\d)${inner}/`, inner := `/x${(0: /\\dx/)}/`)", "nested-scope")
BE1 = ["A := [d = rx.digits]", "B(rx) := /${rx}xx/", "C := B(A) & (d: <100)"]
TE = ["42xx", "100xx", "042xx"], "x100xx 42xx", "100xx 42xx 7xx 300xx"
L_E1 = show("Example 1", "C", BE1, *TE,
            " (`C := B(A) & (d: <100)`, A := `[d = rx.digits]`, B(rx) := `/${rx}xx/`)", "nested-scope")
BE3 = ["A := [d = rx.digits]", "B(rx) := /${[dd = rx]}xx/ & (dd: <100)"]
L_E3 = show("Example 3", "B(A)", BE3, *TE,
            " (`B(A)`, A := `[d = rx.digits]`, B(rx) := `/${[dd = rx]}xx/ & (dd: <100)`)", "nested-scope")
for L in (L_2D, L_1D, L_PC, L_MS, L_E1, L_E3):
    print("   " + L)
r_case1 = refused("/(?<h>\\d)${inner}/", ["inner := /x${(h: <5)}/"])
r_ex2 = refused("C", ["A := [d = rx.digits]", "B(rx) := /${rx}xx/ & (d: <100)", "C := B(A)"])
shared = show("", "A SEQ B", BS, *T2, "", None, names="shared")
POPS = pop("73", 4)
s_2d = ndiff(answers(prog("A SEQ B", BS), POPS), answers(Re(r"(?!)"), POPS))
s_1d = ndiff(answers(prog("/(?<c>\\d)${(c: >= 5)}(?<c>\\d)/"), POPS), answers(Re(r"[5-9]\d"), POPS))
if sab("s8"):
    L_2D = shared
check("SEALED", s_2d == (0, 0, 0) and s_1d == (0, 0, 0) and "FAILS" in L_2D.split(" / ")[0] and r_case1 and r_ex2,
      "of %d texts over `73`: two definitions against the never-matching `(?!)` %s, one definition against "
      "`[5-9]\\d` %s ; case 1 refused: %s ; example 2 refused: %s" % (len(POPS), s_2d, s_1d, r_case1, r_ex2))

# ---------------------------------------------------------------- BOUND: the bound-condition piece's lines
print("== BOUND: a condition bound to a name of its own, under the two candidates of bound-condition")
BC = ["c := (0: rx.digit)"]
TB = ["7x", "77x"], "a7x", "7x 12x 8x"
L_BA = show("(a) where it is used", "/\\d${c}x/", BC, *TB, " (`/\\d${c}x/`, c := `(0: rx.digit)`)", "bound-condition",
            bound="inplace")
L_BB = show("(b) sealed, its own `0`", "/\\d${c}x/", BC, *TB, " (the same program)", "bound-condition", bound="sealed")
BL = ["lt5(S) := (h: S)"]
L_ML = show("A macro returning a condition, (a)", "/(?<h>\\d)${lt5(<5)}/", BL, ["3", "7"], "x7 3", "3 7 4",
            " (`/(?<h>\\d)${lt5(<5)}/`, lt5(S) := `(h: S)`)", "bound-condition", bound="inplace", names="open")
r_lt5 = refused("/(?<h>\\d)${lt5(<5)}/", BL, bound="sealed")
r_cb = refused("/(?<h>\\d)${c}x/", ["c := (h: <5)"], bound="sealed")
for L in (L_BA, L_BB, L_ML):
    print("   " + L)
print("   (b) on the macro: %s ; (b) on `c := (h: <5)`: %s" % (r_lt5, r_cb))
POPB = pop("17x", 4)
b1 = ndiff(answers(prog("/\\d${c}x/", BC), POPB), answers(Re(r"\dx"), POPB))
b2 = ndiff(answers(prog("/\\d${c}x/", BC, bound="sealed"), POPB), answers(Re(r"(?!)"), POPB))
check("BOUND", b1 == (0, 0, 0) and b2 == (0, 0, 0) and r_lt5 and r_cb and "`3` HOLDS" in L_ML,
      "of %d texts over `17x`: (a) against `\\dx` %s, (b) against `(?!)` %s ; under (b) the macro and a named "
      "condition naming h are refused at their definition" % (len(POPB), b1, b2))

# ---------------------------------------------------------------- ZEROARG (A4): a condition passed into a macro's hole
print("== ZEROARG: `/\\d/ SEQ B((0: /\\d/))`: the argument read in its caller's definition (a reading)")
BZ = ["B(rx) := /${rx}xx/"]
EZ = "/\\d/ SEQ B((0: /\\d/))"
L_ZA = show("An argument", EZ, BZ, ["5xx", "xx"], "a5xx", "5xx 55xx", " (`%s`, B(rx) := `/${rx}xx/`)" % EZ,
            "match-so-far")
L_ZH = show("", EZ, BZ, ["5xx", "xx"], "a5xx", "5xx 55xx", "", "report", occ_zero="body")
print("   " + L_ZA)
print("   the hole's definition instead (the statement read without its clause): " + L_ZH)
POPZ = pop("5x", 4)
za = ndiff(answers(prog(EZ, BZ), POPZ), answers(Re(r"\dxx"), POPZ))
check("ZEROARG", za == (0, 0, 0) and "`5xx` FAILS" in L_ZH,
      "of %d texts over `5x`: the caller's reading against `\\dxx` %s ; read in B's definition `5xx` FAILS"
      % (len(POPZ), za))

# ---------------------------------------------------------------- CHARS (D4; the brief's reading 4)
print("== CHARS: `chars` re-spelled with a part label: every printed `length` line, old and new body")
LEN_LINES = []
for mm in re.finditer(r"^.*\(`length\((.*?)\)` as a program: `chars & \(nchars: (.*?)\)`\)$", DOCS, re.M):
    LEN_LINES.append(mm.group(0))
lens = []
for Lt in LEN_LINES:
    mm = re.search(r"WHOLE (.*?) / SEARCHED `(.*?)` .*? / FIND-ALL `(.*?)` \[", Lt)
    wh = re.findall(r"`([^`]*)` (?:HOLDS|FAILS)", mm.group(1))
    sr, fa = mm.group(2), mm.group(3)
    S = re.search(r"as a program: `chars & \(nchars: (.*?)\)`", Lt).group(1)
    tail = Lt[Lt.index(" (`length("):]
    lens.append((Lt, wh, sr, fa, S, tail))


def length_prog(body, S, drop=False):
    """`length(S) := chars & (nchars: S)`, nchars := count((ch: /(?s:.)/)): a count over `ch`'s array at the end."""
    base_binds()
    OPT.clear()
    define("chars := " + body)
    ctx = Ctx()
    mk = fresh("k")
    text = node_ref(("mark", mk)) + "(?:%s)" % lower("chars", ctx)
    sc = "top"
    keyname = "ch@" + sc
    val = parse_value(S, ctx)
    node = ("gq", "count", False, keyname, sc, parse_value("/(?s:.)/", ctx), val, False)
    if drop:
        node = ("gq", "count", False, keyname, sc, parse_value("/(?s:.)/", ctx), ("cmp", val[1], str(int(val[2]) + 1)), False)
    text += node_ref(node)
    Pg = Prog(text)
    return Pg


same, newlines = [], []
for Lt, wh, sr, fa, S, tail in lens:
    old = fmt(length_prog(CHARS_OLD, S), wh, sr, fa) + tail
    new = fmt(length_prog(CHARS_DOC, S, drop=sab("s11")), wh, sr, fa) + tail
    same.append(old == new == Lt)
    print("   old body %s | new body %s | printed %s" % (old == Lt, new == Lt, Lt))
base_binds()
lower("/(?:(?<ch>(?s:.)))*/", Ctx(name="chars"))
cap_old = list(CAPTURES)
base_binds()
lower(CHARS_DOC, Ctx(name="chars"))
cap_new = list(CAPTURES)
check("CHARS", LEN_LINES and all(same) and CHARS_DOC != CHARS_OLD and cap_old == [("chars", "ch")] and cap_new == [],
      "%d printed `length` lines, each the same under the old body %s and the new %s: %s ; captures the bodies "
      "make: old %s, new %s" % (len(LEN_LINES), CHARS_OLD, CHARS_DOC, same, cap_old, cap_new))

# ---------------------------------------------------------------- ANYCASE (A7)
print("== ANYCASE: `any_case(/[a-z]x/ & /[A-Z]x/)`: the candidate body (sides take the flag first) against native")
EA_ARG = "/[a-z]x/ & /[A-Z]x/"
body_rx = ANYCASE_BODY.strip("/")


TEXTS3 = [''.join(p) for n in range(0, 4) for p in itertools.product("aAbBxXzZ7", repeat=n)]
members = [t for t in TEXTS3 if re.fullmatch(r"[a-z]x", t) and re.fullmatch(r"[A-Z]x", t)]
native = Re("|".join(re.escape(x) for x in members) or "(?!)", re.I)
base_binds()
OPT.clear()
mk0 = fresh("k")
side2 = p_alt(Src("(?i:[A-Z]x)")) if not sab("s12") else p_alt(Src("[A-Z]x"))
inner_t = node_ref(("mark", mk0)) + "(?:(?i:[a-z]x))" + node_ref(("andpat", mk0, side2))
Pbody = Prog(body_rx.replace("${rx}", inner_t))
L_AC_B = doc_line("The candidate body: " + fmt(Pbody, ["ax", "AX"], "-Ax", "ax 7x AX") +
                  " (`any_case(%s)`, the body `%s`)" % (EA_ARG, ANYCASE_BODY), "any-case")
L_AC_N = doc_line("Native: " + fmt(native, ["ax", "AX"], "-Ax", "ax 7x AX") + " (the same call)", "any-case")
print("   " + L_AC_B)
print("   " + L_AC_N)
nb = sum(1 for t in TEXTS3 if Pbody.whole(t))
nn = sum(1 for t in TEXTS3 if native.whole(t))
hand = sum(1 for t in TEXTS3 if re.fullmatch(r"[a-z]x", t, re.I) and re.fullmatch(r"[A-Z]x", t, re.I))
check("ANYCASE", nb == hand == 16 and nn == 0 and members == [],
      "of %d texts over `aAbBxXzZ7` (length <= 3): members of the argument %s ; the body WHOLE on %d (python `re`, "
      "each side under re.I: %d), native on %d" % (len(TEXTS3), members, nb, hand, nn))

# ---------------------------------------------------------------- ARRORDER (A11): order, index past the end, `$` in a question
print("== ARRORDER: the array's order with a lookahead; `h[k]` past the array's end; a `$` read inside a group question")
E11 = '/(?:(?=\\d(?<h>\\d))(?<h>\\d))+\\d/ & (h[2]: "1")'
L_AO = show("A lookahead in a pass", E11, [], ["12", "123"], "x123", "123 12", " (`%s`)" % E11, "array-vs-passes")
L_AO_T = show("", E11, [], ["12", "123"], "x123", "123 12", "", None)
E11b = '/(?:(?<h>\\d)?;)+/ & NOT (h[2]: "5")'
L_AE = show("Past the end", E11b, [], ["3;", "3;;", "3;5;"], "x3;", "3; 3;5;", " (`%s`)" % E11b, "array-vs-passes")
E11c = "/(?:(?<h>\\d)(?<m>\\d),)+/ & some((h: $m))"
L_AM = show("A read inside", E11c, [], ["11,23,", "12,31,", "12,"], "x11,23,", "11,23, 12,31, 12,",
            " (`%s`)" % E11c, "array-vs-passes")
for L in (L_AO, L_AE, L_AM):
    print("   " + L)
r12 = prog('/(?:(?=\\d(?<h>\\d))(?<h>\\d))+\\d/').at("12", 0, need_end=2)
order = settings(r12[2].log, "h@top", "top")
POPO = pop("135;,", 4)
Pb11 = prog(E11b)
ae = sum(1 for t in POPO if Pb11.whole(t) != (re.fullmatch(r"(?:\d?;)+", t) is not None
                                               and (re.findall(r"\d", t) + [None, None])[1] != "5"))
check("ARRORDER", order == ["2", "1"] and "`12` HOLDS" in L_AO and ae == 0 and "`12,31,` HOLDS" in L_AM
      and "`11,23,` FAILS" in L_AM,
      "the settings of h on `12` in the order made: %s (the lookahead's first) ; WHOLE past the end against the "
      "direct count (python `re` fullmatch `(?:\\d?;)+` and the second digit not 5): %d of %d differ (a missing k-th "
      "setting fails the test, NOT of it holds) ; `$m` reads the last pass's m" % (order, ae, len(POPO)))

# ---------------------------------------------------------------- EVERYNONE (MODES-12): a loop with no pass
print("== EVERYNONE: every-pass's settings form and item form on a loop that can make no pass")
EE = '/(?:(?<d>\\d),)*x/ & some((d: "7")) & occurs.none(NOT (d: "7"))'
EI = '/(?:(?<d>\\d)${(d: "7")},)*x/'
TE_ = ["x", "7,x"], "-x", "x 7,x 1,x"
L_EN = show("No pass, every setting", EE, [], *TE_, " (`%s`)" % EE, "every-pass")
L_EI = show("No pass, the item form", EI, [], *TE_, " (`%s`)" % EI, "every-pass")
print("   " + L_EN)
print("   " + L_EI)
if sab("s14"):
    L_EN = L_EI
check("EVERYNONE", "`x` FAILS" in L_EN and "`x` HOLDS" in L_EI,
      "on `x` (no pass): the settings form FAILS (`some` false on an empty array), the item form HOLDS")

# ---------------------------------------------------------------- LIFTORDER (D9): class-hole-order, lowered from the text
print("== LIFTORDER: `/${/[${c}]/ + 1}/`, c := [`9`, `0`], and `/${/[09]/ + 1}/`, lowered from the program text")


def lift_program(text, binds):
    """`/${X + n}/` with X a class literal, possibly holding a class-member hole: the lift of `+ n` over X's
    enumerate. A class holding a hole is the alternation of one class per value, in written order
    (core/holes/class); one class enumerates in ascending codepoint order (core/arrays/class-order)."""
    mm = re.fullmatch(r"/\$\{/\[(.*)\]/ \+ (\d+)\}/", text)
    cls, n = mm.group(1), int(mm.group(2))
    hm = re.fullmatch(r"\$\{(\w+)\}", cls)
    if hm:
        vals = binds[hm.group(1)]
        if sab("s15"):
            vals = sorted(vals)
        members = [v for v in vals]                      # one class per value: `[9] | [0]`
    else:
        members = sorted(cls)
    out = []
    for v in members:
        r = str(int(v) + n)
        if r not in out:
            out.append(r)
    return "(?:%s)" % "|".join(out)


LO1 = "/${/[${c}]/ + 1}/"
LO2 = "/${/[09]/ + 1}/"
rx1, rx2 = lift_program(LO1, {"c": ["9", "0"]}), lift_program(LO2, {})
TL = ["10", "1"], "x10", "10 1 101"
L_LO1 = doc_line(fmt(Re(rx1), *TL) + " (`%s`, c := [`9`, `0`]: the alternation `[9] | [0]`, `%s`)" % (LO1, rx1), "lift-order")
L_LO2 = doc_line("The class written by hand: " + fmt(Re(rx2), *TL) + " (`%s` is `%s`)" % (LO2, rx2), "lift-order")
print("   " + L_LO1)
print("   " + L_LO2)
check("LIFTORDER", rx1 == "(?:10|1)" and rx2 == "(?:1|10)",
      "lowered from the text: %s and %s" % (rx1, rx2))

# ---------------------------------------------------------------- RECORD (A9): a record inside a group question
print("== RECORD: `some((h: \"5\", m: \"3\"))` read as the product of its entries; its joint spelling refused")
ER = '/(?:(?<h>\\d):(?<m>\\d),)+/ & some((h: "5", m: "3"))'
EJ = '/(?:(?<h>\\d):(?<m>\\d),)+/ & some(((h, m): ("5", "3")))'
L_RS = show("The record, the reading today", ER, [], ["5:1,2:3,", "5:3,", "2:1,"], "2:1, 5:1,2:3,",
            "5:1,2:3, 2:1, 5:3,", " (`%s`; the joint spelling `some(((h, m): (\"5\", \"3\")))` is a compile error)" % ER,
            "record-in-some")
print("   " + L_RS)
r_joint = refused(EJ)
POPR = pop("53:,", 4)
PR = prog(ER)
rd = sum(1 for t in POPR if PR.whole(t) != (re.fullmatch(r"(?:\d:\d,)+", t) is not None
                                            and "5" in re.findall(r"(\d):", t) and "3" in re.findall(r":(\d)", t)))
if sab("s19"):
    r_joint = None
check("RECORD", rd == 0 and r_joint is not None and "`5:1,2:3,` HOLDS" in L_RS,
      "of %d texts over `53:,`: WHOLE against the direct product (some h is 5 and some m is 3) %d differ ; the joint "
      "spelling refused: %s" % (len(POPR), rd, r_joint))

# ---------------------------------------------------------------- HISEX: his two bound-condition examples
print("== HISEX: his two examples, lowered from the text (the record ran the hand-lowered `5` and `.5`)")
HX1 = "/\\d${(0: 5)}/"
HX2 = "/.${A & (0: 5)}/"
L_HX1 = show("His first example", HX1, [], ["5", "7"], "x75", "5 7 55", " (`A := %s`)" % HX1, "bound-condition")
L_HX2 = show("His second example", HX2, ["A := /\\d/"], ["x5", "x7", "55"], "a7 b5", "x5 y7 55",
             " (`C := %s`, A := `/\\d/`)" % HX2, "bound-condition")
print("   " + L_HX1)
print("   " + L_HX2)
POPH = pop("57x ", 3)
h1 = ndiff(answers(prog(HX1), POPH), answers(Re(r"5"), POPH))
h2 = ndiff(answers(prog(HX2, ["A := /\\d/"]), POPH), answers(Re(r".5"), POPH))
check("HISEX", h1 == h2 == (0, 0, 0),
      "of %d texts over `57x `: his first against `5` %s, his second against `.5` %s" % (len(POPH), h1, h2))

# ---------------------------------------------------------------- QUOTES
print("== QUOTES: the owner's words this lane quotes, verbatim in the record")
QUOTED = [
    "array-scope: the only way to do it is by the scope of the entire rx. As you say, you could limit it by grouping "
    "labels. So x.@a. (?spelling?).",
    "lol. i meant b",
    "bare-nested-scope: case 1: compile error at inner.",
    "bindings define scope. if they must refer to each other then construct in predicate with labels or create them "
    "in the same literal.",
    "X should not have a compare with predecessor test defined in a single binding because it has no meaning.",
    "bound-condition: A := /\\d${(0: 5)}/ binds the literal to 5. A := /\\d/ C := /.${A & (0: 5)}/ the 0: is bound to A "
    "only",
    "that settles it. my two examples are correct.",
    "isodate and all the other libraries don't want to presume everyone is interested in every label being a capture.",
    "ascending codepoints everywhere makes sesne.",
    "a compose and a literal rx have the same label behavior",
    "For A & B: from the perspective of B, the subject is now whatever A matched. There is no outside subject (unless "
    "we allow context, etc). That's its whole world.",
    "i am probably going to rule that only i is inherited this way as it doesn't make sense for any other flag.",
    "Only solution is sorting output when needed.",
    "array-in-piece: if it was written A & /B-defintion/ then the some(h) would see the h from A. but because B is "
    "bound first, its internal references refer only to what can be seen at that point.",
    "or A SEQ /B definition/",
    "bound-condition: the form A := (x: blah) has to be illegal. x has no references in the binding.",
    "bound-condition: correction to rx: B(d & isodate) := (year: < 2100)",
]
if sab("s16"):
    QUOTED[1] = QUOTED[1].replace("lol", "ok")
qmiss = [q for q in QUOTED if ws(q) not in RECORD_WS]
check("QUOTES", not qmiss, "%d quoted sentences; missing from the record: %s" % (len(QUOTED), qmiss))

# ---------------------------------------------------------------- MARKS: what the dispositions put where
print("== MARKS: array-in-piece stated where the array is, the bound-condition readers, the new open pieces")


def piece(text, tag):
    i = text.index("[%s]" % tag)
    i = text.rindex("\n### ", 0, i)
    j = text.find("\n### ", i + 1)
    k = text.find("\n## ", i + 1)
    j = min(x for x in (j, k, len(text)) if x > 0)
    return text[i:j]


READERS = [("core", "core/conditions/pass-start-read"), ("core", "core/values/computed-labels"),
           ("core", "core/labels/labels-vs-captures/array-vs-passes"), ("lib", "lib/counting/count"),
           ("lib", "lib/modifiers/length"), ("lib", "lib/modifiers/month-numbered"), ("core", "core/holes/bare-condition")]
CORE_M = CORE
if sab("s17"):                                   # one reader's pointer dropped: pass-start-read's
    _ps = piece(CORE, "core/conditions/pass-start-read")
    CORE_M = CORE.replace(_ps, _ps.replace("core/holes/bare-condition/bound-condition", "core/holes/bare-condition"))
pointers = [(t, "core/holes/bare-condition/bound-condition" in piece(CORE_M if f == "core" else LIB, t)) for f, t in READERS]
ARR_Q = "its internal references refer only to what can be seen at that point"
coll = [(t, "array-in-piece" in piece(CORE if t.startswith("core") else LIB, t) and
         (ARR_Q in piece(CORE, t) if t in ("core/labels/labels-vs-captures", "core/holes/bare-condition/nested-scope") else True))
        for t in ("core/labels/labels-vs-captures", "core/labels/labels-vs-captures/array-vs-passes",
                  "core/holes/bare-condition/nested-scope", "lib/counting/some", "lib/counting/count", "lib/counting/occurs")]
opens = [(t, re.search(r"\[%s\]\s+open %s " % (re.escape(t), s), CORE + LIB) is not None) for t, s in
         (("core/holes/bare-condition/bound-condition", "bound-condition"),
          ("core/conditions/form/record-in-some", "record-in-some"))]
gloss = "(a binding or a macro body)" not in piece(CORE, "core/conditions/match-so-far").split("\n")[2]
check("MARKS", all(x for _, x in pointers) and all(x for _, x in coll) and all(x for _, x in opens) and gloss,
      "bound-condition readers %s ; array-in-piece stated %s ; open pieces %s ; the gloss out of match-so-far's statement: %s"
      % (pointers, coll, opens, gloss))

# ---------------------------------------------------------------- DOC
print("== DOC: every formatted line occurs verbatim in the documents (report lines in the report)")
lines = list(LINES)
if sab("s18"):
    lines[0] = (lines[0][0], lines[0][1].replace("`7;1`", "`8;1`", 1))
REPORT_PATH = os.path.join(W, "docs", "dev", "lanes", "predfix77_report.md")
REPORT = read(REPORT_PATH) if os.path.exists(REPORT_PATH) else ""
missing = [(t, L) for t, L in lines if L not in (REPORT if t == "report" else DOCS)]
for t, L in lines:
    print("   [%s] %s" % (t, L))
check("DOC", not missing, "%d lines (%d in the report); missing: %s"
      % (len(lines), sum(1 for t, _ in lines if t == "report"), missing))

print("predfix77_model: %d checks, %d failed%s" % (len(CHECKS), len(FAILED), (" (" + ", ".join(FAILED) + ")") if FAILED else ""))
if os.environ.get("PREDFIX77_DUMP"):                         # the lane's own fill step (scratch path; not a check)
    import json
    with open(os.environ["PREDFIX77_DUMP"], "w") as f:
        json.dump(LINES, f)
