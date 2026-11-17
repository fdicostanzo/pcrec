#!/usr/bin/env python3
# Lane predspec23c (2026-11-17): evidence for docs/design/predicates_draft.md rev 23.1 (review r33's fixes; DESIGN
# ONLY; rules nothing). Every answer is printed in BOTH modes (WHOLE value; SEARCHED = candidate R22).
#
# It imports lane predspec23b's engine READ-ONLY (../predspec23b_evidence/predspec23b_model.py, which imports
# predspec23's) and OVERRIDES ONE THING: the search order of `P | Q` over filtered branches. predspec23b searched it
# END-MAJOR (at a start, for each end of branch 1's regex, "branch 1 first, the next branch when its filters reject"),
# a reading the draft never stated (review r33 F2). The MANAGER RULING branch-order (COND-FAMILY 2026-11-17 03:01
# entry, item (3), told to the owner by name) is BRANCH-MAJOR, PCRE's own order: at a start, every row of the first
# branch in its own preference order, then every row of the second; a branch whose own condition rejects a row falls
# through like any failing piece of that branch. A condition OUTSIDE the `|` reads the one parse's row and never sends
# it to another branch (R.1.4; `(B | A) & (l: "a")` on `aa` still rejects). WHOLE value: the stretch is fixed, so the
# order decides only which branch's labels the row carries, never whether it holds. Holds-counts SEARCHED cannot move
# either (the same (start, branch, end) triples are tried, only in another order); REPORTED ROWS can, and find-all
# with them.
#
# PARTS: 0 controls (the old order reproduces predspec23b's PART 5 lines and review r33's 125 / 400); 1 branch-order
# (`when` re-run, before/after per line, counts); 2 F1 (L83 under NOT; the closing example's record twin); 3 F7
# (default.unused (b) under NOT); 4 F8 (the empty-intersection error's domain under NOT and `!S`); 5 F3 (a label its
# operand sets but no match of the `&` of operands can); 6 F12 (NOT over a nested program); 7 F11/F4 (find-all is not
# monotone; the hit list of a filtered argument); 8 F17 (a nullable B in text.none); 9 the re-allowed-NOT sweep rows
# that need a run (L55, L56, L65, L94, L30).
#
# Commands (W = the worktree; run from a scratch dir under $PCREC_TMPDIR, e.g. /var/tmp/pcrec-pcrec/scratch/predspec23c):
#   timeout 900 python3 -I W/docs/dev/lanes/predspec23c_evidence/predspec23c_model.py > fwd.out
#   PREDSPEC23C_SWAP=1 timeout 900 python3 -I W/docs/dev/lanes/predspec23c_evidence/predspec23c_model.py > swap.out
#   diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)        # must print nothing
#   PREDSPEC23C_SABOTAGE=1 (forward and swapped): the diff must print something (the swap check can fail)
# SWAP reverses every order this script has (pools, lists, line computation) and sets predspec23b's (and through it
# predspec23's) SWAP, which reverses condition, filter and pass lists. The BRANCH order of `|` is NOT reversed by
# SWAP: it is the meaning (PCRE's preference order), not an evaluation order. SABOTAGE puts the branch order under
# SWAP (so a swapped run searches branch 2 first) and sets predspec23b's SABOTAGE (Kleene AND = "the first non-TRUE
# value"): the reported rows of `when` and every count over NOT of a looped label then depend on order.
import os, sys, re, io, contextlib

SWAP = os.environ.get("PREDSPEC23C_SWAP") == "1"
SAB = os.environ.get("PREDSPEC23C_SABOTAGE") == "1"
os.environ["PREDSPEC23B_SWAP"] = "1" if SWAP else "0"
os.environ["PREDSPEC23B_SABOTAGE"] = "1" if SAB else "0"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "predspec23b_evidence"))
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23b_model as B                    # read-only import; runs its own parts silently
M = B.M
print("ORDER: %s%s" % ("SWAPPED" if SWAP else "forward", " SABOTAGE" if SAB else ""))
def order(xs): return list(reversed(list(xs))) if SWAP else list(xs)

