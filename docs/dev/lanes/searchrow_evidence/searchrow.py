#!/usr/bin/env python3
# Lane searchrow (2026-11-16): the SEARCHED result row and the complement, candidate by candidate.
# An EXPLORATION's evidence (docs/design/condition_kind.md Part IV); rules nothing.
#
# Python `re` stands in for PCRE (no anchors or lookarounds in the regexes used; every regex is greedy, so the
# left operand's PREFERENCE ORDER of ends at a start is: re.match's end first, then the other whole-match ends,
# longest first; exact for t2, /\d+/, the L34 pair; stated in Part IV).
#
# Commands (W = the worktree):
#   timeout 300 python3 -I W/docs/dev/lanes/searchrow_evidence/searchrow.py > fwd.out
#   SEARCHROW_SWAP=1 timeout 300 python3 -I W/docs/dev/lanes/searchrow_evidence/searchrow.py > swap.out
#   diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)        # must print nothing
#   SEARCHROW_SABOTAGE=1 (forward and swapped): the diff must print something (the swap check can fail)
# SWAP reverses every order the script has: pools, candidates, a program's condition and complement lists.
# SABOTAGE makes candidate M+'s complement remember the last subject's answer for the NEXT subject in iteration
# order (state leaking between rows), so its counts depend on order and the swap run differs.
import os, re

SWAP = os.environ.get("SEARCHROW_SWAP") == "1"
SAB = os.environ.get("SEARCHROW_SABOTAGE") == "1"
print("ORDER: %s%s" % ("SWAPPED" if SWAP else "forward", " SABOTAGE" if SAB else ""))
def order(xs): return list(reversed(xs)) if SWAP else list(xs)

class Prog:
    """A statement: left operand A (an rx), positive conditions (three-valued tests of one row), complements."""
    def __init__(self, A, conds=(), comps=(), name=""):
        self.A = re.compile(A); self.conds = order(conds); self.comps = order(comps); self.name = name

def row_at(P, s, i, j):
    m = P.A.fullmatch(s[i:j])                 # the stretch's own parse (rev 22 §4.5: each span its own parse)
    return None if m is None else m.groupdict()

def ends_pref(P, s, i):
    """Ends at start i in the left operand's preference order (D196): the preferred end, then the others."""
    m = P.A.match(s, i)
    first = [m.end()] if m and row_at(P, s, i, m.end()) is not None else []
    rest = [j for j in range(len(s), i - 1, -1) if j not in first and row_at(P, s, i, j) is not None]
    return first + rest

def conds_ok(P, r): return all(c(r) is True for c in P.conds)

def whole(P, s, i, j):
    """Whole-value: P matches the stretch s[i:j] whole (every candidate agrees here: the row IS the stretch)."""
    r = row_at(P, s, i, j)
    return r is not None and conds_ok(P, r) and not any(whole(B, s, i, j) for B in P.comps)

def findall(s, accept):
    """Non-overlapping, leftmost: at each start the first end (preference order) `accept` admits."""
    out, i = [], 0
    while i <= len(s):
        hit = None
        for j in accept.ends(s, i):
            if accept(s, i, j): hit = j; break
        if hit is None or hit == i:       # no row here (empty rows are not reported: every pool regex is non-nullable)
            i += 1; continue
        out.append((i, hit)); i = hit
    return out

class Acc:
    def __init__(self, P, f): self.P, self.f = P, f
    def ends(self, s, i): return ends_pref(self.P, s, i)
    def __call__(self, s, i, j): return self.f(s, i, j)

# ---- the candidates: rows(P, s) = the searched result rows (spans) of statement P on subject s ----
def rows_R22(P, s):    # rev 22: D196, every filter (a complement too, as a stretch filter) may send it to the next end
    return findall(s, Acc(P, lambda s, i, j: whole(P, s, i, j)))
def rows_X(P, s):      # Part I's S2: every span is a row; a row of P = every span P matches whole
    return [(i, j) for i in range(len(s) + 1) for j in range(i + 1, len(s) + 1) if whole(P, s, i, j)]
def pos_rows(P, s):    # D196 with the POSITIVE conditions only (retry on them)
    return findall(s, Acc(P, lambda s, i, j: conds_ok(P, row_at(P, s, i, j))))
def rows_S(P, s):      # source-row as worded: a complement per SUBJECT
    if any(rows_S(B, s) for B in P.comps): return []
    return pos_rows(P, s)
def rows_M(P, s):      # the manager's M as worded: PCRE's reported matches of A; conditions and complements keep/drop them
    plain = findall(s, Acc(P, lambda s, i, j: True))
    return [(i, j) for (i, j) in plain
            if conds_ok(P, row_at(P, s, i, j)) and not any(whole(B, s, i, j) for B in P.comps)]
