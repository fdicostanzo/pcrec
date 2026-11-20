#!/usr/bin/env -S python3 -I
# Lane predloop (2026-11-19): the evidence for folding the owner's ruling "class-positions: nested loops, classes
# descending" (COND-FAMILY, "2026-11-19 OWNER RULING — class-positions: nested loops, classes descending") into the
# predicate documents. DESIGN EVIDENCE ONLY; rules nothing. STANDALONE (python3 `re` and the documents only).
#
# METHOD. Nothing below is built by hand per example. Each example's EXPRESSION TEXT (as the documents print it,
# `\d + (1|9)`, `[2, 4] + [1, 10]`, `enumerate(/\d/) + 1`) is parsed; each operand is ENUMERATED by one generic
# enumerator (a small regex subset: literals, `\d`, `\w`, `[...]`, groups, alternation, bounded quantifiers greedy or
# lazy) in PCRE's priority order, a class in DESCENDING class value order (the codepoint: for digits the value and the
# codepoint agree; for any other class it is the reading of the open question class-value); the lift is THE NESTED LOOP
# over the operands' enumerations, the first operand outermost, each result appended as the next alternative in loop
# order, nothing from outside the number domain, a repeated result kept at its first occurrence. The alternation is
# run with python `re` in WHOLE, SEARCHED and FIND-ALL and the formatted line must occur VERBATIM in the base file.
# Controls that do not share the loop: (1) the old rule's documented lines (the documents at the lane's base commit
# 18ca97f7e, typed in below as text), run against the loop to list what changed; (2) the rx itself for enumerate's
# re-join (`(?:a|ab){1,2}`, `\d{1,2}?`): the lift must equal PCRE's own pattern on a population; (3) the record's own
# printed answers for the ruling's witness (`10 - \d` SEARCHED `x10` `1`@1).
#
# Run (W = the worktree; any cwd):  timeout 300 python3 -I -B W/docs/dev/lanes/predloop_evidence/predloop_model.py
# PREDLOOP_SABOTAGE=sN (one at a time): a deliberately wrong rule or document fact; its target check must FAIL.
#   s1  a class enumerates ASCENDING                                                -> EXclassorder
#   s2  the lift's results re-sorted longest first (the replaced rule)               -> EXsub
#   s3  the SECOND operand outermost                                                 -> EXfirst
#   s4  a lazy quantifier enumerated as greedy                                       -> EXlazy
#   s5  a repeated result kept at its LAST occurrence                                -> EXnest
#   s6  equal strings kept twice (no de-duplication) with `\d * 0` counted           -> EXeq
#   s7  `+` reads a non-numeral member (`a` as 0)                                    -> EXwplus
#   s8  arrays combine pairwise                                                      -> EXlift
#   s9  the out-of-domain member `x` gives `x` instead of nothing                    -> EXplus
#   s10 enumerate lists widest first instead of PCRE priority                        -> EXenum
#   s11 enumerate's ARRAY ascending while a lift of it is descending                 -> EXenumclass
#   s12 positions of `[ab]\d` enumerated last position outermost                     -> EXpos
#   s13 a quantifier enumerated COUNT-GROUPED (each count whole) not PCRE priority -> EXbounded
#   s14 `left` takes the rightmost characters                                        -> EXleft
#   s15 the old rule's lists (the control of reading (b)) replaced by the loop's      -> RB
#   s16 a retired tag left live (in memory: the class-positions heading kept)        -> TAGS
#   s17 `lengthSorted` given a definition line (in memory)                           -> IDEA
#   s18 a quoted rule sentence strengthened (in memory: "always" planted)            -> QUOTES
#   s19 `*` computed as `+`                                                          -> EXmul
#   s20 the INNER loop's operand enumerated ascending (the outer one descending)    -> EXtwo
import itertools
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
RECORD_PATH = os.path.join(W, "docs", "design", "plan_row_bodies", "COND-FAMILY.md")
SAB = set(x for x in os.environ.get("PREDLOOP_SABOTAGE", "").split(",") if x)
FAILED, CHECKS = [], []


