import sys, io, contextlib, re
D = "/var/tmp/pcrec-pcrec/scratch/crit-predspec23/R/tree/docs/dev/lanes/"
sys.path.insert(0, D + "predspec23_evidence"); sys.path.insert(0, D + "predspec23b_evidence")
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23_model as M
    import predspec23b_model as B
T2 = M.T2; q = M.q
# W1: NOT over a nested label program: inner absence turns into FALSE, so NOT admits a row with an absent inner label
X = r"(?P<x>[\d:]+)"
inq = lambda v: M.whole(q, v)
NOTx = M.Prog(X, [M.NOT(M.test("x", inq))])
setc = M.Prog(X, [M.test("x", lambda v: not inq(v))])
inner_not = M.Prog(X, [M.test("x", lambda v: M.whole(M.Prog(T2, [M.NOT(M.late)]), v))])
flat = M.Prog(T2, [M.NOT(M.late)])
for s in ["9", "9:30", "9:15"]:
    print("W1", s, "| P&NOT(x: q):", M.rep("WHOLE", NOTx, s), "/", M.rep("SEARCHED", NOTx, s),
          "| P&(x: !q):", M.rep("WHOLE", setc, s), "| P&(x: t2&NOT late):", M.rep("WHOLE", inner_not, s),
          "| flat t2&NOT late:", M.rep("WHOLE", flat, s), "/", M.rep("SEARCHED", flat, s))
# W2: adding a condition admits through find-all (records / occurrences hits)
N = B.P2(r"(?P<n>\d+)"); Nc = B.P2(r"(?P<n>\d+)", [B.test("n", B.lt(100))])
for s in ["1234", "123456", "1234 5"]:
    print("W2", s, "findall r:", B.fa(N, s), " r & (n: <100):", B.fa(Nc, s))
# W3: records item / contains argument as WHOLE (R.1.1) vs SEARCHED (role table row 7 / hole)
tq = M.Prog(T2, [], [q])
for s in ["9:30", "9:30 9:15"]:
    print("W3", s, "t2 & !q WHOLE:", M.rep("WHOLE", tq, s), " SEARCHED:", M.rep("SEARCHED", tq, s))
P2tq = B.P2(T2, [], [B.P2(T2, [lambda r: M.late(r)])])
print("W3 findall t2 & !q on 9:30:", B.fa(P2tq, "9:30"))
s = "9:30"
print("W3 contains arg WHOLE-of-stretch:", M.whole(tq, s), " searched-in-stretch:", M.searched(tq, s))
# W4: occurrences hits from PCRE's parse of the body with a STRING-SET hole: order of the set decides
SET = [str(i) for i in range(100)]
asc = "|".join(sorted(SET, key=len)); desc = "|".join(sorted(SET, key=len, reverse=True))
for s in ["1234", "123456"]:
    print("W4", s, "hits asc-order set:", [m.group() for m in re.finditer("(?:%s)" % asc, s)],
          " desc-order set:", [m.group() for m in re.finditer("(?:%s)" % desc, s)],
          " R22 find-all:", B.fa(Nc, s))
# W5: nullable B in text.none / !contains: engine skips empty stretches
ZP = r"(?:(?P<n>\d),)*"
Bz = M.Prog(ZP, [M.rtest(lambda v: M.numeral(v) and int(v) >= 5, "9")], passre=r"(?P<n>\d),", rep="n")
def eng_text_none(s): return not any(M.accept(Bz, s, k, l) for k in range(len(s) + 1) for l in range(k + 1, len(s) + 1))
def def_text_none(s): return not any(M.accept(Bz, s, k, l) for k in range(len(s) + 1) for l in range(k, len(s) + 1))
for s in ["", "1,", "a", "7,"]:
    print("W5", repr(s), "engine-form text.none(B):", eng_text_none(s), " with empty rows (R.1.2):", def_text_none(s),
          " B empty row at 0 accepted:", M.accept(Bz, s, 0, 0))
