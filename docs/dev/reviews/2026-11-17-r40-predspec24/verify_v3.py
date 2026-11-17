import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec24/verify")
from vlib import *
H3 = lambda: W(Committed(Pat(NUMp)), NONE(NOT(C("n", lt(100)))))
with rules("24"):
    Pn = H3()
    for s in ("x300 12", "1234", "1234 5 300", "111"):
        r = search(Pn, s)
        print("SEARCHED", repr(s), "->", None if r is None else (s[r[0]:r[1]], r[0], hitlist(r[2])),
              "| FIND-ALL", [(s[a:b], a, hitlist(rw)) for a, b, rw in findall(Pn, s)],
              "| WHOLE", None if whole_row(Pn, s) is None else hitlist(whole_row(Pn, s)))
    # how many reported hit lists hold a hit the subject's global search never produced
    import re as _re
    def subj_hits(s): return [(m.start(), m.end()) for m in _re.finditer(r"\d+", s)]
    cs = cf = 0
    for s in OCCPOOL:
        sh = set(subj_hits(s))
        r = search(Pn, s)
        if r is not None:
            ps = list(r[2].passes.values())[0]
            # recompute positions of the reported hits inside the stretch
            hs = [(r[0] + m.start(), r[0] + m.end()) for m in _re.finditer(r"\d+", s[r[0]:r[1]])]
            if set(hs) - sh: cs += 1
        bad = False
        for a, b, rw in findall(Pn, s):
            hs = [(a + m.start(), a + m.end()) for m in _re.finditer(r"\d+", s[a:b])]
            if set(hs) - sh: bad = True
        cf += bad
    print("texts whose reported hits include a non-subject hit: SEARCHED %d, FIND-ALL %d of %d" % (cs, cf, len(OCCPOOL)))
