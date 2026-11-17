#!/usr/bin/env python3
# Lane lastpass (2026-11-17): the question **last-pass-default** put to the owner. A bare label set inside a loop and
# read by a condition written after the loop: (T) TODAY'S READING, rev 23.2 (every pass: the pass table, R.1.2 /
# R.1.5 / §4.3's sequence rule), or (R) THE REGEX DEFAULT (what a PCRE callout after the loop sees: the value of the
# last pass that SET the label; unset when no pass set it). DESIGN EVIDENCE ONLY: both are run side by side; nothing
# is chosen.
#
# THE ENGINE. Paths come from lane pathimpact's enumerator (`Rx` in pathimpact_model.py, loaded in memory, never
# edited; its PART A checks it against Python `re`). The branch-scope ruling (2026-11-17 11:35, reading (ii)) is the
# rule: a condition is one more piece of the pattern; a path survives when every condition on it is TRUE; WHOLE =
# some surviving path from 0 reaches the end; SEARCHED = the leftmost start with a surviving path, the first such path
# reported; FIND-ALL = again from the reported end (an empty report steps one). regex-settles (2026-11-17 13:25):
# a test on an absent label FAILS; `!B` keeps a path when NO path of B survives over the stretch; `occurrences` is the
# owner's ONE-PATTERN lazy-gap loop over the span (a condition inside it re-enters). absent-under-not (13:25): logic
# is TWO-VALUED; the engine runs two-valued in modes T and R. Mode T3 (the draft's printed Kleene logic) is run only
# as the CONTROL that this engine reproduces the draft's printed answers.
#
# THE TWO READINGS of a plain condition on a looped label (every other construct is the same in both):
#   T  every row of the pairing loop's pass table (§4.3 THE PAIRING RULE; a pass's own values, a label the pass did
#      not set is absent in it; zero passes = ONE null pass row), each tested; TRUE when every pass row is TRUE.
#   R  the label's PCRE capture after the match (the last pass that set it; earlier values carried over a pass that did
#      not set it; unset if no pass set it), tested once, exactly as a set-once label.
# Group questions (`some`, `count`, `occurs.*`) are over the REAL passes, each pass's own values, in BOTH readings:
# they are the named per-pass forms, not the bare label.
#
# Commands (W = the worktree; run from $PCREC_TMPDIR/scratch/lastpass):
#   timeout 900 python3 -I W/docs/dev/lanes/lastpass_evidence/lastpass_model.py > lastpass_model.out
#   LASTPASS_DEFAULT=T ...   THE SWITCH: column R is computed as T; "MOVED" must print 0 everywhere
#   LASTPASS_SABOTAGE=1 ...  R reads the FIRST pass that set the label: the libpcre2 checks (PART A) must fail
import os, sys, io, re, contextlib, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
LANES = os.path.dirname(HERE)
SWITCH_T = os.environ.get("LASTPASS_DEFAULT") == "T"
SAB = os.environ.get("LASTPASS_SABOTAGE") == "1"
sys.path.insert(0, os.path.join(LANES, "rxmodel_evidence"))
import pcre2h as P                                          # libpcre2-8 through ctypes (lane rxmodel; never edited)

PI = os.path.join(LANES, "pathimpact_evidence", "pathimpact_model.py")
SRC = open(PI).read()
E = {"__file__": PI, "__name__": "pathimpact_defs"}
for k in ("PATHIMPACT_SWAP", "PATHIMPACT_SABOTAGE", "PATHIMPACT_READING", "PATHIMPACT_ENDS"):
    os.environ.pop(k, None)
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(SRC[:re.search(r"^# =+ PART A$", SRC, re.M).start()], PI, "exec"), E)
Rx, strings = E["Rx"], E["strings"]
from re._constants import SUBPATTERN, MAX_REPEAT, MIN_REPEAT, POSSESSIVE_REPEAT, BRANCH, ASSERT, ASSERT_NOT, ATOMIC_GROUP, MAXREPEAT

# ================================================================================================= ROWS AND PASSES
RXC = {}
def rx_of(p):
    if p not in RXC:
        r = Rx(p)
        enc = {}                                            # group id -> its innermost enclosing LOOP (hi >= 2)
        def walk(items, loop):
            for node in items:
                op, av = node
                if op == SUBPATTERN:
                    gid, _, _, sub = av
                    if gid: enc[gid] = loop
                    walk(sub, loop)
                elif op in (MAX_REPEAT, MIN_REPEAT, POSSESSIVE_REPEAT):
                    lo, hi, sub = av
                    walk(sub, ("L", p, id(node)) if (hi == MAXREPEAT or hi >= 2) else loop)
                elif op == BRANCH:
                    for a in av[1]: walk(a, loop)
                elif op in (ASSERT, ASSERT_NOT): walk(av[1], loop)
                elif op == ATOMIC_GROUP: walk(av, loop)
        walk(r.tree, None)
        r.enc = enc
        RXC[p] = r
    return RXC[p]

class Row:
    """One path's row: `last` = PCRE's capture state (the last setting of each label); `loop` = label -> its pairing
    loop (None when set-once); `passes` = loop -> list of pass rows (each: the labels THAT pass set)."""
    def __init__(self):
        self.last, self.first, self.loop, self.passes, self.stretch = {}, {}, {}, {}, None
def row_of(r, s, i, e, caps, hist):
    row = Row(); row.stretch = (i, e)
    for nm, g in r.names.items():
        row.last[nm] = None if caps[g] is None else s[caps[g][0]:caps[g][1]]
        row.loop[nm] = r.enc.get(g)
    firsts = {}
    for ev in hist:
        if ev[0] == "g" and ev[1] not in firsts: firsts[ev[1]] = s[ev[2]:ev[3]]
    for nm, g in r.names.items(): row.first[nm] = firsts.get(g)
    for lp in set(v for v in row.loop.values() if v is not None):
        nid = lp[2]; ps = []
        for ev in hist:
            if ev[0] == "it" and ev[1] == nid: ps.append({})
            elif ev[0] == "g" and ps and r.enc.get(ev[1]) == lp:
                ps[-1][r.gname[ev[1]]] = s[ev[2]:ev[3]]
        row.passes[lp] = ps
    return row
def merge(a, b):
    r = Row(); r.stretch = a.stretch
    for x in (a, b):
        r.last.update(x.last); r.first.update(x.first); r.loop.update(x.loop); r.passes.update(x.passes)
    return r

# ================================================================================================= CONDITIONS
BARE = {"v": False}
MODE = {"v": "T"}                                           # T, R or T3 (the control); a group question's pass view
def K(v): return v                                          # three-valued values: True / False / None
def kand(vs):
    vs = list(vs)
    if any(v is False for v in vs): return False
    if any(v is None for v in vs): return None
    return True
def kor(vs):
    vs = list(vs)
    if any(v is True for v in vs): return True
    if any(v is None for v in vs): return None
    return False
