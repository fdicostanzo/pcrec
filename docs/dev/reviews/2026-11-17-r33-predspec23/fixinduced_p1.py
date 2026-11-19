import sys, io, contextlib
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec23/R/tree/docs/dev/lanes/predspec23b_evidence")
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec23/R/tree/docs/dev/lanes/predspec23_evidence")
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23b_model as B
pk = B.test("k", B.between(3, 7))

def branch_major(alt, s):
    # PCRE's order for an alternation at one start: branch 1 at every end it prefers, then branch 2
    for i in range(len(s) + 1):
        for br in alt.alt:
            for j in B.ends_pref(br, s, i):
                if B.accept(br, s, i, j): return (i, j)
    return None

def show(s, r): return None if r is None else "`%s`@%d" % (s[r[0]:r[1]], r[0])

for nm, c in [("(h: <5)", B.ptest("h", B.lt(5))), ("(h = 0: <5)", B.ptest("h", B.lt(5), "0"))]:
    W = B.when_body(c, pk)
    diff = [s for s in B.KHPOOL if B.searched(W, s) != branch_major(W, s)]
    print(nm, "| x & when (end-major, engine) vs expansion (branch-major) reported row differ on", len(diff),
          "of 1110; first", diff[:3])
    for s in ["5;1;9", "5;9"]:
        print("   on", repr(s), "engine", show(s, B.searched(W, s)), "| branch-major", show(s, branch_major(W, s)))
