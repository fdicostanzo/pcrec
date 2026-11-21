#!/usr/bin/env python3
# Lane predarr (2026-11-21): the evidence for folding the owner's rulings array-vs-passes (a) and joint-in-some
# (agree) into the predicate documents, and for testing the manager's readings of both entries. DESIGN EVIDENCE
# ONLY; rules nothing. STANDALONE (python3 `re`).
#
# METHOD. Every program is LOWERED MECHANICALLY from its text as the documents and the record print it, by a small
# lowerer (`/rx/` with `${name}` holes, `"s"`, a bound name, `[x = E]`, `E | F`, `(E)+`, `E & C` with C a condition,
# placed at E's end as a zero-width test, as core/filters/and and core/conditions/in-sequence have it; the library
# bodies `hits(r)`, `chars`, `nchars` and `anything` READ from library.md), into the text of a backtracking label
# matcher (lane predfix61's, copied: a group's close sets its name, a branching resets the labels inside it, a
# condition reads the labels as they stand, an unset label fails a test and NOT of it holds; PCRE's order of paths;
# added here: lazy quantifiers, the atomic group, `\A` `\z`, `(?s:..)`, `\s` `\S`, a joint condition). The matcher
# keeps, per path, a LOG of every setting and of every pass of every loop. A group question (`some`, `count`,
# `occurs.none`, the index `h[k]`) is an END TEST on the path: when it fails the matcher goes on to the next path.
# Its reading is chosen by a MODE:
#   settings  the ruling (array-vs-passes (a)): the array of a name's settings, every setting in order (from the
#             log), the one outside a loop included; a record of several plain entries is the product of its
#             entries, each a group question over its own array (the manager's reading (a)); a joint entry inside a
#             group question is REFUSED (joint-in-some);
#   passes    the rejected candidate (b): the passes of the outermost loop holding the group, each pass judged with
#             the labels it left (two-valued: an unset label fails, NOT of it holds);
#   byindex   a joint entry pairing the two arrays by index (joint-in-some (a), not adopted);
#   byitem    a joint entry judged on each pass's own labels (joint-in-some (b), not adopted; the reference for
#             "same item").
# Every three-mode line printed for the documents must occur VERBATIM in them, the owner questions' lines in the
# report (DOC). Controls that do not share the
# matcher or the log: python `re` on independent hand regexes (CONTROL, RECORD, IDIOM, HITS), python `re`'s
# finditer over the matched text for the arrays (ARRAYS), the record's printed lines and the owner's quoted words
# (RECLINES, QUOTES).
#
# Run (W = the worktree; any cwd):  timeout 110 python3 -I -B W/docs/dev/lanes/predarr_evidence/predarr_model.py
# PREDARR_SABOTAGE=sN (one at a time): a deliberately wrong rule or fact; its target check must FAIL.
#   s1  the matcher tries alternatives last first                                         -> CONTROL
#   s2  the array keeps an empty slot for a pass that did not set the name               -> ARRAYS
#   s3  a reset deletes the name's earlier settings from the array                       -> OUTSIDE
#   s4  the array drops its first setting                                                -> AVP
#   s5  a record of two entries in a group question pairs its arrays by index            -> RECORD
#   s6  by-index pairing aligns the two arrays from their ends                           -> JOINT
#   s7  a joint entry inside a group question is not refused                             -> REFUSE
#   s8  a part label's condition is placed at the program's end, not at the part's end  -> IDIOM
#   s9  `some` on an empty array holds                                                   -> EMPTY
#   s10 `occurs.none(c)` computed as "no setting fails c"                                -> TRUTH
#   s11 the every-pass form judged over the passes, not the settings                     -> EVERYPASS
#   s12 the settings reading keeps only the last setting                                 -> CHANGED
#   s13 the atomic group is matched as a plain group (re-entered)                        -> HITS
#   s14 a record line altered before the record lookup                                   -> RECLINES
#   s15 a quoted owner sentence altered (in memory)                                      -> QUOTES
#   s16 one formatted line's subject altered before the document lookup                  -> DOC
#   s17 a count of a record of several entries computed (no refusal) under the ruling    -> QUESTIONS
import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
RECORD_PATH = os.path.join(W, "docs", "design", "plan_row_bodies", "COND-FAMILY.md")
SAB = set(x for x in os.environ.get("PREDARR_SABOTAGE", "").split(",") if x)
FAILED, CHECKS = [], []
sys.setrecursionlimit(50000)


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


LIB = read(os.path.join(PRED, "library.md"))
DOCS = "".join(read(os.path.join(PRED, f)) for f in
               ("core.md", "core_details.md", "library.md", "library_details.md", "parked.md", "parked_details.md"))
RECORD = read(RECORD_PATH)
RECORD_WS = ws(RECORD)


class CompileError(Exception):
    pass


# ================================================================== the label matcher (predfix61's, extended)
DIG = frozenset("0123456789")
WORD = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
SPACE = frozenset(" \t\n\r\f\v")
ANY = "ANY"
CANON = re.compile(r"0|[1-9][0-9]*")


class Src:
    def __init__(self, s):
        self.s, self.i, self.dotall = s, 0, False

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
    mem, has_s, has_S = set(), False, False
    while p.peek() != "]":
        a = p.take()
        if a == "\\":
            e = p.take()
            if e == "d":
                mem |= DIG
            elif e == "s":
                has_s = True
                mem |= SPACE
            elif e == "S":
                has_S = True
            else:
                mem.add(e)
            continue
        if p.peek() == "-" and p.peek(1) != "]":
            p.take()
            b = p.take()
            mem |= set(chr(x) for x in range(ord(a), ord(b) + 1))
        else:
            mem.add(a)
    p.take()
    if has_S and not has_s:
        raise CompileError("a class with \\S alone is not modelled")
    return ("cls", ANY if has_S else frozenset(mem))


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
        elif p.s.startswith("?s:", p.i):
            p.i += 3
            old, p.dotall = p.dotall, True
            n = p_alt(p)
            p.dotall = old
        elif p.s.startswith("?>", p.i):
            p.i += 2
            n = ("seq", [p_alt(p)]) if sab("s13") else ("atomic", p_alt(p))
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
        return ("lit", e)
    if c == "[":
        return p_class(p)
    if c == ".":
        return ("cls", ANY) if p.dotall else ("dot",)
    return ("lit", c)


