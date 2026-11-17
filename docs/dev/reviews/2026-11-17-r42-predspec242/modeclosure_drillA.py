import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from eng import *
from um import ukey, strings
lt5 = lambda v: v is not None and num(v) and int(v) < 5
RG = strings("37;", 5); NP = strings("37;,", 5); R4 = strings("37;", 4); A4 = strings("37a", 4)
b  = lambda n: ("(?<h>\\d)?;" if n else "(?:\\d)?;")            # REP's body, named or not
U  = lambda: "(?:(?:%s)*%s)?" % (b(0), b(1))                   # (?:B)* unrolled
U0 = lambda: "(?:(?:%s)*%s)?" % (b(0), b(0))
CASES = [
 ("Q1 `*`", r"(?:(?P<h>\d)?;)*", U(), RG),
 ("Q2 `{0,1}` (not a loop)", r"(?:(?P<h>\d)?;){0,1}", "(?:%s)?" % b(1), RG),
 ("Q3 `{1}` (not a loop)", r"(?:(?P<h>\d)?;){1}", "(?:%s)" % b(1), RG),
 ("Q4 `{0,2}`", r"(?:(?P<h>\d)?;){0,2}", "(?:(?:%s)?%s)?" % (b(0), b(1)), RG),
 ("Q5 `{2}`", r"(?:(?P<h>\d)?;){2}", "%s%s" % (b(0), b(1)), RG),
 ("Q6 lazy `*?`", r"(?:(?P<h>\d)?;)*?", "(?:(?:%s)*?%s)??" % (b(0), b(1)), RG),
 ("Q7 possessive `*+`", r"(?:(?P<h>\d)?;)*+", "(?>(?:(?:%s)*%s)?)" % (b(0), b(1)), RG),
 ("Q8 `(?:B+)?`, the ? outside the loop", r"(?:(?:(?P<h>\d)?;)+)?", "(?:(?:%s)*%s)?" % (b(0), b(1)), RG),
 ("Q9 an optional group in the body `(?:(?:(?<h>\\d);)?,)*`", r"(?:(?:(?P<h>\d);)?,)*", "(?:(?:(?:\\d;)?,)*(?:(?<h>\\d);)?,)?", NP),
 ("Q10 `{1}` inside `*`", r"(?:(?:(?P<h>\d)?;){1})*", U(), RG),
 ("Q11 `{2}` inside `*` (two depths)", r"(?:(?:(?P<h>\d)?;){2},)*", "(?:(?:%s%s,)*%s%s,)?" % (b(0), b(0), b(0), b(1)), NP),
 ("N1 two depths, literal", r"(?:(?:(?P<h>\d)?;)*,)*", "(?:(?:%s,)*%s,)?" % (U0(), U()), NP),
 ("N2 two depths, outer lazy", r"(?:(?:(?P<h>\d)?;)*,)*?", "(?:(?:%s,)*?%s,)??" % (U0(), U()), NP),
 ("N3 two depths, inner possessive", r"(?:(?:(?P<h>\d)?;)*+,)*", "(?:(?:(?>%s),)*(?>%s),)?" % (U0(), U()), NP),
 ("N4 two depths, outer `{0,1}` (one loop)", r"(?:(?:(?P<h>\d)?;)*,)?", "(?:%s,)?" % U(), NP),
 ("N5 two depths, inner `{0,2}` outer `+`", r"(?:(?:(?P<h>\d)?;){0,2},)+", "(?:(?:(?:%s)?%s)?,)*(?:(?:%s)?%s)?," % (b(0), b(0), b(0), b(1)), NP),
 ("NL nullable body `(?:(?<h>\\d)?)*`", r"(?:(?P<h>\d)?)*", "(?:(?:(?:\\d)?)*(?<h>\\d)?)?", R4),
 ("NL2 nullable body `(?:(?<h>\\d)|;?)*`", r"(?:(?P<h>\d)|;?)*", "(?:(?:\\d|;?)*(?:(?<h>\\d)|;?))?", R4),
 ("LB a lookbehind sets h in its pass `(?:\\d|(?<=(?<h>\\d))[a-z])*`", r"(?:\d|(?<=(?P<h>\d))[a-z])*", "(?:(?:\\d|(?<=\\d)[a-z])*(?:\\d|(?<=(?<h>\\d))[a-z]))?", A4),
 ("LA a lookahead sets h `(?:(?=.(?<h>\\d))[a-z]|\\d)*`", r"(?:(?=.(?P<h>\d))[a-z]|\d)*", "(?:(?:(?=.\\d)[a-z]|\\d)*(?:(?=.(?<h>\\d))[a-z]|\\d))?", A4),
 ("AT an atomic body `(?:(?>(?<h>\\d)?;))*`", r"(?:(?>(?P<h>\d)?;))*", "(?:(?:(?>%s))*(?>%s))?" % (b(0), b(1)), RG),
]
for tag, ep, up, pool in CASES:
    for cn, ec, uc in (("(h: <5)", lambda: h5(), '(?C"t")'), ("NOT (h: <5)", lambda: NOT(h5()), '(?!(?C"t"))')):
        fe = ekey(lambda ep=ep, ec=ec: W(Pat(ep), ec()), ("h",))
        fu = ukey(up + uc, {"t": lambda v: lt5(v["h"])}, ("h",))
        d, n = diff(fe, fu, pool)
        print("A %s `& %s`: engine vs model U /%s/: %s %s" % (tag, cn, up + uc, d, "EQUAL" if n == 0 else "DIFFER"))
    sys.stdout.flush()
