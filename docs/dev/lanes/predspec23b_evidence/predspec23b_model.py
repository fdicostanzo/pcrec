#!/usr/bin/env python3
# Lane predspec23b (2026-11-17): evidence for the body of docs/design/predicates_draft.md rev 23 (DESIGN ONLY;
# rules nothing). It re-runs, in BOTH modes (WHOLE value and SEARCHED), every worked example the rev 23 body rewrite
# touches (sections 0.1, 2.6, 4.3, 4.4, 8, 13) and lays out the two WHOLE-TEXT ROUTES (rev 23 section R.4).
#
# The model is predspec23's (docs/dev/lanes/predspec23_evidence/predspec23_model.py, imported READ-ONLY; its own
# output is suppressed): rows are potential matches; a condition is a three-valued test of one row (Kleene `&`, NOT;
# M.k_and / M.k_not are used, so its SWAP and SABOTAGE switches reach this script); absent never matches; a default is
# per test; complement after `&` = pattern difference; SEARCHED = candidate R22 (leftmost start, then the left
# operand's preference order of ends; any filter may send the search to the next end). This script adds a small
# engine of the same shape (P2) because predspec23's rows carry ONE looped label: P2's pass rows carry every label
# the pass sets (joint conditions over loops, the pairing loop with a label outside it), `|` of two filtered
# patterns (when's body), find-all (later matches, non-overlapping, resuming at the reported end), and the two
# whole-text routes. Its CONTROL lines re-derive predspec23's and predspec21's T2 numbers (PART 0).
# The draft's readings implemented (each named in the draft): R1 (a loop's passes are a nested table; zero passes
# = one null pass row); a plain condition on a looped label = Kleene AND over the pass rows; `some` = EXISTS over the
# real passes; the pairing loop pairs an outside label with every pass. ROUTE (i)'s reading of a condition inside a
# lookahead is THIS LANE'S (the draft says so): the lookahead at a position holds when the rows of its own search,
# filtered by its conditions, are (positive) some / (negative) none.
# `padded(S)` on a numeral part = the part with leading zeros read as its number (rev 22 section 2.7's body
# /0*${S}/); Python `re` stands in for PCRE (greedy, anchor-free regexes, plus \A where named).
#
# Commands (W = the worktree; run from a scratch dir under $PCREC_TMPDIR):
#   timeout 600 python3 -I W/docs/dev/lanes/predspec23b_evidence/predspec23b_model.py > fwd.out
#   PREDSPEC23B_SWAP=1 timeout 600 python3 -I W/docs/dev/lanes/predspec23b_evidence/predspec23b_model.py > swap.out
#   diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)        # must print nothing
#   PREDSPEC23B_SABOTAGE=1 (forward and swapped): the diff must print something (the swap check can fail)
# SWAP reverses every order this script has (pools, condition and filter lists, pass lists, line computation) and
# sets predspec23's own SWAP; SABOTAGE sets predspec23's SABOTAGE (Kleene AND = "the first non-TRUE value"), so NOT
# over a looped label, and the counts that use it, depend on order.
import os, sys, re, io, contextlib

SWAP = os.environ.get("PREDSPEC23B_SWAP") == "1"
SAB = os.environ.get("PREDSPEC23B_SABOTAGE") == "1"
os.environ["PREDSPEC23_SWAP"] = "1" if SWAP else "0"
os.environ["PREDSPEC23_SABOTAGE"] = "1" if SAB else "0"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "predspec23_evidence"))
with contextlib.redirect_stdout(io.StringIO()):
    import predspec23_model as M                     # read-only import; runs its own parts silently
print("ORDER: %s%s" % ("SWAPPED" if SWAP else "forward", " SABOTAGE" if SAB else ""))
def order(xs): return list(reversed(list(xs))) if SWAP else list(xs)
kand, knot = M.k_and, M.k_not

# ---- P2: a statement whose pass rows carry every label of the pass ----
class P2:
    def __init__(self, A, conds=(), comps=(), filters=(), textq=(), passre=None, alt=None, start0=False):
        self.A = re.compile(A) if isinstance(A, str) else A
        self.conds, self.comps, self.filters, self.textq = order(conds), order(comps), order(filters), order(textq)
        self.passre = re.compile(passre) if passre else None
        self.alt = alt                               # `P | Q` of filtered patterns over ONE left regex: PCRE's one parse,
        self.start0 = start0                         # branch 1 first, the next branch when its filters reject
