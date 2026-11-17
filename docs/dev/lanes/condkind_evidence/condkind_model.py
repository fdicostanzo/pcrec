# condkind: evidence for docs/design/condition_kind.md (an EXPLORATION, rules nothing) and docs/dev/lanes/condkind_report.md
# (lane condkind, 2026-11-16; design only).
#
# THE MODEL (the owner's, COND-FAMILY 2026-11-16 19:49 / 20:41): a pattern is a SQL STATEMENT; the TABLE is the SOURCE
# it runs over (like the text for a pattern); a condition wraps the statement, `select * from (P) t where c`; the
# complement of a statement is (his best guess) the source rows the statement did not match. An absent label is NULL.
#
# THIS SCRIPT is a DECLARATIVE engine for that model: a condition is DATA (its labels with their controls, a tuple
# set, a kind), never a Python function that happens to consult a value set, so no answer can depend on the order in
# which an evaluator touches things (review r30's process change: `CONDKIND_SWAP=1` reverses every order the engine
# has: the chain, the labels inside a joint condition, the passes, the source rows, the candidate texts; the two runs
# must print the same lines apart from the `ORDER:` line).
#
# ROWS. The SOURCE row is a whole subject (S1; PART 1 (1c) also runs the span row, S2). A RESULT row is one match
# (PCRE's one reading): the set-once labels are columns, the pairing loop's passes a NESTED table inside the row; a
# loop that ran zero times gives ONE pass of NULLs where a plain condition looks (the LEFT JOIN), and no pass where a
# group question counts.
#
# THE MARK CANDIDATES (an absent label written `h?`):
#   M1    one row, "unknown counts as true", the unknown read EXACTLY: some TEXT in the absent label's place puts the
#         tuple in the set (no statement is read; "any text" is the stand-in universe UNIV below)
#   M1t   one row against a per-label CONSTANT: some value of the label's DOMAIN as the REGEX defines it (the values
#         the label takes in any match of the regex that defines it, no condition applied: SQL's column DOMAIN; rev
#         20's REGEX values), read as a fixed set like a type, never re-read through the program's conditions
#   M1a   one row, "IS NULL OR ...": the whole test of that pass is TRUE when a marked label is absent
#   M2c   as ruled (F1, domain-scope, mark-narrows): some value in DOM(h), DOM = h's values in the PROGRAM's rows (a
#         subquery over the statement), a marked condition TRANSPARENT in a pass where its marked label is absent
#         (THE RULE's text, per pass: the unit predspec21's `pv` uses)
#   M2r   as M2c, but while a DOM is computed an absent marked label ranges over the REGEX's values (review r30 V4's
#         candidate unit) instead of the condition being transparent
#   REV22 the answers of rev 22's own engine (predspec21_check.py, MANAGER), read from rev22_ref.py's table
# Unmarked absent label: no text (the condition FAILS). Default `h = v`: v (COALESCE).
#
# Run from the scratch dir:
#   timeout 300 python3 -I /abs/.../condkind_evidence/rev22_ref.py rev22_ref.tsv
#   timeout 600 python3 -I /abs/.../condkind_evidence/condkind_model.py rev22_ref.tsv > fwd.out
#   CONDKIND_SWAP=1 timeout 600 python3 -I /abs/.../condkind_evidence/condkind_model.py rev22_ref.tsv > swap.out
#   diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)      # must print nothing
#   (the same pair with CONDKIND_SABOTAGE=1 must print a difference)
import itertools, os, re, sys

SWAP = os.environ.get("CONDKIND_SWAP") == "1"
# Sabotage (shows the swap check can fail): `CONDKIND_SABOTAGE=1` gives M2c a TRAP-SHAPED transparency, like the
# predspec scripts' `fin` coding: while a DOM is computed, the condition's FIRST label in evaluation order is checked
# before the marks, so the answer depends on the order; the forward and swapped runs must then differ.
SAB = os.environ.get("CONDKIND_SABOTAGE") == "1"
print("ORDER: %s%s" % ("SWAPPED (every order reversed)" if SWAP else "forward", "; SABOTAGE ON" if SAB else ""))
D = [str(i) for i in range(10)]


def O(xs):
    """the engine's one iteration order: forward, or reversed under CONDKIND_SWAP=1"""
    xs = list(xs)
    return xs[::-1] if SWAP else xs


def canon(x):
    return x is not None and x.isdigit() and x == str(int(x))


def num(x):
    return x is not None and x.isdigit()


# "ANY TEXT" stand-in for M1: every set the pools use is decided by a text of at most two digits, `00`-`09`, or one
# letter (thresholds <= 30, digits, `a`/`b`), so a witness exists in UNIV whenever one exists at all.
UNIV = sorted({""} | {str(i) for i in range(100)} | {"%02d" % i for i in range(10)} | {"100", "999"} |
              set("abcxyz"), key=lambda s: (len(s), s))


def sm(xs):
    return min(xs, key=lambda s: (len(s), s)) if xs else None


def hf(b):
    return "HOLDS" if b else "FAILS"


