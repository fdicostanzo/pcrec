#!/usr/bin/env -S python3 -I
# Lane predasc (2026-11-19): the evidence for folding the owner's ruling "quantified-order: PCRE's priority order; and
# classes lowest to highest; sorting only when asked" (COND-FAMILY, its entry of that title) into the predicate
# documents. DESIGN EVIDENCE ONLY; rules nothing. STANDALONE (python3 `re`, git for the base commit's documents).
# Based on lane predloop's model (docs/dev/lanes/predloop_evidence/predloop_model.py), the class order turned round.
#
# METHOD. Nothing below is built by hand per example. Each example's EXPRESSION TEXT is parsed; each operand is
# ENUMERATED by one generic enumerator (literals, `\d`, `\w`, `[...]`, groups, alternation, bounded quantifiers
# greedy or lazy) in PCRE's priority order, a class LOWEST TO HIGHEST (ascending codepoint: for digits the value and
# the codepoint agree; for any other class it is the manager's reading of the open question class-value); the lift is
# THE NESTED LOOP over the operands' enumerations, the first operand outermost, each result appended as the next
# alternative, nothing from outside the number domain, a repeated result kept at its first occurrence. The
# alternation is run with python `re` in WHOLE, SEARCHED and FIND-ALL and the formatted line must occur VERBATIM in
# the base file.
# Controls that do not share the loop: (1) the documents at the lane's base commit 5a299d40d (read by `git show`):
# the printed lines there are compared with the loop's to list every answer that changed, and the answers this
# ruling does not govern must not change; (2) the record's own printed answers of the manager's contemporaneous run
# (asc.py: `\d + 1` bare and between `\b`); (3) the rx itself (enumerate's re-join; a class in a plain match against
# alternations of its members in shuffled orders).
#
# Run (W = the worktree; any cwd):  timeout 300 python3 -I -B W/docs/dev/lanes/predasc_evidence/predasc_model.py
# PREDASC_SABOTAGE=sN (one at a time): a deliberately wrong rule or document fact; its target check must FAIL.
#   s1  a class enumerates DESCENDING (the reversed rule)                            -> EXclassorder
#   s2  the lift's results re-sorted longest first                                   -> EXclassorder
#   s3  the SECOND operand outermost                                                 -> EXfirst
#   s4  a lazy quantifier enumerated as greedy                                       -> EXlazy
#   s5  a repeated result kept at its LAST occurrence                                -> EXfirst
#   s6  equal strings kept twice (no de-duplication)                                 -> EXeq
#   s7  `+` reads a non-numeral member (`a` as 10)                                   -> EXwplus
#   s8  arrays combine pairwise                                                      -> EXlift
#   s9  the out-of-domain member `x` gives `x` instead of nothing                    -> EXplus
#   s10 enumerate lists widest first instead of PCRE priority                        -> EXenum
#   s11 enumerate's ARRAY descending while a lift of it is ascending                 -> EXenumclass
#   s12 positions of `[ab]\d` enumerated last position outermost                     -> EXpos
#   s13 a quantifier enumerated COUNT-GROUPED (each count whole), not PCRE priority  -> EXbounded
#   s14 `left` takes the rightmost characters                                        -> EXleft
#   s15 the boundary dropped from the `\b` example (bare alternation)                -> EXbound
#   s16 the base commit's control replaced by the loop's own lines                   -> OLD
#   s17 a class member that is two characters (`10` in a "class"): order observable -> PCREORD
#   s18 the record's printed asc.py answers mis-copied (`10`@1 for the bare line)    -> RECASC
#   s19 `*` computed as `+`                                                          -> EXmul
#   s20 the INNER loop's operand enumerated descending (the outer one ascending)     -> EXtwo
#   s21 a sort name given a definition line (in memory)                              -> SORT
#   s22 a quoted rule sentence strengthened (in memory: "always" planted)            -> QUOTES
#   s23 a base file keeps "descending" (in memory)                                   -> NODESC
#   s24 the slug quantified-order missing from class-order's slugs (in memory)        -> TAGS
#   s25 `-` computed with its operands swapped (`\d - 10`)                           -> EXsub
#   s26 an alternation's choices enumerated last first                               -> EXnest
import itertools
import os
import random
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
PRED = os.path.join(W, "docs", "design", "predicates")
RECORD_PATH = os.path.join(W, "docs", "design", "plan_row_bodies", "COND-FAMILY.md")
BASE_COMMIT = "5a299d40d"
SAB = set(x for x in os.environ.get("PREDASC_SABOTAGE", "").split(",") if x)
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


