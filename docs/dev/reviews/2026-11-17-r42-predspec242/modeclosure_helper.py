# The EVIDENCE's control construction (predspec242b OwnRx: helper group (?<ps>) at each pass start; a label is the
# pass's own iff its capture STARTS at or after the latest helper) re-implemented here only to TEST it as a model.
import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from eng import *
from um import strings, P
lt5 = lambda v: v is not None and num(v) and int(v) < 5
class HRx:
    def __init__(self, pat, neg=False):
        self.side = None
        self.neg = neg
        self.rx = P.Pcre(pat + ('(?!(?C"t"))' if neg else '(?C"t")') + '(?C"e")', {"t": self.t, "e": self.e})
    def v(self, c):
        sl, ps = c.span("h"), c.span("ps")
        return None if (sl is None or ps is None or sl[0] < ps[0]) else c.subject[sl[0]:sl[1]]
    def t(self, c): return lt5(self.v(c))
    def e(self, c): self.side = (("h", self.v(c)),); return True
    def key(self, mode, s):
        def m(pos, opts=0):
            self.side = None; r = self.rx.match(s, pos, opts)
            return None if r is None else (r[0], r[1], self.side)
        if mode == "WHOLE":
            r = m(0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED); return None if r is None else r[2]
        if mode == "SEARCHED": return m(0)
        out, pos = [], 0
        while pos <= len(s):
            r = m(pos)
            if r is None: break
            out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
        return tuple(out)
def hk(p, neg):
    c = {}
    def f(m, s):
        if "x" not in c: c["x"] = HRx(p, neg)
        return c["x"].key(m, s)
    return f
A4 = strings("37a", 4); R4 = strings("37;", 4)
for nm, ep, hp, pool in (("LB", r"(?:\d|(?<=(?P<h>\d))[a-z])*", r"(?:(?<ps>)(?:\d|(?<=(?<h>\d))[a-z]))*", A4),
                         ("LA", r"(?:(?=.(?P<h>\d))[a-z]|\d)*", r"(?:(?<ps>)(?:(?=.(?<h>\d))[a-z]|\d))*", A4),
                         ("NL", r"(?:(?P<h>\d)?)*", r"(?:(?<ps>)(?<h>\d)?)*", R4)):
    for neg in (False, True):
        fe = ekey(lambda ep=ep, neg=neg: W(Pat(ep), NOT(h5()) if neg else h5()), ("h",))
        d, n = diff(fe, hk(hp, neg), pool)
        print("HELPER %s %s: engine vs the helper-group construction /%s/: %s %s" % (nm, "NOT (h: <5)" if neg else "(h: <5)", hp, d, "EQUAL" if n == 0 else "DIFFER"))
