import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/simulate/wk")
from ev import M, run, num
lt5 = lambda v: num(v) and int(v) < 5
REP = r"(?:(?<h>\d)?;)*"
mk = M(REP)
def comp(mk_, st):
    # !(REP & (h: <5)) on the stretch's own text
    s = mk_.txt; i0 = st.start if hasattr(st, "start") else None
    return True
def fmt(mk, r):
    if r is None: return "FAILS"
    if isinstance(r, tuple):
        i, st = r; return "`%s`@%d h=%s" % (mk.txt[i:st.pos], i, mk.lab(st, "h"))
    return "HOLDS h=%s" % mk.lab(r, "h")
def prog(kind):
    if kind == "lt": return lambda m, st: lt5(m.lab(st, "h"))
    if kind == "not": return lambda m, st: not lt5(m.lab(st, "h"))
    if kind == "cmp": return lambda m, st: (lambda v: v is not None and not lt5(v))(m.lab(st, "h"))
STARTS = {}
def run_c(kind, t):
    # complement: need the stretch start; recompute with a wrapper over starts
    out = []
    m2 = M(REP)
    def surv(sub):
        return any(lt5(m2.lab(st, "h")) for st in m2.paths(sub, 0, len(sub)))
    def first(start, end=None):
        for st in mk.paths(t, start, end):
            sub = t[start:st.pos]
            if not surv(sub): return st
            mk.txt = t
        return None
    mk.txt = t
    w = first(0, len(t)); mk.txt = t
    srch = None
    for i in range(len(t) + 1):
        r = first(i); mk.txt = t
        if r is not None: srch = (i, r); break
    fa = []; pos = 0
    while pos <= len(t):
        r = None
        for i in range(pos, len(t) + 1):
            x = first(i); mk.txt = t
            if x is not None: r = (i, x); break
        if r is None: break
        fa.append(r); pos = r[1].pos if r[1].pos > r[0] else r[1].pos + 1
    return w, srch, fa
FA = "3;7; 7;; 3;"
for line, kind, t in (("R13;;", "lt", "3;;"), ("R23;;", "not", "3;;"), ("R37;;", "cmp", "7;;"), ("R43;;", "c", "3;;"),
                      ("R27;;", "not", "7;;"), ("R47;;", "c", "7;;"), ("R3e", "cmp", ""), ("R33;", "cmp", "3;"), ("R33;7;", "cmp", "3;7;"), ("R33;;", "cmp", "3;;"),
                      ("R2e", "not", ""), ("R23;", "not", "3;"), ("R23;7;", "not", "3;7;"), ("R4e", "c", ""), ("R43;", "c", "3;"), ("R43;7;", "c", "3;7;")):
    if kind == "c":
        w, _, _ = run_c(kind, t); _, s, _ = run_c(kind, t); _, _, f = run_c(kind, FA)
        mk.txt = t; a = fmt(mk, w); b = fmt(mk, s); mk.txt = FA; c = [fmt(mk, x) for x in f]
    else:
        w, s, _ = run(mk, prog(kind), t); a = fmt(mk, w); b = fmt(mk, s)
        f = run(mk, prog(kind), FA)[2]; c = [fmt(mk, x) for x in f]
    print("%-8s %-4s on %-5r WHOLE %s | SEARCHED %s | FIND-ALL %s" % (line, kind, t, a, b, [x for x in c if not x.startswith("``")]))
