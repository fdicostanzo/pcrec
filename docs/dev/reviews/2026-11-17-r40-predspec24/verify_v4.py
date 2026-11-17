import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/verify")
from vlib import *
def admits(mkp, mkc, pool):
    with rules("24"):
        Pp, Pc = mkp(), mkc()
        w = [s for s in pool if whole_row(Pc, s) is not None and whole_row(Pp, s) is None]
        s_ = [s for s in pool if search(Pc, s) is not None and search(Pp, s) is None]
    f = lambda xs: "%d%s" % (len(xs), (" (first %r)" % min(xs, key=lambda x: (len(x), x))) if xs else "")
    return "WHOLE %s, SEARCHED %s of %d" % (f(w), f(s_), len(pool))
l20 = lambda: lab_l(lt(20))
base = lambda: W(Atom(alt_BA()), l20())
added = lambda: W(Atom(ALT(W(Pat(Bd), l20()), Pat(Ad))), l20())
print("(a) AD1 atomic((B&(l<20))|A)&(l<20) over atomic(B|A)&(l<20):", admits(base, added, DIG4))
with rules("24"):
    print("(a) on 25: base", aW(base(), "25"), "added", aW(added(), "25"), aS(added(), "25", ("l",)))
b2 = lambda: AND(Atom(Pat(r"(?P<a>\d+)")), Pat(r"1"))
a2 = lambda: AND(Atom(W(Pat(r"(?P<a>\d+)"), C("a", lt(10)))), Pat(r"1"))
print("(a) SIM-5 atomic(/(?<a>\\d+)/ & (a:<10)) & /1/ over atomic(/(?<a>\\d+)/) & /1/:", admits(b2, a2, DIG4))
# PCRE2 check of AD1 on 25: (?>(?|(?<l>\d\d)(?C"l<20")|(?<l>\d)\d))(?C"l<20")
co = {"l<20": Tc("l", lt(20))}
r1 = P.Pcre(r'(?>(?|(?<l>\d\d)|(?<l>\d)\d))(?C"l<20")', co); r2 = P.Pcre(r'(?>(?|(?<l>\d\d)(?C"l<20")|(?<l>\d)\d))(?C"l<20")', co)
print("(a) PCRE2 WHOLE 25: without", r1.whole("25"), "with inner callout", r2.whole("25"))
# (b) G vs L inside atomic, and FIND-ALL at top
Gp, Lp = r"(?P<h>\d+)", r"(?P<h>\d+?)"
h50 = lambda: C("h", lt(50))
print("(b) SP1 G&(h<50) vs L&(h<50):", cmp(eng(lambda: W(Pat(Gp), h50()), ("h",)), eng(lambda: W(Pat(Lp), h50()), ("h",)), DSP))
print("(b) SP2 atomic(G)&(h<50) vs atomic(L)&(h<50):", cmp(eng(lambda: W(Atom(Pat(Gp)), h50()), ("h",)), eng(lambda: W(Atom(Pat(Lp)), h50()), ("h",)), DSP))
print("(b) plain G vs L (no condition), WHOLE labels:", cmp(eng(lambda: Pat(Gp), ("h",)), eng(lambda: Pat(Lp), ("h",)), DSP, ("WHOLE",)))
S1, S2 = r"(?P<a>\d)|(?P<b>\d)", r"(?P<a>\d)"
print("(b) dead branch plain S1 vs S2 (labels a,b):", cmp(eng(lambda: Pat(S1), ("a", "b")), eng(lambda: Pat(S2), ("a", "b")), DIG4))
print("(b) dead branch S1&(b:\"1\") vs S2&(b:\"1\"):", cmp(eng(lambda: W(Pat(S1), C("b", eq("1"))), ("a", "b")), eng(lambda: W(Pat(S2), C("b", eq("1"))), ("a", "b")), DIG4))
pS1 = pc(r'(?<a>\d)(?C"b=1")|(?<b>\d)(?C"b=1")', {"b=1": Tc("b", eq("1"))}, ("a", "b"))
print("(b) PCRE2 S1 & (b:\"1\") on '1':", pS1("WHOLE", "1"))
# (c) atomic(t2) & !q
with rules("24"):
    At = D(Atom(mk_t2()), mk_q()); Pl = D(mk_t2(), mk_q())
    print("(c) atomic(t2)&!q: WHOLE 9:30", aW(At, "9:30"), "SEARCHED", aS(At, "9:30", ("h", "m")), "FIND-ALL", aF(At, "9:30 9:15", ("h",)))
    print("(c) t2&!q: SEARCHED", aS(Pl, "9:30", ("h", "m")))
