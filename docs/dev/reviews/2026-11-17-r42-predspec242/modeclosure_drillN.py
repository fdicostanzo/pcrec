import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from eng import *
from um import ukey, strings
lt5 = lambda v: v is not None and num(v) and int(v) < 5
NP = strings("37;,", 5); SX = strings("37; ", 5); RG = strings("37;", 5)
b  = lambda n: ("(?<h>\\d)?;" if n else "(?:\\d)?;")
U  = lambda: "(?:(?:%s)*%s)?" % (b(0), b(1))
U0 = lambda: "(?:(?:%s)*%s)?" % (b(0), b(0))
UP  = lambda: "(?:(?:%s)*%s)" % (b(0), b(1))      # (?:B)+ unrolled
UP0 = lambda: "(?:(?:%s)*%s)" % (b(0), b(0))
GAP = "[\\s\\S]*?"
INNER, NEST = r"(?:(?P<h>\d)?;)*", r"(?:(?:(?P<h>\d)?;)*,)*"
CASES = [
 ("H1 a literal loop inside a HOLE loop `/(?:${inner},)*/`, inner := INNER", lambda: Rep(Seq(Pat(INNER), Pat(",")), 0), "(?:(?:%s,)*%s,)?" % (U0(), U()), NP),
 ("H2 a HOLE loop of a literal two-depth item `/(?:${x})*/`, x := `/(?:(?:(?<h>\\d)?;)*,)/`", lambda: Rep(Pat(r"(?:(?:(?P<h>\d)?;)*,)"), 0), "(?:(?:%s,)*%s,)?" % (U0(), U()), NP),
 ("H3 a hole loop inside a hole loop `/(?:${(?:${item})*},)*/`, item := `/(?<h>\\d)?;/`", lambda: Rep(Seq(Rep(Pat(r"(?P<h>\d)?;"), 0), Pat(",")), 0), "(?:(?:%s,)*%s,)?" % (U0(), U()), NP),
 ("AT1 inside atomic: `atomic(NEST) & (h: <5)`", lambda: Atom(Pat(NEST)), "(?>(?:(?:%s,)*%s,)?)" % (U0(), U()), NP),
 ("AT2 atomic inside a hole loop: `/(?:${atomic(/(?:(?<h>\\d)?;)*,/)})*/`", lambda: Rep(Atom(Pat(r"(?:(?P<h>\d)?;)*,")), 0), "(?:(?:(?>%s,))*(?>%s,))?" % (U0(), U()), NP),
 ("O1 inside an `occurrences` argument: `occurrences(/(?:(?<h>\\d)?;)+/, min = 1)`", lambda: OCC(Pat(r"(?:(?P<h>\d)?;)+"), 1), "(?:%s%s)*%s%s[\\s\\S]*" % (GAP, UP0(), GAP, UP()), SX),
 ("O2 atomic inside `occurrences`: `occurrences(atomic(/(?:(?<h>\\d)?;)+/), min = 1)`", lambda: OCC(Atom(Pat(r"(?:(?P<h>\d)?;)+")), 1), "(?:%s(?>%s))*%s(?>%s)[\\s\\S]*" % (GAP, UP0(), GAP, UP()), SX),
 ("O3 a hole loop inside `occurrences`: `occurrences(/(?:${item})+/, min = 1)`, item := `/(?<h>\\d)?;/`", lambda: OCC(Rep(Pat(r"(?P<h>\d)?;"), 1), 1), "(?:%s%s)*%s%s[\\s\\S]*" % (GAP, UP0(), GAP, UP()), SX),
 ("O4 a two-depth literal inside `occurrences`: `occurrences(/(?:(?:(?<h>\\d)?;)+,)+/, min = 1)` (three loops)", lambda: OCC(Pat(r"(?:(?:(?P<h>\d)?;)+,)+"), 1),
   "(?:%s(?:%s,)+)*%s(?:%s,)*%s,[\\s\\S]*" % (GAP, UP0(), GAP, UP0(), UP()), strings("37;, ", 4)),
]
for tag, mk, up, pool in CASES:
    for cn, ec, uc in (("(h: <5)", lambda: h5(), '(?C"t")'), ("NOT (h: <5)", lambda: NOT(h5()), '(?!(?C"t"))')):
        fe = ekey(lambda mk=mk, ec=ec: W(mk(), ec()), ("h",))
        fu = ukey(up + uc, {"t": lambda v: lt5(v["h"])}, ("h",))
        d, n = diff(fe, fu, pool)
        print("N %s `& %s`: engine vs model U /%s/: %s %s" % (tag, cn, up + uc, d, "EQUAL" if n == 0 else "DIFFER"))
    sys.stdout.flush()
# the pass forms over a label two loops deep: the literal spelling vs the hole spelling of the SAME pattern (engine only)
def safe(f):
    def g(m, s):
        try: return f(m, s)
        except ValueError as e: return "REJECTED"
    return g
for cn, ec in (("some((h: <5))", lambda: SOME(h5())), ("occurs.none(NOT (h: <5))", lambda: NONE(NOT(h5()))), ("(h[2]: <5)", lambda: Idx("h", 2, lt(5)))):
    fl = safe(ekey(lambda ec=ec: W(Pat(NEST), ec()), ("h",)))
    fh = safe(ekey(lambda ec=ec: W(Rep(Seq(Pat(INNER), Pat(",")), 0), ec()), ("h",)))
    d, n = diff(fl, fh, NP)
    print("PF `& %s`: literal NEST vs its hole spelling `/(?:${inner},)*/`: %s %s" % (cn, d, "EQUAL" if n == 0 else "DIFFER"))
    for t in ("3;7;,", "7;3;,", "3;,7;,", "7;,3;,", "3;;,"):
        print("PF    `%s`: literal %s ; holes %s" % (t, fl("WHOLE", t), fh("WHOLE", t)))
    sys.stdout.flush()