# ---- conditions: entries `name: S` (S a string, a comparison, an rx, a bound set) and the joint entry
ENTRY = re.compile(r'(\w+): ?(.*)$')


def parse_value(v):
    v = v.strip()
    mm = re.fullmatch(r'"([^"]*)"', v)
    if mm:
        return ("eq", mm.group(1))
    mm = re.fullmatch(r"(>=|<=|<|>|==) ?(\d+)", v)
    if mm:
        return ("cmp", mm.group(1), mm.group(2))
    if v.startswith("/") and v.endswith("/"):
        return ("rx", p_alt(Src(v[1:-1])))
    if v in BINDS:                                  # a bound set (`anything`)
        return ("rx", p_alt(Src(lower(v)[0].strip("/"))))
    raise CompileError("unknown value " + v)


def parse_cond(text):
    """`(e1, e2)`, `NOT (e)`, `((h, m): ("5", "3"))` -> ("cond", neg, entries, joint)"""
    text = text.strip()
    neg = text.startswith("NOT ")
    if neg:
        text = text[4:].strip()
    assert text.startswith("(") and text.endswith(")"), text
    inner = text[1:-1].strip()
    mm = re.fullmatch(r"\((\w+(?:, \w+)+)\): \((.*)\)", inner)
    if mm:
        names = [x.strip() for x in mm.group(1).split(",")]
        vals = [parse_value(x) for x in split_top(mm.group(2), ",")]
        return ("cond", neg, [(tuple(names), tuple(vals))], True)
    entries = []
    for e in split_top(inner, ","):
        em = ENTRY.fullmatch(e.strip())
        entries.append((em.group(1), parse_value(em.group(2))))
    return ("cond", neg, entries, False)


def hole(body):
    return parse_cond(body)


def val_ok(v, val):
    if v is None:
        return False
    if val[0] == "eq":
        return v == val[1]
    if val[0] == "cmp":
        if not CANON.fullmatch(v):
            return False
        a, b = int(v), int(val[2])
        return {">=": a >= b, "<=": a <= b, "<": a < b, ">": a > b, "==": a == b}[val[1]]
    if val[0] == "rx":
        return m(val[1], v, 0, St({}, (), 0), lambda p, st: True if p == len(v) else None) is not None
    raise ValueError(val)


def cond_on_labels(node, lab):
    """A condition on one set of labels (a place in a path, or one pass): two-valued, unset fails."""
    _, neg, entries, joint = node
    if joint:
        names, vals = entries[0]
        res = all(val_ok(lab.get(n), v) for n, v in zip(names, vals))
    else:
        res = all(val_ok(lab.get(n), v) for n, v in entries)
    return (not res) if neg else res


class St:
    __slots__ = ("lab", "log", "start")

    def __init__(self, lab, log, start):
        self.lab, self.log, self.start = lab, log, start


def reset(st, names):
    if not names:
        return st
    lab = {k: v for k, v in st.lab.items() if k not in names}
    log = st.log
    if sab("s3"):
        log = tuple(e for e in log if not (e[0] == "set" and e[1] in names))
    return St(lab, log + (("reset", tuple(sorted(names))),), st.start)


def m(node, s, pos, st, k):
    t = node[0]
    if t == "lit":
        return k(pos + 1, st) if pos < len(s) and s[pos] == node[1] else None
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
            return k(p2, St(lab, st2.log + (("set", name, s[pos:p2]),), st2.start))
        return m(node[2], s, pos, st, close)
    if t == "rep":
        _, sub, lo, hi, names, lazy = node
        branching = not (lo == 1 and hi == 1)
        st0 = reset(st, names) if branching else st
        loopid = id(node)

        def it(i, p, stc):
            def more():
                if hi is None or i < hi:
                    def after(p2, st2):
                        if p2 == p and i >= lo:
                            return None
                        return it(i + 1, p2, St(st2.lab, st2.log + (("pass", loopid, dict(st2.lab), names),), st2.start))
                    return m(sub, s, p, stc, after)
                return None

            def stop():
                if i >= lo:
                    return k(p, St(stc.lab, stc.log + (("endloop", loopid, names),), stc.start))
                return None
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
        return k(pos, st) if cond_on_labels(node, st.lab) else None
    raise ValueError(t)


def mseq(items, i, s, pos, st, k):
    if i == len(items):
        return k(pos, st)
    return m(items[i], s, pos, st, lambda p2, st2: mseq(items, i + 1, s, p2, st2, k))


# ---- the arrays and the passes, read off one path's log
def settings(log, name):
    out = []
    for e in log:
        if e[0] == "set" and e[1] == name:
            out.append(e[2])
        elif sab("s2") and e[0] == "pass" and name not in e[2]:
            out.append("")
    if sab("s4"):
        out = out[1:]
    if sab("s12"):
        out = out[-1:]
    return out


def outer_passes(log, names):
    """The labels each pass of the OUTERMOST loop holding the names left: of the loops whose body holds one of
    the names, the one whose end comes last on the path."""
    ends = [e[1] for e in log if e[0] == "endloop" and set(names) & e[2]]
    if not ends:
        return []
    return [e[2] for e in log if e[0] == "pass" and e[1] == ends[-1]]