def two(v): return v if MODE["v"] == "T3" else (v is True)
class Test:
    """`(l1: S)` or a joint `((l1, ..., lk): R)`, with optional per-test defaults (R.1.6)."""
    def __init__(self, labs, pred, dflt=None):
        self.labs = (labs,) if isinstance(labs, str) else tuple(labs); self.pred = pred; self.dflt = dict(dflt or {})
    def one(self, get):
        vals = []
        for l in self.labs:
            v = get(l)
            if v is None: v = self.dflt.get(l)
            if v is None: return two(None)
            vals.append(v)
        return bool(self.pred(*vals))
    def ev(self, row, view=None):
        looped = [l for l in self.labs if row.loop.get(l) is not None]
        if view is not None:                                # inside a group question: the pass's own values
            return self.one(lambda l: view.get(l) if row.loop.get(l) is not None else row.last.get(l))
        if looped: BARE["v"] = True                        # this line reads a looped label with a bare condition
        mode = "T" if (SWITCH_T and MODE["v"] == "R") else MODE["v"]
        if not looped or mode == "R":
            src = row.first if (SAB and mode == "R") else row.last
            return self.one(lambda l: src.get(l))
        loops = set(row.loop[l] for l in looped)
        if len(loops) != 1: raise ValueError("sibling loops: %r" % (self.labs,))
        ps = row.passes[loops.pop()] or [{}]                # zero passes = the one null pass row
        return kand([self.one(lambda l, p=p: p.get(l) if row.loop.get(l) is not None else row.last.get(l)) for p in ps])
class Not:
    def __init__(self, c): self.c, self.labs = c, c.labs
    def ev(self, row, view=None):
        v = self.c.ev(row, view)
        return (None if v is None else (not v)) if MODE["v"] == "T3" else (not v)
class And:
    def __init__(self, *cs): self.cs, self.labs = cs, tuple(l for c in cs for l in c.labs)
    def ev(self, row, view=None): return kand([c.ev(row, view) for c in self.cs])
class Or:
    def __init__(self, *cs): self.cs, self.labs = cs, tuple(l for c in cs for l in c.labs)
    def ev(self, row, view=None): return kor([c.ev(row, view) for c in self.cs])
def _passes_for(c, row):
    lps = set(row.loop.get(l) for l in c.labs if row.loop.get(l) is not None)
    if len(lps) != 1: raise ValueError("group question over %r" % (c.labs,))
    return row.passes[lps.pop()]
class Count:
    """`count(c)` compared by `cmp`; `some(c)` = count >= 1; `occurs.none(c)` = count == 0 (two-valued, R.1.7)."""
    def __init__(self, c, cmp): self.c, self.cmp, self.labs = c, cmp, c.labs
    def ev(self, row, view=None):
        return bool(self.cmp(sum(1 for p in _passes_for(self.c, row) if self.c.ev(row, p) is True)))
def Some(c): return Count(c, lambda n: n >= 1)
def None_(c): return Count(c, lambda n: n == 0)
def Exactly(k, c): return Count(c, lambda n: n == k)

# ================================================================================================= PROGRAMS
class Pat:
    def __init__(self, p): self.p = p; self.rx = rx_of(p)
    def walk(self, s, i):
        for e, caps, hist in self.rx.paths(s, i):
            yield e, row_of(self.rx, s, i, e, caps, hist), ()
class Where:
    def __init__(self, node, *cs): self.node, self.cs = node, cs
    def walk(self, s, i):
        for e, row, ck in self.node.walk(s, i):
            yield e, row, ck + tuple((lambda c=c, row=row: c.ev(row)) for c in self.cs)
class Diff:                                                 # `node & !B`: no surviving path of B over the stretch
    def __init__(self, node, B): self.node, self.B = node, B
    def walk(self, s, i):
        for e, row, ck in self.node.walk(s, i):
            yield e, row, ck + ((lambda e=e: not any(e2 == e for e2, _ in accepted(self.B, s, i))),)
class Alt:
    def __init__(self, *bs): self.bs = bs
    def walk(self, s, i):
        for b in self.bs: yield from b.walk(s, i)
class AndP:                                                 # `A & B` on patterns: same stretch, left paths outer
    def __init__(self, a, b): self.a, self.b = a, b
    def walk(self, s, i):
        Bp = list(self.b.walk(s, i))
        for e1, r1, c1 in self.a.walk(s, i):
            for e2, r2, c2 in Bp:
                if e1 == e2: yield e1, merge(r1, r2), c1 + c2
class Keep:                                                 # a filter reading the row and the stretch (`when`'s filter form)
    def __init__(self, node, f): self.node, self.f = node, f
    def walk(self, s, i):
        for e, row, ck in self.node.walk(s, i):
            yield e, row, ck + ((lambda e=e, row=row: self.f(row, s, i, e)),)
def set_once_labels(node):
    """The labels a program sets once per row (a hit's own labels; looped ones inside a hit are not hit labels)."""
    if isinstance(node, Pat): return set(nm for nm, g in node.rx.names.items() if node.rx.enc.get(g) is None)
    if isinstance(node, (Where, Diff, Keep)): return set_once_labels(node.node)
    if isinstance(node, Alt): return set().union(*[set_once_labels(b) for b in node.bs])
    if isinstance(node, AndP): return set_once_labels(node.a) | set_once_labels(node.b)
    return set()
OCCM = {"v": "H2"}                                          # H2 = regex-settles (4); H1 = hits committed (the draft's text)
class Occ:
    """`occurrences(X, min = n)`: the owner's ONE-PATTERN model `(?:[\\s\\S]*?(X)){n,}[\\s\\S]*` over the span
    (regex-settles (4): an outer condition re-enters it); X a program; each pass is one hit; the label `hit` is the
    hit's text; a hit's labels are its own (R.1.9, §2.6); PCRE's capture state after the loop = the last hit that set
    each label. An empty hit ends the loop. OCCM = H1 (the CONTROL only): the hits are the global find-all of X inside
    the stretch, committed, one path per stretch (the draft's printed answers predate regex-settles)."""
    def __init__(self, X, mn=0):
        self.X, self.mn = X, mn; self.key = ("L", "occ", id(self)); self.labs = set_once_labels(X) | {"hit"}
    def mkrow(self, s, i, e, hits):
        row = Row(); row.stretch = (i, e)
        row.passes[self.key] = []
        for g, he, hr in hits:
            p = {"hit": s[g:he]}; p.update({k: v for k, v in hr.last.items() if v is not None and k in self.labs})
            row.passes[self.key].append(p)
        for l in self.labs:
            row.loop[l] = self.key
            vals = [p.get(l) for p in row.passes[self.key] if p.get(l) is not None]
            row.last[l] = vals[-1] if vals else None
            row.first[l] = vals[0] if vals else None
        return row
    def walk(self, s, i):
        n = len(s)
        if OCCM["v"] == "H1":
            for e in range(n, i - 1, -1):
                sub = s[i:e]
                hits = [(i + a, i + b, r) for a, b, r in findall(self.X, sub)]
                if len(hits) >= self.mn: yield e, self.mkrow(s, i, e, hits), ()
            return
        def loop(pos, hits, ck):
            for g in range(pos, n + 1):                     # lazy gap: the shortest first
                for e, row, c in self.X.walk(s, g):
                    h = hits + ((g, e, row),)
                    if e == g:                              # an empty hit ends the loop
                        if len(h) >= self.mn: yield from tail(e, h, ck + c)
                        continue
                    yield from loop(e, h, ck + c)
            if len(hits) >= self.mn: yield from tail(pos, hits, ck)
        def tail(pos, hits, ck):
            for e in range(n, pos - 1, -1):                 # the greedy trailing gap
                yield e, self.mkrow(s, i, e, hits), ck
        yield from loop(i, (), ())

def accepted(Pn, s, i):
    return [(e, row) for e, row, ck in Pn.walk(s, i) if all(f() is True for f in ck)]
def whole(Pn, s): return any(e == len(s) for e, _ in accepted(Pn, s, 0))
def search(Pn, s, pos=0):
    for i in range(pos, len(s) + 1):
        a = accepted(Pn, s, i)
        if a: return i, a[0][0], a[0][1]
    return None
def findall(Pn, s):
    out, pos = [], 0
    while pos <= len(s):
        r = search(Pn, s, pos)
        if r is None: break
        out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
    return out