def sab(n):
    return n in SAB


def check(name, ok, detail=""):
    CHECKS.append(name)
    print("%-12s %s %s" % (name, "ok  " if ok else "FAIL", detail))
    if not ok:
        FAILED.append(name)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


CORE = read(os.path.join(PRED, "core.md"))
CORED = read(os.path.join(PRED, "core_details.md"))
LIB = read(os.path.join(PRED, "library.md"))
LIBD = read(os.path.join(PRED, "library_details.md"))
RECORD = read(RECORD_PATH)


# ------------------------------------------------------------------ a regex subset: parse
class P:
    def __init__(self, s):
        self.s, self.i = s, 0

    def peek(self):
        return self.s[self.i] if self.i < len(self.s) else None

    def take(self):
        c = self.s[self.i]
        self.i += 1
        return c


DIGITS = [chr(c) for c in range(ord("0"), ord("9") + 1)]
WORD = DIGITS + [chr(c) for c in range(ord("A"), ord("Z") + 1)] + ["_"] + [chr(c) for c in range(ord("a"), ord("z") + 1)]


def parse_alt(p):
    alts = [parse_seq(p)]
    while p.peek() == "|":
        p.take()
        alts.append(parse_seq(p))
    return ("alt", alts)


def parse_seq(p):
    items = []
    while p.peek() is not None and p.peek() not in "|)":
        items.append(parse_quant(p))
    return ("seq", items)


def parse_quant(p):
    atom = parse_atom(p)
    c = p.peek()
    if c in ("?", "{"):
        if c == "?":
            p.take()
            lo, hi = 0, 1
        else:
            m = re.match(r"\{(\d+)(?:,(\d+))?\}", p.s[p.i:])
            p.i += m.end()
            lo = int(m.group(1))
            hi = int(m.group(2)) if m.group(2) is not None else lo
        lazy = False
        if p.peek() == "?":
            p.take()
            lazy = True
        return ("rep", atom, lo, hi, lazy)
    if c in ("*", "+"):
        raise ValueError("infinite rx: enumerate's budget (under construction)")
    return atom


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
        if e == "d":
            return ("cls", list(DIGITS))
        if e == "w":
            return ("cls", list(WORD))
        return ("lit", e)
    if c == "[":
        members = []
        while p.peek() != "]":
            a = p.take()
            if a == "\\":
                a = p.take()
                if a == "d":
                    members += DIGITS
                    continue
            if p.peek() == "-" and p.s[p.i + 1] != "]":
                p.take()
                b = p.take()
                members += [chr(x) for x in range(ord(a), ord(b) + 1)]
            else:
                members.append(a)
        p.take()
        return ("cls", sorted(set(members)))
    return ("lit", c)


# ------------------------------------------------------------------ enumerate: PCRE priority, classes descending
def enum(node):
    k = node[0]
    if k == "lit":
        yield node[1]
    elif k == "cls":
        members = sorted(node[1], reverse=not sab("s1"))      # DESCENDING class value (codepoint)
        yield from members
    elif k == "alt":
        for a in node[1]:
            yield from enum(a)
    elif k == "seq":
        yield from seq(node[1], 0)
    elif k == "rep":
        _, atom, lo, hi, lazy = node
        if sab("s4"):
            lazy = False
        if COUNT_GROUPED[0] or sab("s13"):
            counts = range(lo, hi + 1) if lazy else range(hi, lo - 1, -1)
            for k in counts:
                yield from seq([atom] * k, 0)
        else:
            yield from rep(atom, lo, hi, lazy, 0)


COUNT_GROUPED = [False]          # the RIVAL order inside a quantifier: every count's strings together (not enumerate's)


def seq(items, i):
    if i == len(items):
        yield ""
        return
    for a in enum(items[i]):
        for t in seq(items, i + 1):
            yield a + t


def rep(atom, lo, hi, lazy, i):
    if i < lo:
        for a in enum(atom):
            for t in rep(atom, lo, hi, lazy, i + 1):
                yield a + t
        return
    if i >= hi:
        yield ""
        return
    if lazy:
        yield ""
    for a in enum(atom):
        for t in rep(atom, lo, hi, lazy, i + 1):
            yield a + t
    if not lazy:
        yield ""