def dstr(d):
    v = sorted(d, key=lambda s: (len(s), s))
    return "{" + ",".join(v) + "}" if len(v) <= 12 else "%d values" % len(v)


# ---------------------------------------------------------------------------------------------------------------- rows
class Row:
    """one RESULT row: subj (the source row), once (set-once label -> text or None), passes (list of dicts, or [])"""
    def __init__(self, subj, once, passes):
        self.subj, self.once, self.passes = subj, once, passes


class Pool:
    def __init__(self, name, source, build, looped=()):
        self.name, self.source, self.looped = name, list(source), frozenset(looped)
        self.rows = [r for r in (build(s) for s in self.source) if r is not None]
        self.labels = sorted(set().union(*[set(r.once) | {k for p in r.passes for k in p} for r in self.rows]))
        self.rdom = {l: set() for l in self.labels}           # the REGEX's values (no condition applied)
        for r in self.rows:
            for l, v in list(r.once.items()) + [kv for p in r.passes for kv in p.items()]:
                if v is not None:
                    self.rdom[l].add(v)


def rx_pool(name, rx, source, merge=None):
    """a pool of set-once labels read by Python `re` (merge: {label: [groups]} for duplicate names / branch reset)"""
    c = re.compile(rx)

    def build(s):
        m = c.fullmatch(s)
        if not m:
            return None
        g = m.groupdict()
        if merge:
            g = {lab: next((g[x] for x in xs if g[x] is not None), None) for lab, xs in merge.items()}
        return Row(s, g, [])
    return Pool(name, source, build)


# ----------------------------------------------------------------------------------------------------------- conditions
class Cond:
    """a condition as DATA. labs: [(label, ctl)], ctl "" (unmarked) | "?" (marked) | ("=", v) (default); R(t, view):
    the tuple set (t in labs order; a `$x` read through view, None when x is absent); kind: plain | all | some | none |
    at_most (n) | not3 (inner: the condition's three-valued NOT) | compl (q: a program; `!q`, label-free)"""
    def __init__(self, name, labs=(), R=None, kind="plain", n=None, reads=(), inner=None, q=None):
        self.name, self.labs, self.R, self.kind, self.n = name, list(labs), R, kind, n
        self.reads, self.inner, self.q = frozenset(reads), inner, q


def views(c, labs, row, pool, group):
    named = {l for l, _ in labs} | c.reads
    if not (named & pool.looped):
        return [dict(row.once)]
    if row.passes:
        return [dict(row.once, **p) for p in row.passes]
    return [] if group else [dict(row.once, **{l: None for l in pool.looped})]     # zero passes: the LEFT JOIN row


def cands(lab, ctl, view, mode, dom, pool):
    v = view.get(lab)
    if v is not None:
        return [v]
    if isinstance(ctl, tuple):
        return [ctl[1]]
    if ctl == "?":
        if mode == "M1":
            return UNIV
        if mode == "M2":
            return sorted(dom[lab])
        if mode == "M1t":
            return sorted(pool.rdom[lab])
    return []


def pass_val(c, labs, view, mode, dom, pool):
    if mode == "M1a" and any(ctl == "?" and view.get(l) is None for l, ctl in labs):
        return True
    order = O(range(len(labs)))
    lists = [O(cands(labs[i][0], labs[i][1], view, mode, dom, pool)) for i in order]
    for combo in itertools.product(*lists):
        t = [None] * len(labs)
        for i, v in zip(order, combo):
            t[i] = v
        if c.R(tuple(t), view):
            return True
    return False


def absent_mark(labs, view):
    return any(ctl == "?" and view.get(l) is None for l, ctl in labs)


def pass3(c, labs, view, mode, dom, pool):
    """three-valued: an absent UNMARKED label is an unknown text: TRUE if every text makes the tuple pass, FALSE if
    none does, else None (UNKNOWN); marks and defaults resolve inside, as in pass_val"""
    free = [i for i, (l, ctl) in enumerate(labs) if ctl == "" and view.get(l) is None]
    if not free:
        return pass_val(c, labs, view, mode, dom, pool)
    seen = set()
    for combo in itertools.product(*[O(UNIV) for _ in free]):
        v2 = dict(view)
        for i, x in zip(free, combo):
            v2[labs[i][0]] = x
        seen.add(pass_val(c, labs, v2, mode, dom, pool))
        if len(seen) == 2:
            return None
    return seen.pop()