def row(P, s, i, j):
    m = P.A.fullmatch(s[i:j])
    if m is None: return None
    r = dict(m.groupdict())
    if P.passre is not None:
        looped = set(P.passre.groupindex)
        outer = {k: v for k, v in r.items() if k not in looped}
        real = [dict(outer, **pm.groupdict()) for pm in P.passre.finditer(s[i:j])]
        r["_real"] = real                        # pass order reversed under SWAP by M.k_and itself (once)
        r["_passes"] = r["_real"] if real else [dict(outer, **{k: None for k in looped})]
    return r
def accept(P, s, i, j):
    if P.alt is not None: return any(accept(B, s, i, j) for B in P.alt)
    if P.start0 and i != 0: return False
    r = row(P, s, i, j)
    if r is None: return False
    if not all(c(r) is True for c in P.conds): return False
    if not all(f(s, i, j) for f in P.filters): return False
    if not all(t(s) for t in P.textq): return False
    return not any(accept(B, s, i, j) for B in P.comps)
def leftA(P): return P.alt[0].A if P.alt is not None else P.A
def ends_pref(P, s, i):
    A = leftA(P); m = A.match(s, i)
    first = [m.end()] if m else []
    return first + [j for j in range(len(s), i - 1, -1) if j not in first and A.fullmatch(s[i:j])]
def search_from(P, s, pos):
    for i in range(pos, len(s) + 1):
        for j in ends_pref(P, s, i):
            if accept(P, s, i, j): return (i, j)
    return None
def whole(P, s): return accept(P, s, 0, len(s))
def searched(P, s): return search_from(P, s, 0)
def findall(P, s, first_only=False):
    out, pos = [], 0
    while pos <= len(s):
        r = search_from(P, s, pos)
        if r is None: break
        out.append(r)
        if first_only: break
        pos = r[1] if r[1] > r[0] else r[1] + 1
    return out
def holds(mode, P, s): return whole(P, s) if mode == "WHOLE" else searched(P, s) is not None
def rep(mode, P, s):
    if mode == "WHOLE": return "HOLDS" if whole(P, s) else "FAILS"
    r = searched(P, s)
    return "FAILS" if r is None else "HOLDS `%s`@%d" % (s[r[0]:r[1]], r[0])
def both(P, s): return "WHOLE %s | SEARCHED %s" % (rep("WHOLE", P, s), rep("SEARCHED", P, s))
def fa(P, s, first_only=False):
    return "[" + ", ".join("`%s`@%d" % (s[i:j], i) for i, j in findall(P, s, first_only)) + "]"

# ---- conditions ----
def numeral(v): return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None
def pnum(v): return v is not None and re.fullmatch(r"\d+", v) is not None          # padded: leading zeros read away
def dv(v, d): return v if v is not None else d
def test(lab, S, d=None):                           # (lab = d: S) on a set-once label
    def c(r):
        v = dv(r.get(lab), d)
        return None if v is None else bool(S(v))
    return c
def ptest(lab, S, d=None):                          # (lab = d: S) on a looped label: Kleene AND over pass rows
    def c(r):
        return kand([(None if dv(p.get(lab), d) is None else bool(S(dv(p.get(lab), d)))) for p in r["_passes"]])
    return c
def pjoint(labs, defs, S):                          # ((l1 = d1, ...): S) per pass row (pairing loop); absent part -> UNKNOWN
    def one(p):
        vs = [dv(p.get(l), d) for l, d in zip(labs, defs)]
        return None if any(v is None for v in vs) else bool(S(*vs))
    return lambda r: kand([one(p) for p in r["_passes"]])
def joint(labs, defs, S):                           # set-once joint
    def c(r):
        vs = [dv(r.get(l), d) for l, d in zip(labs, defs)]
        return None if any(v is None for v in vs) else bool(S(*vs))
    return c
def some_(f): return lambda r: any(f(p) is True for p in r["_real"])
def count_(f): return lambda r: sum(1 for p in r["_real"] if f(p) is True)
def NOT(c): return lambda r: knot(c(r))
def AND(*cs): return lambda r: kand([c(r) for c in cs])
def lt(n): return lambda v: numeral(v) and int(v) < n
def ge(n): return lambda v: numeral(v) and int(v) >= n
def between(a, b): return lambda v: numeral(v) and a <= int(v) <= b
def ptup_ge(lo): return lambda *vs: all(pnum(v) for v in vs) and tuple(int(v) for v in vs) >= lo
def ptup_between(lo, hi): return lambda *vs: all(pnum(v) for v in vs) and lo <= tuple(int(v) for v in vs) <= hi

