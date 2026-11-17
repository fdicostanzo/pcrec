# modeclosure lens: my OWN libpcre2 model of rev 24.2's per-pass label: (*MARK) names (path-exact, restored on
# backtracking by PCRE2 itself) record the TEMPORAL order of "a pass started" (*MARK:P) and "h was set" (*MARK:Hh);
# at a reading callout, h is the last pass's own (outermost view) iff the most recent mark on this path is Hh.
# No helper group, no capture-position comparison (the engine's control construction is not reused).
import sys, ctypes
EV = "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes"
sys.path.insert(0, EV + "/rxmodel_evidence")
import pcre2h as P

class MRx(P.Pcre):
    def __init__(self, pattern, tests, labs, own=()):
        self.labs, self.own, self.side = tuple(labs), set(own), {}
        cos = {k: (lambda c, f=f: bool(f(self._vals(c)))) for k, f in tests.items()}
        cos["__end"] = self._end
        super().__init__(pattern + '(?C"__end")', cos)
    def _callout(self, blkp, _):
        self._mark = blkp.contents.mark.decode() if blkp.contents.mark else None
        return super()._callout(blkp, _)
    def _vals(self, c):
        v = {}
        for l in self.labs:
            if l in self.own: v[l] = c.get(l) if self._mark == "H" + l else None
            else: v[l] = c.get(l)
        return v
    def _end(self, c): self.side = self._vals(c); return True
    def m(self, s, pos=0, opts=0):
        self.side = {}
        r = self.match(s, pos, opts)
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

def strings(alpha, n):
    out = [""]; cur = [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