def at(mode, f):
    old = MODE["v"]; MODE["v"] = mode
    try: return f()
    finally: MODE["v"] = old
def labs_str(row, labs): return "" if not labs else " " + ",".join("%s=%s" % (l, row.last.get(l)) for l in labs)
def ans_w(Pn, s): return "HOLDS" if whole(Pn, s) else "FAILS"
def ans_s(Pn, s, labs=()):
    r = search(Pn, s)
    return "FAILS" if r is None else "`%s`@%d%s" % (s[r[0]:r[1]], r[0], labs_str(r[2], labs))
def ans_f(Pn, s, labs=()):
    return "[" + ", ".join("`%s`@%d" % (s[i:j], i) for i, j, _ in findall(Pn, s)) + "]"

# ================================================================================================= HELPERS
def num(v): return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None
def lt(n): return lambda v: num(v) and int(v) < n
def ge(n): return lambda v: num(v) and int(v) >= n
def between(a, b): return lambda v: num(v) and a <= int(v) <= b
def eq(x): return lambda v: v == x
def neg(f): return lambda *v: not f(*v)
def anytext(*v): return True
def padded_ge(h0, m0): return lambda h, m: (int(h), int(m)) >= (h0, m0)
def canon_lt2(a, b): return lambda h, m: num(h) and num(m) and int(h) < a and int(m) < b
def T_(l, f, **d): return Test(l, f, d)

REP = Pat(r"(?:(?P<h>\d)?;)*")                               # R.3, R.8 items 2, 3: a pass may lack h
REP1 = Pat(r"(?:(?P<h>\d);)*")                              # the witness line; all-question's list
NLC = Pat(r"(?:(?P<n>\d),)*")                               # R.6, R.7 row 3, §4.3
NLO = Pat(r"(?:(?P<n>\d)?,)*")                              # §13's REV 23 block
KH = Pat(r"(?P<k>\d)(?:;(?P<h>\d))*")                       # `when`, the pairing rule
NSTAR = Pat(r"(?P<n>\d)*x")                                 # §0.1 L56, L65
NOPT = Pat(r"(?P<n>\d)?x")
NALT = Pat(r"x|(?P<n>\d)+")
CLOSE = Pat(r"(?:(?P<h>\d+)(?::(?P<m>\d\d))?,)*")           # §4.3 THE CLOSING EXAMPLE
TML = Pat(r"(?:(?P<h>\d{1,2})(?::(?P<m>\d\d))?,)*")         # §8 (4) TM2-L
PAIR = Pat(r"(?:(?P<h>\d{1,2}):(?P<m>\d\d),)*")             # §4.3 the pairing list
TWOF = Pat(r"(?:(?P<a>\d)?-(?P<b>\d)?,)*")                  # §4.3 two optional fields
ABXY = Pat(r"ab(?P<g>[xy])")
GAB = Pat(r"(?P<g>a)?b")
GH = Pat(r"(?P<g>[xy])(?P<h>\d)")
NUM = Pat(r"(?P<n>\d+)")
RM1 = AndP(Pat(r"(?:(?P<h>\d);)+"), Pat(r"\d;"))           # repeated-means
RM2 = Pat(r"(?P<h>\d);")

h5, n5 = T_("h", lt(5)), T_("n", lt(5))
pk = T_("k", between(3, 7))
def when_body(c): return Alt(Where(KH, c, pk), Diff(KH, Where(KH, c)))
def when_filter(c):
    return Keep(KH, lambda row, s, i, e, c=c: (c.ev(row) is True and pk.ev(row) is True) or
                not any(e2 == e for e2, _ in accepted(Where(KH, c), s, i)))
def lists(items, n):
    out = [""]; cur = [""]
    for _ in range(n):
        cur = [c + it for c in cur for it in items]; out += cur
    return out
RG3 = strings("37;", 5)                                     # 364
NL4 = strings("17,", 4)                                     # 121
NL5 = strings("17,", 5)                                     # 364
X4 = strings("37x", 4)                                      # 121
KHPOOL = [k + "".join(";" + x for x in t) for k in "0123456789" for t in [()] + [(a,) for a in "0123456789"] + [(a, b) for a in "0123456789" for b in "0123456789"]]
CLOSEPOOL = lists([h + m + "," for h in ("3", "12") for m in ("", ":15", ":45", ":05", ":99")], 3)   # 1,111
TMPOOL = lists(["9,", "10,", "9:15,", "9:45,", "10:15,"], 3)                                         # 156
PAIRPOOL = lists(["10:00,", "9:30,", "9:15,", "8:45,"], 3)                                           # 85
TWOPOOL = lists(["3-6,", "7-2,", "-6,", "3-,", "-,"], 3)                                              # 156
ABPOOL = strings("ab", 6)                                   # 127
XYPOOL = lists(["abx", "aby", "ab", " "], 3)                # 85
GHPOOL = lists(["x1", "x2", "y1", "y2", " "], 3)            # 156

OUT = []
def out(t=""): OUT.append(t); print(t)

# ================================================================================================= PART A: libpcre2
def has_count(c):
    if isinstance(c, Count): return True
    return any(has_count(x) for x in ([c.c] if hasattr(c, "c") else []) + list(getattr(c, "cs", ())))
def pcre_of(Pn):
    """The R reading of `Pat & conds` as a PCRE2 pattern with ONE callout after the regex (the regex model of a
    condition written after the loop). None when the program is not of that shape."""
    if isinstance(Pn, Where) and isinstance(Pn.node, Pat) and not any(has_count(c) for c in Pn.cs):
        pat = "(?:" + Pn.node.p.replace("(?P<", "(?<") + ')(?C"c")'
        cs = Pn.cs
        def f(ctx):
            row = Row()
            for nm in Pn.node.rx.names: row.last[nm] = ctx.get(nm); row.loop[nm] = None
            return all(at("R", lambda c=c: c.ev(row)) is True for c in cs)
        return P.Pcre(pat, {"c": f})
    if isinstance(Pn, Pat):
        return P.Pcre(Pn.p.replace("(?P<", "(?<"))
    return None
def pcre_cmp(Pn, pool):
    x = pcre_of(Pn)
    if x is None: return None
    dw = ds = df = 0; first = None
    for s in pool:
        a = at("R", lambda: (whole(Pn, s), (search(Pn, s) or (None, None))[:2], [t[:2] for t in findall(Pn, s)]))
        b = (x.whole(s), (x.search(s) or (None, None))[:2], [t[:2] for t in x.findall(s)])
        if a[0] != b[0]: dw += 1
        if a[1] != b[1]: ds += 1
        if a[2] != b[2]: df += 1
        if a != b and first is None: first = s
    return dw, ds, df, first

out("== PART A: PREMISE AND THE REGEX MODEL OF R (libpcre2-8 %s; callout after the regex)" % P.version())
def grp1(pat, s):
    got = []                                                # group 1 is named `g` so the harness's Ctx.get reads it
    y = P.Pcre(pat.replace("(\\d)", "(?<g>\\d)"), {"r": lambda c: (got.append(c.get("g")), True)[1]})
    ok = y.whole(s)
    return ok, got[-1] if got else "no callout"
for pat, s, want in [(r'(?:(\d);)*(?C"r")', "7;3;", "3"), (r'(?:(\d);)*(?C"r")', "", None),
                     (r'(?:(\d)?;)*(?C"r")', "7;;", "7"), (r'(?:(\d)?;)*(?C"r")', "3;;", "3"), (r'(?:(\d)?;)*(?C"r")', ";", None)]:
    ok, g = grp1(pat, s)
    out("  A0 `%s` on `%s`: WHOLE %s, group 1 at the callout = %r (expect %r) %s" % (pat, s, "HOLDS" if ok else "FAILS", g, want, "OK" if (ok and g == want) else "MISMATCH"))
