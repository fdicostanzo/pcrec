#!/usr/bin/env python3
# Lane predspec241 (2026-11-17): the evidence engine of docs/design/predicates_draft.md REVISION 24.1 (review r40's
# fixes, docs/dev/reviews/2026-11-17-r40-predspec24.md). DESIGN EVIDENCE ONLY; rules nothing. A copy of lane
# predspec24's engine (../predspec24_evidence/predspec24_model.py, never edited) with FIVE engine fixes, each where
# the engine disagreed with the draft's text AND with PCRE2 (r40 A1, A2, A3, A5, C1):
#   FIX-A1 a condition in a loop body (a hole-loop item) or an `occurrences` argument reads the labels set SO FAR,
#          an optional label keeping the value an EARLIER pass set (PCRE's capture state; R.1, R.1.7). The engine read
#          only the pass's own values (a per-pass label scope no sentence states).
#   FIX-A2 a loop (`Rep`, `Occ`) exports EVERY label its item sets, the last setting overall, a label looped at two
#          depths and a label set inside an atomic part included (PCRE's capture after the match). The engine
#          exported only the item's set-once labels.
#   FIX-A3 `A & B` and `A & !B` run B WHOLE ON THE STRETCH's own text (R.1.4; §11's scoped match: B's `$`, `\b` and
#          lookarounds read the stretch). The engine ran B in the subject with a tied end.
#   FIX-A5 every comparison printed "(labels compared)" carries the labels in EVERY mode, WHOLE included (the WHOLE
#          key compared holding only).
#   FIX-C1 the order-swap switch (which reversed nothing that carries meaning) is REMOVED; in its place PART C's ORDER
#          CHECK runs each `&` model with its operands swapped and requires the swapped engine to DIFFER from PCRE2
#          (a check that can fail), and the sabotage now also swaps `&`'s operands and drops the carry.
# PART C's models of `&` and `!B` no longer share the engine's construction (r40 A3: the tied-end lookahead let `$`
# see the subject): the operand runs as its OWN libpcre2 pattern, WHOLE on the stretch a callout extracts.
#
# THE RULES OF REV 24 (the owner's rulings of 2026-11-17, COND-FAMILY; the manager's readings marked READING):
#   branch-scope (ii)  a condition is one more piece of the pattern: a path survives when every condition on it holds;
#                      the pattern tries its paths in PCRE's order (`|` included); the report is the first survivor.
#   regex-settles      (1) a test on an absent label fails; (2) `!B` keeps a path when NO path of B survives over the
#                      same stretch; (3) a lookahead is never re-entered from outside; (4) occurrences is the owner's
#                      one-pattern lazy-gap loop over the span (a condition re-enters it); (5) atomic = PCRE's atomic group.
#   absent-under-not   two-valued: NOT around a test of an absent label holds.
#   when-meaning       when(c, p) := x & (NOT c | p), one `|`.
#   last-pass-default  a bare label set in a loop reads the last pass that set it (PCRE's capture after the match).
#   THE DRAFT'S READINGS, asked (r40; draft §R.8): join-order = left side's paths outer; hits-committed = a named
#                      all-hits request reads the global search's committed hit list over the stretch (hits-text).
# THE ENGINE is lane lastpass's (lastpass_model.py, loaded in memory up to its PART A, never edited; it loads lane
# pathimpact's path enumerator and lane rxmodel's libpcre2 harness, never edited), run in its mode R (two-valued,
# last pass), with this lane's own nodes for every place that holds a program: AndS / DiffS (the operand on the
# stretch), Rep (a hole loop) and OccS (occurrences) with the carry, Atom, Idx, OPE (rev 23.2's switch).
#
# SWITCHES (W = the worktree; run from $PCREC_TMPDIR/scratch/predspec241):
#   timeout 1800 python3 -I -B W/docs/dev/lanes/predspec241_evidence/predspec241_model.py > fwd.out
#   PREDSPEC241_SABOTAGE=1 ...  a bare looped label reads the FIRST pass, a loop item does NOT carry earlier passes'
#                               labels, and `&` runs its RIGHT operand's paths outer: PART C (models and the ORDER
#                               CHECK) must fail
#   PREDSPEC241_RULES=23.2 ...  THE SWITCH BACK: the NOW column is computed under rev 23.2's rules; MOVED must print 0
#                               and the PRINTED check must print 0 mismatches either way
import os, sys, io, re, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
LANES = os.path.dirname(HERE)
SWAP = False                                          # FIX-C1: the order-swap switch is removed (see the head)
SAB = os.environ.get("PREDSPEC241_SABOTAGE") == "1"
NOWR = os.environ.get("PREDSPEC241_RULES", "24")
if NOWR not in ("24", "23.2"): sys.exit("PREDSPEC241_RULES must be 24 or 23.2")
print("RUN: %s NOW=rev %s" % ("SABOTAGE" if SAB else "forward", NOWR))
def order(xs): return list(xs)
PASSOWN = {"v": False}                                # the pass-own-labels CANDIDATE (PART Q 10): a pass starts with its body's labels unset

# ------------------------------------------------------------------------------------------------ load lastpass
LPF = os.path.join(LANES, "lastpass_evidence", "lastpass_model.py")
LSRC = open(LPF).read()
for k in ("LASTPASS_DEFAULT", "LASTPASS_SABOTAGE", "PATHIMPACT_SWAP", "PATHIMPACT_SABOTAGE", "PATHIMPACT_READING", "PATHIMPACT_ENDS"):
    os.environ.pop(k, None)
LP = {"__file__": LPF, "__name__": "lastpass_defs"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(LSRC[:re.search(r"^# =+ PART A: libpcre2$", LSRC, re.M).start()], LPF, "exec"), LP)
E = LP["E"]                                           # pathimpact's namespace (the path enumerator reads SAB/SWAP there)
P = LP["P"]                                           # pcre2h
LP["SAB"] = SAB                                       # lastpass's Test: under SAB mode R reads the FIRST pass
E["SAB"], E["SWAP"] = SAB, SWAP                       # Rx.paths: SAB and SWAP together reverse PCRE's path order
Pat, Where, Diff, Alt, AndP, Keep, Occ = (LP[k] for k in ("Pat", "Where", "Diff", "Alt", "AndP", "Keep", "Occ"))
Test, Not_, And_, Or_, Count, Row = (LP[k] for k in ("Test", "Not", "And", "Or", "Count", "Row"))
set_once_labels, strings, lists, merge = LP["set_once_labels"], LP["strings"], LP["lists"], LP["merge"]
num, lt, ge, between, eq = LP["num"], LP["lt"], LP["ge"], LP["between"], LP["eq"]
_row_of = LP["row_of"]
def _row_of_po(r, s, i, e, caps, hist):
    """The pass-own-labels CANDIDATE (PART Q 11; off unless PASSOWN): after a loop a looped label reads the LAST PASS's
    own value (absent when that pass did not set it); the pass is the innermost enclosing loop's."""
    row = _row_of(r, s, i, e, caps, hist)
    if PASSOWN["v"]:
        for l, lp in row.loop.items():
            if lp is not None and row.passes.get(lp): row.last[l] = row.passes[lp][-1].get(l)
    return row
LP["row_of"] = _row_of_po

# ------------------------------------------------------------------------------------------------ the rules switch
RULES = {"v": "24"}
@contextlib.contextmanager
def rules(r):
    old = (RULES["v"], LP["MODE"]["v"], LP["OCCM"]["v"])
    RULES["v"] = r
    LP["MODE"]["v"] = "R" if r == "24" else "T3"
    LP["OCCM"]["v"] = "H2" if r == "24" else "H1"
    try: yield
    finally: RULES["v"], LP["MODE"]["v"], LP["OCCM"]["v"] = old

class OPE:
    """Rev 23.2's reading (iii): one row per stretch end, the first path ending there whose INNER conditions are
    TRUE (a `|` branch's own condition falls through, branch-major); conditions outside judge that one row."""
    def __init__(self, node): self.node = node
    def walk(self, s, i):
        seen = set()
        for e, row, ck in self.node.walk(s, i):
            if e in seen: continue
            if all(f() is True for f in ck):
                seen.add(e); yield e, row, ()
def ope(n): return OPE(n) if RULES["v"] == "23.2" else n

def labels_of(node):
    """FIX-A2: every label a program can set (PCRE's capture state after it: set-once, looped and atomic-inside alike)."""
    if isinstance(node, Pat): return set(node.rx.names)
    if isinstance(node, (Where, Keep, DiffS, Atom, FirstRow, Strip, OPE)): return labels_of(node.node)
    if isinstance(node, Diff): return labels_of(node.node)
    if isinstance(node, Alt): return set().union(*[labels_of(b) for b in node.bs])
    if isinstance(node, (AndS, AndP)): return labels_of(node.a) | labels_of(node.b)
    if isinstance(node, Rep): return labels_of(node.X)
    if isinstance(node, OccS): return labels_of(node.X) | {"hit"}
    if isinstance(node, Committed): return labels_of(node.o)
    return set()
def passrow(key, labs, stretch, ps):
    """A loop's row: `passes` = each pass's OWN values (the pass table); `last` = the last setting of each label over
    the passes (PCRE's capture after the loop; FIX-A2: every label the item sets)."""
    row = Row(); row.stretch = stretch; row.passes[key] = list(ps)
    for l in labs:
        row.loop[l] = key
        vals = [p[l] for p in ps if p.get(l) is not None]
        row.last[l] = vals[-1] if vals else None
        if PASSOWN["v"] and ps: row.last[l] = ps[-1].get(l)   # the pass-own-labels candidate (PART Q 11)
        row.first[l] = vals[0] if vals else None
    return row
def carry_pass(row, c, carry):
    """FIX-A1: a pass's conditions read the labels set SO FAR: a label this pass did not set reads the value an
    earlier pass set (PCRE's capture state at the callout). Returns the pass's own values, or None when a condition of
    the pass fails (the pass is not a path). Under the sabotage the carry is dropped."""
    own = {k: v for k, v in row.last.items() if v is not None}
    if not SAB and not PASSOWN["v"]:                     # PASSOWN: the pass-own-labels candidate (no carry)
        for k, v in carry.items():
            if row.last.get(k) is None: row.last[k] = v
    if not all(f() is True for f in c): return None
    return own
class Rep:
    """`/(?:${X}){lo,}/`: program X repeated, greedy, contiguous; each pass is one path of X with its own checks (a
    condition inside X is a piece of every pass: the regex model is a callout in the loop body), reading the labels
    set so far (FIX-A1). Every label X sets is a looped label of the loop; the bare label reads the last setting
    (FIX-A2)."""
    def __init__(self, X, lo=0): self.X, self.lo = X, lo; self.key = ("L", "rep", id(self)); self.labs = labels_of(X)
    def walk(self, s, i):
        def loop(pos, ps, carry):
            for e, row, c in self.X.walk(s, pos):
                if e == pos: continue                       # an empty pass ends the loop (PCRE)
                own = carry_pass(row, c, carry)
                if own is None: continue
                nc = dict(carry); nc.update(own)
                yield from loop(e, ps + (own,), nc)
            if len(ps) >= self.lo: yield pos, passrow(self.key, self.labs, (i, pos), ps), ()
        yield from loop(i, (), {})
class OccS:
    r"""`occurrences(X, min = n)`: the owner's ONE-PATTERN model `(?:[\s\S]*?(X)){n,}[\s\S]*` over the span
    (regex-settles (4)), lane lastpass's Occ with FIX-A1 (a hit's conditions read the labels set so far, earlier hits
    included) and FIX-A2 (every label X sets is exported, the last setting). OCCM = H1: the hits are the global
    find-all of X inside the stretch, committed (the named all-hits request; each hit a fresh match, no carry);
    `subject=True` (the hits-text candidate): the subject's own global find-all, the hits lying inside the stretch."""
    def __init__(self, X, mn=0, subject=False):
        self.hit_ok = None
        self.X, self.mn, self.subject = X, mn, subject; self.key = ("L", "occ", id(self)); self.labs = labels_of(X) | {"hit"}
    def own_hit(self, s, g, e, row):
        p = {k: v for k, v in row.last.items() if v is not None}; p["hit"] = s[g:e]; return p
    def walk(self, s, i):
        n = len(s)
        if LP["OCCM"]["v"] == "H1":
            full = [(a, b, r) for a, b, r in findall(self.X, s)] if self.subject else None
            for e in range(n, i - 1, -1):
                if self.subject: hits = [(a, b, r) for a, b, r in full if a >= i and b <= e]
                else: hits = [(i + a, i + b, r) for a, b, r in findall(self.X, s[i:e])]
                if len(hits) >= self.mn:
                    yield e, passrow(self.key, self.labs, (i, e), [self.own_hit(s, a, b, r) for a, b, r in hits]), ()
            return
        def loop(pos, hits, carry):
            for g in range(pos, n + 1):                     # lazy gap: the shortest first
                for e, row, c in self.X.walk(s, g):
                    own = carry_pass(row, c, carry)
                    if own is None: continue
                    if self.hit_ok is not None and not self.hit_ok(s, i, g, e): continue
                    own["hit"] = s[g:e]
                    h = hits + (own,)
                    if e == g:                              # an empty hit ends the loop
                        if len(h) >= self.mn: yield from tail(e, h)
                        continue
                    nc = dict(carry); nc.update({k: v for k, v in own.items() if k != "hit"})
                    yield from loop(e, h, nc)
            if len(hits) >= self.mn: yield from tail(pos, hits)
        def tail(pos, hits):
            for e in range(n, pos - 1, -1):                 # the greedy trailing gap
                yield e, passrow(self.key, self.labs, (i, e), hits), ()
        yield from loop(i, (), {})
class AndS:
    """FIX-A3: `A & B` on patterns: the paths of A whose stretch B matches WHOLE, B run on the stretch's own text
    (its anchors and lookarounds read the stretch); the row carries both sides' labels; A's paths are the outer loop
    (join-order, THE DRAFT'S READING). Under the sabotage B's paths are the outer loop."""
    def __init__(self, a, b): self.a, self.b = a, b
    def walk(self, s, i):
        if SAB:
            Bp = {}
            for e2, r2, c2 in self.b.walk(s, i):
                for e1, r1, c1 in self._whole(self.a, s, i, e2, Bp):
                    yield e2, merge(r1, r2), c2 + c1
            return
        cache = {}
        for e1, r1, c1 in self.a.walk(s, i):
            for e2, r2, c2 in self._whole(self.b, s, i, e1, cache):
                yield e1, merge(r1, r2), c1 + c2
    @staticmethod
    def _whole(X, s, i, e, cache):
        if e not in cache:
            sub = s[i:e]
            cache[e] = [(e, r, c) for e2, r, c in X.walk(sub, 0) if e2 == len(sub)]
        return cache[e]
class DiffS:
    """FIX-A3: `A & !B`: a path of A survives when NO path of B survives WHOLE on its stretch's own text."""
    def __init__(self, node, B): self.node, self.B = node, B
    def walk(self, s, i):
        for e, row, ck in self.node.walk(s, i):
            yield e, row, ck + ((lambda e=e: whole_row(self.B, s[i:e]) is None),)
class Atom:
    """PCRE's atomic group `(?>X)`: at a start, X's first SURVIVING path (its own conditions applied inside), then
    no backtracking into it."""
    def __init__(self, node): self.node = node
    def walk(self, s, i):
        for e, row, ck in self.node.walk(s, i):
            if all(f() is True for f in ck):
                yield e, row, (); return
class FirstRow:
    """The manager's restatement 'atomic = the first row BEFORE the filter': the first path at a start, whatever its
    conditions say; its conditions then judge it."""
    def __init__(self, node): self.node = node
    def walk(self, s, i):
        for x in self.node.walk(s, i):
            yield x; return
class Strip:
    """A candidate for lookahead-labels: the named labels are not visible outside (read as absent)."""
    def __init__(self, node, labs): self.node, self.labs = node, labs
    def walk(self, s, i):
        for e, row, ck in self.node.walk(s, i):
            r2 = Row(); r2.stretch = row.stretch
            r2.last = {k: (None if k in self.labs else v) for k, v in row.last.items()}
            r2.first, r2.loop, r2.passes = row.first, row.loop, row.passes
            yield e, r2, ck
class Committed:
    """The named all-hits request (hits-committed, the manager's reading): occurrences with the hits COMMITTED, the
    global search's leftmost, non-overlapping hits inside the stretch, one row per stretch (H1), under any rules."""
    def __init__(self, X, mn=0, subject=False): self.o = OccS(X, mn, subject)
    def walk(self, s, i):
        old = LP["OCCM"]["v"]; LP["OCCM"]["v"] = "H1"
        try: out = list(self.o.walk(s, i))
        finally: LP["OCCM"]["v"] = old
        yield from out

class Idx:
    """`(h[k]: S)`: the value pass k set (a literal index; the named request's pass table)."""
    def __init__(self, lab, k, pred): self.lab, self.k, self.pred, self.labs = lab, k, pred, (lab,)
    def ev(self, row, view=None):
        lp = row.loop.get(self.lab)
        ps = row.passes.get(lp, []) if lp is not None else []
        v = ps[self.k - 1].get(self.lab) if len(ps) >= self.k else None
        if v is None: return LP["two"](None)
        return bool(self.pred(v))

# ------------------------------------------------------------------------------------------------ constructors
def W(node, *cs): return Where(ope(node), *order(cs))
def D(node, B): return DiffS(ope(node), B)
def ALT(*bs): return Alt(*bs)
def AND(a, b): return AndS(ope(a), ope(b))
def C(labs, pred, **d): return Test(labs, pred, d)
def NOT(c): return Not_(c)
def ANDC(*cs): return And_(*order(cs))
def ORC(*cs): return Or_(*order(cs))
def SOME(c): return Count(c, lambda n: n >= 1)
def NONE(c): return Count(c, lambda n: n == 0)
def EXACTLY(k, c): return Count(c, lambda n, k=k: n == k)
def OCC(X, mn=0): return OccS(X, mn)
def WHEN(x, c, p):
    """rev 24: the library definition x & (NOT c | p); rev 23.2: the FILTER form (its §8 choice)."""
    if RULES["v"] == "24": return W(x, ORC(NOT(c), p))
    return Keep(x, lambda row, s, i, e: (c.ev(row) is True and p.ev(row) is True) or
                not any(e2 == e for e2, _ in LP["accepted"](W(x, c), s, i)))
