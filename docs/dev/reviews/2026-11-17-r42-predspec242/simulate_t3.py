import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/simulate/wk")
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
from ev import M, run, num
import pcre2h
PI = "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/pathimpact_evidence/pathimpact_model.py"
src = open(PI).read(); src = src[:src.index("RXC = {}")]
ns = {"__file__": PI, "__name__": "pi"}
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()): exec(compile(src, PI, "exec"), ns)
Rx = ns["Rx"]
def eng_paths(pat, s, i=0):
    """engine: paths with the label = last setting after the last pass start (single loop; any loop node)"""
    r = Rx(pat.replace("(?<", "(?P<"))
    out = []
    for e, caps, hist in r.paths(s, i):
        t = max([k for k, ev in enumerate(hist) if ev[0] == "it"], default=-1)
        lab = {}
        for nm, g in r.names.items():
            vs = [s[ev[2]:ev[3]] for k, ev in enumerate(hist) if ev[0] == "g" and ev[1] == g and k > t]
            lab[nm] = vs[-1] if vs else None
        cap = {nm: (None if caps[g] is None else s[caps[g][0]:caps[g][1]]) for nm, g in r.names.items()}
        out.append((e, lab, cap, [ev for ev in hist if ev[0] == "it"]))
    return out
lt5 = lambda v: num(v) and int(v) < 5
for pat in (r"(?:(?<h>\d)?,?)*", r"(?:(?<h>\d)|(?<e>))*", r"(?:(?<h>\d)?)*"):
    for s in ("3", "3,", "37"):
        print("ENGINE", pat, repr(s), [(e, l, c, len(it)) for e, l, c, it in eng_paths(pat, s)][:4])
        mk = M(pat)
        print("MINE  ", pat, repr(s), [(st.pos, {n: mk.lab(st, n) for n in mk.P.names}, {n: mk.cap(st, n) for n in mk.P.names}, sum(1 for x in st.log if x[0] == "pass")) for st in list(mk.paths(s))[:4]])
        # WHOLE: & NOT (h: <5)
        w_mine = next((st for st in mk.paths(s, 0, len(s)) if not lt5(mk.lab(st, "h"))), None)
        w_eng = next(((e, l) for e, l, c, it in eng_paths(pat, s) if e == len(s) and not lt5(l["h"])), None)
        hg = pat.replace("(?:", "(?:(?<ps>)", 1)
        def t(c):
            hs, ps = c.span("h"), c.span("ps")
            h = c.get("h") if (hs is not None and ps is not None and hs[0] >= ps[0]) else None
            return not lt5(h)
        lib = pcre2h.Pcre(hg + '(?C"t")', {"t": t}).match(s, 0, pcre2h.PCRE2_ANCHORED | pcre2h.PCRE2_ENDANCHORED)
        print("  & NOT (h: <5) WHOLE: mine %s ; engine %s ; libpcre2 helper-group %s" % (
            "FAILS" if w_mine is None else "HOLDS h=%s" % mk.lab(w_mine, "h"), "FAILS" if w_eng is None else "HOLDS h=%s" % w_eng[1]["h"], lib))