_leak = {"v": False}
def rows_Mp(P, s):     # M+ (lane's): D196 with retry on POSITIVE conditions; a complement removes finished rows
    out = []
    for (i, j) in pos_rows(P, s):
        hit = any(whole(B, s, i, j) for B in P.comps)
        if SAB and P.comps:
            hit, _leak["v"] = _leak["v"] or hit, hit
        if not hit: out.append((i, j))
    return out
def rows_Mr(P, s):     # M+ with SQL EXCEPT on rows: remove a row only if it IS a row of B (same span), B searched
    bad = set()
    for B in P.comps: bad |= set(rows_Mr(B, s))
    return [r for r in pos_rows(P, s) if r not in bad]

CANDS = order([("R22", rows_R22), ("X", rows_X), ("S", rows_S), ("M", rows_M), ("M+", rows_Mp), ("Mr", rows_Mr)])
CN = [n for n, _ in CANDS]

# ---- regexes, conditions, pools ----
T2 = r"(?P<h>\d{1,2})(?::(?P<m>\d\d))?"
def late(r):
    if r["h"] is None or r["m"] is None: return None
    return (int(r["h"]), int(r["m"])) >= (9, 30)
def m_lt45(r): return None if r["m"] is None else int(r["m"]) < 45
def h_gt20(r): return None if r["h"] is None else int(r["h"]) > 20
def m0_lt20(r): return int(r["m"] if r["m"] is not None else "0") < 20      # (m = 0: <20), per-test default
def late_m0(r):                                                                # ((h, m = 0): padded(>= (9, 30)))
    if r["h"] is None: return None
    return (int(r["h"]), int(r["m"] if r["m"] is not None else "0")) >= (9, 30)