LINES = {}
def emit(key, text): LINES[key] = text
def count(pool, pred):
    hits = [s for s in order(pool) if pred(s)]
    return len(hits), (min(hits, key=lambda x: (len(x), x)) if hits else None)
MODES = order(["WHOLE", "SEARCHED"])

# ---- pools ----
T2 = r"(?P<h>\d{1,2})(?::(?P<m>\d\d))?"
T2POOL = M.T2POOL                                    # 11,110 (predspec23's)
TOK = [h + mm for h in ["1", "9", "10", "21"] for mm in ["", ":00", ":15", ":30", ":45", ":50"]]
T2PAIRS = TOK + [a + " " + b for a in TOK for b in TOK]   # 600, lane searchrow's two-time pool
assert len(T2PAIRS) == 600
def late(r):                                         # ((h, m): >= (9, 30)): absent part -> UNKNOWN
    return None if r.get("h") is None or r.get("m") is None else (int(r["h"]), int(r["m"])) >= (9, 30)
q = P2(T2, [late])

# ---- PART 0: CONTROL: P2 re-derives predspec23's and predspec21's T2 numbers ----
for mode in MODES:
    c, _ = count(T2POOL, lambda s: holds(mode, P2(T2, [], [q]), s))
    emit((0, 1, mode), "  CONTROL %s T2 (11,110) t2 & !q holds %d (predspec23 PART 3: WHOLE 1970, SEARCHED 11110)" % (mode, c))
PL = lambda m0: P2(T2, [joint(["h", "m"], [None, m0], ptup_ge((9, 30)))])
for name, P in order([("((h, m = 0): padded(>= (9, 30)))", PL("0")), ("((h, m): padded(>= (9, 30)))", PL(None))]):
    c, w = count(T2POOL, lambda s: holds("WHOLE", P, s) != holds("SEARCHED", P, s))
    emit((0, 2, name), "  MODE (sec 0.1) t2 & %s: WHOLE vs SEARCHED differ on %d of 11,110, first %r (rev 21: 1,660 under m = 0, 0 unmarked)" % (name, c, w))

# ---- PART 1: sec 0.1 L94 rewritten: (h: <5, k = 3: between(3, 7)) on /x?/ vs /(?:x|)/ ----
L94A = r"(?P<k>\d)?-(?P<h>\d)?"
L94B = r"(?:(?P<k>\d)|)-(?:(?P<h>\d)|)"
L94POOL = [a + "-" + b for a in [""] + list(M.D) for b in [""] + list(M.D)]
assert len(L94POOL) == 121
for kd in order([None, "3"]):
    cs = [test("h", lt(5)), test("k", between(3, 7), kd)]
    PA, PB = P2(L94A, cs), P2(L94B, cs)
    for mode in MODES:
        c, w = count(L94POOL, lambda s: holds(mode, PA, s) != holds(mode, PB, s))
        n, _ = count(L94POOL, lambda s: holds(mode, PA, s))
        emit((1, str(kd), mode), "  L94 (h: <5, k%s: between(3, 7)) %s: /x?/ holds %d of 121; vs /(?:x|)/ differ %d first %r" % (
            "" if kd is None else " = " + kd, mode, n, c, w))

# ---- PART 2: sec 2.6, occurrences hits (min = 0): the worked rows ----
OCC = lambda r_, conds: P2(r"(?s:.*)", conds, passre=r_)
RG = r"ab(?P<g>[xy])"
eqx = lambda v: v == "x"
for name, c in order([("(g: \"x\") plain", ptest("g", eqx)),
                      ("(g = \"x\": \"x\") every hit, possibly none", ptest("g", eqx, "x")),
                      ("occurs.none((g = \"\": !\"x\")) narrower", lambda r: not any(dv(p.get("g"), "") != "x" for p in r["_real"])),
                      ("some((g: \"x\"))", some_(lambda p: None if p.get("g") is None else p["g"] == "x")),
                      ("occurs.exactly(2, (g: \"x\"))", lambda r: count_(lambda p: None if p.get("g") is None else p["g"] == "x")(r) == 2),
                      ("count((g: \"y\")) == 1", lambda r: count_(lambda p: None if p.get("g") is None else p["g"] == "y")(r) == 1)]):
    for s in order(["abxabyabx", "xyz"]):
        emit((2, name, s), "  OCC /ab(?<g>[xy])/ %s on `%s`: %s" % (name, s, both(OCC(RG, [c]), s)))
