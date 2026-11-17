#!/usr/bin/env python3
# Lane rxmodel (2026-11-17): a REGEX MODEL for each open choice of the predicate language, RUN on the installed
# libpcre2-8 (pcre2h.py), compared with lane pathimpact's engine (pathimpact_model.py, loaded in memory, never edited)
# running each candidate reading on the same lines and text sets. DESIGN EVIDENCE ONLY: "the model equals candidate X"
# is a finding, not a ruling.
#
# THE BASE MODEL (the owner, 2026-11-13, and the manager's note there): a CONDITION is a PCRE2 CALLOUT `(?C"name")`
# placed where the condition is written; it returns "fail here" (callout result 1) when the test is not TRUE, and
# PCRE backtracks to its next choice. Where a choice needs more than a callout, the model uses PCRE2's own constructs:
# conditional groups `(?(<g>)yes|no)` and `(?(?=(?C"t"))yes|no)`, negative lookahead, atomic groups, possessive loops,
# backtracking verbs, and PCRE2 10.45's NON-ATOMIC positive lookahead `(*napla:...)` (used with a captured rest-of-text
# `(?<T>[\s\S]*+)` and `\k<T>\z` to tie two patterns to the SAME stretch).
#
# Commands (W = the worktree; from a scratch dir under $PCREC_TMPDIR):
#   timeout 900 python3 -I W/docs/dev/lanes/rxmodel_evidence/rxmodel.py > rxmodel.out      # about 2 minutes
#   RXMODEL_SABOTAGE=1 ...: every callout answers the OPPOSITE way (TRUE <-> not TRUE); the comparisons must move
import os, sys, io, re, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
LANES = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pcre2h as P

SAB = os.environ.get("RXMODEL_SABOTAGE") == "1"

# ------------------------------------------------------------------------------------------------ pathimpact's engine
PI = os.path.join(LANES, "pathimpact_evidence", "pathimpact_model.py")
SRC = open(PI).read()
E = {"__file__": PI, "__name__": "pathimpact_defs"}
for k in ("PATHIMPACT_SWAP", "PATHIMPACT_SABOTAGE", "PATHIMPACT_READING", "PATHIMPACT_ENDS"):
    os.environ.pop(k, None)
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(SRC[:re.search(r"^# =+ PART A$", SRC, re.M).start()], PI, "exec"), E)
def block(name):
    """One top-level `class NAME` / `def NAME` block of pathimpact_model.py, verbatim."""
    m = re.search(r"^(class|def) %s\b.*?(?=^\S)" % name, SRC, re.M | re.S)
    return m.group(0)
for nm in ("NotAhead", "PosAhead", "h1", "h2", "when_body", "when_filter", "ptest_alt", "some_exists", "some_three",
           "joint_plain", "joint_comp", "record_", "ZIN", "ZNOT", "AndSpan", "DiffSpan"):
    exec(block(nm), E)
exec(r'''
KHP_ = r";(?P<h>\d)"
KH = R(r"(?P<k>\d)(?:;(?P<h>\d))*", passre=KHP_)
KHPOOL = [k + "".join(";" + x for x in t) for k in "0123456789" for t in [()] + [(a,) for a in "0123456789"] + [(a, b) for a in "0123456789" for b in "0123456789"]]
pk = test("k", between(3, 7))
q = W(T2, late_f)
GAPQ = W(R(r"[\s\S]*?" + T2P), late_f)
BODY = R(r"(?:[\s\S]*?(?P<hit>\d+))*[\s\S]*")
OCCPOOL = strings("12 x", 4)
REPx = R(r"(?:(?P<h>\d)?;)*", passre=r"(?P<h>\d)?;")
AH = R(r"a(?P<h>\d)|b(?P<k>\d)|c")
LATEM = W(R(r"[\s\S]*?\d\d:(?P<lm>\d\d)"), test("lm", lambda v: numeral(v) and int(v) >= 30))
NN = W(R(r"(?P<n>\d+)"), test("n", lt(100)))
S9, T30 = lt(9), lt(30)
MDOM = [a + b for a in "0123456789" for b in "0123456789"]
TPOOL = strings("190: ", 4)
DIGS = R(r"\d+")
l20, l10, la = test("l", lt(20)), test("l", lt(10)), test("l", eq("a"))
a1 = test("a", eq("1"))
''', E)
lt, gt, eq, numeral, between, late_f = E["lt"], E["gt"], E["eq"], E["numeral"], E["between"], E["late_f"]
DIG4, DSP, RG3, TPOOL, KHPOOL, OCCPOOL = E["DIG4"], E["DSP"], E["RG3"], E["TPOOL"], E["KHPOOL"], E["OCCPOOL"]
ABC = E["strings"]("abc37", 3)
TP5 = E["strings"]("905: ", 5)       # 3,906 time texts: late times (`9:50`, `9:59`, `50:00`), lm values 50 / 55 / 59 / 90 ...

@contextlib.contextmanager
def setting(**kw):
    old = {k: E[k]["v"] for k in kw}
    for k, v in kw.items(): E[k]["v"] = v
    try: yield
    finally:
        for k, v in old.items(): E[k]["v"] = v

# ------------------------------------------------------------------------------------------------ callouts
def T(lab, S):
    """A condition on one label as a callout: TRUE continues; FALSE or an ABSENT label (UNKNOWN) fails here."""
    def f(c):
        v = c.get(lab)
        return None if v is None else bool(S(v))
    return f
def flip(f):
    if not SAB: return f
    return lambda c: not (f(c) is True)