def uniq(xs):
    if sab("s5"):
        return list(reversed(list(dict.fromkeys(reversed(xs)))))
    return list(dict.fromkeys(xs))


def enumerate_rx(src):
    p = P(src)
    node = parse_alt(p)
    assert p.i == len(src), src
    out = uniq(list(enum(node)))
    if sab("s10"):
        out = sorted(out, key=lambda x: -len(x))
    return out


# ------------------------------------------------------------------ an expression: operands, the nested loop
def operand(text):
    text = text.strip()
    m = re.fullmatch(r"enumerate\(/(.*)/\)", text)
    if m:
        arr = enumerate_rx(m.group(1))
        return sorted(arr) if sab("s11") else arr                   # the ARRAY (s11: ascending array)
    if text.startswith("[") and ("," in text or '"' in text):      # an array the user writes, written order
        return [x.strip().strip('"') for x in text[1:-1].split(",")]
    return enumerate_rx(text)


CANON = re.compile(r"0|[1-9][0-9]*")


def num(s):
    if CANON.fullmatch(s):
        return int(s)
    if sab("s7") and re.fullmatch(r"[A-Za-z_]", s):
        return 0
    return None


def arith(op):
    def f(a, b):
        x, y = num(a), num(b)
        if x is None or y is None:
            if sab("s9") and op == "+" and y is not None:
                return a
            return None
        o = "+" if (sab("s19") and op == "*") else op
        r = {"+": x + y, "-": x - y, "*": x * y, "%": (x % y) if y else None}[o]
        return None if r is None or r < 0 else str(r)
    return f


def left(s, n):
    n = int(n)
    return s[-n:] if sab("s14") else s[:n]


def lift(fn, operands):
    if sab("s20") and len(operands) == 2:
        operands = [operands[0], list(reversed(operands[1]))]
    if sab("s8"):
        combos = list(zip(*operands))
    elif sab("s3"):
        combos = [tuple(reversed(c)) for c in itertools.product(*reversed(operands))]
    else:
        combos = itertools.product(*operands)                      # first operand outermost: the nested loop
    out = [r for r in (fn(*c) for c in combos) if r is not None]
    if sab("s6"):
        return out
    out = uniq(out)
    if sab("s2"):
        out = sorted(out, key=lambda x: -len(x))
    return out


def evaluate(expr):
    """`A op B` (one binary operator written with blanks), `left(/rx/, n)`, or a bare operand."""
    m = re.fullmatch(r"left\(/(.*)/, (\d+)\)", expr)
    if m:
        return lift(left, [enumerate_rx(m.group(1)), [m.group(2)]])
    parts = re.split(r" ([-+*%]) ", expr)
    if len(parts) == 1:
        return operand(expr)
    assert len(parts) == 3, expr
    return lift(arith(parts[1]), [operand(parts[0]), operand(parts[2])])


def rx_of(alts):
    return "(?:" + "|".join(re.escape(a) for a in alts) + ")"


# ------------------------------------------------------------------ the three modes, the documents' line form
def line(rx, whole, srch, fa):
    c = re.compile(rx)
    w = ", ".join("`%s` %s" % (t, "HOLDS" if c.fullmatch(t) else "FAILS") for t in whole)
    m = c.search(srch)
    s = "`%s`@%d" % (m.group(0), m.start()) if m else "no match"
    f = ", ".join("`%s`@%d" % (x.group(0), x.start()) for x in c.finditer(fa))
    return "WHOLE %s / SEARCHED `%s` %s / FIND-ALL `%s` [%s]" % (w, srch, s, fa, f)


def is_text(alts):
    return "`(?:%s)`" % "|".join(alts)


def in_doc(doc, text):
    return text in doc


POP = [""] + ["".join(t) for n in range(1, 6) for t in itertools.product("0123x", repeat=n)]


