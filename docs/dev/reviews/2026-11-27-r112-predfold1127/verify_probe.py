import sys, os, builtins
M = os.path.abspath("docs/dev/lanes/predfold1127_evidence/predfold1127_model.py")
src = builtins.open(M, encoding="utf-8").read()
cut = src.rindex("# ==== CHECKS (a probe loads the model up to this line)")
g = {"__file__": M, "__name__": "probe"}
exec(compile(src[:cut], M, "exec"), g)
W = g["walk_v27"]
P = "P := /(?<d>\\d)/"
for e, b, r in [
 ("X & (X.d: <5)", [P, "X := [a = P] SEQ /;(?<d>\\d)/"], "X.d"),
 ("[n = /(?<g>(?<d>\\d))x(?<d>\\d)/] & (n.d: <5)", [], "n.d"),
 ("[n = (P SEQ /,(?<d>\\d)/)] & (n.d: <5)", [P], "n.d"),
 ("[n = ([a = P] SEQ /,(?<d>\\d)/)] & (n.d: <5)", [P], "n.d"),
 ("B(A) & (B.h: <5)", ["A := /(?<h>\\d)/", "B(rx) := /${[p = rx]}(?<h>\\d)/"], "B.h"),
]:
    try: v = W(e, b, r, array=False)
    except Exception as ex: v = ("EXC", repr(ex)[:300])
    print(e, "|", b, "=>", v)
