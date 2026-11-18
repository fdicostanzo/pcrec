#!/usr/bin/env python3
# Lane predspec251 (2026-11-18): the evidence of docs/design/predicates_draft.md REVISION 25.1 (review r43's fixes).
# DESIGN EVIDENCE ONLY; rules nothing. Every answer-level witness of review r43 (groups A, B, C, D, SIMULATE-4,
# SIMULATE-7) re-run here, and group J's evidence repairs (a product-order sabotage row with a witness that can tell
# the orders apart; a compile check of the JOINED copies; checks on the parse rule; the `x + y` line labelled a reading).
#
# HOW: lane predspec25's engine (../predspec25_evidence/predspec25_model.py, never edited) is LOADED IN MEMORY: its
# text up to its first print (which itself loads predspec244's engine: the parser, the path enumerator with the one
# label rule, the mode helpers; then the libpcre2 helpers, the rx-module expander, the instantiator, the numbering).
# On top: the r43 witnesses, each against a control that shares no construction with what it checks:
#   - libpcre2-8 (installed; through ../rxmodel_evidence/pcre2h.py, run, never read: D181) on HAND-WRITTEN regex;
#   - the one-rule engine (rule 244) where a label rule is the subject;
#   - Python `re` as an intent oracle.
#
# Run (W = the worktree; from $PCREC_TMPDIR/scratch/predspec251; one process, seconds):
#   timeout 900 python3 -I -B W/docs/dev/lanes/predspec251_evidence/predspec251_model.py > fwd.out
#   PREDSPEC251_SABOTAGE=1   deliberately wrong rules (the checks must fail):
#     s1 the cartesian product FIRST HOLE FASTEST (the draft's reading is first slowest);
#     s2 copies differing in a GROUP NAME joined by branch reset `(?|..)` (rev 25's table) instead of a plain
#        alternation with the groups renumbered (the draft's reading in rev 25.1);
#     s3 the parse rule WITHOUT the record's clause "the sequence mark is explicit" (a sequence mark may begin an
#        operand, so `X* SEQ Y` reads `*` as binary);
#     s4 predspec25's operator-ORDER sabotage (`|` tighter than the sequence operator, a postfix binding the whole
#        chain) on PART J's parser: rev 25's RX9 printed "PARSE FAILED" there with no check failing.
#   PREDSPEC251_SABOTAGE=1 switches all four; =s1 (or s2, s3, s4, or a comma list) one at a time. predspec25's own
#   sabotage (its PREDSPEC25_SABOTAGE) is not switched here: it is the premise run of predspec25's engine.
import os, sys, re, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
SRC25 = os.path.join(os.path.dirname(HERE), "predspec25_evidence", "predspec25_model.py")
_sv = os.environ.get("PREDSPEC251_SABOTAGE", "")
SABS = {"s1", "s2", "s3", "s4"} if _sv == "1" else set(x for x in _sv.split(",") if x)
SAB = bool(SABS)
os.environ.pop("PREDSPEC25_SABOTAGE", None)    # predspec25's own sabotage is ITS switch, run in the premise
_src = open(SRC25).read()
_cut = _src.index('print("predspec25 engine')
E = {"__file__": SRC25, "__name__": "predspec25_defs"}
exec(compile(_src[:_cut], SRC25, "exec"), E)
(P, mk, W_, S_, F_, fmt3, strings, num, lt, View, LRx, pW, pS, pF, pD3, prow, erow, compiles, Exp, TypeErr, tokens,
 instantiate, PRULE) = (E[k] for k in ("P", "mk", "W_", "S_", "F_", "fmt3", "strings", "num", "lt", "View", "LRx", "pW",
 "pS", "pF", "pD3", "prow", "erow", "compiles", "Exp", "TypeErr", "tokens", "instantiate", "PRULE"))
if "s3" in SABS:   # s3: the clause dropped: a sequence mark is a word, so it can begin an operand
    E["starts_operand"] = lambda t: t is not None and (t[0] == '"' or t in ("[", "(") or re.match(r"[A-Za-z_]", t))

