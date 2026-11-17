import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from eng import *
from um import ukey, strings, P
lt5 = lambda v: v is not None and num(v) and int(v) < 5
NP = strings("37;,", 5); RG = strings("37;", 5)
b  = lambda n: ("(?<h>\\d)?;" if n else "(?:\\d)?;")
U  = lambda: "(?:(?:%s)*%s)?" % (b(0), b(1)); U0 = lambda: "(?:(?:%s)*%s)?" % (b(0), b(0))
NEST = r"(?:(?:(?P<h>\d)?;)*,)*"; NU = "(?:(?:%s,)*%s,)?" % (U0(), U())
# (6) a per-test default on a label the outermost view leaves unset, top level and nested
d0 = lambda v: lt5(v["h"] if v["h"] is not None else "0")
for nm, mk, up, pool in (("NEST & (h = 0: <5)", lambda: W(Pat(NEST), C("h", lt(5), h="0")), NU + '(?C"t")', NP),
                         ("NEST & NOT (h = 9: <5)", lambda: W(Pat(NEST), NOT(C("h", lt(5), h="9"))), NU + '(?!(?C"u"))', NP),
                         ("occurrences(/(?:(?<h>\\d)?;)+/, min = 1) & (h = 0: <5)", lambda: W(OCC(Pat(r"(?:(?P<h>\d)?;)+"), 1), C("h", lt(5), h="0")),
                          "(?:[\\s\\S]*?(?:(?:%s)*%s))*[\\s\\S]*?(?:(?:%s)*%s)[\\s\\S]*(?C\"t\")" % (b(0), b(0), b(0), b(1)), strings("37; ", 4))):
    fe = ekey(mk, ("h",)); fu = ukey(up, {"t": d0, "u": lambda v: lt5(v["h"] if v["h"] is not None else "9")}, ("h",))
    d, n = diff(fe, fu, pool); print("Y default %s: engine vs model U: %s %s" % (nm, d, "EQUAL" if n == 0 else "DIFFER"))
# (9) a condition inside an atomic part inside a loop item (R.10's stated limit)
TC = {"t": lambda v: lt5(v["h"]), "no": lambda v: False}
LAST = "(?:(?<h>\\d)(?C\"t\")|(?C\"no\"));"
for nm, mk, up in (("`/(?:${atomic(item & (h: <5))})*/`, item := `/(?<h>\\d)?;/`", lambda: Rep(Atom(W(Pat(r"(?P<h>\d)?;"), h5())), 0), "(?:(?>%s))*" % LAST),
                   ("`/(?:${atomic(INNER & (h: <5))},)*/`, INNER := `/(?:(?<h>\\d)?;)*/`", lambda: Rep(Seq(Atom(W(Pat(r"(?:(?P<h>\d)?;)*"), h5())), Pat(",")), 0), "(?:(?>(?:(?:\\d)?;)*%s|(?C\"no\")),)*" % LAST)):
    fe = ekey(mk, ()); fu = ukey(up, TC, ())
    d, n = diff(fe, fu, NP); print("Y atomic-in-loop %s: engine vs model U' (holds, stretch): %s %s" % (nm, d, "EQUAL" if n == 0 else "DIFFER"))
# (4) a joint across two depths, and over two sibling loops: bare and `some(J)`
J = lambda: C(("h", "k"), lambda h, k: num(h) and num(k) and int(h) > int(k))
def safe(f):
    def g(m, s):
        try: return f(m, s)
        except ValueError as e: return "REJECTED (%s)" % e
    return g
TD = r"(?:(?P<k>\d)(?:(?P<h>\d);)*,)*"
SB = r"(?:(?P<k>\d);)*(?:(?P<h>\d),)*"
for nm, mk in (("two depths bare `/(?:(?<k>\\d)(?:(?<h>\\d);)*,)*/ & ((h, k): h > k)`", lambda: W(Pat(TD), J())),
               ("two depths `some(J)`", lambda: W(Pat(TD), SOME(J()))),
               ("sibling loops bare `/(?:(?<k>\\d);)*(?:(?<h>\\d),)*/ & ((h, k): h > k)`", lambda: W(Pat(SB), J())),
               ("sibling loops `some(J)`", lambda: W(Pat(SB), SOME(J())))):
    f = safe(ekey(mk, ("h", "k")))
    print("Y joint %s: WHOLE `37;,` %s ; `3;7,` %s ; SEARCHED `x37;3,` %s" % (nm, f("WHOLE", "37;,"), f("WHOLE", "3;7,"), f("SEARCHED", "x37;3,")))
# hits(r) with a looped label inside each hit: the last COMMITTED hit's own, at the outermost view
X = r"(?:(?P<h>\d)?;)+"
Xu = P.Pcre("(?:(?:\\d)?;)*(?<h>\\d)?;")
def hits_model(mode, s):
    def rows(i):
        for e in range(len(s), i - 1, -1):
            sub, out, pos = s[i:e], [], 0
            while pos <= len(sub):
                r = Xu.match(sub, pos)
                if r is None: break
                out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
            last = out[-1][2]["h"] if out else None
            if lt5(last): yield e, last
    if mode == "WHOLE":
        for e, h in rows(0):
            if e == len(s): return (("h", h),)
        return None
    def search(pos):
        for i in range(pos, len(s) + 1):
            for e, h in rows(i): return (i, e, (("h", h),))
        return None
    if mode == "SEARCHED": return search(0)
    out, pos = [], 0
    while pos <= len(s):
        r = search(pos)
        if r is None: break
        out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
    return tuple(out)
fe = ekey(lambda: W(G["Committed"](Pat(X)), h5()), ("h",))
d, n = diff(fe, hits_model, strings("37; ", 4)); print("Y hits `hits(/(?:(?<h>\\d)?;)+/) & (h: <5)` engine vs a libpcre2 global-search model (last committed hit, unrolled): %s %s" % (d, "EQUAL" if n == 0 else "DIFFER"))
