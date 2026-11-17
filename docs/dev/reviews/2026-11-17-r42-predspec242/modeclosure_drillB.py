import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from eng import *
from um import strings, P
lt5 = lambda v: v is not None and num(v) and int(v) < 5
b  = lambda n: ("(?<h>\\d)?;" if n else "(?:\\d)?;")
U  = lambda: "(?:(?:%s)*%s)?" % (b(0), b(1))
class OpRx:
    """libpcre2 model of `A & B ...` / `A & !B`: A searched in the subject, a callout at A's end runs B (model U, its
    own pattern, a test callout at its end when the condition reads B's label) WHOLE on the stretch's OWN text."""
    def __init__(self, A, Bu, comp=False, test=None, cond="pos"):
        self.side = None
        tests = {}
        if test is not None:
            tests["t"] = (lambda c: bool(test(c.get("h")))) if cond == "pos" else (lambda c: not test(c.get("h")))
        self.B = P.Pcre(Bu + ('(?C"t")' if test is not None else ""), tests)
        self.comp = comp
        self.A = P.Pcre(A + '(?C"op")', {"op": self.op})
    def op(self, c):
        st = c.stretch()
        r = self.B.match(st, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
        if self.comp: self.side = (("h", None),); return r is None
        if r is None: return False
        self.side = (("h", r[2].get("h")),); return True
    def m(self, s, pos=0, opts=0):
        self.side = None
        r = self.A.match(s, pos, opts)
        return None if r is None else (r[0], r[1], self.side)
    def key(self, mode, s):
        if mode == "WHOLE":
            r = self.m(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED); return None if r is None else r[2]
        if mode == "SEARCHED": return self.m(s)
        out, pos = [], 0
        while pos <= len(s):
            r = self.m(s, pos)
            if r is None: break
            out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
        return tuple(out)
def okey(*a, **k):
    c = {}
    def f(m, s):
        if "x" not in c: c["x"] = OpRx(*a, **k)
        return c["x"].key(m, s)
    return f
POOL = strings("37;a", 5)   # 1,365
A_ = r"[\d;a]*"
OPS = [
 ("`$`",         r"(?:(?P<h>\d)?;)*$",           U() + "$"),
 ("`^`",         r"^(?:(?P<h>\d)?;)*",           "^" + U()),
 ("`\\b`",       r"(?:(?P<h>\d)?;)*a\b",         U() + "a\\b"),
 ("lookahead",   r"(?=(?:(?P<h>\d)?;)*a)[\d;a]*", "(?=" + U() + "a)[\\d;a]*"),
 ("lookbehind",  r"(?:(?P<h>\d)?;)*(?<=3;)",     U() + "(?<=3;)"),
]
for nm, Bp, Bu in OPS:
    for cn, ec, cond in (("(h: <5)", lambda: h5(), "pos"), ("NOT (h: <5)", lambda: NOT(h5()), "not")):
        fe = ekey(lambda Bp=Bp, ec=ec: W(AND(Pat(A_), Pat(Bp)), ec()), ("h",))
        fm = okey(A_, Bu, test=lt5, cond=cond)
        d, n = diff(fe, fm, POOL)
        print("B `/[\\d;a]*/ & B & %s`, B %s := /%s/: engine vs libpcre2 operand model: %s %s" % (cn, nm, Bp, d, "EQUAL" if n == 0 else "DIFFER"))
    # the complement with the looped label inside: A & !(B & (h: <5))
    fe = ekey(lambda Bp=Bp: D(Pat(A_), W(Pat(Bp), h5())), ("h",))
    fm = okey(A_, Bu, comp=True, test=lt5)
    d, n = diff(fe, fm, POOL); print("B `/[\\d;a]*/ & !(B & (h: <5))`, B %s: engine vs model: %s %s" % (nm, d, "EQUAL" if n == 0 else "DIFFER"))
    # the LAW with the conditioned operand: A & (B & (h: <5)) vs A & (0: B & (h: <5)), holds and stretch (labels not compared)
    fa = ekey(lambda Bp=Bp: AND(Pat(A_), W(Pat(Bp), h5())), ())
    fz = ekey(lambda Bp=Bp: ZERO(Pat(A_), W(Pat(Bp), h5())), ())
    d, n = diff(fa, fz, POOL); print("B LAW `A & (B & (h: <5))` vs `A & (0: B & (h: <5))`, B %s (holds, stretch): %s %s" % (nm, d, "EQUAL" if n == 0 else "DIFFER"))
    # nested: the same chain inside an occurrences argument, condition inside / outside
    fo = ekey(lambda Bp=Bp: OCC(W(AND(Pat(r"[\d;]+"), Pat(Bp)), h5()), 1), ("h",))
    print("B nested `occurrences((/[\\d;]+/ & B) & (h: <5), min = 1)`, B %s: WHOLE `3;a 7;3;a` %s ; SEARCHED `7;;a3;a` %s ; FIND-ALL `3;a 7;a` %s" % (nm, fo("WHOLE", "3;a 7;3;a"), fo("SEARCHED", "7;;a3;a"), fo("FIND-ALL", "3;a 7;a")))
    sys.stdout.flush()
