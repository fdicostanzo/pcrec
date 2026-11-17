#!/usr/bin/env python3
# Lane predspec23 (2026-11-16): evidence for docs/design/predicates_draft.md rev 23 (DESIGN ONLY; rules nothing).
# The model as ruled 19:31-23:48 (COND-FAMILY.md): a row is ONE POTENTIAL MATCH (a stretch with its labels and its
# pass table); a condition is a three-valued test of one row (TRUE / FALSE / UNKNOWN = None); `&` and NOT on
# conditions are Kleene's; absent never matches; a default is per test (COALESCE inside the one test that writes it);
# `$a` reads the real label; a complement after `&` is pattern difference; `|` is PCRE's one parse (not run here).
# SEARCHED mode = candidate R22 of lane searchrow (docs/dev/lanes/searchrow_evidence/searchrow.py): D196's leftmost
# start, then the left operand's preference order of ends; every filter (a complement too) may send the search to
# the next end. WHOLE mode = the row is the whole value. NOT on a condition is NEW here, implemented from the
# 23:48 record's text ("a condition on an absent label is unknown, its NOT is unknown, the row is dropped").
# The draft's readings implemented here (each named in rev 23 as the draft's): R1 (a looped label's passes are a
# nested table of the row; zero passes = one pass row with the label absent, rev 22's LEFT JOIN row); a plain
# condition on a repeated label = Kleene AND over its pass rows; `some(c)` = SQL EXISTS over the REAL passes
# (two-valued), `occurs.none(c)` = no real pass where c is TRUE, `count(c)` = real passes where c is TRUE.
# Python `re` stands in for PCRE (no anchors or lookarounds in the regexes used; greedy only).
#
# Commands (W = the worktree; run from a scratch dir under $PCREC_TMPDIR):
#   timeout 300 python3 -I W/docs/dev/lanes/predspec23_evidence/predspec23_model.py > fwd.out
#   PREDSPEC23_SWAP=1 timeout 300 python3 -I W/docs/dev/lanes/predspec23_evidence/predspec23_model.py > swap.out
#   diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)        # must print nothing
#   PREDSPEC23_SABOTAGE=1 (forward and swapped): the diff must print something (the swap check can fail)
# SWAP reverses every order the script has: pools, pass lists, condition lists, filter lists, line computation.
# SABOTAGE replaces Kleene AND by "the first non-TRUE value" (UNKNOWN vs FALSE then depends on order), so NOT of a
# plain condition on a repeated label, and so the counts, depend on order.
import os, re

SWAP = os.environ.get("PREDSPEC23_SWAP") == "1"
SAB = os.environ.get("PREDSPEC23_SABOTAGE") == "1"
print("ORDER: %s%s" % ("SWAPPED" if SWAP else "forward", " SABOTAGE" if SAB else ""))
def order(xs): return list(reversed(list(xs))) if SWAP else list(xs)

# ---- three-valued logic (Kleene; SQL's) ----
def k_and(vals):
    vals = order(vals)
    if SAB:
        for v in vals:
            if v is not True: return v
        return True
    if any(v is False for v in vals): return False
    if any(v is None for v in vals): return None
    return True
def k_not(v): return None if v is None else (not v)

# ---- statements ----
class Prog:
    """A statement: left operand A (a regex), conditions (three-valued tests of one row), complements (statements),
    label-free filters on the stretch (contains / !contains), text-level tests (the whole-text question)."""
    def __init__(self, A, conds=(), comps=(), filters=(), textq=(), passre=None, rep=None):
        self.A = re.compile(A); self.conds = order(conds); self.comps = order(comps)
        self.filters = order(filters); self.textq = order(textq)
        self.passre = re.compile(passre) if passre else None; self.rep = rep

def row_at(P, s, i, j):
    m = P.A.fullmatch(s[i:j])
    if m is None: return None
    r = dict(m.groupdict())
    if P.passre is not None:                      # R1: the loop's passes as a nested table; zero passes = one null row
        ps = [pm.groupdict().get(P.rep) for pm in P.passre.finditer(s[i:j])]
        r["_real"] = ps
        r["_passes"] = ps if ps else [None]
    return r

def ends_pref(P, s, i):
    m = P.A.match(s, i)
    first = [m.end()] if m and row_at(P, s, i, m.end()) is not None else []
    rest = [j for j in range(len(s), i - 1, -1) if j not in first and row_at(P, s, i, j) is not None]
    return first + rest