def git_show(rel):
    return subprocess.run(["git", "-C", W, "show", "%s:%s" % (BASE_COMMIT, rel)], check=True,
                          capture_output=True, text=True).stdout


CORE = read(os.path.join(PRED, "core.md"))
CORED = read(os.path.join(PRED, "core_details.md"))
LIB = read(os.path.join(PRED, "library.md"))
LIBD = read(os.path.join(PRED, "library_details.md"))
RECORD = read(RECORD_PATH)
OLD_CORE = git_show("docs/design/predicates/core.md")
OLD_LIB = git_show("docs/design/predicates/library.md")
ws = lambda s: re.sub(r"\s+", " ", s)
RECORD_WS = ws(RECORD)


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


# ------------------------------------------------------------------ enumerate: PCRE priority, classes lowest to highest
DESC = [False]          # the REVERSED rule (classes descending), used only to count what the ruling moved


def enum(node):
    k = node[0]
    if k == "lit":
        yield node[1]
    elif k == "cls":
        members = sorted(node[1], reverse=DESC[0] or sab("s1"))      # LOWEST TO HIGHEST (codepoint)
        yield from members
    elif k == "alt":
        for a in (node[1][::-1] if sab("s26") else node[1]):
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


COUNT_GROUPED = [False]          # the RIVAL order inside a quantifier: every count's strings together (not PCRE's)


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
        return sorted(arr, reverse=True) if sab("s11") else arr     # the ARRAY (s11: descending array)
    if text.startswith("[") and ("," in text or '"' in text):      # an array the user writes, written order
        return [x.strip().strip('"') for x in text[1:-1].split(",")]
    return enumerate_rx(text)


CANON = re.compile(r"0|[1-9][0-9]*")


def num(s):
    if CANON.fullmatch(s):
        return int(s)
    if sab("s7") and re.fullmatch(r"[A-Za-z_]", s):
        return 10
    return None


def arith(op):
    def f(a, b):
        x, y = num(a), num(b)
        if x is None or y is None:
            if sab("s9") and op == "+" and y is not None:
                return a
            return None
        o = "+" if (sab("s19") and op == "*") else op
        if sab("s25") and op == "-":
            x, y = y, x
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


def desc_alts(expr):
    DESC[0] = True
    try:
        return evaluate(expr)
    finally:
        DESC[0] = False


# ================================================================== the examples
print("== the nested-loop lift (first operand outermost), classes LOWEST TO HIGHEST, PCRE priority within an operand")
print("population for comparisons: %d texts over `0123x`, length <= 5 (WHOLE / SEARCHED / FIND-ALL differing)" % len(POP))
NEW = {}     # expr -> the line this model prints (for OLD)

# --- core/arrays/lift (not governed by the class ruling: must not change)
e = "[2, 4] + [1, 10]"
alts = evaluate(e)
L = line(rx_of(alts), ["12", "4"], "x14", "3 12 5 14") + " (`/${%s}/` is %s)" % (e, is_text(alts))
NEW[e] = L
check("EXlift", in_doc(CORE, L) and alts == ["3", "12", "5", "14"], L)

# --- core/values/arithmetic
e = '["7", "x", "41"] + 1'
alts = evaluate(e)
L = line(rx_of(alts), ["8"], "x42 8", "8 x 42") + " (`/${%s}/` is %s: the member `x` gives nothing)" % (e, is_text(alts))
NEW[e] = L
check("EXplus", in_doc(CORE, L), L)

aw, ad = evaluate(r"\w + 1"), evaluate(r"\d + 1")
check("EXwplus", aw == ad and diff(rx_of(aw), rx_of(ad)) == (0, 0, 0),
      r"`\w + 1` = %s ; `\d + 1` = %s ; equal: %s ; %s" % (is_text(aw), is_text(ad), aw == ad, fmtd(diff(rx_of(aw), rx_of(ad)))))