# SAME ITERATION BY RECORD (sec 4.3): /(?<g>[xy])(?<h>\d)/ hits
RGH = r"(?P<g>[xy])(?P<h>\d)"
rec_some = some_(lambda p: None if p.get("g") is None or p.get("h") is None else (p["g"] == "x" and p["h"] == "1"))
two_some = AND(some_(lambda p: None if p.get("g") is None else p["g"] == "x"), some_(lambda p: None if p.get("h") is None else p["h"] == "1"))
for s in order(["x2 y1", "x1 y2"]):
    emit((2, "rec", s), "  OCC record some((g: \"x\", h: 1)) on `%s`: %s ; some((g: \"x\")) & some((h: 1)): %s" % (
        s, both(OCC(RGH, [rec_some]), s), both(OCC(RGH, [two_some]), s)))

# ---- PART 3: sec 4.3 THE PAIRING RULE examples ----
LIST = r"(?:(?P<h>\d{1,2}):(?P<m>\d\d),)*"
LISTP = r"(?P<h>\d{1,2}):(?P<m>\d\d),"
P = P2(LIST, [pjoint(["h", "m"], [None, None], ptup_ge((9, 30)))], passre=LISTP)
emit((3, 1), "  PAIR list & ((h, m): padded(>= (9, 30))) on `10:00,9:30,`: %s" % both(P, "10:00,9:30,"))
KH = r"(?P<k>\d)(?:;(?P<h>\d))*"
KHP = r";(?P<h>\d)"
KHPOOL = [k + "".join(";" + x for x in t) for k in M.D for t in [()] + [(a,) for a in M.D] + [(a, b) for a in M.D for b in M.D]]
assert len(KHPOOL) == 1110
rec = lambda hd: P2(KH, [pjoint(["h", "k"], [hd, None], lambda h, k: lt(5)(h) and between(3, 7)(k))], passre=KHP)
amp = lambda hd: P2(KH, [ptest("h", lt(5), hd), test("k", between(3, 7))], passre=KHP)
for hd in order([None, "0"]):
    nm = "h" if hd is None else "h = 0"
    for s in order(["9", "3", "3;4", "3;7"]):
        emit((3, 2, nm, s), "  PAIR /(?<k>\\d)(?:;(?<h>\\d))*/ & (%s: <5, k: between(3, 7)) on `%s`: %s" % (nm, s, both(rec(hd), s)))
    for mode in MODES:
        c, w = count(KHPOOL, lambda s: holds(mode, rec(hd), s) != holds(mode, amp(hd), s))
        emit((3, 3, nm, mode), "  PAIR record (%s: <5, k: between(3, 7)) vs (%s: <5) & (k: between(3, 7)) %s: differ %d of 1,110 first %r" % (nm, nm, mode, c, w))
AB = r"(?:(?P<a>\d)?-(?P<b>\d)?,)*"
ABP = r"(?P<a>\d)?-(?P<b>\d)?,"
for name, ds in order([("(a: <5, b: between(3, 7))", (None, None)), ("(a = 0: <5, b = 3: between(3, 7))", ("0", "3"))]):
    PA = P2(AB, [pjoint(["a", "b"], list(ds), lambda a, b: lt(5)(a) and between(3, 7)(b))], passre=ABP)
    for s in order(["3-6,", "7-2,", "", "-6,", "3-6,-,"]):
        emit((3, 4, name, s), "  PAIR /(?:(?<a>\\d)?-(?<b>\\d)?,)*/ & %s on `%s`: %s" % (name, s, both(PA, s)))

# ---- PART 4: sec 4.4 a computed label reading an absent label ----
MN = r"(?P<mname>Jan|Feb|Mar)?-(?P<d>\d)"
IDX = {"Jan": "1", "Feb": "2", "Mar": "3"}
def mnum_test(S, d=None):
    def c(r):
        v = IDX.get(r.get("mname")) if r.get("mname") is not None else None    # absent input -> absent computed label
        v = dv(v, d)
        return None if v is None else bool(S(v))
    return c