D = "0123456789"
H12 = list(D) + [a + b for a in D for b in D]
T2POOL = H12 + [h + ":" + a + b for h in H12 for a in D for b in D]
assert len(T2POOL) == 11110
TOK = [h + mm for h in ["1", "9", "10", "21"] for mm in ["", ":00", ":15", ":30", ":45", ":50"]]
T2PAIRS = TOK + [a + " " + b for a in TOK for b in TOK]
assert len(T2PAIRS) == 600
def strings(alpha, n):
    out, cur = [], [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
DIG = [s for s in strings("017 ", 5) if s.strip() == s and "  " not in s]   # digit runs over 0,1,7 with single spaces

def holds(f, P, s): return bool(f(P, s))
def W_pos(c, p):       # `when(c, p)` read per row: c TRUE -> p TRUE; c not TRUE -> TRUE
    return lambda r: (c(r) is True and p(r) is True) or c(r) is not True

def count(pool, pred):
    hits = [s for s in pool if pred(s)]
    return len(hits), (min(hits, key=lambda x: (len(x), x)) if hits else None)

def report(f, P, s):
    rs = f(P, s)
    return ("HOLDS " + ",".join("`%s`@%d" % (s[i:j], i) for i, j in rs)) if rs else "FAILS"

CANON = ["R22", "X", "S", "M", "M+", "Mr"]
POOLC = ["T2 (11,110)", "T2PAIRS (600)"]
LINES = {}
def emit(site, pool, cand, text):
    """Lines print in ONE canonical order whatever order they were computed in (the swap run must match)."""
    k = (site, POOLC.index(pool) if pool in POOLC else -1, CANON.index(cand) if cand in CANON else -1)
    LINES[k + (text.split("`: ")[0] if site == 2 else "",)] = text
def canon_join(d): return " | ".join("%s %s" % (n, d[n]) for n in CANON)

# ---- PART 1: the examples, under every candidate ----
emit(1, locals().get("poolname"), locals().get("n"), "PART 1: examples (program; subject; mode SEARCHED; each candidate's rows)")
q = Prog(T2, [late], name="q := t2 & late")
EX = [
    ("t2 & !q   [source-row's one example]", Prog(T2, [], [q]), ["9:30", "9:15", "9:30 1", "10:00 9:15"]),
    ("/\\d+/ & !/0+/   [review r31 A1]", Prog(r"\d+", [], [Prog(r"0+")]), ["0 7", "00 70", "10", "0"]),
    ("/\\d+/ & !/\\d\\d/", Prog(r"\d+", [], [Prog(r"\d\d")]), ["12", "123"]),
    ("/\\d+/ & !/0|00/   [Mr vs M+]", Prog(r"\d+", [], [Prog(r"0|00")]), ["00", "0 00"]),
    ("L34 /(?<a>\\d+)(?<b>\\d+)/ & (a: <5) & (b: <5)", Prog(r"(?P<a>\d+)(?P<b>\d+)",
        [lambda r: int(r["a"]) < 5, lambda r: int(r["b"]) < 5]), ["123"]),
    ("L59 /(?<a>\\d+)(?<b>\\d+)/ & (a: \"1\")", Prog(r"(?P<a>\d+)(?P<b>\d+)", [lambda r: r["a"] == "1"]), ["123"]),
    ("§11 (i) /\\d+/ & <256", Prog(r"(?P<n>\d+)", [lambda r: int(r["n"]) < 256]), ["x300 12"]),
    ("§4.2 t2 & ((h, m = 0): padded(>= (9, 30)))", Prog(T2, [late_m0]), ["9:15"]),
    ("t2 & (m = 0: <20) & !/\\d:\\d\\d/   [M+ admits by retry]", Prog(T2, [m0_lt20], [Prog(r"\d:\d\d")]), ["9:30"]),
    ("t2 & !/\\d:\\d\\d/   [the same without the condition]", Prog(T2, [], [Prog(r"\d:\d\d")]), ["9:30"]),
]
for name, P, subs in EX:
    for s in subs:
        emit(2, locals().get("poolname"), locals().get("n"), "  %s on `%s`: %s" % (name, s, canon_join({n: report(f, P, s) for n, f in CANDS})))
# L13: the filter reads its stretch (slice), so `^` is the stretch's start
pad5 = re.compile(r"0*(?:^5)")
def L13rows(f):
    P = Prog(r"(?P<n>\d+)", [lambda r: pad5.fullmatch(r["n"]) is not None])
    return report(f, P, "x005")
emit(3, locals().get("poolname"), locals().get("n"), "  L13 /\\d+/ & padded(/^5/) on `x005`: " + canon_join({n: L13rows(f) for n, f in CANDS}))

# ---- PART 2: populations ----
emit(4, locals().get("poolname"), locals().get("n"), "PART 2: counts (mode named on each line; smallest witness by length then text)")
tq = Prog(T2, [], [q])
for poolname, pool in order([("T2 (11,110)", T2POOL), ("T2PAIRS (600)", T2PAIRS)]):
    for n, f in CANDS:
        c, w = count(pool, lambda s: holds(f, tq, s))
        emit(5, locals().get("poolname"), locals().get("n"), "  SEARCHED %s t2 & !q holds: %s %d first %s" % (poolname, n, c, w))
    cw, ww = count(pool, lambda s: whole(tq, s, 0, len(s)))
    emit(6, locals().get("poolname"), locals().get("n"), "  WHOLE %s t2 & !q holds: %d" % (poolname, cw))
    S = dict(CANDS)["S"]
    for n, f in CANDS:
        if n == "S": continue
        c, w = count(pool, lambda s: holds(f, tq, s) != holds(S, tq, s))
        emit(7, locals().get("poolname"), locals().get("n"), "  SEARCHED %s t2 & !q, %s vs S differ: %d first %s" % (poolname, n, c, w))

# the label-free pair
lf = Prog(r"\d+", [], [Prog(r"0+")])
emit(8, locals().get("poolname"), locals().get("n"), "  DIG pool size %d" % len(DIG))
for n, f in CANDS:
    c, w = count(DIG, lambda s: holds(f, lf, s))
    d, dw = count(DIG, lambda s: holds(f, lf, s) != holds(rows_R22, lf, s))
    emit(9, locals().get("poolname"), locals().get("n"), "  SEARCHED DIG /\\d+/ & !/0+/ holds: %s %d; differs from R22 on %d first %s" % (n, c, d, dw))

# `when`: body (x & c & p) | (x & !(x & c)) vs the per-row case-when x & W(c, p)
x = Prog(T2); xcp = Prog(T2, [late, m_lt45]); xnxc = Prog(T2, [], [Prog(T2, [late])]); xw = Prog(T2, [W_pos(late, m_lt45)])
for poolname, pool in order([("T2 (11,110)", T2POOL), ("T2PAIRS (600)", T2PAIRS)]):
    for n, f in CANDS:
        b, _ = count(pool, lambda s: holds(f, xcp, s) or holds(f, xnxc, s))
        c, _ = count(pool, lambda s: holds(f, xw, s))
        d, dw = count(pool, lambda s: (holds(f, xcp, s) or holds(f, xnxc, s)) != holds(f, xw, s))
        emit(10, locals().get("poolname"), locals().get("n"), "  SEARCHED %s when: %s body %d case-when %d differ %d first %s" % (poolname, n, b, c, d, dw))
    b, _ = count(pool, lambda s: whole(xcp, s, 0, len(s)) or whole(xnxc, s, 0, len(s)))
    c, _ = count(pool, lambda s: whole(xw, s, 0, len(s)))
    emit(11, locals().get("poolname"), locals().get("n"), "  WHOLE %s when: body %d case-when %d" % (poolname, b, c))
# M+'s body vs the case-when read per REPORTED match (no retry: M's filter rule), as sets
for poolname, pool in order([("T2 (11,110)", T2POOL), ("T2PAIRS (600)", T2PAIRS)]):
    d, dw = count(pool, lambda s: (holds(rows_Mp, xcp, s) or holds(rows_Mp, xnxc, s)) != holds(rows_M, xw, s))
    emit(18, poolname, None, "  SEARCHED %s when: M+ body vs case-when per reported match (M's rule) differ %d first %s" % (poolname, d, dw))
# `when` with a shorter end that passes: x = /(?<d>\d+)/, c = (d: <50), p = (d: <5)
xd = Prog(r"(?P<d>\d+)"); cd = lambda r: int(r["d"]) < 50; pd = lambda r: int(r["d"]) < 5
DIGP = [s for s in DIG if " " not in s]
for n, f in CANDS:
    body = lambda s: holds(f, Prog(r"(?P<d>\d+)", [cd, pd]), s) or holds(f, Prog(r"(?P<d>\d+)", [], [Prog(r"(?P<d>\d+)", [cd])]), s)
    d, dw = count(DIGP, lambda s: body(s) != holds(f, Prog(r"(?P<d>\d+)", [W_pos(cd, pd)]), s))
    emit(12, locals().get("poolname"), locals().get("n"), "  SEARCHED DIG-runs (%d) when, x=/(?<d>\\d+)/ c=(d: <50) p=(d: <5): %s body vs case-when differ %d first %s" % (len(DIGP), n, d, dw))

# adding a condition never admits: q & !(q & c), add (h: >20) to q (both uses)
before = Prog(T2, [], [Prog(T2, [late])]); after = Prog(T2, [h_gt20], [Prog(T2, [h_gt20, late])])
for poolname, pool in order([("T2 (11,110)", T2POOL), ("T2PAIRS (600)", T2PAIRS)]):
    for n, f in CANDS:
        c, w = count(pool, lambda s: holds(f, after, s) and not holds(f, before, s))
        emit(13, locals().get("poolname"), locals().get("n"), "  SEARCHED %s add (h: >20) to q in q & !(q & late): %s admitted %d first %s" % (poolname, n, c, w))
    c, w = count(pool, lambda s: whole(after, s, 0, len(s)) and not whole(before, s, 0, len(s)))
    emit(14, locals().get("poolname"), locals().get("n"), "  WHOLE %s add (h: >20): admitted %d" % (poolname, c))
# adding a condition at the TOP of a chain: t2 & !/\d:\d\d/  ->  t2 & (m = 0: <20) & !/\d:\d\d/
b2 = Prog(T2, [], [Prog(r"\d:\d\d")]); a2 = Prog(T2, [m0_lt20], [Prog(r"\d:\d\d")])
for poolname, pool in order([("T2 (11,110)", T2POOL), ("T2PAIRS (600)", T2PAIRS)]):
    for n, f in CANDS:
        c, w = count(pool, lambda s: holds(f, a2, s) and not holds(f, b2, s))
        emit(15, locals().get("poolname"), locals().get("n"), "  SEARCHED %s add (m = 0: <20) to t2 & !/\\d:\\d\\d/: %s admitted %d first %s" % (poolname, n, c, w))
# the two spellings of one set: /\d+/ & !/\d\d/ vs the positive filter "not two digits" (D196 retry)
neg = Prog(r"\d+", [], [Prog(r"\d\d")])
posf = Prog(r"(?P<n>\d+)", [lambda r: re.fullmatch(r"\d\d", r["n"]) is None])
for n, f in CANDS:
    c, w = count(DIG, lambda s: holds(f, neg, s) != holds(f, posf, s))
    emit(16, locals().get("poolname"), locals().get("n"), "  SEARCHED DIG /\\d+/ & !/\\d\\d/ vs /\\d+/ & (a positive filter: not /\\d\\d/): %s differ %d first %s" % (n, c, w))
# M (no retry) vs D196 on a positive-only program: /\d+/ & <17 over DIG
lt = Prog(r"(?P<n>\d+)", [lambda r: int(r["n"]) < 17])
for n, f in CANDS:
    c, w = count(DIG, lambda s: holds(f, lt, s) != holds(rows_R22, lt, s))
    emit(17, locals().get("poolname"), locals().get("n"), "  SEARCHED DIG /\\d+/ & <17 (no complement): %s differs from R22 (D196) on %d first %s" % (n, c, w))
for k in sorted(LINES): print(LINES[k])
print("END")
