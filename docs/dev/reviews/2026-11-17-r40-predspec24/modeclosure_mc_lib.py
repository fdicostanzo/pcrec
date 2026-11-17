# modeclosure critic helper: loads rev 24's engine (predspec24_model.py) up to its PART A, read-only.
import os, sys, io, re, contextlib
R = "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/R/tree/docs/dev/lanes"
F = os.path.join(R, "predspec24_evidence", "predspec24_model.py")
SRC = open(F).read()
NS = {"__file__": F, "__name__": "ps24"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(SRC[:SRC.index("# ================================================================================================= PART A")], F, "exec"), NS)
P = NS["P"]
def g(k): return NS[k]
MODES = ("WHOLE", "SEARCHED", "FIND-ALL")
def enkey(mk, labs):
    cache = {}
    def f(m, s):
        with NS["rules"]("24"):
            if "p" not in cache: cache["p"] = mk()
            Pn = cache["p"]
            if m == "WHOLE": return NS["whole_row"](Pn, s) is not None
            if m == "SEARCHED":
                r = NS["search"](Pn, s); return None if r is None else (r[0], r[1], tuple(sorted((l, r[2].last.get(l)) for l in labs)))
            return tuple((a, b, tuple(sorted((l, rw.last.get(l)) for l in labs))) for a, b, rw in NS["findall"](Pn, s))
    return f
def rxkey(pat, co, labs):
    rx = P.Pcre(pat, co)
    def f(m, s):
        if m == "WHOLE": return rx.whole(s)
        if m == "SEARCHED":
            r = rx.search(s); return None if r is None else (r[0], r[1], tuple(sorted((l, r[2].get(l)) for l in labs)))
        return tuple((a, b, tuple(sorted((l, d.get(l)) for l in labs))) for a, b, d in rx.findall(s))
    return f
def cmp(f1, f2, pool, modes=MODES):
    out = []
    for m in modes:
        d = [s for s in pool if f1(m, s) != f2(m, s)]
        if d:
            w = min(d, key=lambda x: (len(x), x))
            out.append("%s %d (first %r: A %s ; B %s)" % (m, len(d), w, f1(m, w), f2(m, w)))
        else: out.append("%s 0" % m)
    return "; ".join(out) + " of %d" % len(pool)
def Tc(l, S):
    def f(c):
        v = c.get(l); return None if v is None else bool(S(v))
    return f
