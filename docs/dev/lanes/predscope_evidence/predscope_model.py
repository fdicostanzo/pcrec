#!/usr/bin/env python3
# Lane predscope (2026-11-21): the evidence for folding the owner's rulings of 2026-11-21 (pure-label, the `_`
# labels, zero-in-definition, his three scope examples) into the predicate documents, and for testing the manager's
# readings of that day. DESIGN EVIDENCE ONLY; rules nothing. STANDALONE (python3 `re`).
#
# METHOD. Every program is LOWERED MECHANICALLY from its text as the documents and the record print it:
#   - a small expression lowerer: `A SEQ B` (each operand `(?:..)`), `P | Q`, `[x = E]` (a label, lowered to the
#     named group the label matcher reads; whether it is a CAPTURE is tracked apart, below), `/rx/` with its holes,
#     `"s"`, a name (a binding), a macro call `m(args)` (a macro is a FUNCTION over rx text: its body text is
#     lowered with the parameters bound to the arguments, each argument lowered first in the CALLER's environment),
#     a trailing `& (cond)`; the library bodies it needs (`rx.digit`, `repeat(x, min)`, `rx.digits`) are READ from
#     library.md, not retyped;
#   - lane predfix61's backtracking label matcher (COPIED, with `\w`, a canonical-numeral domain for comparisons,
#     and two scope nodes added): a group's close sets its name, a branching resets the labels inside it, a
#     condition reads the labels as they stand, an unset label fails a comparison and NOT of it holds; `(?Z:..)`
#     restarts the match so far (`0`) at a definition's start, `(?S:..)` hides the user's labels from a definition
#     (the CLOSED variants of the questions);
#   - the CAPTURES the caller gets are computed from the same lowering: a group written in rx text or by a capture
#     form, public (no `_`); a `[x = A]` label is no capture (pure-label (a)).
# Every three-mode line printed for the documents must occur VERBATIM in them (DOC). Controls that do not share
# the matcher: python `re` on independent hand regexes (CONTROL), python `re`'s own group values (LOOPVAL), python
# `re` over the whole codepoint range (CASELESS, BYTES, CLASSV), the record's printed lines and quoted words
# (RECORD, QUOTES).
#
# Run (W = the worktree; any cwd):  timeout 110 python3 -I -B W/docs/dev/lanes/predscope_evidence/predscope_model.py
# PREDSCOPE_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
#   s1  the matcher tries alternatives last first                                         -> CONTROL
#   s2  a `[x = A]` label counted as a capture (the narrowing of statement 5 undone)        -> CAPT
#   s3  a `_` label exported as a caller capture                                         -> CAPT
#   s4  the comparison domain drops the canonical-numeral rule (`042` is under 100)        -> EX1
#   s5  example 2's body condition resolved where the macro ends up (composed), no refusal  -> EX2
#   s6  example 3's `[dd = rx]` lowered without its label                                   -> EX3
#   s7  the names scan exempts bound conditions and computed labels (no refusal for them)   -> NAMES
#   s8  the closed variant leaves the user's labels visible inside the definition          -> CLOSEDB
#   s9  `0` restarts at every operand of a sequence (one definition split)                  -> ZSEQ
#   s10 under zero-in-definition the inserted definition's `0` starts at the user's start   -> ZNEST
#   s11 an argument written in the caller belongs to the macro's definition                -> ZARG
#   s12 a condition binding's own `0` taken as the using definition's (both variants alike) -> ZCBIND
#   s13 the label read after a loop taken as PCRE's carried value                           -> LOOPVAL
#   s14 the caseless set computed without IGNORECASE                                       -> CASELESS
#   s15 byte-mode members ordered by their cp1252 character instead of the byte value       -> BYTES
#   s16 a class's members enumerated descending                                           -> CLASSV
#   s17 the flat read across `|` refused                                                    -> FLATR
#   s18 `when`'s test condition resolved in the macro body (where `kind` is not visible)    -> WHEN
#   s19 a quoted owner sentence altered (in memory)                                         -> QUOTES
#   s20 one formatted line's subject altered before the document lookup                    -> DOC
#   s21 a record line altered before the record lookup                                      -> RECORD
import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
RECORD_PATH = os.path.join(W, "docs", "design", "plan_row_bodies", "COND-FAMILY.md")
SAB = set(x for x in os.environ.get("PREDSCOPE_SABOTAGE", "").split(",") if x)
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


CORE = read(os.path.join(PRED, "core.md"))
LIB = read(os.path.join(PRED, "library.md"))
DOCS = "".join(read(os.path.join(PRED, f)) for f in
               ("core.md", "core_details.md", "library.md", "library_details.md", "parked.md", "parked_details.md"))
RECORD = read(RECORD_PATH)
ws = lambda s: re.sub(r"\s+", " ", s)
RECORD_WS = ws(RECORD)
DOCS_WS = ws(DOCS)


class CompileError(Exception):
    pass


# ================================================================== the label matcher (copied from predfix61)
DIG = set("0123456789")
WORD = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
CANON = re.compile(r"0|[1-9][0-9]*")


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
    elif k in ("rep", "look", "zscope", "lscope"):
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
        mm = re.match(r"\{(\d+)(?:,(\d*))?\}", p.s[p.i:])
        lo = int(mm.group(1))
        hi = lo if mm.group(2) is None else (int(mm.group(2)) if mm.group(2) else None)
        p.i += mm.end() - 1
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
        elif p.s.startswith("?Z:", p.i):
            p.i += 3
            n = ("zscope", p_alt(p))
        elif p.s.startswith("?S:", p.i):
            p.i += 3
            n = ("lscope", p_alt(p))
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
        if e == "w":
            return ("cls", frozenset(WORD))
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
    mm = re.fullmatch(r"\(0: /(.*)/\)", body)
    if mm:
        return ("zero", re.compile(mm.group(1)))
    mm = COND.fullmatch(body)
    if mm:
        return ("cond", bool(mm.group(1)), mm.group(2), mm.group(3) or "==", mm.group(5))
    raise CompileError("unknown hole " + body)