def answers(rx, texts):
    c = re.compile(rx)
    out = []
    for t in texts:
        m = c.search(t)
        out.append((c.fullmatch(t) is not None, (m.group(0), m.start()) if m else None,
                    tuple((x.group(0), x.start()) for x in c.finditer(t))))
    return out


def diff(rx1, rx2, texts=POP):
    a, b = answers(rx1, texts), answers(rx2, texts)
    return tuple(sum(1 for x, y in zip(a, b) if x[i] != y[i]) for i in range(3))


def fmtd(d):
    return "%d / %d / %d" % d


# ================================================================== the examples
print("== the nested-loop lift (first operand outermost), classes descending, PCRE priority within an operand")
print("population for comparisons: %d texts over `0123x`, length <= 5 (WHOLE / SEARCHED / FIND-ALL differing)" % len(POP))

# --- core/arrays/lift (unchanged answers)
e = "[2, 4] + [1, 10]"
alts = evaluate(e)
L = line(rx_of(alts), ["12", "4"], "x14", "3 12 5 14") + " (`/${%s}/` is %s)" % (e, is_text(alts))
check("EXlift", in_doc(CORE, L) and alts == ["3", "12", "5", "14"], L)

# --- core/values/arithmetic
e = '["7", "x", "41"] + 1'
alts = evaluate(e)
L = line(rx_of(alts), ["8"], "x42 8", "8 x 42") + " (`/${%s}/` is %s: the member `x` gives nothing)" % (e, is_text(alts))
check("EXplus", in_doc(CORE, L), L)

aw, ad = evaluate(r"\w + 1"), evaluate(r"\d + 1")
check("EXwplus", aw == ad and diff(rx_of(aw), rx_of(ad)) == (0, 0, 0),
      r"`\w + 1` = %s ; `\d + 1` = %s ; equal: %s ; %s" % (is_text(aw), is_text(ad), aw == ad, fmtd(diff(rx_of(aw), rx_of(ad)))))

# --- core/arrays/class-order: the one-class lift
e = r"\d + 1"
alts = evaluate(e)
L = line(rx_of(alts), ["10"], "x10", "10 3 11") + " (`/${%s}/` is %s)" % (e, is_text(alts))
asc = [str(d + 1) for d in range(10)]
check("EXclassorder", in_doc(CORE, L) and alts[0] == "10",
      L + " | the ascending rival SEARCHED `x10`: %s" % line(rx_of(asc), [], "x10", "")[len("WHOLE  / "):].split(" / ")[0])

# --- the ruling's witness: a subtraction puts a shorter result first
e = r"10 - \d"
alts = evaluate(e)
L = line(rx_of(alts), ["10", "7"], "x10", "10 7 3") + " (`/${%s}/` is %s)" % (e, is_text(alts))
longest = sorted(alts, key=lambda x: -len(x))
Llong = line(rx_of(longest), ["10", "7"], "x10", "10 7 3")
REC_WITNESS = "WHOLE `10` HOLDS, `7` HOLDS / SEARCHED `x10` `1`@1 / FIND-ALL\n`10 7 3` [`1`@0, `7`@3, `3`@5]"
check("EXsub", in_doc(CORE, L) and "`1`@1" in L and "`10`@1" in Llong and REC_WITNESS in RECORD,
      L + " | the replaced longest-first: " + Llong + " | the record's printed witness found: %s" % (REC_WITNESS in RECORD))

# --- two class positions
e = r"\d + \d"
alts = evaluate(e)
L = line(rx_of(alts), ["13"], "x13", "13 4 18") + " (`/${%s}/` is `(?:18|17|..|1|0)`)" % e
check("EXtwo", in_doc(CORE, L) and alts == [str(n) for n in range(18, -1, -1)], L)

# --- a class under a lazy quantifier
e = r"\d{1,2}? + 1"
alts = evaluate(e)
L = line(rx_of(alts), ["100"], "x100", "100 10 9") + " (`/${%s}/` begins `(?:%s|..`)" % (e, "|".join(alts[:4]))
check("EXlazy", in_doc(CORE, L) and alts[:2] == ["10", "100"], L)