def ZERO(A, B):
    """`A & (0: B)`: B matched WHOLE against the stretch's own text, alone (label 0 = the row's whole match)."""
    return Keep(ope(A), lambda row, s, i, e: whole_row(B, s[i:e]) is not None)

# ------------------------------------------------------------------------------------------------ answers (lazy)
def acc_iter(Pn, s, i):
    for e, row, ck in Pn.walk(s, i):
        if all(f() is True for f in ck): yield e, row
def whole_row(Pn, s):
    for e, row in acc_iter(Pn, s, 0):
        if e == len(s): return row
    return None
def search(Pn, s, pos=0):
    for i in range(pos, len(s) + 1):
        for e, row in acc_iter(Pn, s, i): return i, e, row
    return None
def findall(Pn, s):
    out, pos = [], 0
    while pos <= len(s):
        r = search(Pn, s, pos)
        if r is None: break
        out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
    return out
def hitlist(row):
    for ps in row.passes.values():
        if any("hit" in p for p in ps) or (ps == [] and False): return [p.get("hit") for p in ps]
    return []
def lab(row, labs):
    return "".join((" hits=[%s]" % ",".join(hitlist(row))) if l == "#hits" else " %s=%s" % (l, row.last.get(l)) for l in labs)
def aW(Pn, s): return "HOLDS" if whole_row(Pn, s) is not None else "FAILS"
def aS(Pn, s, labs=()):
    r = search(Pn, s)
    return "FAILS" if r is None else "`%s`@%d%s" % (s[r[0]:r[1]], r[0], lab(r[2], labs))
def aF(Pn, s, labs=()):
    return "[" + ", ".join("`%s`@%d%s" % (s[a:b], a, lab(rw, labs)) for a, b, rw in findall(Pn, s)) + "]"
def plain(x): return re.sub(r" (\w+|#hits)=(\[[^\]]*\]|[^\s,\]]*)", "", x)    # an answer without its labels
def keyW(Pn, s): return whole_row(Pn, s) is not None
def keyS(Pn, s):
    r = search(Pn, s); return None if r is None else (r[0], r[1])
def keyF(Pn, s): return tuple((a, b) for a, b, _ in findall(Pn, s))
KEYS = {"WHOLE": keyW, "SEARCHED": keyS, "FIND-ALL": keyF}
def fmtk(s, m, k):
    if m == "WHOLE": return "HOLDS" if k else "FAILS"
    if m == "SEARCHED": return "FAILS" if k is None else "`%s`@%d" % (s[k[0]:k[1]], k[0])
    return "[" + ", ".join("`%s`@%d" % (s[a:b], a) for a, b in k) + "]"
def diffcount(f1, f2, pool, modes=("WHOLE", "SEARCHED", "FIND-ALL")):
    """f1, f2: (mode, text) -> key. Texts that differ per mode, with the first (shortest, then least)."""
    out = []
    for m in modes:
        d = [s for s in order(pool) if f1(m, s) != f2(m, s)]
        if d:
            w = min(d, key=lambda x: (len(x), x))
            out.append("%s %d (first `%s`: %s vs %s)" % (m, len(d), w, fmtk(w, m, f1(m, w)), fmtk(w, m, f2(m, w))))
        else: out.append("%s 0" % m)
    return "; ".join(out) + " of %d" % len(pool)
def under(r, mk):
    """(mode, text) -> key, the program mk() built and run under rules r."""
    cache = {}
    def f(m, s):
        with rules(r):
            if r not in cache: cache[r] = mk()
            return KEYS[m](cache[r], s)
    return f
def holds(r, mk, pool):
    with rules(r):
        Pn = mk(); return sum(1 for s in order(pool) if whole_row(Pn, s) is not None)

# ------------------------------------------------------------------------------------------------ the programs
t2P = r"(?P<h>\d{1,2})(?::(?P<m>\d\d))?"
def late(h, m): return num(h) and num(m) and (int(h), int(m)) >= (9, 30)
def mk_t2(): return Pat(t2P)
def mk_q(): return W(Pat(t2P), C(("h", "m"), late))
Bd, Ad = r"(?P<l>\d\d)", r"(?P<l>\d)\d"
Ba, Aa = r"(?P<l>aa)", r"(?P<l>a)a"
PABp, PCDp = r"(?P<a>\d+)(?P<b>\d+)", r"(?P<c>\d+)(?P<d>\d+)"
REP1p, REPp = r"(?:(?P<h>\d);)*", r"(?:(?P<h>\d)?;)*"
KHp = r"(?P<k>\d)(?:;(?P<h>\d))*"
AHp = r"a(?P<h>\d)|b(?P<k>\d)|c"
UPp = r"(?P<b>\d+)(?P<a>\d)?"
SVp = r"(?P<h>\d)?x"
NUMp = r"(?P<n>\d+)"
CLOSEp = r"(?:(?P<h>\d+)(?::(?P<m>\d\d))?,)*"
TMLp = r"(?:(?P<h>\d{1,2})(?::(?P<m>\d\d))?,)*"
ABXYp = r"ab(?P<g>[xy])"
def h5(): return C("h", lt(5))
def pk(): return C("k", between(3, 7))
def lab_l(f): return C("l", f)
def alt_BA(B=Bd, A=Ad): return ALT(Pat(B), Pat(A))

DSP = strings("129 ", 5)                                   # 1,365
DIG4 = strings("0129", 4)                                  # 341
AB4 = strings("ab ", 4)                                    # 121
RG3 = strings("37;", 5)                                    # 364
TP5 = strings("905: ", 5)                                  # 3,906
SVPOOL = strings("37x ", 4)                                # 341
AHPOOL = strings("abc37", 3)                               # 156
OCCPOOL = strings("12 x", 4)                               # 341
ABP5 = strings("ab ", 5)                                   # 364
SCX5 = strings("37;x", 5)                                  # 1,365
KHPOOL = LP["KHPOOL"]                                      # 1,110
CLOSEPOOL, TMPOOL, XYPOOL = LP["CLOSEPOOL"], LP["TMPOOL"], LP["XYPOOL"]

# ================================================================================================= PART A: the catalogue
# Each line: tag, the draft site in rev 24, the program (a builder), its labels, the WHOLE / SEARCHED / FIND-ALL texts,
# and rev 23.2's PRINTED answers where the draft printed them (None = not printed in that mode). NOW = the rules in
# force (rev 24 unless switched); BEFORE = rev 23.2's rules.
CAT = []
def line(tag, site, desc, mk, labs, texts, printed=(None, None, None)): CAT.append((tag, site, desc, mk, labs, texts, printed))

# branch-scope (R.1.4)
line("B1", "R.1.4", "`(B | A) & (l: <20)`", lambda: W(alt_BA(), lab_l(lt(20))), ("l",), ("25", "25", "25 13"), ("FAILS", "FAILS", "[`13`@3]"))
line("B2", "R.1.4", "`(B & (l: <20)) | (A & (l: <20))`", lambda: ALT(W(Pat(Bd), lab_l(lt(20))), W(Pat(Ad), lab_l(lt(20)))), ("l",), ("25", "25", "25 13"), ("HOLDS", "`25`@0", None))
line("B3", "R.1.4, R.9 (L60)", "L60 `(B | A) & (l: \"a\")`, B := /(?<l>aa)/, A := /(?<l>a)a/", lambda: W(alt_BA(Ba, Aa), lab_l(eq("a"))), ("l",), ("aa", "aa", "aa aaaa"), ("FAILS", "FAILS", None))
line("B4", "R.1.4, R.9 (note (a), §4.5)", "`P & (a: \"1\")`, P := /(?<a>\\d+)(?<b>\\d+)/", lambda: W(Pat(PABp), C("a", eq("1"))), ("a", "b"), ("123", "123", "123 9 112"), ("FAILS", "`12`@0", None))
line("B5", "R.1.4", "`(B | A) & (l: <10)`", lambda: W(alt_BA(), lab_l(lt(10))), ("l",), ("12", "12", "12 25 13"), ("FAILS", "FAILS", None))
line("B6", "R.1.4", "`((B & (l: >50)) | A) & (l: <10)`", lambda: W(ALT(W(Pat(Bd), lab_l(lambda v: num(v) and int(v) > 50)), Pat(Ad)), lab_l(lt(10))), ("l",), ("12", "12", "12 25 13"), ("HOLDS", "`12`@0", None))
line("B7", "R.1.4", "`P & (a: <5) & (b: <5)` (L34)", lambda: W(Pat(PABp), C("a", lt(5)), C("b", lt(5))), ("a", "b"), ("123", "123", "123 12"), ("FAILS", "`12`@0", None))
line("B8", "R.1.4 (atomic, R.6)", "`atomic(B | A) & (l: <20)` (PCRE's atomic group)", lambda: W(Atom(alt_BA()), lab_l(lt(20))), ("l",), ("25", "25", "25 13"), None)
line("B9", "R.1.4 (atomic, R.6)", "`atomic(P & (a: \"1\"))` (the condition INSIDE the atomic group)", lambda: Atom(W(Pat(PABp), C("a", eq("1")))), ("a", "b"), ("123", "123", "123 9 112"), None)
# two-valued (R.1.5)
line("U1", "R.1.5", "`/(?<b>\\d+)(?<a>\\d)?/ & (a: <5)` (a test on an absent label fails; the next path is tried)", lambda: W(Pat(UPp), C("a", lt(5))), ("a", "b"), ("12", "12", "12 1 19 3"), None)
line("U2", "R.1.5", "`/(?<b>\\d+)(?<a>\\d)?/ & NOT (a: <5)` (NOT around a test of an absent label holds)", lambda: W(Pat(UPp), NOT(C("a", lt(5)))), ("a", "b"), ("1", "1", "1 12 19 3"), None)
line("U3", "R.1.5", "`/a(?<h>\\d)|b(?<k>\\d)|c/ & NOT ((h: <5) | (k: <5))` (one `|`)", lambda: W(Pat(AHp), NOT(ORC(h5(), C("k", lt(5))))), ("h", "k"), ("b7", "b7", "b7 a3 c"), ("FAILS", "FAILS", None))
line("U4", "R.1.5", "`t2 & NOT ((h, m): (<9, <30))` (joint)", lambda: W(mk_t2(), NOT(C(("h", "m"), lambda h, m: num(h) and num(m) and int(h) < 9 and int(m) < 30))), ("h", "m"), ("10", "10", "10 9 10:15"), ("FAILS", "FAILS", None))
line("U5", "R.1.5", "`t2 & NOT (h: <9, m: <30)` (record)", lambda: W(mk_t2(), NOT(ANDC(C("h", lt(9)), C("m", lt(30))))), ("h", "m"), ("10", "10", "10 9 10:15"), ("HOLDS", "`10`@0", None))
line("U6", "R.1.6", "`/(?:(?<a>\\d)?\\/)(?<b>\\d)/ & (a = 0: <10, b: >$a)` (record; `$a` reads the real label)", lambda: W(Pat(r"(?:(?P<a>\d)?/)(?P<b>\d)"), ANDC(C("a", lt(10), a="0"), C(("b", "a"), lambda b, a: num(b) and num(a) and int(b) > int(a)))), ("a", "b"), ("/5", "/5", "/5 3/5"), ("FAILS", "FAILS", None))
line("U7", "R.1.6", "`... & ((a = 0, b): a < 10 & b > a)` (joint: the part name reads the default)", lambda: W(Pat(r"(?:(?P<a>\d)?/)(?P<b>\d)"), C(("a", "b"), lambda a, b: num(a) and num(b) and int(a) < 10 and int(b) > int(a), a="0")), ("a", "b"), ("/5", "/5", "/5 3/5"), ("HOLDS", "`/5`@0", None))
line("U8", "R.1.6", "`/(?<h>\\d)?x/ & (h = 0: <5) & (h = 9: >7)` (two defaults on one label)", lambda: W(Pat(SVp), C("h", lt(5), h="0"), C("h", lambda v: num(v) and int(v) > 7, h="9")), ("h",), ("x", "3x", "x 3x x"), ("HOLDS", "`x`@1", None))
line("U9", "R.1.6", "`/a(?<h>\\d)|b(?<k>\\d)|c/ & (h = 0: <5) & (k: <5)`", lambda: W(Pat(AHp), C("h", lt(5), h="0"), C("k", lt(5))), ("h", "k"), ("b3", "b3", "b3 a3 b9"), ("HOLDS", "`b3`@0", None))
# the three spellings of "not" (R.3)
SV = lambda: Pat(SVp)
for j, (nm, mk) in enumerate((("`NOT (h: <5)`", lambda: W(SV(), NOT(h5()))), ("`(h: !<5)`", lambda: W(SV(), C("h", lambda v: not lt(5)(v)))),
                              ("`P & !(P & (h: <5))`", lambda: D(SV(), W(SV(), h5()))), ("`(h = \"x\": !<5)`", lambda: W(SV(), C("h", lambda v: not lt(5)(v), h="x"))))):
    pw = {0: ("FAILS", "FAILS", "HOLDS"), 1: ("FAILS", "FAILS", "HOLDS"), 2: ("HOLDS", "FAILS", "HOLDS"), 3: ("HOLDS", "FAILS", "HOLDS")}[j]
    ps = {0: ("FAILS", "FAILS", "`7x`@0"), 1: ("FAILS", "FAILS", "`7x`@0"), 2: ("`x`@0", "`x`@1", "`7x`@0"), 3: ("`x`@0", "`x`@1", "`7x`@0")}[j]
    for k, t in enumerate(("x", "3x", "7x")):
        line("N%d%s" % (j + 1, t), "R.3", "`/(?<h>\\d)?x/` & %s on `%s`" % (nm, t), mk, ("h",), (t, t, "x 3x 7x"), (pw[k], ps[k], None))
REP = lambda: Pat(REPp)
REPROWS = (("plain `(h: <5)`", lambda: W(REP(), h5())), ("`NOT (h: <5)`", lambda: W(REP(), NOT(h5()))),
           ("`(h: !<5)`", lambda: W(REP(), C("h", lambda v: not lt(5)(v)))), ("`REP & !(REP & (h: <5))`", lambda: D(REP(), W(REP(), h5()))))
PRINTREP = {  # rev 23.2 §R.3's printed table, WHOLE / SEARCHED, per text, per column
    "": (("FAILS", "FAILS"), ("FAILS", "FAILS"), ("FAILS", "FAILS"), ("HOLDS", "HOLDS")),
    "3;": (("HOLDS", "HOLDS"), ("FAILS", "FAILS"), ("FAILS", "FAILS"), ("FAILS", "HOLDS")),
    "3;7;": (("FAILS", "HOLDS"), ("HOLDS", "HOLDS"), ("FAILS", "HOLDS"), ("HOLDS", "HOLDS")),
    "7;;": (("FAILS", "FAILS"), ("HOLDS", "HOLDS"), ("FAILS", "HOLDS"), ("HOLDS", "HOLDS")),
    "3;;": (("FAILS", "HOLDS"), ("FAILS", "FAILS"), ("FAILS", "FAILS"), ("HOLDS", "HOLDS"))}
for j, (nm, mk) in enumerate(REPROWS):
    for t in ("", "3;", "3;7;", "7;;", "3;;"):
        pw, ps = PRINTREP[t][j]
        line("R%d%s" % (j + 1, t or "e"), "R.3", "REP := `/(?:(?<h>\\d)?;)*/`, `REP & ...` %s on `%s`" % (nm, t), mk, ("h",), (t, t, "3;7; 7;; 3;"), (pw, "HOLDS" if ps == "HOLDS" else ps, None))
# last pass (R.1.7)
line("L1", "R.1.7", "`/(?:(?<h>\\d);)*/ & (h: <5)`", lambda: W(Pat(REP1p), h5()), ("h",), ("7;3;", "7;3;", "7;3; 3;7;"), None)
line("L2", "R.1.7", "the same on the empty text", lambda: W(Pat(REP1p), h5()), ("h",), ("", "", ""), None)
line("L3", "R.1.7", "`/(?:(?<n>\\d),)*/ & (n = 0: <5)`", lambda: W(Pat(r"(?:(?P<n>\d),)*"), C("n", lt(5), n="0")), ("n",), ("7,", "7,", "7, 3,"), ("FAILS", "``@0", None))
line("L4", "R.1.7", "REP & `(h = 0: <5)` on the empty text", lambda: W(REP(), C("h", lt(5), h="0")), ("h",), ("", "", ""), ("HOLDS", "``@0", None))
line("L5", "R.1.7", "REP & `occurs.none((h = \"x\": !<5))` on `;`", lambda: W(REP(), NONE(C("h", lambda v: not lt(5)(v), h="x"))), ("h",), (";", ";", ";3; ;"), ("FAILS", "``@0", None))
line("L6", "R.1.7", "REP & `NOT some((h: <5))` on `;`", lambda: W(REP(), NOT(SOME(h5()))), ("h",), (";", ";", "; 3;"), ("HOLDS", "`;`@0", None))
line("L7", "R.1.7", "REP & `(h: !<5)` on `7;;`", lambda: W(REP(), C("h", lambda v: not lt(5)(v))), ("h",), ("7;;", "7;;", "3;7; 7;; 3;"), ("FAILS", "`7;`@0", None))
# complement and lookahead (R.1.4)
line("K1", "R.1.4", "`P & !(P & (a: \"1\"))`", lambda: D(Pat(PABp), W(Pat(PABp), C("a", eq("1")))), ("a", "b"), ("123", "123", "123 9 113"), ("HOLDS", "`123`@0", None))
line("K2", "R.1.4, R.5", "`t2 & !q` (q := t2 & ((h, m): >= (9, 30)))", lambda: D(mk_t2(), mk_q()), ("h", "m"), ("9:30", "9:30", "9:30 9:15"), ("FAILS", "`9`@0", None))
line("K3", "R.1.4", "`/(?=(?<x>\\d+))\\d/ & (x: \"1\")` (a lookahead is never re-entered)", lambda: W(Pat(r"(?=(?P<x>\d+))\d"), C("x", eq("1"))), ("x",), ("12", "12", "112 12 1"), None)
line("K4", "R.1.4", "`P & NOT (a: \"1\")` (NOT on a condition is not the complement)", lambda: W(Pat(PABp), NOT(C("a", eq("1")))), ("a", "b"), ("123", "123", "123 9 113"), None)
# occurrences (R.1.9)
NN = lambda: W(Pat(NUMp), C("n", lt(100)))
line("H1", "R.1.9", "`occurrences(/(?<n>\\d+)/ & (n: <100))` (the condition inside: every hit)", lambda: OCC(NN()), ("#hits",), ("1234", "x300 12", "1234 5"), (None, None, None))
line("H2", "R.1.9", "`occurrences(/\\d+/) & (hit: <100)` (a bare condition after the loop: the last hit)", lambda: W(OCC(Pat(r"\d+")), C("hit", lt(100))), ("#hits",), ("1234", "x300 12", "1234 5"), None)
line("H3", "R.1.9, R.6", "`hits(/(?<n>\\d+)/) & occurs.none(NOT (n: <100))` (the named all-hits request: committed hits)", lambda: W(Committed(Pat(NUMp)), NONE(NOT(C("n", lt(100))))), ("#hits",), ("1234", "x300 12", "1234 5"), None)
# when (R.1.10)
KH = lambda: Pat(KHp)
line("WH1", "R.1.10", "`KH & when((h: <5), (k: between(3, 7)))`, KH := /(?<k>\\d)(?:;(?<h>\\d))*/", lambda: WHEN(KH(), h5(), pk()), ("k", "h"), ("5;1;9", "5;1;9", "3;0;5 5;1;9"), ("HOLDS", "`5;1;9`@0", None))
line("WH2", "R.1.10", "`KH & when((h: <5), (k: between(3, 7)), (k: <3))` = `KH & (((h: <5) & (k: between(3, 7))) | (NOT (h: <5) & (k: <3)))`", lambda: W(KH(), ORC(ANDC(h5(), pk()), ANDC(NOT(h5()), C("k", lt(3))))), ("k", "h"), ("5;1;9", "1;0;9", "1;0;9 5;1;9 2;7"), None)
# the law A & B vs A & (0: B) (R.1.4)
line("Z1", "R.1.4 LAW", "`/(?<l>\\d+)/ & /1\\d*/`", lambda: AND(Pat(r"(?P<l>\d+)"), Pat(r"1\d*")), ("l",), ("12", "212", "212 31"), None)
line("Z2", "R.1.4 LAW", "`/(?<l>\\d+)/ & (0: /1\\d*/)`", lambda: ZERO(Pat(r"(?P<l>\d+)"), Pat(r"1\d*")), ("l",), ("12", "212", "212 31"), None)

