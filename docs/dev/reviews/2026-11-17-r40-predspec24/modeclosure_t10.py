import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/modeclosure")
from mc_lib import *
W, Pat, C, OCC, lt, Atom, ALT = (g(k) for k in ("W", "Pat", "C", "OCC", "lt", "Atom", "ALT"))
strings = g("strings")
DSP = strings("129 ", 5)
CO = {"l<20": Tc("l", lt(20))}
print("Q8 `occurrences(atomic(B | A), min = 1) & (l: <20)` engine vs PCRE2:",
      cmp(enkey(lambda: W(OCC(Atom(ALT(Pat(r"(?P<l>\d\d)"), Pat(r"(?P<l>\d)\d"))), 1), C("l", lt(20))), ("l",)),
          rxkey(r'(?:[\s\S]*?(?>(?|(?<l>\d\d)|(?<l>\d)\d)))+[\s\S]*(?C"l<20")', CO, ("l",)), DSP))