# ---- the override: branch-major search of `|` (branch-order) ----
search_em = B.search_from                            # predspec23b's end-major order, kept for the before/after lines
def branches(P): return order(P.alt) if SAB else list(P.alt)
def search_bm(P, s, pos):
    for i in range(pos, len(s) + 1):
        if P.alt is not None:
            for br in branches(P):                   # PCRE's order: every row of branch 1, then of branch 2
                for j in B.ends_pref(br, s, i):
                    if B.accept(br, s, i, j): return (i, j)
        else:
            for j in B.ends_pref(P, s, i):
                if B.accept(P, s, i, j): return (i, j)
    return None
B.search_from = search_bm                            # B.searched / B.findall / B.rep now use branch-order
def rep_with(search, mode, P, s):
    if mode == "WHOLE": return "HOLDS" if B.whole(P, s) else "FAILS"
    r = search(P, s, 0)
    return "FAILS" if r is None else "HOLDS `%s`@%d" % (s[r[0]:r[1]], r[0])
def both_with(search, P, s): return "WHOLE %s | SEARCHED %s" % (rep_with(search, "WHOLE", P, s), rep_with(search, "SEARCHED", P, s))

LINES = {}
def emit(key, text): LINES[key] = text
def count(pool, pred):
    hits = [s for s in order(pool) if pred(s)]
    return len(hits), (min(hits, key=lambda x: (len(x), x)) if hits else None)
MODES = order(["WHOLE", "SEARCHED"])
P2, test, ptest, NOT, lt, ge, between = B.P2, B.test, B.ptest, B.NOT, B.lt, B.ge, B.between
KH, KHP, KHPOOL, T2, T2POOL, T2PAIRS = B.KH, B.KHP, B.KHPOOL, B.T2, B.T2POOL, B.T2PAIRS
pk = B.pk
CS = [("(h: <5)", ptest("h", lt(5))), ("(h = 0: <5)", ptest("h", lt(5), "0"))]
def filter_form(W, A=KH, passre=KHP):                # `x & when(c, p)`: x picks ends (D196), the when filter accepts
    return P2(A, [], [], [lambda s, i, j, W=W: B.accept(W, s, i, j)], passre=passre)

# ---- PART 0: CONTROLS ----
for nm, c in order(CS):
    W = B.when_body(c, pk)
    d, w = count(KHPOOL, lambda s: search_em(W, s, 0) != search_bm(W, s, 0))
    emit((0, 1, nm), "  CONTROL KH (1,110) when body, c = %s: end-major (predspec23b) vs branch-major reported row differ %d first %r (review r33 F2: 125 for (h: <5), 400 for (h = 0: <5))" % (nm, d, w))
    d, w = count(KHPOOL, lambda s: search_em(W, s, 0) != search_bm(filter_form(W), s, 0))
    emit((0, 2, nm), "  CONTROL KH (1,110) c = %s: predspec23b's end-major body vs the filter form x & when(c, p) reported row differ %d first %r (expected 0: the old engine searched the body as the filter form)" % (nm, d, w))

# ---- PART 1: branch-order: `when` re-run, both modes ----
for nm, c in order(CS):
    for notc in order([False, True]):
        W = B.when_body(c, pk, notc)
        F = filter_form(W)
        tag = "NOT-c body (x & c & p) | (x & NOT c)" if notc else "body (x & c & p) | (x & !q)"
        for s in order(["0", "5", "5;1", "5;9", "0;9", "5;1;9", "3;0;5", "3;5"]):
            old, new = both_with(search_em, W, s), both_with(search_bm, W, s)
            emit((1, 1, nm, tag, s), "  WHEN c = %s %s on `%s`: branch-order %s ; before (end-major) %s%s ; filter form x & when %s" % (
                nm, tag, s, new, old, "   MOVED" if old != new else "", both_with(search_bm, F, s)))
        for mode in MODES:
            n, _ = count(KHPOOL, lambda s: B.holds(mode, W, s))
            nf, _ = count(KHPOOL, lambda s: B.holds(mode, F, s))
            emit((1, 2, nm, tag, mode), "  WHEN %s c = %s %s: holds %d of 1,110; filter form holds %d" % (mode, nm, tag, n, nf))
        d, w = count(KHPOOL, lambda s: search_bm(W, s, 0) != search_bm(F, s, 0))
        emit((1, 3, nm, tag), "  WHEN SEARCHED c = %s %s vs filter form x & when: reported row differ %d of 1,110 first %r (holds-or-not differ %d)" % (
            nm, tag, d, w, count(KHPOOL, lambda s: (search_bm(W, s, 0) is None) != (search_bm(F, s, 0) is None))[0]))
        d, w = count(KHPOOL, lambda s: search_em(W, s, 0) != search_bm(W, s, 0))
        emit((1, 4, nm, tag), "  WHEN SEARCHED c = %s %s: reported row MOVED by branch-order (end-major -> branch-major) on %d of 1,110 first %r" % (nm, tag, d, w))