CHECKS = []
def check(name, ok): CHECKS.append((name, bool(ok))); return "OK" if ok else "FAILED"
def eD3(p1, p2, pool, keys=()):
    """two ENGINE programs: texts whose reported row (stretch + the named labels) differs per mode"""
    out, first = [], None
    for mode in "WSF":
        n = 0
        for s in pool:
            if erow(p1, s, mode, keys) != erow(p2, s, mode, keys):
                n += 1; first = first or (mode, s)
        out.append(n)
    return (out, first, len(pool))
def show3(lr, w, s_, f_, keys=()):
    return "WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (w, pW(lr, w, keys), s_, pS(lr, s_, keys), f_, pF(lr, f_, keys))

print("predspec251 evidence over predspec25's engine (loaded in memory); libpcre2-8 %s%s" % (P.version(), " ; SABOTAGE %s" % ",".join(sorted(SABS)) if SAB else ""))
print()

# ======================================================================================================== PART A
print("== PART A (review r43 group A, owner question number-names): what a NUMBER names on a composed pattern.")
print("   A condition that reads an unset label FAILS here (the draft's unset rule, R.1.3). libpcre2, hand-written regex.")
# A1 over `|`: A := /(\d)x/, B := /(\d)y/, (A | B) & (1: <5)
c5 = lambda g: (lambda x: lt(5)(x.get(g)))
dist = LRx(r'(?:(?<g1>\d)x(?C"a")|(?<g2>\d)y(?C"b"))', {"a": c5("g1"), "b": c5("g2")})
rda = LRx(r'(?:(?<g1>\d)x|(?<g2>\d)y)(?C"a")', {"a": c5("g1")})
rdc = LRx(r'(?:(?<g1>\d)x|(?<g2>\d)y)(?C"a")', {"a": c5("g2")})
rows = {}
for nm, lr in (("DISTRIBUTED over `|` (R.1.4's law: `A & c | B & c`, each branch its own group 1)", dist),
               ("(a) 1 = A's group (the written-out numbering)", rda), ("(c) 1 = B's group (the nearest literal to the left)", rdc)):
    rows[nm[:3]] = (pW(lr, "3x"), pW(lr, "3y"), pS(lr, "7x 3y 3x"), pF(lr, "7x 3y 3x"))
    print("A1 `(A | B) & (1: <5)`, A := `/(\\d)x/`, B := `/(\\d)y/`, %s: WHOLE `3x` %s, `3y` %s ; SEARCHED `7x 3y 3x` %s ; FIND-ALL `7x 3y 3x` %s" % ((nm,) + rows[nm[:3]]))
print("A1   the distribution law against both readings of a number: %s" % check("A1 over | no reading keeps the law",
      rows["DIS"] == ("HOLDS", "HOLDS", "`3y`@3", "[`3y`@3, `3x`@6]") and rows["(a)"][1] == "FAILS" and rows["(c)"][0] == "FAILS"))
# A2 through a hole: literal /(\d),(\d)/ & (1: <5) vs /${A},(\d)/, A := /(\d)/, the hole keeping its own numbering
lit2 = LRx(r'(?<g1>\d),(?<g2>\d)(?C"a")', {"a": c5("g1")})
hol2 = LRx(r'(?:(?<a1>\d)),(?<g1>\d)(?C"a")', {"a": c5("g1")})
r_l = (pW(lit2, "3,7"), pW(lit2, "7,3"), pS(lit2, "7,3 3,7"), pF(lit2, "7,3 3,7"))
r_h = (pW(hol2, "3,7"), pW(hol2, "7,3"), pS(hol2, "7,3 3,7"), pF(hol2, "7,3 3,7"))
print("A2 the literal `/(\\d),(\\d)/ & (1: <5)`: WHOLE `3,7` %s, `7,3` %s ; SEARCHED `7,3 3,7` %s ; FIND-ALL `7,3 3,7` %s" % r_l)
print("A2 `/${A},(\\d)/ & (1: <5)`, A := `/(\\d)/`, the hole keeping its own numbering (1 = the outer literal's group): WHOLE `3,7` %s, `7,3` %s ; SEARCHED `7,3 3,7` %s ; FIND-ALL `7,3 3,7` %s" % r_h)
print("A2   composed = literal fails for numbers through a hole: %s" % check("A2 hole numbering differs from the literal",
      r_l[:2] == ("HOLDS", "FAILS") and r_h[:2] == ("FAILS", "HOLDS")))
