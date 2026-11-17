#!/usr/bin/env python3
# fixinduced probe: `t & (c1 | c2)` (condition-or, Kleene) vs `(t & c1) | (t & c2)` (pattern | of filtered branches,
# branch-order) vs the §3.5 array form `t & [c1, c2]` (= the second, "pointwise").
import os, sys, io, contextlib
R = "/var/tmp/pcrec-pcrec/scratch/crit-predspec231/tree/docs/dev/lanes/predspec23c_evidence"
sys.path.insert(0, R)
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23c_model as C
B = C.B
def kor(vs):
    if any(v is True for v in vs): return True
    if any(v is None for v in vs): return None
    return False
def OR(*cs): return lambda r: kor([c(r) for c in cs])
c1 = B.ptest("h", B.lt(5))          # (h: <5) on looped h
c2 = B.test("k", B.lt(5))           # (k: <5)
KH, KHP = B.KH, B.KHP
F_or = B.P2(KH, [OR(c1, c2)], passre=KHP)
F_alt = B.P2(KH, alt=[B.P2(KH, [c1], passre=KHP), B.P2(KH, [c2], passre=KHP)])
def rep(P, s):
    w = "HOLDS" if B.whole(P, s) else "FAILS"
    r = B.search_from(P, s, 0)      # branch-major (C installed it)
    return "WHOLE %s | SEARCHED %s" % (w, "FAILS" if r is None else "HOLDS `%s`@%d" % (s[r[0]:r[1]], r[0]))
for s in ["3;1;9", "3;9", "7;1;9", "3"]:
    print("on `%s`: t & ((h: <5) | (k: <5)) %s ;  (t & (h: <5)) | (t & (k: <5)) %s" % (s, rep(F_or, s), rep(F_alt, s)))
for mode in ["WHOLE", "SEARCHED"]:
    d = [s for s in B.KHPOOL if B.holds(mode, F_or, s) != B.holds(mode, F_alt, s)]
    print(mode, "holds differ", len(d))
d = [s for s in B.KHPOOL if B.search_from(F_or, s, 0) != B.search_from(F_alt, s, 0)]
print("SEARCHED reported row differ", len(d), "of", len(B.KHPOOL), "first", min(d, key=lambda x: (len(x), x)) if d else None)
# NOT over each: NOT (c1 | c2) is defined (Kleene); the array/branch form has no NOT spelling except pattern complement
F_notor = B.P2(KH, [B.NOT(OR(c1, c2))], passre=KHP)
F_comp = B.P2(KH, [], [F_alt], passre=KHP)   # t & !((t & c1) | (t & c2))
for mode in ["WHOLE", "SEARCHED"]:
    d = [s for s in B.KHPOOL if B.holds(mode, F_notor, s) != B.holds(mode, F_comp, s)]
    print(mode, "NOT(c1|c2) vs t & !(branches) holds differ", len(d), "first", min(d, key=lambda x: (len(x), x)) if d else None)