# searchrow's T2 `when` (c = late, p = (m: <45)): body as a `|` of filtered branches vs the case-when filter form
m_lt45 = lambda r: None if r.get("m") is None else int(r["m"]) < 45
WT = P2(T2, alt=[P2(T2, [B.late, m_lt45]), P2(T2, [], [P2(T2, [B.late])])])
FT = filter_form(WT, T2, None)
for poolname, pool in order([("T2 (11,110)", T2POOL), ("T2PAIRS (600)", T2PAIRS)]):
    for mode in MODES:
        n, _ = count(pool, lambda s: B.holds(mode, WT, s))
        nf, _ = count(pool, lambda s: B.holds(mode, FT, s))
        emit((1, 5, poolname, mode), "  WHEN-T2 %s %s c = late, p = (m: <45): body holds %d, case-when (filter form) holds %d (searchrow.out: 11,110 / 600 SEARCHED, 6,050 / 18 WHOLE)" % (mode, poolname, n, nf))
    d, w = count(pool, lambda s: search_bm(WT, s, 0) != search_bm(FT, s, 0))
    emit((1, 6, poolname), "  WHEN-T2 SEARCHED %s body (branch-order) vs case-when: reported row differ %d first %r" % (poolname, d, w))
for s in order(["9:45", "9:15", "10:50"]):
    emit((1, 7, s), "  WHEN-T2 on `%s`: body %s ; case-when %s" % (s, both_with(search_bm, WT, s), both_with(search_bm, FT, s)))

# ---- PART 2: F1, L83 under NOT: the joint ((h, m): (S, T)) vs the record (h: S, m: T) ----
def jt(S, T):
    return lambda r: None if r.get("h") is None or r.get("m") is None else (S(r["h"]) and T(r["m"]))
def rec(S, T):
    return B.AND(test("h", S), test("m", T))
for (sn, S, tn, T) in order([("<9", lt(9), "<30", lambda v: re.fullmatch(r"\d+", v) is not None and int(v) < 30)]):
    J, R = jt(S, T), rec(S, T)
    for mode in MODES:
        for nm, a, b in order([("plain", P2(T2, [J]), P2(T2, [R])), ("NOT", P2(T2, [NOT(J)]), P2(T2, [NOT(R)]))]):
            d, w = count(T2POOL, lambda s: B.holds(mode, a, s) != B.holds(mode, b, s))
            emit((2, 1, mode, nm), "  L83 %s T2 (11,110) %s: joint ((h, m): (%s, %s)) vs record (h: %s, m: %s) differ %d first %r" % (mode, nm, sn, tn, sn, tn, d, w))
    for s in order(["10", "9", "8", "10:15"]):
        emit((2, 2, s), "  L83 on `%s`: t2 & NOT joint %s ; t2 & NOT record %s" % (s, B.both(P2(T2, [NOT(J)]), s), B.both(P2(T2, [NOT(R)]), s)))