def late2(c): return late_f({"h": c.get("h2"), "m": c.get("m2")})
def late1(c): return late_f({"h": c.get("h"), "m": c.get("m")})
def passes_c(c):                     # `(h: <5)` Kleene AND over the passes; the callout reads its stretch's text
    st = c.stretch()
    return E["ptest"]("h", lt(5))({"_passes": {"h": [m.group("h") for m in re.finditer(E["KHP_"], st)]}})
SUB = {}
def sub_whole(pat):                  # `(0: B)`: B matched WHOLE against the stretch's own text, a second PCRE2 match
    if pat not in SUB: SUB[pat] = P.Pcre(pat)
    return lambda c: SUB[pat].whole(c.stretch())
QSEARCH = None
def no_q_in_subject(c):              # route (ii): the callout reads the WHOLE subject (a gate), q's own PCRE2 model
    return not QS.findall(c.subject)
CO = {
    "l<20": T("l", lt(20)), "l<10": T("l", lt(10)), "l>50": T("l", gt(50)), "l=a": T("l", eq("a")),
    "a=1": T("a", eq("1")), "a<5": T("a", lt(5)), "a2=1": T("a2", eq("1")), "x=1": T("x", eq("1")),
    "h<5": T("h", lt(5)), "h!<5": T("h", lambda v: not lt(5)(v)), "hit<100": T("hit", lt(100)), "n<100": T("n", lt(100)),
    "a=z": lambda c: None if c.get("a") is None or c.get("z") is None else c.get("a") == c.get("z"),
    "late": late1, "late2": late2, "h<9": T("h", lt(9)), "m<30": T("m", lt(30)),
    "joint": lambda c: E["joint_plain"]({"h": c.get("h"), "m": c.get("m")}),
    "k<5": T("k", lt(5)), "lm>=30": T("lm", lambda v: numeral(v) and int(v) >= 30), "lm=50": T("lm", eq("50")),
    "a=1|c=1": lambda c: E["kor"]([None if c.get("a") is None else c.get("a") == "1", None if c.get("c") is None else c.get("c") == "1"]),
    "c": passes_c, "p": T("k", between(3, 7)), "noq": no_q_in_subject,
}
CO = {k: flip(f) for k, f in CO.items()}
def RXC(p, opts=0): return P.Pcre(p, CO, opts)
T2X = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
T2Y = r"(?<h2>\d{1,2})(?::(?<m2>\d\d))?"
QS = RXC(T2X + r'(?C"late")')
REST = r"(?<T>[\s\S]*+)"
TIE = r"(?=\k<T>\z)"
EAT = r"(?:(?!\k<T>\z)[\s\S])*+"     # consume exactly up to the stretch end the napla fixed

# ------------------------------------------------------------------------------------------------ answers, comparisons
def labt(d, labs): return tuple((l, d.get(l)) for l in labs)
def rx_ans(rx, labs):
    def f(s, mode):
        if mode == "WHOLE": return rx.whole(s)
        if mode == "SEARCHED":
            r = rx.search(s)
            return None if r is None else (r[0], r[1], labt(r[2], labs))
        return tuple((a, b, labt(d, labs)) for a, b, d in rx.findall(s))
    return f
def en_ans(Pn, labs, cmp="C1", **st):
    def f(s, mode):
        with setting(**st):
            if mode == "WHOLE": return E["whole"](Pn, s, None, cmp)
            if mode == "SEARCHED":
                r = E["search"](Pn, s, 0, None, cmp)
                return None if r is None else (r[0], r[1], labt(r[2], labs))
            return tuple((a, b, labt(d, labs)) for a, b, d in E["findall"](Pn, s, None, cmp))
    return f
def fmt(s, mode, a):
    if mode == "WHOLE": return "HOLDS" if a else "FAILS"
    if mode == "SEARCHED":
        return "FAILS" if a is None else "`%s`@%d%s" % (s[a[0]:a[1]], a[0], "".join(" %s=%s" % lv for lv in a[2]))
    return "[" + ", ".join("`%s`@%d%s" % (s[x[0]:x[1]], x[0], "".join(" %s=%s" % lv for lv in x[2])) for x in a) + "]"
MODES3 = ("WHOLE", "SEARCHED", "FIND-ALL")
def cmpr(f1, f2, pool, modes=MODES3):
    out = []
    for m in modes:
        d = [s for s in pool if f1(s, m) != f2(s, m)]
        if d:
            w = min(d, key=lambda x: (len(x), x))
            out.append("%s %d (first `%s`: regex %s, engine %s)" % (m, len(d), w, fmt(w, m, f1(w, m)), fmt(w, m, f2(w, m))))
        else: out.append("%s 0" % m)
    return "; ".join(out) + " of %d" % len(pool)
def show(f, texts):
    """WHOLE on texts[0] / SEARCHED on texts[1] / FIND-ALL on texts[2]."""
    w, s_, fa = texts
    return "WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (w, fmt(w, "WHOLE", f(w, "WHOLE")), s_, fmt(s_, "SEARCHED", f(s_, "SEARCHED")), fa, fmt(fa, "FIND-ALL", f(fa, "FIND-ALL")))
def line(tag, txt): print("  %s %s" % (tag, txt))
def model(tag, name, pat, labs, texts, cands, pool, modes=MODES3, opts=0):
    """Print the regex model's answers and its comparison with each engine candidate over a text set."""
    rx = RXC(pat, opts)
    f = rx_ans(rx, labs)
    line(tag, "MODEL %s  /%s/" % (name, pat))
    line(tag, "  PCRE2: " + show(f, texts))
    for cn, g in cands:
        line(tag, "  vs %s: same lines %s ; over the set: %s" % (cn, "EQUAL" if all(f(t, m) == g(t, m) for t, m in zip(texts, MODES3)) else "DIFFER (" + show(g, texts) + ")", cmpr(f, g, pool, modes)))
    return f