def cval(c, row, pool, mode, dom, ctx, skip=False):
    """the condition's value on one result row (two-valued, as the WHERE keeps it). skip: a pass whose marked label is
    absent is TRANSPARENT (left out) while a DOM is computed (M2c's unit)"""
    if c.kind == "compl":
        return not ctx.answer(c.q, pool, ctx.cur)[row.subj]      # q answered alone, under the same candidate
    if c.kind == "not3":
        inn = c.inner
        vals = [pass3(inn, inn.labs, v, mode, dom, pool) for v in O(views(inn, inn.labs, row, pool, False))
                if not (skip and absent_mark(inn.labs, v))]
        allv = False if False in vals else (True if all(x is True for x in vals) else None)
        return allv is False                              # NOT: FALSE -> TRUE; TRUE -> FALSE; UNKNOWN stays, dropped
    labs = c.labs
    if c.kind == "all":
        labs = [(l, ctl if isinstance(ctl, tuple) else "?") for l, ctl in labs]
    group = c.kind in ("some", "none", "at_most")
    vals = []
    for v in O(views(c, labs, row, pool, group)):
        if skip and SAB:
            first = O(labs)[0]
            if first[1] == "" and v.get(first[0]) is None:
                vals.append(False)
                continue
        if skip and absent_mark(labs, v):
            continue
        vals.append(pass_val(c, labs, v, mode, dom, pool))
    if c.kind in ("plain", "all"):
        return all(vals)
    k = sum(vals)
    return {"some": k >= 1, "none": k == 0, "at_most": k <= (c.n or 0)}[c.kind]


class Ctx:
    """answers per (program, mode); a complemented pattern's program is answered by the same engine, alone"""
    def __init__(self):
        self.cache = {}
        self.cur = None             # the candidate being answered (a complemented pattern is answered under it too)

    def dom(self, prog, pool, unit):
        out = {l: set() for l in pool.labels}
        for row in O(pool.rows):
            if unit == "T-COND":
                ok = all(cval(c, row, pool, "M2", None, self, skip=True) for c in O(prog))
            else:
                ok = all(cval(c, row, pool, "M1t", None, self) for c in O(prog))
            if ok:
                for l, v in list(row.once.items()) + [kv for p in row.passes for kv in p.items()]:
                    if v is not None:
                        out[l].add(v)
        return out

    def answer(self, prog, pool, mode, with_dom=False):
        key = (pool.name, tuple(id(c) for c in prog), mode)
        if key not in self.cache:
            saved, self.cur = self.cur, mode
            dom = None
            ev = mode
            if mode in ("M2c", "M2r"):
                dom = self.dom(prog, pool, "T-COND" if mode == "M2c" else "T-REGEX")
                ev = "M2"
            src = {s: False for s in pool.source}
            for row in O(pool.rows):
                src[row.subj] = all(cval(c, row, pool, ev, dom, self) for c in O(prog))
            self.cache[key] = (src, dom)
            self.cur = saved
        return self.cache[key] if with_dom else self.cache[key][0]


CTX = Ctx()
MODES = ("M1", "M1t", "M1a", "M2c", "M2r")


def ans(prog, pool, mode):
    return CTX.answer(prog, pool, mode)


def ndiff(a, b, pool):
    d = [s for s in pool.source if a[s] != b[s]]
    return len(d), sm(d)


def one(name, lab, S, ctl=""):
    return Cond(name, [(lab, ctl)], lambda t, v, S=S: S(t[0]))


LT5 = lambda x: canon(x) and int(x) < 5
GT7 = lambda x: canon(x) and int(x) > 7
LT3 = lambda x: canon(x) and int(x) < 3
GT5 = lambda x: canon(x) and int(x) > 5

# =====================================================================================================================
print("\nPART 1: WHAT A ROW IS")
# (1a) the plain condition on a looped label: ruled (every pass of the LEFT JOIN, so >= 1 pass) vs SQL's natural
# reading if a RESULT row were a PASS (`select distinct subject from passes where c`: SOME pass)
RZ = Pool("RZ", [k + "".join(";" + h for h in hs) for k in D for n in range(3) for hs in itertools.product(D, repeat=n)],
          lambda s: Row(s, {"k": s.split(";")[0]}, [{"h": x} for x in s.split(";")[1:]])
          if re.fullmatch(r"(?P<k>\d)(?:;(?P<h>\d))*", s) else None, looped=["h"])
its = [h + ("" if m is None else ":" + m) + "," for h in ("1", "6") for m in (None, "2", "7")]
LST = Pool("LST", ["".join(c) for k in range(3) for c in itertools.product(its, repeat=k)],
           lambda s: Row(s, {}, [{"h": x.split(":")[0], "m": (x.split(":")[1] if ":" in x else None)}
                                 for x in s.split(",")[:-1]])
           if re.fullmatch(r"(?:(?P<h>\d)(?::(?P<m>\d))?,)*", s) else None, looped=["h", "m"])
hlt5 = one("(h: <5)", "h", LT5)
some_h = Cond("some((h: <5))", [("h", "")], lambda t, v: LT5(t[0]), kind="some")
a1, a2 = ans([hlt5], RZ, "M1"), ans([some_h], RZ, "M1")
n, ex = ndiff(a1, a2, RZ)
print("   (1a) RZ /(?<k>\\d)(?:;(?<h>\\d))*/, %d subjects: `(h: <5)` read over the match row (every pass, LEFT JOIN) "
      "vs over pass rows (some pass): differ %d (smallest %r: %s / %s)" % (len(RZ.source), n, ex, hf(a1[ex]), hf(a2[ex])))
