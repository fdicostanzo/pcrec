#!/usr/bin/env python3
# fixinduced lens probe: re-runs KEPT rev-23.x sentences under rev 24's engine (read-only import of the engine source).
import os, sys, io, re, contextlib
ENG = "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/R/tree/docs/dev/lanes/predspec24_evidence/predspec24_model.py"
src = open(ENG).read()
G = {"__file__": ENG, "__name__": "ps24defs"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src[:re.search(r"^# =+ PART A: the catalogue$", src, re.M).start()], ENG, "exec"), G)
g = G
W, D, ALT, AND, C, NOT, ANDC, ORC, SOME, NONE, OCC, WHEN, Pat = (g[k] for k in "W D ALT AND C NOT ANDC ORC SOME NONE OCC WHEN Pat".split())
rules, whole_row, search, findall, aW, aS, aF, lt, eq, between, num = (g[k] for k in "rules whole_row search findall aW aS aF lt eq between num".split())
POOLS = {k: g[k] for k in "DSP DIG4 RG3 TP5 SVPOOL KHPOOL XYPOOL".split()}

def keyfn(mode, labs):
    def lb(row): return tuple(row.last.get(l) for l in labs) if labs else ()
    def f(P, s):
        if mode == "WHOLE":
            r = whole_row(P, s); return None if r is None else lb(r) if labs else True
        if mode == "SEARCHED":
            r = search(P, s); return None if r is None else (r[0], r[1]) + lb(r[2])
        return tuple((a, b) + lb(rw) for a, b, rw in findall(P, s))
    return f
def cmp(title, r, mk1, mk2, pool, labs=(), modes=("WHOLE", "SEARCHED", "FIND-ALL")):
    with rules(r):
        P1, P2 = mk1(), mk2(); out = []
        for m in modes:
            f = keyfn(m, labs); d = [s for s in pool if f(P1, s) != f(P2, s)]
            out.append("%s %d%s" % (m, len(d), (" (first `%s`)" % min(d, key=lambda x: (len(x), x))) if d else ""))
    print("%s [rules %s%s]: %s of %d" % (title, r, ", labels " + ",".join(labs) if labs else "", "; ".join(out), len(pool)))
def show(title, r, mk, texts, labs=()):
    with rules(r):
        P = mk(); print("%s [rules %s]: WHOLE %s / SEARCHED %s / FIND-ALL %s" % (title, r, aW(P, texts[0]), aS(P, texts[1], labs), aF(P, texts[2], labs)))
def holdsn(r, mk, pool):
    with rules(r):
        P = mk(); return sum(1 for s in pool if whole_row(P, s) is not None)

ABXY = g["ABXYp"]; PAB, PCD = g["PABp"], g["PCDp"]; REP = lambda: Pat(g["REPp"]); SV = lambda: Pat(g["SVp"])
h5 = g["h5"]; KH = lambda: Pat(g["KHp"]); pk = g["pk"]; t2 = g["mk_t2"]; q = g["mk_q"]; late = g["late"]
notlt = lambda n: (lambda v: not lt(n)(v))

print("== T1 L58/L61: contains(r) & (g: x) vs contains(r & (g: x)), r = /ab(?<g>[xy])/")
for r in ("24", "23.2"):
    show("L58 `contains(r) & (g: \"x\")` on `abx aby`", r, lambda: W(OCC(Pat(ABXY), 1), C("g", eq("x"))), ("abx aby",) * 3, ("g",))
    show("L61 `contains(r & (g: \"x\"))` on `abx aby`", r, lambda: OCC(W(Pat(ABXY), C("g", eq("x"))), 1), ("abx aby",) * 3)
    show("L61 `occurrences(r) & (g: \"x\")` on `abx aby`", r, lambda: W(OCC(Pat(ABXY)), C("g", eq("x"))), ("abx aby",) * 3, ("g",))
    cmp("L61 pair (operand-side vs inside)", r, lambda: W(OCC(Pat(ABXY), 1), C("g", eq("x"))), lambda: OCC(W(Pat(ABXY), C("g", eq("x"))), 1), POOLS["XYPOOL"])
    cmp("L58 `contains(r) & (g: x)` vs `contains(r) & some((g: x))`", r, lambda: W(OCC(Pat(ABXY), 1), C("g", eq("x"))), lambda: W(OCC(Pat(ABXY), 1), SOME(C("g", eq("x")))), POOLS["XYPOOL"])