# A3 name and number of one label across `&` (by construction: the two readings, one an answer, one an error)
rp = mk(r"\d(?<h>\d)")
qn = mk(r'(?<h>\d)\d(?C"amp")', {"amp": lambda v: rp.whole(v.s[v.start:v.pos])[0] and lt(2)(rp.whole(v.s[v.start:v.pos])[1]["h"])})
res = (W_(qn, "12"), W_(qn, "21"), S_(qn, "21 12"), F_(qn, "12 21 10"))
print("A3 `A & B & (1: <2)`, A := `/(?<h>\\d)\\d/`, B := `/\\d(?<h>\\d)/`: the manager's consequence (1 = B's group h, not subject to the")
print("A3   ambiguous-reference error): WHOLE `12` %s, `21` %s ; SEARCHED `21 12` %s ; FIND-ALL `12 21 10` %s ; name = number (TWO NAMES OF" % res)
print("A3   ONE LABEL) with label-flow (4): `1` is h, which both sides surface: the AMBIGUOUS-REFERENCE compile error (no answer) ; %s" % check(
      "A3 consequence answers", res == ("FAILS", "HOLDS", "`21`@0", "[`21`@3, `10`@6]")))
print()

# ======================================================================================================== PART B
print("== PART B (group B, owner question hole-in-filter): an `&` operand stays a filter role (both sides; 'an `&` operand').")
# B1 /x${/^a/ & /(?s).*/}/: both operands filter roles over the text the hole takes (row 2, §0.1 L71) vs a splice
fil = LRx(r'x(?<t>[\s\S]*)(?C"f")', {"f": lambda c: re.fullmatch(r"a", c.get("t")) is not None and re.fullmatch(r"(?s).*", c.get("t")) is not None})
spl = LRx(r"x(?:(?:^a))(?:(?s).*)")
b_f = (pW(fil, "xa"), pS(fil, "zxa"), pF(fil, "xa xa xb"))
b_s = (pW(spl, "xa"), pS(spl, "zxa"), pF(spl, "xa xa xb"))
print("B1 `/x${/^a/ & /(?s).*/}/`, both `&` operands FILTER ROLES over the text the hole takes (`^` = that text's start; the draft's")
print("B1   row 2 and §0.1 L71, kept): WHOLE `xa` %s ; SEARCHED `zxa` %s ; FIND-ALL `xa xa xb` %s" % b_f)
print("B1 the same with the left operand SPLICED as a non-filter (libpcre2 `x(?:^a)(?:(?s).*)`): WHOLE `xa` %s ; SEARCHED `zxa` %s ; FIND-ALL `xa xa xb` %s ; %s" % (
      b_s + (check("B1 filter reading matches 0-2, splice never", b_f[0] == "HOLDS" and b_f[2] == "[`xa`@0, `xa`@3]" and b_s == ("FAILS", "FAILS", "[]")),)))
# B2 the residual: /\d+/ & /${num}/, num := /\b\d+\b/ (a hole carrying an edge assertion inside a filter operand)
WB = P.Pcre(r'\b\d+\b(?C"e")', {"e": lambda c: c.pos == WB_END[0]})
WB_END = [0]
def crossing(c):
    a, b = c.span("s"); WB_END[0] = b
    return WB.match(c.subject, a, P.PCRE2_ANCHORED) is not None
