import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/verify")
from vlib import *
ITEMO = r"(?P<h>\d)?;"
REP = lambda: Pat(REPp)
w1c = lambda: Rep(W(Pat(ITEMO), h5()), 1)
w1d = lambda: W(REP(), SOME(h5()), NONE(NOT(h5())))
old = lambda: W(REP(), h5())
CO = {"h<5": Tc("h", lt(5))}
seen = []
def spy(c): seen.append((c.pos, c.get("h"))); return Tc("h", lt(5))(c)
rx = P.Pcre(r'(?:(?<h>\d)?(?C"t");)+', {"t": spy})
print("PCRE2 WHOLE 3;;:", rx.whole("3;;"), "callout (pos, h) seen:", seen)
print("engine W1c WHOLE 3;;:", eng(w1c, ("h",))("WHOLE", "3;;"), "SEARCHED:", eng(w1c, ("h",))("SEARCHED", "3;;"))
print("engine W1d WHOLE 3;;:", eng(w1d, ("h",))("WHOLE", "3;;"))
print("OLD (rev23.2) REP&(h:<5) WHOLE 3;;:", eng(old, ("h",), "23.2")("WHOLE", "3;;"))
pw1c = pc(r'(?:(?<h>\d)?(?C"h<5");)+', CO, ("h",))
print("engine W1c vs engine W1d (stretch):", cmp(strip(eng(w1c,("h",))), strip(eng(w1d,("h",))), RG3))
print("PCRE2 W1c vs engine W1d (stretch):", cmp(strip(pw1c), strip(eng(w1d,("h",))), RG3))
print("PCRE2 W1c vs OLD rev23.2 (stretch):", cmp(strip(pw1c), strip(eng(old,("h",),"23.2")), RG3))
print("PCRE2 W1c vs engine W1c (labels):", cmp(pw1c, eng(w1c,("h",)), RG3))
ABP = strings("ab ", 5)
COg = {"g=a": Tc("g", eq("a"))}
oc = lambda: OCC(W(Pat(r"(?P<x>(?P<g>a)?b)"), C("g", eq("a"))), 1)
po = pc(r'(?:[\s\S]*?(?<x>(?<g>a)?b)(?C"g=a"))+[\s\S]*', COg, ("x",))
print("occ twin on abb: engine", eng(oc, ("x",))("WHOLE","abb"), eng(oc,("x",))("SEARCHED","abb"), "; PCRE2", po("WHOLE","abb"), po("SEARCHED","abb"))
print("occ twin engine vs PCRE2 (label x):", cmp(eng(oc,("x",)), po, ABP))