def cmp(v, op, x):
    if op == "==":
        return v == x
    if not CANON.fullmatch(v) and not sab("s4"):      # core/values/number-domain: canonical numerals only
        return False
    a, b = int(v), int(x)
    return {">=": a >= b, "<=": a <= b, "<": a < b, ">": a > b}[op]


class St:
    __slots__ = ("lab", "start")

    def __init__(self, lab, start):
        self.lab, self.start = lab, start


def reset(st, names):
    if not names:
        return st
    return St({k: v for k, v in st.lab.items() if k not in names}, st.start)


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
        alts = node[1][::-1] if sab("s1") else node[1]
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
            return k(p2, St(lab, st2.start))
        return m(node[2], s, pos, st, close)
    if t == "rep":
        _, sub, lo, hi, names = node
        branching = not (lo == 1 and hi == 1)
        st0 = reset(st, names) if branching else st

        def it(i, p, stc):
            if hi is None or i < hi:
                def after(p2, st2):
                    if p2 == p and i >= lo:
                        return None
                    return it(i + 1, p2, st2)
                r = m(sub, s, p, stc, after)
                if r is not None:
                    return r
            if i >= lo:
                return k(p, stc)
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
    if t == "zscope":            # a definition's own `0`: the match so far restarts at its start
        start = st.start if sab("s10") else pos
        return m(node[1], s, pos, St(st.lab, start), lambda p2, st2: k(p2, St(st2.lab, st.start)))
    if t == "lscope":            # a CLOSED definition: the user's labels are not visible inside it
        inner0 = dict(st.lab) if sab("s8") else {}

        def out(p2, st2):
            lab = dict(st.lab)
            lab.update(st2.lab)
            return k(p2, St(lab, st.start))
        return m(node[1], s, pos, St(inner0, st.start), out)
    raise ValueError(t)


def cond_holds(node, st):
    _, neg, name, op, val = node
    v = st.lab.get(name)
    if v is None:
        return neg
    res = cmp(v, op, val)
    return (not res) if neg else res


def mseq(items, i, s, pos, st, k):
    if i == len(items):
        return k(pos, st)
    return m(items[i], s, pos, st, lambda p2, st2: mseq(items, i + 1, s, p2, st2, k))


class Prog:
    def __init__(self, rx, conds=()):
        self.rx = rx
        self.node = p_alt(Src(rx))
        self.conds = [hole(c) for c in conds]

    def at(self, s, start, need_end=None, nonempty=False):
        def fin(p, st):
            if need_end is not None and p != need_end:
                return None
            if nonempty and p == start:
                return None
            if not all(cond_holds(c, st) for c in self.conds):
                return None
            return (start, p, st)
        return m(self.node, s, start, St({}, start), fin)

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
            le, pos = b, b
        return out


def fmt(P, whole, srch, fa):
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


# ================================================================== the lowerer (expression text -> rx text)
def split_top(text, sep):
    """Split at `sep` outside (), [], /../ and "..". """
    out, depth, i, last, in_rx, in_q = [], 0, 0, 0, False, False
    while i < len(text):
        c = text[i]
        if in_rx:
            if c == "\\":
                i += 2
                continue
            if c == "/":
                in_rx = False
        elif in_q:
            if c == '"':
                in_q = False
        elif c == "/":
            in_rx = True
        elif c == '"':
            in_q = True
        elif c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif depth == 0 and text.startswith(sep, i):
            out.append(text[last:i])
            i += len(sep)
            last = i
            continue
        i += 1
    out.append(text[last:])
    return [x.strip() for x in out]


IS_COND = re.compile(r"^(NOT )?\(\(?[\w.]+(?:, [\w.]+)*\)?\s*:")


class Val:
    """A lowered value: rx text (with the matcher's hole forms kept), its end conditions, and its CAPTURES."""

    def __init__(self, kind, text, conds=(), caps=frozenset(), labels=frozenset()):
        self.kind, self.text, self.conds, self.caps, self.labels = kind, text, tuple(conds), frozenset(caps), frozenset(labels)


class Macro:
    def __init__(self, head, body):
        self.name, params = re.fullmatch(r"([\w.]+)\((.*)\)", head).groups()
        self.params = [x.strip().split(" = ")[0] for x in params.split(",")]
        self.body = body


class Env:
    def __init__(self, binds=None, macros=None, variant=()):
        self.binds, self.macros, self.variant = dict(binds or {}), dict(macros or {}), set(variant)

    def define(self, line):
        head, body = [x.strip() for x in line.split(":=", 1)]
        if "(" in head:
            mc = Macro(head, body)
            self.macros[mc.name] = mc
        else:
            self.binds[head] = body
        return self


def lit_groups(rx):
    return set(re.findall(r"\(\?<([A-Za-z_]\w*)>", rx))


