# V7: FIND-ALL step-one vs PCRE2's global loop (pcre2demo's: after an empty match retry at the same offset with
# NOTEMPTY_ATSTART|ANCHORED, else advance one), on MY helper control (no lookaround: position == time), and the engine.
import sys
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/verify/w")
sys.path.insert(1, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/R/tree/docs/dev/lanes/rxmodel_evidence")
from eng import *
import pcre2h as P
NE = 0x00000008
lt5 = lambda v: v is not None and num(v) and int(v) < 5
def strings(alpha, n):
    out = [""]; cur = [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
RG = strings("37;", 5)
def ctl(pat, neg):
    side = {}
    def t(c):
        hs, ps = c.span("h"), c.span("ps")
        own = c.get("h") if (hs is not None and ps is not None and hs[0] >= ps[0]) else None
        side["h"] = own
        return lt5(own)
    rx = P.Pcre(pat + ('(?!(?C"t"))' if neg else '(?C"t")'), {"t": t})
    def m(s, pos, opts):
        side.clear(); r = rx.match(s, pos, opts)
        if r is None: return None
        h = side.get("h") if not neg else None   # under NOT the label read is the one the failed callout saw
        return (r[0], r[1])
    return m
def stepone(m, s):
    out, pos = [], 0
    while pos <= len(s):
        r = m(s, pos, 0)
        if r is None: break
        out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
    return tuple(out)
def pcre2loop(m, s):
    out, pos, ne = [], 0, False
    while pos <= len(s):
        r = m(s, pos, (NE | P.PCRE2_ANCHORED) if ne else 0)
        if r is None:
            if ne: pos += 1; ne = False; continue
            break
        out.append(r); ne = (r[1] == r[0]); pos = r[1]
    return tuple(out)
for nm, ep, hp in (("greedy", r"(?:(?P<h>\d)?;)*", r"(?:(?<ps>)(?<h>\d)?;)*"), ("lazy", r"(?:(?P<h>\d)?;)*?", r"(?:(?<ps>)(?<h>\d)?;)*?")):
    for neg in (False, True):
        m = ctl(hp, neg)
        fe = ekey(lambda ep=ep, neg=neg: W(Pat(ep), NOT(h5()) if neg else h5()), ())
        eng = lambda s: tuple((a, b) for a, b, _ in fe("FIND-ALL", s))
        d1 = [s for s in RG if stepone(m, s) != pcre2loop(m, s)]
        d2 = [s for s in RG if eng(s) != pcre2loop(m, s)]
        d3 = [s for s in RG if eng(s) != stepone(m, s)]
        w = min(d1, key=lambda x: (len(x), x)) if d1 else None
        print("%s `& %s(h: <5)` (stretches compared): step-one vs PCRE2 loop %d of %d; engine vs PCRE2 loop %d; engine vs step-one %d%s" % (
            nm, "NOT " if neg else "", len(d1), len(RG), len(d2), len(d3), "" if w is None else "; first `%s`: step-one %s, PCRE2 loop %s, engine %s" % (w, stepone(m, w), pcre2loop(m, w), eng(w))))
