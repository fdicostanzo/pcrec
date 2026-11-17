import sys, io, contextlib, re
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec23/R/tree/docs/dev/lanes/predspec23_evidence")
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23_model as M
pool = M.strings("3xy ", 4)
# (H) the label o is set by the operand /(?<o>\d)x|y/ but by no match of the PROGRAM /(?<o>\d)x|y/ & /y/
yfilter = lambda s, i, j: re.fullmatch("y", s[i:j]) is not None
for name, c in [("(o = \"1\": <5)", M.test("o", M.lt(5), "1")), ("(o: <5)", M.test("o", M.lt(5))),
                ("NOT (o = \"9\": <5)", M.NOT(M.test("o", M.lt(5), "9")))]:
    P = M.Prog(r"(?P<o>\d)x|y", [c], [], [yfilter])
    base = M.Prog(r"(?P<o>\d)x|y", [], [], [yfilter])
    for mode in ["WHOLE", "SEARCHED"]:
        n, w = M.count(pool, lambda s: M.holds(mode, P, s))
        d, dw = M.count(pool, lambda s: M.holds(mode, P, s) != M.holds(mode, base, s))
        print("H", mode, "/(?<o>\\d)x|y/ & /y/ &", name, "holds", n, "of", len(pool), "; vs the program without it differ", d, dw)
# (5.2) NOT over an empty-intersection condition on a looped label: not constant
ZP = "(?:(?P<n>\\d),)*"
zpool = M.strings("37,", 4)
P = M.Prog(ZP, [M.NOT(M.rtest(M.lt(0)))], passre="(?P<n>\\d),", rep="n")
Q = M.Prog(ZP, [M.some(lambda v: True)], passre="(?P<n>\\d),", rep="n")
for mode in ["WHOLE", "SEARCHED"]:
    n, w = M.count(zpool, lambda s: M.holds(mode, P, s))
    d, dw = M.count(zpool, lambda s: M.holds(mode, P, s) != M.holds(mode, Q, s))
    print("5.2", mode, "NOT (n: <0) holds", n, "of", len(zpool), "first", repr(w), "; vs some((n: any text)) differ", d, dw)
for s in ["", "3,", "7,3,"]:
    print("  ", repr(s), M.rep("WHOLE", P, s), "|", M.rep("SEARCHED", P, s))
