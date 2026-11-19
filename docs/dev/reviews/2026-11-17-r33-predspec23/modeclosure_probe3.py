import sys, io, contextlib, itertools
D = "/var/tmp/pcrec-pcrec/scratch/crit-predspec23/R/tree/docs/dev/lanes/"
sys.path.insert(0, D + "predspec23_evidence")
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23_model as M
def kor(a, b): return M.k_not(M.k_and([M.k_not(a), M.k_not(b)]))
def collapse(c): return lambda r: (c(r) is True)
REP, RP = M.REP, M.REPPASS
atoms = [M.rtest(M.lt(5)), M.rtest(M.ge(5)), M.rtest(M.lt(5), "0"), M.some(M.lt(5)), M.none_(M.ge(5)), M.rtest(M.notset(M.lt(5)), "x")]
progs = []
for a, b in itertools.product(atoms, atoms):
    progs.append(("and", lambda r, a=a, b=b: M.k_and([a(r), b(r)])))
    progs.append(("or", lambda r, a=a, b=b: kor(a(r), b(r))))
n = diff = 0
for name, c in progs:
    for mode in ("WHOLE", "SEARCHED"):
        P1 = M.Prog(REP, [c], passre=RP, rep="h")
        # collapse every atom's UNKNOWN to FALSE: rebuild from collapsed atoms is equivalent to collapsing the result for &/| (monotone)
        P2 = M.Prog(REP, [collapse(c)], passre=RP, rep="h")
        P3 = M.Prog(REP, [], [M.Prog(REP, [c], passre=RP, rep="h")], passre=RP, rep="h")
        P4 = M.Prog(REP, [], [M.Prog(REP, [collapse(c)], passre=RP, rep="h")], passre=RP, rep="h")
        for s in M.REPPOOL:
            n += 1
            if M.holds(mode, P1, s) != M.holds(mode, P2, s) or M.holds(mode, P3, s) != M.holds(mode, P4, s): diff += 1
print("third value without NOT (& | over 6 atoms, plain and under complement), cases", n, "differ", diff)
# Kleene atom-level collapse: does collapsing each ATOM before & / | equal the original? (homomorphism check)
d2 = 0; n2 = 0
for a, b in itertools.product(atoms, atoms):
    for s in M.REPPOOL:
        for i in range(len(s)+1):
            for j in range(i, len(s)+1):
                r = M.row_at(M.Prog(REP, passre=RP, rep="h"), s, i, j)
                if r is None: continue
                n2 += 1
                for f in (lambda x, y: M.k_and([x, y]), kor):
                    if (f(a(r), b(r)) is True) != (f(a(r) is True, b(r) is True) is True): d2 += 1
print("atom-collapse homomorphism rows", n2, "differ", d2)
# NOT some(c) vs occurs.none(c), NOT (h:S) vs (h:!S) set-once
d3 = sum(1 for mode in ("WHOLE","SEARCHED") for s in M.REPPOOL
         if M.holds(mode, M.Prog(REP,[M.NOT(M.some(M.lt(5)))],passre=RP,rep="h"), s) != M.holds(mode, M.Prog(REP,[M.none_(M.lt(5))],passre=RP,rep="h"), s))
d4 = sum(1 for mode in ("WHOLE","SEARCHED") for s in M.SVPOOL for dflt in (None, "0", "9", "x")
         if M.holds(mode, M.Prog(M.SV,[M.NOT(M.test("h",M.lt(5),dflt))]), s) != M.holds(mode, M.Prog(M.SV,[M.test("h",M.notset(M.lt(5)),dflt)]), s))
print("NOT some vs occurs.none differ", d3, "of", 2*len(M.REPPOOL), "; set-once NOT (h=d:S) vs (h=d:!S) differ", d4, "of", 8*len(M.SVPOOL))
