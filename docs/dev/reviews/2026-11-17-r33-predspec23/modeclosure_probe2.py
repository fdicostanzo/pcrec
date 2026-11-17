import sys, io, contextlib, re
D = "/var/tmp/pcrec-pcrec/scratch/crit-predspec23/R/tree/docs/dev/lanes/"
sys.path.insert(0, D + "predspec23_evidence"); sys.path.insert(0, D + "predspec23b_evidence")
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23_model as M
    import predspec23b_model as B
T2 = M.T2
c = B.test("h", B.lt(5)); p = lambda r: True
br1 = B.P2(T2, [c, p]); br2 = B.P2(T2, [], [B.P2(T2, [c])])
alt = B.P2(T2, alt=[br1, br2])          # the evidence's reading: next branch when branch 1's filters reject
def nofb(s, i, j):                       # one parse of the regex x|x: branch 1 always parses; its filters decide
    return B.accept(br1, s, i, j)
for s in ["3", "7", "12"]:
    print("when-body on", s, "| evidence (fallback):", B.whole(alt, s), "| one-parse-no-fallback:", nofb(s, 0, len(s)))