mlth = Cond("((h, m): m < h)", [("h", ""), ("m", "")], lambda t, v: num(t[0]) and num(t[1]) and int(t[1]) < int(t[0]))
some_mlth = Cond("some(((h, m): m < h))", mlth.labs, mlth.R, kind="some")
a1, a2 = ans([mlth], LST, "M1"), ans([some_mlth], LST, "M1")
n, ex = ndiff(a1, a2, LST)
print("        LST /(?:(?<h>\\d)(?::(?<m>\\d))?,)*/, %d lists: `((h, m): m < h)` match row vs pass rows: differ %d "
      "(smallest %r: %s / %s)" % (len(LST.source), n, ex, hf(a1[ex]), hf(a2[ex])))
# (1b) zero passes: the LEFT JOIN row (plain) vs no pass (group questions), on RZ's `3`
rec = Cond("(h?: <5, k: 3..7)", [("h", "?"), ("k", "")], lambda t, v: LT5(t[0]) and canon(t[1]) and 3 <= int(t[1]) <= 7)
recu = Cond("(h: <5, k: 3..7)", [("h", ""), ("k", "")], lambda t, v: LT5(t[0]) and canon(t[1]) and 3 <= int(t[1]) <= 7)
print("   (1b) zero passes on RZ `3` (k = 3, no h): `(h: <5, k: 3..7)` %s, `(h?: <5, k: 3..7)` %s (M1) / %s (M2c), "
      "`some((h: <5))` %s; on `9`: `(h?: <5, k: 3..7)` %s (the outside k still tested: zero-pass-record)" % (
          hf(ans([recu], RZ, "M1")["3"]), hf(ans([rec], RZ, "M1")["3"]), hf(ans([rec], RZ, "M2c")["3"]),
          hf(ans([some_h], RZ, "M1")["3"]), hf(ans([rec], RZ, "M1")["9"])))
# (1c) the source row: a whole subject (S1) vs a span of the subject (S2, searched); the complement per source row
H2 = [str(i) for i in range(10)] + ["%02d" % i for i in range(100)]
M2v = ["%02d" % i for i in range(100)]
T2SRC = H2 + [h + ":" + m for h in H2 for m in M2v]
T2RX = re.compile(r"(?P<h>\d{1,2})(?::(?P<m>\d\d))?")


def t2row(s):
    m = T2RX.fullmatch(s)
    return Row(s, {"h": m["h"], "m": m["m"]}, []) if m else None


T2 = Pool("T2", T2SRC, t2row)
LATE = lambda t, v: num(t[0]) and num(t[1]) and (int(t[0]), int(t[1])) >= (9, 30)
late_u = Cond("((h, m): late)", [("h", ""), ("m", "")], LATE)
spans = {}
for s in T2.source:
    rows = []
    for i in range(len(s)):
        for j in range(i + 1, len(s) + 1):
            r = t2row(s[i:j])
            if r is not None:
                rows.append(r)
    spans[s] = rows
qrow = lambda r: cval(late_u, r, T2, "M1", None, CTX)
whole_c = {s: not ans([late_u], T2, "M1")[s] for s in T2.source}                          # t2 & !q, S1
span_c = {s: any(not qrow(r) for r in spans[s]) for s in T2.source}                        # t2 & !q, S2 (a span row)
subj_c = {s: not any(qrow(r) for r in spans[s]) for s in T2.source}                        # !(searched q)
not3_late = Cond("NOT ((h, m): late)", kind="not3", inner=late_u)
span_n = {s: any(cval(not3_late, r, T2, "M1", None, CTX) for r in spans[s]) for s in T2.source}
whole_n = ans([not3_late], T2, "M1")
print("   (1c) T2 /(?<h>\\d{1,2})(?::(?<m>\\d\\d))?/, %d subjects, q := t2 & ((h, m): late), late = padded(>= (9, 30)):"
      % len(T2.source))
print("        `t2 & !q` per whole subject (S1) holds on %d; per span (S2, searched) on %d; `!` of the searched q on %d;"
      " NOT ((h, m): late) whole %d, searched %d" % (sum(whole_c.values()), sum(span_c.values()),
                                                     sum(subj_c.values()), sum(whole_n.values()), sum(span_n.values())))
for nm, x, y in (("S1 vs S2 complement", whole_c, span_c), ("S2 complement vs complement of searched q", span_c, subj_c)):
    d = [s for s in T2.source if x[s] != y[s]]
    print("        %-44s differ %5d (smallest %r)" % (nm, len(d), sm(d)))