# ---- group questions: an end test on a path
def gq_values(cond, log, mode):
    """The verdicts of a condition over its array (settings) or over the passes: a list of booleans."""
    _, neg, entries, joint = cond
    if mode == "passes" or (joint and mode == "byitem"):
        names = entries[0][0] if joint else [n for n, _ in entries]
        return [cond_on_labels(cond, lab) for lab in outer_passes(log, names)]
    if joint:
        if mode == "settings" and not sab("s7"):
            raise CompileError("a joint entry inside a group question is refused for now: label the item where it "
                               "meets the condition, `[ok = item & ((h, m): (..))]`, then `some((ok: anything))`")
        names, vals = entries[0]
        arrs = [settings(log, n) for n in names]
        if sab("s6"):
            n = min(len(a) for a in arrs)
            arrs = [a[len(a) - n:] for a in arrs]
        res = [all(val_ok(x, v) for x, v in zip(tup, vals)) for tup in zip(*arrs)]
        return [(not r) if neg else r for r in res]
    if len(entries) != 1:
        raise CompileError("several entries: no single array")
    name, val = entries[0]
    res = [val_ok(x, val) for x in settings(log, name)]
    return [(not r) if neg else r for r in res]


def gq_some(cond, log, mode):
    _, neg, entries, joint = cond
    if not joint and len(entries) > 1 and mode != "passes":
        if sab("s5"):                               # the record as a joint pairing by index
            arrs = [settings(log, n) for n, _ in entries]
            return any(all(val_ok(x, v) for x, (_, v) in zip(tup, entries)) for tup in zip(*arrs))
        # the manager's reading (a): the product of its entries, each a group question over its own array
        return all(gq_some(("cond", False, [e], False), log, mode) for e in entries)
    vals = gq_values(cond, log, mode)
    if not vals and sab("s9"):
        return True
    return any(vals)


def gq_count(cond, log, mode):
    _, neg, entries, joint = cond
    if not joint and len(entries) > 1 and (mode == "byindex" or sab("s17")):   # count-several's candidate (b): the arrays zipped
        arrs = [settings(log, n) for n, _ in entries]
        return sum(1 for tup in zip(*arrs) if all(val_ok(x, v) for x, (_, v) in zip(tup, entries)))
    return sum(1 for v in gq_values(cond, log, mode) if v)


def gq_none(cond, log, mode):
    if sab("s10") and mode == "settings":
        return not any(not v for v in gq_values(cond, log, mode))
    return gq_count(cond, log, mode) == 0


def gq_index(name, k, val, log, mode):
    if mode == "passes":
        ps = outer_passes(log, [name])
        return len(ps) >= k and val_ok(ps[k - 1].get(name), val)
    arr = settings(log, name)
    return len(arr) >= k and val_ok(arr[k - 1], val)


class Prog:
    """An rx (matcher text) and its end tests (group questions), each a function of the path's log."""

    def __init__(self, rx, ends=()):
        self.rx = rx
        self.node = p_alt(Src(rx))
        self.ends = list(ends)

    def at(self, s, start, need_end=None, nonempty=False):
        def fin(p, st):
            if need_end is not None and p != need_end:
                return None
            if nonempty and p == start:
                return None
            if not all(e(st.log) for e in self.ends):
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


# ================================================================== the lowerer (expression text -> matcher text)
def split_top(text, sep):
    """Split at `sep` outside (), [], /../ and ".."."""
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


IS_COND = re.compile(r"^(NOT )?\(\(?\w+(?:, \w+)*\)?: ")
GQ = re.compile(r"^(NOT )?(some|occurs\.none)\((.*)\)$")
INDEX = re.compile(r'^\((\w+)\[(\d+)\]: (.*)\)$')
BINDS = {}
MACROS = {}
LATE = []          # conditions a part label's `&` pushed to the program's end (sabotage s8 only)


def lib_body(pattern):
    mm = re.search(pattern, LIB)
    assert mm, pattern
    return mm.group(1)


HITS_BODY = lib_body(r"`hits\(r\) := (/.*?/)`")
CHARS = lib_body(r"`chars := (/.*?/)`")
NCHARS = lib_body(r"`nchars := (count\(\(ch: /\(\?s:\.\)/\)\))`")
ANYTHING = lib_body(r"`anything` is `(\[\\s\\S\]\*)`")


def define(line):
    head, body = [x.strip() for x in line.split(":=", 1)]
    mm = re.fullmatch(r"(\w+)\((\w+)\)", head)
    if mm:
        MACROS[mm.group(1)] = (mm.group(2), body)
    else:
        BINDS[head] = body


def base_binds():
    BINDS.clear()
    MACROS.clear()
    define("hits(r) := " + HITS_BODY)
    define("chars := " + CHARS)
    define("nchars := " + NCHARS)
    define("anything := /" + ANYTHING + "/")


def lower(expr, params=None):
    """-> (matcher text, end tests). An end test is a function of a path's log, read in MODE."""
    params = params or {}
    expr = expr.strip()
    parts = split_top(expr, " & ")
    if len(parts) > 1:
        text, ends = lower(" & ".join(parts[:-1]), params)
        last = parts[-1]
        if IS_COND.match(last) and not INDEX.match(last):
            mm = re.fullmatch(r"\((\w+): (.*)\)", last)
            if mm and mm.group(1) in BINDS and BINDS[mm.group(1)].startswith("count("):
                return text, ends + [count_test(BINDS[mm.group(1)], mm.group(2))]
            return "(?:%s)${%s}" % (text, last), ends           # the condition at the operand's end
        return text, ends + [gq_test(last)]
    alts = split_top(expr, " | ")
    if len(alts) > 1:
        vs = [lower(a, params) for a in alts]
        return "|".join("(?:%s)" % v[0] for v in vs), sum((v[1] for v in vs), [])
    mm = re.fullmatch(r"\((.*)\)([+*?])", expr)
    if mm:
        text, ends = lower(mm.group(1), params)
        return "(?:%s)%s" % (text, mm.group(2)), ends
    if expr.startswith("(") and expr.endswith(")") and not IS_COND.match(expr):
        return lower(expr[1:-1], params)
    mm = re.fullmatch(r"\[(\w+) = (.*)\]", expr)
    if mm:
        name, e = mm.groups()
        if sab("s8"):
            sub = split_top(e, " & ")
            if len(sub) > 1:
                text, ends = lower(sub[0], params)
                LATE.append(sub[1])
                return "(?<%s>%s)" % (name, text), ends
        text, ends = lower(e, params)
        return "(?<%s>%s)" % (name, text), ends
    if expr.startswith("/") and expr.endswith("/"):
        return lower_literal(expr[1:-1], params), []
    if expr.startswith('"') and expr.endswith('"'):
        return re.escape(expr[1:-1]), []
    mm = re.fullmatch(r"(\w+)\((.*)\)", expr)
    if mm and mm.group(1) in MACROS:
        pname, body = MACROS[mm.group(1)]
        arg = lower(mm.group(2), params)[0]
        return lower(body, {pname: arg})
    if expr in params:
        return params[expr], []
    if expr in BINDS:
        return lower(BINDS[expr], params)
    raise CompileError("an undeclared name: " + expr)


