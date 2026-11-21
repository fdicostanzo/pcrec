#!/usr/bin/env python3
# fixinduced probe 2: default.unused (b) after rev 23.1 F7. Does a default change answers in the cases (b) now
# suppresses (under a complement, under NOT over a two-valued group question) or fails to cover (a default INSIDE S
# under NOT)?
import os, sys, io, contextlib
R = "/var/tmp/pcrec-pcrec/scratch/crit-predspec231/tree/docs/dev/lanes/predspec23c_evidence"
sys.path.insert(0, R)
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23c_model as C
B = C.B; M = B.M
SVRE = r"(?P<h>\d)?x"                       # set-once optional h (the §R.3 pattern)
alph = ["3", "7", "x", " "]
SV = [""]
for n in range(1, 5):
    SV += ["".join(t) for t in __import__("itertools").product(alph, repeat=n)]
assert len(SV) == 341
REPRE, REPP = r"(?:(?P<h>\d)?;)*", r"(?P<h>\d)?;"
alph2 = ["3", "7", ";"]
REP = [""]
for n in range(1, 6):
    REP += ["".join(t) for t in __import__("itertools").product(alph2, repeat=n)]
assert len(REP) == 364
lt, NOT = B.lt, B.NOT
notlt = lambda n: (lambda v: not lt(n)(v))           # the set !<n over every text
def cmp(name, Pa, Pb, pool):
    for mode in ["WHOLE", "SEARCHED"]:
        d = [s for s in pool if (B.whole(Pa, s) if mode == "WHOLE" else B.search_from(Pa, s, 0)) != (B.whole(Pb, s) if mode == "WHOLE" else B.search_from(Pb, s, 0))]
        print("%-70s %-8s differ %d first %r" % (name, mode, len(d), min(d, key=lambda x: (len(x), x)) if d else None))
P = lambda conds, comps=(): B.P2(SVRE, conds, comps)
# (1) default INSIDE S under NOT (b's mirror): NOT (h = 3: <5) vs NOT (h: <5)
cmp("SV NOT (h = 3: <5) vs NOT (h: <5)", P([NOT(B.test("h", lt(5), "3"))]), P([NOT(B.test("h", lt(5)))]), SV)
# (2) default outside S inside a COMPLEMENTED pattern: x & !(x & (h = 9: <5)) vs x & !(x & (h: <5))
cmp("SV P & !(P & (h = 9: <5)) vs P & !(P & (h: <5))", P([], [P([B.test("h", lt(5), "9")])]), P([], [P([B.test("h", lt(5))])]), SV)
# (3) default outside a SET complement: (h = 3: !<5) vs (h: !<5)
cmp("SV (h = 3: !<5) vs (h: !<5)", P([B.test("h", notlt(5), "3")]), P([B.test("h", notlt(5))]), SV)
# (4) double NOT: NOT NOT (h = 9: <5) vs NOT NOT (h: <5)
cmp("SV NOT NOT (h = 9: <5) vs NOT NOT (h: <5)", P([NOT(NOT(B.test("h", lt(5), "9")))]), P([NOT(NOT(B.test("h", lt(5))))]), SV)
# (5) NOT over a two-valued group question on a looped label: NOT some((h = "x": <5)) vs NOT some((h: <5))
PR = lambda conds: B.P2(REPRE, conds, passre=REPP)
f1 = lambda r: M.k_not(B.some_(lambda p: B.dv(p.get("h"), "x") is not None and lt(5)(B.dv(p.get("h"), "x")))(r))
f2 = lambda r: M.k_not(B.some_(lambda p: None if p.get("h") is None else lt(5)(p["h"]))(r))
cmp("REP NOT some((h = \"x\": <5)) vs NOT some((h: <5))", PR([f1]), PR([f2]), REP)
# (6) occurs.none with a set complement and a default outside it: occurs.none((h = 3: !<5)) vs occurs.none((h: !<5))
g1 = lambda r: not B.some_(lambda p: notlt(5)(B.dv(p.get("h"), "3")))(r)
g2 = lambda r: not B.some_(lambda p: None if p.get("h") is None else notlt(5)(p["h"]))(r)
cmp("REP occurs.none((h = 3: !<5)) vs occurs.none((h: !<5))", PR([g1]), PR([g2]), REP)
# control: the case the draft counts (must differ 1 / 164)
cmp("CONTROL SV NOT (h = 9: <5) vs NOT (h: <5)", P([NOT(B.test("h", lt(5), "9"))]), P([NOT(B.test("h", lt(5)))]), SV)
cmp("CONTROL REP NOT some vs plain-default some differs? (h = 3 in S): NOT some((h = 3: <5)) vs NOT some((h: <5))",
    PR([lambda r: M.k_not(B.some_(lambda p: lt(5)(B.dv(p.get("h"), "3")))(r))]), PR([f2]), REP)