# =====================================================================================================================
print("\nPART 2: THE TWO NOTS (and the complement on the set), unmarked and marked")
N = rx_pool("N", r"(?P<h>\d)?x", ["x"] + [d + "x" for d in D])
qN = [one("(h: <5)", "h", LT5)]
qNm = [one("(h?: <5)", "h", LT5, "?")]
rowsN = [
    ("NOT (h: <5)  (the condition's NOT, three-valued)", [Cond("NOT (h: <5)", kind="not3", inner=qN[0])]),
    ("(h: !(<5))   (the complement on the set)", [one("(h: !(<5))", "h", lambda x: not LT5(x))]),
    ("P & !q, q := P & (h: <5)   (the statement's complement)", [Cond("!q", kind="compl", q=qN)]),
    ("NOT (h?: <5)  (the mark resolves inside)", [Cond("NOT (h?: <5)", kind="not3", inner=qNm[0])]),
    ("(h?: !(<5))", [one("(h?: !(<5))", "h", lambda x: not LT5(x), "?")]),
    ("P & !q, q := P & (h?: <5)", [Cond("!q", kind="compl", q=qNm)]),
]
print("   N = /(?<h>\\d)?x/, 11 subjects; per candidate: answers on `x` (h absent), `3x`, `7x`; holds on n of 11")
for nm, prog in rowsN:
    print("   %-58s %s" % (nm, "  ".join("%s %s/%s/%s %2d" % (md, hf(ans(prog, N, md)["x"])[0], hf(ans(prog, N, md)["3x"])[0],
                                                             hf(ans(prog, N, md)["7x"])[0], sum(ans(prog, N, md).values()))
                                      for md in MODES)))
# repeated label: NOT (h: S) ("not all in S") vs (h: !S) ("each outside S") vs RZ & !q, on RZ
nz = Cond("NOT (h: <5)", kind="not3", inner=hlt5)
sz = one("(h: !(<5))", "h", lambda x: not LT5(x))
cz = Cond("!q", kind="compl", q=[hlt5])
A_n, A_s, A_c = ans([nz], RZ, "M1"), ans([sz], RZ, "M1"), ans([cz], RZ, "M1")
print("   RZ (h looped), 1,110 subjects: holds on: NOT (h: <5) %d, (h: !(<5)) %d, RZ & !q %d; NOT vs set complement differ "
      "%d (smallest %r); NOT vs !q differ %d (smallest %r)" % (sum(A_n.values()), sum(A_s.values()), sum(A_c.values()),
                                                           *ndiff(A_n, A_s, RZ), *ndiff(A_n, A_c, RZ)))

# =====================================================================================================================
print("\nPART 3: THE MARK CANDIDATES SIDE BY SIDE (M1 one row, any text; M1t one row, the label's regex domain; M1a one "
      "row, IS NULL OR; M2c ruled; M2r ruled value set, V4's unit)")


def table(title, pool, progs, witnesses):
    print("   %s" % title)
    for nm, prog in progs:
        cells = []
        for md in MODES:
            a, dm = CTX.answer(prog, pool, md, with_dom=True)
            w = " ".join("%s=%s" % (s, hf(a[s])[0]) for s in witnesses)
            cells.append("%s %4d [%s]%s" % (md, sum(a.values()), w, "" if dm is None else " DOM" + "".join(
                "(%s)%s" % (l, dstr(dm[l])) for l in sorted({l for c in prog for l, ctl in c.labs if ctl == "?"}))))
        print("      %-34s %s" % (nm, " | ".join(cells)))
    for i, j in itertools.combinations(range(len(MODES)), 2):
        tot = [ndiff(ans(p, pool, MODES[i]), ans(p, pool, MODES[j]), pool) for _, p in progs]
        print("      %s vs %s: differ on %s" % (MODES[i], MODES[j], ", ".join("%d%s" % (n, "" if e is None else " (%r)" % e)
                                                                       for n, e in tot)))


table("(T2) 11,110 subjects; witnesses `9`, `5`, `9:15`, `10`", T2, [
    ("((h, m): late)", [late_u]),
    ("((h, m?): late)", [Cond("((h, m?): late)", [("h", ""), ("m", "?")], LATE)]),
    ("((h, m = 0): late)", [Cond("((h, m = 0): late)", [("h", ""), ("m", ("=", "0"))], LATE)]),
    ("((h, m?): !late)", [Cond("((h, m?): !late)", [("h", ""), ("m", "?")], lambda t, v: not LATE(t, v))]),
], ["9", "5", "9:15", "10"])
m30 = Cond("(m?: padded(<30))", [("m", "?")], lambda t, v: num(t[0]) and int(t[0]) < 30)
lm = Cond("((h, m?): late)", [("h", ""), ("m", "?")], LATE)
table("(T2+) the same, with `(m?: padded(<30))` added; and the complemented pattern `t2 & !q`, q := t2 & ((h, m?): late)",
      T2, [("((h, m?): late) & (m?: <30)", [lm, m30]),
           ("t2 & !q", [Cond("!q", kind="compl", q=[lm])]),
           ("t2 & !q & (m?: <30)", [Cond("!q", kind="compl", q=[lm]), m30])], ["9", "5", "09"])
ZE = Pool("ZE", ["%s-%s" % (a, k) + "".join(";" + h for h in hs) for a in D for k in D for n in range(3)
                 for hs in itertools.product(D, repeat=n)],
          lambda s: Row(s, {"a": s[0], "k": s[2]}, [{"h": x} for x in s.split(";")[1:]])
          if re.fullmatch(r"(?P<a>\d)-(?P<k>\d)(?:;(?P<h>\d))*", s) else None, looped=["h"])