print("ORDER: rxmodel%s ; libpcre2-8 %s" % (" SABOTAGE (every callout inverted)" if SAB else "", P.version()))

# ====================================================================================================== PREMISE
print("== PREMISE")
for l, ok in P.selfcheck(): line("P0", "%s %s" % ("PASS" if ok else "FAIL", l))
pr = P.Pcre(r'(?:(?<g1>\d\d)|(?<g2>\d)\d)(?C"t")', {"t": lambda c: c.get("g1") != "25"})
r_ = pr.search("25")
line("P1", "%s `(?:(?<g1>\\d\\d)|(?<g2>\\d)\\d)(?C)` on `25`, the callout failing when g1 = 25: %s (expect g2 = 2: the second branch)" % ("PASS" if r_ and r_[2]["g2"] == "2" and r_[2]["g1"] is None else "FAIL", r_))

# ====================================================================================================== BASE
print("== BASE: the ruled rule (reading (ii)) as callouts; engine = pathimpact's RULE")
model("B1", "`(B | A) & (l: <20)`", r'(?|(?<l>\d\d)|(?<l>\d)\d)(?C"l<20")', ("l",), ("25", "25", "25 13"),
      [("engine (ii)", en_ans(E["W"](E["Alt"](E["Bd"], E["Ad"]), E["l20"]), ("l",)))], DSP)
model("B2", "L60 `(B | A) & (l: \"a\")`", r'(?|(?<l>aa)|(?<l>a)a)(?C"l=a")', ("l",), ("aa", "aa", "aaaa"),
      [("engine (ii)", en_ans(E["W"](E["Alt"](E["Ba"], E["Aa"]), E["la"]), ("l",)))], E["AB4"])
model("B3", "note (a) `P & (a: \"1\")`", r'(?<a>\d+)(?<b>\d+)(?C"a=1")', ("a", "b"), ("123", "123", "123 9 12"),
      [("engine (ii)", en_ans(E["W"](E["PAB"], E["a1"]), ("a", "b")))], DSP)

# ====================================================================================================== a
print("== a unknown-backtracks (E6): a test on an ABSENT label")
UP = E["W"](E["R"](r"(?P<b>\d+)(?P<a>\d)?"), E["test"]("a", lt(5)))
CU = [("engine U1", en_ans(UP, ("a", "b"), UNK="U1")), ("engine U2", en_ans(UP, ("a", "b"), UNK="U2"))]
TA = ("12", "12", "12 1 19 3")
model("a1", "callout, absent = fail here", r'(?<b>\d+)(?<a>\d)?(?C"a<5")', ("a", "b"), TA, CU, DSP)
model("a2", "pure regex: a conditional on the unset group, its no-branch (*FAIL)", r'(?<b>\d+)(?<a>\d)?(?(<a>)(?<=[0-4])|(*FAIL))', ("a", "b"), TA, CU, DSP)
UPZ = E["W"](E["R"](r"(?P<b>\d+)(?P<a>\d)?;(?P<z>\d)"), lambda r: None if r.get("a") is None else r.get("a") == r.get("z"))
model("a3", "pure regex: a BACKREFERENCE to the unset group, `(a: = z)`", r'(?<b>\d+)(?<a>\d)?;(?=\k<a>)(?<z>\d)', ("a", "b", "z"), ("12;2", "12;2", "12;2 1;1 11;1"),
      [("engine U1", en_ans(UPZ, ("a", "b", "z"), UNK="U1")), ("engine U2", en_ans(UPZ, ("a", "b", "z"), UNK="U2"))], E["strings"]("12;", 5))
model("a4", "U2 spelled in regex: the no-branch (*PRUNE)(*FAIL) (end this start)", r'(?<b>\d+)(?<a>\d)?(?(<a>)(?<=[0-4])|(*PRUNE)(*FAIL))', ("a", "b"), TA, CU, DSP)

# ====================================================================================================== b
print("== b condition-not: NOT on a test of an ABSENT label (ruled 11-16 23:48: three-valued, absence never matches)")
UN = E["W"](E["R"](r"(?P<b>\d+)(?P<a>\d)?"), E["NOT"](E["test"]("a", lt(5))))
UN2 = E["W"](E["R"](r"(?P<b>\d+)(?P<a>\d)?"), lambda r: not (E["test"]("a", lt(5))(r) is True))
CN = [("engine RULED three-valued NOT", en_ans(UN, ("a", "b"))), ("engine two-valued NOT (NOT TRUE)", en_ans(UN2, ("a", "b")))]
TB = ("1", "1", "1 12 19 3")
model("b1", "regex's NOT: a negative lookahead around the callout", r'(?<b>\d+)(?<a>\d)?(?!(?C"a<5"))', ("a", "b"), TB, CN, DSP)
model("b2", "pure regex: a negative lookahead around the conditional test", r'(?<b>\d+)(?<a>\d)?(?!(?(<a>)(?<=[0-4])|(*FAIL)))', ("a", "b"), TB, CN, DSP)
model("b3", "the RULED NOT spelled in regex: a guard on the group, then the negative lookahead", r'(?<b>\d+)(?<a>\d)?(?(<a>)(?!(?<=[0-4]))|(*FAIL))', ("a", "b"), TB, CN, DSP)
UNZ = E["W"](E["R"](r"(?P<b>\d+)(?P<a>\d)?;(?P<z>\d)"), E["NOT"](lambda r: None if r.get("a") is None else r.get("a") == r.get("z")))
UNZ2 = E["W"](E["R"](r"(?P<b>\d+)(?P<a>\d)?;(?P<z>\d)"), lambda r: not (r.get("a") is not None and r.get("a") == r.get("z")))
model("b4", "a negative lookahead around a BACKREFERENCE to the unset group, `NOT (a: = z)`", r'(?<b>\d+)(?<a>\d)?;(?!\k<a>)(?<z>\d)', ("a", "b", "z"), ("1;2", "1;2", "1;2 12;2 11;1"),
      [("engine RULED three-valued NOT", en_ans(UNZ, ("a", "b", "z"))), ("engine two-valued NOT", en_ans(UNZ2, ("a", "b", "z")))], E["strings"]("12;", 5))
