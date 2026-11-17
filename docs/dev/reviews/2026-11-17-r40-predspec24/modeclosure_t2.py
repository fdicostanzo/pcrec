import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/modeclosure")
from mc_lib import *
W, Pat, C, Rep, OCC, lt, eq = (g(k) for k in ("W", "Pat", "C", "Rep", "OCC", "lt", "eq"))
strings = g("strings")
CO = {"g=a": Tc("g", eq("a"))}
ABP = strings("ab ", 5)
# the hit's own text as a label (x), so the LAST hit is visible
print("T2c occurrences(/(?<x>(?<g>a)?b)/ & (g: \"a\"), min=1), label x = last hit: engine vs PCRE2:",
      cmp(enkey(lambda: OCC(W(Pat(r"(?P<x>(?P<g>a)?b)"), C("g", eq("a"))), 1), ("x",)), rxkey(r'(?:[\s\S]*?(?<x>(?<g>a)?b)(?C"g=a"))+[\s\S]*', CO, ("x",)), ABP))
