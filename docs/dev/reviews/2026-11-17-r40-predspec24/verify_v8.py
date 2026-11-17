import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/verify")
from vlib import *
gx = lambda: C("g", eq("x"))
inside = lambda: OCC(W(Pat(ABXYp), gx()), 1)
outside = lambda: W(OCC(Pat(ABXYp), 1), gx())
for r in ("24", "23.2"):
    with rules(r):
        print("L58/L61 rules %s: contains(r)&(g:x) on 'abx aby' WHOLE %s SEARCHED %s ; contains(r&(g:x)) WHOLE %s" % (
            r, aW(outside(), "abx aby"), aS(outside(), "abx aby", ("g",)), aW(inside(), "abx aby")))
print("L61 pair, rev 24, stretch:", cmp(strip(eng(inside)), strip(eng(outside)), XYPOOL))
# L100
PA = lambda: W(Pat(PABp), C("a", lt(5))); PB = lambda: W(Pat(PABp), C("a", lambda v: num(v) and int(v) > 10))
PAB = lambda: W(Pat(PABp), C("a", lt(5)), C("a", lambda v: num(v) and int(v) > 10))
with rules("24"):
    a, b, c = PA(), PB(), PAB()
    d = [s for s in DIG4 if ((whole_row(a, s) is not None) and (whole_row(b, s) is not None)) != (whole_row(c, s) is not None)]
    print("L100 rev 24 WHOLE differ:", len(d), "of", len(DIG4), "first", min(d, key=lambda x: (len(x), x)) if d else None)
# §8 when: complement body vs NOT body vs R.1.10
KHf = lambda: Pat(KHp)
def comp_body(): q = W(KHf(), h5()); return ALT(W(KHf(), h5(), pk()), D(KHf(), q))
def not_body(): return ALT(W(KHf(), h5(), pk()), W(KHf(), NOT(h5())))
def r110(): return WHEN(KHf(), h5(), pk())
print("§8 complement body vs NOT body (rev 24):", cmp(strip(eng(comp_body)), strip(eng(not_body)), KHPOOL))
print("§8 complement body vs R.1.10 when (rev 24):", cmp(strip(eng(comp_body)), strip(eng(r110)), KHPOOL))
with rules("24"):
    print("§8 holds WHOLE: complement body", sum(1 for s in KHPOOL if whole_row(comp_body(), s) is not None) if False else holds("24", comp_body, KHPOOL),
          "R.1.10", holds("24", r110, KHPOOL), "of", len(KHPOOL))
# R.2 default.unused (b) under NOT
SVf = lambda: Pat(SVp)
print("R.2 NOT (h = 9: <5) vs NOT (h: <5), rev 24, labels:", cmp(eng(lambda: W(SVf(), NOT(C("h", lt(5), h="9"))), ("h",)), eng(lambda: W(SVf(), NOT(C("h", lt(5)))), ("h",)), SVPOOL))
print("R.2 same under rev 23.2 (control):", cmp(eng(lambda: W(SVf(), NOT(C("h", lt(5), h="9"))), ("h",), "23.2"), eng(lambda: W(SVf(), NOT(C("h", lt(5)))), ("h",), "23.2"), SVPOOL))
# L30 edges on the set-once label
with rules("24"):
    for nm, mk in (("NOT (h: <0)", lambda: W(SVf(), NOT(C("h", lt(0))))), ("(h: !<0)", lambda: W(SVf(), C("h", lambda v: not lt(0)(v)))),
                   ("NOT (h: <10)", lambda: W(SVf(), NOT(C("h", lt(10))))), ("(h: !<10)", lambda: W(SVf(), C("h", lambda v: not lt(10)(v))))):
        print("L30 %-13s WHOLE on 'x' %s, on '3x' %s; holds %d of %d" % (nm, aW(mk(), "x"), aW(mk(), "3x"), holds("24", mk, SVPOOL), len(SVPOOL)))