def lower(expr, env, params=None, wrap_def=False):
    """Lower an expression. `params`: the macro's parameters bound to caller-lowered Vals."""
    params = params or {}
    expr = expr.strip()
    parts = split_top(expr, " & ")
    if len(parts) > 1:
        head = lower(" & ".join(parts[:-1]), env, params)
        last = parts[-1]
        if not IS_COND.match(last):
            raise CompileError("only a trailing condition is modelled after `&`: " + last)
        return Val("rx", head.text, head.conds + (subst_cond(last, params),), head.caps, head.labels)
    alts = split_top(expr, " | ")
    if len(alts) > 1:
        vs = [lower(a, env, params) for a in alts]
        if sab("s1"):
            vs = vs[::-1]
        return Val("rx", "|".join("(?:%s)" % v.text for v in vs), sum((v.conds for v in vs), ()),
                   frozenset().union(*[v.caps for v in vs]), frozenset().union(*[v.labels for v in vs]))
    seq = split_top(expr, " SEQ ")
    if len(seq) > 1:
        vs = [lower(a, env, params) for a in seq]
        for v in vs:
            if v.conds:
                raise CompileError("a condition inside a sequence operand is not modelled")
        return Val("rx", "".join(v.text if v.kind == "cond" else "(?:%s)" % v.text for v in vs), (),
                   frozenset().union(*[v.caps for v in vs]), frozenset().union(*[v.labels for v in vs]))
    if IS_COND.match(expr):
        return Val("cond", "${%s}" % subst_cond(expr, params))
    mm = re.fullmatch(r"\[(\w+) = (.*)\]", expr)
    if mm:
        name, e = mm.groups()
        v = lower(e, env, params)
        caps = set(v.caps) | ({name} if sab("s2") else set())
        return Val("rx", "(?<%s>%s)" % (name, v.text), v.conds, caps, set(v.labels) | {name})
    if expr.startswith("/") and expr.endswith("/"):
        return lower_literal(expr[1:-1], env, params)
    if expr.startswith('"') and expr.endswith('"'):
        return Val("rx", re.escape(expr[1:-1]))
    if expr.startswith("(") and expr.endswith(")") and split_top(expr[1:-1], " SEQ ") != [expr[1:-1]]:
        return lower(expr[1:-1], env, params)
    mm = re.fullmatch(r"([\w.]+)\((.*)\)", expr)
    if mm:
        return call(mm.group(1), split_top(mm.group(2), ","), env, params)
    if expr in params:
        return params[expr]
    if expr in env.binds:
        v = lower(env.binds[expr], env)
        if wrap_def:
            v = Val(v.kind, wrap(v.text, env), v.conds, v.caps, v.labels)
        return v
    raise CompileError("an undeclared name: " + expr)


def wrap(text, env):
    if "zdef" in env.variant:
        text = "(?Z:%s)" % text
    if "closed" in env.variant:
        text = "(?S:%s)" % text
    return text


def subst_cond(text, params):
    """A condition's text with `rx.digit` written as the literal lib/rx/classes gives it."""
    if text in params:
        return params[text].text.strip("${}")
    return text.replace("rx.digit", RXDIGIT)


def call(name, args, env, params):
    if name == "any_of":                     # the record's presumed macro: an alternation of its strings
        return Val("rx", "(?:%s)" % "|".join(re.escape(a.strip().strip('"')) for a in args))
    if name == "peek":                       # library: "A condition given as A is zero width already"
        v = lower(args[0], env, params)
        if v.kind != "cond":
            raise CompileError("peek of a pattern is not modelled")
        return v
    if name == "capture":                    # lib/structural/capture: /(?<${name}>${x})/
        nm = args[0].strip().strip('"')
        v = lower(args[1], env, params)
        return Val("rx", "(?<%s>(?:%s))" % (nm, v.text), v.conds, set(v.caps) | {nm}, set(v.labels) | {nm})
    mc = env.macros.get(name)
    if mc is None:
        raise CompileError("an undeclared macro: " + name)
    bound, pos = {}, 0
    for a in args:
        a = a.strip()
        kw = re.fullmatch(r"(\w+) = (.*)", a)
        if kw:
            pname, a = kw.groups()
        else:
            pname = mc.params[pos]
            pos += 1
        if re.fullmatch(r"\d+", a):
            bound[pname] = Val("num", a)
        else:
            bound[pname] = lower(a, env, params, wrap_def=False)      # the argument: lowered in the CALLER
            if "argdef" in env.variant or sab("s11"):
                bound[pname] = Val(bound[pname].kind, "(?Z:%s)" % bound[pname].text, bound[pname].conds,
                                   bound[pname].caps, bound[pname].labels) if bound[pname].kind == "rx" else bound[pname]
    v = lower(mc.body, env, bound)
    if "macrodef" in env.variant:
        v = Val(v.kind, "(?Z:%s)" % v.text, v.conds, v.caps, v.labels)
    return v


def lower_literal(rx, env, params):
    caps, labels, conds = set(lit_groups(rx)), set(lit_groups(rx)), []
    out, i = [], 0
    while i < len(rx):
        if rx.startswith("${", i):
            j = rx.index("}", i)
            while rx.count("(", i, j) != rx.count(")", i, j) or rx.count("[", i, j) != rx.count("]", i, j):
                j = rx.index("}", j + 1)
            body = rx[i + 2:j].strip()
            i = j + 1
            if body in params:
                v = params[body]
                if v.kind == "num":
                    out.append(v.text)
                elif v.kind == "cond":
                    out.append(v.text)
                else:
                    out.append("(?:%s)" % v.text)
                caps |= v.caps
                labels |= v.labels
                conds += v.conds
            elif re.fullmatch(r"[A-Za-z_][\w.]*", body) and (body in env.binds):
                v = lower(body, env, params, wrap_def=True)
                if v.kind == "cond":
                    out.append(wrap(v.text, env) if "cbind_own" in env.variant else v.text)
                else:
                    out.append("(?:%s)" % v.text)
                caps |= v.caps
                labels |= v.labels
            elif body.startswith("["):
                v = lower(body, env, params)
                out.append("(?:%s)" % v.text)
                caps |= v.caps
                labels |= v.labels
                conds += v.conds
            else:
                out.append("${%s}" % subst_cond(body, params))
            continue
        out.append(rx[i])
        i += 1
    return Val("rx", "".join(out), conds, caps, labels)