def lower_literal(rx, params):
    out, i = [], 0
    while i < len(rx):
        if rx.startswith("${", i):
            j = rx.index("}", i)
            while rx.count("(", i, j) != rx.count(")", i, j):
                j = rx.index("}", j + 1)
            body = rx[i + 2:j].strip()
            i = j + 1
            if body in params:
                out.append("(?:%s)" % params[body])
            elif body in BINDS:
                out.append("(?:%s)" % lower(body)[0])
            else:
                out.append("${%s}" % body)
            continue
        out.append(rx[i])
        i += 1
    return "".join(out)


MODE = ["settings"]


def gq_test(text):
    mm = INDEX.match(text)
    if mm:
        name, k, val = mm.group(1), int(mm.group(2)), parse_value(mm.group(3))
        return lambda log: gq_index(name, k, val, log, MODE[0])
    mm = GQ.match(text)
    if not mm:
        raise CompileError("not a group question: " + text)
    neg, fn, arg = bool(mm.group(1)), mm.group(2), parse_cond(mm.group(3))
    if MODE[0] == "settings" and arg[3] and not sab("s7"):
        gq_values(arg, (), "settings")             # the refusal is at compile time
    f = gq_some if fn == "some" else gq_none

    def test(log):
        r = f(arg, log, MODE[0])
        return (not r) if neg else r
    return test


def count_test(count_text, cmp_text):
    arg = parse_cond(re.fullmatch(r"count\((.*)\)", count_text).group(1))
    if MODE[0] == "settings" and not arg[3] and len(arg[2]) > 1 and not sab("s17"):
        raise CompileError("not stated: what a count of several entries counts")
    val = parse_value(cmp_text)
    return lambda log: val_ok(str(gq_count(arg, log, MODE[0])), val)


def prog(expr, binds=(), mode="settings"):
    base_binds()
    for b in binds:
        define(b)
    MODE[0] = mode
    LATE.clear()
    text, ends = lower(expr)
    for c in LATE:                                   # sabotage s8: the part's condition read at the end
        text = "(?:%s)${%s}" % (text, c)
    P = Prog(text, ends)
    P.mode = mode
    return P


class Bound:
    """A program whose end tests read MODE at run time: fix the mode around every use."""

    def __init__(self, expr, binds=(), mode="settings"):
        self.expr, self.binds, self.mode = expr, binds, mode
        self.P = prog(expr, binds, mode)

    def _with(self, f, *a):
        MODE[0] = self.mode
        return f(*a)

    def whole(self, s):
        return self._with(self.P.whole, s)

    def search(self, s):
        return self._with(self.P.search, s)

    def findall(self, s):
        return self._with(self.P.findall, s)


LINES = []


def doc_line(L, tag):
    LINES.append((tag, L))
    return L


def line(expr, binds, mode, wh, sr, fa, label=None, tag="?"):
    B = Bound(expr, binds, mode)
    L = fmt(B, wh, sr, fa)
    return L


# ================================================================== the checks
# ---------------------------------------------------------------- CONTROL: the matcher + lowerer against python `re`
print("== the library bodies read from library.md: hits %s ; chars %s ; nchars %s ; anything %s"
      % (HITS_BODY, CHARS, NCHARS, ANYTHING))
print("== CONTROL: lowered programs without group questions against python `re` on hand regexes")
POPI = pop("53:,", 5)
c1 = ndiff(answers_p(Bound("/(?:(?<h>\\d)(?::(?<m>\\d))?,)+/"), POPI), answers_re(r"(?:\d(?::\d)?,)+", POPI))
POPA = pop("abc", 4)
c2 = ndiff(answers_p(Bound('"ab" | "a"'), POPA), answers_re(r"ab|a", POPA))
c3 = ndiff(answers_p(Bound('/(?:a|ab)??c/'), POPA), answers_re(r"(?:a|ab)??c", POPA))
check("CONTROL", c1 == (0, 0, 0) and c2 == (0, 0, 0) and c3 == (0, 0, 0),
      "the optional-m item loop %s of %d ; `\"ab\" | \"a\"` %s, `(?:a|ab)??c` %s of %d" % (c1, len(POPI), c2, c3, len(POPA)))

# ---------------------------------------------------------------- ARRAYS: the array of settings against python finditer
print("== ARRAYS: the array of settings (from the path's log) against python `re`'s finditer over the matched text")
PI = prog("/(?:(?<h>\\d)(?::(?<m>\\d))?,)+/")
bad, n_ok = [], 0
for t in pop("53:,", 6):
    r = PI.at(t, 0, need_end=len(t))
    if r is None:
        continue
    n_ok += 1
    hs = [x.group(1) for x in re.finditer(r"(\d)(?::(\d))?,", t)]
    ms = [x.group(2) for x in re.finditer(r"(\d)(?::(\d))?,", t) if x.group(2) is not None]
    if settings(r[2].log, "h") != hs or settings(r[2].log, "m") != ms:
        bad.append(t)