# --- core/arrays/class-order: the one-class lift; reading (c): the rejected codepoint candidate's line is the loop's
e = r"\d + 1"
alts = evaluate(e)
L = line(rx_of(alts), ["10"], "x10", "10 3 11") + " (`/${%s}/` is %s)" % (e, is_text(alts))
NEW[e] = L
CAND_CODEPOINT = "`/${\\d + 1}/` SEARCHED `x10` ascending `1`@1"     # the rejected item's recorded line (core_details at base)
old_cored = git_show("docs/design/predicates/core_details.md")
check("EXclassorder", in_doc(CORE, L) and alts == [str(n) for n in range(1, 11)] and "SEARCHED `x10` `1`@1" in L
      and CAND_CODEPOINT in old_cored,
      L + " | against longest first %s" % fmtd(diff(rx_of(alts), rx_of(sorted(alts, key=lambda x: -len(x))))) +
      " | reading (c): the codepoint candidate's recorded line (`1`@1 on `x10`, rejected at %s: %s) is the loop's"
      % (BASE_COMMIT, CAND_CODEPOINT in old_cored))

# --- the owner's observation: a boundary check makes the alternation reach the whole number
e = r"\d + 1"
alts = evaluate(e)
brx = (r"\b" + rx_of(alts) + r"\b") if not sab("s15") else rx_of(alts)
LB = line(brx, ["10", "7"], "x10 10", "10 3 11") + r" (`/\b${\d + 1}\b/`)"
check("EXbound", in_doc(CORE, LB) and "SEARCHED `x10 10` `10`@4" in LB, LB)

# --- the record's printed answers of the manager's contemporaneous run (asc.py): an independent control
Lbare = line(rx_of(alts), ["10", "7"], "x10 10", "10 3 11")
REC_BARE = "WHOLE `10` HOLDS, `7` HOLDS / SEARCHED `x10 10` `1`@1 / FIND-ALL `10 3 11` [`1`@0, `3`@3, `1`@5, `1`@6]"
REC_B = "WHOLE `10` HOLDS, `7` HOLDS / SEARCHED `x10 10` `10`@4 / FIND-ALL `10 3 11` [`10`@0, `3`@3]"
if sab("s18"):
    REC_BARE = REC_BARE.replace("`1`@1", "`10`@1")
REC_LIST = "`\\d + 1` is `1|2|3|4|5|6|7|8|9|10`"
check("RECASC", REC_BARE in RECORD_WS and REC_B in RECORD_WS and REC_LIST in RECORD_WS
      and Lbare == REC_BARE and LB.startswith(REC_B) and "|".join(alts) == "1|2|3|4|5|6|7|8|9|10",
      "record bare found: %s ; record \\b found: %s ; model bare = record: %s ; model \\b = record: %s"
      % (REC_BARE in RECORD_WS, REC_B in RECORD_WS, Lbare == REC_BARE, LB.startswith(REC_B)))

# --- a subtraction: under ascending the larger result comes first
e = r"10 - \d"
alts = evaluate(e)
L = line(rx_of(alts), ["10", "7"], "x10", "10 7 3") + " (`/${%s}/` is %s)" % (e, is_text(alts))
NEW[e] = L
longest = sorted(alts, key=lambda x: -len(x))
check("EXsub", in_doc(CORE, L) and alts[0] == "10" and "`10`@1" in L,
      L + " | against longest-first %s" % fmtd(diff(rx_of(alts), rx_of(longest))))

# --- two class positions
e = r"\d + \d"
alts = evaluate(e)
L = line(rx_of(alts), ["13"], "x13", "13 4 18") + " (`/${%s}/` is `(?:0|1|..|17|18)`)" % e
NEW[e] = L
check("EXtwo", in_doc(CORE, L) and alts == [str(n) for n in range(0, 19)], L)

# --- a class under a lazy quantifier
e = r"\d{1,2}? + 1"
alts = evaluate(e)
L = line(rx_of(alts), ["100"], "x100", "100 10 9") + " (`/${%s}/` begins `(?:%s|..`)" % (e, "|".join(alts[:4]))
NEW[e] = L
check("EXlazy", in_doc(CORE, L) and alts[:3] == ["1", "2", "11"], L)

# --- the class first beside an alternation
e = r"\d + (1|9)"
alts = evaluate(e)
L = line(rx_of(alts), ["11"], "x11", "11 1 18") + " (`/${%s}/` begins `(?:%s|..`)" % (e, "|".join(alts[:4]))
NEW[e] = L
check("EXfirst", in_doc(CORE, L) and alts[:4] == ["1", "9", "2", "10"], L)

# --- the alternation first
e = r"(1|9) + \d"
alts = evaluate(e)
L = line(rx_of(alts), ["11"], "x11", "11 1 18") + " (`/${%s}/` begins `(?:%s|..`)" % (e, "|".join(alts[:4]))
NEW[e] = L
check("EXnest", in_doc(CORE, L) and alts == [str(n) for n in range(1, 19)], L)

