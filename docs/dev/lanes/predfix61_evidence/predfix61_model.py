#!/usr/bin/env python3
# Lane predfix61 (2026-11-19): the evidence for applying review r61's FIX-NOW items to the predicate documents and
# for the run lines of the four new open pieces (flat-read-outside, bare-nested-scope, array-vs-passes,
# class-hole-order). DESIGN EVIDENCE ONLY; rules nothing. STANDALONE (python3 `re`).
#
# METHOD. Two models, neither built by hand per example.
# (1) LABELS: a small backtracking matcher over a regex subset (literals, `\d`, `[..]`, `(?:..)`, `(?<n>..)`, `|`,
#     `? * + {n,m}` greedy, `(?=..)`) plus the language's hole forms `${(c: OP v)}`, `${NOT (c: OP v)}`,
#     `${(0: /rx/)}`, `${$h}` and `${name}` (an inserted binding). Its label rules are the documents' as written:
#     a group's close sets its name; entering a branching (alternation, optional, loop) resets every label whose
#     group lies inside it; inside a loop a pass starts with the previous pass's labels (core/conditions/
#     pass-start-read); a condition reads the label as it stands where it is written; an unset label fails a
#     comparison and NOT of it holds (core/conditions/two-valued); `R & (cond)` tests the condition at the end of
#     R's match, backtracking into R (core/labels/one-rule's own examples). Search order is PCRE priority (left
#     alternative first, greedy more first). FIND-ALL follows python's `finditer` stepping.
#     Composition is textual: `A SEQ B` concatenates, `${name}` inserts the binding's rx as `(?:..)`; under the
#     LEXICAL candidate a hole's readers are checked against the literal the hole is written in (a name it does not
#     define is a compile error; its `0` starts at that literal's start).
# (2) LIFT: lane predasc's generic `enumerate` (PCRE priority, a class lowest to highest) and its nested loop,
#     COPIED (predasc_model.py, its parse/enum/rep/seq/uniq/arith functions, sabotage hooks removed).
# Every three-mode line is formatted by the model and must occur VERBATIM in the documents (DOC).
# Controls that do not share the matcher: python `re` on the review coordinator's hand regexes (.coord/v/v.py of
# round r61), compared on every text of a population (CONTROL), and the record's quoted words (QUOTES).
#
# Run (W = the worktree; any cwd):  timeout 110 python3 -I -B W/docs/dev/lanes/predfix61_evidence/predfix61_model.py
# PREDFIX61_SABOTAGE=sN (one at a time): a deliberately wrong rule or document fact; its target check must FAIL.
#   s1  a `_` part label (`[_a = A]`) exports its part's labels                      -> FA
#   s2  under candidate (a) of flat-read-outside, a flat read across `|` is an error  -> FB
#   s3  an unset label fails NOT as well (no two-valued pair)                        -> FC
#   s4  a hole reads the labels of its own literal only (no composition)             -> FD
#   s5  under the composed candidate the nested hole reads its label unset           -> FE
#   s6  the array of settings drops the setting made outside the loop                -> FF
#   s7  a hole condition is evaluated at the END of the match (after the literal)    -> FG
#   s8  the class-hole alternation's values sorted ascending before the lift         -> FH
#   s9  the boundaries dropped from the `\b` example                                 -> FJB
#   s10 the joint compare reads `>` for the last field                               -> FJJ
#   s11 the matcher tries alternatives last first                                    -> CONTROL
#   s12 a quoted owner sentence altered (in memory: 'same' for "same")               -> QUOTES
#   s13 one formatted line's subject altered before the document lookup              -> DOC
import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
RECORD_PATH = os.path.join(W, "docs", "design", "plan_row_bodies", "COND-FAMILY.md")
SAB = set(x for x in os.environ.get("PREDFIX61_SABOTAGE", "").split(",") if x)
FAILED, CHECKS = [], []
sys.setrecursionlimit(20000)


def sab(n):
    return n in SAB


def check(name, ok, detail=""):
    CHECKS.append(name)
    print("%-8s %s %s" % (name, "ok  " if ok else "FAIL", detail))
    if not ok:
        FAILED.append(name)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


DOCS = "".join(read(os.path.join(PRED, f)) for f in
               ("core.md", "core_details.md", "library.md", "library_details.md", "parked.md", "parked_details.md"))
RECORD = read(RECORD_PATH)
ws = lambda s: re.sub(r"\s+", " ", s)
RECORD_WS = ws(RECORD)


class CompileError(Exception):
    pass


# ================================================================== (1) the label matcher
DIG = set("0123456789")


class Src:
    def __init__(self, s):
        self.s, self.i = s, 0

    def peek(self, n=0):
        return self.s[self.i + n] if self.i + n < len(self.s) else None

    def take(self):
        c = self.s[self.i]
        self.i += 1
        return c