# the closing example's record twin (predspec23 PART 4's lists and intents; R = (<10, <30))
CLPASS = M.CLPASS
inR_h, inR_m = (lambda h: int(h) < 10), (lambda m: int(m) < 30)
def cl_joint_not(h, m): return None if h is None or m is None else (not (inR_h(h) and inR_m(m)))
def cl_rec_not(h, m): return M.k_not(M.k_and([None if h is None else inR_h(h), None if m is None else inR_m(m)]))
for nm, f in order([("occurs.none(NOT ((h, m): R)) [joint]", cl_joint_not), ("occurs.none(NOT (h: <10, m: <30)) [record]", cl_rec_not)]):
    def acc(s, i, j, f=f):
        if re.fullmatch(M.CL, s[i:j]) is None: return False
        return not any(f(pm.group("h"), pm.group("m")) is True for pm in re.finditer(CLPASS, s[i:j]))
    wh = {s: acc(s, 0, len(s)) for s in M.SUBO}
    parts = []
    for iname, g in M.INTENT:
        d = [s for s in order(M.SUBO) if wh[s] != g([(pm.group("h"), pm.group("m")) for pm in re.finditer(CLPASS, s)])]
        parts.append("%s differ %d%s" % (iname, len(d), "" if not d else " first %r" % min(d, key=lambda x: (len(x), x))))
    se = sum(1 for s in M.SUBO if any(acc(s, i, j) for i in range(len(s) + 1) for j in range(i, len(s) + 1)))
    emit((2, 3, nm), "  CLOSING (1,111 lists) %s WHOLE holds %d (%s) | SEARCHED holds %d" % (nm, sum(wh.values()), "; ".join(parts), se))

# ---- PART 3: F7, default.unused (b) under NOT ----
SV, SVPOOL, REP, REPPASS, REPPOOL = M.SV, M.SVPOOL, M.REP, M.REPPASS, M.REPPOOL
def sv(c): return P2(SV, [c])
def rp(c): return P2(REP, [c], passre=REPPASS)
none_ = lambda S, d=None: (lambda r: not any(B.dv(p.get("h"), d) is not None and S(B.dv(p.get("h"), d)) for p in r["_real"]))
none_not = lambda S, d=None: (lambda r: not any(M.k_not(None if B.dv(p.get("h"), d) is None else bool(S(B.dv(p.get("h"), d)))) is True for p in r["_real"]))
notS = lambda S: (lambda v: not S(v))
PAIRS3 = [("SV (341)", SVPOOL, "(h: <5) vs (h = 9: <5) [no NOT]", sv(test("h", lt(5))), sv(test("h", lt(5), "9"))),
          ("SV (341)", SVPOOL, "NOT (h: <5) vs NOT (h = 9: <5)", sv(NOT(test("h", lt(5)))), sv(NOT(test("h", lt(5), "9")))),
          ("REP (364)", REPPOOL, "(h: <5) vs (h = \"x\": <5) [no NOT]", rp(ptest("h", lt(5))), rp(ptest("h", lt(5), "x"))),
          ("REP (364)", REPPOOL, "NOT (h: <5) vs NOT (h = \"x\": <5)", rp(NOT(ptest("h", lt(5)))), rp(NOT(ptest("h", lt(5), "x")))),
          ("REP (364)", REPPOOL, "some((h: <5)) vs some((h = \"x\": <5)) [group, no NOT]", rp(lambda r: not none_(lt(5))(r)), rp(lambda r: not none_(lt(5), "x")(r))),
          ("REP (364)", REPPOOL, "occurs.none(NOT (h = \"x\": <5)) vs occurs.none((h = \"x\": !<5))", rp(none_not(lt(5), "x")), rp(none_(notS(lt(5)), "x")))]
for mode in MODES:
    for pn, pool, nm, a, b in order(PAIRS3):
        d, w = count(pool, lambda s: B.holds(mode, a, s) != B.holds(mode, b, s))
        emit((3, mode, nm), "  DEFAULT-UNUSED %s %s %s: differ %d first %r" % (mode, pn, nm, d, w))

# ---- PART 4: F8, the empty-intersection error's domain under NOT and `!S` ----
NL = r"(?:(?P<n>\d),)*"
NLP = r"(?P<n>\d),"
NLPOOL = M.strings("37,", 4)
anytext = lambda v: True
F8 = [("SV (341)", SVPOOL, "NOT (h: <0)", sv(NOT(test("h", lt(0))))),
      ("SV (341)", SVPOOL, "(h: !<0)", sv(test("h", notS(lt(0))))),
      ("SV (341)", SVPOOL, "NOT (h: <10)", sv(NOT(test("h", lt(10))))),
      ("SV (341)", SVPOOL, "(h: !<10)", sv(test("h", notS(lt(10))))),
      ("NL (121)", NLPOOL, "NOT (n: <0) [looped n]", P2(NL, [NOT(ptest("n", lt(0)))], passre=NLP)),
      ("NL (121)", NLPOOL, "some((n: any text))", P2(NL, [lambda r: any(p.get("n") is not None for p in r["_real"])], passre=NLP)),
      ("REP (364)", REPPOOL, "occurs.none((h = \"x\": !<10)) [sentinel, S covers every digit]", rp(none_(notS(lt(10)), "x")))]