rxu = RXC(r'(?<b>\d+)(?<a>\d)?;(?!\k<a>)(?<z>\d)', P.PCRE2_MATCH_UNSET_BACKREF)
line("b5", "the same with PCRE2_MATCH_UNSET_BACKREF (an unset group matches empty, so `(?!\\k<a>)` FAILS on an absent a): on `1;2` %s ; on `12;3` %s" % (rxu.search("1;2"), rxu.search("12;3")))

# ====================================================================================================== c
print("== c loop-condition (E2), pass-table, pass-and: a condition on a label set inside a loop")
for nm, rx_, inbody, l1, last in [("/(?:(?<h>\\d);)*/", r"(?:(?P<h>\d);)*", r'(?:(?<h>\d)(?C"h<5");)*', r'(?:(?<h>\d)(?C"h<5");)*(?(<h>)|(*FAIL))', r'(?:(?<h>\d);)*(?C"h<5")'),
                                  ("/(?:(?<h>\\d)?;)*/", r"(?:(?P<h>\d)?;)*", r'(?:(?:(?<h>\d)(?C"h<5"))?;)*', r'(?:(?<h>\d)(?C"h<5");)+', r'(?:(?<h>\d)?;)*(?C"h<5")')]:
    L1 = E["W"](E["R"](rx_, passre=rx_[3:-2]), E["ptest"]("h", lt(5)))
    L2 = E["R"](rx_, piece={"h": lt(5)})
    LL = E["W"](E["R"](rx_), E["test"]("h", lt(5)))
    CL = [("engine L1 (the pass table, Kleene AND, judged after the loop)", en_ans(L1, ("h",))),
          ("engine L2 (a piece in each pass)", en_ans(L2, ("h",))), ("engine LAST (PCRE's last capture)", en_ans(LL, ("h",)))]
    TC = ("7;3;", "7;3;", "3;;7;;3;")
    line("c", "loop %s, `(h: <5)`" % nm)
    model("c1", "the callout WRITTEN INSIDE the body (right after h's group)", inbody, ("h",), TC, CL, RG3)
    model("c2", "the callout written AFTER the loop", last, ("h",), TC, CL, RG3)
    model("c3", "the pass table's Kleene AND as regex: in the body, a pass lacking h fails, at least one pass", l1, ("h",), TC, CL, RG3)
line("c", "pass-and: `NOT (h: <5)` on /(?:(?<h>\\d)?;)*/")
CPA = [("engine Kleene AND (today)", en_ans(E["W"](E["REPx"], E["NOT"](E["ptest"]("h", lt(5)))), ("h",))),
       ("engine a pass lacking h makes it UNKNOWN", en_ans(E["W"](E["REPx"], E["NOT"](E["ptest_alt"]("h", lt(5)))), ("h",)))]
TPA = ("7;;", "7;;", "7;;3;7;;")
model("c4", "regex's NOT after the loop (reads the last capture, two-valued)", r'(?:(?<h>\d)?;)*(?!(?C"h<5"))', ("h",), TPA, CPA, RG3)
model("c5", "Kleene NOT-AND as regex: a flag group set in a pass whose h is not <5, required at the end", r'(?:(?:(?<h>\d)(?(?=(?C"h<5"))|(?<bad>)))?;)*(?(<bad>)|(*FAIL))', ("h",), TPA, CPA, RG3)
model("c6", "the alternative as regex: the same, a pass lacking h fails", r'(?:(?<h>\d)(?(?=(?C"h<5"))|(?<bad>));)*(?(<bad>)|(*FAIL))', ("h",), TPA, CPA, RG3)

# ====================================================================================================== d
print("== d complement-paths (E3): `P & !(P & (a: \"1\"))`, the complement tied to the same stretch")
DF = E["Diff"](E["PAB"], E["W"](E["PAB"], E["a1"]))
CD = [("engine C1 (some surviving path of B)", en_ans(DF, ("a", "b"), "C1")), ("engine C2 (B's one parse judged)", en_ans(DF, ("a", "b"), "C2"))]
TD = ("123", "123", "123 9 113")
model("d1", "negative lookahead tied to the stretch (napla + captured rest)", r'(*napla:(?<a>\d+)(?<b>\d+)' + REST + r')(?!(?<a2>\d+)(?<b2>\d+)(?C"a2=1")\k<T>\z)' + EAT, ("a", "b"), TD, CD, DSP)
model("d2", "C2 as regex: B's first parse of the stretch made atomic, then judged", r'(*napla:(?<a>\d+)(?<b>\d+)' + REST + r')(?!(?>(?<a2>\d+)(?<b2>\d+)\k<T>\z)(?C"a2=1"))' + EAT, ("a", "b"), TD, CD, DSP)
model("d3", "the UNTIED negative lookahead `(?!B)P` (no B from this start, any end)", r'(?!(?<a2>\d+)(?<b2>\d+)(?C"a2=1"))(?<a>\d+)(?<b>\d+)', ("a", "b"), TD, CD, DSP)
model("d5", "tied vs untied on a short complement: `/\\d+/ & !/1/`, tied", r'(*napla:\d+' + REST + r')(?!1\k<T>\z)' + EAT, (), ("12", "12", "12 1 31"),
      [("engine `/\\d+/ & !/1/`", en_ans(E["Diff"](E["DIGS"], E["R"](r"1")), ()))], DSP)
