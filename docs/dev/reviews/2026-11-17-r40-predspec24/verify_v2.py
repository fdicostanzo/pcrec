import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/verify")
from vlib import *
L4 = ("a", "b", "c", "d")
left = lambda: W(AND(Pat(PABp), Pat(PCDp)), ORC(C("a", eq("1")), C("c", eq("1"))))
right = lambda: W(AND(Pat(PCDp), Pat(PABp)), ORC(C("a", eq("1")), C("c", eq("1"))))
print("(a) E5 left vs right, labels in WHOLE too:", cmp(eng(left, L4), eng(right, L4), DSP))
print("(a) E5 holding/stretch only:", cmp(strip(eng(left, L4)), strip(eng(right, L4)), DSP))
print("(a) WHOLE 111 left/right:", eng(left, L4)("WHOLE", "111"), eng(right, L4)("WHOLE", "111"))
G, Lz = r"(?P<a>\d+)", r"(?P<c>\d+?)"
GL = lambda: AND(Pat(G), Pat(Lz)); LG = lambda: AND(Pat(Lz), Pat(G))
print("(b) G&L vs L&G stretch:", cmp(strip(eng(GL)), strip(eng(LG)), DSP))
X, Bp, Ap = r"\d+", r"\d", r"\d\d"
xa = lambda: AND(Pat(X), ALT(Pat(Bp), Pat(Ap)))
xb = lambda: ALT(AND(Pat(X), Pat(Bp)), AND(Pat(X), Pat(Ap)))
ax = lambda: AND(ALT(Pat(Bp), Pat(Ap)), Pat(X))
bx = lambda: ALT(AND(Pat(Bp), Pat(X)), AND(Pat(Ap), Pat(X)))
print("(b) X&(B|A) vs (X&B)|(X&A):", cmp(strip(eng(xa)), strip(eng(xb)), DSP))
print("(b) (B|A)&X vs (B&X)|(A&X):", cmp(strip(eng(ax)), strip(eng(bx)), DSP))
# PCRE2 lookahead model of join-order (V19 style) for G & L: left outer, a lazy right
REST, TIE = r"(?<T>[\s\S]*+)", r"(?=\k<T>\z)"
pgl = pc(r'(*napla:(?<a>\d+)' + REST + r')(?<c>\d+?)' + TIE, {}, ())
plg = pc(r'(*napla:(?<c>\d+?)' + REST + r')(?<a>\d+)' + TIE, {}, ())
print("(b) PCRE2 model G&L vs engine G&L:", cmp(strip(pgl), strip(eng(GL)), DSP))
print("(b) PCRE2 model L&G vs engine L&G:", cmp(strip(plg), strip(eng(LG)), DSP))
# (c) L1 grouping: (x & S) & T vs x & (S & T), with P, Q and a third pattern; L39 swap = E5 above
R3 = r"(?P<e>\d)(?P<f>\d+)"
g1 = lambda: W(AND(AND(Pat(PABp), Pat(PCDp)), Pat(R3)), ORC(C("a", eq("1")), C("c", eq("1"))))
g2 = lambda: W(AND(Pat(PABp), AND(Pat(PCDp), Pat(R3))), ORC(C("a", eq("1")), C("c", eq("1"))))
print("(c) L1 grouping (P&Q)&R vs P&(Q&R), cond a|c, labels:", cmp(eng(g1, L4), eng(g2, L4), DSP))