for name, c in order([("(mnum: <3)", mnum_test(lt(3))), ("(mnum = 9: <3)", mnum_test(lt(3), "9")),
                      ("(mnum = 1: <3)", mnum_test(lt(3), "1")), ("NOT (mnum: <3)", NOT(mnum_test(lt(3))))]):
    for s in order(["-5", "Feb-5", "Mar-5"]):
        emit((4, name, s), "  COMPUTED mnum := $mname.index over /(?<mname>Jan|Feb|Mar)?-(?<d>\\d)/ & %s on `%s`: %s" % (name, s, both(P2(MN, [c]), s)))

# ---- PART 5: sec 8 when(c, p) = (x & c & p) | (x & !q), q := x & c; and the TM2-L list table; caveat (2) ----
def when_body(c, p, notc=False):
    qq = P2(KH, [c], passre=KHP)
    b1 = P2(KH, [c, p], passre=KHP)
    b2 = P2(KH, [NOT(c)], passre=KHP) if notc else P2(KH, [], [qq], passre=KHP)
    return P2(KH, alt=[b1, b2])
pk = test("k", between(3, 7))
for nm, c in order([("(h: <5)", ptest("h", lt(5))), ("(h = 0: <5)", ptest("h", lt(5), "0"))]):
    for s in order(["0", "5", "5;1", "5;9", "0;9"]):
        emit((5, 1, nm, s), "  WHEN x & when(%s, (k: between(3, 7))) on `%s`: %s ; with NOT c in place of !q: %s" % (
            nm, s, both(when_body(c, pk), s), both(when_body(c, pk, True), s)))
    for mode in MODES:
        n, _ = count(KHPOOL, lambda s: holds(mode, when_body(c, pk), s))
        d, w = count(KHPOOL, lambda s: holds(mode, when_body(c, pk), s) != holds(mode, when_body(c, pk, True), s))
        emit((5, 2, nm, mode), "  WHEN %s c = %s: body holds %d of 1,110; body vs the NOT-c body differ %d first %r" % (mode, nm, n, d, w))
CL = r"(?:(?P<h>\d{1,2})(?::(?P<m>\d\d))?,)*"
CLP = r"(?P<h>\d{1,2})(?::(?P<m>\d\d))?,"
for name, ds in order([("((h, m): R)", (None, None)), ("((h, m = 0): R)", (None, "0")),
                       ("((h = 10, m = 0): R)", ("10", "0")), ("((h = 10, m = 30): R)", ("10", "30")),
                       ("((h, m = 30): R)", (None, "30"))]):
    PT = P2(CL, [pjoint(["h", "m"], list(ds), ptup_ge((9, 30)))], passre=CLP)
    cells = ["`%s` %s/%s" % (s, "H" if whole(PT, s) else "F", "H" if searched(PT, s) else "F") for s in ["", "10,", "9,", "9:45,", "10,9:15,"]]
    emit((5, 3, name), "  TM2-L R = padded(>= (9, 30)) %s (WHOLE/SEARCHED): %s" % (name, " ; ".join(cells)))
for name, md in order([("((h, m): padded(between((9, 30), (11, 0))))", None), ("((h, m = 0): padded(between((9, 30), (11, 0))))", "0")]):
    emit((5, 4, name), "  CAVEAT2 t2 & %s on `10`: %s" % (name, both(P2(T2, [joint(["h", "m"], [None, md], ptup_between((9, 30), (11, 0)))]), "10")))

# ---- PART 6: sec 13 O28 under rev 23: NOT c, (x: !S), P & !q on a repeated n and on t2's joint ----
RN = r"(?:(?P<n>\d)?,)*"
RNP = r"(?P<n>\d)?,"
RNPOOL = M.strings("17,", 5)
O28 = [("(n: <5)", P2(RN, [ptest("n", lt(5))], passre=RNP)),
       ("NOT (n: <5)", P2(RN, [NOT(ptest("n", lt(5)))], passre=RNP)),
       ("(n: !<5)", P2(RN, [ptest("n", lambda v: not lt(5)(v))], passre=RNP)),
       ("P & !(P & (n: <5))", P2(RN, [], [P2(RN, [ptest("n", lt(5))], passre=RNP)], passre=RNP))]
for name, PP in order(O28):
    for s in order(["1,7,", "7,", "", "7,,"]):
        emit((6, 1, name, s), "  O28 /(?:(?<n>\\d)?,)*/ & %s on `%s`: %s" % (name, s, both(PP, s)))
    for mode in MODES:
        c, w = count(RNPOOL, lambda s: holds(mode, PP, s))
        emit((6, 2, name, mode), "  O28 %s pool {1,7,comma} to length 5 (%d texts) %s holds %d first %r" % (mode, len(RNPOOL), name, c, w))