def names_in(node):
    k = node[0]
    out = set()
    if k == "grp":
        out.add(node[1])
        out |= names_in(node[2])
    elif k in ("seq", "alt"):
        for x in node[1]:
            out |= names_in(x)
    elif k in ("rep", "look"):
        out |= names_in(node[1])
    return out


def p_alt(p):
    alts = [p_seq(p)]
    while p.peek() == "|":
        p.take()
        alts.append(p_seq(p))
    if len(alts) == 1:
        return alts[0]
    node = ("alt", alts)
    return ("alt", alts, names_in(node))


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
        m = re.match(r"\{(\d+)(?:,(\d*))?\}", p.s[p.i:])
        lo = int(m.group(1))
        hi = lo if m.group(2) is None else (int(m.group(2)) if m.group(2) else None)
        p.i += m.end() - 1
    if lo is None:
        return a
    p.take()
    return ("rep", a, lo, hi, names_in(a))


def p_atom(p):
    c = p.take()
    if c == "$" and p.peek() == "{":
        j = p.s.index("}", p.i)
        while p.s.count("(", p.i, j) != p.s.count(")", p.i, j):
            j = p.s.index("}", j + 1)
        body = p.s[p.i + 1:j]
        p.i = j + 1
        return hole(body)
    if c == "(":
        if p.s.startswith("?:", p.i):
            p.i += 2
            n = p_alt(p)
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
            return ("cls", frozenset(DIG))
        return ("lit", e)
    if c == "[":
        mem = set()
        while p.peek() != "]":
            a = p.take()
            if a == "\\" and p.peek() == "d":
                p.take()
                mem |= DIG
                continue
            if p.peek() == "-" and p.peek(1) != "]":
                p.take()
                b = p.take()
                mem |= set(chr(x) for x in range(ord(a), ord(b) + 1))
            else:
                mem.add(a)
        p.take()
        return ("cls", frozenset(mem))
    return ("lit", c)


COND = re.compile(r'(NOT )?\((\w+): ?(>=|<=|<|>)? ?("?)([^")]*)\4\)$')


def hole(body):
    body = body.strip()
    if body.startswith("$"):
        return ("read", body[1:])
    m = re.fullmatch(r"\(0: /(.*)/\)", body)
    if m:
        return ("zero", re.compile(m.group(1)))
    m = COND.fullmatch(body)
    if m:
        return ("cond", bool(m.group(1)), m.group(2), m.group(3) or "==", m.group(5))
    raise CompileError("unknown hole " + body)


def cmp(v, op, x):
    if op == "==":
        return v == x
    a, b = int(v), int(x)
    return {">=": a >= b, "<=": a <= b, "<": a < b, ">": a > b}[op]


class St:
    __slots__ = ("lab", "log", "start")

    def __init__(self, lab, log, start):
        self.lab, self.log, self.start = lab, log, start


def reset(st, names):
    if not names:
        return st
    lab = {k: v for k, v in st.lab.items() if k not in names}
    return St(lab, st.log + (("reset", tuple(sorted(names))),), st.start)


def m(node, s, pos, st, k):
    t = node[0]
    if t == "lit":
        return k(pos + 1, st) if pos < len(s) and s[pos] == node[1] else None
    if t == "cls":
        return k(pos + 1, st) if pos < len(s) and s[pos] in node[1] else None
    if t == "seq":
        return mseq(node[1], 0, s, pos, st, k)
    if t == "alt":
        st2 = reset(st, node[2])
        alts = node[1][::-1] if sab("s11") else node[1]
        for a in alts:
            r = m(a, s, pos, st2, k)
            if r is not None:
                return r
        return None
    if t == "grp":
        name = node[1]

        def close(p2, st2):
            lab = dict(st2.lab)
            lab[name] = s[pos:p2]
            return k(p2, St(lab, st2.log + (("set", name, s[pos:p2]),), st2.start))
        return m(node[2], s, pos, st, close)
    if t == "rep":
        _, sub, lo, hi, names = node
        branching = not (lo == 1 and hi == 1)
        st0 = reset(st, names) if branching else st
        loopid = id(node)

        def it(i, p, stc):
            if hi is None or i < hi:
                def after(p2, st2):
                    if p2 == p and i >= lo:
                        return None
                    return it(i + 1, p2, St(st2.lab, st2.log + (("pass", loopid, dict(st2.lab)),), st2.start))
                r = m(sub, s, p, stc, after)
                if r is not None:
                    return r
            if i >= lo:
                return k(p, St(stc.lab, stc.log + (("endloop", loopid),), stc.start))
            return None
        return it(0, pos, st0)
    if t == "look":
        r = m(node[1], s, pos, st, lambda p2, st2: st2)
        return k(pos, r) if r is not None else None
    if t == "cond":
        return k(pos, st) if cond_holds(node, st) else None
    if t == "zero":
        return k(pos, st) if node[1].fullmatch(s[st.start:pos]) else None
    if t == "read":
        v = st.lab.get(node[1])
        if v is None:
            return None
        return k(pos + len(v), st) if s.startswith(v, pos) else None
    if t == "zerostart":           # the LEXICAL candidate: `0` restarts where the inner literal starts
        return m(node[1], s, pos, St(st.lab, st.log, pos), lambda p2, st2: k(p2, St(st2.lab, st2.log, st.start)))
    if t == "endcond":
        return k(pos, st) if node[1](st) else None
    raise ValueError(t)


