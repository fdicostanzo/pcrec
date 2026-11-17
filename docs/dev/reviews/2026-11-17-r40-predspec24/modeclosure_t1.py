import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/modeclosure")
from mc_lib import *
W, Pat, C, Rep, OCC, lt, eq = (g(k) for k in ("W", "Pat", "C", "Rep", "OCC", "lt", "eq"))
strings = g("strings")
RG3 = strings("37;", 5)
CO = {"h<5": Tc("h", lt(5)), "g=a": Tc("g", eq("a"))}
# T1: W1c's NEW spelling: item with an OPTIONAL label, the loop over the conditioned item
print("T1 Rep(item := /(?<h>\\d)?;/ & (h: <5), +) engine vs PCRE2 callout model:",
      cmp(enkey(lambda: Rep(W(Pat(r"(?P<h>\d)?;"), C("h", lt(5))), 1), ("h",)), rxkey(r'(?:(?<h>\d)?(?C"h<5");)+', CO, ("h",)), RG3))
print("T1b same with *:", cmp(enkey(lambda: Rep(W(Pat(r"(?P<h>\d)?;"), C("h", lt(5))), 0), ("h",)), rxkey(r'(?:(?<h>\d)?(?C"h<5");)*', CO, ("h",)), RG3))
# T2: occurrences with a condition inside, optional label
ABP = strings("ab ", 5)
print("T2 occurrences(/(?<g>a)?b/ & (g: \"a\"), min=1) engine vs PCRE2:",
      cmp(enkey(lambda: OCC(W(Pat(r"(?P<g>a)?b"), C("g", eq("a"))), 1), ("g",)), rxkey(r'(?:[\s\S]*?(?<g>a)?b(?C"g=a"))+[\s\S]*', CO, ("g",)), ABP))
print("T2b min=0:",
      cmp(enkey(lambda: OCC(W(Pat(r"(?P<g>a)?b"), C("g", eq("a"))), 0), ("g",)), rxkey(r'(?:[\s\S]*?(?<g>a)?b(?C"g=a"))*[\s\S]*', CO, ("g",)), ABP))