table("(ZE) zero-pass-empty, /(?<a>\\d)-(?<k>\\d)(?:;(?<h>\\d))*/, 11,100 subjects; witnesses `0-3`, `5-3`", ZE, [
    ("(h?: <$a, k: 3)", [Cond("(h?: <$a, k: 3)", [("h", "?"), ("k", "")], lambda t, v: canon(t[0]) and v["a"] is not None
                               and int(t[0]) < int(v["a"]) and t[1] == "3", reads=["a"])])], ["0-3", "5-3"])
MN = rx_pool("MN", r"(?P<mnum>[123])?-(?P<d>\d)", [m + "-" + d for m in ["", "1", "2", "3"] for d in D])
table("(MN) a set disjoint from the label's values: /(?<mnum>[123])?-(?<d>\\d)/, 40 subjects; witness `-5`", MN, [
    ("(mnum?: >5)", [one("(mnum?: >5)", "mnum", GT5, "?")]), ("(mnum?: <3)", [one("(mnum?: <3)", "mnum", LT3, "?")])],
    ["-5"])
J = rx_pool("J", r"(?P<j>\d)(?P<h>\d)?(?P<k>\d)", [j + h + k for j in D for h in [""] + D for k in D])
c1 = Cond("(h?: <$k)", [("h", "?")], lambda t, v: canon(t[0]) and int(t[0]) < int(v["k"]), reads=["k"])
c2 = Cond("(h?: >$j)", [("h", "?")], lambda t, v: canon(t[0]) and int(t[0]) > int(v["j"]), reads=["j"])
c12 = Cond("(h?: >$j & <$k)", [("h", "?")], lambda t, v: canon(t[0]) and int(v["j"]) < int(t[0]) < int(v["k"]),
           reads=["j", "k"])
table("(J) one-witness, /(?<j>\\d)(?<h>\\d)?(?<k>\\d)/, 1,100 subjects; witness `12`", J,
      [("(h?: <$k) & (h?: >$j)", [c1, c2]), ("(h?: >$j & <$k)", [c12])], ["12"])
for md in MODES:
    n_, ex_ = ndiff(ans([c1, c2], J, md), ans([c12], J, md), J)
    print("      [%s] two conditions vs one: differ %d%s" % (md, n_, "" if ex_ is None else " (smallest %r)" % ex_))
BR = rx_pool("BR", r"(?:(?P<k1>a)(?:;(?P<h1>\d))?|(?P<k2>b)(?:;(?P<h2>[5-9]))?)",
             ["a", "b"] + ["a;" + d for d in D] + ["b;" + d for d in D], merge={"k": ["k1", "k2"], "h": ["h1", "h2"]})
kb = Cond("(k: \"b\")", [("k", "")], lambda t, v: t[0] == "b")
hm5 = one("(h?: <5)", "h", LT5, "?")
table("(BR) domain-scope's table (the branch reset with 0-1 passes, 17 subjects); witness `b`", BR, [
    ("P & (h?: <5)", [hm5]), ("P & (k: \"b\") & (h?: <5)", [kb, hm5]),
    ("P & ((k, h?): (\"b\", <5))", [Cond("((k, h?): (b, <5))", [("k", ""), ("h", "?")],
                                         lambda t, v: t[0] == "b" and LT5(t[1]))]),
    ("P & (k?: \"b\") & (h?: <5)", [Cond("(k?: \"b\")", [("k", "?")], lambda t, v: t[0] == "b"), hm5]),
    ("P & ((k, h?): (a,<5)|(b,>=5))", [Cond("((k, h?): ...)", [("k", ""), ("h", "?")],
                                            lambda t, v: (t[0] == "a" and LT5(t[1])) or
                                            (t[0] == "b" and canon(t[1]) and int(t[1]) >= 5))]),
    ("P & ((k, h?): (\"a\", <5))", [Cond("((k, h?): (a, <5))", [("k", ""), ("h", "?")],
                                         lambda t, v: t[0] == "a" and LT5(t[1]))])], ["b"])
# mark-in-none (LST), the `6,` example
MLT = lambda t, v: num(t[0]) and num(t[1]) and int(t[1]) < int(t[0])
none_m = Cond("occurs.none(((h, m?): m < h))", [("h", ""), ("m", "?")], MLT, kind="none")
gt5m = Cond("(m?: >5)", [("m", "?")], lambda t, v: num(t[0]) and int(t[0]) > 5)
table("(LST) mark-in-none, 43 lists; witnesses `6,`, `1,`", LST, [
    ("occurs.none(((h, m?): m < h))", [none_m]), ("  + (m?: >5)", [none_m, gt5m])], ["6,", "1,"])
for md in MODES:
    a, b = ans([none_m], LST, md), ans([none_m, gt5m], LST, md)
    mv = [s for s in LST.source if not a[s] and b[s]]
    print("      [%s] adding (m?: >5) turns FAILS into HOLDS on %d lists%s" % (md, len(mv), "" if not mv else
                                                                          " (smallest %r)" % sm(mv)))