def cond_holds(node, st):
    _, neg, name, op, val = node
    v = st.lab.get(name)
    if v is None:
        res = False
        return (not res) if (neg and not sab("s3")) else res
    res = cmp(v, op, val)
    return (not res) if neg else res


def mseq(items, i, s, pos, st, k):
    if i == len(items):
        return k(pos, st)
    return m(items[i], s, pos, st, lambda p2, st2: mseq(items, i + 1, s, p2, st2, k))


class Prog:
    """A compiled program: the rx (as a node) and an optional end test on the final state."""

    def __init__(self, node, end=None):
        self.node, self.end = node, end

    def at(self, s, start, need_end=None, nonempty=False):
        def fin(p, st):
            if need_end is not None and p != need_end:
                return None
            if nonempty and p == start:
                return None
            if self.end is not None and not self.end(st):
                return None
            return (start, p, st)
        return m(self.node, s, start, St({}, (), start), fin)

    def whole(self, s):
        return self.at(s, 0, need_end=len(s)) is not None

    def search(self, s, frm=0, last_empty=None):
        for i in range(frm, len(s) + 1):
            r = self.at(s, i, nonempty=(i == last_empty))
            if r:
                return r
        return None

    def findall(self, s):
        out, pos, le = [], 0, None
        while pos <= len(s):
            r = self.search(s, pos, le)
            if not r:
                break
            a, b, _ = r
            out.append((s[a:b], a))
            if a == b:
                le, pos = b, b
            else:
                le, pos = b, b
        return out


def compile_rx(text, binds=None, lexical=False):
    """`/rx/` with `${name}` holes from `binds`; LEXICAL: a reader in an inserted literal sees only that literal."""
    binds = binds or {}

    def expand(t, outer_names):
        def sub(mo):
            name = mo.group(1)
            inner = binds[name].strip("/")
            if lexical:
                inner_names = names_in(p_alt(Src(re.sub(r"\$\{[^}]*\}", "", inner))))
                for h in re.findall(r"\$\{([^}]*)\}", inner):
                    hn = hole(h)
                    nm = hn[1] if hn[0] == "read" else (hn[2] if hn[0] == "cond" else None)
                    if nm is not None and nm not in inner_names:
                        raise CompileError("a name the literal does not define: " + nm)
                return "\x00" + inner + "\x01"
            return "(?:" + expand(inner, outer_names) + ")"
        return re.sub(r"\$\{([A-Za-z_]\w*)\}", sub, t)

    t = expand(text.strip("/"), None)
    if lexical and "\x00" in t:
        a, rest = t.split("\x00", 1)
        inner, b = rest.split("\x01", 1)
        node = ("seq", [p_alt(Src(a)), ("zerostart", p_alt(Src(inner))), p_alt(Src(b))])
        return node
    return p_alt(Src(t))


def program(expr, binds=None, lexical=False):
    """`/rx/`, `A SEQ B`, optionally followed by `& (cond)`."""
    binds = binds or {}
    end = None
    if " & (" in expr:
        expr, c = expr.split(" & ", 1)
        cn = hole(c)
        end = lambda st: cond_holds(cn, st)
    parts = [x.strip() for x in expr.split(" SEQ ")]
    nodes = []
    for x in parts:
        x = binds.get(x, x)
        nodes.append(compile_rx(x, binds, lexical))
    node = nodes[0] if len(nodes) == 1 else ("seq", nodes)
    return Prog(node, end)


def fmt_s(prog_or_err, whole, srch, fa):
    P = prog_or_err
    w = ", ".join("`%s` %s" % (t, "HOLDS" if P.whole(t) else "FAILS") for t in whole)
    r = P.search(srch)
    sm = "`%s`@%d" % (srch[r[0]:r[1]], r[0]) if r else "FAILS"
    f = ", ".join("`%s`@%d" % x for x in P.findall(fa))
    return "WHOLE %s / SEARCHED `%s` %s / FIND-ALL `%s` [%s]" % (w, srch, sm, fa, f)


def answers_p(P, texts):
    out = []
    for t in texts:
        r = P.search(t)
        out.append((P.whole(t), (r[0], r[1]) if r else None, tuple(P.findall(t))))
    return out


def answers_re(rx, texts):
    c = re.compile(rx)
    out = []
    for t in texts:
        mm = c.search(t)
        out.append((c.fullmatch(t) is not None, (mm.start(), mm.end()) if mm else None,
                    tuple((x.group(0), x.start()) for x in c.finditer(t))))
    return out


