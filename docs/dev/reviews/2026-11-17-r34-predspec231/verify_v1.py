import os, sys, re, io, contextlib
L = "/var/tmp/pcrec-pcrec/scratch/crit-predspec231/tree/docs/dev/lanes"
sys.path.insert(0, L + "/predspec23b_evidence")
os.environ["PREDSPEC23B_SWAP"] = "0"; os.environ["PREDSPEC23B_SABOTAGE"] = "0"
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23b_model as B
M = B.M
canon = lambda v: v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None
READ = {"VALUE": lambda v, n: re.fullmatch(r"\d+", v) is not None and int(v) < n,
        "CANON": lambda v, n: canon(v) and int(v) < n}
# L83
for rd, f in READ.items():
    T = lambda v, f=f: f(v, 30)
    J = lambda r, T=T: None if r.get("h") is None or r.get("m") is None else (B.lt(9)(r["h"]) and T(r["m"]))
    R = B.AND(B.test("h", B.lt(9)), B.test("m", T))
    a, b = B.P2(B.T2, [B.NOT(J)]), B.P2(B.T2, [B.NOT(R)])
    for mode in ["WHOLE", "SEARCHED"]:
        d = [s for s in B.T2POOL if B.holds(mode, a, s) != B.holds(mode, b, s)]
        print("L83", rd, mode, "differ", len(d), "first", min(d, key=lambda x: (len(x), x)) if d else None)
# closing
def jt(h, m, dh, dm, S):
    h = h if h is not None else dh; m = m if m is not None else dm
    if h is None or m is None: return None
    return bool(S(h, m))
def kand(xs):
    if any(x is False for x in xs): return False
    if any(x is None for x in xs): return None
    return True
def knot(x): return None if x is None else (not x)
for rd, f in READ.items():
    inR = lambda h, m, f=f: f(h, 10) and f(m, 30)
    notR = lambda h, m, inR=inR: not inR(h, m)
    C = [("occurs.none(NOT ((h, m): R)) joint", lambda ps: not any(knot(jt(h, m, None, None, inR)) is True for h, m in ps)),
         ("occurs.none(NOT (h:<10, m:<30)) record", lambda ps: not any(knot(kand([None if h is None else f(h, 10), None if m is None else f(m, 30)])) is True for h, m in ps)),
         ("occurs.none(((h, m = 00): !R))", lambda ps: not any(jt(h, m, None, "00", notR) is True for h, m in ps)),
         ("((h = 0, m = 00): R) every pass", lambda ps: kand([jt(h, m, "0", "00", inR) for h, m in (ps if ps else [(None, None)])]) is True),
         ("((h = 0, m = 0): R)", lambda ps: kand([jt(h, m, "0", "0", inR) for h, m in (ps if ps else [(None, None)])]) is True)]
    INT = [("I1", lambda ps: all(m is not None and inR(h, m) for h, m in ps)),
           ("I2a", lambda ps: all(m is None or inR(h, m) for h, m in ps)),
           ("I2b", lambda ps: all(f(h, 10) if m is None else inR(h, m) for h, m in ps))]
    for nm, c in C:
        wh = {}
        for s in M.SUBO:
            ps = [(p.group("h"), p.group("m")) for p in re.finditer(M.CLPASS, s)]
            wh[s] = (re.fullmatch(M.CL, s) is not None and c(ps), ps)
        out = []
        for iname, g in INT:
            d = [s for s in M.SUBO if wh[s][0] != g(wh[s][1])]
            out.append("%s %d%s" % (iname, len(d), " first %r" % min(d, key=lambda x: (len(x), x)) if d else ""))
        print("CLOSING", rd, nm, "holds", sum(v[0] for v in wh.values()), "|", "; ".join(out))
