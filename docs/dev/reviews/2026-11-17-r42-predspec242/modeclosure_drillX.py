import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from eng import *
from um import ukey, strings
lt5 = lambda v: v is not None and num(v) and int(v) < 5
NP = strings("37;,", 5); RG = strings("37;", 5); SX = strings("37; ", 4)
# (1) inner views and an item condition, model U' = the test placed where the pass's own h is decided (fresh per pass)
TC = {"t": lambda v: lt5(v["h"]), "no": lambda v: False}
TCn = {"t": lambda v: not lt5(v["h"]), "no": lambda v: True}
ITEMO, INNER = r"(?P<h>\d)?;", r"(?:(?P<h>\d)?;)*"
LAST = lambda: "(?:(?<h>\\d)(?C\"t\")|(?C\"no\"));"
V = [
 ("view (i) every inner pass `/(?:(?:${item})*,)*/`, item := `/(?<h>\\d)?;/ & (h: <5)`", lambda c: Rep(Seq(Rep(W(Pat(ITEMO), c()), 0), Pat(",")), 0), "(?:(?:%s)*,)*" % LAST()),
 ("view (ii) the inner loop's last pass in each outer pass `/(?:${inner},)*/`, inner := INNER & (h: <5)", lambda c: Rep(Seq(W(Pat(INNER), c()), Pat(",")), 0), "(?:(?:(?:(?:\\d)?;)*%s|(?C\"no\")),)*" % LAST()),
 ("in an occurrences argument: `occurrences(/(?:(?<h>\\d)?;)+/ & (h: <5), min = 1)`", lambda c: OCC(W(Pat(r"(?:(?P<h>\d)?;)+"), c()), 1), "(?:[\\s\\S]*?(?:(?:\\d)?;)*%s)+[\\s\\S]*" % LAST()),
]
for nm, mk, up in V:
    for cn, ec, tc in (("(h: <5)", lambda: h5(), TC), ("NOT (h: <5)", lambda: NOT(h5()), TCn)):
        fe = ekey(lambda mk=mk, ec=ec: mk(ec), ())
        fu = ukey(up, tc, ())
        pool = SX if "occurrences" in nm else NP
        d, n = diff(fe, fu, pool)
        print("X %s with `%s`: engine vs model U' /%s/ (holds and stretch): %s %s" % (nm, cn, up, d, "EQUAL" if n == 0 else "DIFFER"))
    sys.stdout.flush()
# (2) a lookahead holding a loop, inside a loop: outermost view through the lookahead
b  = lambda n: ("(?<h>\\d)?;" if n else "(?:\\d)?;")
U0 = "(?:(?:%s)*%s)?" % (b(0), b(0)); U1 = "(?:(?:%s)*%s)?" % (b(0), b(1))
LP_ = r"(?:(?=(?:(?P<h>\d)?;)*,)[\d;]*,)*"
LPu = "(?:(?:(?=%s,)[\\d;]*,)*(?=%s,)[\\d;]*,)?" % (U0, U1)
for cn, ec, uc in (("(h: <5)", lambda: h5(), '(?C"t")'), ("NOT (h: <5)", lambda: NOT(h5()), '(?!(?C"t"))')):
    fe = ekey(lambda ec=ec: W(Pat(LP_), ec()), ("h",)); fu = ukey(LPu + uc, {"t": lambda v: lt5(v["h"])}, ("h",))
    d, n = diff(fe, fu, NP); print("X a loop inside a LOOKAHEAD inside a loop /%s/ `& %s`: engine vs model U: %s %s" % (LP_, cn, d, "EQUAL" if n == 0 else "DIFFER"))
# (3) the black box (same-results) in NESTED places: each pair, each condition, each place, engine answers compared
CONDS = [("(h: <5)", lambda: h5()), ("NOT (h: <5)", lambda: NOT(h5())), ("(h = 0: <5)", lambda: C("h", lt(5), h="0")), ("(h: !<5)", lambda: C("h", lambda x: not lt(5)(x))), ("(h: \"3\")", lambda: C("h", eq("3")))]
PAIRS = [("SAME-1", lambda: Pat(r"(?:(?P<h>\d);)*"), lambda: Pat(r"(?:(?:\d;)*(?P<h>\d);)?")),
         ("SAME-2", lambda: Pat(r"(?P<h>\d)?;"), lambda: Pat(r"(?:(?P<h>\d)|);")),
         ("SAME-3", lambda: Pat(r"(?:(?P<h>\d)?;)*"), lambda: Pat(r"(?:(?:(?P<h>\d)?;)+)?")),
         ("SAME-4", lambda: Pat(r"(?:(?P<h>\d)?;)*"), lambda: Rep(Pat(r"(?P<h>\d)?;"), 0))]
PLACES = [("a hole loop `/(?:${X},)+/`, condition after", lambda X, c: W(Rep(Seq(X(), Pat(",")), 1), c()), NP),
          ("a hole loop, condition on the item `/(?:${X & c},)+/`", lambda X, c: Rep(Seq(W(X(), c()), Pat(",")), 1), NP),
          ("an occurrences argument, condition after", lambda X, c: W(OCC(Seq(X(), Pat(",")), 1), c()), NP),
          ("an occurrences argument, condition inside", lambda X, c: OCC(W(Seq(X(), Pat(",")), c()), 1), NP),
          ("the right operand of `&`", lambda X, c: W(AND(Pat(r"[\d;]*"), X()), c()), RG),
          ("atomic", lambda X, c: W(Atom(X()), c()), RG),
          ("a complement `/[\\d;]*/ & !(X & c)`", lambda X, c: D(Pat(r"[\d;]*"), W(X(), c())), RG)]
tot = {}
for pn, m1, m2 in PAIRS:
    for pl, mk, pool in PLACES:
        for cn, ec in CONDS:
            f1 = ekey(lambda m1=m1, mk=mk, ec=ec: mk(m1, ec), ("h",)); f2 = ekey(lambda m2=m2, mk=mk, ec=ec: mk(m2, ec), ("h",))
            d, n = diff(f1, f2, pool)
            tot[(pn, pl)] = tot.get((pn, pl), 0) + n
            if n: print("X SAME %s in %s `& %s`: %s DIFFER" % (pn, pl, cn, d))
        print("X SAME %s in %s: %d texts x modes differ over 5 conditions (%d texts)" % (pn, pl, tot[(pn, pl)], len(pool)))
        sys.stdout.flush()