r = PI.at("5,2:3,", 0, need_end=6)
a_h, a_m = settings(r[2].log, "h"), settings(r[2].log, "m")
POPT = prog("/(?:(?<h>\\d)?;)*/")
r2 = POPT.at("7;;3;", 0, need_end=5)
a_slot = settings(r2[2].log, "h")
check("ARRAYS", not bad and a_h == ["5", "2"] and a_m == ["3"] and a_slot == ["7", "3"],
      "%d whole matches over `53:,` (length <= 6), %d differ ; `5,2:3,`: h = %s, m = %s ; "
      "`/(?:(?<h>\\d)?;)*/` on `7;;3;`: h = %s" % (n_ok, len(bad), a_h, a_m, a_slot))

# ---------------------------------------------------------------- OUTSIDE: the label beside the array
print("== OUTSIDE: the label rule (a reset, a name set before a loop and inside it) beside the array of settings")
RX_OUT = "/(?<h>\\d);(?:(?<h>\\d);)*/"
L_OUT_A = doc_line("Outside the loop: Settings: " + fmt(Bound(RX_OUT + ' & some((h: "7"))'), ["7;", "1;7;"], "x7;", "7; 1;7; 1;")
                   + ' (`%s & some((h: "7"))`)' % RX_OUT, "array-vs-passes")
L_OUT_L = doc_line("Outside the loop, the label beside it: " + fmt(Bound(RX_OUT + ' & (h: "7")'), ["7;", "1;7;"], "x7;", "7; 1;7; 1;")
                   + ' (`%s & (h: "7")`)' % RX_OUT, "array-vs-passes")
r = prog(RX_OUT).at("7;", 0, need_end=2)
lab_h, arr_h = r[2].lab.get("h"), settings(r[2].log, "h")
PSEP = prog("/(?<h>\\d)(?:,(?<h>\\d))*/")
r = PSEP.at("7", 0, need_end=1)
sep_lab, sep_arr = r[2].lab.get("h"), settings(r[2].log, "h")
print("   " + L_OUT_A)
print("   " + L_OUT_L)
check("OUTSIDE", lab_h is None and arr_h == ["7"] and sep_lab is None and sep_arr == ["7"]
      and "WHOLE `7;` HOLDS" in L_OUT_A and "WHOLE `7;` FAILS" in L_OUT_L,
      "`7;`: label h %s, array %s ; the separated list on `7`: label %s, array %s (a reset acts on the label, the "
      "array keeps every setting)" % (lab_h, arr_h, sep_lab, sep_arr))

# ---------------------------------------------------------------- AVP: the six lines of the piece, re-run
print("== AVP: the piece's three witnesses, settings (ruled) and passes (rejected)")
AVP = [
    ("Two depths", "/(?:(?:(?<h>\\d);)+,)+/", '(h[2]: "5")', ["3;4;,5;,", "3;,5;,"], "x3;4;,5;,", "3;4;,5;, 3;,5;,"),
    ("Two in a pass", "/(?:(?<d>\\d)(?<d>\\d),)+/", 'some((d: "7"))', ["71,", "17,"], "x71,", "71, 17, 12,"),
    ("Outside the loop", RX_OUT, 'some((h: "7"))', ["7;", "1;7;"], "x7;", "7; 1;7; 1;"),
]
avp = {}
for nm, rx_t, q, wh, sr, fa in AVP:
    for mode, word in (("settings", "Settings"), ("passes", "Passes")):
        L = fmt(Bound("%s & %s" % (rx_t, q), mode=mode), wh, sr, fa)
        tag = "array-vs-passes" if mode == "settings" else "array-vs-passes rejected"
        avp[(nm, mode)] = doc_line("%s: %s: %s (`%s & %s`)" % (nm, word, L, rx_t, q), tag)
        print("   " + avp[(nm, mode)])
differ = sum(1 for nm, *_ in AVP if avp[(nm, "settings")].split(": ", 2)[2] != avp[(nm, "passes")].split(": ", 2)[2])
check("AVP", differ == 3 and "`3;4;,5;,` FAILS" in avp[("Two depths", "settings")]
      and "`71,` HOLDS" in avp[("Two in a pass", "settings")] and "`7;` HOLDS" in avp[("Outside the loop", "settings")],
      "the two readings give different lines on %d of 3 witnesses; settings: two depths `3;4;,5;,` FAILS, `71,` HOLDS, `7;` HOLDS" % differ)

# ---------------------------------------------------------------- RECORD: the record's run, a record of two entries
print("== RECORD: `some((h: \"5\", m: \"3\"))`, the manager's reading (a): the product of its entries, each over its own array")
RX_HM = "/(?:(?<h>\\d):(?<m>\\d),)+/"
Q_REC = 'some((h: "5", m: "3"))'
L_REC_S = doc_line("A record of two entries: " + fmt(Bound("%s & %s" % (RX_HM, Q_REC)), ["5:1,2:3,", "5:3,", "2:1,"],
                   "2:1, 5:1,2:3,", "5:1,2:3, 2:1, 5:3,") + " (`%s & %s`)" % (RX_HM, Q_REC), "array-vs-passes")
L_REC_P = doc_line("Passes: " + fmt(Bound("%s & %s" % (RX_HM, Q_REC), mode="passes"), ["5:1,2:3,", "5:3,", "2:1,"],
                   "2:1, 5:1,2:3,", "5:1,2:3, 2:1, 5:3,") + " (`%s & %s`)" % (RX_HM, Q_REC), "array-vs-passes rejected")
print("   " + L_REC_S)
print("   " + L_REC_P)
POPR = pop("53:,", 6)
hand = r"(?=(?:\d:\d,)*5:\d,)(?=(?:\d:\d,)*\d:3,)(?:\d:\d,)+"
crec = ndiff(answers_p(Bound("%s & %s" % (RX_HM, Q_REC)), POPR), answers_re(hand, POPR))
rec_claim = ws("passes WHOLE `5:1,2:3,` FAILS, settings HOLDS") in RECORD_WS
check("RECORD", crec == (0, 0, 0) and "`5:1,2:3,` HOLDS" in L_REC_S and "`5:1,2:3,` FAILS" in L_REC_P and rec_claim,
      "settings against the hand regex `%s`: %s of %d ; the record's line (passes FAILS, settings HOLDS on `5:1,2:3,`): %s"
      % (hand, crec, len(POPR), rec_claim))