def accept(P, s, i, j):
    r = row_at(P, s, i, j)
    if r is None: return False
    if not all(c(r) is True for c in P.conds): return False
    if not all(f(s, i, j) for f in P.filters): return False
    if not all(t(s) for t in P.textq): return False
    return not any(accept(B, s, i, j) for B in P.comps)

def whole(P, s): return accept(P, s, 0, len(s))
def searched(P, s):
    """R22: the first reported row (leftmost start, first admitted end in preference order), or None."""
    for i in range(len(s) + 1):
        for j in ends_pref(P, s, i):
            if accept(P, s, i, j): return (i, j)
    return None
def holds(mode, P, s): return whole(P, s) if mode == "WHOLE" else searched(P, s) is not None
def rep(mode, P, s):
    if mode == "WHOLE": return "HOLDS" if whole(P, s) else "FAILS"
    r = searched(P, s)
    return "FAILS" if r is None else "HOLDS `%s`@%d" % (s[r[0]:r[1]], r[0])

# ---- conditions ----
def numeral(v): return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None
def lt(n): return lambda v: numeral(v) and int(v) < n          # `<n`: a set of canonical numerals (rev 22 §2.4)
def ge(n): return lambda v: numeral(v) and int(v) >= n
def notset(S): return lambda v: not S(v)                       # `!S`: complement over EVERY text (review r31 G)
def test(label, S, default=None):
    """(label = default: S) on a set-once label: COALESCE inside this one test; absent -> UNKNOWN."""
    def c(r):
        v = r.get(label)
        if v is None: v = default
        if v is None: return None
        return bool(S(v))
    return c
def rtest(S, default=None):
    """(h = default: S) on a REPEATED label: Kleene AND over the pass rows (R1; zero passes = one null row)."""
    def c(r):
        return k_and([(None if (v if v is not None else default) is None else bool(S(v if v is not None else default)))
                      for v in r["_passes"]])
    return c
def NOT(c): return lambda r: k_not(c(r))
def AND(*cs): return lambda r: k_and([c(r) for c in cs])
def some(S, default=None):                                      # EXISTS over the real passes (two-valued)
    return lambda r: any((v if v is not None else default) is not None and S(v if v is not None else default)
                         for v in r["_real"])
def none_(S, default=None): return lambda r: not some(S, default)(r)

