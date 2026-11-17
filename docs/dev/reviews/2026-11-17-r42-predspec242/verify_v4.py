# V4: pass forms over a label two loops deep, literal vs hole spelling. Engine via eng.py (modeclosure's, unchanged).
import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/verify/w")
from eng import *
def strings(alpha, n):
    out = [""]; cur = [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
NP = strings("37;,", 5)
INNER, NEST = r"(?:(?P<h>\d)?;)*", r"(?:(?:(?P<h>\d)?;)*,)*"
def safe(f):
    def g(m, s):
        try: return f(m, s)
        except ValueError as e: return "REJECTED"
    return g
for cn, ec in (("(h: <5) [bare control]", lambda: h5()), ("some((h: <5))", lambda: SOME(h5())), ("occurs.none(NOT (h: <5))", lambda: NONE(NOT(h5()))), ("(h[2]: <5)", lambda: Idx("h", 2, lt(5)))):
    fl = safe(ekey(lambda ec=ec: W(Pat(NEST), ec()), ("h",)))
    fh = safe(ekey(lambda ec=ec: W(Rep(Seq(Pat(INNER), Pat(",")), 0), ec()), ("h",)))
    print("PF `& %s`: literal vs holes: %s" % (cn, diff(fl, fh, NP)[0]))
    for t in (",", "3;7;,", "7;3;,", "3;;,7;,", "3;,7;,", "7;,3;,"):
        print("   `%s` WHOLE: literal %s ; holes %s" % (t, fl("WHOLE", t), fh("WHOLE", t)))
    sys.stdout.flush()
