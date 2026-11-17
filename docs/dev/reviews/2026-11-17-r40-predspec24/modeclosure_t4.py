import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/modeclosure")
from mc_lib import *
W, Pat, C, OCC, lt, eq, Committed, NONE, NOT, SOME = (g(k) for k in ("W", "Pat", "C", "OCC", "lt", "eq", "Committed", "NONE", "NOT", "SOME"))
strings, search, findall, hitlist, whole_row, rules = g("strings"), g("search"), g("findall"), g("hitlist"), g("whole_row"), g("rules")
OCCPOOL = strings("12 x", 4)
NUMp = r"(?P<n>\d+)"
mk = lambda: W(Committed(Pat(NUMp)), NONE(NOT(C("n", lt(100)))))
glob = re.compile(r"\d+")
with rules("24"):
    Pn = mk()
    for s in ("x300 12", "1234", "1234 5 300"):
        r = search(Pn, s)
        print("H3 SEARCHED %r ->" % s, None if r is None else (s[r[0]:r[1]], r[0], hitlist(r[2])), "; FIND-ALL ->", [(s[a:b], a, hitlist(rw)) for a, b, rw in findall(Pn, s)])
    # count texts where a reported hit list (SEARCHED or FIND-ALL) holds a hit that is NOT a hit of the global search of the SUBJECT
    nS = nF = 0; first = None
    for s in OCCPOOL:
        gh = set((m.start(), m.end()) for m in glob.finditer(s))
        def bad(i, e, rw):
            # positions of committed hits inside the stretch: recompute as global find-all of stretch
            hs = [(i + m.start(), i + m.end()) for m in glob.finditer(s[i:e])]
            return any(h not in gh for h in hs)
        r = search(Pn, s)
        if r is not None and bad(r[0], r[1], r[2]): nS += 1; first = first or s
        if any(bad(a, b, rw) for a, b, rw in findall(Pn, s)): nF += 1
    print("H3 hit lists holding a hit the subject's global search never produced: SEARCHED %d, FIND-ALL %d of %d (first %r)" % (nS, nF, len(OCCPOOL), first))