for mode in MODES:
    c, w = count(RNPOOL, lambda s: holds(mode, O28[1][1], s) != holds(mode, O28[2][1], s))
    emit((6, 3, mode), "  O28 %s NOT (n: <5) vs (n: !<5) differ %d first %r" % (mode, c, w))
R930 = ptup_ge((9, 30))
for name, PP in order([("((h, m): R)", P2(T2, [joint(["h", "m"], [None, None], R930)])),
                       ("NOT ((h, m): R)", P2(T2, [NOT(joint(["h", "m"], [None, None], R930))])),
                       ("((h, m): !R)", P2(T2, [joint(["h", "m"], [None, None], lambda h, m: not R930(h, m))])),
                       ("t2 & !(t2 & ((h, m): R))", P2(T2, [], [P2(T2, [joint(["h", "m"], [None, None], R930)])])),
                       ("((h, m = 00): R)", P2(T2, [joint(["h", "m"], [None, "00"], R930)])),
                       ("NOT ((h, m = 00): R)", P2(T2, [NOT(joint(["h", "m"], [None, "00"], R930))])),
                       ("((h, m = 00): !R)", P2(T2, [joint(["h", "m"], [None, "00"], lambda h, m: not R930(h, m))]))]):
    emit((6, 4, name), "  O28 t2 & %s (R = padded(>= (9, 30))) on `9`: %s" % (name, both(PP, "9")))

# ---- PART 7: THE WHOLE-TEXT ROUTES ----
def q_rows(s, lo=0):                                 # every row of q (searched) starting at or after lo
    return [(k, l) for k in range(lo, len(s) + 1) for l in range(k + 1, len(s) + 1) if accept(q, s, k, l)]
def q_from_here_none(s, i, j): return not q_rows(s, i)        # route (i)(a): /(?![\s\S]*${q})/ at the row's start
def text_none(s): return not q_rows(s, 0)                     # route (ii): text.none(q)
ROUTES = [
    ("t2 & !q (pattern difference, today)", P2(T2, [], [q])),
    ("t2 & !contains(q) (today)", P2(T2, [], [], [lambda s, i, j: not any(accept(q, s, k, l) for k in range(i, j + 1) for l in range(k + 1, j + 1))])),
    ("(i)(a) /(?![\\s\\S]*${q})${t2}/ (lookahead at the row's start)", P2(T2, [], [], [q_from_here_none])),
    ("(i)(b) /\\A(?![\\s\\S]*${q})[\\s\\S]*?${t2}/ (gate at the text's start)", P2(r"(?s:.*?)" + T2, [], [], [], [text_none], start0=True)),
    ("(ii) t2 & text.none(q)", P2(T2, [], [], [], [text_none])),
]
SUBJ = ["9:30", "9:15", "9:15 9:30", "9:30 9:15", "9:30 1"]
for name, PP in order(ROUTES):
    for s in order(SUBJ):
        emit((7, 1, name, s), "  ROUTE %s on `%s`: %s ; find-all %s" % (name, s, both(PP, s), fa(PP, s)))
for mode in MODES:
    for poolname, pool in order([("T2 (11,110)", T2POOL), ("T2PAIRS (600)", T2PAIRS)]):
        for name, PP in order(ROUTES):
            c, w = count(pool, lambda s: holds(mode, PP, s))
            emit((7, 2, mode, poolname, name), "  ROUTE %s %s %s holds %d first %r" % (mode, poolname, name, c, w))
        for a_, b_ in order([(2, 4), (3, 4), (0, 4)]):
            c, w = count(pool, lambda s: holds(mode, ROUTES[a_][1], s) != holds(mode, ROUTES[b_][1], s))
            emit((7, 3, mode, poolname, a_, b_), "  ROUTE %s %s [%s] vs [%s] differ %d first %r" % (mode, poolname, ROUTES[a_][0], ROUTES[b_][0], c, w))
# find-all: how many texts of T2PAIRS report MORE THAN ONE match under each route, and route (ii)'s all-or-none
for name, PP in order(ROUTES):
    multi, _ = count(T2PAIRS, lambda s: len(findall(PP, s)) > 1)
    emit((7, 4, name), "  ROUTE FIND-ALL T2PAIRS (600) %s: texts with 2+ matches %d" % (name, multi))

for k in sorted(LINES, key=lambda k: tuple(str(x) for x in k)): print(LINES[k])
print("END")