# review r30 RULING-2 (equal-behaviour programs) and RULING-7 (record-is-product vs record = `&`)
SRC12 = sorted({h + "-" + k + t for h in [""] + D for k in D for t in [""] + ["+" + j for j in D]})
RP = rx_pool("R2P", r"(?P<h>\d)?-(?P<k1>[1-9])(?:\+(?P<j1>[5-9]))?|-(?P<k2>0)\+(?P<j2>[0-4])", SRC12,
             merge={"h": ["h"], "k": ["k1", "k2"], "j": ["j1", "j2"]})
RQ = rx_pool("R2Q", r"(?P<h>\d)?-(?P<k1>[1-9])(?:\+(?P<j1>[5-9]))?", SRC12,
             merge={"h": ["h"], "k": ["k1"], "j": ["j1"]})
C1 = Cond("((h?, k): h < k)", [("h", "?"), ("k", "")], lambda t, v: canon(t[0]) and canon(t[1]) and int(t[0]) < int(t[1]))
C2 = one("(j?: <5)", "j", LT5, "?")
print("   (R2) review r30 RULING-2: P = /(?<h>\\d)?-(?<k>[1-9])(?:\\+(?<j>[5-9]))?|-(?<k>0)\\+(?<j>[0-4])/, Q = its first "
      "branch, %d source rows" % len(SRC12))
for md in MODES:
    bp = {r.subj: (r.once["h"], r.once["k"], r.once["j"]) for r in RP.rows if ans([C1], RP, md)[r.subj]}
    bq = {r.subj: (r.once["h"], r.once["k"], r.once["j"]) for r in RQ.rows if ans([C1], RQ, md)[r.subj]}
    a, b = ans([C1, C2], RP, md), ans([C1, C2], RQ, md)
    d = [s for s in SRC12 if a[s] != b[s]]
    print("      [%s] P & C1 and Q & C1 equal behaviour: %s (%d rows); + C2: differ %d of %d%s" % (
        md, bp == bq, len(bp), len(d), len(SRC12), "" if not d else " (smallest %r: P %s, Q %s)" % (
            sm(d), hf(a[sm(d)]), hf(b[sm(d)]))))
S9 = rx_pool("S9", r"(?P<h>\d)?-(?:(?P<k>\d)|-(?P<j>\d))", [h + "-" + k for h in [""] + D for k in D] +
             [h + "--" + j for h in [""] + D for j in D])
print("   (S9) review r30 SIMULATE-9: /(?<h>\\d)?-(?:(?<k>\\d)|-(?<j>\\d))/, %d subjects, `((h?, k): h < k) & (j?: <3)` "
      "(a non-product joint with an unmarked partner beside a third marked label)" % len(S9.source))
for md in MODES:
    a, dm = CTX.answer([C1, one("(j?: <3)", "j", LT3, "?")], S9, md, with_dom=True)
    print("      [%s] holds on %d; on `-1` %s%s" % (md, sum(a.values()), hf(a["-1"]), "" if dm is None else
                                                  "; DOM(j) %s" % dstr(dm["j"])))
R7 = rx_pool("R7", r"(?P<h>\d)?-(?P<k1>[0-4])(?:\+(?P<j1>[5-9]))?|-(?P<k2>[5-9])\+(?P<j2>[0-4])", SRC12,
             merge={"h": ["h"], "k": ["k1", "k2"], "j": ["j1", "j2"]})
JT = Cond("((h?, k): (<5, <5))", [("h", "?"), ("k", "")], lambda t, v: LT5(t[0]) and LT5(t[1]))
print("   (R7) review r30 RULING-7: the product joint as ONE condition vs its record = `&` spelling, beside (j?: <5); "
      "%d rows" % len(R7.rows))
for md in MODES:
    a, b = ans([JT, C2], R7, md), ans([one("(h?: <5)", "h", LT5, "?"), one("(k: <5)", "k", LT5), C2], R7, md)
    a0, b0 = ans([JT], R7, md), ans([one("(h?: <5)", "h", LT5, "?"), one("(k: <5)", "k", LT5)], R7, md)
    print("      [%s] joint vs record = `&`: differ %d%s; without (j?: <5): %d" % (
        md, ndiff(a, b, R7)[0], "" if ndiff(a, b, R7)[1] is None else " (smallest %r)" % ndiff(a, b, R7)[1],
        ndiff(a0, b0, R7)[0]))

# =====================================================================================================================
print("\nPART 4: THE PROGRAM SEARCH (every program of 1-3 conditions, rev 22's pools A, B, P, LST) against rev 22's own "
      "engine, and between candidates; FAIL -> HOLD when a condition is added")
REF = {}
for line in open(sys.argv[1]):
    p, prog, s, v = line.rstrip("\n").split("\t")
    REF[(p, prog, s)] = v == "1"