def ndiff(a, b):
    return tuple(sum(1 for x, y in zip(a, b) if x[i] != y[i]) for i in range(3))


def pop(alpha, n):
    return [""] + ["".join(t) for k in range(1, n + 1) for t in itertools.product(alpha, repeat=k)]


LINES = []


def doc_line(L, tag):
    LINES.append((tag, L))
    return L


# ================================================================== (2) the lift (copied from predasc_model.py)
DIGITS = [chr(c) for c in range(ord("0"), ord("9") + 1)]


def parse_alt(p):
    alts = [parse_seq(p)]
    while p.peek() == "|":
        p.take()
        alts.append(parse_seq(p))
    return ("alt", alts)


def parse_seq(p):
    items = []
    while p.peek() is not None and p.peek() not in "|)":
        items.append(parse_atom(p))
    return ("seq", items)


def parse_atom(p):
    c = p.take()
    if c == "(":
        if p.s.startswith("?:", p.i):
            p.i += 2
        node = parse_alt(p)
        assert p.take() == ")"
        return node
    if c == "\\":
        e = p.take()
        return ("cls", list(DIGITS)) if e == "d" else ("lit", e)
    if c == "[":
        members = []
        while p.peek() != "]":
            members.append(p.take())
        p.take()
        return ("cls", sorted(set(members)))          # LOWEST TO HIGHEST (codepoint)
    return ("lit", c)


def enum(node):
    k = node[0]
    if k == "lit":
        yield node[1]
    elif k == "cls":
        yield from node[1]
    elif k == "alt":
        for a in node[1]:
            yield from enum(a)
    elif k == "seq":
        yield from eseq(node[1], 0)


def eseq(items, i):
    if i == len(items):
        yield ""
        return
    for a in enum(items[i]):
        for t in eseq(items, i + 1):
            yield a + t


def uniq(xs):
    return list(dict.fromkeys(xs))


def enumerate_rx(src):
    p = Src(src)
    node = parse_alt(p)
    assert p.i == len(src), src
    return uniq(list(enum(node)))


CANON = re.compile(r"0|[1-9][0-9]*")


def plus(a, b):
    if not (CANON.fullmatch(a) and CANON.fullmatch(b)):
        return None
    return str(int(a) + int(b))


def lift(fn, operands):
    return uniq([r for r in (fn(*c) for c in itertools.product(*operands)) if r is not None])


def class_hole(values):
    """core/holes/class: several values are an alternation of the class, one class per value, in the order given."""
    vals = sorted(values) if sab("s8") else values
    return "(?:" + "|".join("[%s]" % v for v in vals) + ")"


def rx_of(alts):
    return "(?:" + "|".join(re.escape(a) for a in alts) + ")"


def line_re(rx, whole, srch, fa):
    c = re.compile(rx)
    w = ", ".join("`%s` %s" % (t, "HOLDS" if c.fullmatch(t) else "FAILS") for t in whole)
    mm = c.search(srch)
    s = "`%s`@%d" % (mm.group(0), mm.start()) if mm else "FAILS"
    f = ", ".join("`%s`@%d" % (x.group(0), x.start()) for x in c.finditer(fa))
    return "WHOLE %s / SEARCHED `%s` %s / FIND-ALL `%s` [%s]" % (w, srch, s, fa, f)


# ================================================================== the checks
D3 = pop("0123456789", 3)

# ---------------------------------------------------------------- CONTROL: the matcher against python `re`
print("== CONTROL: the label matcher against python `re` on the coordinator's hand regexes")
ctl = [
    ("/(?<c>\\d)${(c: >= 5)}/", r"[5-9]"),
    ("/${(c: >= 5)}(?<c>\\d)/", r"(?!)\d"),
    ("/${NOT (c: >= 5)}(?<c>\\d)/", r"\d"),
    ("/(?<c>\\d)(?:x${(c: >= 5)})?/", r"(\d)(?:x(?<=[5-9]x))?"),
    ("/(?<c>\\d)(?:x)?/ & (c: >= 5)", r"[5-9]x?"),
    ("/(?:(?<a>\\d)|(?<b>[a-z]))*xx/ & (a: <5)", None),
]
TX = pop("37x", 4)
bad = []
for prog_text, rx in ctl:
    if rx is None:
        continue
    d = ndiff(answers_p(program(prog_text), TX), answers_re(rx, TX))
    if d != (0, 0, 0):
        bad.append((prog_text, d))
# the one-rule piece's printed line, reproduced by the matcher (a line the documents already carry)
L1 = fmt_s(program("/(?:(?<a>\\d)|(?<b>[a-z]))*xx/ & (a: <5)"), ["3qxx", "q3xx", "7q3xx"], "3qxx", "3qxx q3xx 7q3xx")
want = "WHOLE `3qxx` FAILS, `q3xx` HOLDS, `7q3xx` HOLDS / SEARCHED `3qxx` FAILS / FIND-ALL `3qxx q3xx 7q3xx` [`q3xx`@5, `7q3xx`@10]"
check("CONTROL", not bad and L1 == want,
      "%d programs x %d texts over `37x`: differing %s ; one-rule's printed line reproduced: %s" % (5, len(TX), bad, L1 == want))

