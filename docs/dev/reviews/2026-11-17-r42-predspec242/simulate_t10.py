import sys, itertools
sys.path.insert(0, "/var/tmp/pcrec-pcrec/scratch/crit-predspec242/simulate/wk")
from ev import M, num
lt5 = lambda v: num(v) and int(v) < 5
pool = ["".join(t) for L in range(6) for t in itertools.product("37;", repeat=L)]
print(len(pool))
REP = M(r"(?:(?<h>\d)?;)*")
def passes_h(st, txt):
    # recompute per-pass h from the path by re-splitting: tokens of the whole text
    return None
# OLD (every pass, possibly none, default 0): WHOLE holds iff the text is a REP whole match and every pass's h (or 0) < 5
# (REP's whole parse is unique: tokens d; or ;)
def toks(s):
    out = []; i = 0
    while i < len(s):
        if s[i].isdigit() and i + 1 < len(s) and s[i + 1] == ";": out.append(s[i]); i += 2
        elif s[i] == ";": out.append(None); i += 1
        else: return None
    return out
old = lambda s: (lambda t: t is not None and all(lt5(h if h is not None else "0") for h in t))(toks(s))
new = lambda s: any(lt5(REP.lab(st, "h") if REP.lab(st, "h") is not None else "0") for st in REP.paths(s, 0, len(s)))
d = [s for s in pool if old(s) != new(s)]
print("W2b-bare WHOLE differ", len(d), d[:5])
# W1a bare
P1 = M(r"(?:(?<h>\d);)*")
def toks1(s):
    return [s[i] for i in range(0, len(s), 2)] if len(s) % 2 == 0 and all(s[i].isdigit() and s[i+1] == ";" for i in range(0, len(s), 2)) else None
old1 = lambda s: (lambda t: t is not None and len(t) >= 1 and all(lt5(h) for h in t))(toks1(s))
new1 = lambda s: any(lt5(P1.lab(st, "h")) for st in P1.paths(s, 0, len(s)))
d1 = [s for s in pool if old1(s) != new1(s)]
print("W1a-bare WHOLE differ", len(d1), d1[:5])