# --- the class first beside an alternation
e = r"\d + (1|9)"
alts = evaluate(e)
L = line(rx_of(alts), ["11"], "x11", "11 1 18") + " (`/${%s}/` begins `(?:%s|..`)" % (e, "|".join(alts[:4]))
check("EXfirst", in_doc(CORE, L) and alts[:2] == ["10", "18"], L)

# --- the alternation first (reading (d)): same answers as the documents printed before
e = r"(1|9) + \d"
alts = evaluate(e)
L = line(rx_of(alts), ["11"], "x11", "11 1 18") + " (`/${%s}/` begins `(?:%s|..`)" % (e, "|".join(alts[:4]))
OLD_NEST = "WHOLE `11` HOLDS ; SEARCHED `x11` `1`@1 ; FIND-ALL `11 1 18` [`1`@0, `1`@1, `1`@3, `1`@5, `8`@6]"  # predspec291 PART CO
old_nest_alts = ["10"] + [str(n) for n in range(1, 10)] + [str(n) for n in range(11, 19)]      # predspec291's printed list
dn = diff(rx_of(alts), rx_of(old_nest_alts))
check("EXnest", in_doc(CORE, L) and dn == (0, 0, 0),
      L + " | against the old nested-longest list (predspec291 PART CO) %s" % fmtd(dn))

# --- equal strings are one result (reading (d))
alts = evaluate(r"\d * 0")
check("EXeq", alts == ["0"] and diff(rx_of(alts), "0") == (0, 0, 0), r"`\d * 0` = %s" % alts)

# --- \d * \d against longest-first (reading (b))
alts = evaluate(r"\d * \d")
check("EXmul", len(alts) == 37 and alts[0] == "81" and diff(rx_of(alts), rx_of(sorted(alts, key=lambda x: -len(x)))) == (0, 0, 0),
      r"`\d * \d` %d results, begins %s ; against longest-first %s" % (len(alts), alts[:6],
                                                                       fmtd(diff(rx_of(alts), rx_of(sorted(alts, key=lambda x: -len(x)))))))

# --- reading (c): the bounded lazy/greedy lifts
BOUND = {}
for e in (r"\d{1,3}? + \d{1,3}?", r"\d{1,3}? + \d{1,3}", r"\d{1,3} + \d{1,3}?", r"\d{1,3} + \d{1,3}"):
    alts = evaluate(e)
    BOUND[e] = line(rx_of(alts), ["123", "7"], "x123", "123 7 45") + " (`/${%s}/`)" % e
    print("   bounded %-22s first tried %s : %s" % (e, alts[:4], BOUND[e]))
ll, lg = BOUND[r"\d{1,3}? + \d{1,3}?"], BOUND[r"\d{1,3}? + \d{1,3}"]
COUNT_GROUPED[0] = True
cg = evaluate(r"\d{1,3}? + \d{1,3}")
COUNT_GROUPED[0] = False
lg_cg = line(rx_of(cg), ["123", "7"], "x123", "123 7 45")
print("   the RIVAL, a quantifier count-grouped (not enumerate's priority order), lazy + greedy: first tried %s : %s"
      % (cg[:4], lg_cg))
check("EXbounded", "SEARCHED `x123` `12`@1" in ll and "SEARCHED `x123` `12`@1" in lg and "SEARCHED `x123` `123`@1" in lg_cg
      and in_doc(CORE, ll) and in_doc(CORE, lg),
      "lazy + lazy: %s || lazy + greedy: %s || count-grouped rival lazy + greedy: %s" % (ll, lg, lg_cg))

# --- lib/builtin/enumerate: the ruled example, no class: unchanged; and re-joining = the rx itself
e = r"(?:a|ab){1,2}"
alts = evaluate("enumerate(/%s/)" % e)
L = line(rx_of(alts), ["aba"], "aba", "aab aba") + " (`/${enumerate(/%s/)}/` is %s)" % (e, is_text(alts))
TXT = [""] + ["".join(t) for n in range(1, 6) for t in itertools.product("ab", repeat=n)]
check("EXenum", in_doc(LIB, L) and diff(rx_of(alts), e, TXT) == (0, 0, 0),
      L + " | against `%s` itself %s of %d texts" % (e, fmtd(diff(rx_of(alts), e, TXT)), len(TXT)))