model("d6", "the same, UNTIED `(?!1)\\d+`", r'(?!1)\d+', (), ("12", "12", "12 1 31"),
      [("engine `/\\d+/ & !/1/`", en_ans(E["Diff"](E["DIGS"], E["R"](r"1")), ()))], DSP)
line("d", "complement-place: a lone `!q` in a WHOLE place (\"the value is not a late time\")")
f_lone = rx_ans(RXC(r'(?!' + T2X + r'(?C"late")\z)[\s\S]*'), ())
g_lone = lambda s, m: not E["whole"](E["q"], s)
line("d4", "MODEL `(?!q\\z)[\\s\\S]*` WHOLE: on `9:30` %s, `9` %s, `10:45` %s ; vs engine `not whole(q)` over the time texts: %s" % tuple(
    [fmt(v, "WHOLE", f_lone(v, "WHOLE")) for v in ("9:30", "9", "10:45")] + [cmpr(f_lone, g_lone, TP5, ("WHOLE",))]))

# ====================================================================================================== e
print("== e lookahead-reentry (E4, E4'), lookahead-labels")
CE = [("engine LA1 (atomic)", en_ans(E["W"](E["R"](r"(?=(?P<x>\d+))\d", look_atomic=True), E["test"]("x", eq("1"))), ("x",))),
      ("engine LA2 (re-entered)", en_ans(E["W"](E["R"](r"(?=(?P<x>\d+))\d", look_atomic=False), E["test"]("x", eq("1"))), ("x",)))]
TE = ("12", "12", "112 12 1")
model("e1", "PCRE's ordinary positive lookahead", r'(?=(?<x>\d+))\d(?C"x=1")', ("x",), TE, CE, DSP)
model("e2", "PCRE2's NON-ATOMIC lookahead (*napla:)", r'(*napla:(?<x>\d+))\d(?C"x=1")', ("x",), TE, CE, DSP)
CNA = [("engine NA1 (inner condition backtracks inside)", en_ans(E["NotAhead"](E["T2"], E["GAPQ"], "NA1"), ("h", "m"))),
       ("engine NA2 (inner first path judged)", en_ans(E["NotAhead"](E["T2"], E["GAPQ"], "NA2"), ("h", "m")))]
TNA = ("9:15", "9:15 10:45", "9:15 10:45 1")
model("e3", "negative lookahead holding a condition (whole-text route (i))", r'(?![\s\S]*?' + T2Y + r'(?C"late2"))' + T2X, ("h", "m"), TNA, CNA, TP5)
model("e4", "NA2 as regex: the inner first path made atomic, then judged", r'(?!(?>[\s\S]*?' + T2Y + r')(?C"late2"))' + T2X, ("h", "m"), TNA, CNA, TP5)
CLL = [("engine LA1 (PCRE's)", en_ans(E["W"](E["PosAhead"](E["T2"], E["LATEM"], "LA1"), E["test"]("lm", eq("50"))), ("h", "lm"))),
       ("engine LA2 (re-entered)", en_ans(E["W"](E["PosAhead"](E["T2"], E["LATEM"], "LA2"), E["test"]("lm", eq("50"))), ("h", "lm")))]
TLL = ("9:15", "9:15 10:45 11:50", "9:15 10:45 11:50 1")
model("e5", "lookahead-labels: a positive lookahead's capture read outside it", r'(?=[\s\S]*?\d\d:(?<lm>\d\d)(?C"lm>=30"))' + T2X + r'(?C"lm=50")', ("h", "lm"), TLL, CLL, TP5)
model("e6", "lookahead-labels with (*napla:)", r'(*napla:[\s\S]*?\d\d:(?<lm>\d\d)(?C"lm>=30"))' + T2X + r'(?C"lm=50")', ("h", "lm"), TLL, CLL, TP5)

# ====================================================================================================== f
print("== f hits-reentry (E5), hit-list: `occurrences(/\\d+/)` with `(hit: <100)` (WHOLE); a filtered argument's hit list")
CH = [("engine H1 (hits fixed, judged)", lambda s, m: E["whole"](E["h1"](lt(100)), s)), ("engine H2 (re-enters the body)", lambda s, m: E["whole"](E["h2"](lt(100)), s))]
for tag, nm, pat in [("f1", "each hit committed: possessive gaps and hits, the callout after each", r'\A(?:\D*+(?<hit>\d++)(?C"hit<100"))++\D*+\z'),
                     ("f2", "the body with the callout inside each pass (re-entered)", r'\A(?:[\s\S]*?(?<hit>\d+)(?C"hit<100"))+[\s\S]*\z')]:
    rx = RXC(pat); f = lambda s, m, rx=rx: rx.whole(s)
    line(tag, "MODEL %s  /%s/" % (nm, pat))
    line(tag, "  PCRE2 WHOLE: `1234` %s, `x300 12` %s, `5 123` %s" % tuple(fmt(v, "WHOLE", f(v, "WHOLE")) for v in ("1234", "x300 12", "5 123")))
    for cn, g in CH: line(tag, "  vs %s: %s" % (cn, cmpr(f, g, OCCPOOL, ("WHOLE",))))