def prog(expr, env):
    v = lower(expr, env)
    return Prog(v.text, v.conds), v


def caller_captures(v):
    caps = v.caps if sab("s3") else {c for c in v.caps if not c.startswith("_")}
    return sorted(caps)


# ---------------------------------------------------------------- the library bodies, READ from library.md
def lib_body(pattern):
    mm = re.search(pattern, LIB)
    assert mm, pattern
    return mm.group(1)


RXDIGIT = lib_body(r"`rx\.digit := (/\\d/)`")
REPEAT_MIN = lib_body(r"`(repeat\(x, min\) := /\(\?:\$\{x\}\)\{\$\{min\},\}/)`")
RXDIGITS = lib_body(r"`(rx\.digits := rx\.repeat\(rx\.digit, min = 1\))`")


def base_env(variant=()):
    e = Env(variant=variant)
    e.define("rx.digit := " + RXDIGIT)
    e.define("rx." + REPEAT_MIN)
    e.define(RXDIGITS)
    e.define("rx.word_char := /\\w/")         # lib/rx/classes: `rx.word_char` is `\w`
    return e


LINES = []


def doc_line(L, tag):
    LINES.append((tag, L))
    return L


# ================================================================== the checks
print("== the library bodies read from library.md: %s ; %s ; %s" % (RXDIGIT, REPEAT_MIN, RXDIGITS))

# ---------------------------------------------------------------- CONTROL: the matcher + lowerer against python `re`
print("== CONTROL: lowered programs against python `re` on independent hand regexes")
POP = pop("019x", 5)
ex1 = base_env().define("A := [d = rx.digits]").define("B(rx) := /${rx}xx/")
P1, V1 = prog("B(A) & (d: <100)", ex1)
d1 = ndiff(answers_p(P1, POP), answers_re(r"(?:[1-9]\d?|0)xx", POP))
P0, _ = prog("rx.digits", base_env())
d0 = ndiff(answers_p(P0, POP), answers_re(r"\d+", POP))
ctl2 = Prog("(?:a|ab)(?<c>\\d)?")
d2 = ndiff(answers_p(ctl2, pop("ab3", 4)), answers_re(r"(?:a|ab)(\d)?", pop("ab3", 4)))
check("CONTROL", d1 == (0, 0, 0) and d0 == (0, 0, 0) and d2 == (0, 0, 0),
      "example 1 against `(?:[1-9]\\d?|0)xx` %s, `rx.digits` against `\\d+` %s of %d texts over `019x`; the ordered alternation %s"
      % (d1, d0, len(POP), d2))

# ---------------------------------------------------------------- PREMISE: the manager's two folds of today, re-run
print("== PREMISE: the printed lines of the manager's folds of today (flat-read-outside, class-value)")
fe = base_env().define("pair := [b = /(?<x>\\d)/] | [c = /a(?<x>\\d)/]").define(
    'date := [y = /(?<v>\\d)/] SEQ "-" SEQ [m = /(?<v>\\d)/]')
FA, _ = prog("pair & (x: <5)", fe)
LF1 = doc_line(("a compile error (the flat read refused)" if sab("s17") else fmt(FA, ["3", "a3", "a7"], "a7 a3", "3 a7 a4")) +
               " (`pair & (x: <5)`, pair := `[b = /(?<x>\\d)/] | [c = /a(?<x>\\d)/]`)", "flat-read-outside")
FD_, _ = prog("date & (v: <5)", fe)
LF2 = doc_line(fmt(FD_, ["7-3", "3-7"], "3-7 7-3", "7-3 3-7 1-2") +
               ' (`date & (v: <5)`, date := `[y = /(?<v>\\d)/] SEQ "-" SEQ [m = /(?<v>\\d)/]`)', "flat-read-outside")
check("FLATR", LF1.startswith("WHOLE `3` HOLDS, `a3` HOLDS, `a7` FAILS") and LF2.startswith("WHOLE `7-3` HOLDS, `3-7` FAILS"),
      LF1 + " | " + LF2)


def members(cls_rx, flags=0, top=0x110000):
    c = re.compile(cls_rx, flags)
    out = [chr(x) for x in range(top) if c.fullmatch(chr(x))]
    return out[::-1] if sab("s16") else out


hexm = "".join(members(r"[\dA-Fa-f]", re.ASCII))
acb = members(r"[a-cB]")
digs = members(r"\d", re.ASCII)
cv_ok = (hexm == "0123456789ABCDEFabcdef" and hexm.index("A") + 1 == 11 and hexm.index("a") + 1 == 17
         and acb == ["B", "a", "b", "c"] and "".join(digs) == "0123456789")
cv_doc = all(x in LIB for x in ("`enumerate(/[\\dA-Fa-f]/)` is `0123456789ABCDEFabcdef`, so `A` is 11 and `a` is 17",
                                "`[a-cB]` gives `B`, `a`,"))
check("CLASSV", cv_ok and cv_doc, "`[\\dA-Fa-f]` %s (A %d, a %d) ; `[a-cB]` %s ; `\\d` %s ; the class-value lines in library.md: %s"
      % (hexm, hexm.index("A") + 1 if "A" in hexm else -1, hexm.index("a") + 1 if "a" in hexm else -1, acb, "".join(digs), cv_doc))