# --- enumerate's array of a class is descending, so a lift of it is the class's lift
arr = operand(r"enumerate(/\d/)")
a1, a2 = evaluate(r"enumerate(/\d/) + 1"), evaluate(r"\d + 1")
L = line(rx_of(a1), ["10"], "x10", "10 3 11") + r" (`/${enumerate(/\d/) + 1}/` = `/${\d + 1}/`)"
check("EXenumclass", in_doc(LIB, L) and a1 == a2 and arr[0] == "9",
      "array %s ; " % arr + L)

# --- reading (e): a class inside a larger rx: nested positions in text order, each class descending
arr = operand(r"enumerate(/[ab]\d/)")
if sab("s12"):
    arr = ["".join(reversed(x)) for x in itertools.product(DIGITS[::-1], ["b", "a"])]
ok = arr[:3] == ["b9", "b8", "b7"] and arr[10] == "a9" and len(arr) == 20
abc = operand("enumerate(/[abc]/)")
check("EXpos", ok and abc == ["c", "b", "a"] and "[`b9`, `b8`, .., `b0`, `a9`, .., `a0`]" in LIB
      and "[`c`, `b`, `a`]" in LIB, r"`enumerate(/[ab]\d/)` = %s ; `enumerate(/[abc]/)` = %s" % (arr, abc))

# --- lib/strings/left: the ruled example unchanged; a lazy class through left keeps PCRE's own order
e = "left(/foobar|bazqux/, 2)"
alts = evaluate(e)
L = line(rx_of(alts), ["fo", "foo"], "xba", "fo ba") + " (`%s` is `%s`)" % (e, "|".join(alts))
e2 = r"left(/\d{1,2}?/, 2)"
alts2 = evaluate(e2)
L2 = line(rx_of(alts2), ["12"], "x12", "12 3") + " (`/${%s}/`: `\\d{1,2}?` itself)" % e2
d2 = diff(rx_of(alts2), r"\d{1,2}?")
dl = diff(rx_of(alts2), rx_of(sorted(alts2, key=lambda x: -len(x))))
check("EXleft", in_doc(LIB, L) and in_doc(LIB, L2) and d2 == (0, 0, 0) and dl != (0, 0, 0),
      L + " || " + L2 + " | against `\\d{1,2}?` itself %s ; against its results longest first %s" % (fmtd(d2), fmtd(dl)))

# ================================================================== reading (b): every lift example, loop vs longest-first
print("== reading (b): the loop against the old rule (class-order: longest; class-positions' candidates), the population above")
# the OLD rule (class-order: longest, and the open class-positions candidates as the documents at 18ca97f7e printed
# them), typed from those documents' descriptions; a control that does not share the loop.
D_ASC = list(range(10))
by_len = lambda xs: sorted(uniq(xs), key=lambda x: -len(x))
OLD = {
    r"\d + 1": ("class-order (ruled then)", by_len([str(d + 1) for d in D_ASC])),
    r"\w + 1": (r"arithmetic reading, = `\d + 1`", by_len([str(d + 1) for d in D_ASC])),
    r"enumerate(/\d/) + 1": ("class-index (a)", by_len([str(d + 1) for d in D_ASC])),
    r"\d * 0": ("class-order reading: one result", ["0"]),
    r"(1|9) + \d": ("class-order reading: nesting", uniq(by_len([str(1 + d) for d in D_ASC]) + by_len([str(9 + d) for d in D_ASC]))),
    r"10 - \d": ("class-order (ruled then), not printed", by_len([str(10 - d) for d in D_ASC])),
    r"\d + \d": ("class-positions C1 (open)", by_len([str(a + b) for a in D_ASC for b in D_ASC])),
    r"\d * \d": ("class-positions C1's rule (open)", by_len([str(a * b) for a in D_ASC for b in D_ASC])),
    r"\d + (1|9)": ("class-positions A (open)", uniq(by_len([str(d + 1) for d in D_ASC]) + by_len([str(d + 9) for d in D_ASC]))),
    r"\d{1,2}? + 1": ("class-positions Q1 (open)", uniq(by_len([str(d + 1) for d in D_ASC]) + by_len([str(n + 1) for n in range(10, 100)]))),
    "[2, 4] + [1, 10]": ("array-lift (ruled)", ["3", "12", "5", "14"]),
}
rb = {}
for e, (src, old) in OLD.items():
    alts = evaluate(e)
    if sab("s15"):
        old = alts
    rb[e] = diff(rx_of(alts), rx_of(old))
    print("   %-22s against %-38s %s" % (e, src, fmtd(rb[e])))
