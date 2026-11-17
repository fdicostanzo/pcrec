# V1: nullable loop body. (a) libpcre2 fact, (b) witness on the engine and libpcre2, (c) one MODECLOSURE-1 count.
# Engine loader: eng.py, copied unchanged from modeclosure/work/eng.py. libpcre2 control: MY OWN helper-group-free
# trace model (see lib_key): a callout at every loop-body start records the pass starts on the CURRENT path via a
# capture `(?<ps>)` (path exact), and the test reads h only if h was set at/after the last pass start. No lookaround
# here, so position == time.
import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/verify/w")
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
from eng import *
import pcre2h as P

# (a) the fact
tr = []
rx = P.Pcre(r'(?:(?C"s")(?<p>)(?<h>\d)?)*(?C"e")', {"s": lambda c: tr.append(("s", c.pos)) or True,
                                                    "e": lambda c: tr.append(("e", c.pos, c.span("p"), c.span("h"))) or True})
print("FACT /(?:(?C\"s\")(?<p>)(?<h>\\d)?)*(?C\"e\")/ WHOLE on `3`:", rx.match("3", 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED), tr)
tr.clear()
rx2 = P.Pcre(r'(?:a|(?<e>))*(?C"e")', {"e": lambda c: tr.append(("e", c.pos, c.span("e"))) or True})
print("FACT /(?:a|(?<e>))*/ WHOLE on `a`:", rx2.match("a", 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED), tr)

lt5 = lambda v: v is not None and num(v) and int(v) < 5
def lib_key(pat_ps, neg):
    # pat_ps: the loop with (?<ps>) at the start of its body; the label is own iff h.start >= ps.start
    def t(c):
        hs, ps = c.span("h"), c.span("ps")
        own = c.get("h") if (hs is not None and (ps is None or hs[0] >= ps[0])) else None
        side["h"] = own
        return lt5(own) != neg
    side = {}
    rx = P.Pcre(pat_ps + '(?C"t")', {"t": t})
    def m(s, pos=0, opts=0):
        r = rx.match(s, pos, opts)
        return None if r is None else (r[0], r[1], (("h", side.get("h")),))
    def f(mode, s):
        if mode == "WHOLE":
            r = m(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED); return None if r is None else r[2]
        if mode == "SEARCHED": return m(s)
        out, pos = [], 0
        while pos <= len(s):
            r = m(s, pos)
            if r is None: break
            out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
        return tuple(out)
    return f

def strings(alpha, n):
    out = [""]; cur = [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out

pat = r"(?:(?P<h>\d)?)*"
for neg in (True, False):
    fe = ekey(lambda neg=neg: W(Pat(pat), NOT(h5()) if neg else h5()), ("h",))
    fl = lib_key(r"(?:(?<ps>)(?<h>\d)?)*", neg)
    nm = "NOT (h: <5)" if neg else "(h: <5)"
    for s in ("3", "37", "7"):
        print("WITNESS `/(?:(?<h>\\d)?)*/ & %s` on `%s`: engine W=%s S=%s F=%s | libpcre2 W=%s S=%s F=%s" % (
            nm, s, fe("WHOLE", s), fe("SEARCHED", s), fe("FIND-ALL", s), fl("WHOLE", s), fl("SEARCHED", s), fl("FIND-ALL", s)))
    print("COUNT `/(?:(?<h>\\d)?)*/ & %s` engine vs libpcre2 (alphabet `37;`, len<=4):" % nm, diff(fe, fl, strings("37;", 4))[0])
    sys.stdout.flush()
