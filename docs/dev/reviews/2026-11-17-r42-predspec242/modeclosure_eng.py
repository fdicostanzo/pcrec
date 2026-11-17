# Load rev 24.2's engine DEFINITIONS (predspec242b's patches P1-P6 applied to predspec241's source, cut before its
# PART A so no part runs; P7 is then moot: _ev_passown is never installed, as P7 disables it). Read-only copies.
import os, sys, io, re, contextlib
EV = "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes"
F242 = EV + "/predspec242b_evidence/predspec242b_model.py"
F241 = EV + "/predspec241_evidence/predspec241_model.py"
src = open(F242).read()
head = src[:src.index("# ================================================================================================= PART 0")]
ns = {"__file__": F242, "__name__": "p242head"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(head, F242, "exec"), ns)
full = ns["patched"](True, False)
cut = full[:full.index("# ================================================================================================= PART A: the catalogue")]
G = {"__file__": F241, "__name__": "p241defs"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(cut, F241, "exec"), G)
assert G["PASSOWN"]["v"] is True and G["RULES"]["v"] == "24"
@contextlib.contextmanager
def R(rule):
    old = G["PASSOWN"]["v"]
    with G["rules"]("23.2" if rule == "23.2" else "24"):
        G["PASSOWN"]["v"] = (rule == "24.2")
        try: yield
        finally: G["PASSOWN"]["v"] = old
class Seq:
    """`/${X}${Y}/` (holes in a literal), as predspec242b's PART N defines it."""
    def __init__(self, a, b): self.a, self.b = a, b
    def walk(self, s, i):
        for e1, r1, c1 in self.a.walk(s, i):
            for e2, r2, c2 in self.b.walk(s, e1):
                r = G["merge"](r1, r2); r.stretch = (i, e2); yield e2, r, c1 + c2
_lo = G["labels_of"]
def _labels_of(node):
    if isinstance(node, Seq): return _labels_of(node.a) | _labels_of(node.b)
    return _lo(node)
G["labels_of"] = _labels_of
def ekey(mk, labs, rule="24.2"):
    cache = {}
    def f(mode, s):
        with R(rule):
            if "p" not in cache: cache["p"] = mk()
            Pn = cache["p"]
            lab = lambda row: tuple((l, row.last.get(l)) for l in labs)
            if mode == "WHOLE":
                r = G["whole_row"](Pn, s); return None if r is None else lab(r)
            if mode == "SEARCHED":
                r = G["search"](Pn, s); return None if r is None else (r[0], r[1], lab(r[2]))
            return tuple((a, b, lab(rw)) for a, b, rw in G["findall"](Pn, s))
    return f
def diff(f1, f2, pool, modes=("WHOLE", "SEARCHED", "FIND-ALL")):
    out, tot, firsts = [], 0, {}
    for m in modes:
        d = []
        for s in pool:
            try: a = f1(m, s)
            except Exception as e: a = "ERR:%s" % e
            try: b = f2(m, s)
            except Exception as e: b = "ERR:%s" % e
            if a != b: d.append((s, a, b))
        tot += len(d)
        if d:
            w = min(d, key=lambda x: (len(x[0]), x[0])); firsts[m] = w
            out.append("%s %d (first `%s`: %s vs %s)" % (m, len(d), w[0], w[1], w[2]))
        else: out.append("%s 0" % m)
    return " / ".join(out) + " of %d" % len(pool), tot
Pat, W, C, NOT, Rep, OCC, AND, D, Atom, ZERO, SOME, NONE, Idx = (G[k] for k in ("Pat", "W", "C", "NOT", "Rep", "OCC", "AND", "D", "Atom", "ZERO", "SOME", "NONE", "Idx"))
lt, eq, num = G["lt"], G["eq"], G["num"]
def h5(): return C("h", lt(5))
