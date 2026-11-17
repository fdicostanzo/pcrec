# V5: helper-group construction vs a label set by a lookaround inside a pass. Engine (eng.py), the helper-group
# construction (own iff h.start >= ps.start, as §R.6 / §R.10 describe it), my own unrolled control (only the last pass's
# copy of the body names h; PCRE's path-exact state then IS the last pass's own label).
import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/verify/w")
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
from eng import *
import pcre2h as P
lt5 = lambda v: v is not None and num(v) and int(v) < 5
WH = P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED
def helper(pat):
    def t(c):
        hs, ps = c.span("h"), c.span("ps")
        return lt5(c.get("h") if (hs is not None and ps is not None and hs[0] >= ps[0]) else None)
    return P.Pcre(pat + '(?C"t")', {"t": t})
def unrolled(pat):
    return P.Pcre(pat + '(?C"t")', {"t": lambda c: lt5(c.get("h"))})
CASES = [("LOOKBEHIND", r"(?:\d|(?<=(?P<h>\d))[a-z])*", r"(?:(?<ps>)(?:\d|(?<=(?<h>\d))[a-z]))*",
          r"(?:(?:\d|(?<=\d)[a-z])*(?:\d|(?<=(?<h>\d))[a-z]))?", ("3a", "7a", "3", "a", "3a7")),
         ("LOOKAHEAD", r"(?:(?=.(?P<h>\d))[a-z]|\d)*", r"(?:(?<ps>)(?:(?=.(?<h>\d))[a-z]|\d))*",
          r"(?:(?:(?=.\d)[a-z]|\d)*(?:(?=.(?<h>\d))[a-z]|\d))?", ("a3", "a7", "a3a3", "3"))]
for nm, ep, hp, up, texts in CASES:
    fe = ekey(lambda ep=ep: W(Pat(ep), h5()), ("h",))
    H, U = helper(hp), unrolled(up)
    for s in texts:
        print("%s `%s` WHOLE: engine %s ; helper %s ; unrolled %s" % (nm, s, fe("WHOLE", s), H.match(s, 0, WH) is not None, U.match(s, 0, WH) is not None))
