# V10: zero-place, `occurrences(/\d+/ & /1\d*/, min = 1)` (the reference) vs `0` = PCRE's group 0 (OccG0, defined as in
# predspec241_model.py l.1125-1130), pool DSP = strings("129 ", 5) (1,365), under several metrics.
import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/verify/w")
from eng import *
OccS, whole_row, search, findall = G["OccS"], G["whole_row"], G["search"], G["findall"]
labkey = lambda row, labs: tuple(G["hitlist"](row))   # as predspec241_model.py l.815 for ("#hits",)
class OccG0(OccS):
    def __init__(self, A, B, mn=0):
        OccS.__init__(self, A, mn); self.B = B
        self.hit_ok = lambda s, i, g, e: whole_row(self.B, s[i:e]) is not None
def strings(alpha, n):
    out = [""]; cur = [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
DSP = strings("129 ", 5)
def keys(mk, rule):
    c = {}
    def f(m, s):
        with R(rule):
            if "p" not in c: c["p"] = mk()
            P = c["p"]
            if m == "WHOLE": r = whole_row(P, s); return None if r is None else labkey(r, ("#hits",))
            if m == "SEARCHED": r = search(P, s); return None if r is None else (r[0], r[1], labkey(r[2], ("#hits",)))
            return tuple((a, b, labkey(rw, ("#hits",))) for a, b, rw in findall(P, s))
    return f
proj = {
 "full (holds/stretch + hit lists)": lambda m, k: k,
 "stretch only (no hit lists)": lambda m, k: (k is not None) if m == "WHOLE" else (None if k is None else k[:2]) if m == "SEARCHED" else tuple(x[:2] for x in k),
 "holds only": lambda m, k: (k is not None) if m != "FIND-ALL" else len(k) > 0,
}
for rule in ("24.2", "24"):
    ref = keys(lambda: OCC(AND(Pat(r"\d+"), Pat(r"1\d*")), 1), rule)
    g0 = keys(lambda: OccG0(Pat(r"\d+"), Pat(r"1\d*"), 1), rule)
    inn = keys(lambda: OCC(ZERO(Pat(r"\d+"), Pat(r"1\d*")), 1), rule)
    cache = {}
    for m in ("WHOLE", "SEARCHED", "FIND-ALL"):
        for s in DSP: cache[(m, s)] = (ref(m, s), g0(m, s), inn(m, s))
    for pn, pf in proj.items():
        out = []
        for m in ("WHOLE", "SEARCHED", "FIND-ALL"):
            d = [s for s in DSP if pf(m, cache[(m, s)][0]) != pf(m, cache[(m, s)][1])]
            out.append("%s %d%s" % (m, len(d), (" (first `%s`)" % min(d, key=lambda x: (len(x), x))) if d else ""))
        d2 = sum(1 for m in ("WHOLE", "SEARCHED", "FIND-ALL") for s in DSP if pf(m, cache[(m, s)][0]) != pf(m, cache[(m, s)][2]))
        print("rules %s, ref vs group-0, %s: %s of %d ; ref vs innermost: %d" % (rule, pn, " / ".join(out), len(DSP), d2))
    # per-mode texts differing under any metric, union and the count of texts where only some modes differ
    sys.stdout.flush()
