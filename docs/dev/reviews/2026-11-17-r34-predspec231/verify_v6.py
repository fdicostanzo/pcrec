import os, sys, re, io, contextlib
L = "/var/tmp/pcrec-pcrec/scratch/crit-predspec231/tree/docs/dev/lanes"
sys.path.insert(0, L + "/predspec23b_evidence")
os.environ["PREDSPEC23B_SWAP"] = "0"; os.environ["PREDSPEC23B_SABOTAGE"] = "0"
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23b_model as B
M = B.M
P2, test, ptest, NOT, lt = B.P2, B.test, B.ptest, B.NOT, B.lt
notS = lambda S: (lambda v: not S(v))
SV, SVPOOL = M.SV, M.SVPOOL
REP, REPPOOL, REPPASS = M.REP, M.REPPOOL, r"(?P<h>\d)?;"
def sv(conds=(), comps=()): return P2(SV, conds, comps)
def rp(conds=(), comps=()): return P2(REP, conds, comps, passre=REPPASS)
def cmp(name, pool, a, b):
    w = sum(1 for s in pool if B.whole(a, s) != B.whole(b, s))
    se = sum(1 for s in pool if B.searched(a, s) != B.searched(b, s))   # reported row (None = fails)
    print("%-62s WHOLE differ %d | SEARCHED reported-row differ %d (of %d)" % (name, w, se, len(pool)))
# SV, d = 9 (outside <5)
cmp("SV P & !(P & (h = 9: <5)) vs P & !(P & (h: <5))", SVPOOL,
    sv(comps=[sv([test("h", lt(5), "9")])]), sv(comps=[sv([test("h", lt(5))])]))
cmp("SV (h = 3: !<5) vs (h: !<5)", SVPOOL, sv([test("h", notS(lt(5)), "3")]), sv([test("h", notS(lt(5)))]))
cmp("SV NOT NOT (h = 9: <5) vs NOT NOT (h: <5)", SVPOOL, sv([NOT(NOT(test("h", lt(5), "9")))]), sv([NOT(NOT(test("h", lt(5))))]))
cmp("SV control NOT (h = 9: <5) vs NOT (h: <5)", SVPOOL, sv([NOT(test("h", lt(5), "9"))]), sv([NOT(test("h", lt(5)))]))
# REP, d = "x" (outside <5); looped test = Kleene AND over pass rows
cmp("REP P & !(P & (h = x: <5)) vs P & !(P & (h: <5))", REPPOOL,
    rp(comps=[rp([ptest("h", lt(5), "x")])]), rp(comps=[rp([ptest("h", lt(5))])]))
cmp("REP (h = 3: !<5) vs (h: !<5)", REPPOOL, rp([ptest("h", notS(lt(5)), "3")]), rp([ptest("h", notS(lt(5)))]))
cmp("REP control NOT (h = x: <5) vs NOT (h: <5)", REPPOOL, rp([NOT(ptest("h", lt(5), "x"))]), rp([NOT(ptest("h", lt(5)))]))