# ---------------------------------------------------------------- CAPT: pure-label (a) and the `_` labels
print("== CAPT: what the caller gets (captures) against what the program reads (labels)")
capt_cases = [
    ("[d = rx.digits] & (d: <100)", base_env(), [], ["d"]),
    ('capture("d", /\\d+/)', base_env(), ["d"], ["d"]),
    ('pub', base_env().define("A := /(?<h>\\d)/").define('pub := [a = A] SEQ "!"'), ["h"], ["a", "h"]),
    ("year", base_env().define("year := /(?<_v>\\d{4})/ & (_v: >= 2000)"), [], ["_v"]),
    ("B(A) & (d: <100)", ex1, [], ["d"]),
    ("months", base_env().define("months := [mname = /Jan/ | /Feb/]"), [], ["mname"]),
]
cbad = []
for expr, env, want_caps, want_labels in capt_cases:
    _, v = prog(expr, env)
    got = (caller_captures(v), sorted(v.labels))
    print("   %-32s captures %s ; labels %s" % (expr, got[0], got[1]))
    if got != (want_caps, want_labels):
        cbad.append(expr)
re_caps = sorted(re.compile(lower('capture("d", /\\d+/)', base_env()).text.replace("(?<", "(?P<")).groupindex)
check("CAPT", not cbad and re_caps == ["d"],
      "every case as pure-label (a) and the `_` statement have it: %s ; python `re` groups of `capture(\"d\", /\\d+/)`: %s"
      % (not cbad, re_caps))

# ---------------------------------------------------------------- the owner's three examples
print("== the owner's three examples (pure-label entry), lowered from their text")
L_EX1 = doc_line(fmt(P1, ["42xx", "100xx", "042xx"], "x100xx 42xx", "100xx 42xx 7xx 300xx") +
                 " (`C := B(A) & (d: <100)`, A := `[d = digits]`, B(rx) := `/${rx}xx/`)", "nested-scope")
rec_ex1 = "WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 / FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17]"
check("EX1", L_EX1.startswith(rec_ex1) and ws(rec_ex1) in RECORD_WS, L_EX1)


def names_scan(defn, env_names):
    """(written, named, illegal) for one definition `NAME[(params)] := BODY` under the manager's reading (a)."""
    head, body = [x.strip() for x in defn.split(":=", 1)]
    pm = re.fullmatch(r"[\w.]+\((.*)\)", head)
    params = [x.strip().split(" = ")[0] for x in pm.group(1).split(",")] if pm else []
    written = set(re.findall(r"\(\?<([A-Za-z_]\w*)>", body)) | set(re.findall(r"\[([A-Za-z_]\w*) =", body))
    for nm in re.findall(r"\b([A-Za-z_][\w.]*)\b", re.sub(r"/[^/]*/|\"[^\"]*\"", " ", body)):
        if nm in env_names and nm not in params:
            written |= env_names[nm]                  # a part it writes in: its public labels
    named = set(re.findall(r"\((?:\()?([A-Za-z_]\w*)(?:, ([A-Za-z_]\w*))?\)?(?: = [^:]+)?: ", body))
    named = {x for pair in named for x in pair if x}
    named |= set(re.findall(r"\$([A-Za-z_]\w*)", body))
    named -= {"0"}
    return written, named, sorted(named - written)


# example 2: B(rx) := /${rx}xx/ & (d: <100)
w2, n2, ill2 = names_scan("B(rx) := /${rx}xx/ & (d: <100)", {})
ex2 = base_env().define("A := [d = rx.digits]").define("B(rx) := /${rx}xx/ & (d: <100)")
P2, _ = prog("B(A)", ex2)
L_EX2c = fmt(P2, ["42xx", "100xx", "042xx"], "x100xx 42xx", "100xx 42xx 7xx 300xx")
refused2 = bool(ill2) and not sab("s5")
check("EX2", refused2 and ill2 == ["d"] and L_EX2c.startswith(rec_ex1),
      "the body names %s, writes %s: refused (his \"is incorrect\"); composed it would equal example 1: %s" % (sorted(n2), sorted(w2), L_EX2c))

# example 3: B(rx) := /${[dd = rx]}xx/ & (dd: <100)
w3, n3, ill3 = names_scan("B(rx) := /${[dd = rx]}xx/ & (dd: <100)", {})
ex3 = base_env().define("A := [d = rx.digits]").define("B(rx) := /${[dd = rx]}xx/ & (dd: <100)")
if sab("s6"):
    ex3 = base_env().define("A := [d = rx.digits]").define("B(rx) := /${rx}xx/ & (dd: <100)")
P3, V3 = prog("B(A)", ex3)
L_EX3 = doc_line(fmt(P3, ["42xx", "100xx", "042xx"], "x100xx 42xx", "100xx 42xx 7xx 300xx") +
                 " (`B(A)`, B(rx) := `/${[dd = rx]}xx/ & (dd: <100)`)", "nested-scope")
check("EX3", not ill3 and L_EX3.startswith(rec_ex1) and sorted(V3.labels) == ["d", "dd"] and caller_captures(V3) == [],
      "the body names %s and writes %s: legal ; labels %s, captures %s ; %s" % (sorted(n3), sorted(w3), sorted(V3.labels), caller_captures(V3), L_EX3))