print("== T2 L100: P & A & B vs (P & A) and (P & B), P = /(?<a>\\d+)(?<b>\\d+)/, A = (a: \"1\"), B = (b: \"3\")")
for r in ("24", "23.2"):
    with rules(r):
        PA, PB, PAB_ = W(Pat(PAB), C("a", eq("1"))), W(Pat(PAB), C("b", eq("3"))), W(Pat(PAB), C("a", eq("1")), C("b", eq("3")))
        d = [s for s in POOLS["DIG4"] if (whole_row(PAB_, s) is not None) != (whole_row(PA, s) is not None and whole_row(PB, s) is not None)]
    print("L100 [rules %s] WHOLE differ %d of %d%s" % (r, len(d), len(POOLS["DIG4"]), (" first `%s`" % min(d, key=lambda x: (len(x), x))) if d else ""))
    for r2 in (r,):
        with rules(r2):
            for s in ("123",): print("   on `%s`: P&A %s, P&B %s, P&A&B %s" % (s, aW(PA, s), aW(PB, s), aW(PAB_, s)))
# a looped-label twin: REP & (h: <5) & (h: !<3)... vs separately (last pass is one value, so not a witness); a lt/gt pair on a:
for r in ("24", "23.2"):
    with rules(r):
        PA, PB, PAB_ = W(Pat(PAB), C("a", lt(5))), W(Pat(PAB), C("a", lambda v: num(v) and int(v) > 10)), W(Pat(PAB), C("a", lt(5)), C("a", lambda v: num(v) and int(v) > 10))
        d = [s for s in POOLS["DIG4"] if (whole_row(PAB_, s) is not None) != (whole_row(PA, s) is not None and whole_row(PB, s) is not None)]
    print("L100 one label [rules %s] (a: <5), (a: >10): WHOLE differ %d of %d%s" % (r, len(d), len(POOLS["DIG4"]), (" first `%s`" % min(d, key=lambda x: (len(x), x))) if d else ""))

print("== T3 L1/L39: (P & Q) & c vs (Q & P) & c, c = (a: \"1\") | (c: \"1\")")
cc = lambda: ORC(C("a", eq("1")), C("c", eq("1")))
for r in ("24", "23.2"):
    cmp("L39 swap, holds/stretch", r, lambda: W(AND(Pat(PAB), Pat(PCD)), cc()), lambda: W(AND(Pat(PCD), Pat(PAB)), cc()), POOLS["DSP"])
    cmp("L39 swap, labels", r, lambda: W(AND(Pat(PAB), Pat(PCD)), cc()), lambda: W(AND(Pat(PCD), Pat(PAB)), cc()), POOLS["DSP"], ("a", "b", "c", "d"))
    show("P & Q & c on `123`", r, lambda: W(AND(Pat(PAB), Pat(PCD)), cc()), ("123",) * 3, ("a", "c"))
    show("Q & P & c on `123`", r, lambda: W(AND(Pat(PCD), Pat(PAB)), cc()), ("123",) * 3, ("a", "c"))
# with a plain AND of conditions (no |): P & Q & (a: "1") & (d: "3")
for r in ("24",):
    cmp("L39 swap, c = (a:1) & (c:12)", r, lambda: W(AND(Pat(PAB), Pat(PCD)), C("a", eq("1"))), lambda: W(AND(Pat(PCD), Pat(PAB)), C("a", eq("1"))), POOLS["DSP"], ("a", "b", "c", "d"))

print("== T4 §8 when: complement body vs rev 24 definition vs rev 20-21 NOT body, KH, c=(h:<5), p=(k: between(3,7))")
for cname, cmk in (("(h: <5)", lambda: h5()), ("(h = 0: <5)", lambda: C("h", lt(5), h="0"))):
    comp = lambda cmk=cmk: ALT(W(KH(), cmk(), pk()), D(KH(), W(KH(), cmk())))
    notb = lambda cmk=cmk: ALT(W(KH(), cmk(), pk()), W(KH(), NOT(cmk())))
    r24 = lambda cmk=cmk: W(KH(), ORC(NOT(cmk()), pk()))
    for r in ("24",):
        cmp("c=%s complement body vs rev24 x & (NOT c | p)" % cname, r, comp, r24, POOLS["KHPOOL"])
        cmp("c=%s NOT body vs rev24 x & (NOT c | p)" % cname, r, notb, r24, POOLS["KHPOOL"])
        cmp("c=%s complement body vs NOT body" % cname, r, comp, notb, POOLS["KHPOOL"])
    print("  holds WHOLE: complement %d, rev24 def %d, NOT body %d (rev 24); complement %d (rev 23.2)" % (holdsn("24", comp, POOLS["KHPOOL"]), holdsn("24", r24, POOLS["KHPOOL"]), holdsn("24", notb, POOLS["KHPOOL"]), holdsn("23.2", comp, POOLS["KHPOOL"])))
    with rules("24"):
        Pn = comp(); print("  complement body SEARCHED holds %d" % sum(1 for s in POOLS["KHPOOL"] if search(Pn, s) is not None))