out("  (A0 rows 3-4: a pass that does not set the label CARRIES the earlier pass's value: R reads `7` on `7;;`, the")
out("   last pass that SET h, not the last pass; the engine's R reads the same capture state.)")

# ================================================================================================= CATALOGUE
# Every worked example of predicates_draft.md rev 23.2 (live sections) whose program reads a looped label with a plain
# condition, or whose answer depends on one; plus the group-question and hit lines nearby (expected not to move, run
# as controls). Fields: id, site, program text, program, whole/searched text, find-all text, the draft's printed
# answer (WHOLE / SEARCHED, as printed; '' = not printed), the pool the counts run over.
C = []
def ex(i, site, txt, Pn, s, fa, printed, pool, plabel):
    C.append(dict(id=i, site=site, txt=txt, P=Pn, s=s, fa=fa, printed=printed, pool=pool, plabel=plabel))
FA_REP = "3;7; 7;; 3;"
FA_NL = "1,7, 7,, 3,"
FA_KH = "5;1;9 3;0;5"
for s, pr in [("", ("FAILS / FAILS", "FAILS / FAILS", "FAILS / FAILS", "HOLDS / HOLDS")),
              ("3;", ("HOLDS / HOLDS", "FAILS / FAILS", "FAILS / FAILS", "FAILS / HOLDS")),
              ("3;7;", ("FAILS / HOLDS", "HOLDS / HOLDS", "FAILS / HOLDS", "HOLDS / HOLDS")),
              ("7;;", ("FAILS / FAILS", "HOLDS / HOLDS", "FAILS / HOLDS", "HOLDS / HOLDS")),
              ("3;;", ("FAILS / HOLDS", "FAILS / FAILS", "FAILS / FAILS", "HOLDS / HOLDS"))]:
    for k, (nm, Pn) in enumerate([("REP & (h: <5)", Where(REP, h5)), ("REP & NOT (h: <5)", Where(REP, Not(h5))),
                                  ("REP & (h: !<5)", Where(REP, T_("h", neg(lt(5))))), ("REP & !(REP & (h: <5))", Diff(REP, Where(REP, h5)))]):
        ex("R3.%s.%d" % (s or "empty", k), "§R.3 repeated table (also R.8 item 2 on `7;;`)", nm, Pn, s, FA_REP, pr[k], RG3, "RG3")
ex("R17.a", "§R.1.7 example", "REP & (h = 0: <5)", Where(REP, T_("h", lt(5), h="0")), "", FA_REP, "HOLDS / HOLDS", RG3, "RG3")
ex("R17.b", "§R.1.7 example", "REP & (h = 0: <5)", Where(REP, T_("h", lt(5), h="0")), ";", FA_REP, "HOLDS / HOLDS", RG3, "RG3")
ex("R17.c", "§R.1.7 example", 'REP & occurs.none((h = "x": !<5))', Where(REP, None_(T_("h", neg(lt(5)), h="x"))), "", FA_REP, "HOLDS / HOLDS", RG3, "RG3")
ex("R17.d", "§R.1.7 example", 'REP & occurs.none((h = "x": !<5))', Where(REP, None_(T_("h", neg(lt(5)), h="x"))), ";", FA_REP, "FAILS / HOLDS", RG3, "RG3")
ex("R2.a", "§R.2 (empty S, repeated)", "REP & NOT (h: <0)", Where(REP, Not(T_("h", lt(0)))), "3;;", FA_REP, "HOLDS / HOLDS", RG3, "RG3")
ex("R2.b", "§R.2 (empty S, repeated)", "REP & (h: !<0)", Where(REP, T_("h", neg(lt(0)))), "3;;", FA_REP, "FAILS / HOLDS", RG3, "RG3")
for s, pr in [("", "HOLDS / HOLDS"), ("7;", "HOLDS / HOLDS"), (";", "FAILS / HOLDS")]:
    ex("R2.s." + (s or "empty"), "§R.2 sentinel idiom", 'REP & occurs.none((h = "x": !<10))', Where(REP, None_(T_("h", neg(lt(10)), h="x"))), s, FA_REP, pr if s != ";" else "FAILS / ", RG3, "RG3")
ex("R6.a", "§R.6 nullable loop", "NL & (n = 0: <5)", Where(NLC, T_("n", lt(5), n="0")), "7,", FA_NL, "FAILS / HOLDS", NL4, "NL4")
class TextNone:                                             # `text.none(B)`: a gate over the whole subject, no labels
    def __init__(self, B): self.B = B
    def walk(self, s, i):
        if i == 0 and not any(accepted(self.B, s, j) for j in range(len(s) + 1)):
            yield len(s), Row(), ()
for s in ["", "1,", "a", "7,"]:
    ex("R6.b." + (s or "empty"), "§R.6 a nullable B", "text.none(B), B := NL & (n = 9: >=5)", TextNone(Where(NLC, T_("n", ge(5), n="9"))),
       s, "1, a", "FAILS / ", NL4, "NL4")
for k, (nm, Pn, pr) in enumerate([("NL & (n = 0: <5)", Where(NLC, T_("n", lt(5), n="0")), "HOLDS / HOLDS"),
                                  ("NL & (n: <5)", Where(NLC, n5), "FAILS / FAILS"),
                                  ("NL & some((n: <5))", Where(NLC, Some(n5)), "FAILS / FAILS"),
                                  ("NL & NOT some((n: <5))", Where(NLC, Not(Some(n5))), "HOLDS / HOLDS")]):
    ex("R7.3.%d" % k, "§R.7 row 3, §4.3 narrower question (zero passes)", nm, Pn, "", FA_NL, pr, NL4, "NL4")
for s, pr in [("1,7,", ("FAILS / HOLDS", "HOLDS / HOLDS", "FAILS / HOLDS", "HOLDS / HOLDS")), ("7,,", ("", "HOLDS / HOLDS", "FAILS / HOLDS", "")),
              ("", ("", "FAILS / FAILS", "FAILS / FAILS", "HOLDS / HOLDS"))]:
    for k, (nm, Pn) in enumerate([("NLO & (n: <5)", Where(NLO, n5)), ("NLO & NOT (n: <5)", Where(NLO, Not(n5))),
                                  ("NLO & (n: !<5)", Where(NLO, T_("n", neg(lt(5))))), ("NLO & !(NLO & (n: <5))", Diff(NLO, Where(NLO, n5)))]):
        if pr[k]: ex("O13.%s.%d" % (s or "empty", k), "§13 REV 23 block (also R.7b b2)", nm, Pn, s, FA_NL, pr[k], NL5, "NL5")
for s, pr in [("3-6,", ("HOLDS / HOLDS", "")), ("7-2,", ("FAILS / HOLDS", "")), ("", ("HOLDS / HOLDS", "FAILS / FAILS")), ("-6,", ("HOLDS / HOLDS", "FAILS / FAILS"))]:
    ex("B6.%s.d" % (s or "empty"), "§4.3 two optional fields (R.7b b6)", "TWOF & (a = 0: <5, b = 3: between(3, 7))",
       Where(TWOF, And(T_("a", lt(5), a="0"), T_("b", between(3, 7), b="3"))), s, "3-6,7-2, -6,", pr[0], TWOPOOL, "TWOPOOL")
    if pr[1]: ex("B6.%s.n" % (s or "empty"), "§4.3 two optional fields, no defaults", "TWOF & (a: <5, b: between(3, 7))",
                 Where(TWOF, And(T_("a", lt(5)), T_("b", between(3, 7)))), s, "3-6,7-2, -6,", pr[1], TWOPOOL, "TWOPOOL")