# ---------------------------------------------------------------- NAMES: the manager's reading (a) against the documents' examples
print("== NAMES: the manager's reading (a) of the three examples, against every definition the documents print")
EXP = {"isodate": {"year", "month", "day"}, "chars": {"ch"}, "A": {"h"}, "months": {"mname"}}
DEFS = [  # (definition text as printed, its piece, its kind)
    ("c := `NOT (h: /\\d/) | (n: >= $h)`", "core/conditions/pass-start-read", "condition"),
    ("sum := `$a + $b`", "core/values/computed-labels", "computed label"),
    ('n := `count((d: "7"))`', "lib/counting/count", "computed label"),
    ("`nchars := count((ch: /(?s:.)/))`", "lib/modifiers/length", "computed label"),
    ("`mnum := $mname.index`", "lib/modifiers/month-numbered", "computed label"),
    ("late := `/(?<h>\\d):(?<m>\\d)/ & ((h, m): >= (5, 3))`", "core/diagnostics/looped-compare", "rx"),
    ("year := `/(?<_v>\\d{4})/ & (_v: >= 2000)`", "core/labels/export", "rx"),
    ("B := `/${(c: >= 5)}(?<c>\\d)/`", "core/holes/bare-condition/labels", "rx"),
    ("inner := `/x${(h: <5)}/`", "core/holes/bare-condition/nested-scope", "rx"),
    ("inner := `/x${$h}/`", "core/holes/bare-condition/nested-scope", "rx"),
    ("inner := `/x${(0: /\\dx/)}/`", "core/holes/bare-condition/nested-scope", "rx"),
    ("`date_in(years) := isodate & (year: years)`", "core/operators/bindings", "rx"),
    ("`when(test, then, else = //) := (test SEQ then) | (NOT peek(test) SEQ else)`", "lib/control/when", "rx"),
    ("`occurrences(x, min = 0)` is the lazy-gap loop `/(?:(?s:.*?)(?<hit>${x})){${min},}(?s:.*)/`", "lib/search/occurrences", "rx"),
    ("`length(S) := chars & (nchars: S)`", "lib/modifiers/length", "rx"),
    ("`capture(name, x) := /(?<${name}>${x})/`", "lib/structural/capture", "rx"),
    ("`list_of(X, sep = S)` is the separated list `/(?:${X}${S})*${X}/`", "lib/records/list-of", "rx"),
]
nbad, refused = [], []
for text, piece, kind in DEFS:
    present = text in DOCS
    t = text.replace("`", "")
    t = re.sub(r"^(\S+\(.*?\)) is the [\w -]+ ", r"\1 := ", t)
    w, n, ill = names_scan(t, EXP)
    if sab("s7") and kind != "rx":
        ill = []
    if "length(S)" in t:
        ill = [x for x in ill if x != "nchars"]       # `nchars` is a binding it writes in (a computed label)
    print("   %-5s %-15s %-40s names %-10s writes %-18s %s" % ("" if present else "ABSENT", kind, piece, sorted(n), sorted(w),
                                                        "REFUSED " + str(ill) if ill else "legal"))
    if not present:
        nbad.append(text)
    if ill:
        refused.append((piece, kind, ill))
ref_kinds = sorted(set(k for _, k, _ in refused))
ref_rx = [p for p, k, _ in refused if k == "rx"]
check("NAMES", not nbad and len(refused) == 7 and ref_rx == ["core/holes/bare-condition/nested-scope"] * 2,
      "%d definitions, all present: %s ; refused by the rule as stated: %d (%s), the rx definitions among them only nested-scope's two lines"
      % (len(DEFS), not nbad, len(refused), ref_kinds))

# ---------------------------------------------------------------- CLOSEDB: the Composed line (B holds c, reads A's)
print("== CLOSEDB: bare-condition/labels' Composed line, composed against a definition closed to its user's labels")
cb = base_env().define("A := /(?<c>\\d)/").define("B := /${(c: >= 5)}(?<c>\\d)/")
PB, _ = prog("A SEQ B", cb)
LB = fmt(PB, ["73", "37"], "37 73", "73 37 51") + " (`A SEQ B`, A := `/(?<c>\\d)/`, B := `/${(c: >= 5)}(?<c>\\d)/`)"
cbc = base_env(("closed",)).define("A := /(?<c>\\d)/").define("B := /${(c: >= 5)}(?<c>\\d)/")
cbc.binds["B"] = "/${(c: >= 5)}(?<c>\\d)/"
PBc = Prog("(?:(?<c>\\d))(?:%s)" % wrap(lower("B", cbc).text, cbc))
LBc = fmt(PBc, ["73", "37"], "37 73", "73 37 51")
check("CLOSEDB", ("Composed: " + LB) in CORE and "HOLDS" not in LBc and LBc.endswith("[]"),
      "composed (the documents): %s | closed: %s" % (LB, LBc))

# ---------------------------------------------------------------- zero-in-definition
print("== zero-in-definition: `0` is the match so far of the definition it is written in")
zs = Prog("(?:\\d)${(0: /7/)}(?:\\d)" if not sab("s9") else "(?:\\d)(?Z:${(0: /7/)})(?:\\d)")
LZS = doc_line(fmt(zs, ["73", "37"], "373", "73 77 37") + " (`/\\d/ SEQ (0: /7/) SEQ /\\d/`)", "match-so-far")
check("ZSEQ", LZS.startswith("WHOLE `73` HOLDS, `37` FAILS / SEARCHED `373` `73`@1 / FIND-ALL `73 77 37` [`73`@0, `77`@3]"), LZS)