for mode in MODES:
    for pn, pool, nm, P in order(F8):
        c, w = count(pool, lambda s: B.holds(mode, P, s))
        emit((4, 1, mode, pn, nm), "  EMPTY-ERROR %s %s %s holds %d of %d first %r" % (mode, pn, nm, c, len(pool), w))
    for (a_, b_) in order([(0, 1), (2, 3), (4, 5)]):
        d, w = count(F8[a_][1], lambda s: B.holds(mode, F8[a_][3], s) != B.holds(mode, F8[b_][3], s))
        emit((4, 2, mode, a_, b_), "  EMPTY-ERROR %s [%s] vs [%s] differ %d first %r" % (mode, F8[a_][2], F8[b_][2], d, w))
for s in order(["", ";", "7;", "3;"]):
    emit((4, 3, s), "  EMPTY-ERROR sentinel occurs.none((h = \"x\": !<10)) on `%s`: %s" % (s, B.both(F8[6][3], s)))

# ---- PART 5: F3, a label its own operand sets but no match of the program's `&` operands can ----
OP = r"(?P<o>\d)x|y"
F3POOL = M.strings("1xy ", 4)
isy = lambda s, i, j: re.fullmatch("y", s[i:j]) is not None
F3 = [("/(?<o>\\d)x|y/ & /y/", P2(OP, [], [], [isy])),
      ("/(?<o>\\d)x|y/ & /y/ & (o = \"1\": <5)", P2(OP, [test("o", lt(5), "1")], [], [isy])),
      ("/(?<o>\\d)x|y/ & /y/ & (o: <5)", P2(OP, [test("o", lt(5))], [], [isy])),
      ("/(?<o>\\d)x|y/ & /y/ & NOT (o = \"9\": <5)", P2(OP, [NOT(test("o", lt(5), "9"))], [], [isy]))]
for mode in MODES:
    for nm, P in order(F3):
        c, _ = count(F3POOL, lambda s: B.holds(mode, P, s))
        d, w = count(F3POOL, lambda s: B.holds(mode, P, s) != B.holds(mode, F3[0][1], s))
        emit((5, mode, nm), "  LABEL-NO-MATCH %s (%d texts) %s holds %d; vs the program without the test differ %d first %r" % (mode, len(F3POOL), nm, c, d, w))

# ---- PART 6: F12, NOT over a nested program (the third value does not cross a `label:` boundary) ----
q = B.q
X = r"(?P<x>[\d:]+)"
inq = lambda v: B.whole(q, v)
F12 = [("X & (x: q)", P2(X, [lambda r: None if r.get("x") is None else inq(r["x"])])),
       ("X & NOT (x: q)", P2(X, [NOT(lambda r: None if r.get("x") is None else inq(r["x"]))])),
       ("X & (x: !q)", P2(X, [lambda r: None if r.get("x") is None else (not inq(r["x"]))])),
       ("X & (x: t2 & NOT late)", P2(X, [lambda r: None if r.get("x") is None else B.whole(P2(T2, [NOT(B.late)]), r["x"])])),
       ("t2 & NOT late (flat)", P2(T2, [NOT(B.late)])),
       ("t2 & !q (difference, flat)", P2(T2, [], [q]))]
for nm, P in order(F12):
    for s in order(["9", "9:30", "9:15"]):
        emit((6, nm, s), "  NESTED %s on `%s`: %s" % (nm, s, B.both(P, s)))

# ---- PART 7: F11 / F4, find-all is not monotone; the hit list of a filtered argument ----
NUM = r"(?P<n>\d+)"
for nm, P in order([("/(?<n>\\d+)/", P2(NUM)), ("/(?<n>\\d+)/ & (n: <100)", P2(NUM, [test("n", lt(100))]))]):
    for s in order(["1234", "123456"]):
        emit((7, 1, nm, s), "  FIND-ALL %s on `%s`: %s" % (nm, s, B.fa(P, s)))