print("== T5 default.unused (b) under NOT, rev 24 two-valued")
for r in ("24", "23.2"):
    cmp("set-once `NOT (h = 9: <5)` vs `NOT (h: <5)`", r, lambda: W(SV(), NOT(C("h", lt(5), h="9"))), lambda: W(SV(), NOT(h5())), POOLS["SVPOOL"], ("h",))
    cmp("REP `NOT (h = \"x\": <5)` vs `NOT (h: <5)`", r, lambda: W(REP(), NOT(C("h", lt(5), h="x"))), lambda: W(REP(), NOT(h5())), POOLS["RG3"], ("h",))
    cmp("REP `(h: <5)` vs `NOT some(NOT (h: <5))`", r, lambda: W(REP(), h5()), lambda: W(REP(), NOT(SOME(NOT(h5())))), POOLS["RG3"], ("h",))
    cmp("set-once `(h = 9: <5)` vs `(h: <5)`", r, lambda: W(SV(), C("h", lt(5), h="9")), lambda: W(SV(), h5()), POOLS["SVPOOL"], ("h",))
    cmp("set-once `(h = 3: !<5)` vs `(h: !<5)`", r, lambda: W(SV(), C("h", notlt(5), h="3")), lambda: W(SV(), C("h", notlt(5))), POOLS["SVPOOL"], ("h",))

print("== T6 L30 edges")
for r in ("24", "23.2"):
    cmp("REP `NOT (h: <0)` vs `(h: !<0)`", r, lambda: W(REP(), NOT(C("h", lt(0)))), lambda: W(REP(), C("h", notlt(0))), POOLS["RG3"])
    cmp("set-once SV `NOT (h: <0)` vs `(h: !<0)`", r, lambda: W(SV(), NOT(C("h", lt(0)))), lambda: W(SV(), C("h", notlt(0))), POOLS["SVPOOL"])
    cmp("set-once SV `NOT (h: <10)` vs `(h: !<10)`", r, lambda: W(SV(), NOT(C("h", lt(10)))), lambda: W(SV(), C("h", notlt(10))), POOLS["SVPOOL"])
    print("  SV `NOT (h: <10)` holds WHOLE %d, `(h: !<10)` %d of %d [rules %s]" % (holdsn(r, lambda: W(SV(), NOT(C("h", lt(10)))), POOLS["SVPOOL"]), holdsn(r, lambda: W(SV(), C("h", notlt(10))), POOLS["SVPOOL"]), len(POOLS["SVPOOL"]), r))

print("== T7 §4.4 computed label mnum := $mname.index over /(?<mname>Jan|Feb|Mar)?-(?<d>\\d)/")
MN = r"(?P<mname>Jan|Feb|Mar)?-(?P<d>\d)"
ix = lambda v: v is not None and ["Jan", "Feb", "Mar"].index(v) + 1 < 3
for r in ("24", "23.2"):
    show("`NOT (mnum: <3)` on `-5`", r, lambda: W(Pat(MN), NOT(C("mname", ix))), ("-5",) * 3)

print("== T8 sub-part numbers on the 3,906 pool (TP5)")
for r in ("24", "23.2"):
    cmp("L83 joint vs record under NOT", r, lambda: W(t2(), NOT(C(("h", "m"), lambda h, m: num(h) and num(m) and int(h) < 9 and int(m) < 30))), lambda: W(t2(), NOT(ANDC(C("h", lt(9)), C("m", lt(30))))), POOLS["TP5"], ("h", "m"))
    print("  `t2 & !q` holds WHOLE %d of %d [rules %s]" % (holdsn(r, lambda: D(t2(), q()), POOLS["TP5"]), len(POOLS["TP5"]), r))
    cmp("L95 `t2 & !q` vs `t2 & ((h, m = 0): !R)`", r, lambda: D(t2(), q()), lambda: W(t2(), C(("h", "m"), lambda h, m: not late(h, m), m="0")), POOLS["TP5"])
print("DONE-PROBE")