# --- equal strings are one result
alts = evaluate(r"\d * 0")
check("EXeq", alts == ["0"] and diff(rx_of(alts), "0") == (0, 0, 0), r"`\d * 0` = %s" % alts)

# --- \d * \d
alts = evaluate(r"\d * \d")
check("EXmul", len(alts) == 37 and alts[:6] == ["0", "1", "2", "3", "4", "5"] and alts[10:15] == ["10", "12", "14", "16", "18"],
      r"`\d * \d` %d results, begins %s, then %s ; against longest-first %s" % (
          len(alts), alts[:10], alts[10:15], fmtd(diff(rx_of(alts), rx_of(sorted(alts, key=lambda x: -len(x)))))))

# --- the bounded lazy/greedy lifts (quantified-order: PCRE's priority order, RULED)
BOUND = {}
for e in (r"\d{1,3}? + \d{1,3}?", r"\d{1,3}? + \d{1,3}", r"\d{1,3} + \d{1,3}?", r"\d{1,3} + \d{1,3}"):
    alts = evaluate(e)
    BOUND[e] = line(rx_of(alts), ["123", "7"], "x123", "123 7 45") + " (`/${%s}/`)" % e
    NEW[e] = BOUND[e]
    print("   bounded %-22s first tried %s : %s" % (e, alts[:4], BOUND[e]))
COUNT_GROUPED[0] = True
cg = evaluate(r"\d{1,3}? + \d{1,3}")
COUNT_GROUPED[0] = False
lg_cg = line(rx_of(cg), ["123", "7"], "x123", "123 7 45")
print("   the RIVAL (count by count, NOT the ruled order), lazy + greedy: first tried %s : %s" % (cg[:4], lg_cg))
lg = evaluate(r"\d{1,3}? + \d{1,3}")
dcg = diff(rx_of(lg), rx_of(cg))
check("EXbounded", in_doc(CORE, BOUND[r"\d{1,3}? + \d{1,3}?"]) and in_doc(CORE, BOUND[r"\d{1,3}? + \d{1,3}"])
      and "SEARCHED `x123` `1`@1" in BOUND[r"\d{1,3}? + \d{1,3}?"] and "SEARCHED `x123` `123`@1" in BOUND[r"\d{1,3}? + \d{1,3}"]
      and lg[:3] == ["0", "100", "101"] and lg != cg,
      "lazy + lazy, lazy + greedy printed in core.md; lazy + greedy begins %s (the rival count by count %s); ruled vs"
      " rival over the population %s" % (lg[:3], cg[:3], fmtd(dcg)))

# --- lib/builtin/enumerate: the ruled example, no class: unchanged; and re-joining = the rx itself
e = r"(?:a|ab){1,2}"
alts = evaluate("enumerate(/%s/)" % e)
L = line(rx_of(alts), ["aba"], "aba", "aab aba") + " (`/${enumerate(/%s/)}/` is %s)" % (e, is_text(alts))
NEW["enumerate(/%s/)" % e] = L
TXT = [""] + ["".join(t) for n in range(1, 6) for t in itertools.product("ab", repeat=n)]
check("EXenum", in_doc(LIB, L) and diff(rx_of(alts), e, TXT) == (0, 0, 0),
      L + " | against `%s` itself %s of %d texts" % (e, fmtd(diff(rx_of(alts), e, TXT)), len(TXT)))

# --- enumerate's array of a class is ascending, so a lift of it is the class's lift
arr = operand(r"enumerate(/\d/)")
a1, a2 = evaluate(r"enumerate(/\d/) + 1"), evaluate(r"\d + 1")
L = line(rx_of(a1), ["10"], "x10", "10 3 11") + r" (`/${enumerate(/\d/) + 1}/` = `/${\d + 1}/`)"
NEW[r"enumerate(/\d/) + 1"] = L
check("EXenumclass", in_doc(LIB, L) and a1 == a2 and arr == DIGITS and "[`0`, `1`, .., `9`]" in LIB,
      "array %s ; " % arr + L)

# --- a class inside a larger rx: nested positions in text order, each class lowest to highest
arr = operand(r"enumerate(/[ab]\d/)")
if sab("s12"):
    arr = ["".join(reversed(x)) for x in itertools.product(DIGITS, ["a", "b"])]