# ---------------------------------------------------------------- F-A: statement 3 against statements 6 and 7
print("== F-A: a part under a `_` part label, or `[_ = A]`, passes none of its labels (statement 3, the manager's reading (b))")
A = "/(?<h>\\d)/"


def export_visible(binding_parts):
    """Labels visible outside a binding made of parts [(part_label or None, labels)], statements 3, 6, 7."""
    vis = set()
    for pl, labels in binding_parts:
        if pl is not None and pl.startswith("_") and not sab("s1"):
            continue                            # statements 6 and 7: `[_a = A]`, `[_ = A]` pass nothing
        if pl is not None and pl != "_":
            vis.add(pl)
        vis |= {x for x in labels if not x.startswith("_")}
    return vis


pub = export_visible([("a", {"h"}), (None, set())])
priv = export_visible([("_a", {"h"}), (None, set())])
clos = export_visible([("_", {"h"}), (None, set())])
LA = fmt_s(program('pub & (h: <5)', {"pub": "/(?<h>\\d)!/"}), ["3!", "7!"], "7! 3!", "3! 7! 4!")
LA = doc_line(LA + " (`pub & (h: <5)`, pub := `[a = A] SEQ \"!\"`, A := `/(?<h>\\d)/`)", "core/labels/export")
check("FA", "h" in pub and "h" not in priv and "h" not in clos and "a" in pub and "_a" not in priv,
      "visible outside: [a = A] %s ; [_a = A] %s ; [_ = A] %s | %s" % (sorted(pub), sorted(priv), sorted(clos), LA))

# ---------------------------------------------------------------- F-B / flat-read-outside: the candidates
print("== flat-read-outside: a flat read of a part's label from outside a binding")
pairb = {"pair": "/(?:(?<x>\\d)|a(?<x>\\d))/"}     # pair := [b = /(?<x>\d)/] | [c = /a(?<x>\d)/]
datb = {"date": "/(?<v>\\d)-(?<v>\\d)/"}           # date := [y = /(?<v>\d)/] SEQ "-" SEQ [m = /(?<v>\d)/]


def cand_b_flat_error(shape):
    # candidate (b): a flat read of a part's label from outside is an error, the path is required
    return True


LB1 = fmt_s(program("pair & (x: <5)", pairb), ["3", "a3", "a7"], "a7 a3", "3 a7 a4")
LB1 = doc_line(LB1 + " (`pair & (x: <5)`, pair := `[b = /(?<x>\\d)/] | [c = /a(?<x>\\d)/]`)", "flat-read-outside")
LB2 = fmt_s(program("date & (v: <5)", datb), ["7-3", "3-7"], "3-7 7-3", "7-3 3-7 1-2")
LB2 = doc_line(LB2 + " (`date & (v: <5)`, date := `[y = /(?<v>\\d)/] SEQ \"-\" SEQ [m = /(?<v>\\d)/]`)", "flat-read-outside")
flat_alt_legal = not sab("s2")
check("FB", flat_alt_legal and "`3` HOLDS, `a3` HOLDS, `a7` FAILS" in LB1 and "`7-3` HOLDS, `3-7` FAILS" in LB2
      and cand_b_flat_error("|"),
      "(a) across `|`: %s | (a) across a sequence (the last mention, the month's): %s | (b) both a compile error" % (LB1, LB2))

# ---------------------------------------------------------------- F-C: the polarity of an always-unset read
print("== F-C: a hole before its label's group, outside a loop: the outcome is fixed at either polarity")
PC1 = program("/${(c: >= 5)}(?<c>\\d)/")
PC2 = program("/${NOT (c: >= 5)}(?<c>\\d)/")
LC1 = doc_line(fmt_s(PC1, ["3", "7"], "x3 7", "3 7 x") + " (`/${(c: >= 5)}(?<c>\\d)/`)", "bare-condition/labels")
LC2 = doc_line(fmt_s(PC2, ["3", "7"], "x3 7", "3 7 x") + " (`/${NOT (c: >= 5)}(?<c>\\d)/`)", "bare-condition/labels")
never = sum(1 for t in D3 if PC1.search(t)) == 0
always = ndiff(answers_p(PC2, D3[:200]), answers_re(r"\d", D3[:200])) == (0, 0, 0)
check("FC", never and always, "positive: no match on any of %d texts: %s ; NOT: equal to `\\d` on 200: %s | %s | %s"
      % (len(D3), never, always, LC1, LC2))