# ---- pools ----
def strings(alpha, n):
    out, cur = [""], [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
SV = "(?P<h>\\d)?x"                                             # rev 22's /(?<h>\d)?x/: h set at most once
SVPOOL = [s for s in strings("37x ", 4)]                        # 341 subjects (searched variety); WHOLE rows = `x`,`3x`,`7x`
REP = "(?:(?P<h>\\d)?;)*"                                       # h repeated; a pass may lack h; zero passes possible
REPPASS = "(?P<h>\\d)?;"
REPPOOL = strings("37;", 5)                                     # 364 subjects
T2 = r"(?P<h>\d{1,2})(?::(?P<m>\d\d))?"
D = "0123456789"
H12 = list(D) + [a + b for a in D for b in D]
T2POOL = H12 + [h + ":" + a + b for h in H12 for a in D for b in D]
assert len(T2POOL) == 11110
def late(r):                                                    # ((h, m): >= (9, 30)): absent part -> UNKNOWN
    if r.get("h") is None or r.get("m") is None: return None
    return (int(r["h"]), int(r["m"])) >= (9, 30)
def setcomp_late(r):                                            # ((h, m): !R): complement of R over every tuple of texts
    if r.get("h") is None or r.get("m") is None: return None
    return not ((int(r["h"]), int(r["m"])) >= (9, 30))

LINES = {}
def emit(key, text): LINES[key] = text
def count(pool, pred):
    hits = [s for s in order(pool) if pred(s)]
    return len(hits), (min(hits, key=lambda x: (len(x), x)) if hits else None)
MODES = order(["WHOLE", "SEARCHED"])

# ---- PART 1: the definition block's examples, both modes ----
q = Prog(T2, [late])
EX = [
    ("D1 t2 & !q (q := t2 & late)", Prog(T2, [], [q]), ["9:30", "9:15", "9:30 1"]),
    ("D2 /\\d+/ & !/0+/ (11-15 20:43 tie)", Prog(r"\d+", [], [Prog(r"0+")]), ["0 7", "0"]),
    ("D3 t2 & NOT late", Prog(T2, [NOT(late)]), ["9:30", "9:15", "9"]),
    ("D4 t2 & ((h, m): !R) (R = >= (9, 30))", Prog(T2, [setcomp_late]), ["9:30", "9:15", "9"]),
    ("D5 t2 & !contains(q)", Prog(T2, [], [], [lambda s, i, j: not any(accept(q, s, k, l)
        for k in range(i, j + 1) for l in range(k + 1, j + 1))]), ["9:30", "9:15", "9:30 1"]),
    ("D6 t2 & nowhere(q) [proposed whole-text test]", Prog(T2, [], [], [], [lambda s: not any(accept(q, s, k, l)
        for k in range(len(s) + 1) for l in range(k + 1, len(s) + 1))]), ["9:30", "9:15", "9:30 1"]),
    ("D7 (a, b) record (a = 0: <10, b: >$a) [$a reads the real label]",
        Prog(r"(?:(?P<a>\d)?/)(?P<b>\d)", [test("a", lt(10), "0"),
             lambda r: None if (r.get("a") is None or r.get("b") is None) else int(r["b"]) > int(r["a"])]), ["/5", "x/5", "2/5"]),
    ("D8 the joint ((a = 0, b): a < 10 & b > a)",
        Prog(r"(?:(?P<a>\d)?/)(?P<b>\d)", [lambda r: None if r.get("b") is None else
             (int(r["a"] or "0") < 10 and int(r["b"]) > int(r["a"] or "0"))]), ["/5", "x/5", "2/5"]),
    ("D9 two defaults on one label (h = 0: <5) & (h = 9: >7)", Prog(SV, [test("h", lt(5), "0"), test("h", lambda v: numeral(v) and int(v) > 7, "9")]), ["x", "3x", "a x"]),
]
for name, P, subs in EX:
    for s in subs:
        emit((1, name, s), "  %s on `%s`: WHOLE %s | SEARCHED %s" % (name, s, rep("WHOLE", P, s), rep("SEARCHED", P, s)))

# ---- PART 2: the three spellings, single-valued and repeated label, both modes ----
SPELL_SV = [
    ("NOT c          ", Prog(SV, [NOT(test("h", lt(5)))])),
    ("(h: !S)        ", Prog(SV, [test("h", notset(lt(5)))])),
    ("P & !(P & c)   ", Prog(SV, [], [Prog(SV, [test("h", lt(5))])])),
    ("NOT (h = 0: c) ", Prog(SV, [NOT(test("h", lt(5), "0"))])),
    ("NOT (h = 9: c) ", Prog(SV, [NOT(test("h", lt(5), "9"))])),
    ("(h = \"x\": !S)  ", Prog(SV, [test("h", notset(lt(5)), "x")])),
    ("(h = \"x\": >=5) ", Prog(SV, [test("h", ge(5), "x")])),
]
SPELL_REP = [
    ("plain c (every pass, >=1 row)        ", Prog(REP, [rtest(lt(5))], passre=REPPASS, rep="h")),
    ("NOT c (not every pass)               ", Prog(REP, [NOT(rtest(lt(5)))], passre=REPPASS, rep="h")),
    ("(h: !S) (every pass in !S)           ", Prog(REP, [rtest(notset(lt(5)))], passre=REPPASS, rep="h")),
    ("P & !(P & c)                         ", Prog(REP, [], [Prog(REP, [rtest(lt(5))], passre=REPPASS, rep="h")], passre=REPPASS, rep="h")),
    ("(h = 0: c) every pass, possibly none ", Prog(REP, [rtest(lt(5), "0")], passre=REPPASS, rep="h")),
    ("occurs.none((h = \"x\": !S)) narrower  ", Prog(REP, [none_(notset(lt(5)), "x")], passre=REPPASS, rep="h")),
    ("NOT some(c)                          ", Prog(REP, [NOT(some(lt(5)))], passre=REPPASS, rep="h")),
    ("occurs.none(c)                       ", Prog(REP, [none_(lt(5))], passre=REPPASS, rep="h")),
]
for mode in MODES:
    for pool_name, pool, sp in order([("SV (341)", SVPOOL, SPELL_SV), ("REP (364)", REPPOOL, SPELL_REP)]):
        for name, P in sp:
            c, w = count(pool, lambda s: holds(mode, P, s))
            emit((2, pool_name, mode, name), "  %s %s %s holds %d first %r" % (mode, pool_name, name, c, w))
# pairwise "where they part" among the three spellings, both pools, both modes
for mode in MODES:
    for pool_name, pool, sp, idx in order([("SV (341)", SVPOOL, SPELL_SV, (0, 1, 2)), ("REP (364)", REPPOOL, SPELL_REP, (1, 2, 3))]):
        for a_, b_ in order([(idx[0], idx[1]), (idx[0], idx[2]), (idx[1], idx[2])]):
            (na, Pa), (nb, Pb) = sp[a_], sp[b_]
            c, w = count(pool, lambda s: holds(mode, Pa, s) != holds(mode, Pb, s))
            emit((3, pool_name, mode, a_, b_), "  %s %s [%s] vs [%s] differ %d first %r" % (mode, pool_name, na.strip(), nb.strip(), c, w))
# per-subject answers on the small WHOLE-value rows (the worked table)
for pool_name, sp, subs in order([("SV", SPELL_SV, ["x", "3x", "7x"]), ("REP", SPELL_REP, ["", ";", "3;", "7;", "3;;", "7;;", "3;7;", "3;3;"])]):
    for s in order(subs):
        cells = []
        for name, P in sp:
            cells.append("%s=%s/%s" % (name.strip(), "H" if holds("WHOLE", P, s) else "F", "H" if holds("SEARCHED", P, s) else "F"))
        emit((4, pool_name, s), "  ROW %s `%s` (WHOLE/SEARCHED): %s" % (pool_name, s, " ; ".join(cells)))

# ---- PART 3: T2 counts, both modes ----
SP_T2 = [
    ("t2 & !q (pattern difference)", Prog(T2, [], [q])),
    ("t2 & NOT late (condition NOT)", Prog(T2, [NOT(late)])),
    ("t2 & ((h, m): !R) (set complement)", Prog(T2, [setcomp_late])),
    ("t2 & !contains(q)", EX[4][1]),
    ("t2 & nowhere(q) [proposed]", EX[5][1]),
]
for mode in MODES:
    for name, P in order(SP_T2):
        c, w = count(T2POOL, lambda s: holds(mode, P, s))
        emit((5, mode, name), "  %s T2 (11,110) %s holds %d first %r" % (mode, name, c, w))
    c, w = count(T2POOL, lambda s: holds(mode, SP_T2[0][1], s) and not holds(mode, SP_T2[4][1], s))
    emit((6, mode), "  %s T2 (11,110) t2 & !q holds while the text has a late time somewhere: %d first %r" % (mode, c, w))

# L95 rewritten with a default: t2 & ((h, m = 0): !R) vs t2 & !q
def setcomp_late_m0(r):
    if r.get("h") is None: return None
    return not ((int(r["h"]), int(r["m"] if r.get("m") is not None else "0")) >= (9, 30))
L95 = Prog(T2, [setcomp_late_m0])
for mode in MODES:
    c, w = count(T2POOL, lambda s: holds(mode, L95, s))
    d, dw = count(T2POOL, lambda s: holds(mode, L95, s) != holds(mode, SP_T2[0][1], s))
    emit((7, mode), "  %s T2 (11,110) t2 & ((h, m = 0): !R) holds %d first %r; vs t2 & !q differ %d first %r" % (mode, c, w, d, dw))

# ---- PART 4: rev 22's closing example, rewritten without the mark and `all`, both modes ----
CL = r"(?:(?P<h>\d+)(?::(?P<m>\d\d))?,)*"
CLPASS = r"(?P<h>\d+)(?::(?P<m>\d\d))?,"
ITEMS = [h + (":" + m if m else "") + "," for h in ["3", "12"] for m in [None, "15", "45", "05", "99"]]
SUBO = [""] + ITEMS + [a + b for a in ITEMS for b in ITEMS] + [a + b + c for a in ITEMS for b in ITEMS for c in ITEMS]
assert len(SUBO) == 1111
def cl_row(P, s, i, j):
    m = P.A.fullmatch(s[i:j])
    if m is None: return None
    ps = [(pm.group("h"), pm.group("m")) for pm in re.finditer(CLPASS, s[i:j])]
    return {"_real": ps, "_passes": ps if ps else [(None, None)]}
class CLProg(Prog):
    pass
def inR(h, m): return int(h) < 10 and int(m) < 30
def jt(h, m, dh, dm, S):                       # ((h = dh, m = dm): S) on one pass: absent part (no default) -> UNKNOWN
    h = h if h is not None else dh; m = m if m is not None else dm
    if h is None or m is None: return None
    return bool(S(h, m))
notR = lambda h, m: not inR(h, m)
CLC = [
    ("((h, m): R) plain", lambda r: k_and([jt(h, m, None, None, inR) for h, m in r["_passes"]])),
    ("occurs.none(((h, m): !R))", lambda r: not any(jt(h, m, None, None, notR) is True for h, m in r["_real"])),
    ("occurs.none(((h, m = 99): !R))", lambda r: not any(jt(h, m, None, "99", notR) is True for h, m in r["_real"])),
    ("occurs.none(((h, m = 00): !R))", lambda r: not any(jt(h, m, None, "00", notR) is True for h, m in r["_real"])),
    ("occurs.none(NOT ((h, m): R)) [legal again]", lambda r: not any(k_not(jt(h, m, None, None, inR)) is True for h, m in r["_real"])),
    ("((h = 0, m = 00): R) every pass, possibly none", lambda r: k_and([jt(h, m, "0", "00", inR) for h, m in r["_passes"]])),
    ("((h, m = 00): R) (h without a default)", lambda r: k_and([jt(h, m, None, "00", inR) for h, m in r["_passes"]])),
]
INTENT = [("I1", lambda ps: all(m is not None and inR(h, m) for h, m in ps)),
          ("I2a", lambda ps: all(m is None or inR(h, m) for h, m in ps)),
          ("I2b", lambda ps: all((int(h) < 10) if m is None else inR(h, m) for h, m in ps))]
for name, c in order(CLC):
    P = Prog(CL, [c])
    P_row = lambda P_, s, i, j: cl_row(P_, s, i, j)
    def acc(s, i, j, c=c):
        r = cl_row(P, s, i, j)
        return r is not None and c(r) is True
    def first_searched(s):
        for i in range(len(s) + 1):
            m = P.A.match(s, i)
            ends = ([m.end()] if m else []) + [j for j in range(len(s), i - 1, -1) if not (m and j == m.end()) and P.A.fullmatch(s[i:j])]
            for j in ends:
                if acc(s, i, j): return (i, j)
        return None
    wh = {s: acc(s, 0, len(s)) for s in SUBO}
    se = {s: first_searched(s) is not None for s in SUBO}
    parts = []
    for iname, f in INTENT:
        d = [s for s in SUBO if wh[s] != f([(pm.group("h"), pm.group("m")) for pm in re.finditer(CLPASS, s)])]
        parts.append("%s differ %d%s" % (iname, len(d), "" if not d else " first %r" % min(d, key=lambda x: (len(x), x))))
    emit((8, name), "  CLOSING (1,111 lists) %-48s WHOLE holds %d (%s) | SEARCHED holds %d" % (name, sum(wh.values()), "; ".join(parts), sum(se.values())))

# ---- PART 5: zero iterations of /(?:(?<n>\d),)*/ on the empty subject, both modes ----
ZP = "(?:(?P<n>\\d),)*"
ZC = [("(n: <5)", Prog(ZP, [rtest(lt(5))], passre="(?P<n>\\d),", rep="n")),
      ("(n = 0: <5)", Prog(ZP, [rtest(lt(5), "0")], passre="(?P<n>\\d),", rep="n")),
      ("some((n: <5))", Prog(ZP, [some(lt(5))], passre="(?P<n>\\d),", rep="n")),
      ("NOT some((n: <5))", Prog(ZP, [NOT(some(lt(5)))], passre="(?P<n>\\d),", rep="n")),
      ("NOT (n: <5)", Prog(ZP, [NOT(rtest(lt(5)))], passre="(?P<n>\\d),", rep="n"))]
for name, P in order(ZC):
    for s in order(["", "3,", "7,", "3,7,"]):
        emit((9, name, s), "  ZERO-PASS %s on `%s`: WHOLE %s | SEARCHED %s" % (name, s, rep("WHOLE", P, s), rep("SEARCHED", P, s)))

for k in sorted(LINES, key=lambda k: tuple(str(x) for x in k)): print(LINES[k])
print("END")