ok = arr[:3] == ["a0", "a1", "a2"] and arr[10] == "b0" and len(arr) == 20
abc = operand("enumerate(/[abc]/)")
check("EXpos", ok and abc == ["a", "b", "c"] and "[`a0`, `a1`, .., `a9`, `b0`, .., `b9`]" in LIB
      and "[`a`, `b`, `c`]" in LIB, r"`enumerate(/[ab]\d/)` = %s ; `enumerate(/[abc]/)` = %s" % (arr, abc))

# --- lib/strings/left
e = "left(/foobar|bazqux/, 2)"
alts = evaluate(e)
L = line(rx_of(alts), ["fo", "foo"], "xba", "fo ba") + " (`%s` is `%s`)" % (e, "|".join(alts))
NEW[e] = L
e2 = r"left(/\d{1,2}?/, 2)"
alts2 = evaluate(e2)
L2 = line(rx_of(alts2), ["12"], "x12", "12 3") + " (`/${%s}/`: `\\d{1,2}?` itself)" % e2
NEW[e2] = L2
d2 = diff(rx_of(alts2), r"\d{1,2}?")
dl = diff(rx_of(alts2), rx_of(sorted(alts2, key=lambda x: -len(x))))
check("EXleft", in_doc(LIB, L) and in_doc(LIB, L2) and d2 == (0, 0, 0) and dl != (0, 0, 0),
      L + " || " + L2 + " | against `\\d{1,2}?` itself %s ; against its results longest first %s" % (fmtd(d2), fmtd(dl)))

# ================================================================== reading (a): what a run CAN show of a class's order
# In a plain match a class is ONE position taking one character: the order of its members cannot be observed. The
# control is the rx engine itself: the class written as an alternation of its members in shuffled orders.
print("== reading (a): a class's member order in a plain match (the class as an alternation, 20 shuffles each)")
rng = random.Random(20261119)
worst = (0, 0, 0)
for shape in (r"{C}", r"{C}{{1,2}}", r"{C}{{1,2}}?", r"x{C}{C}", r"(?:{C}|1){{1,3}}"):
    members = list(DIGITS) + (["10"] if sab("s17") else [])
    base = shape.format(C="(?:" + "|".join(sorted(members)) + ")")
    for _ in range(20):
        m2 = members[:]
        rng.shuffle(m2)
        d = diff(base, shape.format(C="(?:" + "|".join(m2) + ")"))
        worst = tuple(max(a, b) for a, b in zip(worst, d))
    print("   %-22s worst over 20 shuffles %s" % (shape.format(C=r"\d"), fmtd(worst)))
check("PCREORD", worst == (0, 0, 0), "no shuffle of a class's members changes a plain match: worst %s" % fmtd(worst))

# ================================================================== the base commit's documents: what changed
print("== ANSWERS CHANGED against the documents at %s (the printed lines, read by git show)" % BASE_COMMIT)


def old_line(doc, new_line):
    """The base commit's printed line for the same expression (matched by the parenthesised tail's expression)."""
    m = re.search(r"\(`(/\$\{.*?\}/|left\(.*?\))`", new_line)
    key = m.group(1)
    for ln in doc.splitlines():
        if ln.startswith("WHOLE ") and ("(`" + key + "`") in ln:
            return ln
    return None


changed, unchanged, absent = [], [], []
for e, L in NEW.items():
    doc = OLD_LIB if ("enumerate" in e or e.startswith("left")) else OLD_CORE
    o = old_line(doc, L)
    if sab("s16"):
        o = L
    if o is None:
        absent.append(e)
    elif o.split(" (`")[0] == L.split(" (`")[0] and o == L:
        unchanged.append(e)
    else:
        changed.append(e)
        print("   CHANGED %s\n      old: %s\n      new: %s" % (e, o, L))
print("   unchanged: %s" % unchanged)
print("   not printed at the base commit: %s" % absent)
NOT_GOVERNED = ["[2, 4] + [1, 10]", '["7", "x", "41"] + 1', r"enumerate(/(?:a|ab){1,2}/)", "left(/foobar|bazqux/, 2)",
                r"left(/\d{1,2}?/, 2)"]
EXPECT_CHANGED = sorted([r"\d + 1", r"10 - \d", r"\d + \d", r"\d{1,2}? + 1", r"\d + (1|9)", r"(1|9) + \d",
                         r"enumerate(/\d/) + 1", r"\d{1,3}? + \d{1,3}?", r"\d{1,3}? + \d{1,3}"])