cro = LRx(r'(?<s>\d+)(?C"f")', {"f": crossing})
alone = LRx(r'(?<s>\d+)(?C"f")', {"f": lambda c: re.fullmatch(r"\b\d+\b", c.get("s")) is not None})
r_c = (pW(cro, "12"), pS(cro, "a12 34"), pF(cro, "12 a34 56"))
r_a = (pW(alone, "12"), pS(alone, "a12 34"), pF(alone, "12 a34 56"))
print("B2 `/\\d+/ & /${num}/`, num := `/\\b\\d+\\b/`: (i) THE DRAFT'S READING, the operand classified AFTER expansion: the operand-context")
print("B2   compile ERROR, as `/\\d+/ & num` (no answer in any mode)")
print("B2   (ii) the assertion CROSSES the border (hole-reading's rule carried into the operand): WHOLE `12` %s ; SEARCHED `a12 34` %s ; FIND-ALL `12 a34 56` %s" % r_c)
print("B2   (iii) the operand over the stretch's own text (the string-set reading without its error): WHOLE `12` %s ; SEARCHED `a12 34` %s ; FIND-ALL `12 a34 56` %s ; %s" % (
      r_a + (check("B2 crossing and stretch-alone differ", r_c[1] == "`34`@4" and r_a[1] == "`12`@1" and r_c[2] == "[`12`@0, `56`@7]" and r_a[2] == "[`12`@0, `34`@4, `56`@7]"),)))
print()

# ======================================================================================================== PART C
print("== PART C (group C, owner question hit-carry): pass-start-read at two depths, and inside an `occurrences` argument.")
def ge_or_unset(get):
    h, n = get("h"), get("n")
    return h is None or (num(n) and num(h) and int(n) >= int(h))
TWO = r'(?:(?:(?=(?<n>\d))(?C"c")(?<h>\d);)*,)*'
e2d = mk(TWO, {"c": lambda v: ge_or_unset(v.lab)}, PRULE)
l2d = LRx(TWO, {"c": lambda x: ge_or_unset(x.get)})
def items_sorted(t):
    its = re.findall(r"(\d);", t); return all(a <= b for a, b in zip(its, its[1:]))
for t in ("7;,3;,", "3;4;,1;2;,", "3;,7;,", "7;3;,"):
    print("C1 `/(?:(?:(?=(?<n>\\d))${c}(?<h>\\d);)*,)*/`, c := 'h unset or n >= h', `%s`: engine (the one rule) WHOLE %s, SEARCHED %s ; libpcre2 WHOLE %s, SEARCHED %s ; intent 'items non-decreasing' %s" % (
        t, W_(e2d, t), S_(e2d, t), pW(l2d, t), pS(l2d, t), items_sorted(t)))
print("C1   at two depths the one rule and PCRE's capture part (entering the inner loop resets h): %s" % check("C1 two depths split",
      W_(e2d, "7;,3;,") == "HOLDS" and pW(l2d, "7;,3;,") == "FAILS" and W_(e2d, "3;,7;,") == pW(l2d, "3;,7;,") == "HOLDS"))
OA = r'(?:.*?(?C"c")(?<h>\d)){2,}.*'
OB = r'(?:.*?(?<h>\d)){2,}.*'
cA = {"c": lambda v: not (num(v.lab("h")) and int(v.lab("h")) >= 5)}
ea, eb = mk(OA, cA, PRULE), mk(OB)
la = LRx(OA, {"c": lambda x: not (num(x.get("h")) and int(x.get("h")) >= 5)})
POOL = strings("37x", 5)
dA = eD3(ea, eb, POOL, ("h",)); dS = eD3(ea, eb, POOL, ())
dL = sum(1 for s in POOL for m in "WSF" if erow(ea, s, m, ("h",)) != prow(la, s, m, ("h",)))
print("C2 `occurrences(/${c}(?<h>\\d)/, min = 2)`, c := NOT (h: >= 5), one-pattern model `/%s/` (R.1.7's text: before its group the" % OA)
print("C2   condition reads the PREVIOUS hit's h) vs the own-hit reading (R.1.9, hits-pass: c always holds before the group, `/%s/`):" % OB)
print("C2   WHOLE `73` %s / %s ; SEARCHED `73` %s / %s ; FIND-ALL `73 33` %s / %s" % (W_(ea, "73"), W_(eb, "73", ("h",)), S_(ea, "73"), S_(eb, "73", ("h",)), F_(ea, "73 33"), F_(eb, "73 33")))
print("C2   over %d texts (alphabet `37x`, length <= 5): stretch only %s ; with label h %s ; engine (A) vs libpcre2 (A): %d rows differ ; %s" % (
    len(POOL), fmt3(dS), fmt3(dA), dL, check("C2 hit-carry decides answers (WHOLE 84, SEARCHED 84 by stretch and 134 with labels)", dS[0][:2] == [84, 84] and dA[0][1] == 134)))
