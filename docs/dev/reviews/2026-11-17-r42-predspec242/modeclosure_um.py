# Model U (modeclosure's own control): STRUCTURAL UNROLLING. A loop B* is rewritten (?:B'*B)? where B' is B with the
# label's group made non-capturing; only the LAST pass's copy carries the named group, so PCRE2's own capture state
# (path-exact) IS the last pass's own label (outermost view: unroll every enclosing loop). Nested loops unroll
# recursively. The test is a plain callout reading the capture. No helper group, no position comparison.
# Caveat: the unrolled form moves the "how many passes" choice before the body's own choices, so path ORDER can
# differ where a body has two live choices; every body used here is effectively deterministic per text.
import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
import pcre2h as P
class URx:
    def __init__(self, pattern, tests, labs):
        self.labs, self.side = tuple(labs), {}
        cos = {k: (lambda c, f=f: bool(f({l: c.get(l) for l in self.rx.names}))) for k, f in tests.items()}
        cos["__end"] = self._end
        self.pattern = pattern
        self.rx = P.Pcre(pattern + '(?C"__end")', cos)
    def _end(self, c): self.side = {l: c.get(l) for l in self.labs}; return True
    def m(self, s, pos=0, opts=0):
        self.side = {}
        r = self.rx.match(s, pos, opts)
        return None if r is None else (r[0], r[1], tuple((l, self.side.get(l)) for l in self.labs))
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
def ukey(pattern, tests, labs):
    c = {}
    def f(m, s):
        if "x" not in c: c["x"] = URx(pattern, tests, labs)
        return c["x"].key(m, s)
    return f
def strings(alpha, n):
    out = [""]; cur = [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