ok = all(e in unchanged for e in NOT_GOVERNED) and sorted(changed) == EXPECT_CHANGED
# population differences, the reversed rule against the ruled one, for each lift
for e in [r"\d + 1", r"\w + 1", r"enumerate(/\d/) + 1", r"10 - \d", r"\d + \d", r"\d * \d", r"\d{1,2}? + 1",
          r"\d + (1|9)", r"(1|9) + \d", r"\d * 0", r"\d{1,3}? + \d{1,3}?", r"\d{1,3}? + \d{1,3}", r"\d{1,3} + \d{1,3}?",
          r"\d{1,3} + \d{1,3}", r"left(/\d{1,2}?/, 2)", "[2, 4] + [1, 10]"]:
    print("   ascending vs descending  %-22s %s" % (e, fmtd(diff(rx_of(evaluate(e)), rx_of(desc_alts(e))))))
check("OLD", ok, "changed %d (expected %d: %s) ; the answers not governed by the class rulings unchanged: %s"
      % (len(changed), len(EXPECT_CHANGED), sorted(changed) == EXPECT_CHANGED, all(e in unchanged for e in NOT_GOVERNED)))

# ================================================================== the documents' structure
class_order_entry = CORED[CORED.index("## core/arrays/class-order"):]
class_order_entry = class_order_entry[:class_order_entry.index("\n## ")]
slugs = re.search(r"^slugs: (.*)$", class_order_entry, re.M).group(1).split()
if sab("s24"):
    slugs = [s for s in slugs if s != "quantified-order"]
live_tags = set(re.findall(r"^### .*?\[([a-z/-]+)\]", CORE + LIB, re.M))
check("TAGS", "quantified-order" in slugs and "class-order" in slugs
      and re.search(r"\[lib/builtin/enumerate/class-value\]\s+open class-value", LIB) is not None
      and re.search(r"\[core/arrays/class-order\]\s+ruled 2026-11-19", CORE) is not None,
      "class-order slugs %s ; class-value still open: %s" % (slugs, "lib/builtin/enumerate/class-value" in live_tags))

sortpiece = LIB[LIB.index("[lib/structural/sort]"):]
sortpiece = sortpiece[:sortpiece.index("\n### ")]
if sab("s21"):
    sortpiece += "\nlsort(alts) := sort(alts, by = \"length\", order = \"desc\")\n"
check("SORT", "lengthSorted()" in sortpiece and ":=" not in sortpiece and "under-construction" in sortpiece.split("\n")[0]
      and "Need a terser sort function for common use" in sortpiece and "defined: ?" in sortpiece,
      "sort piece: lengthSorted named, his request quoted, no definition, still under construction")

# every quoted rule sentence from the ruling, as the documents print it, is verbatim in the record
QUOTES = ["quantified-order: keep pcre priority order and classes change to lowest to highest unless pcre priority order disagrees.",
          "It was to help the arithmetic common choice but if it doesn't completely then it shouldn't at all.",
          "Only solution is sorting output when needed.", "Need a terser sort function for common use.",
          "most numbers will use boundary checks to make sure they match the whole subject number",
          "classes change to lowest to highest unless pcre priority order disagrees", "keep pcre priority order"]
docs_ws = ws(CORE + CORED + LIB + LIBD)
if sab("s22"):
    docs_ws = docs_ws.replace('"keep pcre priority order"', '"always keep pcre priority order"')
    QUOTES[-1] = "always keep pcre priority order"
rec_ok = all(q in RECORD_WS for q in QUOTES)
doc_ok = all(('"%s' % q) in docs_ws or (q + '"') in docs_ws for q in QUOTES)
check("QUOTES", rec_ok and doc_ok, "record has each: %s ; documents print each quoted: %s" % (rec_ok, doc_ok))

base_text = CORE + LIB
if sab("s23"):
    base_text += "\nA class enumerates in descending class value order.\n"
hits = [ln for ln in base_text.splitlines() if re.search(r"descend", ln, re.I)]
check("NODESC", not hits, "base files (core.md, library.md) lines with 'descend': %d %s" % (len(hits), hits[:2]))

print("predasc_model: %d checks, %d failed%s" % (len(CHECKS), len(FAILED), (": " + " ".join(FAILED)) if FAILED else ""))
sys.exit(1 if FAILED else 0)