zb = base_env(("zdef",)).define("inner := /x${(0: /\\dx/)}/")
PZa, _ = prog("/(?<h>\\d)${inner}/", zb)
PZb, _ = prog("/(?<h>\\d)${inner}/", base_env().define("inner := /x${(0: /\\dx/)}/"))
LZa = doc_line(fmt(PZa, ["3x", "7x"], "a3x", "3x 7x") + " (`/(?<h>\\d)${inner}/`, inner := `/x${(0: /\\dx/)}/`)", "nested-scope")
LZb = fmt(PZb, ["3x", "7x"], "a3x", "3x 7x")
check("ZNEST", LZa.startswith("WHOLE `3x` FAILS, `7x` FAILS / SEARCHED `a3x` FAILS / FIND-ALL `3x 7x` []")
      and LZb == "WHOLE `3x` HOLDS, `7x` HOLDS / SEARCHED `a3x` `3x`@1 / FIND-ALL `3x 7x` [`3x`@0, `7x`@3]",
      "the ruled (a), the inner definition's own `0`: %s | the rejected (b): %s" % (LZa, LZb))

# reading (a): an argument written in the caller belongs to the caller's definition
za_env = base_env(("macrodef",)).define("B(rx) := /${rx}xx/")
PZc, _ = prog("/\\d/ SEQ B((0: /\\d/))", base_env().define("B(rx) := /${rx}xx/"))
if sab("s11"):
    PZc = Prog("(?:\\d)(?:(?Z:${(0: /\\d/)})xx)")
PZm = Prog("(?:\\d)(?:(?Z:${(0: /\\d/)}xx))")
LZc = doc_line(fmt(PZc, ["5xx", "xx"], "a5xx", "5xx 55xx") + " (`/\\d/ SEQ B((0: /\\d/))`, B(rx) := `/${rx}xx/`)", "match-so-far")
LZm = fmt(PZm, ["5xx", "xx"], "a5xx", "5xx 55xx")
check("ZARG", "HOLDS" in LZc and "HOLDS" not in LZm and LZm.endswith("[]"),
      "the argument in the caller's definition (the reading): %s | in the macro's: %s" % (LZc, LZm))

# reading (b): a condition bound alone
zc_use = base_env().define("c := (0: rx.digit)")
zc_own = base_env(("zdef", "cbind_own")).define("c := (0: rx.digit)")
PCu, _ = prog("/\\d${c}x/", zc_use)
PCo, _ = prog("/\\d${c}x/", zc_own if not sab("s12") else zc_use)
LCu = doc_line(fmt(PCu, ["7x", "77x"], "a7x", "7x 12x 8x") + " (`/\\d${c}x/`, c := `(0: rx.digit)`)", "bare-condition")
LCo = fmt(PCo, ["7x", "77x"], "a7x", "7x 12x 8x")
check("ZCBIND", LCu.startswith("WHOLE `7x` HOLDS, `77x` FAILS / SEARCHED `a7x` `7x`@1 / FIND-ALL `7x 12x 8x` [`7x`@0, `2x`@4, `8x`@7]")
      and LCo == "WHOLE `7x` FAILS, `77x` FAILS / SEARCHED `a7x` FAILS / FIND-ALL `7x 12x 8x` []",
      "as if written in place, the using definition's `0`: %s | the binding's own `0` (empty at its point): %s" % (LCu, LCo))
L_ZCo = LCo

# ---------------------------------------------------------------- LOOPVAL: a captured label a loop sets
print("== LOOPVAL: the caller's value for a group in rx text set in a loop: the label against PCRE's capture")
LV = Prog("(?:(?<h>\\d)?;)+")
rv = re.compile(r"(?:(?P<h>\d)?;)+")


def lv(t, at=0):
    r = LV.at(t, at)
    lab = r[2].lab.get("h") if r else None
    if sab("s13"):
        lab = rv.match(t, at).group("h")
    return lab, rv.match(t, at).group("h")


rows = [("3;;", 0), ("3;", 0), ("x3;;", 1), ("7;", 4)]
vals = [lv(t if t != "7;" else "3;; 7;", a) for t, a in rows]
LLV = fmt(LV, ["3;;", "3;"], "x3;;", "3;; 7;")
check("LOOPVAL", vals[0] == (None, "3") and vals[1] == ("3", "3") and vals[3] == ("7", "7"),
      "%s ; `3;;`: label %s, python `re` capture %s ; `3;`: %s ; `7;`@4: %s" % (LLV, vals[0][0], vals[0][1], vals[1], vals[3]))
L_LV = LLV

# ---------------------------------------------------------------- class-value readings
print("== the class-value readings: a caseless single character; byte mode")
ck = members(r"k", 0 if sab("s14") else re.IGNORECASE)
check("CASELESS", [hex(ord(c)) for c in ck] == ["0x4b", "0x6b", "0x212a"],
      "python `re` (str mode), `(?i)k` over every codepoint, ascending: %s" % [hex(ord(c)) for c in ck])
bc = re.compile(rb"[A-C\xe9\x80]")
bmem = [bytes([b]) for b in range(256) if bc.fullmatch(bytes([b]))]
order = sorted(bmem, key=(lambda b: ord(b.decode("cp1252"))) if sab("s15") else (lambda b: b[0]))
by_cp = sorted(bmem, key=lambda b: ord(b.decode("latin-1")))
check("BYTES", order == by_cp and [b[0] for b in order] == [0x41, 0x42, 0x43, 0x80, 0xe9],
      "byte mode `[A-C\\xe9\\x80]`: by byte value %s ; equals the Latin-1 codepoint order: %s"
      % ([hex(b[0]) for b in order], order == by_cp))