for s, (nm, Pn, pr) in [("9", ("KH & (h: <5, k: between(3, 7))", Where(KH, And(h5, pk)), "FAILS / FAILS")),
                        ("3", ("KH & (h: <5, k: between(3, 7))", Where(KH, And(h5, pk)), "FAILS / FAILS")),
                        ("3", ("KH & (h = 0: <5, k: between(3, 7))", Where(KH, And(T_("h", lt(5), h="0"), pk)), "HOLDS / HOLDS")),
                        ("3;7", ("KH & (h = 0: <5, k: between(3, 7))", Where(KH, And(T_("h", lt(5), h="0"), pk)), "FAILS / `3`@0"))]:
    ex("B7.%s.%s" % (s, "d" if "= 0" in nm else "n"), "§4.3 pairing: a label outside the loop (R.7b b7)", nm, Pn, s, FA_KH, pr, KHPOOL, "KHPOOL")
ex("PAIR.a", "§4.3 pairing list", "PAIR & ((h, m): padded(>= (9, 30)))", Where(PAIR, T_(("h", "m"), padded_ge(9, 30))), "10:00,9:30,", "10:00,9:30, 9:15,", "HOLDS / HOLDS", PAIRPOOL, "PAIRPOOL")
TMS = ["", "10,", "9,", "9:45,", "10,9:15,"]
TMR = [("((h, m): R)", {}, "FFFHF"), ("((h, m = 0): R)", {"m": "0"}, "FHFHF"), ("((h, m = 30): R)", {"m": "30"}, "FHHHF"),
       ("((h = 10, m = 0): R)", {"h": "10", "m": "0"}, "HHFHF"), ("((h = 10, m = 30): R)", {"h": "10", "m": "30"}, "HHHHF")]
for nm, d, pr in TMR:
    for s, c in zip(TMS, pr):
        ex("TM2L.%s.%s" % (nm, s or "empty"), "§8 (4) TM2-L table (R.7b b9), R = padded(>= (9, 30))", "TML & " + nm,
           Where(TML, Test(("h", "m"), padded_ge(9, 30), d)), s, "10,9:15, 9:45,", {"H": "HOLDS", "F": "FAILS"}[c] + " / ", TMPOOL, "TMPOOL")
ex("NS.a", "§0.1 L56 / L65", "/(?<n>\\d)*x/ & (n: <5)", Where(NSTAR, n5), "x", "x 73x", "FAILS / FAILS", X4, "X4")
ex("NS.b", "§0.1 L56 / L65", "/(?<n>\\d)*x/ & (n = 0: <5)", Where(NSTAR, T_("n", lt(5), n="0")), "x", "x 73x", "HOLDS / HOLDS", X4, "X4")
ex("NS.c", "§0.1 L65", "/x|(?<n>\\d)+/ & (n: <5)", Where(NALT, n5), "x", "x 73x", "FAILS / FAILS", X4, "X4")
ex("NS.d", "§0.1 L65", "/x|(?<n>\\d)+/ & (n = 0: <5)", Where(NALT, T_("n", lt(5), n="0")), "x", "x 73x", "HOLDS / HOLDS", X4, "X4")
# occurrences / hits
OXY = Occ(ABXY)
for k, (nm, c, pr) in enumerate([('(g: "x")', T_("g", eq("x")), "FAILS / HOLDS"), ('some((g: "x"))', Some(T_("g", eq("x"))), "HOLDS / HOLDS"),
                                 ('occurs.exactly(2, (g: "x"))', Exactly(2, T_("g", eq("x"))), "HOLDS / HOLDS"),
                                 ('count((g: "y")) = 1', Exactly(1, T_("g", eq("y"))), "HOLDS / HOLDS"),
                                 ('(g = "x": "x")', T_("g", eq("x"), g="x"), "FAILS / "), ('occurs.none((g: "y"))', None_(T_("g", eq("y"))), "FAILS / ")]):
    ex("HIT.%d" % k, "§2.6 / §4.3 hits of /ab(?<g>[xy])/ (R.7b b5; §0.1 L52, L58)", "occurrences(/ab(?<g>[xy])/) & " + nm,
       Where(OXY, c), "abxabyabx", "abxabyabx abyabx", pr, XYPOOL, "XYPOOL")
ex("HIT.z1", "§2.6 zero hits (§0.1 L55)", 'occurrences(/ab(?<g>[xy])/) & (g: "x")', Where(OXY, T_("g", eq("x"))), "xyz", "xyz abx", "FAILS / FAILS", XYPOOL, "XYPOOL")
ex("HIT.z2", "§2.6 zero hits", 'occurrences(/ab(?<g>[xy])/) & (g = "x": "x")', Where(OXY, T_("g", eq("x"), g="x")), "xyz", "xyz abx", "HOLDS / HOLDS", XYPOOL, "XYPOOL")
ex("HIT.z3", "§2.6 zero hits, min = 1 (§0.1 L55)", 'occurrences(/ab(?<g>[xy])/, min = 1) & (g: "x")', Where(Occ(ABXY, 1), T_("g", eq("x"))), "xyz", "xyz abx", "FAILS / FAILS", XYPOOL, "XYPOOL")
ex("HIT.own", "§2.6 THE ITERATION'S OWN VALUES", 'occurrences(/(?<g>a)?b/) & (g: "a")', Where(Occ(GAB), T_("g", eq("a"))), "abb", "abb ab", "FAILS / ", ABPOOL, "ABPOOL")
ex("HIT.L61a", "§0.1 L61", 'contains(/ab(?<g>[xy])/ & (g: "x"))', Occ(Where(ABXY, T_("g", eq("x"))), 1), "abx aby", "abx aby aby", "HOLDS / ", XYPOOL, "XYPOOL")
ex("HIT.L61b", "§0.1 L61", 'contains(/ab(?<g>[xy])/) & (g: "x")', Where(Occ(ABXY, 1), T_("g", eq("x"))), "abx aby", "abx aby aby", "FAILS / ", XYPOOL, "XYPOOL")
OGH = Occ(GH)
for s in ["x2 y1", "x1 y2"]:
    for k, (nm, c) in enumerate([('some((g: "x", h: 1))', Some(And(T_("g", eq("x")), T_("h", eq("1"))))),
                                 ('some((g: "x")) & some((h: 1))', And(Some(T_("g", eq("x"))), Some(T_("h", eq("1"))))),
                                 ('(g: "x", h: 1) (the plain record)', And(T_("g", eq("x")), T_("h", eq("1"))))]):
        pr = {("x2 y1", 0): "FAILS / FAILS", ("x2 y1", 1): "HOLDS / HOLDS", ("x1 y2", 0): "HOLDS / HOLDS", ("x1 y2", 1): "HOLDS / HOLDS"}.get((s, k), "")
        ex("REC.%s.%d" % (s, k), "§4.3 SAME ITERATION BY RECORD (§0.1 L31)", "occurrences(/(?<g>[xy])(?<h>\\d)/) & " + nm, Where(OGH, c), s, "x1 y2 x2 y1", pr, GHPOOL, "GHPOOL")
ex("HL.a", "§R.8 item 11 hit-list (the condition inside the argument)", "occurrences(/(?<n>\\d+)/ & (n: <100), min = 2)",
   Occ(Where(NUM, n5.__class__("n", lt(100))), 2), "1234", "1234 5", "", strings("12 ", 4), "D3")