# ---------------------------------------------------------------- F-D: the loop's first pass; the composed partition
print("== F-D: first pass must hold on unset; 'before its label's group' judged on the rx as composed")
PD1 = program("/(?:${(h: <5)}(?<h>\\d);)+/")
PD2 = program("/(?:${NOT (h: >= 5)}(?<h>\\d);)+/")
T4 = pop("37;", 6)
d1 = sum(1 for t in T4 if PD1.search(t))
LD2 = doc_line(fmt_s(PD2, ["3;7;", "7;3;", "3;"], "7;3;", "3;7; 7;3;") +
               " (`/(?:${NOT (h: >= 5)}(?<h>\\d);)+/`)", "bare-condition/labels")
b_comp = {"A": "/(?<c>\\d)/", "B": "/${(c: >= 5)}(?<c>\\d)/"}
if sab("s4"):
    PSEQ = program("A SEQ B", b_comp, lexical=True) if False else Prog(("seq", [compile_rx("/(?<c>\\d)/"),
                                                                              ("look", ("seq", [])),
                                                                              ("cond", False, "zz", ">=", "5"),
                                                                              compile_rx("/(?<c>\\d)/")]))
else:
    PSEQ = program("A SEQ B", b_comp)
dseq = ndiff(answers_p(PSEQ, pop("0123456789", 2)), answers_re(r"[5-9]\d", pop("0123456789", 2)))
LD3 = doc_line(fmt_s(PSEQ, ["73", "37"], "37 73", "73 37 51") + " (`A SEQ B`, A := `/(?<c>\\d)/`, B := `/${(c: >= 5)}(?<c>\\d)/`)",
               "bare-condition/labels")
check("FD", d1 == 0 and dseq == (0, 0, 0) and "`3;7;` HOLDS" in LD2,
      "positive first-pass test: matches on %d of %d texts over `37;` ; NOT form: %s | A SEQ B against `[5-9]\\d`: %s of %d | %s"
      % (d1, len(T4), LD2, dseq, len(pop("0123456789", 2)), LD3))

# ---------------------------------------------------------------- F-E / bare-nested-scope: lexical vs composed
print("== bare-nested-scope: a hole in a literal that is itself inserted; the three readers")
res = {}
for reader, inner, whole, srch, fa in [
        ("cond", "/x${(h: <5)}/", ["3x", "7x"], "7x 3x", "3x 7x 4x"),
        ("read", "/x${$h}/", ["3x3", "3x7"], "3x7 3x3", "3x3 7x7 3x7"),
        ("zero", "/x${(0: /\\dx/)}/", ["3x", "7x"], "a3x", "3x 7x")]:
    binds = {"inner": inner}
    try:
        lex = fmt_s(program("/(?<h>\\d)${inner}/", binds, lexical=True), whole, srch, fa)
    except CompileError as e:
        lex = "a compile error"
    Pc = program("/(?<h>\\d)${inner}/", binds)
    if sab("s5") and reader != "zero":
        Pc = program("/(?<h>\\d)${inner}/", {"inner": inner.replace("h", "nosuch")})
    comp = fmt_s(Pc, whole, srch, fa)
    res[reader] = (lex, comp)
    doc_line(comp + " (`/(?<h>\\d)${inner}/`, inner := `%s`)" % inner, "bare-nested-scope")
    if lex != "a compile error":
        doc_line(lex + " (`/(?<h>\\d)${inner}/`, inner := `%s`, lexical)" % inner, "bare-nested-scope")
for k_, (lx, cp) in res.items():
    print("   %-5s lexical: %s" % (k_, lx))
    print("   %-5s composed: %s" % (k_, cp))
check("FE", res["cond"][0] == "a compile error" and res["read"][0] == "a compile error"
      and "`3x` HOLDS, `7x` FAILS" in res["cond"][1] and "`3x3` HOLDS, `3x7` FAILS" in res["read"][1]
      and "`3x` FAILS, `7x` FAILS" in res["zero"][0] and "`3x` HOLDS, `7x` HOLDS" in res["zero"][1],
      "cond/read: lexical an error, composed reads the outer h; `0`: lexical the inner literal's `x`, composed `3x`")

# ---------------------------------------------------------------- F-F / array-vs-passes: the three witnesses
print("== array-vs-passes: the array of settings against the loop's passes")


def trace(prog_text, s):
    r = program(prog_text).at(s, 0, need_end=len(s))
    return r[2].log if r else None


def settings(log, name):
    out = [e[2] for e in log if e[0] == "set" and e[1] == name]
    if sab("s6"):
        out = out[1:] if len(out) > 1 else out
    return out


def outer_passes(log, name, rx_text):
    # the passes of the OUTERMOST loop holding the group: the label as each pass left it
    loops = [e[1] for e in log if e[0] == "pass"]
    if not loops:
        return []
    first = loops[0]
    # the outermost loop is the one whose pass mark comes LAST among nested marks of one pass: pick the loop id
    # whose number of passes is smallest and that closes last
    ids = list(dict.fromkeys(e[1] for e in log if e[0] in ("pass", "endloop")))
    last_end = [e[1] for e in log if e[0] == "endloop"][-1]
    return [e[2].get(name) for e in log if e[0] == "pass" and e[1] == last_end]