# ---------------------------------------------------------------- JOINT and REFUSE: a joint entry inside `some`
print("== JOINT: `some(((h, m): (\"5\", \"3\")))` on the optional-m loop, paired by index and by item; REFUSE: the ruling")
RX_OPT = "/(?:(?<h>\\d)(?::(?<m>\\d))?,)+/"
Q_J = 'some(((h, m): ("5", "3")))'
WH4 = ["5:3,", "5:1,2:3,", "5,2:3,", "2:3,5,"]
SR4, FA4 = "x5,2:3,", "5:3, 5,2:3, 2:3,5, 5:1,2:3,"
L_BI = doc_line("By index: " + fmt(Bound("%s & %s" % (RX_OPT, Q_J), mode="byindex"), WH4, SR4, FA4)
                + " (`%s & %s`)" % (RX_OPT, Q_J), "array-vs-passes rejected")
L_BY = doc_line("By item: " + fmt(Bound("%s & %s" % (RX_OPT, Q_J), mode="byitem"), WH4, SR4, FA4)
                + " (`%s & %s`)" % (RX_OPT, Q_J), "array-vs-passes rejected")
L_RO = doc_line("The record form: " + fmt(Bound("%s & %s" % (RX_OPT, Q_REC)), WH4, SR4, FA4)
                + " (`%s & %s`)" % (RX_OPT, Q_REC), "array-vs-passes")
for L in (L_BI, L_BY, L_RO):
    print("   " + L)
bi = [Bound("%s & %s" % (RX_OPT, Q_J), mode="byindex").whole(t) for t in WH4]
by = [Bound("%s & %s" % (RX_OPT, Q_J), mode="byitem").whole(t) for t in WH4]
check("JOINT", bi == [True, False, True, False] and by == [True, False, False, False],
      "WHOLE by index %s, by item %s on %s: they part on `5,2:3,` only (the record: \"`5:3,` both find it; "
      "`5:1,2:3,` neither\")" % (bi, by, WH4))
try:
    Bound("%s & %s" % (RX_OPT, Q_J))
    refused = None
except CompileError as e:
    refused = str(e)
check("REFUSE", refused is not None and "[ok = item" in refused,
      "under the ruling the program is a compile error: %s" % refused)

# ---------------------------------------------------------------- IDIOM: "same item" written on the item
print("== IDIOM: the on-item label, then a group question on it, against the by-item reference")
B_ITEM = "item := /(?<h>\\d)(?::(?<m>\\d))?,/"
E_ID = '([ok = item & ((h, m): ("5", "3"))] | item)+ & some((ok: anything))'
L_ID = doc_line("Same item, on the item: " + fmt(Bound(E_ID, [B_ITEM]), WH4, SR4, FA4)
                + " (`%s`, item := `/(?<h>\\d)(?::(?<m>\\d))?,/`)" % E_ID, "array-vs-passes")
print("   " + L_ID)
POPID = pop("53:,", 6)
ans_id = answers_p(Bound(E_ID, [B_ITEM]), POPID)
d_ref = ndiff(ans_id, answers_p(Bound("%s & %s" % (RX_OPT, Q_J), mode="byitem"), POPID))
hand_id = r"(?:\d(?::\d)?,)*5:3,(?:\d(?::\d)?,)*"
d_hand = ndiff(ans_id, answers_re(hand_id, POPID))
same3 = L_ID.split(": ", 1)[1].split(" (`")[0] == L_BY.split(": ", 1)[1].split(" (`")[0]
check("IDIOM", d_ref == (0, 0, 0) and d_hand == (0, 0, 0) and same3,
      "against the by-item reading %s, against the hand regex `%s` %s, of %d texts over `53:,`; the printed line "
      "equals the by-item line: %s" % (d_ref, hand_id, d_hand, len(POPID), same3))

# ---------------------------------------------------------------- EMPTY: the group questions on an empty array
print("== EMPTY: `some` false and `count` zero on an empty array (the manager's reading (c))")
RX_DO = "/(?:(?<d>\\d)?,)+/"
L_E_S = doc_line("An empty array: " + fmt(Bound(RX_DO + ' & some(NOT (d: "7"))'), [",", "7,", "1,"], "7, ,", ", 7, 1,")
                 + ' (`%s & some(NOT (d: "7"))`)' % RX_DO, "array-vs-passes")
L_E_P = doc_line("Passes: " + fmt(Bound(RX_DO + ' & some(NOT (d: "7"))', mode="passes"), [",", "7,", "1,"], "7, ,", ", 7, 1,")
                 + ' (`%s & some(NOT (d: "7"))`)' % RX_DO, "array-vs-passes rejected")
NB = 'n := count(NOT (d: "7"))'
L_E_C = doc_line("A count of zero: " + fmt(Bound(RX_DO + " & (n: ==0)", [NB]), [",", "7,", "1,"], "1, ,", "1, , 7,")
                 + ' (`%s & (n: ==0)`, n := `count(NOT (d: "7"))`)' % RX_DO, "array-vs-passes")
L_E_CP = doc_line("Passes: " + fmt(Bound(RX_DO + " & (n: ==0)", [NB], mode="passes"), [",", "7,", "1,"], "1, ,", "1, , 7,")
                  + ' (`%s & (n: ==0)`, n := `count(NOT (d: "7"))`)' % RX_DO, "array-vs-passes rejected")
for L in (L_E_S, L_E_P, L_E_C, L_E_CP):
    print("   " + L)