nonzero = sorted(e for e in rb if rb[e] != (0, 0, 0))
check("RB", nonzero == sorted([r"10 - \d", r"\d + (1|9)", r"\d{1,2}? + 1"]),
      "differ from the old rule: %s (the ruling's witness; the open candidates A and Q1); every other 0 / 0 / 0" % nonzero)

# ================================================================== the documents' structure
core_tags = re.findall(r"^### .*?\[([a-z/-]+)\]", CORE, re.M)
lib_tags = re.findall(r"^### .*?\[([a-z/-]+)\]", LIB, re.M)
live = set(core_tags + lib_tags)
if sab("s16"):
    live.add("core/arrays/class-positions")
retired = ["core/arrays/class-positions", "lib/builtin/enumerate/class-index", "core/arrays/class-index"]
was_ok = all(re.search(r"^was: %s \(" % re.escape(t), CORED + LIBD, re.M) for t in retired)
check("TAGS", not (live & set(retired)) and was_ok and "lib/builtin/enumerate/class-value" in live
      and re.search(r"\[lib/builtin/enumerate/class-value\]\s+open class-value", LIB) is not None,
      "retired tags live: %s ; each named by a was: line: %s ; class-value open: %s"
      % (sorted(live & set(retired)), was_ok, "lib/builtin/enumerate/class-value" in live))

sortpiece = LIB[LIB.index("[lib/structural/sort]"):]
sortpiece = sortpiece[:sortpiece.index("\n### ")]
if sab("s17"):
    sortpiece += "\nlengthSorted(alts) := sort(alts, by = \"length\", order = \"desc\")\n"
check("IDEA", "lengthSorted()" in sortpiece and ":=" not in sortpiece and "under-construction" in sortpiece.split("\n")[0],
      "lengthSorted named on lib/structural/sort, no definition, the piece still under construction")

# every quoted rule sentence from the ruling, as the documents print it, is verbatim in the record
QUOTES = ["descending class value order", "lazy/greedy loops start\nshortest/ longest respectively",
          "as though this was against fn() and not +", "Perhaps then we need a lengthSorted() transform",
          "class-positions: nested loops, classes descending"]
DOCQ = ['"descending class value order"', '"lazy/greedy loops start shortest/ longest respectively"',
        '"as though this was against fn() and not +"', '"Perhaps then we need a lengthSorted() transform."',
        '"class-positions: nested loops, classes descending"']
docs_all = CORE + CORED + LIB + LIBD
if sab("s18"):
    docs_all = docs_all.replace('"descending class value order"', '"always descending class value order"')
    DOCQ[0] = '"always descending class value order"'
rec_ok = all(q in RECORD for q in QUOTES[:1] + QUOTES[2:]) and "lazy/greedy loops start\nshortest/ longest respectively" in RECORD
doc_ok = all(q in docs_all for q in DOCQ)
strip = lambda q: q.strip('"').rstrip(".")
verb_ok = all(strip(q).replace("start shortest", "start\nshortest") in RECORD or strip(q) in RECORD for q in DOCQ)
check("QUOTES", rec_ok and doc_ok and verb_ok, "record has each: %s ; documents print each: %s ; each verbatim: %s"
      % (rec_ok, doc_ok, verb_ok))

print("predloop_model: %d checks, %d failed%s" % (len(CHECKS), len(FAILED), (": " + " ".join(FAILED)) if FAILED else ""))
sys.exit(1 if FAILED else 0)
