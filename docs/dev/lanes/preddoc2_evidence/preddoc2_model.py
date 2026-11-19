#!/usr/bin/env -S python3 -I
# Lane preddoc2 (2026-11-19): the evidence that the macros moved from the core to the library (`peek`, `when` with
# its test, `rx.repeat`) have BODIES in the core language reproducing every RULED example of the frozen draft
# (docs/design/predicates_draft.md revision 29.1) in WHOLE, SEARCHED and FIND-ALL; the zero-values sub-pieces'
# examples; the manager's readings 3 and 4 (no `needs:` from the core into the library; no moved statement
# changes wording); the slug census (124 of 124 homed, counted as lane preddoc1 counted).
# DESIGN EVIDENCE ONLY; rules nothing.
#
# METHOD. A BODY is written once below as a function from its arguments (regex text) to regex text, using only the
# core's own constructs: a pattern hole `${X}` = `(?:X)`, a lookahead, the sequence (concatenation), `|`, count
# holes (the copy rule of core/holes/count), NOT on a zero-width test (a negative lookahead). Each example is then
# (1) RUN: the expanded regex in python `re`, the three modes; (2) compared with the DRAFT'S PRINTED ANSWERS, typed
# in here from the draft by hand (the control; they were run by earlier lanes on libpcre2 and against PCRE2's own
# conditional group, so they do not share a source with these bodies); where the draft printed fewer than three
# modes, (3) a DIRECT SEMANTIC MODEL written from the ruled words alone (no regex for the conditional: "if the test
# holds at the point, then-branch from there (peek, condition) or after the test (bare), else the else-branch; no
# fall-through"), with its own find-all loop, supplies the missing modes and must agree with the run; and (4) the
# example LINE printed by the formatter must occur verbatim in the document it is the example of.
#
# Run (W = the worktree; any cwd):  timeout 300 python3 -I -B W/docs/dev/lanes/preddoc2_evidence/preddoc2_model.py
# PREDDOC2_SABOTAGE=sN (one at a time): a deliberately wrong body or fact; its check must FAIL.
#   s1  peek CONSUMES (the body without the lookahead)                  -> PE, W1, WT, WD
#   s2  when's else branch UNGUARDED (no `NOT peek(test)`)              -> W1, WT, WN, WC, WV
#   s3  the missing else FAILS (`else = (?!)`)                          -> W1, WD, WN, WCnot, W8
#   s4  a bare test PEEKED (when-peek reversed)                         -> W1, WT, WV
#   s5  peek hides its labels (the label group made non-capturing)      -> PE
#   s6  `then` optional in when's signature                             -> WS
#   s7  the condition test's guard dropped (`NOT c` replaced by nothing) -> WC
#   s8  a value test as its own case (a bare `$y` test peeked)          -> WV
#   s9  one array mentioned twice bound ONCE (not per mention)          -> RB
#   s10 an illegal count copy KEPT (reversed to a legal range)          -> RXnone
#   s11 "no maximum" written as `{min,min}`                             -> R6
#   s12 zero values in a pattern hole read as the empty string          -> ZV
#   s13 zero values in a count hole read as the count value zero        -> ZV
#   s14 a moved statement reworded                                      -> M4
#   s15 a `needs:` from the core into the library planted               -> M3
#   s16 the 2026-11-17 special case reading the FIRST pass's h          -> W8
#   s17 a slug dropped from its details entry                           -> SL
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
SAB = set(x for x in os.environ.get("PREDDOC2_SABOTAGE", "").split(",") if x)
FAILED, CHECKS = [], []


def sab(n):
    return n in SAB


def check(name, ok, detail=""):
    CHECKS.append(name)
    print("%-6s %s %s" % (name, "ok  " if ok else "FAIL", detail))
    if not ok:
        FAILED.append(name)


