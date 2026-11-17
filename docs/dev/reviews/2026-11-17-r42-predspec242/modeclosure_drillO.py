import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from eng import *
from um import ukey, strings
pool = strings("ab ", 4)
X, Xn = r"(?P<g>a)?b?", "(?:a)?b?"
up = "(?:(?:[\\s\\S]*?%s)*[\\s\\S]*?(?<g>a)?b?)?[\\s\\S]*" % Xn
for cn, ec, uc in (("(g: \"a\")", lambda: C("g", eq("a")), '(?C"t")'), ("NOT (g: \"a\")", lambda: NOT(C("g", eq("a"))), '(?!(?C"t"))')):
    fe = ekey(lambda ec=ec: W(OCC(Pat(X)), ec()), ("g",))
    fu = ukey(up + uc, {"t": lambda v: v["g"] == "a"}, ("g",))
    d, n = diff(fe, fu, pool)
    print("O occurrences(/(?<g>a)?b?/) & %s (a NULLABLE argument): engine vs model U /%s/: %s %s" % (cn, up + uc, d, "EQUAL" if n == 0 else "DIFFER"))
    fe2 = ekey(lambda ec=ec: W(Rep(Pat(X), 0), ec()), ("g",))
    up2 = "(?:(?:%s)*(?<g>a)?b?)?" % Xn
    fu2 = ukey(up2 + uc, {"t": lambda v: v["g"] == "a"}, ("g",))
    d, n = diff(fe2, fu2, pool)
    print("O hole loop /(?:${x})*/, x := /(?<g>a)?b?/, & %s: engine vs model U /%s/: %s %s" % (cn, up2 + uc, d, "EQUAL" if n == 0 else "DIFFER"))