ex("RM.a", "§R.8 repeated-means", "/(?:(?<h>\\d);)+/ & /\\d;/ & (h: <5)", Where(RM1, h5), "3;", "3;7;3;", "", RG3, "RG3")
ex("RM.b", "§R.8 repeated-means", "/(?<h>\\d);/ & (h: <5)", Where(RM2, h5), "3;", "3;7;3;", "", RG3, "RG3")
ex("W.L", "§R.1.4 / §R.8 item 8: the witness list", "/(?:(?<h>\\d);)*/ & (h: <5)", Where(REP1, h5), "7;3;", "7;3; 3;7;", "", RG3, "RG3")
ex("W.E", "the all-question list (CF 23:18)", "/(?:(?<h>\\d);)*/ & (h: <5)", Where(REP1, h5), "", "7;3; 3;7;", "FAILS / ", RG3, "RG3")
ex("W.E0", "the all-question list (CF 23:18)", "/(?:(?<h>\\d);)*/ & (h = 0: <5)", Where(REP1, T_("h", lt(5), h="0")), "", "7;3; 3;7;", "HOLDS / ", RG3, "RG3")
for c, cn in [(h5, "(h: <5)"), (T_("h", lt(5), h="0"), "(h = 0: <5)")]:
    for s, pr in [("5;1;9", ("HOLDS / `5;1`@0", "HOLDS / `5;1;9`@0")), ("5;9", ("HOLDS / `5`@0", "")), ("0", ("", ""))]:
        if cn == "(h: <5)" and s == "5;9": pr = ("", "")
        if cn == "(h = 0: <5)" and s == "5;1;9": pr = ("", "")
        ex("WH.%s.%s.b" % (cn, s), "§R.1.4 / §R.8 item 8 / §R.7c c1 / §8 `when` body", "(KH & c & p) | (KH & !(KH & c)), c = " + cn, when_body(c), s, FA_KH, pr[0], KHPOOL, "KHPOOL")
        ex("WH.%s.%s.f" % (cn, s), "§R.8 item 8 / §R.6 `when` filter form", "KH & when(c, p), c = " + cn, when_filter(c), s, FA_KH, pr[1], KHPOOL, "KHPOOL")
ex("WH.occ.b", "§R.8 item 8 find-all place", "occurrences((KH & c & p) | (KH & !(KH & c)), min = 2), c = (h: <5)", Occ(when_body(h5), 2), "3;0;5", "3;0;5 5;1;9", "HOLDS / ", KHPOOL[:0] or [s for s in strings("035;", 5)], "D035")
ex("WH.occ.f", "§R.8 item 8 find-all place", "occurrences(KH & when(c, p), min = 2), c = (h: <5)", Occ(when_filter(h5), 2), "3;0;5", "3;0;5 5;1;9", "FAILS / ", [s for s in strings("035;", 5)], "D035")

# ================================================================================================= PART B
def cell(mode, Pn, s, fa):
    return at(mode, lambda: (ans_w(Pn, s), ans_s(Pn, s), ans_f(Pn, fa)))
out()
out("== PART B: THE CATALOGUE, T beside R (WHOLE / SEARCHED / FIND-ALL); MOVES = the R cells differ from T")
moved_lines, ctl_bad, MV = [], [], {}
for x in C:
    BARE["v"] = False
    t = cell("T", x["P"], x["s"], x["fa"]); x["bare"] = BARE["v"]; r = cell("R", x["P"], x["s"], x["fa"]); OCCM["v"] = "H1"; t3 = cell("T3", x["P"], x["s"], x["fa"]); OCCM["v"] = "H2"
    mv = [m for m, a, b in zip(("WHOLE", "SEARCHED", "FIND-ALL"), t, r) if a != b]
    if mv: moved_lines.append(x["id"]); MV[x["id"]] = mv
    pw, _, ps = x["printed"].partition(" / ")
    ctl = []
    if pw and pw != t3[0]: ctl.append("WHOLE printed %s, T3 %s" % (pw, t3[0]))
    if ps:
        got = "HOLDS" if t3[1] != "FAILS" else "FAILS"
        if not (ps == t3[1] or ps == got or (ps.startswith("`") and ps.split()[0] == t3[1].split()[0])): ctl.append("SEARCHED printed %s, T3 %s" % (ps, t3[1]))
    if ctl: ctl_bad.append((x["id"], ctl))
    out("  [%s] %s | `%s` on `%s`%s" % (x["id"], x["site"], x["txt"], x["s"], "" if x["bare"] else "   (no bare looped read: a control)"))
    out("      T  %s / %s / FIND-ALL on `%s` %s" % (t[0], t[1], x["fa"], t[2]))
    out("      R  %s / %s / FIND-ALL %s%s" % (r[0], r[1], r[2], ("   MOVES: " + ", ".join(mv)) if mv else "   same"))
    if t3 != t: out("      T3 (the draft's text: Kleene logic, hits committed; before absent-under-not and regex-settles) %s / %s / %s" % t3)
    if x["printed"]: out("      printed in the draft: %s%s" % (x["printed"], "   CONTROL: " + "; ".join(ctl) if ctl else ""))
out()
out("PART B SUMMARY: %d catalogue lines; MOVED (any mode) %d; not moved %d" % (len(C), len(moved_lines), len(C) - len(moved_lines)))
out("PART B MOVED ids: %s" % ", ".join(moved_lines))
DR = [x for x in C if not x["id"].startswith("W.")]           # W.* = the brief's witness and the record's list, not draft lines
nb = [x for x in DR if x["bare"]]
out("PART B DRAFT LINES: %d (the W.* lines are the brief's witness and the all-question list, not counted); MOVED %d" % (len(DR), sum(1 for x in DR if x["id"] in MV)))
out("PART B BARE LOOPED READS: %d lines read a looped label with a bare condition; %d of them move; %d control lines (group questions, set-once labels) move %d" % (
    len(nb), sum(1 for x in nb if x["id"] in MV), len(DR) - len(nb), sum(1 for x in DR if not x["bare"] and x["id"] in MV)))
out("PART B BARE LINES THAT DO NOT MOVE: %s" % ", ".join(x["id"] for x in nb if x["id"] not in MV))
out("PART B MOVED by mode: WHOLE %d, SEARCHED %d, FIND-ALL %d" % tuple(sum(1 for i, m in MV.items() if k in m and not i.startswith("W.")) for k in ("WHOLE", "SEARCHED", "FIND-ALL")))
out("PART B CONTROL (T3 = the draft's own text: Kleene, hits committed; vs the draft's printed answer): %d mismatches %s" % (len(ctl_bad), ctl_bad))

out()
out("PART B (H1): the hit lines again with the hits COMMITTED (the global search's hits, then judged; the candidate")
out("meaning of a NAMED all-hits request), two-valued, T beside R:")
OCCM["v"] = "H1"; nh = 0
for x in C:
    if not x["id"].startswith(("HIT", "REC", "HL", "WH.occ")): continue
    t = cell("T", x["P"], x["s"], x["fa"]); r = cell("R", x["P"], x["s"], x["fa"])
    nh += t != r
    out("  [%s] `%s` on `%s`: T %s / %s / %s ; R %s / %s / %s%s" % (x["id"], x["txt"], x["s"], *t, *r, "   MOVES" if t != r else ""))
OCCM["v"] = "H2"
out("PART B (H1) SUMMARY: %d of the hit lines move T -> R when the hits are committed" % nh)

