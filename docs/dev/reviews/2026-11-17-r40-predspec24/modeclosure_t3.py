import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/modeclosure")
from mc_lib import *
W, Pat, C, Rep, OCC, lt, eq, ALT, AND, Atom, D, ORC = (g(k) for k in ("W", "Pat", "C", "Rep", "OCC", "lt", "eq", "ALT", "AND", "Atom", "D", "ORC"))
strings, whole_row, search = g("strings"), g("whole_row"), g("search")
DSP = strings("129 ", 5); DIG4 = strings("0129", 4)
Bd, Ad = r"(?P<l>\d\d)", r"(?P<l>\d)\d"
# J1: join order with a lazy operand: stretch
GR, LZ = r"(?P<a>\d+)", r"(?P<c>\d+?)"
print("J1 `G & L` vs `L & G` (G := /(?<a>\\d+)/, L := /(?<c>\\d+?)/), stretch only:",
      cmp(enkey(lambda: AND(Pat(GR), Pat(LZ)), ()), enkey(lambda: AND(Pat(LZ), Pat(GR)), ()), DSP))
# J2: join order inside atomic: holding
PAB, PCD = r"(?P<a>\d+)(?P<b>\d+)", r"(?P<c>\d+)(?P<d>\d+)"
print("J2 `atomic(P & Q) & ((a: \"1\") | (c: \"1\"))` left vs right outer:",
      cmp(enkey(lambda: W(Atom(AND(Pat(PAB), Pat(PCD))), ORC(C("a", eq("1")), C("c", eq("1")))), ()),
          enkey(lambda: W(Atom(AND(Pat(PCD), Pat(PAB))), ORC(C("a", eq("1")), C("c", eq("1")))), ()), DSP))
print("J2b `atomic(G & L) & (c: \"1\")` left vs right outer:",
      cmp(enkey(lambda: W(Atom(AND(Pat(GR), Pat(LZ))), C("c", eq("1"))), ()),
          enkey(lambda: W(Atom(AND(Pat(LZ), Pat(GR))), C("c", eq("1"))), ()), DSP))
# DI: & distributing over | with a PATTERN on the left: X & (B | A) vs (X & B) | (X & A)
X, B1, A2 = r"\d+", r"\d", r"\d\d"
print("DI1 `X & (B | A)` vs `(X & B) | (X & A)`, X := /\\d+/, B := /\\d/, A := /\\d\\d/:",
      cmp(enkey(lambda: AND(Pat(X), ALT(Pat(B1), Pat(A2))), ()), enkey(lambda: ALT(AND(Pat(X), Pat(B1)), AND(Pat(X), Pat(A2))), ()), DSP))
print("DI2 `(B | A) & X` vs `(B & X) | (A & X)`:",
      cmp(enkey(lambda: AND(ALT(Pat(B1), Pat(A2)), Pat(X)), ()), enkey(lambda: ALT(AND(Pat(B1), Pat(X)), AND(Pat(A2), Pat(X))), ()), DSP))
# AD: adding a condition inside atomic admits a text (single match)
def admits(mkp, mkc, pool):
    with g("rules")("24"):
        Pp, Pc = mkp(), mkc()
        w = [s for s in pool if whole_row(Pc, s) is not None and whole_row(Pp, s) is None]
        s_ = [s for s in pool if search(Pc, s) is not None and search(Pp, s) is None]
    f = lambda xs: "%d%s" % (len(xs), (" (first %r)" % min(xs, key=lambda x: (len(x), x))) if xs else "")
    return "WHOLE %s, SEARCHED %s of %d" % (f(w), f(s_), len(pool))
print("AD1 `atomic((B & (l: <20)) | A) & (l: <20)` over `atomic(B | A) & (l: <20)`:",
      admits(lambda: W(Atom(ALT(Pat(Bd), Pat(Ad))), C("l", lt(20))), lambda: W(Atom(ALT(W(Pat(Bd), C("l", lt(20))), Pat(Ad))), C("l", lt(20))), DIG4))
print("AD2 `atomic(P & (a: \"1\")) & (b: <5)` over `atomic(P) & (b: <5)`:",
      admits(lambda: W(Atom(Pat(PAB)), C("b", lt(5))), lambda: W(Atom(W(Pat(PAB), C("a", eq("1")))), C("b", lt(5))), DIG4))
# SP: "whether a single match holds is some path survives": atomic(B | A) & (l: <20): a path (A, l=2) survives the condition, the program fails