DIGRX = P.Pcre(r"\d+")
f2s = lambda s, m: bool(DIGRX.findall(s)) and all(lt(100)(s[x[0]:x[1]]) for x in DIGRX.findall(s))
line("f3", "MODEL two steps: PCRE2 find-all of /\\d+/, then every hit judged: vs engine H1: %s ; vs engine H2: %s" % (cmpr(f2s, CH[0][1], OCCPOOL, ("WHOLE",)), cmpr(f2s, CH[1][1], OCCPOOL, ("WHOLE",))))
model("f4", "hit-list: the callout inside the searched pattern, find-all", r'(?<n>\d+)(?C"n<100")', ("n",), ("1234", "1234", "5 123 1234"),
      [("engine hit list (R.1.9)", en_ans(E["NN"], ("n",)))], DSP)

# ---- rulings R1/R2: the owner's model of occurrences, one regex `(?:.*?(${rx}))*.*` (dot matching everything; R2: the
# LAZY gap is his model, the greedy gap a comparison line). Which hits a path carries is read by a tracker: a callout
# after the hit group files the hit under its end position, prefixed by the list filed under the pass's start (the
# empty group `g` marks where the pass began); a callout at the very end reads the list of the successful path.
STORE, LASTH = {}, {}
def rec(c):
    g, hs = c.span("g"), c.span("hit")
    STORE[hs[1]] = ([] if g[0] == c.start else list(STORE.get(g[0], []))) + [hs]
    return True
def endrec(c):
    hs = c.span("hit")
    LASTH["v"] = [] if hs is None else STORE.get(hs[1], [])
    return True
CO.update({"rec": rec, "end": endrec})
def hits_of(rx, s):
    STORE.clear(); LASTH.clear()
    if not rx.whole(s): return None
    return [s[a:b] for a, b in LASTH["v"]]
GLOB = P.Pcre(r"\d+")
def glob_hits(s): return [s[a:b] for a, b, _ in GLOB.findall(s)]
OCCT = ("12 34", "1234", "x300 12", "5 123")
print("== f (rulings R1, R2) the owner's model of occurrences: one regex, `(?:.*?(rx))*.*`, rx = /\\d+/")
for tag, nm, pat in [("fR1", "HIS MODEL (lazy gap), no condition", r'(?:(?<g>)[\s\S]*?(?<hit>\d+)(?C"rec"))*[\s\S]*(?C"end")'),
                     ("fR2", "comparison: greedy gap, no condition", r'(?:(?<g>)[\s\S]*(?<hit>\d+)(?C"rec"))*[\s\S]*(?C"end")')]:
    rx = RXC(pat)
    d = [t for t in OCCPOOL if hits_of(rx, t) != glob_hits(t)]
    line(tag, "MODEL %s  /%s/: hits of the first (reported) path on %s ; vs the GLOBAL search's hits over {1, 2, space, x} to length 4 (341): differ %d%s" % (
        nm, pat, " ; ".join("`%s` %s" % (t, hits_of(rx, t)) for t in OCCT), len(d), "" if not d else " (first `%s`: loop %s, global %s)" % (min(d, key=lambda x: (len(x), x)), hits_of(rx, min(d, key=lambda x: (len(x), x))), glob_hits(min(d, key=lambda x: (len(x), x))))))
for tag, nm, pat in [("fR3", "his model, `(hit: <100)` written INSIDE the body (after the hit group), zero passes allowed", r'(?:(?<g>)[\s\S]*?(?<hit>\d+)(?C"rec")(?C"hit<100"))*[\s\S]*(?C"end")'),
                     ("fR4", "his model, `(hit: <100)` INSIDE the body, at least one pass `{1,}`", r'(?:(?<g>)[\s\S]*?(?<hit>\d+)(?C"rec")(?C"hit<100")){1,}[\s\S]*(?C"end")'),
                     ("fR5", "his model, `(hit: <100)` written AFTER the loop (reads the last pass's capture)", r'(?:(?<g>)[\s\S]*?(?<hit>\d+)(?C"rec"))*[\s\S]*(?C"hit<100")(?C"end")')]:
    rx = RXC(pat); f = lambda t, m, rx=rx: hits_of(rx, t) is not None
    line(tag, "MODEL %s  /%s/" % (nm, pat))
    line(tag, "  PCRE2 WHOLE (hits of the reported path): %s" % " ; ".join("`%s` %s" % (t, "FAILS" if hits_of(rx, t) is None else "HOLDS %s" % hits_of(rx, t)) for t in OCCT + ("x",)))
    for cn, g in CH: line(tag, "  vs %s: %s" % (cn, cmpr(f, g, OCCPOOL, ("WHOLE",))))
MIN2 = RXC(r'(?:[\s\S]*?(?<hit>\d+)){2,}[\s\S]*')
fm = lambda t, m: MIN2.whole(t); gm = lambda t, m: len(glob_hits(t)) >= 2
line("fR6", "MODEL `min = 2` as `{2,}` in his model  /%s/: `1234` %s, `12 34` %s, `1` %s ; vs the GLOBAL search's count >= 2: %s" % (
    MIN2.pattern, fmt("1234", "WHOLE", fm("1234", 0)), fmt("12 34", "WHOLE", fm("12 34", 0)), fmt("1", "WHOLE", fm("1", 0)), cmpr(fm, gm, OCCPOOL, ("WHOLE",))))
EMP = RXC(r'(?:(?<g>)[\s\S]*?(?<hit>\d*)(?C"rec"))*[\s\S]*(?C"end")'); GE = P.Pcre(r"\d*")
line("fR7", "EMPTY hits, rx = /\\d*/: his model on `1 2` %s, on `a1` %s ; the GLOBAL search's hits on `1 2` %s, on `a1` %s (a loop ends on an empty pass; a global search steps on)" % (
    hits_of(EMP, "1 2"), hits_of(EMP, "a1"), [ "1 2"[a:b] for a, b, _ in GE.findall("1 2")], ["a1"[a:b] for a, b, _ in GE.findall("a1")]))