check("C2 engine = libpcre2", dL == 0)
print()

# ======================================================================================================== PART D
print("== PART D (group D, owner question product-order): the cartesian product's order, legality, the removal unit, the join.")
def product(holes, fastest=False):
    if not fastest: return list(itertools.product(*holes))
    return [tuple(reversed(c)) for c in itertools.product(*reversed(holes))]
FAST = "s1" in SABS   # s1
def inst(template, holes, name_join=False, fastest=None):
    """the draft's reading (rev 25.1): one copy per combination, first hole SLOWEST; illegal copies removed (legality:
    libpcre2 compiles the COPY); copies joined by branch reset, EXCEPT copies differing in a group name: a plain
    alternation, groups renumbered. Sabotage s1: first hole fastest; s2: the name join by branch reset."""
    fastest = FAST if fastest is None else fastest
    keep = [template.format(*c) for c in product(holes, fastest) if compiles(template.format(*c)) is None]
    if not keep: return "(?!)"
    if len(keep) == 1: return "(?:%s)" % keep[0]
    return ("(?:" if name_join and "s2" not in SABS else "(?|") + "|".join(keep) + ")"
XY = inst(r"(?<x>\d{{{0}}})(?<y>\d{{{1}}})", [["1", "2"], ["1", "2"]])
XYf = inst(r"(?<x>\d{{{0}}})(?<y>\d{{{1}}})", [["1", "2"], ["1", "2"]], fastest=True)
XYs = inst(r"(?<x>\d{{{0}}})(?<y>\d{{{1}}})", [["1", "2"], ["1", "2"]], fastest=False)
lx = LRx(XY)
print("D1 `/(?<x>\\d{${a}})(?<y>\\d{${b}})/`, a, b := [1, 2], the draft's order (first hole slowest) -> `/%s/`:" % XY)
print("D1   %s" % show3(lx, "123", "a123", "123 45 6789", ("x", "y")))
print("D1   first slowest WHOLE `123` %s ; first fastest WHOLE `123` %s" % (pW(LRx(XYs), "123", ("x", "y")), pW(LRx(XYf), "123", ("x", "y"))))
d = pD3(LRx(XYs), LRx(XYf), strings("12x", 5), ("x", "y"))
print("D1   slowest vs fastest, labels x, y: %s ; %s" % (fmt3(d), check("D1 product order (the discriminating witness)", pW(lx, "123", ("x", "y")) == "HOLDS x = `1`, y = `23`")))
# D2 the draft's old witness cannot tell the orders apart: the lengths tried at 0, every length rejected
def tried(pat, s):
    seen = []
    P.Pcre(pat + '(?C"e")', {"e": lambda c: seen.append(len(c.get("r"))) or False}).match(s, 0, P.PCRE2_ANCHORED); return seen
def order_pat(fastest):
    combos = [c for c in product([["2", "3", "4"], ["2", "3", "4"]], fastest) if int(c[0]) <= int(c[1])]
    return "(?|" + "|".join(r"(?<r>\d{%s,%s})" % c for c in combos) + ")"
ts, tf = tried(order_pat(False), "123456"), tried(order_pat(True), "123456")
fo = lambda xs: [x for i, x in enumerate(xs) if x not in xs[:i]]
print("D2 rev 25's witness `[r = repeat(rx.digit, n, n)] & (r: length in L)`, n := [2, 3, 4], every length rejected, lengths tried at 0 of `123456`:")
print("D2   slowest %s ; fastest %s ; first occurrence of each length %s / %s: a length test cannot tell the orders apart ; %s" % (
    ts, tf, fo(ts), fo(tf), check("D2 old witness blind", ts != tf and fo(ts) == fo(tf))))
