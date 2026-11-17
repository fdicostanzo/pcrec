import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/modeclosure")
from mc_lib import *
W, Pat, C, lt, NOT, ANDC, D = (g(k) for k in ("W", "Pat", "C", "lt", "NOT", "ANDC", "D"))
strings = g("strings")
SV = strings("37x ", 4)
AH = strings("abc37", 3)
CO = {"h<5": Tc("h", lt(5)), "d0": lambda c: lt(5)("0"), "k<5": Tc("k", lt(5)), "dx!": lambda c: not lt(5)("x"), "h!<5": Tc("h", lambda v: not lt(5)(v))}
# DEFAULTS as plain PCRE: a conditional group on whether h is set
print("DF1 `/(?<h>\\d)?x/ & (h = 0: <5)` engine vs PCRE2 `(?<h>\\d)?x(?(<h>)(?C\"h<5\")|(?C\"d0\"))`:",
      cmp(enkey(lambda: W(Pat(r"(?P<h>\d)?x"), C("h", lt(5), h="0")), ("h",)), rxkey(r'(?<h>\d)?x(?(<h>)(?C"h<5")|(?C"d0"))', CO, ("h",)), SV))
print("DF2 `/a(?<h>\\d)|b(?<k>\\d)|c/ & (h = 0: <5) & (k: <5)` engine vs PCRE2 conditional:",
      cmp(enkey(lambda: W(Pat(r"a(?P<h>\d)|b(?P<k>\d)|c"), C("h", lt(5), h="0"), C("k", lt(5))), ("h", "k")),
          rxkey(r'(?:a(?<h>\d)|b(?<k>\d)|c)(?(<h>)(?C"h<5")|(?C"d0"))(?C"k<5")', CO, ("h", "k")), AH))
print("DF3 `(h = \"x\": !<5)` engine vs PCRE2 conditional:",
      cmp(enkey(lambda: W(Pat(r"(?P<h>\d)?x"), C("h", lambda v: not lt(5)(v), h="x")), ("h",)), rxkey(r'(?<h>\d)?x(?(<h>)(?C"h!<5")|(?C"dx!"))', CO, ("h",)), SV))
# ONE negation: (h: !<5) = presence & NOT (h: <5)
anyv = lambda v: True
print("NG1 `(h: !<5)` vs `(h: /.*/) & NOT (h: <5)` on /(?<h>\\d)?x/:",
      cmp(enkey(lambda: W(Pat(r"(?P<h>\d)?x"), C("h", lambda v: not lt(5)(v))), ("h",)), enkey(lambda: W(Pat(r"(?P<h>\d)?x"), C("h", anyv), NOT(C("h", lt(5)))), ("h",)), SV))
