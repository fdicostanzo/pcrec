# verify lens helper: loads rev 24's engine (predspec24_model.py) up to its PART A, read-only, in memory.
import os, sys, io, re, contextlib
LANES = "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/R/tree/docs/dev/lanes"
F = os.path.join(LANES, "predspec24_evidence", "predspec24_model.py")
SRC = open(F).read()
NS = {"__file__": F, "__name__": "ps24v"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(SRC[:SRC.index("# ================================================================================================= PART A")], F, "exec"), NS)
globals().update({k: v for k, v in NS.items() if not k.startswith("__")})
LPm = NS["LP"]
MODES = ("WHOLE", "SEARCHED", "FIND-ALL")

def eng(mk, labs=(), rul="24", wholelabs=True):
    """engine key; WHOLE carries labels when wholelabs."""
    cache = {}
    def f(m, s):
        with NS["rules"](rul):
            if "p" not in cache: cache["p"] = mk()
            Pn = cache["p"]
            if m == "WHOLE":
                r = NS["whole_row"](Pn, s)
                if r is None: return None
                return tuple((l, r.last.get(l)) for l in labs) if wholelabs else True
            if m == "SEARCHED":
                r = NS["search"](Pn, s)
                return None if r is None else (r[0], r[1], tuple((l, r[2].last.get(l)) for l in labs))
            return tuple((a, b, tuple((l, rw.last.get(l)) for l in labs)) for a, b, rw in NS["findall"](Pn, s))
    return f

def pc(pat, co, labs=()):
    rx = P.Pcre(pat, co)
    def f(m, s):
        if m == "WHOLE":
            r = rx.match(s, 0, 0x80000000 | 0x20000000)
            return None if r is None else tuple((l, r[2].get(l)) for l in labs)
        if m == "SEARCHED":
            r = rx.search(s); return None if r is None else (r[0], r[1], tuple((l, r[2].get(l)) for l in labs))
        return tuple((a, b, tuple((l, d.get(l)) for l in labs)) for a, b, d in rx.findall(s))
    return f

def strip(f):
    """same key with labels dropped (holding/stretch only)."""
    def g(m, s):
        k = f(m, s)
        if m == "WHOLE": return k is not None
        if m == "SEARCHED": return None if k is None else k[:2]
        return tuple(x[:2] for x in k)
    return g

def cmp(f1, f2, pool, modes=MODES):
    out = []
    for m in modes:
        d = [s for s in pool if f1(m, s) != f2(m, s)]
        if d:
            w = min(d, key=lambda x: (len(x), x))
            out.append("%s %d (first %r: %s vs %s)" % (m, len(d), w, f1(m, w), f2(m, w)))
        else: out.append("%s 0" % m)
    return "; ".join(out) + " of %d" % len(pool)

def Tc(l, S):
    def f(c):
        v = c.get(l); return None if v is None else bool(S(v))
    return f