# D3 legality: what libpcre2 refuses among the table's rows
for pat, why in ((r"(?|(?<a>\d)|(?<b>\d))", "the GROUP NAME row's branch-reset join"), (r"(?J)(?|(?<a>\d)|(?<b>\d))", "the same under (?J)"),
                 (r"(?:(?<a>\d)|(?<b>\d))", "the name copies joined by a plain alternation, renumbered (rev 25.1's reading)"),
                 (r"(?<h>\d)(?<h>\d)", "a duplicate-name copy (R.1.7 makes two groups of one name legal)"),
                 (r"(?<=(?:\d))x", "PATTERN row, one member `\\d` in a lookbehind"), (r"(?<=(?:\d+))x", "PATTERN row, one member `\\d+` in a lookbehind"),
                 (r"(?<=(?:\d|\d+))x", "PATTERN row, members [`\\d`, `\\d+`] as ONE inner alternation"), (r"a|\d{5,2}", "COUNT row, min above max")):
    print("D3 `%s` (%s): libpcre2 %s" % (pat, why, "compiles" if compiles(pat) is None else "REFUSED: " + compiles(pat)))
check("D3 legality facts", compiles(r"(?|(?<a>\d)|(?<b>\d))") and compiles(r"(?<h>\d)(?<h>\d)") and compiles(r"(?<=(?:\d|\d+))x")
      and compiles(r"(?<=(?:\d))x") is None and compiles(r"(?:(?<a>\d)|(?<b>\d))") is None)
# D4 the removal unit: the whole literal's copy, or the hole's construct
la_, lb_ = LRx("(?!)"), LRx(r"a|(?:(?!))")
print("D4 `/a|\\d{${m},${M}}/`, m := [5], M := [2]: the LITERAL's copy removed (the draft's unit) -> `(?!)`: %s" % show3(la_, "a", "xa", "a xa"))
print("D4   the hole's construct removed (the library spelling through `repeat`) -> `a|(?:(?!))`: %s ; %s" % (show3(lb_, "a", "xa", "a xa"),
      check("D4 removal unit decides", pW(la_, "a") == "FAILS" and pW(lb_, "a") == "HOLDS")))
# D5 every JOINED copy set compiles (group J): the shown instantiations
joined = [XY, inst(r"(?<{0}>\d)", [["a", "b"]], name_join=True), inst(r"\d{{{0},{1}}}", [["2", "4"], ["2", "4"]]),
          inst(r"(\d+?)\d{{{0}}}", [["2", "4"]]), inst(r"(?<r>\d{{{0},{1}}})", [["2", "3", "4"], ["2", "3", "4"]])]
bad = [j for j in joined if compiles(j) is not None]
print("D5 the JOINED copies compile (libpcre2), %d sets: %s ; name join -> `/%s/` ; %s" % (len(joined), "all" if not bad else "REFUSED %s" % bad, joined[1],
      check("D5 joined copies compile", not bad)))
print()

# ======================================================================================================== PART I
print("== PART I: SIMULATE-4 (owner question backref-across-parts) and SIMULATE-7 (the printed hit list)")
bk = LRx(r"(?J)(?:(?P<x>a)|(?P<x>b))+\k<x>")
print("I1 `(?J)(?:(?<x>a)|(?<x>b))+\\k<x>` (a backreference to a name two groups share): WHOLE `abba` %s, `abbb` %s ; SEARCHED `abbbab` %s ; FIND-ALL `aba abb bbaa` %s" % (
    pW(bk, "abba"), pW(bk, "abbb"), pS(bk, "abbbab"), pF(bk, "aba abb bbaa")))
print("I1   it reads the FIRST SET group of the name (`a`), not the last-set `b` ; %s" % check("I1 backref first set", pW(bk, "abba") == "HOLDS" and pW(bk, "abbb") == "FAILS"))
sp = LRx(r"(?J)(?:(?P<h>\d))(?:(?P<h>\d)\k<h>)"); bo = LRx(r"(?P<h>\d)\k<h>")
print("I1 A := `/(?<h>\\d)/`, B := `/(?<h>\\d)\\k<h>/`, `A SEQ B` spliced (with (?J)): WHOLE `733` %s, `737` %s ; SEARCHED `1733 737` %s ; FIND-ALL `737 733 747` %s" % (
    pW(sp, "733"), pW(sp, "737"), pS(sp, "1733 737"), pF(sp, "737 733 747")))
