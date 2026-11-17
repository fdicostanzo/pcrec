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