hk = lambda: [one("(%s%s: %s)" % (lab, "?" if mk_ else "", sn), lab, S, "?" if mk_ else "")
              for lab in "hk" for S, sn in ((LT5, "<5"), (GT7, ">7")) for mk_ in (False, True)]
JHK = Cond("((h?, k?): h < k)", [("h", "?"), ("k", "?")],
           lambda t, v: canon(t[0]) and canon(t[1]) and int(t[0]) < int(t[1]))
EXTRA = [C1, one("(h?: !(<5))", "h", lambda x: not LT5(x), "?"), one("(k?: !(<5))", "k", lambda x: not LT5(x), "?")]
A = rx_pool("A", r"a(?P<h>\d)|b(?P<k>\d)|c", ["a" + d for d in D] + ["b" + d for d in D] + ["c"])
B = rx_pool("B", r"(?P<h>\d)?-(?P<k>\d)?", [h + "-" + k for h in [""] + D for k in [""] + D])
P = Pool("P", ["a"] + ["a;" + d for d in D] + ["b"] + ["b;" + d for d in "56789"], BR.rows and
         (lambda s: next((r for r in BR.rows if r.subj == s), None)))
LSTP = [none_m, Cond("occurs.at_most(1, ((h, m?): m < h))", none_m.labs, MLT, kind="at_most", n=1),
        Cond("some(((h, m?): m < h))", none_m.labs, MLT, kind="some"),
        Cond("((h, m?): m < h)", none_m.labs, MLT),
        Cond("(m?: <5)", [("m", "?")], lambda t, v: num(t[0]) and int(t[0]) < 5), gt5m, hlt5]
SEARCH = [(A, hk() + [JHK], EXTRA), (B, hk() + [JHK], EXTRA),
          (P, [kb, Cond("(k?: \"b\")", [("k", "?")], lambda t, v: t[0] == "b"), one("(h: <5)", "h", LT5), hm5,
               one("(h?: >7)", "h", GT7, "?")], [one("(h?: !(<5))", "h", lambda x: not LT5(x), "?")]),
          (LST, LSTP, [Cond("occurs.none(((h, m): m >= h))", [("h", ""), ("m", "")],
                            lambda t, v: num(t[0]) and num(t[1]) and int(t[1]) >= int(t[0]), kind="none")])]
ALLM = MODES + ("REV22",)
pdiff = {(x, y): [0, 0, None] for x, y in itertools.combinations(ALLM, 2)}
f2h = {m: [0, 0, None] for m in ALLM}
nprog = 0
for pool, base, extra in SEARCH:
    for withx in (False, True):
        pl = base + (extra if withx else [])
        A_ = {}
        for n_ in (1, 2, 3):
            for combo in itertools.combinations(range(len(pl)), n_):
                if withx and not any(i >= len(base) for i in combo):
                    continue
                prog = [pl[i] for i in combo]
                nm = " & ".join(c.name for c in prog)
                res = {md: ans(prog, pool, md) for md in MODES}
                if not withx:
                    res["REV22"] = {s: REF[(pool.name, nm, s)] for s in pool.source}
                A_[combo] = res
                nprog += 1
                for x, y in pdiff:
                    if x in res and y in res:
                        d = [s for s in pool.source if res[x][s] != res[y][s]]
                        if d:
                            e = pdiff[(x, y)]
                            e[0] += 1
                            e[1] += len(d)
                            cand = (len(combo), len(sm(d)), pool.name, nm, sm(d), hf(res[x][sm(d)]), hf(res[y][sm(d)]))
                            e[2] = cand if e[2] is None or cand < e[2] else e[2]
        for combo, res in A_.items():
            if len(combo) > 2:
                continue
            for j in range(len(pl)):
                c2 = tuple(sorted(combo + (j,)))
                if j in combo or c2 not in A_:
                    continue
                for md in res:
                    if md not in A_[c2]:
                        continue
                    d = [s for s in pool.source if not res[md][s] and A_[c2][md][s]]
                    f2h[md][0] += 1
                    if d:
                        f2h[md][1] += 1
                        cand = (len(c2), len(sm(d)), pool.name, " & ".join(pl[i].name for i in combo), pl[j].name, sm(d))
                        f2h[md][2] = cand if f2h[md][2] is None or cand < f2h[md][2] else f2h[md][2]
print("   %d (pool, program) cases; the REV22 column only for rev 22's own pools (no EXTRA condition)" % nprog)
for (x, y), (np_, ns, best) in sorted(pdiff.items()):
    print("   %-5s vs %-5s: %4d programs answer differently (%5d program-subject pairs)%s" % (
        x, y, np_, ns, "" if best is None else "; smallest: %s `%s` on %r (%s / %s)" % best[2:]))
for md in ALLM:
    n_, mv, best = f2h[md]
    print("   [%-5s] adding a condition turns a FAIL into a HOLD in %d of %d (program, added condition) pairs%s" % (
        md, mv, n_, "" if best is None else "; smallest: %s `%s` + `%s` on %r" % best[2:]))
print("\nEND")
