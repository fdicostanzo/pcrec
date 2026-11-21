import sys, io, contextlib, re
D = "/var/tmp/pcrec-pcrec/scratch/crit-predspec23/R/tree/docs/dev/lanes/"
sys.path.insert(0, D + "predspec23_evidence"); sys.path.insert(0, D + "predspec23b_evidence")
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23_model as M
    import predspec23b_model as B

def modes(P, s, eng): return "%s / %s" % (eng.rep("WHOLE", P, s), eng.rep("SEARCHED", P, s))
def differ(eng, pool, P, Q):
    return [sum(1 for s in pool if eng.holds(m, P, s) != eng.holds(m, Q, s)) for m in ("WHOLE", "SEARCHED")]

print("== V-3 pair: /(?:(?<h>\\d);)+/ & /\\d;/ vs /(?<h>\\d);/")
f1 = lambda s, i, j: re.fullmatch(r"\d;", s[i:j]) is not None
pool = M.strings("37;x", 4)
for nm, cl, cs in [("(h: <5)", B.ptest("h", B.lt(5)), B.test("h", B.lt(5))),
                   ("NOT (h: <5)", B.NOT(B.ptest("h", B.lt(5))), B.NOT(B.test("h", B.lt(5))))]:
    P = B.P2(r"(?:(?P<h>\d);)+", [cl], [], [f1], passre=r"(?P<h>\d);")
    Q = B.P2(r"(?P<h>\d);", [cs])
    print(nm, "differ WHOLE/SEARCHED over", len(pool), ":", differ(B, pool, P, Q))

print("== V-5 SV: NOT (h: <5) vs NOT (h = 9: <5)")
a = M.Prog(M.SV, [M.NOT(M.test("h", M.lt(5)))]); b = M.Prog(M.SV, [M.NOT(M.test("h", M.lt(5), "9"))])
print("on x:", modes(a, "x", M), "|", modes(b, "x", M), "| differ over SVPOOL", differ(M, M.SVPOOL, a, b))

print("== V-8/9 find-all /(?<n>\\d+)/ with and without (n: <100)")
P0 = B.P2(r"(?P<n>\d+)"); P1 = B.P2(r"(?P<n>\d+)", [B.test("n", B.lt(100))])
for s in ["1234", "123456"]:
    print(s, "plain", B.fa(P0, s), "| with (n: <100)", B.fa(P1, s))

print("== V-10 X & NOT (x: q) on 9 vs flat t2 & NOT late")
q = M.Prog(M.T2, [M.late])
xin = lambda r: None if r.get("x") is None else M.whole(q, r["x"])
X = r"(?P<x>[\d:]+)"
for s in ["9", "9:15", "9:30"]:
    print(s, "X & NOT (x: q):", modes(M.Prog(X, [M.NOT(xin)]), s, M), "| t2 & NOT late:", modes(M.Prog(M.T2, [M.NOT(M.late)]), s, M))

print("== V-11 when body: fallthrough vs one parse without fallthrough (WHOLE)")
c = B.test("h", B.lt(5)); p = lambda r: True
br1 = B.P2(M.T2, [c, p]); br2 = B.P2(M.T2, [], [B.P2(M.T2, [c])])
alt = B.P2(M.T2, alt=[br1, br2])
for s in ["3", "7", "12"]:
    print(s, "fallthrough:", B.whole(alt, s), "| no fallthrough:", B.accept(br1, s, 0, len(s)))
pk = B.test("k", B.between(3, 7))
def branch_major(W, s):
    for i in range(len(s) + 1):
        for br in W.alt:
            for j in B.ends_pref(br, s, i):
                if B.accept(br, s, i, j): return (i, j)
    return None
W = B.when_body(B.ptest("h", B.lt(5)), pk)
for s in ["5;1;9"]:
    r1, r2 = B.searched(W, s), branch_major(W, s)
    print(s, "engine end-major", s[r1[0]:r1[1]], r1, "| branch-major", s[r2[0]:r2[1]], r2)

print("== V-12 nullable B: text.none by definition (empty rows included) vs engine form (non-empty only)")
Bn = M.Prog(r"(?:(?P<n>\d),)*", [M.rtest(M.ge(5), "9")], passre=r"(?P<n>\d),", rep="n")
for s in ["", "1,", "a"]:
    incl = any(M.accept(Bn, s, k, l) for k in range(len(s) + 1) for l in range(k, len(s) + 1))
    excl = any(M.accept(Bn, s, k, l) for k in range(len(s) + 1) for l in range(k + 1, len(s) + 1))
    print(repr(s), "text.none def:", not incl, "| engine form:", not excl)

print("== V-13 pointwise !c (neither = difference) vs condition NOT on x")
pw = M.Prog(M.SV, [], [M.Prog(M.SV, [M.test("h", M.lt(5))])])
nt = M.Prog(M.SV, [M.NOT(M.test("h", M.lt(5)))])
print("on x: pointwise", modes(pw, "x", M), "| NOT", modes(nt, "x", M), "| differ SVPOOL", differ(M, M.SVPOOL, pw, nt))

print("== V-14 /(?<o>\\d)x|y/ & /y/ & (o = \"1\": <5)")
fy = lambda s, i, j: re.fullmatch("y", s[i:j]) is not None
R0 = M.Prog(r"(?P<o>\d)x|y", [], [], [fy]); R1 = M.Prog(r"(?P<o>\d)x|y", [M.test("o", M.lt(5), "1")], [], [fy])
R2 = M.Prog(r"(?P<o>\d)x|y", [M.test("o", M.lt(5))], [], [fy])
print("differ default-vs-none", differ(M, M.SVPOOL + M.strings("1y", 3), R0, R1),
      "| holds plain (W,S)", [sum(1 for s in M.SVPOOL + M.strings("1y", 3) if M.holds(m, R0, s)) for m in ("WHOLE", "SEARCHED")],
      "| (o: <5) holds", [sum(1 for s in M.SVPOOL + M.strings("1y", 3) if M.holds(m, R2, s)) for m in ("WHOLE", "SEARCHED")])

print("== V-15 NOT (n: <0) on /(?:(?<n>\\d),)*/")
N = M.Prog(r"(?:(?P<n>\d),)*", [M.NOT(M.rtest(M.lt(0)))], passre=r"(?P<n>\d),", rep="n")
for s in ["", "3,", "3,7,"]:
    print(repr(s), modes(N, s, M))
print("sentinel occurs.none((h = 'x': !<10)) on /(?:(?<h>\\d)?;)*/")
Sn = M.Prog(M.REP, [M.none_(M.notset(M.lt(10)), "x")], passre=M.REPPASS, rep="h")
for s in ["", ";", "7;"]:
    print(repr(s), modes(Sn, s, M))

print("== V-16 on 10: NOT joint vs NOT record (S = <9, T = <30)")
def jt(r):
    if r.get("h") is None or r.get("m") is None: return None
    return M.lt(9)(r["h"]) and M.lt(30)(r["m"])
rec = M.AND(M.test("h", M.lt(9)), M.test("m", M.lt(30)))
J = M.Prog(M.T2, [M.NOT(jt)]); Rr = M.Prog(M.T2, [M.NOT(rec)])
print("on 10: joint", modes(J, "10", M), "| record", modes(Rr, "10", M), "| differ T2POOL", differ(M, M.T2POOL, J, Rr))
J0 = M.Prog(M.T2, [jt]); R0 = M.Prog(M.T2, [rec])
print("without NOT differ", differ(M, M.T2POOL, J0, R0))
