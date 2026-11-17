#!/usr/bin/env python3
# Lane predspec24 (2026-11-17): the evidence engine of docs/design/predicates_draft.md REVISION 24. DESIGN EVIDENCE
# ONLY. Every worked example and count revision 24 states is printed here; the draft cites this file's output
# (predspec24_model.out) by line tag.
#
# THE RULES OF REV 24 (the owner's rulings of 2026-11-17, COND-FAMILY; the manager's readings marked READING):
#   branch-scope (ii)  a condition is one more piece of the pattern: a path survives when every condition on it holds;
#                      the pattern tries its paths in PCRE's order (`|` included); the report is the first survivor.
#   regex-settles      (1) a test on an absent label fails (the pattern tries its next path); (2) `!B` keeps a path
#                      when NO path of B survives over the same stretch; (3) a lookahead is never re-entered from
#                      outside (PCRE's atomic lookaround), a negative one tries every inner path; (4) occurrences is
#                      the owner's one-pattern lazy-gap loop over the span (a condition re-enters it); (5) atomic =
#                      PCRE's atomic group.
#   absent-under-not   two-valued: NOT around a test of an absent label holds.
#   when-meaning       when(c, p) := x & (NOT c | p), one `|` (an alternation of zero-width tests).
#   last-pass-default  a bare label set in a loop reads the last pass that set it (PCRE's capture after the match).
#   READINGS (the manager's, carried open): join-order = left side's paths outer; hits-committed = a named all-hits
#                      request reads the global search's committed hit list (H1); the other forms are the regex ones.
# THE ENGINE is lane lastpass's (lastpass_model.py, loaded in memory up to its PART A, never edited; it loads lane
# pathimpact's path enumerator and lane rxmodel's libpcre2 harness, never edited), run in its mode R (two-valued,
# last pass) with occurrences H2, plus four nodes of this lane's own: OPE (rev 23.2's one-row-per-end, for the switch),
# Rep (a loop over a conditioned item: `/(?:${item})+/`), Atom (PCRE's atomic group) and Idx (a literal pass index).
#
# SWITCHES (W = the worktree; run from $PCREC_TMPDIR/scratch/predspec24):
#   timeout 1800 python3 -I W/docs/dev/lanes/predspec24_evidence/predspec24_model.py > fwd.out
#   PREDSPEC24_SWAP=1 ...       reverses text pools, condition lists and the order lines are COMPUTED (printing order
#                               fixed); diff of the two without ORDER: lines must print nothing
#   PREDSPEC24_SABOTAGE=1 ...   a bare looped label reads the FIRST pass, and under SWAP PCRE's path order is reversed:
#                               the libpcre2 checks must fail and forward vs swapped must differ
#   PREDSPEC24_RULES=23.2 ...   THE SWITCH BACK: the NOW column is computed under rev 23.2's rules (reading (iii):
#                               one row per stretch end, inner conditions only fall through; Kleene three-valued
#                               logic; every pass; committed hits; `when` = the filter form); MOVED must print 0 and
#                               the PRINTED check must print 0 mismatches either way
import os, sys, io, re, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
LANES = os.path.dirname(HERE)
SWAP = os.environ.get("PREDSPEC24_SWAP") == "1"
SAB = os.environ.get("PREDSPEC24_SABOTAGE") == "1"
NOWR = os.environ.get("PREDSPEC24_RULES", "24")
if NOWR not in ("24", "23.2"): sys.exit("PREDSPEC24_RULES must be 24 or 23.2")
print("ORDER: %s%s NOW=rev %s" % ("SWAPPED" if SWAP else "forward", " SABOTAGE" if SAB else "", NOWR))
def order(xs): return list(reversed(list(xs))) if SWAP else list(xs)

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
set_once_labels, strings, lists = LP["set_once_labels"], LP["strings"], LP["lists"]
num, lt, ge, between, eq = LP["num"], LP["lt"], LP["ge"], LP["between"], LP["eq"]

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

class Rep:
    """`/(?:${X}){lo,}/`: program X repeated, greedy, contiguous; each pass is one path of X with its own checks (a
    condition inside X is a piece of every pass: the regex model is a callout in the loop body). The labels X sets
    once become looped labels of the loop; the bare label reads the last pass (PCRE's capture)."""
    def __init__(self, X, lo=0): self.X, self.lo = X, lo; self.key = ("L", "rep", id(self)); self.labs = set_once_labels(X)
    def mkrow(self, s, i, e, ps):
        row = Row(); row.stretch = (i, e); row.passes[self.key] = []
        for pr in ps: row.passes[self.key].append({k: v for k, v in pr.last.items() if v is not None and k in self.labs})
        for l in self.labs:
            row.loop[l] = self.key
            vals = [p.get(l) for p in row.passes[self.key] if p.get(l) is not None]
            row.last[l] = vals[-1] if vals else None
            row.first[l] = vals[0] if vals else None
        return row
    def walk(self, s, i):
        def loop(pos, ps, ck):
            for e, row, c in self.X.walk(s, pos):
                if e == pos: continue                       # an empty pass ends the loop (PCRE)
                yield from loop(e, ps + (row,), ck + c)
            if len(ps) >= self.lo: yield pos, self.mkrow(s, i, pos, ps), ck
        yield from loop(i, (), ())

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
    def __init__(self, X, mn=0): self.o = Occ(X, mn)
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
def D(node, B): return Diff(ope(node), B)
def ALT(*bs): return Alt(*bs)
def AND(a, b): return AndP(ope(a), ope(b))
def C(labs, pred, **d): return Test(labs, pred, d)
def NOT(c): return Not_(c)
def ANDC(*cs): return And_(*order(cs))
def ORC(*cs): return Or_(*order(cs))
def SOME(c): return Count(c, lambda n: n >= 1)
def NONE(c): return Count(c, lambda n: n == 0)
def EXACTLY(k, c): return Count(c, lambda n, k=k: n == k)
def OCC(X, mn=0): return Occ(X, mn)
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
 ("W1c", "every pass, at least one, a pass may lack h", "REP & `(h: <5)`", "`/(?:${item})+/`, item := `/(?<h>\\d)?;/ & (h: <5)`",
  lambda: W(REP(), h5()), lambda: Rep(W(Pat(ITEMO), h5()), 1), RG3),
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
