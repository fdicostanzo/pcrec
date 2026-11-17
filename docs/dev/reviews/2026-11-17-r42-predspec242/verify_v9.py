import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/verify/w")
from eng import *
for mn in (0, 1):
    f = ekey(lambda mn=mn: W(OCC(Pat(r"(?P<g>a)?b"), mn), C("g", eq("a"))), ("g",))
    print("occurrences(/(?<g>a)?b/, min=%d) & (g: \"a\") on `abb`: WHOLE %s ; SEARCHED %s ; FIND-ALL %s" % (mn, f("WHOLE", "abb"), f("SEARCHED", "abb"), f("FIND-ALL", "abb")))
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
import pcre2h as P
seen = {}
def t(c):
    gs, ps = c.span("g"), c.span("ps")
    own = c.get("g") if (gs is not None and ps is not None and gs[0] >= ps[0]) else None
    seen["g"] = own; seen["ps"] = ps
    return own == "a"
rx = P.Pcre(r'(?:[\s\S]*?(?<ps>)(?<g>a)?b)*[\s\S]*(?C"t")', {"t": t})
print("libpcre2 one-pattern helper model WHOLE on `abb`:", rx.match("abb", 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED), seen)