check("EMPTY", "`,` FAILS" in L_E_S and "`,` HOLDS" in L_E_P and L_E_C.split(" / ")[0].endswith("`,` HOLDS, `7,` HOLDS, `1,` FAILS")
      and "`,` FAILS" in L_E_CP,
      "on `,` (one pass, no setting): settings `some(NOT c)` FAILS and the count is 0; passes HOLDS and 1")

# ---------------------------------------------------------------- TRUTH: group-truth's forms, on settings and on passes
print("== TRUTH: `NOT some(c)`, `occurs.none(c)`, `occurs.none(NOT c)` with c := (d: \"7\")")
POPT2 = pop("17,", 5)
forms = {"NOT some(c)": 'NOT some((d: "7"))', "occurs.none(c)": 'occurs.none((d: "7"))',
         "occurs.none(NOT c)": 'occurs.none(NOT (d: "7"))'}
res = {}
for mode in ("settings", "passes"):
    for k_, q in forms.items():
        res[(mode, k_)] = answers_p(Bound(RX_DO + " & " + q, mode=mode), POPT2)
t1 = ndiff(res[("settings", "NOT some(c)")], res[("settings", "occurs.none(c)")])
t2 = ndiff(res[("settings", "NOT some(c)")], res[("settings", "occurs.none(NOT c)")])
t3 = ndiff(res[("passes", "NOT some(c)")], res[("passes", "occurs.none(c)")])
t4 = ndiff(res[("settings", "occurs.none(NOT c)")], res[("passes", "occurs.none(NOT c)")])
t5 = ndiff(res[("settings", "NOT some(c)")], res[("passes", "NOT some(c)")])
check("TRUTH", t1 == (0, 0, 0) and t2 != (0, 0, 0) and t3 == (0, 0, 0) and t4 != (0, 0, 0) and t5 == (0, 0, 0),
      "of %d texts over `17,` on `%s`: settings NOT some(c) vs occurs.none(c) %s, vs occurs.none(NOT c) %s; passes "
      "NOT some(c) vs occurs.none(c) %s; occurs.none(NOT c) settings vs passes %s; NOT some(c) settings vs passes %s"
      % (len(POPT2), RX_DO, t1, t2, t3, t4, t5))
TRUTH_NUMS = (len(POPT2), t2, t4)

# ---------------------------------------------------------------- EVERYPASS: the every-pass form on settings
print("== EVERYPASS: `some(c) & occurs.none(NOT c)` against the item form")
E_EP = RX_DO + ' & some((d: "7")) & occurs.none(NOT (d: "7"))'
L_EP_S = doc_line("Every setting: " + fmt(Bound(E_EP, mode="passes" if sab("s11") else "settings"), ["7,7,", "7,,", "7,1,"], "7,, 7,7,", "7,, 7,1, 7,7,")
                  + ' (`%s`)' % E_EP, "every-pass")
E_IT = '/(?:(?<d>\\d)?${(d: "7")},)+/'
L_EP_I = doc_line("The item form: " + fmt(Bound(E_IT), ["7,7,", "7,,", "7,1,"], "7,, 7,7,", "7,, 7,1, 7,7,")
                  + ' (`%s`)' % E_IT, "every-pass")
L_EP_P = doc_line("Passes: " + fmt(Bound(E_EP, mode="passes"), ["7,7,", "7,,", "7,1,"], "7,, 7,7,", "7,, 7,1, 7,7,")
                  + ' (`%s`)' % E_EP, "every-pass")
for L in (L_EP_S, L_EP_I, L_EP_P):
    print("   " + L)
check("EVERYPASS", "`7,,` HOLDS" in L_EP_S and "`7,,` FAILS" in L_EP_I and "`7,,` FAILS" in L_EP_P,
      "on `7,,` every SETTING is 7 (HOLDS) where the item form and the passes reading FAIL")

# ---------------------------------------------------------------- CHANGED: the printed examples, pass reading -> settings
print("== CHANGED: every printed example with a group question, under the pass reading and the settings reading")
EXS = [
    ("lib/counting/some", '/(?:(?<d>\\d),)+/ & some((d: "7"))', [], ["1,7,", "1,2,"], "1,2, 7,", "7,1, 2, 3,7,",
     ' (`/(?:(?<d>\\d),)+/ & some((d: "7"))`)'),
    ("lib/counting/count", '/(?:(?<d>\\d),)+/ & (n: ==2)', ['n := count((d: "7"))'], ["7,1,7,", "7,1,"], "7,7,7,",
     "7,7,7, 1,7,7,", ' (`/(?:(?<d>\\d),)+/ & (n: ==2)`, n := `count((d: "7"))`)'),
    ("lib/modifiers/length", "chars & (nchars: ==3)", [], ["abc", "ab"], "abcd", "abcdefg",
     " (`length(==3)` as a program: `chars & (nchars: ==3)`)"),
]
chg = []
for tag, e, bs, wh, sr, fa, tail in EXS:
    Lp = fmt(Bound(e, bs, mode="passes"), wh, sr, fa) + tail
    Ls = doc_line(fmt(Bound(e, bs), wh, sr, fa) + tail, tag)
    chg.append((tag, Lp == Ls))
    print("   [%s] same under both: %s | %s" % (tag, Lp == Ls, Ls))
check("CHANGED", all(x for _, x in chg), "the three printed lines are the same under the pass and the settings "
      "readings: %s" % chg)

# ---------------------------------------------------------------- HITS: the hit list, its body against python `re`
print("== HITS: `hits(r)`'s body (read from library.md) against python `re`; \"every hit under 100\"")
POPH = pop("12 x", 5)
hits_rx = HITS_BODY.strip("/").replace("${r}", "(?:\\d+)").replace("(?<", "(?P<")   # python spells a named group (?P<..>)
ch = ndiff(answers_p(Bound("hits(/\\d+/)"), POPH), answers_re(hits_rx, POPH))
E_H = "hits(/\\d+/) & occurs.none((hit: >= 100))"
hv = {}
for mode in ("settings", "passes"):
    hv[mode] = [Bound(E_H, mode=mode).whole(t) for t in ["1234", "12 34", "12 345", "x300 12"]]
