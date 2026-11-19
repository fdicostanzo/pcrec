import sys, io, contextlib
R = "/var/tmp/pcrec-pcrec/scratch/crit-predspec231/tree/docs/dev/lanes/predspec23c_evidence"
sys.path.insert(0, R)
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23c_model as C
B = C.B; M = B.M; P2 = B.P2
REP, REPPASS, REPPOOL = M.REP, M.REPPASS, M.REPPOOL
lt5 = B.lt(5)
def pt(p):  # (h: <5) on one pass row, three-valued
    v = p.get("h"); return None if v is None else bool(lt5(v))
plain = lambda r: M.k_and([pt(p) for p in r["_passes"]])                       # pass-and
exists_not = lambda r: any(M.k_not(pt(p)) is True for p in r["_real"])       # some(NOT c), EXISTS over real passes
def k_or(vals):
    vals = list(vals)
    if any(v is True for v in vals): return True
    if any(v is None for v in vals): return None
    return False
any_not = lambda r: k_or([M.k_not(pt(p)) for p in r["_passes"]])             # some(NOT c), Kleene OR (SQL ANY) over pass rows
progs = [("(h: <5) [pass-and]", P2(REP, [plain], passre=REPPASS)),
         ("NOT some(NOT (h: <5)) [EXISTS]", P2(REP, [lambda r: not exists_not(r)], passre=REPPASS)),
         ("NOT some(NOT (h: <5)) [Kleene ANY over pass rows]", P2(REP, [lambda r: M.k_not(any_not(r))], passre=REPPASS))]
for s in ["", ";", "3;", "3;;", "7;;", "3;7;"]:
    print("on %r: " % s + " ; ".join("%s %s" % (n, B.both(P, s)) for n, P in progs))
for mode in ["WHOLE", "SEARCHED"]:
    for a, b in [(0, 1), (0, 2)]:
        d = sorted([s for s in REPPOOL if B.holds(mode, progs[a][1], s) != B.holds(mode, progs[b][1], s)], key=lambda x: (len(x), x))
        print("%s REP(364) %s vs %s differ %d first %r" % (mode, progs[a][0], progs[b][0], len(d), d[0] if d else None))