# ================================================================================================= PART C: counts
out()
out("== PART C: COUNTS OVER THE TEXT SETS, per distinct program: T vs R (texts that differ; first differing text)")
seenp, totc = set(), [0, 0, 0]
for x in C:
    key = x["txt"]
    if key in seenp: continue
    seenp.add(key)
    dw = ds = df = 0; fw = fs = ff = None; hw = [0, 0]
    for s in x["pool"]:
        t = at("T", lambda: (whole(x["P"], s), (search(x["P"], s) or (None, None))[:2], [q[:2] for q in findall(x["P"], s)]))
        r = at("R", lambda: (whole(x["P"], s), (search(x["P"], s) or (None, None))[:2], [q[:2] for q in findall(x["P"], s)]))
        hw[0] += t[0]; hw[1] += r[0]
        if t[0] != r[0]: dw += 1; fw = fw if fw is not None else s
        if t[1] != r[1]: ds += 1; fs = fs if fs is not None else s
        if t[2] != r[2]: df += 1; ff = ff if ff is not None else s
    out("  `%s` over %s (%d): WHOLE holds T %d R %d, differ %d (first %r); SEARCHED report differ %d (first %r); FIND-ALL differ %d (first %r)" % (
        key, x["plabel"], len(x["pool"]), hw[0], hw[1], dw, fw, ds, fs, df, ff))

# ================================================================================================= PART D: libpcre2
out()
out("== PART D: R VALIDATED ON libpcre2 (the program's regex with ONE callout after it; WHOLE / SEARCHED / FIND-ALL over the set)")
nv = nbad = 0
for x in C:
    if x["txt"] in [y for y in []]: pass
done = set()
for x in C:
    if x["txt"] in done: continue
    done.add(x["txt"])
    r = pcre_cmp(x["P"], x["pool"])
    if r is None: continue
    nv += 1; nbad += (r[0] + r[1] + r[2]) > 0
    out("  `%s` over %s (%d): engine R vs libpcre2 differ WHOLE %d / SEARCHED %d / FIND-ALL %d (first %r)" % (x["txt"], x["plabel"], len(x["pool"]), *r))
for nm, Pn, pool in [("occurrences(/ab(?<g>[xy])/) body", Pat(r"(?:[\s\S]*?(?P<hit>ab(?P<g>[xy])))*[\s\S]*"), XYPOOL)]:
    Wn = Where(Pn, T_("g", eq("x"))); r = pcre_cmp(Wn, pool); nv += 1; nbad += (r[0] + r[1] + r[2]) > 0
    out("  the owner's one-pattern body `(?:[\\s\\S]*?(?<hit>ab(?<g>[xy])))*[\\s\\S]*` & (g: \"x\") over XYPOOL: differ %d / %d / %d (first %r)" % r)
    cmpo = sum(1 for s in pool if at("R", lambda: whole(Where(OXY, T_("g", eq("x"))), s)) != at("R", lambda: whole(Wn, s)))
    out("    the engine's Occ node vs that body as one regex, R, WHOLE over XYPOOL: differ %d" % cmpo)
out("PART D SUMMARY: %d programs checked on libpcre2; %d with any difference" % (nv, nbad))

# ================================================================================================= PART E: open questions
out()
out("== PART E: WHAT EACH OPEN LOOP QUESTION BECOMES (witness lines; T / R)")
def show(lbl, Pn, s, fa=None):
    t = cell("T", Pn, s, fa or s); r = cell("R", Pn, s, fa or s)
    out("  %s on `%s`: T %s / %s / %s ; R %s / %s / %s" % (lbl, s, t[0], t[1], t[2], r[0], r[1], r[2]))
# E2 loop-condition: where is the every-pass test judged (L1 after the loop over the pass list, L2 a piece in each pass)?
L2 = Pat(r"(?:(?P<h>\d);)*")
def L2prog(): return Where(L2, h5)
show("E2 the bare label `/(?:(?<h>\\d);)*/ & (h: <5)`", Where(REP1, h5), "7;3;", "7;3; 3;7;")
show("E2 the bare label, zero passes", Where(REP1, h5), "", "")
out("  E2 under R there is ONE judge: the callout after the loop (PART D shows the engine = libpcre2); L1/L2 is no longer a question of the bare label.")
# the named every-pass test: two placements, run with the per-pass piece model as a regex (L2) and the after-loop list judge (L1)
def every_after(c): return None_(Not(c))                    # every real pass c TRUE, possibly none: judged after the loop
EV1 = Where(REP1, every_after(h5))
EV2 = Pat(r"(?:(?P<h>[0-4]);)*")                             # the same test written as a piece in each pass (regular)
d = [(s, at("R", lambda: (whole(EV1, s), search(EV1, s)[:2] if search(EV1, s) else None)), (whole(EV2, s), search(EV2, s)[:2] if search(EV2, s) else None)) for s in RG3]
out("  the NAMED every-pass test `every((h: <5))` (= occurs.none(NOT (h: <5)), possibly none): judged after the loop (L1) vs a piece in each pass (L2, the regex `(?:[0-4];)*`) over RG3: WHOLE differ %d, SEARCHED differ %d (first %r)" % (
    sum(1 for s, a, b in d if a[0] != b[0]), sum(1 for s, a, b in d if a[1] != b[1]), next((s for s, a, b in d if a != b), None)))
out("    witness `7;3;`: L1 searched %s, L2 searched %s" % (at("R", lambda: ans_s(EV1, "7;3;")), at("R", lambda: ans_s(EV2, "7;3;"))))
# pass-table / pass-and / group-truth
show("pass-table `REP & NOT (h: <5)`", Where(REP, Not(h5)), "7;;")
show("pass-table `REP & (h: !<5)`", Where(REP, T_("h", neg(lt(5)))), "7;;")
show("group-truth `REP & NOT some((h: <5))`", Where(REP, Not(Some(h5))), ";")
show("the interaction: `REP & (h: <5)`", Where(REP, h5), "")
show("the interaction: `REP & NOT some(NOT (h: <5))`", Where(REP, Not(Some(Not(h5)))), "")
for nm, a, b in [("`(h: <5)` vs `NOT some(NOT (h: <5))` (the De Morgan dual, item 5's twin)", Where(REP, h5), Where(REP, Not(Some(Not(h5))))),
                 ("`(h: <5)` vs `some((h: <5)) & NOT some(NOT (h: <5))` (T's plain test spelled by the group questions)", Where(REP, h5), Where(REP, And(Some(h5), Not(Some(Not(h5)))))),
                 ("`NOT (h: <5)` vs `(h: !<5)` (L30, R.2)", Where(REP, Not(h5)), Where(REP, T_("h", neg(lt(5))))),
                 ("`NOT (h: <0)` vs `(h: !<0)` (R.2 empty S)", Where(REP, Not(T_("h", lt(0)))), Where(REP, T_("h", neg(lt(0))))),
                 ("`P & !some(c)` vs `P & occurs.none(c)` (L102)", Where(REP, Not(Some(h5))), Where(REP, None_(h5))),
                 ('`NOT (h = "x": <5)` vs `NOT (h: <5)` (R.7c c6)', Where(REP, Not(T_("h", lt(5), h="x"))), Where(REP, Not(h5))),
                 ("`(h: <5)` vs `(h = 0: <5)` (L36)", Where(REP, h5), Where(REP, T_("h", lt(5), h="0")))]:
    for mode in ("T", "R"):
        dw = sum(1 for s in RG3 if at(mode, lambda: whole(a, s)) != at(mode, lambda: whole(b, s)))
        ds = sum(1 for s in RG3 if at(mode, lambda: (search(a, s) is None)) != at(mode, lambda: (search(b, s) is None)))
        fw = next((s for s in RG3 if at(mode, lambda: whole(a, s)) != at(mode, lambda: whole(b, s))), None)
        out("  RG3 (364) %s, %s: differ WHOLE %d, SEARCHED holds %d (first WHOLE %r)" % (nm, mode, dw, ds, fw))