print("I1   B alone: WHOLE `33` %s, `37` %s ; the splice without (?J): %s ; %s" % (pW(bo, "33"), pW(bo, "37"),
      "REFUSED: " + (compiles(r"(?:(?P<h>\d))(?:(?P<h>\d)\k<h>)") or "compiles"),
      check("I1 splice changes B's backreference", pW(sp, "733") == "FAILS" and pW(sp, "737") == "HOLDS" and pW(bo, "33") == "HOLDS")))
def hitrun(pat, s, judge_ok):
    hits, judged = [], {}
    def rec(c):
        sp_ = c.span("n")
        while hits and hits[-1][1] > sp_[0]: hits.pop()
        hits.append(sp_); return True
    def judge(c):
        judged["h"] = [c.subject[a:b] for a, b in hits]; return all(judge_ok(c.subject[a:b]) for a, b in hits)
    m = P.Pcre(pat, {"rec": rec, "judge": judge}).match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
    return ("FAILS" if m is None else "HOLDS") + " hits %s" % judged.get("h")
FT = r'\A(?:.*?(?>(?<n>\d+))(?C"rec"))*\D*\z(?C"judge")'
r_int = [hitrun(FT, t, lambda v: int(v) < 100) for t in ("1234", "12 34", "12 345", "x300 12")]
r_can = [hitrun(FT, t, lt(100)) for t in ("1234", "12 34", "12 345", "x300 12")]
print("I2 PART H's FIRST TRY `%s`, 'every number under 100':" % FT)
print("I2   the int() judge (rev 25's print) %s" % " ; ".join(r_int))
print("I2   the CANONICAL-numeral judge (NUMERALS: no leading zeros) %s ; %s" % (" ; ".join(r_can),
      check("I2 canonical hit list", r_can[3] == "HOLDS hits ['0', '12']" and r_int[3] == "HOLDS hits ['00', '12']")))
print()

# ======================================================================================================== PART J
print("== PART J (group J): the PARSE RULE, checked. Readings marked: the parse rule is MINE in the record; longest-first is MINE.")
X = Exp({"x": "a", "y": "b", "item": r"(?<h>\d)", "rx.digit": r"\d"}, sab="s4" in SABS)
def ex(src):
    try: return X(src)
    except TypeErr as e: return "TYPE ERROR (%s)" % e
    except AssertionError as e: return "PARSE FAILED %s" % (e,)
J9 = (("x++", "(?:(?:a))++", "longest first (MINE): `++` one operator"),
      ("x+?", "(?:(?:a))+?", "longest first"), ("x*+", "(?:(?:a))*+", "longest first"), ("x??", "(?:(?:a))??", "longest first"),
      ("x+ | y", "(?:(?:(?:a))+|(?:b))", "the parse rule: `|` cannot begin an operand, so `+` is postfix"),
      ('(item SEQ ",")* SEQ item', r"(?:(?:(?:(?:(?<h>\d)))(?:,))*)(?:(?:(?<h>\d)))",
       "the record's clause 'the sequence mark is explicit': a sequence mark cannot begin an operand, so `*` is postfix"),
      ("x + y", "TYPE ERROR (binary `+` on patterns: arithmetic, not a quantifier)",
       "THE DRAFT'S READING (open: value-is-pattern, which folds plus-operands): binary `+` on two patterns is a type error"),
      ("x * y", "TYPE ERROR (binary `*` on patterns: arithmetic, not a quantifier)", "THE DRAFT'S READING, as `x + y`"))
for src, want, why in J9:
    got = ex(src)
    print("J9 `%s` tokens %s -> %s ; %s ; %s" % (src, tokens(src), got, why, check("J9 %s" % src, got == want)))
print()

# ======================================================================================================== CHECKS
ok = sum(1 for _, v in CHECKS if v)
print("== CHECKS: %d of %d OK%s" % (ok, len(CHECKS), "" if ok == len(CHECKS) else " ; FAILED: " + ", ".join(n for n, v in CHECKS if not v)))
