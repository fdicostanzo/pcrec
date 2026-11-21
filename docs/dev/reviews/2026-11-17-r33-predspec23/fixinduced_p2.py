import sys, io, contextlib
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec23/R/tree/docs/dev/lanes/predspec23_evidence")
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23_model as M
lt5 = M.lt(5)
def perpass(S, d=None, neg=False):
    # one pass (set-once inside the pass): (h = d: S), optionally under NOT
    def f(v):
        v = v if v is not None else d
        t = None if v is None else bool(S(v))
        return M.k_not(t) if neg else t
    return f
def none_of(f): return lambda r: not any(f(v) is True for v in r["_real"])
def some_of(f): return lambda r: any(f(v) is True for v in r["_real"])
mk = lambda c: M.Prog(M.REP, [c], passre=M.REPPASS, rep="h")
mks = lambda c: M.Prog(M.SV, [c])
# (1) a default OUTSIDE the set it meets changes answers once NOT wraps it (default.unused (b) premise)
SV = [("NOT (h: <5)", mks(M.NOT(M.test("h", lt5)))), ("NOT (h = 9: <5)", mks(M.NOT(M.test("h", lt5, "9")))),
      ("NOT (h = \"none\": <5)", mks(M.NOT(M.test("h", lt5, "none"))))]
REP = [("NOT (h: <5) rep", mk(M.NOT(M.rtest(lt5)))), ("NOT (h = \"x\": <5) rep", mk(M.NOT(M.rtest(lt5, "x")))),
       ("occurs.none(NOT (h: <5))", mk(none_of(perpass(lt5, None, True)))),
       ("occurs.none(NOT (h = \"x\": <5))", mk(none_of(perpass(lt5, "x", True)))),
       ("occurs.none((h = \"x\": !<5)) [R.1.7 narrower]", mk(none_of(perpass(M.notset(lt5), "x")))),
       ("some((h: <5))", mk(some_of(perpass(lt5)))), ("some((h = \"x\": <5))", mk(some_of(perpass(lt5, "x")))),
       ("NOT some((h = \"x\": <5))", mk(M.NOT(some_of(perpass(lt5, "x"))))), ("NOT some((h: <5))", mk(M.NOT(some_of(perpass(lt5)))))]
for mode in ["WHOLE", "SEARCHED"]:
    for pool, sp, base in [(M.SVPOOL, SV, 0), (M.REPPOOL, REP, None)]:
        for name, P in sp:
            c, w = M.count(pool, lambda s: M.holds(mode, P, s))
            print(mode, name, "holds", c, "first", repr(w))
    def d(pool, A, Bp):
        return M.count(pool, lambda s: M.holds(mode, A, s) != M.holds(mode, Bp, s))
    print(mode, "SV NOT (h:<5) vs NOT (h=9:<5) differ", d(M.SVPOOL, SV[0][1], SV[1][1]))
    print(mode, "REP NOT (h:<5) vs NOT (h=\"x\":<5) differ", d(M.REPPOOL, REP[0][1], REP[1][1]))
    print(mode, "REP occurs.none(NOT c) vs occurs.none(NOT (h=\"x\":c)) differ", d(M.REPPOOL, REP[2][1], REP[3][1]))
    print(mode, "REP occurs.none(NOT (h=\"x\":c)) vs narrower sentinel differ", d(M.REPPOOL, REP[3][1], REP[4][1]))
    print(mode, "REP some(c) vs some((h=\"x\":c)) differ", d(M.REPPOOL, REP[5][1], REP[6][1]))
    for s in ["x", "7x"]:
        print("  ROW", repr(s), mode, [(n, M.rep(mode, P, s)) for n, P in SV])
    for s in ["", ";", "7;", "3;;", "7;;"]:
        print("  ROW", repr(s), mode, [(n, M.rep(mode, P, s)) for n, P in REP[:5]])