OGB = Occ(GAB)
for occm in ("H2", "H1"):
    OCCM["v"] = occm
    for mode in ("T", "R"):
        a = Where(OGB, None_(T_("g", neg(eq("a")), g=""))); b = Where(OGB, T_("g", eq("a"), g="a"))
        dw = sum(1 for s in ABPOOL if at(mode, lambda: whole(a, s)) != at(mode, lambda: whole(b, s)))
        ds = sum(1 for s in ABPOOL if at(mode, lambda: search(a, s) is None) != at(mode, lambda: search(b, s) is None))
        out("  §4.3 / R.7b b3 over 127 spans, hits %s, %s: `occurs.none((g = \"\": !\"a\"))` vs `(g = \"a\": \"a\")` differ WHOLE %d, SEARCHED holds %d" % (occm, mode, dw, ds))
OCCM["v"] = "H2"
# hit-list / hits-reentry
show("hits `occurrences(/(?<n>\\d+)/) & (n: <100)` (H2: the condition re-enters the one pattern)", Where(Occ(NUM), T_("n", lt(100))), "1234", "1234 5")
show("hits `occurrences(/(?<n>\\d+)/ & (n: <100))` (the condition inside the argument: hit-list)", Occ(Where(NUM, T_("n", lt(100)))), "1234", "1234 5")
d = sum(1 for s in strings("12 x", 4) if at("T", lambda: whole(Where(Occ(NUM, 1), T_("n", lt(100))), s)) != at("R", lambda: whole(Where(Occ(NUM, 1), T_("n", lt(100))), s)))
out("  hits `occurrences(/(?<n>\\d+)/, min = 1) & (n: <100)` over {1, 2, space, x} to length 4 (341): T vs R WHOLE differ %d" % d)
# the closing example and its intents
def items(s): return [it for it in s.split(",") if it]
def I1(s): return all(":" in it and num(it.split(":")[0]) and int(it.split(":")[0]) < 10 and num(it.split(":")[1]) and int(it.split(":")[1]) < 30 for it in items(s))
def I2a(s): return all((":" not in it) or (num(it.split(":")[0]) and int(it.split(":")[0]) < 10 and num(it.split(":")[1]) and int(it.split(":")[1]) < 30) for it in items(s))
def I2b(s): return all(num(it.split(":")[0]) and int(it.split(":")[0]) < 10 and ((":" not in it) or (num(it.split(":")[1]) and int(it.split(":")[1]) < 30)) for it in items(s))
RR = canon_lt2(10, 30)
out("  THE CLOSING EXAMPLE (§4.3; CLOSE over 1,111 lists; WHOLE differences from each intent, I1 / I2a / I2b; WHOLE holds):")
for nm, c in [("((h, m): R)", Test(("h", "m"), RR)), ("occurs.none(((h, m): !R))", None_(Test(("h", "m"), neg(RR)))),
              ("occurs.none(NOT ((h, m): R))", None_(Not(Test(("h", "m"), RR)))), ("occurs.none(NOT (h: <10, m: <30))", None_(Not(And(T_("h", lt(10)), T_("m", lt(30)))))),
              ("occurs.none(((h, m = 99): !R))", None_(Test(("h", "m"), neg(RR), {"m": "99"}))), ("occurs.none(((h, m = 0): !R))", None_(Test(("h", "m"), neg(RR), {"m": "0"}))),
              ("((h = 0, m = 0): R)", Test(("h", "m"), RR, {"h": "0", "m": "0"})), ("((h, m = 0): R)", Test(("h", "m"), RR, {"m": "0"}))]:
    Pn = Where(CLOSE, c)
    for mode in ("T", "R"):
        hv = {s: at(mode, lambda: whole(Pn, s)) for s in CLOSEPOOL}
        out("    `%s` %s: %d / %d / %d; holds %d" % (nm, mode, sum(hv[s] != I1(s) for s in CLOSEPOOL), sum(hv[s] != I2a(s) for s in CLOSEPOOL),
                                                  sum(hv[s] != I2b(s) for s in CLOSEPOOL), sum(hv.values())))
show("the closing example's stale minute: `CLOSE & ((h, m): R)`", Where(CLOSE, Test(("h", "m"), RR)), "3:15,3,")
show("  and `CLOSE & ((h, m = 0): R)` (the default never fires: m carries `15`)", Where(CLOSE, Test(("h", "m"), RR, {"m": "0"})), "3:45,3,")

# ================================================================================================= PART F: regularity
out()
out("== PART F: REGULAR FORMS (plain regex, no callout, no capture read) equal to each reading, WHOLE over the set")
def rx_whole(p, s): return re.fullmatch(p, s) is not None
for nm, Pn, rxp, mode, pool in [
        ("R `(?:(?<h>\\d)?;)*` & (h: <5): the last pass that SET h is < 5", Where(REP, h5), r"(?:\d?;)*[0-4];;*", "R", RG3),
        ("R `(?:(?<h>\\d)?;)*` & NOT (h: <5)", Where(REP, Not(h5)), r";*|(?:\d?;)*[5-9];;*", "R", RG3),
        ("T `(?:(?<h>\\d)?;)*` & (h: <5): every pass sets h < 5, at least one", Where(REP, h5), r"(?:[0-4];)+", "T", RG3),
        ("named some((h: <5))", Where(REP, Some(h5)), r"(?:\d?;)*[0-4];(?:\d?;)*", "R", RG3),
        ("named every, possibly none: occurs.none(NOT (h: <5))", Where(REP, None_(Not(h5))), r"(?:[0-4];)*", "R", RG3),
        ("named occurs.exactly(2, (h: <5))", Where(REP, Exactly(2, h5)), r"(?:(?:[5-9]?;))*[0-4];(?:(?:[5-9]?;))*[0-4];(?:(?:[5-9]?;))*", "R", RG3),
        ("R hits, re-entered (H2): (g: \"x\") = some hit is abx", Where(OXY, T_("g", eq("x"))), r"[\s\S]*abx[\s\S]*", "R", XYPOOL),
        ("T hits, re-entered (H2): (g: \"x\") = some hit is abx", Where(OXY, T_("g", eq("x"))), r"[\s\S]*abx[\s\S]*", "T", XYPOOL),
        ("H2 occurs.none((g: \"y\")) holds on every text (a gap swallows each aby)", Where(OXY, None_(T_("g", eq("y")))), r"[\s\S]*", "T", XYPOOL),
        ("R hits, committed (H1): the LAST hit's g is x", Where(OXY, T_("g", eq("x"))), r"[\s\S]*abx(?:(?!ab[xy])[\s\S])*", "R+H1", XYPOOL),
        ("T hits, committed (H1): EVERY hit's g is x, at least one", Where(OXY, T_("g", eq("x"))), r"(?:(?!ab[xy])[\s\S])*abx(?:(?:(?!ab[xy])[\s\S])*abx)*(?:(?!ab[xy])[\s\S])*", "T+H1", XYPOOL)]:
    OCCM["v"] = "H1" if mode.endswith("+H1") else "H2"; mode = mode.split("+")[0]
    d = sum(1 for s in pool if at(mode, lambda: whole(Pn, s)) != rx_whole(rxp, s))
    OCCM["v"] = "H2"
    out("  %s = /%s/: differ %d of %d" % (nm, rxp, d, len(pool)))

out()
print_moved = len(moved_lines)
out("== MOVED LINES %d (of %d); switch LASTPASS_DEFAULT=%s" % (print_moved, len(C), "T" if SWITCH_T else "unset"))
