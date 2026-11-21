import sys, io, contextlib, re
D = "/var/tmp/pcrec-pcrec/scratch/crit-predspec23/R/tree/docs/dev/lanes/"
sys.path.insert(0, D + "predspec23_evidence")
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23_model as M
def rec(h, m):   # (h: <10, m: <30) on one pass: Kleene AND of entries
    a = None if h is None else int(h) < 10
    b = None if m is None else int(m) < 30
    return M.k_and([a, b])
c = lambda r: not any(M.k_not(rec(h, m)) is True for h, m in r["_real"])
P = M.Prog(M.CL, [c])
wh = {s: (lambda r: r is not None and c(r) is True)(M.cl_row(P, s, 0, len(s))) for s in M.SUBO}
print("record twin occurs.none(NOT (h: <10, m: <30)) WHOLE holds", sum(wh.values()))
for iname, f in M.INTENT:
    d = [s for s in M.SUBO if wh[s] != f([(pm.group("h"), pm.group("m")) for pm in re.finditer(M.CLPASS, s)])]
    print(" ", iname, "differ", len(d), "first", (min(d, key=lambda x: (len(x), x)) if d else None))