check("HITS", ch == (0, 0, 0) and hv["settings"] == [False, True, False, False] and hv["settings"] == hv["passes"],
      "the body against python `re` %s of %d ; `%s` WHOLE on `1234`, `12 34`, `12 345`, `x300 12`: settings %s, "
      "passes %s (the base: FAILS, HOLDS, FAILS, FAILS)" % (ch, len(POPH), E_H, hv["settings"], hv["passes"]))

# ---------------------------------------------------------------- QUESTIONS: the owner questions' example lines (in the report)
print("== QUESTIONS: the lines the report's owner questions print")
NC = 'n := count((h: "5", m: "3"))'
try:
    Bound(RX_HM + " & (n: ==1)", [NC])
    cs_a = "computed"
except CompileError as e:
    cs_a = "a compile error (" + str(e) + ")"
L_CS_B = doc_line("count-several (b), the arrays paired by index: " + fmt(Bound(RX_HM + " & (n: ==1)", [NC], mode="byindex"),
                  ["5:3,2:1,", "5:1,2:3,"], "5:1,2:3, 5:3,", "5:3,2:1, 5:1,2:3, 5:3,")
                  + ' (`%s & (n: ==1)`, n := `count((h: "5", m: "3"))`)' % RX_HM, "report")
L_GT_1 = doc_line("group-truth, `NOT some(c)`: " + fmt(Bound(RX_DO + ' & NOT some((d: "7"))'), ["1,,", "7,1,", ","], "7, 1,,", "7, 1,, 7,1, ,")
                  + ' (`%s & NOT some((d: "7"))`)' % RX_DO, "report")
L_GT_2 = doc_line("group-truth, `occurs.none(c)`: " + fmt(Bound(RX_DO + ' & occurs.none((d: "7"))'), ["1,,", "7,1,", ","], "7, 1,,", "7, 1,, 7,1, ,")
                  + ' (`%s & occurs.none((d: "7"))`)' % RX_DO, "report")
L_GT_3 = doc_line("group-truth, `occurs.none(NOT c)`: " + fmt(Bound(RX_DO + ' & occurs.none(NOT (d: "7"))'), ["1,,", "7,1,", ","], "7, 1,,", "7, 1,, 7,1, ,")
                  + ' (`%s & occurs.none(NOT (d: "7"))`)' % RX_DO, "report")
for L in (L_CS_B, L_GT_1, L_GT_2, L_GT_3):
    print("   " + L)
check("QUESTIONS", cs_a.startswith("a compile error") and L_GT_1.split(": ", 1)[1].split(" (`")[0] == L_GT_2.split(": ", 1)[1].split(" (`")[0]
      and L_GT_1.split(": ", 1)[1].split(" (`")[0] != L_GT_3.split(": ", 1)[1].split(" (`")[0],
      "count of a record under the ruling's model: %s ; NOT some(c) and occurs.none(c) print the same line, occurs.none(NOT c) another" % cs_a)

# ---------------------------------------------------------------- RECLINES: the record's lines this lane relies on
print("== RECLINES: the record's printed lines, in the record and as run")
rec_lines = [
    "passes WHOLE `5:1,2:3,` FAILS, settings HOLDS",
    "`5,2:3,` has h = [`5`, `2`], m = [`3`]: paired BY INDEX the tuple (`5`, `3`) is found though no item holds both; "
    "paired by ITEM it is not found. `5:3,` both find it; `5:1,2:3,` neither.",
    "`[ok = item & ((h, m): (\"5\", \"3\"))]` then `some((ok: anything))`",
]
if sab("s14"):
    rec_lines[0] = rec_lines[0].replace("FAILS", "HOLDS")
rmiss = [x for x in rec_lines if ws(x) not in RECORD_WS]
check("RECLINES", not rmiss, "%d record lines; missing: %s" % (len(rec_lines), rmiss))

# ---------------------------------------------------------------- QUOTES: the owner's words this lane quotes
print("== QUOTES: the owner's words this lane quotes, verbatim in the record")
QUOTED = [
    "they chose to use the same labels and therefore that has to have a meaning. for simplicity, and due to the fact "
    "that the other interpretations can be otherwise spelled, i think option \"a\"",
    "if they wanted the out-the-loop setting to be separately labeled they could have done so.",
    "if they wanted the h5,m3 condition to be held at the same time they could have specified (h,m): (5,3) but they "
    "did not.",
    "join-in-some: agree and elegant. that said, no one would know to write it.",
    "The array takes all h including the one outside the group",
    "record-is-product: absolutely. This is precisely the sort of simplifying semantics I'm looking for.",
]
if sab("s15"):
    QUOTED[3] = QUOTED[3].replace("elegant", "simple")
qmiss = [q for q in QUOTED if ws(q) not in RECORD_WS]
check("QUOTES", not qmiss, "%d quoted sentences; missing from the record: %s" % (len(QUOTED), qmiss))

# ---------------------------------------------------------------- DOC: every formatted line is in the documents
print("== DOC: every formatted line occurs verbatim in the documents")
lines = list(LINES)
if sab("s16"):
    lines[0] = (lines[0][0], lines[0][1].replace("`7;`", "`8;`", 1))
REPORT_PATH = os.path.join(W, "docs", "dev", "lanes", "predarr_report.md")
REPORT = read(REPORT_PATH) if os.path.exists(REPORT_PATH) else ""
missing = [(t, L) for t, L in lines if L not in (REPORT if t == "report" else DOCS)]
for t, L in lines:
    print("   [%s] %s" % (t, L))
check("DOC", not missing, "%d lines (%d in the report); missing: %s" % (len(lines), sum(1 for t, _ in lines if t == "report"), missing))

print("predarr_model: %d checks, %d failed%s" % (len(CHECKS), len(FAILED), (" (" + ", ".join(FAILED) + ")") if FAILED else ""))