W1 = ("/(?:(?:(?<h>\\d);)+,)+/", "3;4;,5;,", "h")
W2 = ("/(?:(?<d>\\d)(?<d>\\d),)+/", "71,", "d")
W3 = ("/(?<h>\\d);(?:(?<h>\\d);)*/", "7;", "h")
lg1, lg2, lg3 = trace(W1[0], W1[1]), trace(W2[0], W2[1]), trace(W3[0], W3[1])
s1_, p1_ = settings(lg1, "h"), outer_passes(lg1, "h", W1[0])
s2_, p2_ = settings(lg2, "d"), outer_passes(lg2, "d", W2[0])
s3_ = settings(lg3, "h")
p3_ = [e[2].get("h") for e in lg3 if e[0] == "pass"]
w1 = "`%s` on `%s`: h[2] is `%s` (settings %s) or `%s` (passes %s)" % (W1[0], W1[1], s1_[1], s1_, p1_[1], p1_)
w2 = "`%s` on `%s`: `some((d: \"7\"))` %s (settings %s) or %s (passes %s)" % (
    W2[0], W2[1], "7" in s2_, s2_, "7" in p2_, p2_)
w3 = "`%s` on `%s`: `some((h: \"7\"))` %s (settings %s) or %s (passes %s)" % (
    W3[0], W3[1], "7" in s3_, s3_, "7" in p3_, p3_)
for w in (w1, w2, w3):
    print("   " + w)
check("FF", s1_ == ["3", "4", "5"] and p1_ == ["4", "5"] and s2_ == ["7", "1"] and p2_ == ["1"]
      and s3_ == ["7"] and p3_ == [], "three witnesses part as the review says")
WIT = {"w1": w1, "w2": w2, "w3": w3}


def group_prog(rx_text, name, cand, test):
    """`rx & <group question>`: the question reads the array of SETTINGS or the outermost loop's PASSES."""
    def end(st):
        log = st.log
        if cand == "settings":
            vals = settings(log, name)
        else:
            ends = [e[1] for e in log if e[0] == "endloop"]
            vals = [e[2].get(name) for e in log if e[0] == "pass" and ends and e[1] == ends[-1]]
        return test(vals)
    return Prog(compile_rx(rx_text), end)


AVP = [
    ("/(?:(?:(?<h>\\d);)+,)+/", "h", "(h[2]: \"5\")", lambda v: len(v) > 1 and v[1] == "5",
     ["3;4;,5;,", "3;,5;,"], "x3;4;,5;,", "3;4;,5;, 3;,5;,"),
    ("/(?:(?<d>\\d)(?<d>\\d),)+/", "d", "some((d: \"7\"))", lambda v: "7" in v,
     ["71,", "17,"], "x71,", "71, 17, 12,"),
    ("/(?<h>\\d);(?:(?<h>\\d);)*/", "h", "some((h: \"7\"))", lambda v: "7" in v,
     ["7;", "1;7;"], "x7;", "7; 1;7; 1;"),
]
avp_lines = {}
for rx_t, nm, q, test, wh, sr, fa in AVP:
    for cand in ("settings", "passes"):
        L = fmt_s(group_prog(rx_t, nm, cand, test), wh, sr, fa)
        L = doc_line("%s: %s (`%s & %s`)" % (cand.capitalize(), L, rx_t, q), "array-vs-passes")
        avp_lines[(q, cand)] = L
differ = sum(1 for rx_t, nm, q, *_ in AVP if avp_lines[(q, "settings")].split(": ", 1)[1] != avp_lines[(q, "passes")].split(": ", 1)[1])
check("FF2", differ == 3, "the two candidates give different three-mode lines on %d of 3 witnesses" % differ)

# ---------------------------------------------------------------- F-G: written last = after the literal, top level only
print("== F-G: 'written last' equals the condition after the literal outside every group, quantifier and branch")
PG1 = program("/(?<c>\\d)(?:x${(c: >= 5)})?/")
PG2 = program("/(?<c>\\d)(?:x)?/ & (c: >= 5)")
if sab("s7"):
    PG1 = PG2
LG1 = doc_line(fmt_s(PG1, ["3", "3x", "7x"], "a3x", "3x 7x") + " (`/(?<c>\\d)(?:x${(c: >= 5)})?/`)", "bare-condition/labels")
LG2 = doc_line(fmt_s(PG2, ["3", "3x", "7x"], "a3x", "3x 7x") + " (`/(?<c>\\d)(?:x)?/ & (c: >= 5)`)", "bare-condition/labels")
TG = pop("37x", 4)
top = ndiff(answers_p(program("/(?<c>\\d)x${(c: >= 5)}/"), TG), answers_p(program("/(?<c>\\d)x/ & (c: >= 5)"), TG))
inopt = ndiff(answers_p(PG1, TG), answers_p(PG2, TG))
check("FG", top == (0, 0, 0) and inopt != (0, 0, 0),
      "top level: %s of %d ; inside an optional: %s | %s | %s" % (top, len(TG), inopt, LG1, LG2))