def doc(name):
    with open(os.path.join(PRED, name), encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------------ the three modes on a regex (python `re`)
def modes_rx(rx, whole, srch, fa, label=None):
    """-> (whole verdicts [(text, bool, label)], searched (text, span or None), find-all (text, [(text, start)]))."""
    c = re.compile(rx)
    wv = []
    for t in whole:
        m = c.fullmatch(t)
        wv.append((t, m is not None, m.group(label) if (m and label) else None))
    m = c.search(srch)
    sv = (srch, (m.group(0), m.start()) if m else None)
    fv = (fa, [(x.group(0), x.start()) for x in c.finditer(fa)])
    return wv, sv, fv


def fmt(res, prog):
    wv, sv, fv = res
    w = ", ".join("`%s` %s%s" % (t, "HOLDS" if ok else "FAILS", " (%s)" % lab if lab else "") for t, ok, lab in wv)
    s = "`%s` %s" % (sv[0], ("`%s`@%d" % sv[1]) if sv[1] else "FAILS")
    f = "`%s` [%s]" % (fv[0], ", ".join("`%s`@%d" % x for x in fv[1]))
    return "WHOLE %s / SEARCHED %s / FIND-ALL %s (%s)" % (w, s, f, prog)


# ------------------------------------------------------------------ BODIES (the core language, as regex text)
def hole(x):                       # core/holes/pattern: `${X}` is `(?:X)`
    return "(?:%s)" % x


def peek(a):                       # peek(A) := /(?=${A})/
    if sab("s1"):
        return hole(a)
    return "(?=%s)" % hole(a)


def not_peek(a):                   # NOT peek(A): the negative peek, "A cannot match here"
    return "(?!%s)" % hole(a)


EMPTY = ""                         # `//`, the empty pattern: "nothing required" (when-default)


def when(test, then, else_=None, bare=False):
    """when(test, then, else = //) := (test SEQ then) | (NOT peek(test) SEQ else).
    `test` is regex text: a condition or a peek is already zero width; a bare pattern is consumed by `test SEQ then`."""
    if else_ is None:
        else_ = "(?!)" if sab("s3") else EMPTY
    if bare and sab("s4"):
        test = peek(test)
    guard = "" if sab("s2") else not_peek(test)
    return "%s|%s" % (hole(test + hole(then)), hole(guard + hole(else_)))


def when_call(*args, **kw):
    """The signature `when(test, then, else = //)`: then has no default (`then` is required, RULED); a call binds its
    arguments positionally, then by name; an unknown, doubled or missing parameter is a compile error."""
    params, defaults = ["test", "then", "else"], {"else": EMPTY}
    if sab("s6"):
        defaults["then"] = EMPTY
    if len(args) > len(params):
        return None
    bound = dict(zip(params, args))
    for k, v in kw.items():
        if k not in params or k in bound:
            return None
        bound[k] = v
    for p in params:
        if p not in bound:
            if p not in defaults:
                return None
            bound[p] = defaults[p]
    return bound


def copies(lit, holes):
    """core/holes/count's copy rule: one copy of LIT per combination of the count holes (first hole slowest, values in
    the order given), a copy that is not a legal pattern removed whole; every copy removed: `(?!)`."""
    combos = [[]]
    for vals in holes:
        combos = [c + [v] for c in combos for v in vals]
    out = []
    for c in combos:
        t = lit
        for v in c:
            t = t.replace("{}", str(v), 1) if "{}" in t else t
        ok = True
        nums = [v for v in c if v is not None]
        if len(c) == 2 and c[1] is not None and c[0] > c[1]:
            ok = False
            if sab("s10"):
                t = lit.replace("{}", str(c[1]), 1).replace("{}", str(c[0]), 1)
                ok = True
        if ok and nums:
            out.append(t)
    return "(?:%s)" % "|".join(out) if out else "(?!)"


def repeat(x, n=None, mn=None, mx=None, nomax=False):
    """repeat(x, n) := /(?:${x}){${n}}/; repeat(x, min, max) := /(?:${x}){${min},${max}}/;
    repeat(x, min) := /(?:${x}){${min},}/ (the draft's reading for "no maximum": a second body, the bound left out).
    n, mn, mx are arrays of counts (a constant is a one-member array)."""
    if n is not None:
        return copies(hole(x) + "{{}}", [n])
    if nomax:
        if sab("s11"):
            return copies(hole(x) + "{{},{}}", [mn, mn])
        return copies(hole(x) + "{{},}", [mn])
    return copies(hole(x) + "{{},{}}", [mn, mx])


def lift_add(arr, k):              # core/arrays/lift: `n + 1` over an array
    return [v + k for v in arr]


# ------------------------------------------------------------------ the DIRECT SEMANTIC MODEL of `when`
def ends(rx, s, i):
    m = re.compile(rx).match(s, i)
    return [m.end()] if m else []


def sem_when(kind, a, b, c, pre=None):
    """-> f(s, i): the ends of `when` from i, priority order. kind: 'peek' | 'bare' | 'cond' (a is then a predicate
    on (s, i)). pre: a fixed piece before the conditional (regex), as in `[h = rx.digit] SEQ when(...)`."""
    def f(s, i):
        starts = ends(pre, s, i) if pre else [i]
        out = []
        for j in starts:
            if kind == "cond":
                holds = a(s, j)
                after = [j]
            else:
                ae = ends(a, s, j)
                holds = bool(ae)
                after = [j] if kind == "peek" else ae
            if holds:
                for k in after:
                    out += ends(b, s, k)
            elif c is not None:
                out += ends(c, s, j)
            else:
                out.append(j)
        return out
    return f


def sem_modes(f, whole, srch, fa):
    wv = [(t, len(t) in f(t, 0), None) for t in whole]
    sv = (srch, None)
    for i in range(len(srch) + 1):
        e = f(srch, i)
        if e:
            sv = (srch, (srch[i:e[0]], i))
            break
    hits, i, last_empty_at = [], 0, None
    while i <= len(fa):
        e = f(fa, i)
        if last_empty_at == i:            # PCRE: after an empty match, retry here non-empty, else advance
            e = [x for x in e if x != i]
        if e:
            hits.append((fa[i:e[0]], i))
            if e[0] == i:
                last_empty_at = i
            else:
                i = e[0]
                last_empty_at = None
                continue
            continue
        i += 1
    return wv, sv, (fa, hits)


def same(a, b):
    return [(t, ok) for t, ok, _ in a[0]] == [(t, ok) for t, ok, _ in b[0]] and a[1] == b[1] and a[2] == b[2]


def printed(res, whole, srch, fa):
    """Compare a run with the draft's printed answers: whole = {text: bool}, srch = (text, start) or None, fa = [..]."""
    wv, sv, fv = res
    ok = all(dict((t, o) for t, o, _ in wv)[t] == v for t, v in whole.items())
    if srch is not False:
        ok = ok and (sv[1] == srch)
    if fa is not None:
        ok = ok and fv[1] == fa
    return ok


def in_doc(line, *names):
    return any(line in doc(n) for n in names)


def part(name, fn):
    try:
        fn()
    except Exception as ex:  # a part that raises is its own FAILED check
        check("P" + name, False, "raised %r" % ex)


# ================================================================== PE: peek
def part_pe():
    # the draft (when-test entry, lookahead-labels): `(?=(?<d>\d))\d\d` on `37`: d = `3`; s5 hides the label
    rx = peek("\\d" if sab("s5") else "(?P<d>\\d)") + "\\d\\d"
    res = modes_rx(rx, ["37", "3"], "x37", "37 4 56", label="d" if "(?P<d>" in rx else None)
    ok = printed(res, {"37": True, "3": False}, ("37", 1), [("37", 0), ("56", 5)]) and res[0][0][2] == "3"
    sem = sem_modes(sem_when("peek", "\\d", "\\d\\d", "(?!)"), ["37", "3"], "x37", "37 4 56")  # no else: fail
    t, o, lab = res[0][0]
    wv = [(t, o, ("d = `%s`" % lab) if lab else None), res[0][1]]
    line = fmt((wv, res[1], res[2]), "`peek(/(?<d>\\d)/) SEQ /\\d\\d/` is `(?=(?:(?<d>\\d)))\\d\\d`")
    check("PE", ok and res[1] == sem[1] and res[2] == sem[2] and in_doc(line, "library.md"),
          "peek: %s | doc line %s" % (line, "found" if in_doc(line, "library.md") else "NOT FOUND"))


# ================================================================== W1: the four forms of R.1.10's table
TABLE = [  # form, (test, then, else, bare, kind), the draft's printed WHOLE `12` / SEARCHED `x123` / FIND-ALL
    ("when(peek(A), B, else = C)", (peek("\\d"), "\\d\\d", "\\w", False, "peek"),
     True, ("x", 0), [("12", 0), ("x", 3), ("12", 5), ("x", 10)]),
    ("when(peek(A), B)", (peek("\\d"), "\\d\\d", None, False, "peek"),
     True, ("", 0), [("12", 0), ("", 2), ("", 3), ("", 4), ("12", 5), ("", 8), ("", 10), ("", 11), ("", 13)]),
    ("when(A, B, else = C)", ("\\d", "\\d\\d", "\\w", True, "bare"),
     False, ("x", 0), [("x", 3), ("123", 5), ("x", 10)]),
    ("when(A, B)", ("\\d", "\\d\\d", None, True, "bare"),
     False, ("", 0), [("", 2), ("", 3), ("", 4), ("123", 5), ("", 8), ("", 10), ("", 11), ("", 13)]),
]


def part_w1():
    bad = []
    for form, (t, b, c, bare, kind), w12, s, fa in TABLE:
        rx = when(t, b, c, bare=bare)
        res = modes_rx(rx, ["12"], "x123", "12 x 123 1x 7")
        sem = sem_modes(sem_when(kind, "\\d", b, c), ["12"], "x123", "12 x 123 1x 7")
        if not (printed(res, {"12": w12}, s, fa) and same(res, sem)):
            bad.append(form)
    check("W1", not bad, "R.1.10's four forms against the draft's table and the semantic model; differ: %s" % (bad or "none"))
    rx = when(peek("\\d"), "\\d\\d", "\\w")
    line = fmt(modes_rx(rx, ["12", "1"], "x123", "12 x 123 1x 7"),
               "`when(peek(/\\d/), /\\d\\d/, else = /\\w/)` is `(?=\\d)\\d\\d|(?!\\d)\\w`")
    check("W1doc", in_doc(line, "library.md"), "when's example line: %s" % line)


# ================================================================== WT: the when-test entry's table (whole values)
def part_wt():
    peekf = when(peek("\\d"), "\\d\\d", "\\w")
    cons = when("\\d", "\\d\\d", "\\w", bare=True)
    pv = {t: modes_rx(peekf, [t], "", "")[0][0][1] for t in ("12", "123", "x", "1")}
    cv = {t: modes_rx(cons, [t], "", "")[0][0][1] for t in ("12", "123", "x", "1")}
    ok = pv == {"12": True, "123": False, "x": True, "1": False} and cv == {"12": False, "123": True, "x": True, "1": False}
    check("WT", ok, "peek %r consumed %r (the draft: peek 12 holds, 123 fails, x holds, 1 fails; consumed 12 fails, "
                   "123 holds, x holds, 1 fails)" % (pv, cv))
    rx = when("\\d", "\\d\\d", "\\w", bare=True)
    line = fmt(modes_rx(rx, ["12", "123"], "x123", "12 x 123 1x 7"),
               "`when(/\\d/, /\\d\\d/, else = /\\w/)`, a bare test, is `\\d\\d\\d|(?!\\d)\\w`")
    check("WTdoc", in_doc(line, "library.md"), "the test's example line: %s" % line)


# ================================================================== WD: when-default's hand-worked answers
def part_wd():
    rx = when(peek("\\d"), "\\d\\d")
    res = modes_rx(rx, ["12", "1"], "x", "")
    check("WD", printed(res, {"12": True, "1": False}, ("", 0), None),
          "when-default: WHOLE `12` HOLDS, `1` FAILS, SEARCHED `x` ``@0 (the draft R.1.10 (2))")


# ================================================================== WN: else-only by NOT (a peek)
def part_wn():
    t = "(?!%s)" % hole("\\d")              # NOT peek(x), x := \d
    rx = when(t, "\\w")
    res = modes_rx(rx, ["x"], "1x", "x1 y 12")
    sem = sem_modes(sem_when("cond", lambda s, i: not re.match("\\d", s[i:]), "\\w", None), ["x"], "1x", "x1 y 12")
    check("WN", printed(res, {"x": True}, ("", 0), [("x", 0), ("", 1), ("y", 3), ("", 5), ("", 6)]) and same(res, sem),
          "when(NOT peek(x), z): WHOLE `x` HOLDS; SEARCHED `1x` ``@0; FIND-ALL `x1 y 12` [`x`@0, ``@1, `y`@3, ``@5, ``@6]")


# ================================================================== WC: a CONDITION as the test, and the else-only by NOT
def part_wc():
    c = "(?<=[0-4])"                         # (h: <5), h the digit just read (the label rx.digit sets)
    notc = "(?<![0-4])"
    if sab("s7"):
        rx = "\\d(?:%s)" % ("%s|%s" % (hole(c + hole("\\d\\d")), hole("\\w")))
    else:
        rx = "\\d(?:%s)" % when(c, "\\d\\d", "\\w")
    res = modes_rx(rx, ["112"], "x7x", "112 7x 17")
    cond = lambda s, i: i > 0 and s[i - 1] in "01234"
    sem = sem_modes(sem_when("cond", cond, "\\d\\d", "\\w", pre="\\d"), ["112"], "x7x", "112 7x 17")
    check("WC", printed(res, {"112": True}, ("7x", 1), [("112", 0), ("7x", 4)]) and same(res, sem),
          "[h = rx.digit] SEQ when((h: <5), /\\d\\d/, else = /\\w/): WHOLE `112` HOLDS; SEARCHED `x7x` `7x`@1; "
          "FIND-ALL `112 7x 17` [`112`@0, `7x`@4]")
    rx = "\\d(?:%s)" % when(notc, "\\w")
    res = modes_rx(rx, ["7x"], "x17x", "7x 1x 17 7")
    sem = sem_modes(sem_when("cond", lambda s, i: not cond(s, i), "\\w", None, pre="\\d"), ["7x"], "x17x", "7x 1x 17 7")
    check("WCnot", printed(res, {"7x": True}, ("1", 1), [("7x", 0), ("1", 3), ("1", 6)]) and same(res, sem),
          "[h = rx.digit] SEQ when(NOT (h: <5), /\\w/): WHOLE `7x` HOLDS; SEARCHED `x17x` `1`@1; FIND-ALL [`7x`@0, `1`@3, `1`@6]")


# ================================================================== WS: the call forms (then required; single arg an error)
def part_ws():
    legal = [(("x", "y"), {}), (("x", "y", "z"), {}), (("x",), {"then": "y"}), (("x",), {"then": "y", "else": "z"}),
             (("x", "y"), {"else": "z"})]
    refused = [(("x",), {}), (("x",), {"else": "z"})]
    ok = all(when_call(*a, **k) is not None for a, k in legal) and all(when_call(*a, **k) is None for a, k in refused)
    check("WS", ok, "the five legal calls bind, `when(x)` and `when(x, else = z)` are refused (then required; R.1.10 (8))")


# ================================================================== WV: value-test (a `$y` test is an rx like any other)
def part_wv():
    pre = "(?P<y>\\d{4}):"
    c = "(?<=1492:)"                          # the condition (y: 1492), y the four digits just before `:`
    a = "(?:%s)" % when(c, "Columbus", "(?P=y)")
    res = modes_rx(pre + a, ["1492:Columbus", "2025:2025"], "x1492:Columbus", "1492:Columbus 2025:2025 1492:1492")
    ok_a = printed(res, {"1492:Columbus": True, "2025:2025": True}, ("1492:Columbus", 1), [("1492:Columbus", 0), ("2025:2025", 14)])
    t = "(?P=y)(?<=1492)"                     # his test `$y & (0: 1492)` written bare: CONSUMED (when-peek)
    if sab("s8"):
        b = "(?:%s)" % when(peek(t), "Columbus", "(?P=y)")
    else:
        b = "(?:%s)" % when(t, "Columbus", "(?P=y)", bare=True)
    res = modes_rx(pre + b, ["1492:Columbus", "1492:1492Columbus"], "x1492:Columbus", "1492:Columbus 2025:2025 1492:1492")
    ok_b = printed(res, {"1492:Columbus": False, "1492:1492Columbus": True}, None, [("2025:2025", 14)])
    check("WV", ok_a and ok_b, "value-test (a) the condition test, (b) his test consumed: the draft R.8's answers")


# ================================================================== W8: the 2026-11-17 definition as the special case
def part_w8():
    # KH := /(?<k>\d)(?:;(?<h>\d))*/; `KH & when((h: <5), (k: between(3, 7)))` and the else form `(k: <3)`.
    # Conditions on labels, judged at KH's end on its path: h is the LAST pass's (s16: the first's).
    def run(text_list, srch, fa, els):
        def holds(m):
            hs = re.findall(";(\\d)", m)
            h = (hs[0] if sab("s16") else hs[-1]) if hs else None
            k = int(m[0])
            c = h is not None and int(h) < 5
            # when(c, p, else = q) on conditions: (c SEQ p) | (NOT c SEQ q), q nothing required when absent
            return (c and 3 <= k <= 7) or (not c and (els is None or els(k)))

        def paths(s, i):  # KH's ends from i, priority order (greedy loop: longest first)
            m = re.match("\\d(?:;\\d)*", s[i:])
            if not m:
                return []
            e = [i + 1 + 2 * n for n in range((len(m.group(0)) - 1) // 2, -1, -1)]
            return [x for x in e if holds(s[i:x])]
        wv = [(t, len(t) in paths(t, 0), None) for t in text_list]
        return sem_modes(lambda s, i: paths(s, i), [t for t in text_list], srch, fa) if True else wv
    r1 = run(["5;1;9"], "5;1;9", "3;0;5 5;1;9", None)
    r2 = run(["5;1;9"], "1;0;9", "1;0;9", lambda k: k < 3)
    ok = printed(r1, {"5;1;9": True}, ("5;1;9", 0), [("3;0;5", 0), ("5;1;9", 6)]) and \
        printed(r2, {"5;1;9": False}, ("1;0;9", 0), None)
    # the same through the BODY: when's guarded form with condition operands, as regex (lookarounds over KH's end)
    c = "(?<=;[0-4])"
    p = "(?:(?=[3-7])(?P<K>))?"               # k in 3..7 recorded at KH's start as an empty group
    q = "(?:(?=[0-2])(?P<Q>))?"
    body1 = "%s%s\\d(?:;\\d)*(?:%s)" % (p, q, when(c, "(?(K)|(?!))"))
    body2 = "%s%s\\d(?:;\\d)*(?:%s)" % (p, q, when(c, "(?(K)|(?!))", "(?(Q)|(?!))"))
    b1 = modes_rx(body1, ["5;1;9"], "5;1;9", "3;0;5 5;1;9")
    b2 = modes_rx(body2, ["5;1;9"], "1;0;9", "1;0;9")
    okb = printed(b1, {"5;1;9": True}, ("5;1;9", 0), [("3;0;5", 0), ("5;1;9", 6)]) and printed(b2, {"5;1;9": False}, ("1;0;9", 0), None)
    check("W8", ok and okb, "rev 26's `KH & when((h: <5), (k: between(3, 7)))`: WH1 and the else form `5;1;9` FAILS, `1;0;9`@0, "
                            "by the semantic model and by when's body")


# ================================================================== RX / RB / R6: rx.repeat
def part_rx():
    n = [2, 4]
    rx = repeat("\\d", mn=n, mx=n)
    res = modes_rx(rx, ["123", "1"], "12345", "12345 6")
    ok = printed(res, {"123": True, "1": False}, ("12", 0), [("12", 0), ("34", 2)])
    pool = ["".join(p) for L in range(6) for p in __import__("itertools").product("1x", repeat=L)]
    diff = sum(1 for t in pool if (re.fullmatch(rx, t) is None) != (re.fullmatch("\\d{2,4}", t) is None))
    check("RX", ok and diff == 0, "RX5 min = n, max = n, n := [2, 4]: WHOLE `123` HOLDS; SEARCHED `12345` `12`@0; FIND-ALL "
                                  "[`12`@0, `34`@2]; WHOLE equals `\\d{2,4}` on %d of %d differing" % (diff, len(pool)))
    exact = repeat("\\d", n=n)
    ok = re.fullmatch(exact, "123") is None and all((re.fullmatch(exact, t) is None) == (re.fullmatch("\\d{2}|\\d{4}", t) is None) for t in pool)
    check("RXexact", ok, "one-argument exact `rx.repeat(rx.digit, n)`: WHOLE `123` FAILS, equal to `\\d{2}|\\d{4}`")
    check("RXnone", repeat("\\d", mn=[5], mx=[2, 3]) == "(?!)", "every combination illegal: `(?!)`")
    al = repeat("\\d", n=lift_add(n, 1))
    check("RXlift", printed(modes_rx(al, ["123"], "123456", "12345 678"), {"123": True}, ("123", 0), [("123", 0), ("678", 6)]),
          "AL2 `rx.repeat(rx.digit, n + 1)` is `\\d{3}|\\d{5}`: WHOLE `123` HOLDS; SEARCHED `123456` `123`@0; FIND-ALL [`123`@0, `678`@6]")
    line = fmt(res, "`rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4], is `(?:\\d{2,2}|\\d{2,4}|\\d{4,4})`: the copy (4,2) removed")
    check("RXdoc", in_doc(line, "library.md"), "repeat's example line: %s" % line)


def part_rb():
    n = [2, 5]
    if sab("s9"):   # one binding for every mention: (2,3), (5,6)
        rx = "(?:%s)" % "|".join("(?:\\d){%d,%d}" % (v, v + 1) for v in n)
    else:
        rx = repeat("\\d", mn=n, mx=lift_add(n, 1))
    check("RB", re.fullmatch(rx, "1234") is not None and "{5,3}" not in rx,
          "`repeat(digit, n, n + 1)`, n := [2, 5]: copies (2,3), (2,6), (5,6), (5,3) removed; WHOLE `1234` HOLDS (the cross copy)")


def part_r6():
    one = repeat("(?P<a>\\d)", mn=[1], nomax=True)
    ok1 = printed(modes_rx(one + "(?<=[0-4])", ["73", "37"], "", ""), {"73": True, "37": False}, False, None)
    m = re.fullmatch(one, "73")
    ok1 = ok1 and m is not None and m.group("a") == "3"
    inner = repeat("(?P<a>(?=[0-4])\\d)", mn=[1], nomax=True)
    res = modes_rx(inner, ["3417", "341"], "3417", "3417 82", label="a")
    ok2 = printed(res, {"3417": False, "341": True}, ("341", 0), [("341", 0), ("2", 6)]) and res[0][1][2] == "1"
    digits = repeat("\\d", mn=[1], nomax=True)
    pool = ["".join(p) for L in range(6) for p in __import__("itertools").product("1x", repeat=L)]
    ok3 = all((re.fullmatch(digits, t) is None) == (re.fullmatch("\\d+", t) is None) for t in pool)
    check("R6", ok1 and ok2 and ok3, "RX6: `rx.repeat([a = rx.digit], min = 1)` & (a: <5) WHOLE `73` HOLDS a = 3, `37` FAILS; "
                                     "inside: `3417` FAILS, `341` HOLDS a = `1`, SEARCHED `341`@0, FIND-ALL [`341`@0, `2`@6]; "
                                     "`digits` equals `\\d+`")


# ================================================================== ZV: the zero-values sub-pieces' examples
def zero_pattern():
    return "" if sab("s12") else "(?!)"       # an alternation of no members


def part_zv():
    rx = "a" + hole(zero_pattern()) + "|b"
    line = fmt(modes_rx(rx, ["a", "b"], "ab", "a b ab"), "`/a${[]}|b/` is `a(?!)|b`")
    ok = printed(modes_rx(rx, ["a", "b"], "ab", "a b ab"), {"a": False, "b": True}, ("b", 1), [("b", 2), ("b", 5)])
    check("ZVpattern", ok and in_doc(line, "core.md"), line)
    lit = "(?:a){0}" if sab("s13") else copies("(?:a){{}}", [[]])
    rx = hole(lit) + "|" + hole("b")
    res = modes_rx(rx, ["", "b"], "ab", "a b")
    line = fmt(res, "`/a{${n}}/ | /b/`, n := `[]`: the literal `/a{${n}}/` never matches")
    ok = printed(res, {"": False, "b": True}, ("b", 1), [("b", 2)])
    check("ZVcount", ok and in_doc(line, "core.md"), line)
    rx = "a" + hole("(?!)") + "|b"                 # the class position's lowering is preddoc1's PART R3 (its s3)
    res = modes_rx(rx, ["ax", "b"], "axb", "ax b")
    line = fmt(res, "`/a[${[]}x]|b/` is `a(?!)|b`")
    ok = printed(res, {"ax": False, "b": True}, ("b", 2), [("b", 3)])
    check("ZVclass", ok and in_doc(line, "core.md"), line)


# ================================================================== M3, M4: the manager's readings 3 and 4
def base_pieces(text):
    out, cur = {}, None
    for ln in text.split("\n"):
        m = re.match(r"^### .*\[(\S+)\]\s+(\S.*)$", ln)
        if m:
            cur = m.group(1)
            out[cur] = {"head": ln, "lines": []}
        elif cur and ln.startswith("## "):
            cur = None
        elif cur:
            out[cur]["lines"].append(ln)
    return out


def part_m3():
    core = doc("core.md")
    if sab("s15"):
        core = core.replace("see: lib/rx/repeat", "needs: lib/rx/repeat", 1)
    bad = [t for t, p in base_pieces(core).items() for ln in p["lines"]
           if ln.startswith("needs:") and any(x.startswith("lib/") or x.startswith("parked/") for x in ln[6:].split())]
    sees = [t for t, p in base_pieces(core).items() for ln in p["lines"] if ln.startswith("see:")]
    check("M3", not bad and len(sees) >= 3, "core needs: into the library: %s; core pieces with see: %s" % (bad or "none", sees))


PILOT = "76024ee9e"   # main's merge of the pilot (the predicate documents as preddoc1 delivered them)
MOVED = {"core/patterns/repeat": "lib/rx/repeat", "core/conditional/when": "lib/control/when",
         "core/conditional/test": "lib/control/when-test", "core/conditional/peek": "lib/control/peek"}


def statement(p):
    for ln in p["lines"]:
        if ln.strip():
            return None if re.match(r"^(needs|by|see|modes|skeleton|module|default):", ln) else ln.strip()
    return None


def part_m4():
    old = subprocess.run(["git", "-C", W, "show", "%s:docs/design/predicates.md" % PILOT], capture_output=True, text=True)
    if old.returncode != 0:
        check("M4", False, "cannot read the pilot: %s" % old.stderr.strip())
        return
    olds, news = base_pieces(old.stdout), base_pieces(doc("library.md"))
    rows, bad = [], []
    for o, n in MOVED.items():
        a, b = statement(olds[o]), statement(news[n])
        if sab("s14") and n == "lib/rx/repeat":
            b = b.replace("all counting", "every count")
        st = olds[o]["head"].split("]")[-1].strip()
        if a is not None and a != b:
            bad.append(o)
        rows.append("%s (%s): %s" % (o, st, "statement equal" if a is not None and a == b else
                                    ("no pilot statement ('?' piece)" if a is None else "CHANGED")))
    check("M4", not bad, "; ".join(rows))


# ================================================================== SL: the slug census (preddoc1's count)
def part_sl():
    draft = open(os.path.join(W, "docs", "design", "predicates_draft.md"), encoding="utf-8").read().split("\n")
    a = next(i for i, ln in enumerate(draft) if ln.startswith("### R.8 "))
    b = next(i for i, ln in enumerate(draft) if ln.startswith("### R.9 "))
    bold = set(re.findall(r"\*\*([a-z0-9]+(?:-[a-z0-9]+)+)\*\*", "\n".join(draft[a:b])))  # kebab slugs (two words or more)
    want = bold | {"group-truth", "negated-class-hole", "inner-label-read", "bare-condition-labels"}
    homed = set()
    for f in ("core_details.md", "library_details.md", "parked_details.md"):
        for ln in doc(f).split("\n"):
            if ln.startswith("slugs:"):
                homed.update(x for x in re.split(r"[\s,]+", ln[6:]) if x)
    if sab("s17"):
        homed.discard("when-default")
    miss = sorted(want - homed)
    check("SL", len(want) == 124 and not miss, "%d of %d slugs homed (R.8's %d bold kebab slugs + 4); missing: %s"
          % (len(want) - len(miss), len(want), len(bold), miss or "none"))


for name, fn in [("PE", part_pe), ("W1", part_w1), ("WT", part_wt), ("WD", part_wd), ("WN", part_wn), ("WC", part_wc),
                 ("WS", part_ws), ("WV", part_wv), ("W8", part_w8), ("RX", part_rx), ("RB", part_rb), ("R6", part_r6),
                 ("ZV", part_zv), ("M3", part_m3), ("M4", part_m4), ("SL", part_sl)]:
    part(name, fn)
print("preddoc2_model: %d checks, %d failed%s" % (len(CHECKS), len(FAILED), (": " + " ".join(FAILED)) if FAILED else ""))
sys.exit(1 if FAILED else 0)