# ---------------------------------------------------------------- WHEN: a condition passed as an argument
print("== WHEN: condition-argument's run, `when`'s body lowered from library.md, the test resolved in the caller")
WHEN_BODY = lib_body(r"`(when\(test, then, else = //\) := \(test SEQ then\) \| \(NOT peek\(test\) SEQ else\))`")
we = base_env().define("digits := rx.digits").define("word := rx.repeat(rx.word_char, min = 1)")
we.define(WHEN_BODY.replace("else = //", "else"))
we.macros["when"].body = we.macros["when"].body.replace("NOT peek(test)", "NOTPEEK(test)")
_lower0 = lower


def lower_when(expr, env, params=None, wrap_def=False):
    params = params or {}
    mm = re.fullmatch(r"NOTPEEK\((\w+)\)", expr.strip())
    if mm:
        v = params[mm.group(1)]
        if v.kind != "cond":
            raise CompileError("NOT peek of a pattern is not modelled")
        return Val("cond", v.text.replace("${", "${NOT ", 1))
    return _lower0(expr, env, params, wrap_def)


lower = lower_when
try:
    if sab("s18"):
        raise CompileError("`kind` is not visible in `when`'s body")
    PW, _ = prog('[kind = any_of("n", "w")] SEQ ":" SEQ when((kind: "n"), digits, else = word)', we)
    LW = fmt(PW, ["n:42", "n:ab", "w:ab", "w:42"], "n:ab w:ab", "n:42 n:ab w:ab n:7x")
except CompileError as e:
    LW = "a compile error: %s" % e
lower = _lower0
rec_w = "WHOLE `n:42` HOLDS, `n:ab` FAILS, `w:ab` HOLDS, `w:42` HOLDS / SEARCHED `n:ab w:ab` `w:ab`@5 / FIND-ALL `n:42 n:ab w:ab n:7x` [`n:42`@0, `w:ab`@10, `n:7`@15]"
w_names = names_scan(WHEN_BODY, {})
check("WHEN", LW == rec_w and ws(rec_w) in RECORD_WS and w_names[1] == set(),
      "%s ; `when`'s body names %s (the test's `kind` is the caller's)" % (LW, sorted(w_names[1])))

# ---------------------------------------------------------------- RECORD: the record lines this lane relies on
rec_lines = [
    "`[d = digits] & (d: <100)`: WHOLE `42` HOLDS, `100` FAILS, `042` FAILS / SEARCHED `x100 42` `10`@1",
    "Example 3 with `B(A)` gives the same answers (dd and d are one text).",
    "(a) WHOLE `3x` FAILS / SEARCHED `a3x` FAILS / FIND-ALL `3x 7x` []",
]
if sab("s21"):
    rec_lines[1] = rec_lines[1].replace("same", "other")
P42, _ = prog("[d = rx.digits] & (d: <100)", base_env())
L42 = fmt(P42, ["42", "100", "042"], "x100 42", "100 42 7")
rmiss = [x for x in rec_lines if ws(x) not in RECORD_WS]
check("RECORD", not rmiss and L42 == "WHOLE `42` HOLDS, `100` FAILS, `042` FAILS / SEARCHED `x100 42` `10`@1 / FIND-ALL `100 42 7` [`10`@0, `0`@2, `42`@4, `7`@7]",
      "missing from the record: %s ; the pure-label run re-run: %s" % (rmiss, L42))

# ---------------------------------------------------------------- QUOTES: the owner's words this lane quotes
QUOTES = [
    "i agree that captures are explicitly written either in literal form or using a macro like capture().",
    "what i don't know is precisely what that looks like.",
    "two methods are to specify it like a wrapper like [ d = capture(digits) ] etc or specify it afterthefact like [ d = digits ] & capture(d) or something. no spelling suggested.",
    "isodate and all the other libraries don't want to presume everyone is interested in every label being a capture.",
    "but then, someone might later want the year of an isodate as a capture. so an add on component that converted a label into a capture is needed.",
    "1. purely predicate labels and 2. cannot become exported captures (although they might be internal captures)",
    "C can see d as a flat look into A. C cannot see rx as its a binding variable not a label.",
    "is incorrect.",
    "would be correct",
    "zero-in-definition: a",
    "setting labels is just the label using the group-label-not-capture syntax",
    "ascending codepoints everywhere",
    "they would be used in your examples to define a binding level label like the quote character in a string.",
]
if sab("s19"):
    QUOTES[0] = QUOTES[0].replace("explicitly", "always")
qmiss = [q for q in QUOTES if ws(q) not in RECORD_WS]
qdoc = [q for q in QUOTES if ws(q) not in DOCS_WS]
check("QUOTES", not qmiss and not qdoc, "%d quoted sentences; missing from the record: %s ; not quoted in the documents: %s"
      % (len(QUOTES), qmiss, qdoc))

# ---------------------------------------------------------------- DOC: every formatted line occurs in the documents
print("== DOC: every formatted line occurs verbatim in the documents")
doc_extra = [("nested-scope", "Example 2, the composed reading he refused: " + L_EX2c),
             ("bare-condition", "the binding's own `0`: " + L_ZCo),
             ("labels-vs-captures", L_LV)]
missing = []
for tag, L in LINES + doc_extra:
    probe = L
    if sab("s20") and L is LINES[0][1]:
        probe = L.replace("WHOLE `3`", "WHOLE `4`")
    ok = probe in DOCS
    print("   [%s] %s%s" % (tag, L, "" if ok else "   <-- MISSING"))
    if not ok:
        missing.append(tag)
check("DOC", not missing, "%d lines; missing: %s" % (len(LINES) + len(doc_extra), missing))

print("predscope_model: %d checks, %d failed%s" % (len(CHECKS), len(FAILED), (" (" + ", ".join(FAILED) + ")") if FAILED else ""))
sys.exit(1 if FAILED else 0)