SET100 = [str(k) for k in range(100)]
for nm, alts in order([("longest-first", sorted(SET100, key=lambda x: (-len(x), x))), ("shortest-first", sorted(SET100, key=lambda x: (len(x), x)))]):
    rx = re.compile("(?:" + "|".join(alts) + ")")
    emit((7, 2, nm), "  HITS string-set reading of the argument (set's alternation %s) on `1234`: %s" % (nm, [m.group(0) for m in rx.finditer("1234")]))

# ---- PART 8: F17, a nullable B in text.none / !contains ----
BN = P2(NL, [ptest("n", ge(5), "9")], passre=NLP)
def tn_def(s): return not any(B.accept(BN, s, k, l) for k in range(len(s) + 1) for l in range(k, len(s) + 1))
def tn_eng(s): return not any(B.accept(BN, s, k, l) for k in range(len(s) + 1) for l in range(k + 1, len(s) + 1))
for s in order(["", "1,", "a", "7,"]):
    emit((8, s), "  NULLABLE-B B = /(?:(?<n>\\d),)*/ & (n = 9: >=5), text.none(B) on `%s`: by the definition (empty rows included) %s ; non-empty rows only %s" % (s, tn_def(s), tn_eng(s)))

# ---- PART 9: the re-allowed-NOT sweep: SAME rows that need a run ----
# L56 / L65: under NOT (n: <5), on the span `x`
for nm, A in order([("/(?<n>\\d)?x/", r"(?P<n>\d)?x"), ("/(?<n>\\d)*x/", r"(?:(?P<n>\d))*x"), ("/x|(?<n>\\d)+/", r"x|(?:(?P<n>\d))+")]):
    loop = "*" in A or "+" in A
    c = ptest("n", lt(5)) if loop else test("n", lt(5))
    P = P2(A, [NOT(c)], passre=(r"(?P<n>\d)" if loop else None))
    emit((9, 1, nm), "  SWEEP L56/L65 %s & NOT (n: <5) on `x`: %s" % (nm, B.both(P, "x")))
# L94 with NOT on the whole record
L94POOL = B.L94POOL
for mode in MODES:
    rec94 = lambda r: M.k_and([test("h", lt(5))(r), test("k", between(3, 7), "3")(r)])
    PA, PB = P2(B.L94A, [NOT(rec94)]), P2(B.L94B, [NOT(rec94)])
    d, w = count(L94POOL, lambda s: B.holds(mode, PA, s) != B.holds(mode, PB, s))
    emit((9, 2, mode), "  SWEEP L94 %s NOT (h: <5, k = 3: between(3, 7)): /x?/ vs /(?:x|)/ differ %d of 121 first %r" % (mode, d, w))
# L55 with NOT inside: (m: occurrences(r) & NOT (g: "x")) vs the min = 1 form, on spans with NO hit
RG = B.RG
OCCPOOL = M.strings("abxy", 4)
nohit = [s for s in OCCPOOL if re.search(RG, s) is None]
c0 = NOT(ptest("g", B.eqx))
P0 = P2(r"(?s:.*)", [c0], passre=RG)
P1 = P2(r"(?s:.*)", [c0, lambda r: len(r["_real"]) >= 1], passre=RG)
d, w = count(nohit, lambda s: B.whole(P0, s) != B.whole(P1, s))
n0, _ = count(nohit, lambda s: B.whole(P0, s))
emit((9, 3), "  SWEEP L55 WHOLE (%d spans over {a,b,x,y} to length 4 with no hit) occurrences(r) & NOT (g: \"x\") vs min = 1: differ %d first %r (the first holds on %d)" % (len(nohit), d, w, n0))
# L30's edges: answers (the compile verdicts are text, §5.2)
for mode in MODES:
    for a_, b_ in order([(0, 1), (2, 3)]):
        d, w = count(SVPOOL, lambda s: B.holds(mode, F8[a_][3], s) != B.holds(mode, F8[b_][3], s))
        emit((9, 4, mode, a_), "  SWEEP L30 %s SV (341) [%s] vs [%s] differ %d first %r" % (mode, F8[a_][2], F8[b_][2], d, w))

for k in sorted(LINES, key=lambda k: tuple(str(x) for x in k)): print(LINES[k])
print("END")