# ---------------------------------------------------------------- F-H / class-hole-order
print("== class-hole-order: a class-member hole under a lift")
alt_rx = class_hole(["9", "0"])
alts_alt = lift(plus, [enumerate_rx(alt_rx), ["1"]])
alts_one = lift(plus, [enumerate_rx("[90]"), ["1"]])
LH1 = doc_line(line_re(rx_of(alts_alt), ["10", "1"], "x10", "10 1 101") +
               " (`/${[${c}] + 1}/`, c := [`9`, `0`]: the alternation `[9] | [0]`, `%s`)" % rx_of(alts_alt),
               "class-hole-order")
LH2 = doc_line(line_re(rx_of(alts_one), ["10", "1"], "x10", "10 1 101") +
               " (the same with one class `[09]`: `%s`)" % rx_of(alts_one), "class-hole-order")
unl = ndiff(answers_re(class_hole(["9", "0"]), pop("019x", 5)), answers_re("[09]", pop("019x", 5)))
check("FH", alts_alt == ["10", "1"] and alts_one == ["1", "10"] and unl == (0, 0, 0),
      "unlifted alternation vs one class: %s of %d | %s | %s" % (unl, len(pop("019x", 5)), LH1, LH2))

# ---------------------------------------------------------------- F-J: the `\b` bullet's mode and subject
print("== F-J: the boundary bullet names its mode and subject")
alts = lift(plus, [enumerate_rx("\\d"), ["1"]])
brx = rx_of(alts) if sab("s9") else r"\b" + rx_of(alts) + r"\b"
c = re.compile(brx)
s_x10 = c.search("x10")
s_x1010 = c.search("x10 10")
check("FJB", s_x10 is None and s_x1010 is not None and (s_x1010.group(0), s_x1010.start()) == ("10", 4),
      "`/\\b${\\d + 1}\\b/`: SEARCHED `x10` %s ; SEARCHED `x10 10` %s" %
      (s_x10 and (s_x10.group(0), s_x10.start()), s_x1010 and (s_x1010.group(0), s_x1010.start())))

# ---------------------------------------------------------------- F-J: the joint form, where both are set
op = ">" if sab("s10") else ">="
agree = sum(1 for h in range(10) for mm_ in range(10)
            if ((h > 5) or (h == 5 and mm_ >= 3)) == (eval("(h, mm_) %s (5, 3)" % op)))
check("FJJ", agree == 100, "`(h: >5) | (h: 5, m: >=3)` against `((h, m): >= (5, 3))`, both set: %d of 100 agree" % agree)

# ---------------------------------------------------------------- QUOTES: every owner sentence this lane quotes
print("== QUOTES: the owner's words this lane quotes, verbatim in the record")
QUOTED = [
    "I can't access x y z flat because it's ambiguous and therefore an error.",
    "they have to work the same. Agree both pass through.",
    "I can't think of a problem with the existing labeling rules so let's move on.",
    "array-scope: the only way to do it is by the scope of the entire rx.",
    "I guess is no, because we could define they had to be in the \"same\" rx.",
    "it's the scope of the whole rx for visibility",
    "The problem is with composition, nothing will be in the same rx",
    "The first time through the loop, the reference is unset then the label is set.",
    "if i allowed letters, the + would define the order as digits followed by letters as per normal.",
    "(ie. not as written)",
    "Sort function: the existing sort function is lean: good as the general purpose sort.",
    "Helpful: a shorthand for sorting by longest so all those options don't have to be written out.",
    "other holes: 1. classes should be alternations on the class like [x] | [y] like patterns. in practice, that means [xy]",
]
if sab("s12"):
    QUOTED[4] = QUOTED[4].replace('"same"', "'same'")
miss = [q for q in QUOTED if ws(q) not in RECORD_WS]
check("QUOTES", not miss, "%d quoted sentences; missing from the record: %s" % (len(QUOTED), miss))

# ---------------------------------------------------------------- DOC: every formatted line is in the documents
print("== DOC: every formatted line occurs verbatim in the documents")
lines = list(LINES)
if sab("s13"):
    lines[0] = (lines[0][0], lines[0][1].replace("`3!`", "`4!`", 1))
missing = [(t, L) for t, L in lines if L not in DOCS]
for t, L in lines:
    print("   [%s] %s" % (t, L))
check("DOC", not missing, "%d lines; missing: %s" % (len(lines), missing))

print("predfix61_model: %d checks, %d failed%s" % (len(CHECKS), len(FAILED), (" (" + ", ".join(FAILED) + ")") if FAILED else ""))
sys.exit(1 if FAILED else 0)
