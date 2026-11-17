# FIND-ALL: the evidence's "empty match -> step one character" vs PCRE2's own global loop (retry at the same place
# with NOTEMPTY_ATSTART|ANCHORED, then advance), both on model U, for the per-pass rule's NOT lines.
import sys; sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/modeclosure/work")
from eng import *
from um import URx, strings, P
NOTEMPTY_ATSTART = 0x00000008
lt5 = lambda v: v is not None and num(v) and int(v) < 5
b  = lambda n: ("(?<h>\\d)?;" if n else "(?:\\d)?;")
RG = strings("37;", 5)
def real_findall(u, s):
    out, pos, ne = [], 0, False
    while pos <= len(s):
        r = u.m(s, pos, (NOTEMPTY_ATSTART | P.PCRE2_ANCHORED) if ne else 0)
        if r is None:
            if ne: pos += 1; ne = False; continue
            break
        out.append(r); ne = (r[1] == r[0]); pos = r[1]
    return tuple(out)
for nm, ep, up in (("greedy REP", r"(?:(?P<h>\d)?;)*", "(?:(?:%s)*%s)?" % (b(0), b(1))),
                   ("lazy REP `*?`", r"(?:(?P<h>\d)?;)*?", "(?:(?:%s)*?%s)??" % (b(0), b(1)))):
    for cn, ec, uc in (("(h: <5)", lambda: h5(), '(?C"t")'), ("NOT (h: <5)", lambda: NOT(h5()), '(?!(?C"t"))')):
        u = URx(up + uc, {"t": lambda v: lt5(v["h"])}, ("h",))
        fe = ekey(lambda ep=ep, ec=ec: W(Pat(ep), ec()), ("h",))
        d1 = [t for t in RG if u.key("FIND-ALL", t) != real_findall(u, t)]
        d2 = [t for t in RG if fe("FIND-ALL", t) != real_findall(u, t)]
        w = min(d2, key=lambda x: (len(x), x)) if d2 else None
        print("F %s `& %s`: model U step-one vs PCRE2's own global loop: %d of 364 ; ENGINE vs PCRE2's own global loop: %d of 364%s" % (
            nm, cn, len(d1), len(d2), "" if w is None else " (first `%s`: engine %s vs PCRE2 %s)" % (w, fe("FIND-ALL", w), real_findall(u, w))))
