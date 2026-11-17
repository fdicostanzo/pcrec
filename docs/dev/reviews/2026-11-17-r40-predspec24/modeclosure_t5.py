import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/modeclosure")
from mc_lib import *
W, Pat, C, OCC, lt, eq, Rep, SOME, NONE, NOT = (g(k) for k in ("W", "Pat", "C", "OCC", "lt", "eq", "Rep", "SOME", "NONE", "NOT"))
strings = g("strings")
RG = strings("37;x", 5)
CO = {"h<5": Tc("h", lt(5))}
# N1: a label looped INSIDE an occurrences argument, read bare after occurrences (last pass of the last hit, PCRE)
print("N1 `occurrences(/(?:(?<h>\\d);)+/, min = 1) & (h: <5)` engine vs PCRE2 (last pass of the last hit):",
      cmp(enkey(lambda: W(OCC(Pat(r"(?:(?P<h>\d);)+"), 1), C("h", lt(5))), ("h",)),
          rxkey(r'(?:[\s\S]*?(?:(?<h>\d);)+)+[\s\S]*(?C"h<5")', CO, ("h",)), RG))
# N2: a label looped inside a Rep item (nested loop via a hole), read bare after the outer loop
print("N2 `/(?:${item})+/ & (h: <5)`, item := /(?:(?<h>\\d);)+x/ engine vs PCRE2:",
      cmp(enkey(lambda: W(Rep(Pat(r"(?:(?P<h>\d);)+x"), 1), C("h", lt(5))), ("h",)),
          rxkey(r'(?:(?:(?<h>\d);)+x)+(?C"h<5")', CO, ("h",)), RG))
# N3: a set-once label of the item read bare after the Rep loop (should equal: last pass)
print("N3 `/(?:${item})+/ & (h: <5)`, item := /(?<h>\\d);/ engine vs PCRE2:",
      cmp(enkey(lambda: W(Rep(Pat(r"(?P<h>\d);"), 1), C("h", lt(5))), ("h",)),
          rxkey(r'(?:(?<h>\d);)+(?C"h<5")', CO, ("h",)), RG))