# ====================================================================================================== g
print("== g join-order (E1): `(P & Q) & ((a: \"1\") | (c: \"1\"))`, P = /(?<a>\\d+)(?<b>\\d+)/, Q = /(?<c>\\d+)(?<d>\\d+)/")
J = E["W"](E["And"](E["PAB"], E["PCD"]), E["OR"](E["a1"], E["test"]("c", eq("1"))))
CJ = [("engine left-outer", en_ans(J, ("a", "b", "c", "d"), JOIN="left")), ("engine right-outer", en_ans(J, ("a", "b", "c", "d"), JOIN="right"))]
TJ = ("123", "123", "123 1121")
model("g1", "P in a non-atomic lookahead (outer), Q consumed to the same end", r'(*napla:(?<a>\d+)(?<b>\d+)' + REST + r')(?<c>\d+)(?<d>\d+)' + TIE + r'(?C"a=1|c=1")', ("a", "b", "c", "d"), TJ, CJ, DSP)
model("g2", "Q in the lookahead (outer), P consumed", r'(*napla:(?<c>\d+)(?<d>\d+)' + REST + r')(?<a>\d+)(?<b>\d+)' + TIE + r'(?C"a=1|c=1")', ("a", "b", "c", "d"), TJ, CJ, DSP)
model("g3", "the usual idiom with an ORDINARY (atomic) lookahead: P gets one path", r'(?=(?<a>\d+)(?<b>\d+)' + REST + r')(?<c>\d+)(?<d>\d+)' + TIE + r'(?C"a=1|c=1")', ("a", "b", "c", "d"), TJ, CJ, DSP)

J1 = E["W"](E["And"](E["PAB"], E["PCD"]), E["a1"])
CJ1 = [("engine left-outer", en_ans(J1, ("a", "b", "c", "d"), JOIN="left")), ("engine right-outer", en_ans(J1, ("a", "b", "c", "d"), JOIN="right"))]
model("g4", "`(P & Q) & (a: \"1\")`, the usual idiom (ordinary atomic lookahead on P)", r'(?=(?<a>\d+)(?<b>\d+)' + REST + r')(?<c>\d+)(?<d>\d+)' + TIE + r'(?C"a=1")', ("a", "b", "c", "d"), ("123", "123", "123 1121"), CJ1, DSP)
model("g5", "`(P & Q) & (a: \"1\")`, P in (*napla:)", r'(*napla:(?<a>\d+)(?<b>\d+)' + REST + r')(?<c>\d+)(?<d>\d+)' + TIE + r'(?C"a=1")', ("a", "b", "c", "d"), ("123", "123", "123 1121"), CJ1, DSP)

# ====================================================================================================== h
print("== h `A & B` vs `A & (0: B)`: does B see the text around the stretch?")
for tag, bp in [("h1", r"^\d+"), ("h2", r"\b\d+"), ("h3", r"\d+$"), ("h4", r"(?<= )\d+")]:
    Bx = E["R"](bp)
    CHB = [("engine IN-CONTEXT `&`", en_ans(E["And"](E["DIGS"], Bx), ())), ("engine SPAN `&` (the draft's filter role)", en_ans(E["AndSpan"](E["DIGS"], Bx), ())),
           ("engine `& (0: B)`", en_ans(E["ZIN"](E["DIGS"], Bx), ()))]
    model(tag, "`/\\d+/ & /%s/`: B consumed in the subject, tied to A's end" % bp, r'(*napla:\d+' + REST + r')' + bp + TIE, (), ("1", " 1", " 1 12"), CHB, DSP)
    CO["0:" + bp] = flip(sub_whole(bp))
    model(tag + "z", "`/\\d+/ & (0: /%s/)`: a callout that matches B WHOLE against the stretch alone" % bp, r'\d+(?C"0:' + bp + r'")', (), ("1", " 1", " 1 12"), CHB, DSP)

# ====================================================================================================== i
print("== i the other open slugs")
CR = [("engine today: joint UNKNOWN on an absent part", en_ans(E["W"](E["T2"], E["NOT"](E["joint_plain"])), ("h", "m"))),
      ("engine completion (item 18)", en_ans(E["W"](E["T2"], E["NOT"](E["joint_comp"])), ("h", "m"))),
      ("engine the record (h: <9, m: <30)", en_ans(E["W"](E["T2"], E["NOT"](E["record_"])), ("h", "m")))]
TR = ("10", "10", "10 9 10:15")
model("i1", "record-under-not: regex NOT around the record's two tests", T2X + r'(?!(?C"h<9")(?C"m<30"))', ("h", "m"), TR, CR, TP5)
model("i2", "record-under-not: regex NOT around the joint test", T2X + r'(?!(?C"joint"))', ("h", "m"), TR, CR, TP5)
CG = [("engine EXISTS two-valued (today)", en_ans(E["W"](E["REPx"], E["NOT"](E["some_exists"](lt(5)))), ("h",))),
      ("engine three-valued some", en_ans(E["W"](E["REPx"], E["NOT"](E["some_three"](lt(5)))), ("h",)))]
model("i3", "group-truth `NOT some((h: <5))`: a flag group set in a pass whose h is <5, forbidden at the end", r'(?:(?:(?<h>\d)(?(?=(?C"h<5"))(?<hit>)|))?;)*(?(<hit>)(*FAIL)|)', ("h",), (";", ";", ";;3;7;"), CG, RG3)
CO_ = [("engine Kleene OR (today)", en_ans(E["W"](E["AH"], E["NOT"](lambda r: E["kor"]([E["test"]("h", lt(5))(r), E["test"]("k", lt(5))(r)]))), ("h", "k"))),
       ("engine two-valued OR (rev 22)", en_ans(E["W"](E["AH"], lambda r: not (E["test"]("h", lt(5))(r) is True or E["test"]("k", lt(5))(r) is True)), ("h", "k")))]