# ------------------------------------------------------------------------------------------------ run PART A
print("== PART A: the catalogue (NOW = rev %s rules; BEFORE = rev 23.2 rules; PRINTED = rev 23.2's printed answer)" % NOWR)
RES = {}
for tag, site, desc, mk, labs, texts, printed in order(CAT):
    row = {}
    for col, r in (("NOW", NOWR), ("BEFORE", "23.2")):
        with rules(r):
            Pn = mk()
            row[col] = (aW(Pn, texts[0]), aS(Pn, texts[1], labs), aF(Pn, texts[2], labs))
    RES[tag] = row
moved, pmis, pchk = [], [], 0
for tag, site, desc, mk, labs, texts, printed in CAT:
    nw, bf = RES[tag]["NOW"], RES[tag]["BEFORE"]
    mv = nw != bf
    if mv: moved.append(tag)
    print("A %s [%s] %s" % (tag, site, desc))
    print("A %s   NOW    WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (tag, texts[0], nw[0], texts[1], nw[1], texts[2], nw[2]))
    print("A %s   BEFORE WHOLE %s ; SEARCHED %s ; FIND-ALL %s%s" % (tag, bf[0], bf[1], bf[2], "   MOVED" if mv else "   same"))
    if printed:
        for k, (p, b) in enumerate(zip(printed, bf)):
            if p is None: continue
            pchk += 1
            got = plain(b) if k else b
            if k == 1 and p == "HOLDS": ok = got != "FAILS"
            else: ok = got == p
            if not ok: pmis.append("%s mode %d: printed %s, rev 23.2 rules give %s" % (tag, k, p, got))
print("== PART A SUMMARY: %d lines; MOVED %d (%s)" % (len(CAT), len(moved), ", ".join(moved)))
print("== PRINTED CHECK: %d printed rev 23.2 answers compared with the rev 23.2 rules; mismatches %d" % (pchk, len(pmis)))
for x in pmis: print("   MISMATCH " + x)

# ================================================================================================= PART B: the old meanings
# Lane lastpass's table "WHAT THE NAMED REQUEST MUST COVER": for each row, the rev 23.2 program run under rev 23.2's
# rules (OLD) against the rev 24 spelling run under rev 24's rules (NEW), over a text set, in the three modes (WHOLE
# holds; SEARCHED the reported stretch; FIND-ALL the list of stretches). Labels are not compared (the spellings set
# different labels). The rev 24 spellings use only ruled pieces: a condition on the item with the loop over the
# conditioned item (§11's hole holding a program with conditions, repeated), `some`, `count`, `occurs.*`, NOT.
print("== PART B: the ways to write the old meanings (OLD = rev 23.2 program, rev 23.2 rules; NEW = rev 24 spelling, rev 24 rules)")
ITEM1 = r"(?P<h>\d);"
ITEMO = r"(?P<h>\d)?;"
def late_c(): return C(("h", "m"), late)
def close_R(**d): return C(("h", "m"), lambda h, m: num(h) and num(m) and int(h) < 10 and int(m) < 30, **d)
def hk(): return C(("h", "k"), lambda h, k: num(h) and num(k) and int(h) > int(k))
WAYS = [
 ("W1a", "every pass, at least one (rev 23.2's plain condition)", "`/(?:(?<h>\\d);)*/ & (h: <5)`", "`/(?:${item})+/`, item := `/(?<h>\\d);/ & (h: <5)`",
  lambda: W(Pat(REP1p), h5()), lambda: Rep(W(Pat(ITEM1), h5()), 1), RG3),
 ("W1b", "the same, by group questions", "`/(?:(?<h>\\d);)*/ & (h: <5)`", "`/(?:(?<h>\\d);)*/ & some((h: <5)) & occurs.none(NOT (h: <5))`",
  lambda: W(Pat(REP1p), h5()), lambda: W(Pat(REP1p), SOME(h5()), NONE(NOT(h5()))), RG3),
 ("W1c", "every pass, at least one, a pass may lack h (re-spelled in rev 24.1: a pass lacking h is not a pass of the item, so the loop ends there, as the old meaning's failing pass does)", "REP & `(h: <5)`", "`/(?:${item})+/`, item := `/(?<h>\\d);/ & (h: <5)` (= W1a's spelling)",
  lambda: W(REP(), h5()), lambda: Rep(W(Pat(ITEM1), h5()), 1), RG3),
 ("W1d", "the same, by group questions", "REP & `(h: <5)`", "REP & `some((h: <5)) & occurs.none(NOT (h: <5))`",
  lambda: W(REP(), h5()), lambda: W(REP(), SOME(h5()), NONE(NOT(h5()))), RG3),
 ("W2a", "every pass, possibly none (rev 23.2's `(h = d: S)`)", "REP & `(h = 0: <5)`", "`/(?:${item})*/`, item := `/(?<h>\\d)?;/ & (h = 0: <5)`",
  lambda: W(REP(), C("h", lt(5), h="0")), lambda: Rep(W(Pat(ITEMO), C("h", lt(5), h="0")), 0), RG3),
 ("W2b", "the same, by a group question", "REP & `(h = 0: <5)`", "REP & `occurs.none(NOT (h = 0: <5))`",
  lambda: W(REP(), C("h", lt(5), h="0")), lambda: W(REP(), NONE(NOT(C("h", lt(5), h="0")))), RG3),
 ("W3", "zero passes fine, a pass lacking h not (the sentinel)", "REP & `occurs.none((h = \"x\": !<5))`", "the same spelling",
  lambda: W(REP(), NONE(C("h", lambda v: not lt(5)(v), h="x"))), lambda: W(REP(), NONE(C("h", lambda v: not lt(5)(v), h="x"))), RG3),
 ("W4a", "a record per pass of the pairing loop, a label outside the loop with each pass", "KH & `(h: <5, k: between(3, 7))`",
  "KH & `(k: between(3, 7)) & some((h: <5)) & occurs.none(NOT (h: <5))`",
  lambda: W(KH(), ANDC(h5(), pk())), lambda: W(KH(), pk(), SOME(h5()), NONE(NOT(h5()))), KHPOOL),
 ("W4b", "a joint per pass", "TML & `((h, m): >= (9, 30))`", "TML & `some(J) & occurs.none(NOT J)`, J := `((h, m): >= (9, 30))`",
  lambda: W(Pat(TMLp), late_c()), lambda: W(Pat(TMLp), SOME(late_c()), NONE(NOT(late_c()))), TMPOOL),
 ("W4c", "every pass, possibly none, a joint with defaults (§4.3's closing example, I2b)", "CLOSE & `((h = 0, m = 0): (<10, <30))`",
  "CLOSE & `occurs.none(NOT ((h = 0, m = 0): (<10, <30)))`",
  lambda: W(Pat(CLOSEp), close_R(h="0", m="0")), lambda: W(Pat(CLOSEp), NONE(NOT(close_R(h="0", m="0")))), CLOSEPOOL),
 ("W4d", "a pass compared with a label outside the loop (`$k`)", "KH & `((h, k): h > k)`", "KH & `some(J) & occurs.none(NOT J)`, J := `((h, k): h > k)`",
  lambda: W(KH(), hk()), lambda: W(KH(), SOME(hk()), NONE(NOT(hk()))), KHPOOL),
 ("W5a", "not every pass (rev 23.2's NOT over the pass table)", "REP & `NOT (h: <5)`", "REP & `some((h: !<5))`",
  lambda: W(REP(), NOT(h5())), lambda: W(REP(), SOME(C("h", lambda v: not lt(5)(v)))), RG3),
 ("W5b", "every pass in !S", "REP & `(h: !<5)`", "REP & `some((h: !<5)) & occurs.none(NOT (h: !<5))`",
  lambda: W(REP(), C("h", lambda v: not lt(5)(v))), lambda: W(REP(), SOME(C("h", lambda v: not lt(5)(v))), NONE(NOT(C("h", lambda v: not lt(5)(v))))), RG3),
 ("W5c", "the pattern difference over every pass", "`REP & !(REP & (h: <5))`", "`REP & !(REP & some((h: <5)) & occurs.none(NOT (h: <5)))`",
  lambda: D(REP(), W(REP(), h5())), lambda: D(REP(), W(REP(), SOME(h5()), NONE(NOT(h5())))), RG3),
 ("W6a", "some", "REP & `some((h: <5))`", "the same spelling", lambda: W(REP(), SOME(h5())), lambda: W(REP(), SOME(h5())), RG3),
 ("W6b", "occurs.exactly", "REP & `occurs.exactly(2, (h: <5))`", "the same spelling", lambda: W(REP(), EXACTLY(2, h5())), lambda: W(REP(), EXACTLY(2, h5())), RG3),
 ("W6c", "NOT some = occurs.none", "REP & `NOT some((h: <5))`", "REP & `occurs.none((h: <5))`", lambda: W(REP(), NOT(SOME(h5()))), lambda: W(REP(), NONE(h5())), RG3),
 ("W6d", "occurs.at_least (r40 B9: run)", "REP & `occurs.at_least(2, (h: <5))`", "the same spelling", lambda: W(REP(), Count(h5(), lambda n: n >= 2)), lambda: W(REP(), Count(h5(), lambda n: n >= 2)), RG3),
 ("W6e", "occurs.at_most (r40 B9: run)", "REP & `occurs.at_most(1, (h: <5))`", "the same spelling", lambda: W(REP(), Count(h5(), lambda n: n <= 1)), lambda: W(REP(), Count(h5(), lambda n: n <= 1)), RG3),
 ("W7b", "one hit's label by literal index, `$m.hit[2].g` as a test (r40 B9: run)", "`hits(/ab(?<g>[xy])/) & (g[2]: \"x\")`", "the same spelling",
  lambda: W(Committed(Pat(ABXYp)), Idx("g", 2, eq("x"))), lambda: W(Committed(Pat(ABXYp)), Idx("g", 2, eq("x"))), XYPOOL),
 ("W7", "one pass by literal index", "REP & `(h[2]: <5)`", "the same spelling", lambda: W(REP(), Idx("h", 2, lt(5))), lambda: W(REP(), Idx("h", 2, lt(5))), RG3),
 ("W8", "the committed hits of a search, every hit (rev 23.2's plain condition on `hit`)", "`occurrences(/(?<n>\\d+)/) & (n: <100)`",
  "`hits(/(?<n>\\d+)/) & some((n: <100)) & occurs.none(NOT (n: <100))` (the named all-hits request)",
  lambda: W(OCC(Pat(NUMp)), C("n", lt(100))), lambda: W(Committed(Pat(NUMp)), SOME(C("n", lt(100))), NONE(NOT(C("n", lt(100))))), OCCPOOL),
 ("W9", "every hit is `abx` (rev 23.2's [HIT.0])", "`occurrences(/ab(?<g>[xy])/) & (g: \"x\")`",
  "`hits(/ab(?<g>[xy])/) & some((g: \"x\")) & occurs.none(NOT (g: \"x\"))`",
  lambda: W(OCC(Pat(ABXYp)), C("g", eq("x"))), lambda: W(Committed(Pat(ABXYp)), SOME(C("g", eq("x"))), NONE(NOT(C("g", eq("x"))))), XYPOOL),
]
WRES = {}
for tag, what, old, new, mko, mkn, pool in order(WAYS):
    WRES[tag] = diffcount(under("23.2", mko), under("24", mkn), pool)
zero = 0
for tag, what, old, new, mko, mkn, pool in WAYS:
    if all(x.split(" ")[1] == "0" for x in WRES[tag].split(" of ")[0].split("; ")): zero += 1
    print("B %s %s: OLD %s ; NEW %s" % (tag, what, old, new))
    print("B %s   texts that differ: %s" % (tag, WRES[tag]))
print("== PART B SUMMARY: %d rows; %d at 0 differences in every mode" % (len(WAYS), zero))
# W10: reading a pass's VALUE (`$h[2]`): the named request's pass table is the same data under both rules
def val2(r):
    out = {}
    with rules(r):
        Pn = W(REP())
        for s in order(RG3):
            rw = whole_row(Pn, s)
            if rw is not None:
                lp = rw.loop.get("h"); ps = rw.passes.get(lp, []) if lp else []
                out[s] = ps[1].get("h") if len(ps) >= 2 else None
    return out
v23, v24 = val2("23.2"), val2("24")
print("B W10 reading a pass's value `$h[2]` (the captures level) on REP's whole rows: texts whose value differs %d of %d (both rules read the same pass table)" % (sum(1 for s in RG3 if v23.get(s) != v24.get(s)), len(RG3)))
# CONTROL for PART B: the comparison can fail. The rev 24 BARE spelling (the last pass) against the old meaning.
CTRL = [("W1c-carry", "the rev 24 spelling with the OPTIONAL item, `/(?:${item})+/`, item := `/(?<h>\\d)?;/ & (h: <5)` (rev 24's W1c; a pass lacking h reads the earlier pass's h, FIX-A1)", lambda: W(REP(), h5()), lambda: Rep(W(Pat(ITEMO), h5()), 1), RG3),
        ("W1a-bare", "`/(?:(?<h>\\d);)*/ & (h: <5)` read under rev 24 (the last pass)", lambda: W(Pat(REP1p), h5()), lambda: W(Pat(REP1p), h5()), RG3),
        ("W2b-bare", "REP & `(h = 0: <5)` under rev 24", lambda: W(REP(), C("h", lt(5), h="0")), lambda: W(REP(), C("h", lt(5), h="0")), RG3),
        ("W4a-bare", "KH & `(h: <5, k: between(3, 7))` under rev 24", lambda: W(KH(), ANDC(h5(), pk())), lambda: W(KH(), ANDC(h5(), pk())), KHPOOL),
        ("W4c-bare", "CLOSE & `((h = 0, m = 0): (<10, <30))` under rev 24", lambda: W(Pat(CLOSEp), close_R(h="0", m="0")), lambda: W(Pat(CLOSEp), close_R(h="0", m="0")), CLOSEPOOL),
        ("W8-bare", "`occurrences(/(?<n>\\d+)/) & (n: <100)` under rev 24 (one pattern, the last hit)", lambda: W(OCC(Pat(NUMp)), C("n", lt(100))), lambda: W(OCC(Pat(NUMp)), C("n", lt(100))), OCCPOOL)]
CR = {t: diffcount(under("23.2", mo), under("24", mn), pool) for t, d, mo, mn, pool in order(CTRL)}
for t, d, mo, mn, pool in CTRL: print("B %s CONTROL rev 23.2's meaning vs %s: %s" % (t, d, CR[t]))

# ================================================================================================= PART C: libpcre2
# Each rev 24 rule whose regex model exists, as a PCRE2 pattern with callouts (a condition = a callout placed where it
# is written; "fail here" when the test is not TRUE), RUN on libpcre2-8, against the rev 24 engine (NOW rules) over a
# text set in all three modes, labels included.
print("== PART C: the rev 24 engine against libpcre2-8 %s (callout models; NO_AUTO_POSSESS, NO_START_OPTIMIZE)" % P.version())
def Tc(l, S):
    def f(c):
        v = c.get(l); return None if v is None else bool(S(v))
    return f
CO = {"l<20": Tc("l", lt(20)), "l=a": Tc("l", eq("a")), "a=1": Tc("a", eq("1")), "a<5": Tc("a", lt(5)), "h<5": Tc("h", lt(5)),
      "h!<5": Tc("h", lambda v: not lt(5)(v)), "x=1": Tc("x", eq("1")), "a2=1": Tc("a2", eq("1")), "p": Tc("k", between(3, 7)),
      "k<3": Tc("k", lt(3)), "n<100": Tc("n", lt(100)), "late": lambda c: late(c.get("h"), c.get("m")),
      "a=1|c=1": lambda c: c.get("a") == "1" or c.get("c") == "1"}
REST, TIE = r"(?<T>[\s\S]*+)", r"(?=\k<T>\z)"
EAT = r"(?:(?!\k<T>\z)[\s\S])*+"
def rxkey(rx, labs):
    """PCRE2's answers, with the program's labels only (the model's helper groups T, a2, h2, ... are not labels)."""
    def f(m, s):
        if m == "WHOLE":                                # FIX-A5: the WHOLE key carries the labels
            r = rx.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
            return None if r is None else tuple(sorted((l, r[2].get(l)) for l in labs))
        if m == "SEARCHED":
            r = rx.search(s); return None if r is None else (r[0], r[1], tuple(sorted((l, r[2].get(l)) for l in labs)))
        return tuple((a, b, tuple(sorted((l, d.get(l)) for l in labs))) for a, b, d in rx.findall(s))
    return f
def enkey(mk, labs):
    cache = {}
    def f(m, s):
        with rules(NOWR):
            if "p" not in cache: cache["p"] = mk()
            Pn = cache["p"]
            if m == "WHOLE":                            # FIX-A5
                r = whole_row(Pn, s); return None if r is None else tuple(sorted((l, r.last.get(l)) for l in labs))
            if m == "SEARCHED":
                r = search(Pn, s); return None if r is None else (r[0], r[1], tuple(sorted((l, r[2].last.get(l)) for l in labs)))
            return tuple((a, b, tuple(sorted((l, rw.last.get(l)) for l in labs))) for a, b, rw in findall(Pn, s))
    return f
def fmtc(s, m, k):
    if m == "WHOLE": return "FAILS" if k is None else "HOLDS" + "".join(" %s=%s" % lv for lv in k)
    one = lambda x: "`%s`@%d%s" % (s[x[0]:x[1]], x[0], "".join(" %s=%s" % lv for lv in x[2]))
    if m == "SEARCHED": return "FAILS" if k is None else one(k)
    return "[" + ", ".join(one(x) for x in k) + "]"
class SM:
    """FIX-A3's independent control: a libpcre2 model of `A & B` (kind "and") or `A & !B` (kind "not") in which B is
    its OWN compiled pattern, run WHOLE (ANCHORED | ENDANCHORED) on the stretch that a callout at the end of A extracts
    (subject[start_match:current_position]); so B's anchors and lookarounds read the stretch, as R.1.4 says, and the
    model does not share the engine's construction. A failing inner match makes the callout fail: PCRE backtracks
    into A's next path (A's paths outer). B's own callouts see A's captures (`o`) and B's (`c`). The reported labels
    are A's captures and the inner match's (the last successful callout's)."""
    def __init__(self, outer, inner, kind, ico=None):
        self.kind, self.side, self.o = kind, {}, {}
        self.pattern = "%s (?C) then %s%s on the stretch" % (outer, "!" if kind == "not" else "", inner)
        self.inner = P.Pcre(inner, {k: (lambda c, f=f: f(c, self.o)) for k, f in (ico or {}).items()})
        self.outer = P.Pcre(outer + '(?C"__op")', {"__op": self._op})
    def _op(self, ctx):
        self.o = {nm: ctx.get(nm) for nm in self.outer.names}
        r = self.inner.match(ctx.stretch(), 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
        if self.kind == "not": return r is None
        if r is None: return False
        self.side = r[2]; return True
    def match(self, s, start=0, opts=0):
        self.side = {}
        r = self.outer.match(s, start, opts)
        if r is None: return None
        d = dict(r[2]); d.update(self.side); return r[0], r[1], d
    def search(self, s, pos=0): return self.match(s, pos)
    def findall(self, s):
        out, pos = [], 0
        while pos <= len(s):
            r = self.match(s, pos)
            if r is None: break
            out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
        return out
PABx, PCDx = r"(?<a>\d+)(?<b>\d+)", r"(?<c>\d+)(?<d>\d+)"
T2x = r"(?<h>\d{1,2})(?::(?<m>\d\d))?"
PCASES = [
 ("V1", "branch-scope `(B | A) & (l: <20)`", r'(?|(?<l>\d\d)|(?<l>\d)\d)(?C"l<20")', lambda: W(alt_BA(), lab_l(lt(20))), ("l",), DSP),
 ("V2", "L60 `(B | A) & (l: \"a\")`", r'(?|(?<l>aa)|(?<l>a)a)(?C"l=a")', lambda: W(alt_BA(Ba, Aa), lab_l(eq("a"))), ("l",), AB4),
 ("V3", "`P & (a: \"1\")`", r'(?<a>\d+)(?<b>\d+)(?C"a=1")', lambda: W(Pat(PABp), C("a", eq("1"))), ("a", "b"), DSP),
 ("V4", "an absent label fails, the next path is tried", r'(?<b>\d+)(?<a>\d)?(?C"a<5")', lambda: W(Pat(UPp), C("a", lt(5))), ("a", "b"), DSP),
 ("V5", "NOT around an absent label holds (a negative lookahead)", r'(?<b>\d+)(?<a>\d)?(?!(?C"a<5"))', lambda: W(Pat(UPp), NOT(C("a", lt(5)))), ("a", "b"), DSP),
 ("V6", "last pass `/(?:(?<h>\\d);)*/ & (h: <5)`", r'(?:(?<h>\d);)*(?C"h<5")', lambda: W(Pat(REP1p), h5()), ("h",), RG3),
 ("V7", "last pass, a pass may lack h: REP & `(h: <5)`", r'(?:(?<h>\d)?;)*(?C"h<5")', lambda: W(REP(), h5()), ("h",), RG3),
 ("V8", "REP & `(h: !<5)`", r'(?:(?<h>\d)?;)*(?C"h!<5")', lambda: W(REP(), C("h", lambda v: not lt(5)(v))), ("h",), RG3),
 ("V9", "REP & `NOT (h: <5)`", r'(?:(?<h>\d)?;)*(?!(?C"h<5"))', lambda: W(REP(), NOT(h5())), ("h",), RG3),
 ("V10", "every pass: `/(?:${item})+/`, item := `/(?<h>\\d);/ & (h: <5)`", r'(?:(?<h>\d)(?C"h<5");)+', lambda: Rep(W(Pat(ITEM1), h5()), 1), ("h",), RG3),
 ("V11", "complement: `P & !(P & (a: \"1\"))` (the operand run WHOLE on the extracted stretch)", SM(PABx, PABx + '(?C"a=1")', "not", {"a=1": lambda c, o: c.get("a") == "1"}),
  lambda: D(Pat(PABp), W(Pat(PABp), C("a", eq("1")))), ("a", "b"), DSP),
 ("V12", "a lookahead is not re-entered", r'(?=(?<x>\d+))\d(?C"x=1")', lambda: W(Pat(r"(?=(?P<x>\d+))\d"), C("x", eq("1"))), ("x",), DSP),
 ("V13", "when(c, p) = x & (NOT c | p): an alternation of two tests", r'(?<k>\d)(?:;(?<h>\d))*(?:(?!(?C"h<5"))|(?C"p"))', lambda: WHEN(KH(), h5(), pk()), ("k", "h"), KHPOOL),
 ("V14", "when(c, p) against PCRE's conditional group", r'(?<k>\d)(?:;(?<h>\d))*(?(?=(?C"h<5"))(?C"p")|)', lambda: WHEN(KH(), h5(), pk()), ("k", "h"), KHPOOL),
 ("V15", "the else form x & ((c & p) | (NOT c & q))", r'(?<k>\d)(?:;(?<h>\d))*(?:(?C"h<5")(?C"p")|(?!(?C"h<5"))(?C"k<3"))',
  lambda: W(KH(), ORC(ANDC(h5(), pk()), ANDC(NOT(h5()), C("k", lt(3))))), ("k", "h"), KHPOOL),
 ("V16", "occurrences, the condition inside: `occurrences(/(?<n>\\d+)/ & (n: <100), min = 1)`", r'(?:[\s\S]*?(?<n>\d+)(?C"n<100"))+[\s\S]*', lambda: OCC(NN(), 1), ("n",), OCCPOOL),
 ("V17", "atomic(B | A) & (l: <20)", r'(?>(?|(?<l>\d\d)|(?<l>\d)\d))(?C"l<20")', lambda: W(Atom(alt_BA()), lab_l(lt(20))), ("l",), DSP),
 ("V18", "atomic(P & (a: \"1\"))", r'(?>(?<a>\d+)(?<b>\d+)(?C"a=1"))', lambda: Atom(W(Pat(PABp), C("a", eq("1")))), ("a", "b"), DSP),
 ("V19", "join-order left: `(P & Q) & ((a: \"1\") | (c: \"1\"))` (Q WHOLE on the extracted stretch)", SM(PABx, PCDx + '(?C"a|c")', "and", {"a|c": lambda c, o: o.get("a") == "1" or c.get("c") == "1"}),
  lambda: W(AND(Pat(PABp), Pat(PCDp)), ORC(C("a", eq("1")), C("c", eq("1")))), ("a", "b", "c", "d"), DSP),
 ("V20", "`t2 & !q` (q WHOLE on the extracted stretch)", SM(T2x, T2x + '(?C"late")', "not", {"late": lambda c, o: late(c.get("h"), c.get("m"))}),
  lambda: D(mk_t2(), mk_q()), ("h", "m"), TP5),
 ("V21", "join-order with a LAZY right operand: `G & L`, G := /(?<a>\\d+)/, L := /(?<c>\\d+?)/", SM(r"(?<a>\d+)", r"(?<c>\d+?)", "and"),
  lambda: AND(Pat(r"(?P<a>\d+)"), Pat(r"(?P<c>\d+?)")), ("a", "c"), DSP),
 ("V22", "the same, the other order: `L & G`", SM(r"(?<c>\d+?)", r"(?<a>\d+)", "and"),
  lambda: AND(Pat(r"(?P<c>\d+?)"), Pat(r"(?P<a>\d+)")), ("a", "c"), DSP),
 ("V23", "an ANCHORED right operand: `/\\d/ & /\\d$/`", SM(r"\d", r"\d$", "and"), lambda: AND(Pat(r"\d"), Pat(r"\d$")), (), DSP),
 ("V24", "a LOOKAHEAD right operand under the complement: `/\\d/ & !/\\d(?=\\d)/`", SM(r"\d", r"\d(?=\d)", "not"), lambda: D(Pat(r"\d"), Pat(r"\d(?=\d)")), (), DSP),
 ("V25", "a `\\b` right operand: `/\\d+/ & /\\d+\\b/`", SM(r"\d+", r"\d+\b", "and"), lambda: AND(Pat(r"\d+"), Pat(r"\d+\b")), (), DSP),
 # DEFAULTS (r40 C6: DEFAULTS leave §R.6's exception list): a per-test default is PCRE's conditional group on the label
 ("V26", "a default inside the set: `/(?<h>\\d)?x/ & (h = 0: <5)`", r'(?<h>\d)?x(?(<h>)(?C"h<5")|(?C"d0<5"))', lambda: W(Pat(SVp), C("h", lt(5), h="0")), ("h",), SVPOOL),
 ("V27", "a default outside the set: `/(?<h>\\d)?x/ & (h = 9: <5)`", r'(?<h>\d)?x(?(<h>)(?C"h<5")|(?C"d9<5"))', lambda: W(Pat(SVp), C("h", lt(5), h="9")), ("h",), SVPOOL),
 ("V28", "the same under NOT: `/(?<h>\\d)?x/ & NOT (h = 9: <5)`", r'(?<h>\d)?x(?!(?(<h>)(?C"h<5")|(?C"d9<5")))', lambda: W(Pat(SVp), NOT(C("h", lt(5), h="9"))), ("h",), SVPOOL),
 ("V29", "a joint with defaults over a loop: `CLOSE & ((h = 0, m = 0): (<10, <30))` (last settings)", r'(?:(?<h>\d+)(?::(?<m>\d\d))?,)*(?(<h>)(?C"h<10")|(?C"d0<10"))(?(<m>)(?C"m<30")|(?C"d0<30"))',
  lambda: W(Pat(CLOSEp), close_R(h="0", m="0")), ("h", "m"), CLOSEPOOL),
 # THE PLACE-BY-OPERATOR GRID (r40 A1, A2): a label set inside a loop place, read by a condition INSIDE the place
 # (reading the labels set so far) or OUTSIDE it (the last setting overall)
 ("G1", "hole loop, OPTIONAL label, condition INSIDE: `/(?:${item})+/`, item := `/(?<h>\\d)?;/ & (h: <5)` (W1c)", r'(?:(?<h>\d)?;(?C"h<5"))+', lambda: Rep(W(Pat(r"(?P<h>\d)?;"), h5()), 1), ("h",), RG3),
 ("G2", "occurrences, OPTIONAL label, condition INSIDE: `occurrences(/(?<x>(?<g>a)?b)/ & (g: \"a\"), min = 1)`", r'(?:[\s\S]*?(?<x>(?<g>a)?b)(?C"g=a"))+[\s\S]*', lambda: OCC(W(Pat(r"(?P<x>(?P<g>a)?b)"), C("g", eq("a"))), 1), ("x", "g"), ABP5),
 ("G3", "hole loop, OPTIONAL label, condition OUTSIDE: `/(?:${item})+/ & (h: <5)`, item := `/(?<h>\\d)?;/`", r'(?:(?<h>\d)?;)+(?C"h<5")', lambda: W(Rep(Pat(r"(?P<h>\d)?;"), 1), h5()), ("h",), RG3),
 ("G4", "occurrences, OPTIONAL label, condition OUTSIDE: `occurrences(/(?<x>(?<g>a)?b)/, min = 1) & (g: \"a\")`", r'(?:[\s\S]*?(?<x>(?<g>a)?b))+[\s\S]*(?C"g=a")', lambda: W(OCC(Pat(r"(?P<x>(?P<g>a)?b)"), 1), C("g", eq("a"))), ("x", "g"), ABP5),
 ("G5", "hole loop, label looped at TWO depths, condition OUTSIDE: item := `/(?:(?<h>\\d);)+x/`", r'(?:(?:(?<h>\d);)+x)+(?C"h<5")', lambda: W(Rep(Pat(r"(?:(?P<h>\d);)+x"), 1), h5()), ("h",), SCX5),
 ("G6", "occurrences, label looped at TWO depths, condition OUTSIDE: `occurrences(/(?:(?<h>\\d);)+/, min = 1) & (h: <5)`", r'(?:[\s\S]*?(?:(?<h>\d);)+)+[\s\S]*(?C"h<5")', lambda: W(OCC(Pat(r"(?:(?P<h>\d);)+"), 1), h5()), ("h",), SCX5),
 ("G7", "hole loop, ATOMIC item, condition OUTSIDE: item := `atomic(B | A)`, then `(l: <20)`", r'(?:(?>(?|(?<l>\d\d)|(?<l>\d)\d)))+(?C"l<20")', lambda: W(Rep(Atom(alt_BA()), 1), lab_l(lt(20))), ("l",), DSP),
 ("G8", "occurrences, ATOMIC argument, condition OUTSIDE: `occurrences(atomic(B | A), min = 1) & (l: <20)`", r'(?:[\s\S]*?(?>(?|(?<l>\d\d)|(?<l>\d)\d)))+[\s\S]*(?C"l<20")', lambda: W(OCC(Atom(alt_BA()), 1), lab_l(lt(20))), ("l",), DSP),
 ("G9", "hole loop, label looped at TWO depths, condition INSIDE: item := `/(?:(?<h>\\d);)+x/ & (h: <5)`", r'(?:(?:(?<h>\d);)+x(?C"h<5"))+', lambda: Rep(W(Pat(r"(?:(?P<h>\d);)+x"), h5()), 1), ("h",), SCX5),
]
CO["late2"] = lambda c: late(c.get("h2"), c.get("m2"))
CO["g=a"] = Tc("g", eq("a"))
CO.update({"d0<5": lambda c: True, "d9<5": lambda c: False, "h<10": Tc("h", lt(10)), "m<30": Tc("m", lt(30)), "d0<10": lambda c: True, "d0<30": lambda c: True})
pexact = 0
for tag, nm, pat, mk, labs, pool in PCASES:
    rx = pat if isinstance(pat, SM) else P.Pcre(pat, CO)
    f1, f2 = rxkey(rx, labs), enkey(mk, labs)
    out = []
    for m in ("WHOLE", "SEARCHED", "FIND-ALL"):
        d = [s for s in order(pool) if f1(m, s) != f2(m, s)]
        if d:
            w = min(d, key=lambda x: (len(x), x))
            out.append("%s %d (first `%s`: PCRE2 %s, engine %s)" % (m, len(d), w, fmtc(w, m, f1(m, w)), fmtc(w, m, f2(m, w))))
        else: out.append("%s 0" % m)
    if all(x.split(" ")[1] == "0" for x in out): pexact += 1
    print("C %s %s  /%s/" % (tag, nm, rx.pattern))
    print("C %s   texts that differ: %s of %d" % (tag, "; ".join(out), len(pool)))
print("== PART C SUMMARY: %d models; %d equal to the engine in every mode" % (len(PCASES), pexact))
# THE ORDER CHECK (r40 C1: replaces the order-swap run, which reversed nothing that carries meaning). `&`'s operand
# order carries meaning in rev 24 (join-order: labels; a lazy operand: the stretch). Each `&` model is run against the
# engine with its operands SWAPPED: that comparison MUST differ (else the model cannot tell the orders apart and the
# PART C equality guards nothing); the forward comparison is PART C's line.
print("== ORDER CHECK: each `&` model of PART C against the engine with the operands SWAPPED (must differ)")
PBY = {t: (pt, lb, pl) for t, n_, pt, m_, lb, pl in PCASES}
ocheck = []
for tag, mksw in (("V19", lambda: W(AND(Pat(PCDp), Pat(PABp)), ORC(C("a", eq("1")), C("c", eq("1"))))),
                  ("V21", lambda: AND(Pat(r"(?P<c>\d+?)"), Pat(r"(?P<a>\d+)"))),
                  ("V22", lambda: AND(Pat(r"(?P<a>\d+)"), Pat(r"(?P<c>\d+?)")))):
    rx, labs, pool = PBY[tag]
    f1, f2 = rxkey(rx, labs), enkey(mksw, labs)
    n = [sum(1 for s in pool if f1(m, s) != f2(m, s)) for m in ("WHOLE", "SEARCHED", "FIND-ALL")]
    ok = sum(n) > 0; ocheck.append(ok)
    print("C ORDER %s the model vs the engine with the operands swapped: WHOLE %d; SEARCHED %d; FIND-ALL %d of %d: %s" % (
        tag, n[0], n[1], n[2], len(pool), "DIFFERS (the check can fail)" if ok else "EQUAL: THE CHECK GUARDS NOTHING"))
print("== ORDER CHECK SUMMARY: %d of %d swapped runs differ from their model" % (sum(ocheck), len(ocheck)))

# ================================================================================================= PART D: properties
print("== PART D: properties of the rev 24 rules (NOW), with rev 23.2 (BEFORE) beside")
def nowf(mk): return under(NOWR, mk)
def bef(mk): return under("23.2", mk)
def l1(): return lab_l(eq("1"))
CS = [("(l: <20)", lambda: lab_l(lt(20))), ("(l: \"1\")", l1), ("NOT (l: <20)", lambda: NOT(lab_l(lt(20))))]
for nm, c in CS:
    a = lambda c=c: W(alt_BA(), c()); b = lambda c=c: ALT(W(Pat(Bd), c()), W(Pat(Ad), c()))
    print("D D1 `&` distributes over `|`: `(B | A) & %s` vs `(B & %s) | (A & %s)`: NOW %s ; BEFORE %s" % (nm, nm, nm, diffcount(nowf(a), nowf(b), DIG4), diffcount(bef(a), bef(b), DIG4)))
def admits(r, mkp, mkc, pool):
    with rules(r):
        Pp, Pc = mkp(), mkc()
        w = [s for s in order(pool) if whole_row(Pc, s) is not None and whole_row(Pp, s) is None]
        s_ = [s for s in order(pool) if search(Pc, s) is not None and search(Pp, s) is None]
    f = lambda xs: "%d%s" % (len(xs), (" (first `%s`)" % min(xs, key=lambda x: (len(x), x))) if xs else "")
    return "WHOLE %s, SEARCHED %s of %d" % (f(w), f(s_), len(pool))
for nm, mkp, mkc in (("`(B | A) & (l: <10)` over `B | A`", lambda: alt_BA(), lambda: W(alt_BA(), lab_l(lt(10)))),
                     ("`((B & (l: >50)) | A) & (l: <10)` over `(B | A) & (l: <10)` (a condition added INSIDE a branch)", lambda: W(alt_BA(), lab_l(lt(10))),
                      lambda: W(ALT(W(Pat(Bd), lab_l(lambda v: num(v) and int(v) > 50)), Pat(Ad)), lab_l(lt(10)))),
                     ("`P & (a: \"1\")` over P", lambda: Pat(PABp), lambda: W(Pat(PABp), C("a", eq("1")))),
                     ("`P & NOT ((b: \"2\") & (a: \"1\"))` over `P & NOT (b: \"2\")` (added under NOT)", lambda: W(Pat(PABp), NOT(C("b", eq("2")))),
                      lambda: W(Pat(PABp), NOT(ANDC(C("b", eq("2")), C("a", eq("1")))))),
                     ("`P & !(P & (b: \"2\") & (a: \"1\"))` over `P & !(P & (b: \"2\"))` (added inside a complement)", lambda: D(Pat(PABp), W(Pat(PABp), C("b", eq("2")))),
                      lambda: D(Pat(PABp), W(Pat(PABp), C("b", eq("2")), C("a", eq("1")))))):
    print("D D2 adding a condition admits a text (single match, the top of the chain): %s: NOW %s ; BEFORE %s" % (nm, admits(NOWR, mkp, mkc, DIG4), admits("23.2", mkp, mkc, DIG4)))
def resplit(r, mkp, mkc, pool):
    with rules(r):
        Pp, Pc = mkp(), mkc()
        xs = [s for s in order(pool) if set((a, b) for a, b, _ in findall(Pc, s)) - set((a, b) for a, b, _ in findall(Pp, s))]
    return "%d of %d%s" % (len(xs), len(pool), (" (first `%s`)" % min(xs, key=lambda x: (len(x), x))) if xs else "")
print("D D3 FIND-ALL hits re-split (a hit that is not a hit of the plain pattern): `/(?<l>\\d+)/ & (l: <100)`: NOW %s ; BEFORE %s" % (
    resplit(NOWR, lambda: Pat(r"(?P<l>\d+)"), lambda: W(Pat(r"(?P<l>\d+)"), lab_l(lt(100))), DSP), resplit("23.2", lambda: Pat(r"(?P<l>\d+)"), lambda: W(Pat(r"(?P<l>\d+)"), lab_l(lt(100))), DSP)))
print("D D3 the same for `P & (a: \"1\")`: NOW %s ; BEFORE %s" % (resplit(NOWR, lambda: Pat(PABp), lambda: W(Pat(PABp), C("a", eq("1"))), DIG4), resplit("23.2", lambda: Pat(PABp), lambda: W(Pat(PABp), C("a", eq("1"))), DIG4)))
a = lambda: W(Pat(PABp), NOT(C("a", eq("1")))); b = lambda: D(Pat(PABp), W(Pat(PABp), C("a", eq("1"))))
print("D D4 NOT on a condition vs the complement: `P & NOT (a: \"1\")` vs `P & !(P & (a: \"1\"))`: NOW %s ; BEFORE %s" % (diffcount(nowf(a), nowf(b), DIG4), diffcount(bef(a), bef(b), DIG4)))
for nm, A_, B_ in (("`/(?<l>\\d+)/` & `/1\\d*/`", lambda: Pat(r"(?P<l>\d+)"), lambda: Pat(r"1\d*")),
                   ("`/(?<l>\\d+)/` & `/\\d+?/` (a lazy B)", lambda: Pat(r"(?P<l>\d+)"), lambda: Pat(r"\d+?")),
                   ("`/\\d+/` & `(P & (a: \"1\"))` (a conditioned B)", lambda: Pat(r"\d+"), lambda: W(Pat(PABp), C("a", eq("1")))),
                   ("`t2` & `q`", mk_t2, mk_q),
                   ("`/\\d/` & `/\\d$/` (an ANCHORED B, r40 A3)", lambda: Pat(r"\d"), lambda: Pat(r"\d$")),
                   ("`/\\d/` & `/\\d(?=\\d)/` (a LOOKAHEAD B)", lambda: Pat(r"\d"), lambda: Pat(r"\d(?=\d)")),
                   ("`/\\d+/` & `/\\d+\\b/` (a `\\b` B)", lambda: Pat(r"\d+"), lambda: Pat(r"\d+\b")),
                   ("`/\\d+/` & `/(?<!1)\\d+/` (a LOOKBEHIND B)", lambda: Pat(r"\d+"), lambda: Pat(r"(?<!1)\d+"))):
    x = lambda A_=A_, B_=B_: AND(A_(), B_()); y = lambda A_=A_, B_=B_: ZERO(A_(), B_())
    xd = lambda A_=A_, B_=B_: D(A_(), B_())
    yd = lambda A_=A_, B_=B_: Keep(ope(A_()), lambda row, s, i, e, B_=B_: whole_row(B_(), s[i:e]) is None)
    pool = DSP if "t2" not in nm else TP5
    print("D D5 LAW `A & B` vs `A & (0: B)` (holds and the stretch), %s: NOW %s ; BEFORE %s" % (nm, diffcount(nowf(x), nowf(y), pool), diffcount(bef(x), bef(y), pool)))
    print("D D5 LAW `A & !B` vs `A & NOT (0: B)`, %s: NOW %s" % (nm, diffcount(nowf(xd), nowf(yd), pool)))
lj = lambda: W(AND(Pat(r"\d+"), Pat(PABp)), C("a", eq("1"))); lz = lambda: W(ZERO(Pat(r"\d+"), Pat(PABp)), C("a", eq("1")))
print("D D5 LAW, the labels part: `(/\\d+/ & P) & (a: \"1\")` vs `(/\\d+/ & (0: P)) & (a: \"1\")` (only `&` joins P's labels): NOW %s" % diffcount(nowf(lj), nowf(lz), DIG4))
a = lambda: W(mk_t2(), NOT(C(("h", "m"), lambda h, m: num(h) and num(m) and int(h) < 9 and int(m) < 30))); b = lambda: W(mk_t2(), NOT(ANDC(C("h", lt(9)), C("m", lt(30)))))
print("D D6 joint vs record under NOT: `t2 & NOT ((h, m): (<9, <30))` vs `t2 & NOT (h: <9, m: <30)`: NOW %s ; BEFORE %s" % (diffcount(nowf(a), nowf(b), TP5), diffcount(bef(a), bef(b), TP5)))
a = lambda: W(Pat(AHp), NOT(ORC(h5(), C("k", lt(5))))); b = lambda: W(Pat(AHp), NOT(h5()), NOT(C("k", lt(5))))
print("D D7 De Morgan on conditions: `NOT ((h: <5) | (k: <5))` vs `NOT (h: <5) & NOT (k: <5)` on AH: NOW %s ; BEFORE %s" % (diffcount(nowf(a), nowf(b), AHPOOL), diffcount(bef(a), bef(b), AHPOOL)))
a = lambda: W(REP(), h5()); b = lambda: W(REP(), NOT(SOME(NOT(h5()))))
print("D D7 the loop dual is NOT the bare condition under rev 24 (the bare label is the last pass; the every-pass form is the named one, PART B): REP & `(h: <5)` vs REP & `NOT some(NOT (h: <5))`: NOW %s ; BEFORE %s" % (diffcount(nowf(a), nowf(b), RG3), diffcount(bef(a), bef(b), RG3)))
a = lambda: WHEN(KH(), h5(), pk())
print("D D8 `KH & when((h: <5), (k: between(3, 7)))`, rev 24's definition vs rev 23.2's filter form: %s ; WHOLE holds NOW %d, BEFORE %d of %d" % (
    diffcount(nowf(a), bef(a), KHPOOL), holds(NOWR, a, KHPOOL), holds("23.2", a, KHPOOL), len(KHPOOL)))
a = lambda: W(ALT(W(Pat(Bd), lab_l(lambda v: num(v) and int(v) > 50)), Pat(Ad)), lab_l(lt(10)))
nv = lambda: W(alt_BA(), lab_l(lambda v: num(v) and int(v) > 50), lab_l(lt(10)))
print("D D9 the table picture: a condition written in a branch filters only that branch's rows; NAIVE filtering (every condition on every row) vs the engine, `((B & (l: >50)) | A) & (l: <10)`: %s" % diffcount(nowf(nv), nowf(a), DIG4))
a = lambda: W(FirstRow(alt_BA()), lab_l(lt(20))); b = lambda: W(Atom(alt_BA()), lab_l(lt(20)))
print("D D9 atomic = 'the first row BEFORE the filter', a condition OUTSIDE: `first(B | A) & (l: <20)` vs `atomic(B | A) & (l: <20)`: %s" % diffcount(nowf(a), nowf(b), DSP))
a = lambda: FirstRow(W(Pat(PABp), C("a", eq("1")))); b = lambda: Atom(W(Pat(PABp), C("a", eq("1"))))
print("D D9 the same with the condition INSIDE: `first(P & (a: \"1\"))` vs `atomic(P & (a: \"1\"))`: %s" % diffcount(nowf(a), nowf(b), DSP))
a = lambda: W(AND(Pat(r"(?:(?P<h>\d);)+"), Pat(r"\d;")), h5()); b = lambda: W(Pat(r"(?P<h>\d);"), h5())
print("D D10 repeated-means: `/(?:(?<h>\\d);)+/ & /\\d;/` vs `/(?<h>\\d);/`, each `& (h: <5)`: NOW %s ; BEFORE %s" % (diffcount(nowf(a), nowf(b), RG3), diffcount(bef(a), bef(b), RG3)))
a = lambda: W(Pat(REP1p), h5())
print("D D11 last-pass-default moves: `/(?:(?<h>\\d);)*/ & (h: <5)` NOW vs BEFORE: %s" % diffcount(nowf(a), bef(a), RG3))
a = lambda: W(KH(), ANDC(h5(), pk()))
print("D D11 the pairing example `KH & (h: <5, k: between(3, 7))` NOW vs BEFORE: %s" % diffcount(nowf(a), bef(a), KHPOOL))

def labkey(row, labs): return tuple((l, tuple(hitlist(row)) if l == "#hits" else row.last.get(l)) for l in labs)
def candf(ctx, mk, labs):
    """(mode, text) -> the answer WITH the candidate's labels (the reported row's labels are part of what is compared)."""
    cache = {}
    def f(m, s):
        with ctx():
            if "p" not in cache: cache["p"] = mk()
            Pn = cache["p"]
            if m == "WHOLE":                            # FIX-A5: the WHOLE key carries the labels
                r = whole_row(Pn, s); return None if r is None else labkey(r, labs)
            if m == "SEARCHED":
                r = search(Pn, s); return None if r is None else (r[0], r[1], labkey(r[2], labs))
            return tuple((a, b, labkey(rw, labs)) for a, b, rw in findall(Pn, s))
    return f
def fmtl(s, m, k):
    lv = lambda kv: "".join(" %s=%s" % (l, ("[" + ",".join(v) + "]") if isinstance(v, tuple) else v) for l, v in kv)
    if m == "WHOLE": return "FAILS" if k is None else "HOLDS" + lv(k)
    one = lambda x: "`%s`@%d%s" % (s[x[0]:x[1]], x[0], lv(x[2]))
    if m == "SEARCHED": return "FAILS" if k is None else one(k)
    return "[" + ", ".join(one(x) for x in k) + "]"
def diffl(f1, f2, pool):
    out = []
    for m in ("WHOLE", "SEARCHED", "FIND-ALL"):
        d = [s for s in order(pool) if f1(m, s) != f2(m, s)]
        if d:
            w = min(d, key=lambda x: (len(x), x))
            out.append("%s %d (first `%s`: %s vs %s)" % (m, len(d), w, fmtl(w, m, f1(m, w)), fmtl(w, m, f2(m, w))))
        else: out.append("%s 0" % m)
    return "; ".join(out) + " of %d (labels compared)" % len(pool)
# ---- rev 24.1 additions (review r40): the kept sentences A6, A8, A9 and C5 name, re-run under rev 24's rules
def l100(r):
    gt10 = lambda v: num(v) and int(v) > 10
    with rules(r):
        pab, pa, pb = W(Pat(PABp), C("a", lt(5)), C("a", gt10)), W(Pat(PABp), C("a", lt(5))), W(Pat(PABp), C("a", gt10))
        xs = [t for t in DIG4 if keyW(pab, t) != (keyW(pa, t) and keyW(pb, t))]
    return "%d of %d%s" % (len(xs), len(DIG4), (" (first `%s`)" % min(xs, key=lambda x: (len(x), x))) if xs else "")
print("D D12 (r40 A8, L100) `P & A & B` vs 'P & A holds and P & B holds', P := /(?<a>\\d+)(?<b>\\d+)/, A := `(a: <5)`, B := `(a: >10)`, WHOLE: NOW %s ; BEFORE %s" % (l100(NOWR), l100("23.2")))
RX = lambda: Pat(ABXYp)
a = lambda: OCC(W(RX(), C("g", eq("x"))), 1); b = lambda: W(OCC(RX(), 1), C("g", eq("x")))
print("D D13 (r40 A8, L61) `contains(r & (g: \"x\"))` vs `contains(r) & (g: \"x\")`, r := /ab(?<g>[xy])/: NOW %s ; BEFORE %s" % (diffcount(nowf(a), nowf(b), XYPOOL), diffcount(bef(a), bef(b), XYPOOL)))
with rules(NOWR):
    print("D D13 (L58) `contains(r) & (g: \"x\")` on `abx aby`: NOW WHOLE %s ; SEARCHED %s" % (aW(b(), "abx aby"), aS(b(), "abx aby", ("g",))))
with rules("23.2"):
    print("D D13 (L58) the same, BEFORE: WHOLE %s ; SEARCHED %s" % (aW(b(), "abx aby"), aS(b(), "abx aby", ("g",))))
def when_cbody(c):
    return lambda: ALT(W(KH(), c(), pk()), D(KH(), W(KH(), c())))
for nm, c in (("`(h: <5)`", h5), ("`(h = 0: <5)`", lambda: C("h", lt(5), h="0"))):
    a = when_cbody(c); b = lambda c=c: W(KH(), NOT(c())); b2 = lambda c=c: WHEN(KH(), c(), pk())
    nb = lambda c=c: ALT(W(KH(), c(), pk()), W(KH(), NOT(c())))
    print("D D14 (r40 A8, §8) `when` with c = %s: the complement body `(x & c & p) | (x & !(x & c))` vs the NOT body `(x & c & p) | (x & NOT c)`: NOW %s" % (nm, diffcount(nowf(a), nowf(nb), KHPOOL)))
    print("D D14   the complement body vs R.1.10's `x & (NOT c | p)`: NOW %s ; WHOLE holds: complement body %d, R.1.10 %d of %d (BEFORE: complement body %d)" % (
        diffcount(nowf(a), nowf(b2), KHPOOL), holds(NOWR, a, KHPOOL), holds(NOWR, b2, KHPOOL), len(KHPOOL), holds("23.2", a, KHPOOL)))
def labdiff(f1, f2, pool): return diffl(f1, f2, pool)
SVn = lambda: Pat(SVp)
for tag, nm, mka, mkb, pool, labs in (
        ("D15", "(r40 A9, §7.1) `NOT (h = 9: <5)` vs `NOT (h: <5)` on /(?<h>\\d)?x/", lambda: W(SVn(), NOT(C("h", lt(5), h="9"))), lambda: W(SVn(), NOT(h5())), SVPOOL, ("h",)),
        ("D15", "(§7.1) REP `NOT (h = \"x\": <5)` vs `NOT (h: <5)`", lambda: W(REP(), NOT(C("h", lt(5), h="x"))), lambda: W(REP(), NOT(h5())), RG3, ("h",)),
        ("D15", "(§7.1) REP `(h: <5)` vs `NOT some(NOT (h: <5))`", lambda: W(REP(), h5()), lambda: W(REP(), NOT(SOME(NOT(h5())))), RG3, ("h",)),
        ("D15", "(positive control) `(h = 9: <5)` vs `(h: <5)` on /(?<h>\\d)?x/", lambda: W(SVn(), C("h", lt(5), h="9")), lambda: W(SVn(), h5()), SVPOOL, ("h",)),
        ("D16", "(r40 A8, L30 empty S) `NOT (h: <0)` vs `(h: !<0)` on /(?<h>\\d)?x/", lambda: W(SVn(), NOT(C("h", lt(0)))), lambda: W(SVn(), C("h", lambda v: not lt(0)(v))), SVPOOL, ("h",)),
        ("D16", "(L30 full S) `NOT (h: <10)` vs `(h: !<10)` on /(?<h>\\d)?x/", lambda: W(SVn(), NOT(C("h", lt(10)))), lambda: W(SVn(), C("h", lambda v: not lt(10)(v))), SVPOOL, ("h",)),
        ("D16", "(L30 empty S, REP) `NOT (h: <0)` vs `(h: !<0)`", lambda: W(REP(), NOT(C("h", lt(0)))), lambda: W(REP(), C("h", lambda v: not lt(0)(v))), RG3, ("h",)),
        ("D19", "(r40 A6 (b), the dead branch) `/(?<a>\\d)|(?<b>\\d)/ & (b: \"1\")` vs `/(?<a>\\d)/ & (b: \"1\")`", lambda: W(ALT(Pat(r"(?P<a>\d)"), Pat(r"(?P<b>\d)")), C("b", eq("1"))), lambda: W(Pat(r"(?P<a>\d)"), C("b", eq("1"))), DIG4, ("a", "b")),
        ("D19", "(the same two patterns, no condition)", lambda: ALT(Pat(r"(?P<a>\d)"), Pat(r"(?P<b>\d)")), lambda: Pat(r"(?P<a>\d)"), DIG4, ("a", "b")),
        ("D21", "(r40 C5, L95) `t2 & !q` vs `t2 & ((h, m = 0): !R)`, R := `>= (9, 30)`", lambda: D(mk_t2(), mk_q()), lambda: W(mk_t2(), C(("h", "m"), lambda h, m: not late(h, m), m="0")), TP5, ("h", "m"))):
    f = lambda mk, r: candf(lambda r=r: rules(r), mk, labs)
    print("D %s %s: NOW %s ; BEFORE %s" % (tag, nm, diffl(f(mka, NOWR), f(mkb, NOWR), pool), diffl(f(mka, "23.2"), f(mkb, "23.2"), pool)))
MN = r"(?P<mname>Jan|Feb|Mar)?-(?P<d>\d)"
mnum = lambda f: C("mname", lambda v: f(("Jan", "Feb", "Mar").index(v) + 1))
for r in (NOWR, "23.2"):
    with rules(r):
        Pn = W(Pat(MN), NOT(mnum(lambda n: n < 3)))
        print("D D17 (r40 A8, §4.4) `mnum := $mname.index` over /(?<mname>Jan|Feb|Mar)?-(?<d>\\d)/, `NOT (mnum: <3)` on `-5` (mnum absent with mname), rules %s: WHOLE %s ; SEARCHED %s" % (r, aW(Pn, "-5"), aS(Pn, "-5")))
for nm, mkp, mkc in (("`atomic((B & (l: <20)) | A) & (l: <20)` over `atomic(B | A) & (l: <20)` (a condition INSIDE an atomic part, r40 A6 (a))",
                      lambda: W(Atom(alt_BA()), lab_l(lt(20))), lambda: W(Atom(ALT(W(Pat(Bd), lab_l(lt(20))), Pat(Ad))), lab_l(lt(20)))),
                     ("`/(?=(?<x>\\d+))\\d/ & (x: \"1\")` over `/(?=(?<x>\\d+))\\d/` (a lookahead)", lambda: Pat(r"(?=(?P<x>\d+))\d"), lambda: W(Pat(r"(?=(?P<x>\d+))\d"), C("x", eq("1"))))):
    print("D D18 adding a condition admits a text: %s: NOW %s" % (nm, admits(NOWR, mkp, mkc, DIG4)))
# C2: a `records` item (§7): compile-time, condition-free, never re-entered: the one-pattern loop's first path vs
# the committed find-all, hit lists compared
def hitsof(mk, s):
    with rules(NOWR):
        rw = whole_row(mk(), s); return None if rw is None else hitlist(rw)
xs = [t for t in DSP if hitsof(lambda: OCC(Pat(r"\d+")), t) != hitsof(lambda: Committed(Pat(r"\d+")), t)]
print("D D20 (r40 C2) a `records` item, condition-free: the one-pattern model's first WHOLE path vs the committed find-all, hit lists: %d of %d differ" % (len(xs), len(DSP)))

# ================================================================================================= PART E: the open table
# Each item left open (the manager's readings and the told-not-ruled items): every candidate on a WHOLE value, a
# SEARCHED text and a several-match subject (FIND-ALL), and the texts on which each candidate differs from the first
# (the draft's reading) over a set. A candidate is a program plus the rules it runs under.
print("== PART E: the open items, every candidate run (the first candidate is the draft's reading)")
@contextlib.contextmanager
def kleene():
    """rev 24's rules except the logic: Kleene three-valued (the retired reading), for set-once labels only."""
    with rules(NOWR):
        old = LP["MODE"]["v"]; LP["MODE"]["v"] = "T3"
        try: yield
        finally: LP["MODE"]["v"] = old
@contextlib.contextmanager
def now(): 
    with rules(NOWR): yield
def ecase(tag, slug, desc, cands, labs, texts, pool):
    print("E %s **%s** %s" % (tag, slug, desc))
    fs = []
    for nm, ctx, mk in cands:
        with ctx():
            Pn = mk()
            print("E %s   %s: WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (tag, nm, texts[0], aW(Pn, texts[0]), texts[1], aS(Pn, texts[1], labs), texts[2], aF(Pn, texts[2], labs)))
        fs.append((nm, candf(ctx, mk, labs)))
    for nm, f in fs[1:]:
        print("E %s   %s vs %s: %s" % (tag, fs[0][0], nm, diffl(fs[0][1], f, pool)))
UN = lambda: W(Pat(UPp), NOT(C("a", lt(5))))
ecase("E1", "three-valued (retired: the manager's reading)", "`/(?<b>\\d+)(?<a>\\d)?/ & NOT (a: <5)`",
      [("two-valued", now, UN), ("Kleene three-valued", kleene, UN)], ("a", "b"), ("1", "1", "1 12 19 3"), DSP)
JN = lambda: W(mk_t2(), NOT(C(("h", "m"), lambda h, m: num(h) and num(m) and int(h) < 9 and int(m) < 30)))
RN = lambda: W(mk_t2(), NOT(ANDC(C("h", lt(9)), C("m", lt(30)))))
ecase("E2", "record-under-not (dissolved: the manager's reading)", "the joint `t2 & NOT ((h, m): (<9, <30))` and the record `t2 & NOT (h: <9, m: <30)`",
      [("joint, two-valued", now, JN), ("record, two-valued", now, RN), ("joint, Kleene", kleene, JN), ("record, Kleene", kleene, RN)], ("h", "m"), ("10", "10", "10 9 10:15"), TP5)
OR_ = lambda: W(Pat(AHp), NOT(ORC(h5(), C("k", lt(5)))))
ecase("E3", "condition-or (deleted: one `|`; the manager's reading)", "`/a(?<h>\\d)|b(?<k>\\d)|c/ & NOT ((h: <5) | (k: <5))`",
      [("one `|` (two-valued; = an alternation of two tests)", now, OR_), ("Kleene OR", kleene, OR_)], ("h", "k"), ("b7", "b7", "b7 a3 c"), AHPOOL)
ecase("E4", "hits-committed (the manager's reading)", "every hit of `/(?<n>\\d+)/` under 100",
      [("committed hits (H1): `hits(/(?<n>\\d+)/) & some((n: <100)) & occurs.none(NOT (n: <100))`", now, lambda: W(Committed(Pat(NUMp)), SOME(C("n", lt(100))), NONE(NOT(C("n", lt(100)))))),
       ("one pattern (H2): `occurrences(/(?<n>\\d+)/) & some((n: <100)) & occurs.none(NOT (n: <100))`", now, lambda: W(OCC(Pat(NUMp)), SOME(C("n", lt(100))), NONE(NOT(C("n", lt(100)))))),
       ("the condition inside: `occurrences(/(?<n>\\d+)/ & (n: <100), min = 1)`", now, lambda: OCC(NN(), 1))],
      ("#hits",), ("1234", "x300 12", "1234 5 300"), OCCPOOL)
ecase("E5", "join-order (left side's paths outer: the manager's reading)", "`(P & Q) & ((a: \"1\") | (c: \"1\"))`, Q := /(?<c>\\d+)(?<d>\\d+)/",
      [("left outer", now, lambda: W(AND(Pat(PABp), Pat(PCDp)), ORC(C("a", eq("1")), C("c", eq("1"))))),
       ("right outer", now, lambda: W(AND(Pat(PCDp), Pat(PABp)), ORC(C("a", eq("1")), C("c", eq("1")))))],
      ("a", "b", "c", "d"), ("123", "123", "123 1121"), DSP)
ecase("E6", "polarity-rule (no error, no warning: the manager's reading; the answers do not depend on it)", "`t2 & NOT (h: <0)` (h is set in every match of t2) against plain `t2`",
      [("`t2 & NOT (h: <0)`", now, lambda: W(mk_t2(), NOT(C("h", lt(0))))), ("plain `t2`", now, mk_t2)], ("h",), ("9:30", "x9:30", "9:30 1"), TP5)
ecase("E6b", "polarity-rule, the complement form", "`t2 & !(t2 & (h: <0))` against plain `t2` (rev 23.2: a compile ERROR)",
      [("`t2 & !(t2 & (h: <0))`", now, lambda: D(mk_t2(), W(mk_t2(), C("h", lt(0))))), ("plain `t2`", now, mk_t2)], ("h",), ("9:30", "x9:30", "9:30 1"), TP5)
ecase("E7", "looped-warning (a WARNING when a bare condition reads a looped label: the manager's proposal; answers unaffected)", "`/(?:(?<h>\\d);)*/ & (h: <5)`",
      [("the bare condition (last pass)", now, lambda: W(Pat(REP1p), h5())), ("the every-pass spelling `/(?:${item})+/`", now, lambda: Rep(W(Pat(ITEM1), h5()), 1))],
      ("h",), ("7;3;", "7;3;", "7;3; 3;7;"), RG3)
ecase("E8", "sql-picture (the table holds every path, each row remembers its branch; filter, then the first row: the manager's restatement)", "`((B & (l: >50)) | A) & (l: <10)`",
      [("rows remember their branch (the engine)", now, lambda: W(ALT(W(Pat(Bd), lab_l(lambda v: num(v) and int(v) > 50)), Pat(Ad)), lab_l(lt(10)))),
       ("naive (every condition on every row)", now, lambda: W(alt_BA(), lab_l(lambda v: num(v) and int(v) > 50), lab_l(lt(10))))],
      ("l",), ("12", "12", "12 25 13"), DIG4)
ecase("E8b", "sql-picture: atomic = 'the first row before the filter'", "a condition inside the atomic part, `atomic(P & (a: \"1\"))`",
      [("PCRE's atomic group", now, lambda: Atom(W(Pat(PABp), C("a", eq("1"))))), ("the first row before the filter", now, lambda: FirstRow(W(Pat(PABp), C("a", eq("1")))))],
      ("a", "b"), ("123", "123", "123 9 112"), DSP)
ANYp = r"[\s\S]*"
ecase("E9", "complement-place (a lone complement in a WHOLE-value place)", "`!q` as a whole value (read as `/[\\s\\S]*/ & !q`); rev 23.2: a compile ERROR",
      [("whole-value reading", now, lambda: D(Pat(ANYp), mk_q()))], ("h",), ("9:30", "9", "9 9:30 10"), TP5)
print("E E9   (a SEARCHED lone `!q` has no reading: no pattern gives its stretch or its order; the candidates are the ERROR or the whole-value reading only)")
ecase("E10", "nested-complement", "`t2 & contains(t2 & !q)`",
      [("one pattern (H2)", now, lambda: AND(mk_t2(), OCC(D(mk_t2(), mk_q()), 1))), ("committed hits (H1)", now, lambda: AND(mk_t2(), Committed(D(mk_t2(), mk_q()), 1)))],
      ("#hits",), ("9:30", "9:30", "9:30 1"), TP5)
ecase("E11", "repeated-means", "`(h: <5)` on `/(?:(?<h>\\d);)+/ & /\\d;/` and on `/(?<h>\\d);/`",
      [("repeated (the operand regex)", now, lambda: W(AND(Pat(r"(?:(?P<h>\d);)+"), Pat(r"\d;")), h5())), ("set once", now, lambda: W(Pat(r"(?P<h>\d);"), h5()))],
      ("h",), ("3;", "7;3;", "3; 7;3;"), RG3)
ecase("E12", "group-truth / pass-table (now inside the named request)", "REP & `NOT some((h: <5))` and REP & `occurs.none(NOT (h: <5))`",
      [("`NOT some((h: <5))`", now, lambda: W(REP(), NOT(SOME(h5())))), ("`occurs.none((h: <5))`", now, lambda: W(REP(), NONE(h5()))),
       ("`occurs.none(NOT (h: <5))` (every pass, possibly none)", now, lambda: W(REP(), NONE(NOT(h5()))))],
      ("h",), (";", "7;;", "; 3;7;; 3;"), RG3)
LA = r"(?=[\s\S]*?\d\d:(?P<lm>\d\d))(?P<h>\d{1,2})(?::\d\d)?"
ecase("E13", "lookahead-labels", "`/(?=[\\s\\S]*?\\d\\d:(?<lm>\\d\\d))(?<h>\\d{1,2})(?::\\d\\d)?/ & (lm: >= 30)`",
      [("PCRE's: the lookahead's labels are the outer row's", now, lambda: W(Pat(LA), C("lm", ge(30)))),
       ("never visible outside", now, lambda: W(Strip(Pat(LA), ("lm",)), C("lm", ge(30))))],
      ("h", "lm"), ("10:45", "9:15 10:45", "9:15 10:45 11:20"), TP5)
ecase("E14", "atomic spelling (the meaning: PCRE's atomic group; predicates_future item 19)", "`atomic(B | A) & (l: <20)` against `(B | A) & (l: <20)`",
      [("atomic", now, lambda: W(Atom(alt_BA()), lab_l(lt(20)))), ("plain", now, lambda: W(alt_BA(), lab_l(lt(20))))], ("l",), ("25", "25", "25 13"), DSP)
ecase("E14b", "atomic: predicates_future item 14 (the pattern returns `9:30`, then the condition judges it)", "`atomic(t2) & !q` against `t2 & !q`",
      [("atomic", now, lambda: D(Atom(mk_t2()), mk_q())), ("plain", now, lambda: D(mk_t2(), mk_q()))], ("h", "m"), ("9:30", "9:30", "9:30 9:15"), TP5)
ecase("E15", "conditional spelling (the meaning: the library definitions)", "`KH & when((h: <5), (k: between(3, 7)), (k: <3))`",
      [("the else form `KH & (((h: <5) & p) | (NOT (h: <5) & (k: <3)))`", now, lambda: W(KH(), ORC(ANDC(h5(), pk()), ANDC(NOT(h5()), C("k", lt(3)))))),
       ("the two-argument form `KH & when((h: <5), p)`", now, lambda: WHEN(KH(), h5(), pk()))],
      ("k", "h"), ("5;1;9", "1;0;9", "1;0;9 5;1;9 2;7"), KHPOOL)

# ================================================================================================= PART Q: the owner questions
# Review r40's nine owner questions (the manager takes them to the owner). Each: the draft's current definition is the
# FIRST candidate where one exists (labelled THE DRAFT'S READING in the draft); each candidate's answers on a WHOLE
# value, a SEARCHED subject and a several-match subject; the texts on which each differs from the first, labels
# compared in every mode; and the earlier rulings' lines it touches, RE-RUN under each candidate. Nothing is chosen.
print("== PART Q: the owner questions of review r40, every candidate run (nothing chosen; the first candidate is the draft's current reading)")
REJ = "REJECTED (a compile error)"
def progf(mk, labs, ctx=None): return candf(ctx or now, mk, labs)
def rejf(modes=("WHOLE", "SEARCHED", "FIND-ALL"), base=None):
    def f(m, s): return REJ if m in modes else base(m, s)
    return f
def fmtq(s, m, k): return k if k == REJ else fmtl(s, m, k)
def qcase(slug, desc, cands, texts, pool):
    print("Q %s %s" % (slug, desc))
    for nm, f in cands:
        print("Q %s   %s: WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (slug, nm, texts[0], fmtq(texts[0], "WHOLE", f("WHOLE", texts[0])),
              texts[1], fmtq(texts[1], "SEARCHED", f("SEARCHED", texts[1])), texts[2], fmtq(texts[2], "FIND-ALL", f("FIND-ALL", texts[2]))))
    for nm, f in cands[1:]:
        out = []
        for m in ("WHOLE", "SEARCHED", "FIND-ALL"):
            d = [t for t in pool if cands[0][1](m, t) != f(m, t)]
            if d:
                w = min(d, key=lambda x: (len(x), x))
                out.append("%s %d (first `%s`: %s vs %s)" % (m, len(d), w, fmtq(w, m, cands[0][1](m, w)), fmtq(w, m, f(m, w))))
            else: out.append("%s 0" % m)
        print("Q %s   %s vs %s: %s of %d (labels compared)" % (slug, cands[0][0], nm, "; ".join(out), len(pool)))
def qline(slug, txt): print("Q %s   RE-RUN %s" % (slug, txt))

# 1. hits-text
H3P = lambda subj=False: W(Committed(Pat(NUMp), 0, subj), NONE(NOT(C("n", lt(100)))))
qcase("hits-text", "`hits(/(?<n>\\d+)/) & occurs.none(NOT (n: <100))` (H3): whose search are the hits?",
      [("THE DRAFT'S READING: the global search of the MATCHED STRETCH (re-run inside each stretch the pattern tries)", progf(H3P, ("#hits",))),
       ("the global search of the SUBJECT (its hits that lie inside the stretch)", progf(lambda: H3P(True), ("#hits",))),
       ("`hits` legal in WHOLE only (a SEARCHED or FIND-ALL program with `hits` is an error)", rejf(("SEARCHED", "FIND-ALL"), progf(H3P, ("#hits",))))],
      ("1234", "x300 12", "1234 5 300"), OCCPOOL)
for tag, mko, mkn, pool in (("W8", lambda: W(OCC(Pat(NUMp)), C("n", lt(100))), lambda: W(Committed(Pat(NUMp), 0, True), SOME(C("n", lt(100))), NONE(NOT(C("n", lt(100))))), OCCPOOL),
                            ("W9", lambda: W(OCC(Pat(ABXYp)), C("g", eq("x"))), lambda: W(Committed(Pat(ABXYp), 0, True), SOME(C("g", eq("x"))), NONE(NOT(C("g", eq("x"))))), XYPOOL)):
    qline("hits-text", "%s (the old meaning, rev 23.2) against its rev 24 spelling with the SUBJECT's hits: %s (the draft's reading: PART B %s, 0)" % (tag, diffcount(under("23.2", mko), under("24", mkn), pool), tag))
# 2. atomic-search
def firststart(mk_inner, mk_full, labs):
    cache = {}
    def srch(Pi, Pf, s, pos):
        for i in range(pos, len(s) + 1):
            if any(True for _ in acc_iter(Pi, s, i)):
                for e, row in acc_iter(Pf, s, i): return i, e, row
                return None
        return None
    def f(m, s):
        with now():
            if "p" not in cache: cache["p"] = (mk_inner(), mk_full())
            Pi, Pf = cache["p"]
            if m == "WHOLE":
                r = whole_row(Pf, s); return None if r is None else labkey(r, labs)
            if m == "SEARCHED":
                r = srch(Pi, Pf, s, 0); return None if r is None else (r[0], r[1], labkey(r[2], labs))
            out, pos = [], 0
            while pos <= len(s):
                r = srch(Pi, Pf, s, pos)
                if r is None: break
                out.append((r[0], r[1], labkey(r[2], labs))); pos = r[1] if r[1] > r[0] else r[1] + 1
            return tuple(out)
    return f
qcase("atomic-search", "`atomic(t2) & !q` (predicates_future item 14): what does atomic do in a search?",
      [("THE DRAFT'S READING: PCRE's atomic group (regex-settles (5)): no retry inside, the search moves to the next start", progf(lambda: D(Atom(mk_t2()), mk_q()), ("h", "m"))),
       ("stop at the first match start: where the atomic part first matches, the condition judges that match; if it fails there the search ends", firststart(lambda: Atom(mk_t2()), lambda: D(Atom(mk_t2()), mk_q()), ("h", "m")))],
      ("9:30", "9:30", "9:30 9:15"), TP5)
f1 = progf(lambda: W(Atom(alt_BA()), lab_l(lt(20))), ("l",)); f2 = firststart(lambda: Atom(alt_BA()), lambda: W(Atom(alt_BA()), lab_l(lt(20))), ("l",))
qline("atomic-search", "B8 `atomic(B | A) & (l: <20)` (regex-settles (5)) under the first-start candidate: %s" % diffl(f1, f2, DSP))
f1 = progf(lambda: Atom(W(Pat(PABp), C("a", eq("1")))), ("a", "b")); f2 = firststart(lambda: Atom(W(Pat(PABp), C("a", eq("1")))), lambda: Atom(W(Pat(PABp), C("a", eq("1")))), ("a", "b"))
qline("atomic-search", "B9 `atomic(P & (a: \"1\"))` (a condition INSIDE) under the first-start candidate: %s" % diffl(f1, f2, DSP))
# 3. joint-last-pass
class LastPassTest:
    """A joint read on the LAST PASS's own values (a label that pass did not set is absent there)."""
    def __init__(self, labs, pred): self.labs, self.pred = labs, pred
    def ev(self, row, view=None):
        lps = set(row.loop.get(l) for l in self.labs if row.loop.get(l) is not None)
        if len(lps) != 1: return False
        ps = row.passes.get(lps.pop(), [])
        if not ps: return False
        vals = [ps[-1].get(l) for l in self.labs]
        return None not in vals and bool(self.pred(*vals))
JPOOL = lists(["9:45,", "10,", "10:45,", "9,"], 3)
jeq = lambda h, m: (h, m) == ("10", "45")
JJ = lambda: C(("h", "m"), jeq)
qcase("joint-last-pass", "`CLOSE & ((h, m): == (10, 45))`, CLOSE := /(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*/: a joint over a loop",
      [("THE DRAFT'S READING: each label's last setting (PCRE's capture state; possibly from different passes)", progf(lambda: W(Pat(CLOSEp), JJ()), ("h", "m"))),
       ("the last pass's own tuple (a label it did not set is absent)", progf(lambda: W(Pat(CLOSEp), LastPassTest(("h", "m"), jeq)), ("h", "m"))),
       ("some pass holds the tuple (`some(J)`)", progf(lambda: W(Pat(CLOSEp), SOME(JJ())), ("h", "m"))),
       ("every pass, at least one (rev 23.2's per-pass pairing, `some(J) & occurs.none(NOT J)`)", progf(lambda: W(Pat(CLOSEp), SOME(JJ()), NONE(NOT(JJ()))), ("h", "m")))],
      ("9:45,10,", "10,9:45,", "9:45,10, 10:45,"), JPOOL)
rxj = P.Pcre(r'(?:(?<h>\d+)(?::(?<m>\d\d))?,)*(?C"j")', {"j": lambda c: jeq(c.get("h"), c.get("m"))})
qline("joint-last-pass", "the draft's reading against libpcre2 `/(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*(?C)/` (the callout tests the joint): %s" % diffl(rxkey(rxj, ("h", "m")), enkey(lambda: W(Pat(CLOSEp), JJ()), ("h", "m")), JPOOL).replace(" (labels compared)", ""))
# 4. hits-committed: PART E E4 (the named all-hits request, committed vs one pattern) and PART B's W8-bare control
f1 = under("23.2", lambda: W(OCC(Pat(ABXYp)), C("g", eq("x")))); f2 = under("24", lambda: W(OCC(Pat(ABXYp)), SOME(C("g", eq("x"))), NONE(NOT(C("g", eq("x"))))))
qline("hits-committed", "W9's old meaning against its spelling over the ONE-PATTERN hits (the candidate that drops the committed list): %s" % diffcount(f1, f2, XYPOOL))
# 5. join-order
G_, L_ = lambda: Pat(r"(?P<a>\d+)"), lambda: Pat(r"(?P<c>\d+?)")
qcase("join-order", "`G & L`, G := /(?<a>\\d+)/, L := /(?<c>\\d+?)/ (a LAZY right operand)",
      [("THE DRAFT'S READING: the left side's paths outer", progf(lambda: AND(G_(), L_()), ("a", "c"))),
       ("the right side's paths outer", progf(lambda: AND(L_(), G_()), ("a", "c")))],
      ("11", "11", "11 123"), DSP)
X_, B_, A_ = lambda: Pat(r"\d+"), lambda: Pat(r"\d"), lambda: Pat(r"\d\d")
for nm, sw in (("left outer", False), ("right outer", True)):
    j = (lambda a, b: AND(b, a)) if sw else (lambda a, b: AND(a, b))
    qline("join-order", "(%s) `X & (B | A)` vs `(X & B) | (X & A)`, X := /\\d+/, B := /\\d/, A := /\\d\\d/ (`&` distributing over a `|` on the RIGHT): %s" % (nm,
        diffcount(nowf(lambda: j(X_(), ALT(B_(), A_()))), nowf(lambda: ALT(j(X_(), B_()), j(X_(), A_()))), DSP)))
    qline("join-order", "(%s) `(B | A) & X` vs `(B & X) | (A & X)` (a `|` on the LEFT): %s" % (nm,
        diffcount(nowf(lambda: j(ALT(B_(), A_()), X_())), nowf(lambda: ALT(j(B_(), X_()), j(A_(), X_()))), DSP)))
    qline("join-order", "(%s) the LAW with a lazy B: `/(?<l>\\d+)/ & /\\d+?/` vs `/(?<l>\\d+)/ & (0: /\\d+?/)`: %s" % (nm,
        diffcount(nowf(lambda: j(Pat(r"(?P<l>\d+)"), Pat(r"\d+?"))), nowf(lambda: ZERO(Pat(r"(?P<l>\d+)"), Pat(r"\d+?"))), DSP)))
# 6. polarity-rule
T2N = lambda: W(mk_t2(), NOT(C("h", lt(0))))
qcase("polarity-rule", "`t2 & NOT (h: <0)`: a test that can never pass, under NOT (always TRUE)",
      [("THE DRAFT'S READING (the manager's 13:25): no error, no warning", progf(T2N, ("h",))),
       ("a WARNING (the answers as the draft's)", progf(T2N, ("h",))),
       ("the §5.2 ERROR at every polarity (as `t2 & (h: <0)` without NOT)", rejf())],
      ("9:30", "x9:30", "9:30 1"), TP5)
qline("polarity-rule", "E6/E6b: the draft's reading equals plain `t2` (PART E). Without NOT, `t2 & (h: <0)` is the §5.2 ERROR under every candidate")
# 7. exception-rule
qcase("exception-rule", "H3 `hits(/(?<n>\\d+)/) & occurs.none(NOT (n: <100))` (the hit list of an rx whose hit list is NOT proven regular, lane rxmodel)",
      [("(B) asked for by name (13:30 (B); the draft's reading as rev 24 printed it)", progf(H3P, ("#hits",))),
       ("(A) proven or not offered: the hit list of `\\d+` is unproven, so `hits` is not offered", rejf()),
       ("both: proven, OR asked for by name (the manager's lean)", progf(H3P, ("#hits",)))],
      ("1234", "x300 12", "1234 5 300"), OCCPOOL)
W9N = lambda: W(Committed(Pat(ABXYp)), SOME(C("g", eq("x"))), NONE(NOT(C("g", eq("x")))))
qcase("exception-rule", "W9 `hits(/ab(?<g>[xy])/) & some((g: \"x\")) & occurs.none(NOT (g: \"x\"))` (a hit list proven regular, lane lastpass: 0 of 85)",
      [("(B) asked for by name", progf(W9N, ("#hits",))), ("(A) proven", progf(W9N, ("#hits",))), ("both", progf(W9N, ("#hits",)))],
      ("abx", "abx aby", "abxabx aby abx"), XYPOOL)
# 8. pass-list-read
PLp = r"(?:(?P<h>\d);)*(?P<k>\d)"
qcase("pass-list-read", "`/(?:(?<h>\\d);)*(?<k>\\d)/ & (k: == $h)`: what a bare `$h` reads on a value side when h is looped",
      [("THE DRAFT'S READING: `$h` is the PASS LIST (§R.4's `sorted`/`distinct` read it); comparing k with a list has no stated meaning", rejf()),
       ("the last pass, as regex's `\\k<h>` (last-pass-default's rule for a bare `h:` applied to `$h`)", progf(lambda: W(Pat(PLp), C(("k", "h"), lambda k, h: k == h)), ("h", "k"))),
       ("the pass list, k equal to SOME pass", progf(lambda: W(Pat(PLp), SOME(C(("h", "k"), lambda h, k: h == k))), ("h", "k"))),
       ("the pass list, k equal to EVERY pass (at least one)", progf(lambda: W(Pat(PLp), SOME(C(("h", "k"), lambda h, k: h == k)), NONE(NOT(C(("h", "k"), lambda h, k: h == k)))), ("h", "k")))],
      ("3;7;7", "3;7;3", "3;7;7 7;3;3"), RG3)
rxb = P.Pcre(r'(?:(?<h>\d);)*(?<k>\k<h>)')
qline("pass-list-read", "the last-pass candidate against libpcre2's backreference `/(?:(?<h>\\d);)*(?<k>\\k<h>)/`: %s" % diffl(rxkey(rxb, ("h", "k")), enkey(lambda: W(Pat(PLp), C(("k", "h"), lambda k, h: k == h)), ("h", "k")), RG3).replace(" (labels compared)", ""))
# 9. zero-place
class OccG0(OccS):
    """`occurrences(A & (0: B))` with `0` read as PCRE's group 0: B whole on the text from the PROGRAM's match start
    to the hit's end (not the hit)."""
    def __init__(self, A, B, mn=0):
        OccS.__init__(self, A, mn); self.B = B
        self.hit_ok = lambda s, i, g, e: whole_row(self.B, s[i:e]) is not None
qcase("zero-place", "`occurrences(/\\d+/ & (0: /1\\d*/), min = 1)`: what `0` names inside a nested place",
      [("THE LAW's twin `occurrences(/\\d+/ & /1\\d*/, min = 1)` (the reference: `&` on the hit's stretch)", progf(lambda: OCC(AND(Pat(r"\d+"), Pat(r"1\d*")), 1), ("#hits",))),
       ("`0` = the innermost stretch (the hit)", progf(lambda: OCC(ZERO(Pat(r"\d+"), Pat(r"1\d*")), 1), ("#hits",))),
       ("`0` = PCRE's group 0 (the program's match start to here)", progf(lambda: OccG0(Pat(r"\d+"), Pat(r"1\d*"), 1), ("#hits",)))],
      (" 1", " 1", " 1 12"), DSP)
rxg0 = P.Pcre(r'(?:[\s\S]*?\d+(?C"z"))+[\s\S]*', {"z": lambda c: re.fullmatch(r"1\d*", c.subject[c.start:c.pos]) is not None})
qline("zero-place", "the group-0 candidate against libpcre2 `/(?:[\\s\\S]*?\\d+(?C))+[\\s\\S]*/` (the callout tests `/1\\d*/` whole on subject[start_match:current_position]), holding and stretch: %s" % diffcount(
    lambda m, t: (lambda k: (k is not None) if m == "WHOLE" else (None if k is None else k[:2]) if m == "SEARCHED" else tuple(x[:2] for x in k))(rxkey(rxg0, ())(m, t)),
    under(NOWR, lambda: OccG0(Pat(r"\d+"), Pat(r"1\d*"), 1)), DSP))
qline("zero-place", "at the top level the two candidates are one (group 0 is the stretch): D5's LAW lines")
# 10. the C2 records model: no question (D20: 0 differ; the item is condition-free and its result is a value)
# 11. pass-own-labels (rulings R2, the owner's "could you use defaults m=00"): does a loop pass start with its body's
# labels UNSET? THE DRAFT'S READING: no, PCRE's capture state (a label this pass did not set reads an earlier pass's
# value; after the loop each label reads its last setting). THE CANDIDATE: each pass starts with its body's labels
# unset (inside the body a label this pass did not set is absent, a default stands in; after the loop a label reads
# the LAST PASS's own value, absent when that pass did not set it).
_Tev = LP["Test"].ev
def _ev_passown(self, row, view=None):
    if PASSOWN["v"] and view is None and LP["MODE"]["v"] == "R" and any(row.loop.get(l) is not None for l in self.labs):
        def get(l):
            if row.loop.get(l) is None: return row.last.get(l)
            ps = row.passes.get(row.loop[l]) or []
            return ps[-1].get(l) if ps else None
        return self.one(get)
    return _Tev(self, row, view)
LP["Test"].ev = _ev_passown
@contextlib.contextmanager
def passown():
    with rules(NOWR):
        PASSOWN["v"] = True
        try: yield
        finally: PASSOWN["v"] = False
def pkey(ctx, mk):
    cache = {}
    def f(m, s):
        with ctx():
            if "p" not in cache: cache["p"] = mk()
            return KEYS[m](cache["p"], s)
    return f
ITEMC = r"(?P<h>\d+)(?::(?P<m>\d\d))?,"
JD = lambda: C(("h", "m"), jeq, m="00")
PO_TEXTS = ("9:45,10,", "10,9:45,", "10:45,10,")
for nm, mk in (("`CLOSE & ((h, m): == (10, 45))` (bare, after the loop)", lambda: W(Pat(CLOSEp), JJ())),
               ("`CLOSE & ((h, m = 00): == (10, 45))` (bare, a default)", lambda: W(Pat(CLOSEp), JD())),
               ("`CLOSE & ((h, m = 00): == (10, 00))` (bare, a default, the hour alone)", lambda: W(Pat(CLOSEp), C(("h", "m"), lambda h, m: (h, m) == ("10", "00"), m="00"))),
               ("`/(?:${item})*/`, item := `/(?<h>\\d+)(?::(?<m>\\d\\d))?,/ & ((h, m): == (10, 45))` (the joint on the item, inside the loop)", lambda: Rep(W(Pat(ITEMC), JJ()), 0)),
               ("`/(?:${item})*/`, item := `/(?<h>\\d+)(?::(?<m>\\d\\d))?,/ & ((h, m = 00): == (10, 45))` (inside, a default)", lambda: Rep(W(Pat(ITEMC), JD()), 0))):
    a, b = progf(mk, ("h", "m")), progf(mk, ("h", "m"), passown)
    print("Q pass-own-labels %s: WHOLE on %s: THE DRAFT'S READING (PCRE's capture state) %s ; PASS-OWN %s" % (nm, ", ".join("`%s`" % t for t in PO_TEXTS),
          ", ".join(fmtq(t, "WHOLE", a("WHOLE", t)) for t in PO_TEXTS), ", ".join(fmtq(t, "WHOLE", b("WHOLE", t)) for t in PO_TEXTS)))
    qcase("pass-own-labels", nm,
          [("THE DRAFT'S READING: PCRE's capture state (carry; the last setting)", a), ("a pass starts with its body's labels UNSET", b)],
          ("9:45,10,", "10,9:45,", "9:45,10, 10:45,10,"), JPOOL)
qline("pass-own-labels", "R13;; `REP & (h: <5)` (last-pass-default's \"a pass that sets nothing keeps the earlier value\"), carry vs pass-own: %s" % diffl(progf(lambda: W(REP(), h5()), ("h",)), progf(lambda: W(REP(), h5()), ("h",), passown), RG3))
qline("pass-own-labels", "the every-pass spelling with the OPTIONAL item (rev 24's W1c, item := `/(?<h>\\d)?;/ & (h: <5)`) against W1c's old meaning: carry %s ; pass-own %s" % (
    diffcount(under("23.2", lambda: W(REP(), h5())), under("24", lambda: Rep(W(Pat(ITEMO), h5()), 1)), RG3),
    diffcount(under("23.2", lambda: W(REP(), h5())), pkey(passown, lambda: Rep(W(Pat(ITEMO), h5()), 1)), RG3)))
qline("pass-own-labels", "W2a, a per-test default inside the loop (item := `/(?<h>\\d)?;/ & (h = 0: <5)`) against its old meaning: carry %s ; pass-own %s" % (
    diffcount(under("23.2", lambda: W(REP(), C("h", lt(5), h="0"))), under("24", lambda: Rep(W(Pat(ITEMO), C("h", lt(5), h="0")), 0)), RG3),
    diffcount(under("23.2", lambda: W(REP(), C("h", lt(5), h="0"))), pkey(passown, lambda: Rep(W(Pat(ITEMO), C("h", lt(5), h="0")), 0)), RG3)))
qline("pass-own-labels", "W1a (a MANDATORY label, every pass sets it): carry vs pass-own %s" % diffl(progf(lambda: Rep(W(Pat(ITEM1), h5()), 1), ("h",)), progf(lambda: Rep(W(Pat(ITEM1), h5()), 1), ("h",), passown), RG3))
qline("pass-own-labels", "joint-last-pass: the bare joint under pass-own vs the 'last pass's own tuple' candidate (carry rules): %s" % diffl(progf(lambda: W(Pat(CLOSEp), JJ()), ("h", "m"), passown), progf(lambda: W(Pat(CLOSEp), LastPassTest(("h", "m"), jeq)), ("h", "m")), JPOOL))
rxg1 = P.Pcre(r'(?:(?<h>\d)?;(?C"h<5"))+', CO)
qline("pass-own-labels", "G1 against libpcre2 (PCRE's carry) `/(?:(?<h>\\d)?;(?C))+/`: carry %s ; pass-own %s" % (
    diffl(rxkey(rxg1, ("h",)), progf(lambda: Rep(W(Pat(ITEMO), h5()), 1), ("h",)), RG3), diffl(rxkey(rxg1, ("h",)), progf(lambda: Rep(W(Pat(ITEMO), h5()), 1), ("h",), passown), RG3)))
# RAMIFICATIONS (rulings R3): the whole revision's worked lines run both ways
print("Q pass-own-labels RAMIFICATIONS (1): every worked line, PCRE's carry (the draft's reading) vs pass-own")
pa_moved = []
for tag, site, desc, mk, labs, texts, printed in CAT:
    with passown():
        Pn = mk(); po = (aW(Pn, texts[0]), aS(Pn, texts[1], labs), aF(Pn, texts[2], labs))
    if po != RES[tag]["NOW"]:
        pa_moved.append(tag)
        print("Q pass-own-labels   PART A %s [%s] MOVES: WHOLE `%s` %s -> %s ; SEARCHED `%s` %s -> %s ; FIND-ALL `%s` %s -> %s" % (tag, site, texts[0], RES[tag]["NOW"][0], po[0], texts[1], RES[tag]["NOW"][1], po[1], texts[2], RES[tag]["NOW"][2], po[2]))
print("Q pass-own-labels   PART A: %d of %d catalogue lines move (%s); %d do not" % (len(pa_moved), len(CAT), ", ".join(pa_moved), len(CAT) - len(pa_moved)))
pb_nz = []
for tag, what, old_, new_, mko, mkn, pool in WAYS:
    d = diffcount(under("23.2", mko), pkey(passown, mkn), pool)
    if not all(x.split(" ")[1] == "0" for x in d.split(" of ")[0].split("; ")): pb_nz.append(tag); print("Q pass-own-labels   PART B %s under pass-own against its old meaning: %s" % (tag, d))
print("Q pass-own-labels   PART B: %d of %d old-meaning spellings still at 0 under pass-own (%s differ)" % (len(WAYS) - len(pb_nz), len(WAYS), ", ".join(pb_nz) or "none"))
def sortk(f):
    """the engine's labelled key with its labels in rxkey's (sorted) order"""
    def g(m, t):
        k = f(m, t)
        if k is None: return None
        if m == "WHOLE": return tuple(sorted(k))
        if m == "SEARCHED": return (k[0], k[1], tuple(sorted(k[2])))
        return tuple((a, b, tuple(sorted(l))) for a, b, l in k)
    return g
pc_ne = []
for tag, nm, pat, mk, labs, pool in PCASES:
    rx = pat if isinstance(pat, SM) else P.Pcre(pat, CO)
    d = diffl(rxkey(rx, labs), sortk(progf(mk, labs, passown)), pool)
    if not all(x.split(" ")[1] == "0" for x in d.split(" of ")[0].split("; ")): pc_ne.append(tag); print("Q pass-own-labels   PART C %s: libpcre2 (carry) vs the engine under pass-own: %s" % (tag, d))
print("Q pass-own-labels   PART C: %d of %d libpcre2 models still equal under pass-own (%s differ)" % (len(PCASES) - len(pc_ne), len(PCASES), ", ".join(pc_ne) or "none"))
print("Q pass-own-labels RAMIFICATIONS (2): the constructs")
def both(nm, mk, labs, texts, pool):
    a, b = progf(mk, labs), progf(mk, labs, passown)
    print("Q pass-own-labels   %s: carry %s ; pass-own %s" % (nm, "; ".join("`%s` %s" % (t, fmtq(t, "WHOLE", a("WHOLE", t))) for t in texts), "; ".join("`%s` %s" % (t, fmtq(t, "WHOLE", b("WHOLE", t))) for t in texts)))
    print("Q pass-own-labels     carry vs pass-own: %s" % diffl(a, b, pool))
both("last-pass-default, bare `REP & (h: <5)` (WHOLE)", lambda: W(REP(), h5()), ("h",), ("3;;", "7;3;", "3;"), RG3)
both("last-pass-default, mandatory label `/(?:(?<h>\\d);)*/ & (h: <5)`", lambda: W(Pat(REP1p), h5()), ("h",), ("7;3;", "3;7;"), RG3)
both("a per-test default AFTER the loop, `REP & (h = 0: <5)`", lambda: W(REP(), C("h", lt(5), h="0")), ("h",), ("7;;", "3;;", "7;3;"), RG3)
both("a per-test default AFTER the loop, outside the set, `REP & (h = 9: <5)`", lambda: W(REP(), C("h", lt(5), h="9")), ("h",), ("3;;", "3;"), RG3)
both("a per-test default INSIDE the loop, `/(?:${item})+/`, item := `/(?<h>\\d)?;/ & (h = 9: <5)`", lambda: Rep(W(Pat(ITEMO), C("h", lt(5), h="9")), 1), ("h",), ("3;;", "3;"), RG3)
both("the every-pass spelling, OPTIONAL item (rev 24's W1c)", lambda: Rep(W(Pat(ITEMO), h5()), 1), ("h",), ("3;;", "3;7;"), RG3)
both("group questions over an optional label, `REP & some((h: <5)) & occurs.none(NOT (h: <5))` (W1d)", lambda: W(REP(), SOME(h5()), NONE(NOT(h5()))), ("h",), ("3;;", "3;"), RG3)
both("`REP & occurs.exactly(2, (h: <5))`", lambda: W(REP(), Count(h5(), lambda n: n == 2)), ("h",), ("3;;3;", "3;3;"), RG3)
both("an alternation in the body, `/(?:(?<a>\\d)|(?<b>[a-z]))*/ & (a: <5)`", lambda: W(Pat(r"(?:(?P<a>\d)|(?P<b>[a-z]))*"), C("a", lt(5))), ("a", "b"), ("3x", "x3", "3"), strings("37x", 5))
both("occurrences, a condition INSIDE (G2), `occurrences(/(?<x>(?<g>a)?b)/ & (g: \"a\"), min = 1)`", lambda: OCC(W(Pat(r"(?P<x>(?P<g>a)?b)"), C("g", eq("a"))), 1), ("x", "g"), ("abb", "ab"), ABP5)
both("occurrences, bare AFTER, `occurrences(/(?<x>(?<g>a)?b)/, min = 1) & (g: \"a\")`", lambda: W(OCC(Pat(r"(?P<x>(?P<g>a)?b)"), 1), C("g", eq("a"))), ("x", "g"), ("abb", "ab", "abab"), ABP5)
# nested loops and a label set before the loop: a direct WHOLE evaluator (each text has one parse), independent of the engine
def nest_parse(t):
    if t and not t.endswith(","): return None
    outs = t.split(",")[:-1] if t else []
    passes = []
    for o in outs:
        if o and not o.endswith(";"): return None
        ins = o.split(";")[:-1] if o else []
        if any(x not in ("", "3", "7") for x in ins): return None
        passes.append(ins)
    return passes
def nest_val(passes, cand):
    if passes is None: return "nomatch"
    if cand == "carry":
        v = [x for o in passes for x in o if x]; return v[-1] if v else None
    if cand == "inner":
        inner = [x for o in passes for x in o]; return inner[-1] or None if inner else None
    if cand == "every":
        if not passes or not passes[-1]: return None
        return passes[-1][-1] or None
NEST = r"(?:(?:(?P<h>\d)?;)*,)*"
NPOOL = strings("37;,", 5)
def nest_ans(cand, t):
    p = nest_parse(t)
    if p is None: return "FAILS"
    v = nest_val(p, cand); return "HOLDS h=%s" % v if (v is not None and int(v) < 5) else "FAILS h=%s" % v
eng_c, eng_p = progf(lambda: W(Pat(NEST), h5()), ("h",)), progf(lambda: W(Pat(NEST), h5()), ("h",), passown)
rxn = P.Pcre(r'(?:(?:(?<h>\d)?;)*,)*(?C"h<5")', CO)
dc = sum(1 for t in NPOOL if (rxn.match(t, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED) is not None) != nest_ans("carry", t).startswith("HOLDS"))
de = sum(1 for t in NPOOL if (eng_c("WHOLE", t) is not None) != nest_ans("carry", t).startswith("HOLDS"))
di = sum(1 for t in NPOOL if (eng_p("WHOLE", t) is not None) != nest_ans("inner", t).startswith("HOLDS"))
print("Q pass-own-labels   NESTED LOOPS `/(?:(?:(?<h>\\d)?;)*,)*/ & (h: <5)` (WHOLE; a direct evaluator, one parse per text): " + " ; ".join("`%s`: carry %s, innermost pass unsets %s, every enclosing pass unsets %s" % (t, nest_ans("carry", t), nest_ans("inner", t), nest_ans("every", t)) for t in ("3;,,", "3;;,", "3;,;,", "3;,7;,")))
print("Q pass-own-labels     counts of %d texts (holds): carry vs innermost %d; carry vs every %d; innermost vs every %d. CONTROLS: the direct carry vs libpcre2 %d; vs the engine %d; the direct innermost vs the engine's pass-own %d" % (len(NPOOL),
      sum(1 for t in NPOOL if nest_ans("carry", t)[:5] != nest_ans("inner", t)[:5]), sum(1 for t in NPOOL if nest_ans("carry", t)[:5] != nest_ans("every", t)[:5]), sum(1 for t in NPOOL if nest_ans("inner", t)[:5] != nest_ans("every", t)[:5]), dc, de, di))
def pre_ans(cand, t):
    if not re.fullmatch(r"\d?(?:;\d?)*", t): return "FAILS"
    segs = t.split(";"); before, passes = segs[0] or None, [x or None for x in segs[1:]]
    if cand == "carry": v = ([x for x in passes if x] or [before])[-1]
    else: v = passes[-1] if passes else before
    return "HOLDS h=%s" % v if (v is not None and int(v) < 5) else "FAILS h=%s" % v
PPOOL = strings("37;", 5)
print("Q pass-own-labels   A LABEL SET BEFORE THE LOOP AND INSIDE IT `/(?<h>\\d)?(?:;(?<h>\\d)?)*/ & (h: <5)` (duplicate names; WHOLE, a direct evaluator): " + " ; ".join("`%s`: carry %s, pass-own %s" % (t, pre_ans("carry", t), pre_ans("own", t)) for t in ("3", "3;", "3;7", "7;3;")) + " ; differ %d of %d" % (sum(1 for t in PPOOL if pre_ans("carry", t)[:5] != pre_ans("own", t)[:5]), len(PPOOL)))
try:
    P.Pcre(r'(?J)(?<h>\d)?(?:;(?<h>\d)?)*'); dn = "the harness reads it"
except ValueError as e:
    dn = "no libpcre2 control: PCRE2 compiles duplicate names under (?J), but the harness's by-name capture read refuses them (%s)" % e
print("Q pass-own-labels     %s" % dn)
print("Q pass-own-labels RAMIFICATIONS (3): regex models of pass-own")
rxe = P.Pcre(r'(?:(?<h>\d|);)*(?C"h<5")', CO)
rxe0 = P.Pcre(r'(?:(?<h>\d|);)*(?(<h>)(?C"h<5")|(?C"d0<5"))', CO)
def hs(rx): return lambda m, t: (lambda k: (k is not None) if m == "WHOLE" else (None if k is None else k[:2]) if m == "SEARCHED" else tuple(x[:2] for x in k))(rxkey(rx, ())(m, t))
print("Q pass-own-labels   (a) the empty alternative `/(?:(?<h>\\d|);)*/` (h set to the empty string each pass; a branch reset group `(?|(?<h>\\d)|())` is the same) with the test `(h: <5)`, holding and stretch, vs the engine's pass-own: %s" % diffcount(hs(rxe), pkey(passown, lambda: W(REP(), h5())), RG3))
print("Q pass-own-labels       the same with a default `(h = 0: <5)` (PCRE's conditional sees the empty h as SET, so the default never fires): %s" % diffcount(hs(rxe0), pkey(passown, lambda: W(REP(), C("h", lt(5), h="0"))), RG3))
def own_h(c):
    sh, sp = c.span("h"), c.span("ps")
    return None if (sh is None or sp is None or sh[0] < sp[0]) else c.subject[sh[0]:sh[1]]
rxm = P.Pcre(r'(?:(?<ps>)(?<h>\d)?;)*(?C"own")', {"own": lambda c: (lambda v: v is not None and int(v) < 5)(own_h(c))})
rxm0 = P.Pcre(r'(?:(?<ps>)(?<h>\d)?;)*(?C"own")', {"own": lambda c: (lambda v: int(v if v is not None else "0") < 5)(own_h(c))})
rxmi = P.Pcre(r'(?:(?<ps>)(?<h>\d)?;(?C"own"))+', {"own": lambda c: (lambda v: v is not None and int(v) < 5)(own_h(c))})
print("Q pass-own-labels   (b) a helper group marking each pass's start, `/(?:(?<ps>)(?<h>\\d)?;)*(?C)/`, the callout reading h only when it starts at or after ps (set in this pass), vs the engine's pass-own: bare %s ; with the default `h = 0` %s ; inside the body (W1c's item) %s" % (
    diffcount(hs(rxm), pkey(passown, lambda: W(REP(), h5())), RG3), diffcount(hs(rxm0), pkey(passown, lambda: W(REP(), C("h", lt(5), h="0"))), RG3), diffcount(hs(rxmi), pkey(passown, lambda: Rep(W(Pat(ITEMO), h5()), 1)), RG3)))
print("Q pass-own-labels     CONTROL: the same callout model against the engine's CARRY (must differ): %s" % diffcount(hs(rxm), pkey(now, lambda: W(REP(), h5())), RG3))


# ================================================================================================= PART F: whole-text
# The owner's model (2026-11-17 13:55, adopted if legal at 14:05): a parser J of the whole text; a check C against J's
# result that can fail the whole thing; a search M for the matches inside J's span; the matches reported only when C
# holds. Written with ruled pieces only: the program matched WHOLE (the caller's whole-value mode), `&` (one stretch),
# a condition or a label-free filter for C, `occurrences(M)` for M (its hits, the label `hit`, read as the hit list).
# Compared with the meaning the whole-text question asks (rev 23.2's route (ii): the matches of M, all of them when the
# text has no q, none otherwise).
print("== PART F: whole-text legality (J & C & occurrences(M), matched WHOLE)")
def route2(s):
    with rules(NOWR):
        if search(mk_q(), s) is not None: return None
        return [s[a:b] for a, b, _ in findall(mk_t2(), s)]
def jcm(mk):
    def f(s):
        with rules(NOWR):
            rw = whole_row(mk(), s)
            return None if rw is None else hitlist(rw)
    return f
T2Q = r"(?P<hh>\d{1,2})(?::(?P<mm>\d\d))?"
def late_hm(): return C(("h", "m"), late)
F1 = lambda: D(AND(Pat(ANYp), OCC(mk_t2())), OCC(mk_q(), 1))
F2 = lambda: W(AND(Pat(TMLp), OCC(Pat(T2Q))), NONE(late_hm()))
for tag, nm, mk, texts, pool in (("F1", "J := `/[\\s\\S]*/` (any text), C := `!contains(q)`, M := `occurrences(t2)`: `J & !contains(q) & occurrences(t2)`", F1, ("9:15 1", "9:30 1", "9 10:45", ""), TP5),
                                 ("F2", "J := TML (a comma list of times), C := `occurs.none(((h, m): >= (9, 30)))` on J's items, M := `occurrences(/(?<hh>\\d{1,2})(?::(?<mm>\\d\\d))?/)`", F2, ("9,9:15,", "9:15,9:45,", "10,", ""), TMPOOL)):
    print("F %s %s" % (tag, nm))
    for t in texts:
        r = jcm(mk)(t)
        print("F %s   WHOLE `%s`: %s ; route (ii)'s find-all: %s" % (tag, t, "FAILS" if r is None else "HOLDS, hits [%s]" % ", ".join("`%s`" % x for x in r), "none" if route2(t) is None else "[%s]" % ", ".join("`%s`" % x for x in route2(t))))
    d = [s for s in order(pool) if jcm(mk)(s) != route2(s)]
    print("F %s   texts where (holds, hits) differ from route (ii)'s (all matches or none): %d of %d%s" % (tag, len(d), len(pool), (" (first `%s`)" % min(d, key=lambda x: (len(x), x))) if d else ""))
# The SEARCHED form (each match of M reported as a match of the program, gated by C over the whole subject): the
# nearest ruled spelling, `t2 & !contains(q)`, reads the ROW's stretch, not the subject.
def r2key(m, s):
    r = route2(s)
    with rules(NOWR):
        hits = [] if r is None else findall(mk_t2(), s)
    if m == "WHOLE": return (r is not None) and whole_row(mk_t2(), s) is not None
    if m == "SEARCHED": return (hits[0][0], hits[0][1]) if hits else None
    return tuple((a, b) for a, b, _ in hits)
nc = under(NOWR, lambda: D(mk_t2(), OCC(mk_q(), 1)))
print("F F3 the SEARCHED form: `t2 & !contains(q)` vs route (ii) `t2 & text.none(q)` (a text-level test, not a ruled piece): %s" % diffcount(nc, r2key, TP5))

# ================================================================================================= summary
print("== SUMMARY: catalogue %d lines, MOVED %d; printed rev 23.2 answers %d, mismatches %d; old meanings %d rows, %d at 0; libpcre2 models %d, %d equal; order check %d of %d differ" % (
    len(CAT), len(moved), pchk, len(pmis), len(WAYS), zero, len(PCASES), pexact, sum(ocheck), len(ocheck)))
