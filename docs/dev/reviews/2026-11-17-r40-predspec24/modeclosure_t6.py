import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/modeclosure")
from mc_lib import *
W, Pat, C, lt, eq, Atom, AND, ZERO, ALT, D = (g(k) for k in ("W", "Pat", "C", "lt", "eq", "Atom", "AND", "ZERO", "ALT", "D"))
strings = g("strings")
DSP = strings("129 ", 5)
# SP1: the spelling principle: two patterns with the same subjects and the same label settings, condition (h: <50)
print("SP1 `/(?<h>\\d+)/ & (h: <50)` vs `/(?<h>\\d+?)/ & (h: <50)` (same set, same labels):",
      cmp(enkey(lambda: W(Pat(r"(?P<h>\d+)"), C("h", lt(50))), ("h",)), enkey(lambda: W(Pat(r"(?P<h>\d+?)"), C("h", lt(50))), ("h",)), DSP))
# SP2: with atomic: holding
print("SP2 `atomic(/(?<h>\\d+)/) & (h: <50)` vs `atomic(/(?<h>\\d+?)/) & (h: <50)`:",
      cmp(enkey(lambda: W(Atom(Pat(r"(?P<h>\d+)")), C("h", lt(50))), ()), enkey(lambda: W(Atom(Pat(r"(?P<h>\d+?)")), C("h", lt(50))), ()), DSP))
# LAW inside atomic, labels of A read outside
PAB = r"(?P<a>\d+)(?P<b>\d+)"
print("LW1 `atomic(A & B) & (a: <5)` vs `atomic(A & (0: B)) & (a: <5)`, A := P, B := /1\\d*/:",
      cmp(enkey(lambda: W(Atom(AND(Pat(PAB), Pat(r"1\d*"))), C("a", lt(5))), ("a", "b")), enkey(lambda: W(Atom(ZERO(Pat(PAB), Pat(r"1\d*"))), C("a", lt(5))), ("a", "b")), DSP))
# complement inside atomic vs NOT (0: B)
print("LW2 `atomic(A & !B)` vs `atomic(A & NOT (0: B))` , A := P, B := /1\\d*/:",
      cmp(enkey(lambda: Atom(D(Pat(PAB), Pat(r"1\d*"))), ("a", "b")),
          enkey(lambda: Atom(g("Keep")(Pat(PAB), lambda row, s, i, e: g("whole_row")(Pat(r"1\d*"), s[i:e]) is None)), ("a", "b")), DSP))
