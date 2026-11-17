import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/simulate/wk")
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
from ev import M, run, num
import pcre2h, ctypes
# duplicate names in a loop: label (per §4.3: the value from whichever duplicate group the pass set) vs capture (\k<x>)
for s in ("aba", "abb", "ab", "ba"):
    for tail in ("a", "b"):
        pat = r"(?J)(?:(?<x>a)|(?<x>b))+\k<x>"
        code = pcre2h.L.pcre2_compile_8(pat.encode(), len(pat), pcre2h.BASE_OPTS, ctypes.byref(ctypes.c_int()), ctypes.byref(pcre2h.SIZE()), None)
    mk = M(r"(?J)(?:(?<x>a)|(?<x>b))+")
    st = next(mk.paths(s, 0, len(s)), None)
    lab = mk.lab(st, "x") if st else None; cap = mk.cap(st, "x") if st else None
    # libpcre2: which value does \k<x> read after the loop on s? test s+'a' and s+'b' WHOLE
    rd = [c for c in "ab" if pcre2h.Pcre.__new__(pcre2h.Pcre) is not None]
    out = []
    for c in "ab":
        p = object.__new__(pcre2h.Pcre); p.pattern = r"(?J)(?:(?<x>a)|(?<x>b))+\k<x>"; p.callouts = {}
        err, off = ctypes.c_int(0), pcre2h.SIZE(0); pb = p.pattern.encode()
        p.code = pcre2h.L.pcre2_compile_8(pb, len(pb), pcre2h.BASE_OPTS, ctypes.byref(err), ctypes.byref(off), None)
        p.md = pcre2h.L.pcre2_match_data_create_from_pattern_8(p.code, None); p.mctx = pcre2h.L.pcre2_match_context_create_8(None)
        p._cb = pcre2h.CB(p._callout); pcre2h.L.pcre2_set_callout_8(p.mctx, p._cb, None); p.names = {}; p.calls = 0; p._exc = None
        r = p.match(s + c, 0, pcre2h.PCRE2_ANCHORED | pcre2h.PCRE2_ENDANCHORED)
        out.append((s + c, r is not None))
    print("dup", repr(s), "label x (last pass's own) =", lab, "; my capture (lowest-numbered set) =", cap, "; libpcre2 \\k<x> WHOLE:", out)