model("i4", "condition-or `NOT ((h: <5) | (k: <5))`: a negative lookahead around an alternation of callouts", r'(?:a(?<h>\d)|b(?<k>\d)|c)(?!(?C"h<5")|(?C"k<5"))', ("h", "k"), ("b7", "b7", "b7 a3 c a9"), CO_, ABC)
CW = [("engine filter form `x & when(c, p)`", en_ans(E["when_filter"](E["ptest"]("h", lt(5))), ("k",))),
      ("engine body `(x & c & p) | (x & !(x & c))`", en_ans(E["when_body"](E["ptest"]("h", lt(5))), ("k",)))]
TW = ("5;1;9", "5;1;9", "3;0;5 5;1;9")
model("i5", "when-meaning: PCRE's CONDITIONAL GROUP, `x(?(?=(?C c))(?C p)|)`", r'(?<k>\d)(?:;(?<h>\d))*(?(?=(?C"c"))(?C"p")|)', ("k",), TW, CW, KHPOOL)
model("i6", "when-meaning: the body as a regex alternation (complement tied to the stretch)",
      r'(?|(?<k>\d)(?:;(?<h>\d))*(?C"c")(?C"p")|(*napla:(?<k>\d)(?:;(?<h>\d))*' + REST + r')(?!(?<k2>\d)(?:;(?<h2>\d))*(?C"c")\k<T>\z)' + EAT + ')', ("k",), TW, CW, KHPOOL)
for tag, nm, pat in [("i7", "repeated-means: `(?:(?<h>\\d);)+` & `\\d;` & `(h: <5)`", r'(*napla:\d;' + REST + r')(?:(?<h>\d);)+' + TIE + r'(?C"h<5")'),
                     ("i8", "repeated-means: `(?<h>\\d);` & `(h: <5)`", r'(?<h>\d);(?C"h<5")')]:
    f = rx_ans(RXC(pat), ("h",))
    line(tag, "MODEL %s  /%s/: %s" % (nm, pat, show(f, ("3;", "7;3;", "3;7;3;"))))
CWT = [("engine today `t2 & !q`", en_ans(E["Diff"](E["T2"], E["q"]), ("h", "m"))),
       ("engine route (ii) `t2 & text.none(q)`", en_ans(E["SF"](E["T2"], lambda s, i, e: not E["findall"](E["q"], s)), ("h", "m"))),
       ("engine route (i) NA1", en_ans(E["NotAhead"](E["T2"], E["GAPQ"], "NA1"), ("h", "m")))]
TWT = ("9:30", "9:30", "9:15 9:30 1")
model("i9", "whole-text route (ii) as a callout reading the whole subject (q's own regex model)", r'(?C"noq")' + T2X, ("h", "m"), TWT, CWT, TP5)
model("i10", "whole-text gated at the text start, `\\A(?![\\s\\S]*q)` then `\\K`", r'\A(?![\s\S]*?' + T2Y + r'(?C"late2"))[\s\S]*?\K' + T2X, ("h", "m"), TWT, CWT, TP5, ("SEARCHED",))
for bad in [r'(?<![\s\S]*' + T2Y + r')' + T2X, r'(?<!.{0,300})x']:
    try: P.Pcre(bad); line("i11", "compiles (unexpected): /%s/" % bad)
    except ValueError as e: line("i11", "REFUSED by PCRE2 (no unbounded lookbehind, so \"no q BEHIND this start\" has no plain spelling): %s" % e)

# ====================================================================================================== j
print("== j E7 atomic: PCRE's atomic group vs pathimpact's labelled extra")
At, Wh, Df, Al = E["Atomic"], E["W"], E["Diff"], E["Alt"]
for tag, nm, pat, P_, texts, labs, pool in [
        ("j1", "`t2 & q` atomic", r'(?>' + T2X + r')(?C"late")', Wh(At(E["T2"]), late_f), ("9:30", "9:30", "9:30 10:15"), ("h", "m"), TP5),
        ("j2", "`t2 & !q` atomic (item 14)", r'(*napla:(?>' + T2X + r')' + REST + r')(?!' + T2Y + r'(?C"late2")\k<T>\z)' + EAT, Df(At(E["T2"]), E["q"]), ("9:30", "9:30", "9:30 10:15"), ("h", "m"), TP5),
        ("j3", "`(B | A) & (l: <20)` atomic", r'(?>(?|(?<l>\d\d)|(?<l>\d)\d))(?C"l<20")', Wh(At(Al(E["Bd"], E["Ad"])), E["l20"]), ("25", "25", "25 13"), ("l",), DSP),
        ("j4", "`P & (a: \"1\")` atomic", r'(?>(?<a>\d+)(?<b>\d+))(?C"a=1")', Wh(At(E["PAB"]), E["a1"]), ("123", "123", "123 9 113"), ("a", "b"), DSP),
        ("j5", "`atomic(P & (a: \"1\"))`: the condition INSIDE the atomic group", r'(?>(?<a>\d+)(?<b>\d+)(?C"a=1"))', At(Wh(E["PAB"], E["a1"])), ("123", "123", "123 9 113"), ("a", "b"), DSP)]:
    model(tag, nm, pat, labs, texts, [("engine atomic", en_ans(P_, labs))], pool)
print("== END")
