#!/usr/bin/env python3
# Lane pathimpact (2026-11-17): what the owner's BRANCH-SCOPE ruling (COND-FAMILY 2026-11-17 11:35, reading (ii))
# does to docs/design/predicates_draft.md rev 23.2. DESIGN EVIDENCE ONLY; it rules nothing and writes no draft text.
#
# THE RULE AS MODELLED (the record's words: "a condition is ONE MORE PIECE of the pattern: when it rejects, the
# pattern backtracks in PCRE's own preference order, into another branch of `|` as into any other choice point, for
# conditions inside and outside the `|`; the reported row is the first path that satisfies the conditions"):
#   * a PATH is one complete way the pattern's regex text matches from a start: every choice (each `|` branch, each
#     repeat count, each optional part) fixed; it fixes the end and every label's value (and a loop's passes);
#   * paths are listed in PCRE's preference order (a backtracking enumerator over Python's own parse of the regex,
#     PART A checks it against Python `re`: the first path is re.match's, the ends are re.fullmatch's);
#   * a condition is evaluated on a path's row; a path survives when every condition is TRUE on it (UNKNOWN rejects,
#     as a WHERE keeps TRUE only; the alternative is listed OPEN); `&` with another pattern keeps a path when the other
#     side has a path over the same stretch (left side's paths outer: OPEN, both orders run); a complement `!B` keeps
#     a path when B has no surviving path over the same stretch;
#   * WHOLE value: some surviving path from 0 ends at the text's end. SEARCHED: the leftmost start with a surviving
#     path; the report is the FIRST surviving path there (its stretch and labels). FIND-ALL: the same again from the
#     reported end (an empty report advances by one), as the earlier engines do.
# THE OTHER READINGS (for the before / after columns and the sabotage switch): (iii) = rev 23.2's text (a stretch's
# row is the first path ending there whose conditions INSIDE a `|` branch are TRUE; conditions outside judge that
# one row; anything not under a `|` reads PCRE's one parse of the stretch, section 4.5); (i) = one parse everywhere
# (the first path ending there; every condition judges it). ATOMIC (a labelled extra, predicates_future.md items 14
# and 19): the pattern commits to its first path at a start; conditions outside judge only that one.
#
# Commands (W = the worktree; run from a scratch dir under $PCREC_TMPDIR, e.g. /var/tmp/pcrec-pcrec/scratch/pathimpact):
#   timeout 900 python3 -I W/docs/dev/lanes/pathimpact_evidence/pathimpact_model.py > fwd.out
#   PATHIMPACT_SWAP=1 timeout 900 python3 -I W/.../pathimpact_model.py > swap.out
#   diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)          # must print nothing
#   PATHIMPACT_SABOTAGE=1 (forward and swapped): the diff must print something (the swap check can fail)
#   PATHIMPACT_READING=iii timeout 900 python3 -I W/.../pathimpact_model.py > iii.out   # THE RULE SWITCH: every
#     line is then computed under rev 23.2's reading; the closing "MOVED LINES" count must print 0 (and the PART B
#     engine re-run runs the engines' own one-parse rows).
# SWAP reverses every evaluation order that is not meaning: text pools, condition lists, the order lines are computed.
# PCRE's path order is MEANING and is not reversed by SWAP. SABOTAGE puts the path order under SWAP (a swapped run
# lists paths last-first), so every reported row and every count resting on "the first surviving path" depends on
# evaluation order and the swap diff must show it.
import os, sys, re, io, contextlib, types
import re._parser as SP
from re._constants import (LITERAL, NOT_LITERAL, ANY, IN, SUBPATTERN, BRANCH, MAX_REPEAT, MIN_REPEAT,
                           POSSESSIVE_REPEAT, AT, ASSERT, ASSERT_NOT, ATOMIC_GROUP, NEGATE, RANGE, CATEGORY,
                           CATEGORY_DIGIT, CATEGORY_NOT_DIGIT, CATEGORY_SPACE, CATEGORY_NOT_SPACE, CATEGORY_WORD,
                           CATEGORY_NOT_WORD, AT_BEGINNING_STRING, AT_BEGINNING, AT_END_STRING, AT_END,
                           SRE_FLAG_DOTALL)

sys.setrecursionlimit(20000)
HERE = os.path.dirname(os.path.abspath(__file__))
LANES = os.path.dirname(HERE)
SWAP = os.environ.get("PATHIMPACT_SWAP") == "1"
SAB = os.environ.get("PATHIMPACT_SABOTAGE") == "1"
RULE = os.environ.get("PATHIMPACT_READING", "ii")
if RULE not in ("i", "ii", "iii"): sys.exit("PATHIMPACT_READING must be i, ii or iii")
BEFORE = "iii"                                        # rev 23.2's text
print("ORDER: %s%s RULE=(%s)" % ("SWAPPED" if SWAP else "forward", " SABOTAGE" if SAB else "", RULE))
def order(xs): return list(reversed(list(xs))) if SWAP else list(xs)

# ======================================================================================================== PATHS
DIGITS, SPACES = set("0123456789"), set(" \t\n\r\f\v")
def _word(ch): return ch.isalnum() or ch == "_"
def _cat(c, ch):
    return {CATEGORY_DIGIT: lambda: ch in DIGITS, CATEGORY_NOT_DIGIT: lambda: ch not in DIGITS,
            CATEGORY_SPACE: lambda: ch in SPACES, CATEGORY_NOT_SPACE: lambda: ch not in SPACES,
            CATEGORY_WORD: lambda: _word(ch), CATEGORY_NOT_WORD: lambda: not _word(ch)}[c]()
def _in(items, ch):
    neg, hit = False, False
    for op, av in items:
        if op == NEGATE: neg = True
        elif op == LITERAL: hit = hit or ord(ch) == av
        elif op == RANGE: hit = hit or av[0] <= ord(ch) <= av[1]
        elif op == CATEGORY: hit = hit or _cat(av, ch)
        else: raise ValueError("class item %r" % (op,))
    return hit != neg

class Rx:
    """Every PATH of a regex from a start, in PCRE's preference order (depth-first backtracking over Python's own
    parse of the pattern). A path = (end, caps, hist): caps[g] = (start, end) of group g's LAST setting or None;
    hist = every group setting in order, with a marker at the start of each loop pass. look_atomic: a positive
    lookahead keeps only its first path (PCRE's lookarounds are atomic); False = it is backtracked into (OPEN item).
    piece: {label: cond on the label's text}: the condition checked as a piece RIGHT AFTER the label's group closes
    (OPEN item: where a rejecting condition re-enters)."""
    def __init__(self, pattern, look_atomic=True, piece=None):
        t = SP.parse(pattern)
        self.pattern, self.tree, self.look_atomic = pattern, list(t), look_atomic
        self.names = dict(t.state.groupdict)
        self.gname = {v: k for k, v in self.names.items()}
        self.ng = t.state.groups
        self.flags = t.state.flags
        self.piece = {self.names[k]: f for k, f in (piece or {}).items()}
    def paths(self, s, i):
        out = list(self._seq(self.tree, 0, s, i, (None,) * self.ng, (), self.flags))
        return list(reversed(out)) if (SAB and SWAP) else out
    def _seq(self, items, k, s, pos, caps, hist, fl):
        if k == len(items):
            yield pos, caps, hist; return
        for p2, c2, h2 in self._one(items[k], s, pos, caps, hist, fl):
            yield from self._seq(items, k + 1, s, p2, c2, h2, fl)
    def _one(self, node, s, pos, caps, hist, fl):
        op, av = node
        n = len(s)
        if op == LITERAL:
            if pos < n and ord(s[pos]) == av: yield pos + 1, caps, hist
        elif op == NOT_LITERAL:
            if pos < n and ord(s[pos]) != av: yield pos + 1, caps, hist
        elif op == ANY:
            if pos < n and (fl & SRE_FLAG_DOTALL or s[pos] != "\n"): yield pos + 1, caps, hist
        elif op == IN:
            if pos < n and _in(av, s[pos]): yield pos + 1, caps, hist
        elif op == SUBPATTERN:
            gid, add, dele, items = av
            for p2, c2, h2 in self._seq(items, 0, s, pos, caps, hist, (fl | add) & ~dele):
                if gid:
                    if gid in self.piece and self.piece[gid](s[pos:p2]) is not True: continue
                    c2 = c2[:gid] + ((pos, p2),) + c2[gid + 1:]
                    h2 = h2 + (("g", gid, pos, p2),)
                yield p2, c2, h2
        elif op == BRANCH:
            for alt in av[1]:
                yield from self._seq(alt, 0, s, pos, caps, hist, fl)
        elif op in (MAX_REPEAT, MIN_REPEAT, POSSESSIVE_REPEAT):
            lo, hi, items = av
            g = self._rep(items, lo, hi, op != MIN_REPEAT, 0, s, pos, caps, hist, fl, id(node))
            if op == POSSESSIVE_REPEAT:
                for x in g: yield x; break
            else: yield from g
        elif op == AT:
            ok = {AT_BEGINNING_STRING: pos == 0, AT_BEGINNING: pos == 0, AT_END_STRING: pos == n,
                  AT_END: pos == n or (pos == n - 1 and s[pos] == "\n")}.get(av)
            if ok is None: raise ValueError("anchor %r" % (av,))
            if ok: yield pos, caps, hist
        elif op == ASSERT:
            d, items = av
            if d != 1: raise ValueError("lookbehind")
            g = self._seq(items, 0, s, pos, caps, hist, fl)
            for _, c2, h2 in g:
                yield pos, c2, h2
                if self.look_atomic: break
        elif op == ASSERT_NOT:
            d, items = av
            if d != 1: raise ValueError("lookbehind")
            if next(self._seq(items, 0, s, pos, caps, hist, fl), None) is None: yield pos, caps, hist
        elif op == ATOMIC_GROUP:
            for x in self._seq(av, 0, s, pos, caps, hist, fl): yield x; break
        else:
            raise ValueError("op %r" % (op,))
    def _rep(self, items, lo, hi, greedy, count, s, pos, caps, hist, fl, nid):
        def more():
            if count < hi:
                for p2, c2, h2 in self._seq(items, 0, s, pos, caps, hist + (("it", nid, pos),), fl):
                    if p2 == pos and count >= lo: continue          # an empty pass past the minimum ends the loop
                    yield from self._rep(items, lo, hi, greedy, count + 1, s, p2, c2, h2, fl, nid)
        if greedy:
            yield from more()
            if count >= lo: yield pos, caps, hist
        else:
            if count >= lo: yield pos, caps, hist
            yield from more()
    def labels(self, s, caps):
        return {nm: (None if caps[g] is None else s[caps[g][0]:caps[g][1]]) for nm, g in self.names.items()}
    def passes(self, s, hist, lab):
        """The values a looped label took, one per setting, in order (each pass sets it at most once in the
        engines' loops)."""
        g = self.names[lab]
        return [s[a:b] for e in hist if e[0] == "g" and e[1] == g for a, b in [(e[2], e[3])]]

RXC = {}
def RX(p, **kw):
    k = (p, kw.get("look_atomic", True), tuple(sorted((kw.get("piece") or {}).keys())), id(kw.get("piece")))
    if k not in RXC: RXC[k] = Rx(p, **kw)
    return RXC[k]

# ======================================================================================================== LOGIC
def kand(vals):
    vals = list(vals)
    if any(v is False for v in vals): return False
    if any(v is None for v in vals): return None
    return True
def knot(v): return None if v is None else (not v)
def kor(vals):
    vals = list(vals)
    if any(v is True for v in vals): return True
    if any(v is None for v in vals): return None
    return False
def numeral(v): return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None    # section 2.2 (review r34 A1)
def lt(n): return lambda v: numeral(v) and int(v) < n
def gt(n): return lambda v: numeral(v) and int(v) > n
def eq(x): return lambda v: v == x
def test(lab, S, d=None):
    def c(r):
        v = r.get(lab)
        if v is None: v = d
        return None if v is None else bool(S(v))
    c.labs = (lab,)
    return c
def ptest(lab, S, d=None):                            # a plain condition on a looped label: Kleene AND over pass rows
    def c(r):
        ps = r["_passes"][lab]
        if not ps: ps = [None]                         # zero passes = the one null pass row (R1)
        return kand([(None if (v if v is not None else d) is None else bool(S(v if v is not None else d))) for v in ps])
    c.labs = (lab,)
    return c
def NOT(c): return lambda r: knot(c(r))
def OR(*cs): return lambda r: kor([c(r) for c in order(cs)])
def AND(*cs): return lambda r: kand([c(r) for c in order(cs)])

# ======================================================================================================== PROGRAMS
# A program is a tree of nodes. walk(s, i, inalt) yields (end, row, recs) for EVERY path of the condition-free
# skeleton, in PCRE's order; recs = the conditions' and complements' results on that path, each tagged with its
# scope ("in" = inside a `|` branch, "out" = not). The READING decides which paths survive (see accepted()).
class R:
    """A regex operand. passre (as the earlier engines): a loop's pass rows are the pass regex's matches inside the
    stretch (exact for the unambiguous loops the census covers); without it a looped label's passes are its
    settings on the path, in order (one label per pass in every loop used so)."""
    def __init__(self, p, passre=None, **kw):
        self.rx = RX(p, **kw); self.name = p; self.passre = re.compile(passre) if passre else None
    def walk(self, s, i, inalt, cmp):
        for e, caps, hist in self.rx.paths(s, i):
            row = self.rx.labels(s, caps)
            if self.passre is not None:
                pms = [pm.groupdict() for pm in self.passre.finditer(s[i:e])]
                row["_passes"] = {lab: [pm.get(lab) for pm in pms] for lab in self.passre.groupindex}
            else:
                row["_passes"] = {lab: self.rx.passes(s, hist, lab) for lab in self.rx.names}
            yield e, row, ()
class SF:                                               # a label-free filter on the stretch (contains, a whole-text test)
    def __init__(self, node, f): self.node, self.f = node, f
    def walk(self, s, i, inalt, cmp):
        sc = "in" if inalt else "out"
        for e, row, recs in self.node.walk(s, i, inalt, cmp):
            yield e, row, recs + ((sc, bool(self.f(s, i, e))),)
class Alt:
    def __init__(self, *bs): self.bs = bs
    def walk(self, s, i, inalt, cmp):
        for b in self.bs:                              # PCRE's order: every path of branch 1, then of branch 2
            yield from b.walk(s, i, True, cmp)
class Where:
    def __init__(self, node, *conds): self.node, self.conds = node, order(conds)
    def walk(self, s, i, inalt, cmp):
        sc = "in" if inalt else "out"
        for e, row, recs in self.node.walk(s, i, inalt, cmp):
            yield e, row, recs + tuple((sc, c(row)) for c in self.conds)
JOIN = {"v": "left"}                                    # OPEN: the order of paths across the two sides of `&`
class And:
    def __init__(self, a, b): self.a, self.b = a, b
    def walk(self, s, i, inalt, cmp):
        A = list(self.a.walk(s, i, inalt, cmp)); Bp = list(self.b.walk(s, i, inalt, cmp))
        if JOIN["v"] == "left":
            for e1, r1, c1 in A:
                for e2, r2, c2 in Bp:
                    if e1 == e2: yield e1, merge(r1, r2), c1 + c2
        else:
            for e2, r2, c2 in Bp:
                for e1, r1, c1 in A:
                    if e1 == e2: yield e1, merge(r1, r2), c1 + c2
def merge(r1, r2):
    r = dict(r1); r.update({k: v for k, v in r2.items() if k != "_passes"})
    r["_passes"] = dict(r1.get("_passes", {})); r["_passes"].update(r2.get("_passes", {}))
    return r
class Diff:                                             # `node & !B`: B's surviving paths over the same stretch
    def __init__(self, node, B): self.node, self.B = node, B
    def walk(self, s, i, inalt, cmp):
        sc = "in" if inalt else "out"
        for e, row, recs in self.node.walk(s, i, inalt, cmp):
            yield e, row, recs + ((sc, not stretch_ok(self.B, s, i, e, cmp)),)
class Atomic:                                           # commits to the first path (its own conditions applied inside)
    def __init__(self, node): self.node = node
    def walk(self, s, i, inalt, cmp):
        for e, row, recs in self.node.walk(s, i, inalt, cmp):
            if all(v is True for _, v in recs):
                yield e, row, (); break

CUR = {"rd": RULE}                                    # the reading in force for nested programs (complement, lookaheads)
UNK = {"v": "U1"}                                     # OPEN: does UNKNOWN backtrack like FALSE?
def accepted(P, s, i, reading=None, cmp="C1"):
    """The surviving (end, row) pairs at start i, in report order, under a reading."""
    reading = reading or CUR["rd"]
    prev = CUR["rd"]; CUR["rd"] = reading
    try: paths = list(P.walk(s, i, False, cmp))
    finally: CUR["rd"] = prev
    if reading == "ii":
        if UNK["v"] == "U1":                             # UNKNOWN rejects and the pattern backtracks, as on FALSE
            return [(e, row) for e, row, recs in paths if all(v is True for _, v in recs)]
        out = []                                         # U2 (OPEN candidate): an UNKNOWN path ends the tries at this start
        for e, row, recs in paths:
            if all(v is True for _, v in recs): out.append((e, row))
            elif any(v is None for _, v in recs) and not any(v is False for _, v in recs): break
        return out
    out, seen = [], set()
    for k, (e, row, recs) in enumerate(paths):
        if e in seen: continue
        seen.add(e)
        if reading == "i": kd = k                        # (i): the first path at e, whatever its conditions say
        else:                                            # (iii): the first path at e whose INNER conditions are TRUE
            kd = next((k2 for k2 in range(k, len(paths)) if paths[k2][0] == e
                       and all(v is True for sc, v in paths[k2][2] if sc == "in")), None)
            if kd is None: continue
        if all(v is True for sc, v in paths[kd][2] if reading == "i" or sc == "out"): out.append((kd, e, paths[kd][1]))
    return [(e, row) for _, e, row in sorted(out, key=lambda x: x[0])]   # reported at the designated path's place
def stretch_ok(B, s, i, e, cmp):
    """Does B keep the stretch (i, e)? C1: B judged by the rule (some surviving path under (ii)); C2: B judged by its
    one parse of the stretch (the first path ending at e), as rev 23.2 judged every program."""
    return any(e2 == e for e2, _ in accepted(B, s, i, CUR["rd"] if cmp == "C1" else "i", cmp))

def whole(P, s, reading=None, cmp="C1"):
    return any(e == len(s) for e, _ in accepted(P, s, 0, reading, cmp))
def search(P, s, pos=0, reading=None, cmp="C1"):
    for i in range(pos, len(s) + 1):
        a = accepted(P, s, i, reading, cmp)
        if a: return i, a[0][0], a[0][1]
    return None
def findall(P, s, reading=None, cmp="C1"):
    out, pos = [], 0
    while pos <= len(s):
        r = search(P, s, pos, reading, cmp)
        if r is None: break
        out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
    return out
def show_labels(row, labs): return "" if not labs else " [" + ", ".join("%s=%s" % (l, row.get(l)) for l in labs) + "]"
def hs(P, s, reading=None, cmp="C1", labs=()):
    r = search(P, s, 0, reading, cmp)
    return "%s / %s" % ("HOLDS" if whole(P, s, reading, cmp) else "FAILS",
                        "FAILS" if r is None else "HOLDS `%s`@%d%s" % (s[r[0]:r[1]], r[0], show_labels(r[2], labs)))
def fa(P, s, reading=None, cmp="C1", labs=()):
    return "[" + ", ".join("`%s`@%d%s" % (s[i:j], i, show_labels(r, labs)) for i, j, r in findall(P, s, reading, cmp)) + "]"
def ans3(P, s, reading=None, cmp="C1", labs=()):
    return "%s / FIND-ALL %s" % (hs(P, s, reading, cmp, labs), fa(P, s, reading, cmp, labs))

# ======================================================================================================== OUTPUT
LINES, MOVED = {}, []
def emit(k, t): LINES[k] = t
def mv(k, text, f):
    """A line whose answer depends on the reading: computed under the RULE and under rev 23.2's (iii)."""
    a, b = f(RULE), f(BEFORE)
    if a != b: MOVED.append(k)
    emit(k, "  %s %s: %s%s" % ("MOVED" if a != b else "same ", text, a, "" if a == b else "   <- rev 23.2 (iii): " + b))
def flush():
    for k in sorted(LINES, key=lambda k: tuple(str(x) for x in k)): print(LINES[k])
    LINES.clear()
def strings(alpha, n):
    out, cur = [""], [""]
    for _ in range(n):
        cur = [c + a for c in cur for a in alpha]; out += cur
    return out
def cnt(pool, f):
    hits = [x for x in order(pool) if f(x)]
    return len(hits), (min(hits, key=lambda x: (len(x), x)) if hits else None)
def MODES(): return order(["WHOLE", "SEARCHED", "FIND-ALL"])
def ansmode(mode, P, s, reading=None, cmp="C1", labs=()):
    if mode == "WHOLE": return whole(P, s, reading, cmp)
    if mode == "SEARCHED":
        r = search(P, s, 0, reading, cmp)
        return None if r is None else (r[0], r[1], tuple((l, r[2].get(l)) for l in labs))
    return tuple((i, j, tuple((l, r.get(l)) for l in labs)) for i, j, r in findall(P, s, reading, cmp))

# ======================================================================================================== PART B HOOKS
# The four earlier engines (predspec23, predspec23b, predspec23c, searchrow) are re-run THROUGH lane predspec23d's
# script (its canonical-numeral fixes, review r34 A1, are the draft's current numbers): 23d's source is read, its
# FIXES dict is extended with this lane's replacements (each must match exactly once, 23d's own check), and it is
# executed in memory. Nothing is edited on disk. The replacements:
#   * every stretch parse `m = P.A.fullmatch(s[i:j])` goes through PI_FULL, which records the CENSUS: for each regex,
#     how many stretches the engines parse, how many have 2+ paths, how many 2+ distinct label sets, and whether the
#     path enumerator's first path equals Python's fullmatch (the control);
#   * each engine's ACCEPT (predspec23 accept, predspec23b accept, searchrow whole) takes ANY path of the stretch
#     whose conditions are all TRUE under RULE (ii), the one parse under (iii) / (i);
#   * each ends_pref goes through PI_ENDS: under (ii) the ends in PCRE's path order, else the engine's own order; the
#     census records every start where the two orders differ.
CENSUS = {}
def _cen(p): return CENSUS.setdefault(p, {"stretch": 0, "multi": 0, "amb": 0, "ctl_bad": 0, "starts": 0, "ord_bad": 0, "first_bad": None})
FULLMEMO, ENDMEMO = {}, {}
def PI_FULL(A, sub):
    m = A.fullmatch(sub)
    c = _cen(A.pattern)
    k = (A.pattern, sub)
    if k not in FULLMEMO:                             # (multi, amb, ctl_bad) of this stretch text; counted per call
        rx = RX(A.pattern)
        ps = [caps for e, caps, hist in rx.paths(sub, 0) if e == len(sub)]
        bad = int((m is None) != (not ps)) + int(bool(m is not None and ps and rx.labels(sub, ps[0]) != m.groupdict()))
        FULLMEMO[k] = (int(len(ps) > 1), int(len({tuple(sorted(rx.labels(sub, cp).items())) for cp in ps}) > 1), bad)
    multi, amb, bad = FULLMEMO[k]
    c["ctl_bad"] += bad
    if m is not None:
        c["stretch"] += 1; c["multi"] += multi; c["amb"] += amb
        if amb and c["first_bad"] is None: c["first_bad"] = sub
    return m
ROWMEMO = {}
def PI_ROWS(P, s, i, j, rowfn):
    r0 = rowfn(P, s, i, j)
    if r0 is None: return []
    if RULE != "ii": return [r0]
    sub = s[i:j]; k = (P.A.pattern, sub)
    if k not in ROWMEMO:
        rx = RX(P.A.pattern)
        ROWMEMO[k] = [rx.labels(sub, caps) for e, caps, hist in rx.paths(sub, 0) if e == len(sub)]
    rows = []
    for lab in ROWMEMO[k]:
        r = dict(r0); r.update(lab); rows.append(r)
    return rows or [r0]
ENDS_MODE = {"v": os.environ.get("PATHIMPACT_ENDS", "path")}   # "engine": keep the engines' own end order under (ii)
def PI_ENDS(P, s, i, old):
    ends = old(P, s, i)
    A = P.alt[0].A if getattr(P, "alt", None) is not None else P.A
    c = _cen(A.pattern); c["starts"] += 1
    k = (A.pattern, s, i)
    if k not in ENDMEMO:
        pe = []
        for e, _, _ in RX(A.pattern).paths(s, i):
            if e not in pe: pe.append(e)
        ENDMEMO[k] = pe
    pe = ENDMEMO[k]
    if pe != ends: c["ord_bad"] += 1
    return pe if (RULE == "ii" and ENDS_MODE["v"] == "path") else ends
PI_FIXES = {
    "predspec23": [
        ("def row_at(P, s, i, j):\n    m = P.A.fullmatch(s[i:j])\n", "def row_at(P, s, i, j):\n    m = PI_FULL(P.A, s[i:j])\n"),
        ("def cl_row(P, s, i, j):\n    m = P.A.fullmatch(s[i:j])\n", "def cl_row(P, s, i, j):\n    m = PI_FULL(P.A, s[i:j])\n"),
        ("    r = row_at(P, s, i, j)\n    if r is None: return False\n    if not all(c(r) is True for c in P.conds): return False\n",
         "    rs = PI_ROWS(P, s, i, j, row_at)\n    if not rs: return False\n    if not any(all(c(r) is True for c in P.conds) for r in rs): return False\n"),
        ("def ends_pref(P, s, i):\n", "def ends_pref(P, s, i): return PI_ENDS(P, s, i, _pi_old_ends_pref)\ndef _pi_old_ends_pref(P, s, i):\n"),
    ],
    "predspec23b": [
        ("def row(P, s, i, j):\n    m = P.A.fullmatch(s[i:j])\n", "def row(P, s, i, j):\n    m = PI_FULL(P.A, s[i:j])\n"),
        ("    r = row(P, s, i, j)\n    if r is None: return False\n    if not all(c(r) is True for c in P.conds): return False\n",
         "    rs = PI_ROWS(P, s, i, j, row)\n    if not rs: return False\n    if not any(all(c(r) is True for c in P.conds) for r in rs): return False\n"),
        ("def ends_pref(P, s, i):\n", "def ends_pref(P, s, i): return PI_ENDS(P, s, i, _pi_old_ends_pref)\ndef _pi_old_ends_pref(P, s, i):\n"),
    ],
    "predspec23c": [],
    "searchrow": [
        ("def row_at(P, s, i, j):\n    m = P.A.fullmatch(s[i:j])", "def row_at(P, s, i, j):\n    m = PI_FULL(P.A, s[i:j])"),
        ("    r = row_at(P, s, i, j)\n    return r is not None and conds_ok(P, r) and not any(whole(B, s, i, j) for B in P.comps)\n",
         "    rs = PI_ROWS(P, s, i, j, row_at)\n    return bool(rs) and any(conds_ok(P, r) for r in rs) and not any(whole(B, s, i, j) for B in P.comps)\n"),
        ("def ends_pref(P, s, i):\n", "def ends_pref(P, s, i): return PI_ENDS(P, s, i, _pi_old_ends_pref)\ndef _pi_old_ends_pref(P, s, i):\n"),
    ],
}
def run_23d_patched():
    path = os.path.join(LANES, "predspec23d_evidence", "predspec23d_model.py")
    src = open(path).read()
    for a, b in [("def load(name, fixes=True):\n", "for _k, _v in PI_FIXES.items(): FIXES[_k] = FIXES[_k] + _v\ndef load(name, fixes=True):\n"),
                 ("    mod.PS23D_CANON = CANON ", "    mod.PI_FULL, mod.PI_ROWS, mod.PI_ENDS = PI_FULL, PI_ROWS, PI_ENDS; mod.PS23D_CANON = CANON ")]:
        if src.count(a) != 1: sys.exit("pathimpact: 23d hook site matched %d times: %r" % (src.count(a), a))
        src = src.replace(a, b)
    mod = types.ModuleType("predspec23d_model"); mod.__file__ = path
    mod.PI_FIXES, mod.PI_FULL, mod.PI_ROWS, mod.PI_ENDS = PI_FIXES, PI_FULL, PI_ROWS, PI_ENDS
    saved = {k: os.environ.get(k) for k in ("PREDSPEC23D_SWAP", "PREDSPEC23D_SABOTAGE")}
    os.environ["PREDSPEC23D_SWAP"] = "0"; os.environ["PREDSPEC23D_SABOTAGE"] = "0"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(src, path + " [hooked by pathimpact]", "exec"), mod.__dict__)
    for k, v in saved.items():
        if v is None: os.environ.pop(k, None)
        else: os.environ[k] = v
    return mod, buf.getvalue()

# ======================================================================================================== DEFINITIONS
T2P = r"(?P<h>\d{1,2})(?::(?P<m>\d\d))?"
Bd, Ad = R(r"(?P<l>\d\d)"), R(r"(?P<l>\d)\d")                 # B := /(?<l>\d\d)/, A := /(?<l>\d)\d/ (review r34)
Ba, Aa = R(r"(?P<l>aa)"), R(r"(?P<l>a)a")                     # L60's B and A
PAB, PABL, PA1 = R(r"(?P<a>\d+)(?P<b>\d+)"), R(r"(?P<a>\d+?)(?P<b>\d+)"), R(r"(?P<a>1)(?P<b>\d+)")
PCD = R(r"(?P<c>\d+)(?P<d>\d+)")
NL = R(r"(?P<l>\d+)")
T2 = R(T2P)
def late_f(r):                                                  # ((h, m): >= (9, 30)), canonical; absent part -> UNKNOWN
    h, m = r.get("h"), r.get("m")
    if h is None or m is None: return None
    return numeral(h) and numeral(m) and (int(h), int(m)) >= (9, 30)
late_f.labs = ("h", "m")
def between(a, b): return lambda v: numeral(v) and a <= int(v) <= b
W = Where
DIG3 = strings("0129", 3)                                       # 85 (lane predspec23d's DPOOL)
DIG4 = strings("0129", 4)                                       # 341
DSP = strings("129 ", 5)                                        # 1,365: several-match subjects
AB4 = strings("ab", 4)                                          # 31
RG3 = strings("37;", 5)                                         # 364 (the earlier engines' REP pool)

# ======================================================================================================== PART A
print("== PART A: the path enumerator against Python `re` (first path = re.match; per stretch, the first path = re.fullmatch's parse; ends = re.fullmatch's)")
CTL = [(Bd, DIG4), (Ad, DIG4), (Ba, AB4), (Aa, AB4), (PAB, DIG4), (PABL, DIG4), (PA1, DIG4), (NL, DIG4),
       (R(r"(?P<b>\d+)(?P<a>\d)?"), DIG4), (R(r"(?=(?P<x>\d+))\d"), DIG4), (R(r"(?:(?P<h>\d);)*"), RG3),
       (R(r"(?:(?P<h>\d{1,2}),?)+"), strings("12,", 5)), (R(r"(?:[\s\S]*?(?P<hit>\d+))*[\s\S]*"), strings("1x2", 4)),
       (T2, [h + (":" + m if m else "") for h in ["", "1", "9", "12", "09"] for m in [None, "00", "30", "5"]] + ["9:30 1", "1 9:3"])]
for node, pool in order(CTL):
    rx, cre = node.rx, re.compile(node.rx.pattern)
    st = sb = bad = multi = amb = 0
    for s in order(pool):
        for i in range(len(s) + 1):
            st += 1
            ps = rx.paths(s, i); m = cre.match(s, i)
            if (m is None) != (not ps) or (m is not None and (ps[0][0] != m.end() or rx.labels(s, ps[0][1]) != m.groupdict())): bad += 1
            for j in range(i, len(s) + 1):
                sub = s[i:j]; fm = cre.fullmatch(sub)
                pj = [c for e, c, h in rx.paths(sub, 0) if e == len(sub)]
                if (fm is None) != (not pj) or (fm is not None and rx.labels(sub, pj[0]) != fm.groupdict()): bad += 1
                if fm is not None:
                    sb += 1; multi += len(pj) > 1; amb += len({tuple(sorted(rx.labels(sub, c).items())) for c in pj}) > 1
    emit((0, rx.pattern), "  CONTROL /%s/ over %d texts: %d starts, %d stretches; MISMATCHES %d; stretches with 2+ paths %d, with 2+ label sets %d" % (rx.pattern, len(pool), st, sb, bad, multi, amb))
flush()

# ======================================================================================================== PART B
print("== PART B: the four earlier engines re-run under the rule (through predspec23d's script, its canonical fixes kept); BEFORE = predspec23d_model.out as committed")
def body23d(text): return [l for l in text.splitlines() if not l.startswith("ORDER:")]
BEFORE_23D = body23d(open(os.path.join(LANES, "predspec23d_evidence", "predspec23d_model.out")).read())
def part_b_diff(after):
    import difflib
    moved = []
    for tag, a1, a2, b1, b2 in difflib.SequenceMatcher(None, BEFORE_23D, after, autojunk=False).get_opcodes():
        if tag != "equal": moved.append((BEFORE_23D[a1:a2], after[b1:b2]))
    return moved
_, OUT_B = run_23d_patched()
MOVED_B = part_b_diff(body23d(OUT_B))
print("  ENGINE LINES THAT MOVE (predspec23d's PART B / X / Y lines, every engine line in full): %d hunks" % len(MOVED_B))
for bef, aft in MOVED_B:
    for l in bef: print("    BEFORE " + l)
    for l in aft: print("    AFTER  " + l)
print("  CENSUS (every stretch the engines parse; 'paths' = stretches with 2+ paths; 'labels' = with 2+ label sets; 'order' = starts where PCRE's path order of ends differs from the engine's ends_pref):")
for p in sorted(CENSUS):
    c = CENSUS[p]
    print("    /%s/: stretches %d, paths %d, labels %d, control mismatches %d; starts %d, order %d%s" % (
        p, c["stretch"], c["multi"], c["amb"], c["ctl_bad"], c["starts"], c["ord_bad"], "" if c["first_bad"] is None else ", first 2+ labels `%s`" % c["first_bad"]))
amb_rx = sorted(p for p, c in CENSUS.items() if c["amb"])
print("  REGEXES WITH A STRETCH OF 2+ LABEL SETS: %d of %d (%s)" % (len(amb_rx), len(CENSUS), "; ".join("/%s/" % p for p in amb_rx)))
if RULE == "ii":
    CENSUS.clear(); ENDS_MODE["v"] = "engine"
    _, OUT_E = run_23d_patched()
    ENDS_MODE["v"] = "path"
    ME = part_b_diff(body23d(OUT_E))
    print("  ORDER CONTROL: the same run with the engines' own end order kept: %d hunks (%s)" % (len(ME), "identical to the path-order run" if ME == MOVED_B else "DIFFERENT from the path-order run"))

# ======================================================================================================== PART C
print("== PART C: the draft's worked lines on patterns with 2+ paths over one stretch (rev 23.2 = reading (iii) vs the RULE); WHOLE / SEARCHED / FIND-ALL")
l20, l10, g50, la = test("l", lt(20)), test("l", lt(10)), test("l", gt(50)), test("l", eq("a"))
a1, a12 = test("a", eq("1")), test("a", eq("12"))
CW = [("C01 L60 `(B | A) & (l: \"a\")` on `aa` (CF:953-955's ruled reject)", W(Alt(Ba, Aa), la), "aa", ("l",)),
      ("C02 L60 `(A | B) & (l: \"a\")` on `aa`", W(Alt(Aa, Ba), la), "aa", ("l",)),
      ("C03 L60 inner `(B & (l: \"a\")) | (A & (l: \"a\"))` on `aa`", Alt(W(Ba, la), W(Aa, la)), "aa", ("l",)),
      ("C04 section 4.5 / note (a) / L59 `P & (a: \"1\")` on `123`", W(PAB, a1), "123", ("a", "b")),
      ("C05 section 4.5 `P & (a: \"12\")` on `123`", W(PAB, a12), "123", ("a", "b")),
      ("C06 L60 lazy `/(?<a>\\d+?)(?<b>\\d+)/ & (a: \"1\")` on `123`", W(PABL, a1), "123", ("a", "b")),
      ("C07 L59 constraint written in `/(?<a>1)(?<b>\\d+)/` on `123`", PA1, "123", ("a", "b")),
      ("C08 L34 / O33 `P & (a: <5) & (b: <5)` on `123`", W(PAB, test("a", lt(5)), test("b", lt(5))), "123", ("a", "b")),
      ("C09 shown to the owner `(B | A) & (l: <20)` on `25 13`", W(Alt(Bd, Ad), l20), "25 13", ("l",)),
      ("C10 R.8 item 6 `(B | A) & (l: <20)` on `25`", W(Alt(Bd, Ad), l20), "25", ("l",)),
      ("C11 R.8 item 6 `(B & (l: <20)) | (A & (l: <20))` on `25`", Alt(W(Bd, l20), W(Ad, l20)), "25", ("l",)),
      ("C12 R.1.4 cost (2) `(B | A) & (l: <10)` on `12`", W(Alt(Bd, Ad), l10), "12", ("l",)),
      ("C13 R.1.4 cost (2) `((B & (l: >50)) | A) & (l: <10)` on `12`", W(Alt(W(Bd, g50), Ad), l10), "12", ("l",)),
      ("C14 the owner's 25-13 example, find-all on `13 25`", W(Alt(Bd, Ad), l20), "13 25", ("l",))]
for nm, P, s, labs in order(CW):
    mv((1, nm), nm, lambda rd, P=P, s=s, labs=labs: ans3(P, s, rd, labs=labs))
# section 5.6's validating assertions: `"123" & P & (a: v)` holds on the value `123` (WHOLE)
for v in order(["12", "1"]):
    mv((2, v), "C15 section 5.6 `@assert.%s(\"123\" & P & (a: \"%s\"))`" % ("some" if v == "12" else "none", v),
       lambda rd, v=v: ("PASSES" if (whole(W(PAB, test("a", eq(v))), "123", rd) == (v == "12")) else "FAILS") + " (`\"123\" & P & (a: \"%s\")` %s)" % (v, "HOLDS" if whole(W(PAB, test("a", eq(v))), "123", rd) else "FAILS"))
flush()
# CROSS-CHECK against lane predspec23d's own branch-scope evaluator (a separate implementation): its PART Y lines and
# its 85-text counts, every reading.
emit((4, -1), "  CROSS-CHECK vs predspec23d PART Y (alt_accept, a separate implementation) and predspec23c's `when` engine, every reading:")
YPX = [("(B | A) & (l: <20)", W(Alt(Bd, Ad), l20), "25"), ("(B & (l: <20)) | (A & (l: <20))", Alt(W(Bd, l20), W(Ad, l20)), "25"),
       ("(B | A) & (l: <10)", W(Alt(Bd, Ad), l10), "12"), ("((B & (l: >50)) | A) & (l: <10)", W(Alt(W(Bd, g50), Ad), l10), "12"),
       ("L60 (B | A) & (l: \"a\")", W(Alt(Ba, Aa), la), "aa"), ("(B & (l: \"a\")) | (A & (l: \"a\"))", Alt(W(Ba, la), W(Aa, la)), "aa")]
for nm, P, s in order(YPX):
    emit((4, 0, nm), "    %s on `%s`: (i) %s ; (ii) %s ; (iii) %s" % (nm, s, hs(P, s, "i"), hs(P, s, "ii"), hs(P, s, "iii")))
for rd in order(["i", "ii", "iii"]):
    for mode in order(["WHOLE", "SEARCHED holds", "SEARCHED reported row"]):
        f = {"WHOLE": lambda P, s: whole(P, s, rd), "SEARCHED holds": lambda P, s: search(P, s, 0, rd) is not None,
             "SEARCHED reported row": lambda P, s: (search(P, s, 0, rd) or (None, None))[:2]}[mode]
        d, w = cnt(DIG3, lambda s: f(W(Alt(Bd, Ad), l20), s) != f(Alt(W(Bd, l20), W(Ad, l20)), s))
        emit((4, 1, rd, mode), "    reading (%s) %s (85 texts): `(B | A) & (l: <20)` vs `(B & (l: <20)) | (A & (l: <20))` differ %d first %r" % (rd, mode, d, w))

# `when`'s expansion vs predspec23c's branch-major engine (KH, p = (k: between(3, 7))), every reading of mine.
KHP_ = r";(?P<h>\d)"
KH = R(r"(?P<k>\d)(?:;(?P<h>\d))*", passre=KHP_)
KHPOOL = [k + "".join(";" + x for x in t) for k in "0123456789" for t in [()] + [(a,) for a in "0123456789"] + [(a, b) for a in "0123456789" for b in "0123456789"]]
pk = test("k", between(3, 7))
def when_body(c): return Alt(W(KH, c, pk), Diff(KH, W(KH, c)))
def when_filter(c):                                         # `x & when(c, p)`: x's paths, kept when `c & p` or not a row of `x & c`
    return W(KH, lambda r, c=c: True if (c(r) is True and pk(r) is True) else (c(r) is not True))
with contextlib.redirect_stdout(io.StringIO()):
    sys.path.insert(0, os.path.join(LANES, "predspec23c_evidence")); sys.path.insert(0, os.path.join(LANES, "predspec23b_evidence"))
    sys.modules.pop("predspec23b_model", None); sys.modules.pop("predspec23_model", None)
    for k in ("PREDSPEC23C_SWAP", "PREDSPEC23C_SABOTAGE", "PREDSPEC23B_SWAP", "PREDSPEC23B_SABOTAGE", "PREDSPEC23_SWAP", "PREDSPEC23_SABOTAGE"):
        os.environ[k] = "0"
    import predspec23c_model as C23
B23 = C23.B
for cn, c, bc in order([("(h: <5)", ptest("h", lt(5)), B23.ptest("h", B23.lt(5))), ("(h = 0: <5)", ptest("h", lt(5), "0"), B23.ptest("h", B23.lt(5), "0"))]):
    BW = B23.when_body(bc, B23.pk)
    for rd in order(["i", "ii", "iii"]):
        dr, wr = cnt(KHPOOL, lambda s: (search(when_body(c), s, 0, rd) or (None, None))[:2] != (B23.searched(BW) if False else C23.search_bm(BW, s, 0) or (None, None))[:2])
        dw, ww = cnt(KHPOOL, lambda s: whole(when_body(c), s, rd) != B23.whole(BW, s))
        df, wf = cnt(KHPOOL, lambda s: [x[:2] for x in findall(when_body(c), s, rd)] != B23.findall(BW, s))
        emit((4, 2, cn, rd), "    `when` expansion, c = %s, reading (%s) vs predspec23c's branch-major engine over KH (1,110): WHOLE differ %d first %r; SEARCHED report differ %d first %r; FIND-ALL differ %d first %r" % (cn, rd, dw, ww, dr, wr, df, wf))
    for s in order(["5;1;9", "3;0;5"]):
        mv((3, cn, s), "C16 `when` expansion `(x & c & p) | (x & !(x & c))`, c = %s, on `%s`" % (cn, s), lambda rd, c=c, s=s: ans3(when_body(c), s, rd))
        mv((3, cn, s, "F"), "C17 `x & when(c, p)` (the filter form), c = %s, on `%s`" % (cn, s), lambda rd, c=c, s=s: ans3(when_filter(c), s, rd))
flush()

# ======================================================================================================== PART D
print("== PART D: properties over text sets (RULE; rev 23.2's (iii) beside it); WHOLE / SEARCHED (reported row: stretch and labels) / FIND-ALL (hit list)")
def report(P, s, rd, labs):
    r = search(P, s, 0, rd)
    return None if r is None else (r[0], r[1], tuple((l, r[2].get(l)) for l in labs))
def hits(P, s, rd, labs=()): return [(i, j, tuple((l, r.get(l)) for l in labs)) for i, j, r in findall(P, s, rd)]
def three(rd, P1, P2, pool, labs):
    out = []
    for mode in ["WHOLE", "SEARCHED", "FIND-ALL"]:
        f = {"WHOLE": lambda P, s: whole(P, s, rd), "SEARCHED": lambda P, s: report(P, s, rd, labs),
             "FIND-ALL": lambda P, s: hits(P, s, rd, labs)}[mode]
        d, w = cnt(pool, lambda s: f(P1, s) != f(P2, s))
        out.append("%s %d%s" % (mode, d, "" if w is None else " (first %r)" % w))
    return "differ " + "; ".join(out)
# D1: whether a value holds = some path satisfies the conditions; checked against an INDEPENDENT oracle that splits
# the stretch by hand (no path enumerator, no regex engine beyond fullmatch of one branch).
def split_oracle(c):
    def ok(t): return len(t) >= 2 and t.isdigit() and any(c({"a": t[:k], "b": t[k:]}) is True for k in range(1, len(t)))
    return ok
def alt_oracle(c):
    def ok(t): return any(re.fullmatch(rx, t) and c({"l": re.fullmatch(rx, t).group("l")}) is True for rx in (r"(?P<l>\d\d)", r"(?P<l>\d)\d"))
    return ok
for nm, P, ok in order([("P & (a: \"1\")", W(PAB, a1), split_oracle(a1)),
                        ("P & (a: <5) & (b: <5)", W(PAB, test("a", lt(5)), test("b", lt(5))), split_oracle(AND(test("a", lt(5)), test("b", lt(5))))),
                        ("P & NOT (a: \"1\")", W(PAB, NOT(a1)), split_oracle(NOT(a1))),
                        ("(B | A) & (l: <20)", W(Alt(Bd, Ad), l20), alt_oracle(l20)),
                        ("(B | A) & (l: <10)", W(Alt(Bd, Ad), l10), alt_oracle(l10))]):
    def line(rd, P=P, ok=ok):
        dw, ww = cnt(DIG4, lambda s: whole(P, s, rd) != ok(s))
        ds, ws = cnt(DIG4, lambda s: (search(P, s, 0, rd) is not None) != any(ok(s[i:j]) for i in range(len(s) + 1) for j in range(i, len(s) + 1)))
        return "vs the some-split oracle over DIG4 (341): WHOLE differ %d%s; SEARCHED holds differ %d%s" % (dw, "" if ww is None else " first %r" % ww, ds, "" if ws is None else " first %r" % ws)
    mv((1, nm), "D1 HOLDS = SOME PATH `%s`" % nm, line)
# D2: `&` distributes over `|`.
for cn, c in order([("(l: <20)", l20), ("NOT (l: <20)", NOT(l20)), ("(l: \"1\")", test("l", eq("1")))]):
    for pn, pool in order([("DIG4 (341)", DIG4), ("DSP (1,365)", DSP)]):
        mv((2, cn, pn), "D2 DISTRIBUTES `(B | A) & %s` vs `(B & %s) | (A & %s)` over %s" % (cn, cn, cn, pn),
           lambda rd, c=c, pool=pool: three(rd, W(Alt(Bd, Ad), c), Alt(W(Bd, c), W(Ad, c)), pool, ("l",)))
# D3: the array-of-filters equation `t & [f, g]` = `(t & f) | (t & g)` with two DIFFERENT conditions (f = (l: <20),
# g = (l: >50)); `[f, g]` read as one condition, Kleene OR (the draft's condition-or).
for tn, t in order([("/(?<l>\\d\\d)/", Bd), ("/(?<l>\\d+)/", NL), ("B | A", Alt(Bd, Ad))]):
    for s in order(["75", "75 13"]):
        mv((3, tn, s), "D3 ARRAY `t & [f, g]` vs `(t & f) | (t & g)`, t = %s, on `%s`" % (tn, s),
           lambda rd, t=t, s=s: "%s  vs  %s" % (ans3(W(t, OR(l20, g50)), s, rd, labs=("l",)), ans3(Alt(W(t, l20), W(t, g50)), s, rd, labs=("l",))))
    for pn, pool in order([("DIG4 (341)", DIG4), ("DSP (1,365)", DSP)]):
        mv((3, tn, pn), "D3 ARRAY t = %s over %s" % (tn, pn), lambda rd, t=t, pool=pool: three(rd, W(t, OR(l20, g50)), Alt(W(t, l20), W(t, g50)), pool, ("l",)))
# D4: "adding a condition never admits", position by position (admit = the extended program holds where the base fails).
b5, a5 = test("b", lt(5)), test("a", lt(5))
qb = W(PAB, a5); qx = W(PAB, a5, a1)
POS = [("top of the `&` chain", W(PAB, a5), W(PAB, a5, b5), DIG4),
       ("inside a `|` branch whose label an outer test reads", W(Alt(Bd, Ad), l10), W(Alt(W(Bd, g50), Ad), l10), DIG4),
       ("inside an `&` operand", And(W(PAB, a5), R(r"\d{3}")), And(W(PAB, a5, b5), R(r"\d{3}")), DIG4),
       ("through a twice-used program `q & !(q & (b: <5))`", Diff(qb, W(qb, b5)), Diff(qx, W(qx, b5)), DIG4),
       ("inside a complement `P & !(P & c)`", Diff(PAB, W(PAB, a1)), Diff(PAB, W(PAB, a1, test("b", eq("23")))), DIG4),
       ("under NOT `P & NOT c`", W(PAB, NOT(a1)), W(PAB, NOT(AND(a1, test("b", eq("23"))))), DIG4),
       ("a `|` branch, no outer test", Alt(Bd, Ad), Alt(W(Bd, g50), Ad), DIG4)]
def admits(rd, base, ext, pool):
    out = []
    for mode in ["WHOLE", "SEARCHED", "FIND-ALL 2+"]:
        f = {"WHOLE": lambda P, s: whole(P, s, rd), "SEARCHED": lambda P, s: search(P, s, 0, rd) is not None,
             "FIND-ALL 2+": lambda P, s: len(findall(P, s, rd)) >= 2}[mode]
        d, w = cnt(pool, lambda s: f(ext, s) and not f(base, s))
        out.append("%s %d%s" % (mode, d, "" if w is None else " (first %r)" % w))
    return "admits " + "; ".join(out)
for nm, base, ext, pool in order(POS):
    mv((4, nm), "D4 ADDING A CONDITION %s" % nm, lambda rd, base=base, ext=ext, pool=pool: admits(rd, base, ext, pool))
mv((4, "zz-findall"), "D4 ADDING A CONDITION in a find-all place: `/(?<l>\\d+)/` vs `& (l: <100)` over DSP (1,365)",
   lambda rd: admits(rd, NL, W(NL, test("l", lt(100))), DSP))
# D5: find-all hits can re-split (a hit of the filtered program that is not a hit of the plain one).
for nm, base, ext, pool in order([("`(B | A)` vs `(B | A) & (l: <20)`", Alt(Bd, Ad), W(Alt(Bd, Ad), l20), DSP),
                                  ("`P` vs `P & (a: \"1\")`", PAB, W(PAB, a1), DSP),
                                  ("`/(?<l>\\d+)/` vs `& (l: <100)`", NL, W(NL, test("l", lt(100))), DSP)]):
    mv((5, nm), "D5 RE-SPLIT over DSP (1,365) %s" % nm,
       lambda rd, base=base, ext=ext, pool=pool: (lambda d: "texts with a hit not among the plain hits %d (first %r)" % d)(
           cnt(pool, lambda s: not set((i, j) for i, j, _ in findall(ext, s, rd)) <= set((i, j) for i, j, _ in findall(base, s, rd)))))
# D6: a value can hold both `P & c` and `P & NOT c`; NOT c vs pattern difference.
mv((6, "a"), "D6 BOTH `P & (a: \"1\")` AND `P & NOT (a: \"1\")` hold, WHOLE, over DIG4 (341)",
   lambda rd: "%d (first %r)" % cnt(DIG4, lambda s: whole(W(PAB, a1), s, rd) and whole(W(PAB, NOT(a1)), s, rd)))
mv((6, "b"), "D6 `P & NOT (a: \"1\")` vs `P & !(P & (a: \"1\"))` over DIG4 (341)", lambda rd: three(rd, W(PAB, NOT(a1)), Diff(PAB, W(PAB, a1)), DIG4, ("a", "b")))
# D7: one language, two spellings, under a condition.
mv((7, "a"), "D7 SPELLING greedy `P & (a: \"1\")` vs lazy `/(?<a>\\d+?)(?<b>\\d+)/ & (a: \"1\")` over DIG4 (341)", lambda rd: three(rd, W(PAB, a1), W(PABL, a1), DIG4, ("a", "b")))
mv((7, "b"), "D7 SPELLING `(A | B) & (l: \"a\")` vs `(B | A) & (l: \"a\")` over {a, b} to length 4 (31)", lambda rd: three(rd, W(Alt(Aa, Ba), la), W(Alt(Ba, Aa), la), AB4, ("l",)))
mv((7, "d"), "D7 SPELLING `(B | A) & (l: <20)` vs `(A | B) & (l: <20)` over DIG4 (341) (labels compared)", lambda rd: three(rd, W(Alt(Bd, Ad), l20), W(Alt(Ad, Bd), l20), DIG4, ("l",)))
mv((7, "e"), "D7 SPELLING greedy `P & (a: <5)` vs lazy `/(?<a>\\d+?)(?<b>\\d+)/ & (a: <5)` over DIG4 (341) (labels compared)", lambda rd: three(rd, W(PAB, a5), W(PABL, a5), DIG4, ("a", "b")))
mv((7, "c"), "D7 SPELLING `P & (a: \"1\")` vs `P & (a: \"1\")` written in (`/(?<a>1)(?<b>\\d+)/`) over DIG4 (341)", lambda rd: three(rd, W(PAB, a1), PA1, DIG4, ("a", "b")))
flush()

# ======================================================================================================== PART E
print("== PART E: OPEN UNDER THE NEW RULE: each candidate run (RULE = (ii) for everything else); WHOLE / SEARCHED / FIND-ALL")
class NotAhead:                                         # `/(?!...${B})${node}/`: node's paths at i where B has no row from i
    def __init__(self, node, B, inner): self.node, self.B, self.inner = node, B, inner
    def walk(self, s, i, inalt, cmp):
        sc = "in" if inalt else "out"
        if self.inner == "NA1": ok = not accepted(self.B, s, i)                     # B's own conditions backtrack inside
        else:                                                                       # NA2: B's first path at i, judged
            ps = list(self.B.walk(s, i, False, cmp)); ok = not (ps and all(v is True for _, v in ps[0][2]))
        for e, row, recs in self.node.walk(s, i, inalt, cmp):
            yield e, row, recs + ((sc, ok),)
def eline(k, text, f): emit(k, "  %s: %s" % (text, f()))
# E1 the order of paths across the two sides of `&` (the same-stretch join): which labels the reported row carries.
J = W(And(PAB, PCD), OR(a1, test("c", eq("1"))))
for jo in order(["left", "right"]):
    def e1(jo=jo):
        JOIN["v"] = jo
        r = "%s ; over DIG4 holds WHOLE %d, SEARCHED %d" % (ans3(J, "123", labs=("a", "b", "c", "d")), cnt(DIG4, lambda s: whole(J, s))[0], cnt(DIG4, lambda s: search(J, s) is not None)[0])
        JOIN["v"] = "left"; return r
    eline((1, jo), "E1 JOIN %s side's paths outer, `(P & Q) & ((a: \"1\") | (c: \"1\"))`, P = /(?<a>\\d+)(?<b>\\d+)/, Q = /(?<c>\\d+)(?<d>\\d+)/, on `123`" % jo, e1)
def e1d():
    JOIN["v"] = "left"; L = {s: report(J, s, None, ("a", "b", "c", "d")) for s in DIG4}
    JOIN["v"] = "right"; Rr = {s: report(J, s, None, ("a", "b", "c", "d")) for s in DIG4}
    JOIN["v"] = "left"
    return "reported row differs on %d of 341 (first %r); holds differ 0 by construction (the same pairs, another order)" % cnt(DIG4, lambda s: L[s] != Rr[s])
eline((1, "z"), "E1 JOIN left vs right over DIG4", e1d)
# E2 where a rejecting condition re-enters: after the whole operand (Where) vs as a piece right after its label's
# group (inside a loop: inside each pass; zero passes then run no piece).
REPa = r"(?:(?P<h>\d);)*"; REPo = r"(?:(?P<h>\d)?;)*"
for rxn, rx in order([("/(?:(?<h>\\d);)*/", REPa), ("/(?:(?<h>\\d)?;)*/", REPo)]):
    L1 = W(R(rx, passre=rx[3:-2]), ptest("h", lt(5))); L2 = R(rx, piece={"h": lt(5)})
    for s in order(["", "7;3;", "3;7;", "3;;"]):
        eline((2, rxn, s), "E2 LOOP %s `(h: <5)` on `%s`: L1 after the loop %s ; L2 a piece in each pass %s" % (rxn, s, ans3(L1, s), ans3(L2, s)), lambda: "")
    eline((2, rxn, "z"), "E2 LOOP %s `(h: <5)` L1 vs L2 over {3, 7, ;} to length 5 (364)" % rxn, lambda L1=L1, L2=L2: three(RULE, L1, L2, RG3, ()))
PABp = R(r"(?P<a>\d+)(?P<b>\d+)", piece={"a": eq("1")})
eline((2, "set-once"), "E2 SET-ONCE `P & (a: \"1\")` after the operand vs a piece right after a's group, over DIG4 (341)", lambda: three(RULE, W(PAB, a1), PABp, DIG4, ("a", "b")))
# E3 a rejecting condition inside a complement.
for cm in order(["C1", "C2"]):
    eline((3, cm), "E3 COMPLEMENT %s `P & !(P & (a: \"1\"))` on `123`" % {"C1": "C1 (the complemented program judged by the rule: some path)", "C2": "C2 (judged by its one parse)"}[cm],
          lambda cm=cm: "%s ; over DIG4 holds WHOLE %d, SEARCHED %d" % (ans3(Diff(PAB, W(PAB, a1)), "123", cmp=cm, labs=("a", "b")),
                                                                         cnt(DIG4, lambda s: whole(Diff(PAB, W(PAB, a1)), s, cmp=cm))[0], cnt(DIG4, lambda s: search(Diff(PAB, W(PAB, a1)), s, cmp=cm) is not None)[0]))
eline((3, "z"), "E3 COMPLEMENT C1 vs C2 over DIG4", lambda: (lambda P: "%s" % " ; ".join(
    "%s %d" % (mode, cnt(DIG4, lambda s: (whole(P, s, cmp="C1") != whole(P, s, cmp="C2")) if mode == "WHOLE" else (report(P, s, None, ()) != (lambda r: None if r is None else (r[0], r[1], ()))(search(P, s, 0, None, "C2"))))[0]) for mode in ["WHOLE", "SEARCHED"]))(Diff(PAB, W(PAB, a1))))
# E4 a rejecting condition and a lookahead: (a) a POSITIVE lookahead's label read outside it; (b) a condition INSIDE a
# negative lookahead (whole-text route (i)).
for la_ in order([True, False]):
    LP = W(R(r"(?=(?P<x>\d+))\d", look_atomic=la_), test("x", eq("1")))
    eline((4, la_), "E4 LOOKAHEAD %s `/(?=(?<x>\\d+))\\d/ & (x: \"1\")` on `12`" % ("LA1 atomic (PCRE: the lookahead is not re-entered)" if la_ else "LA2 re-entered by the outer condition"),
          lambda LP=LP: "%s ; on `112`: %s ; over DIG4 SEARCHED holds %d" % (ans3(LP, "12", labs=("x",)), ans3(LP, "112", labs=("x",)), cnt(DIG4, lambda s: search(LP, s) is not None)[0]))
q = W(T2, late_f)
GAPQ = W(R(r"[\s\S]*?" + T2P), late_f)
for na in order(["NA1", "NA2"]):
    RT = NotAhead(T2, GAPQ, na)
    for s in order(["9:15 10:45", "9:45 1", "1 9:15"]):
        eline((4, na, s), "E4 NEGATIVE LOOKAHEAD %s `/(?![\\s\\S]*${q})${t2}/` on `%s`" % ({"NA1": "NA1 (the inner condition backtracks inside: no late time from here on)", "NA2": "NA2 (the inner program's first path, judged)"}[na], s),
              lambda RT=RT, s=s: ans3(RT, s))
# E5 a rejecting condition outside an `occurrences` / `contains`: H1 the hits are the argument's own find-all, the
# condition judges them; H2 the condition backtracks into the body's paths (the gap may swallow a hit; hits re-split).
BODY = R(r"(?:[\s\S]*?(?P<hit>\d+))*[\s\S]*")
def h1(S):
    def f(s, i, e):
        hs_ = [m.group(0) for m in re.finditer(r"\d+", s[i:e])]
        return kand([bool(S(v)) for v in hs_] or [None]) is True
    return SF(R(r"[\s\S]*"), f)
def h2(S): return W(BODY, ptest("hit", S))
OCCPOOL = strings("12 x", 4)
for hn, mk in order([("H1", h1), ("H2", h2)]):
    P_ = mk(lt(100))
    eline((5, hn), "E5 OCCURRENCES `occurrences(/\\d+/)` with `(hit: <100)`, %s, WHOLE on `1234` / `x300 12` / `5 123`" % {"H1": "H1 (hits fixed, judged)", "H2": "H2 (the condition re-enters the body)"}[hn],
          lambda P_=P_: "%s / %s / %s ; over {1, 2, space, x} to length 4 (341) WHOLE holds %d" % tuple(
              ["HOLDS" if whole(P_, s) else "FAILS" for s in ["1234", "x300 12", "5 123"]] + [cnt(OCCPOOL, lambda s: whole(P_, s))[0]]))
eline((5, "z"), "E5 H1 vs H2 over {1, 2, space, x} to length 4 (341), WHOLE", lambda: "differ %d (first %r)" % cnt(OCCPOOL, lambda s: whole(h1(lt(100)), s) != whole(h2(lt(100)), s)))
# E6 UNKNOWN: does it reject and backtrack like FALSE (U1), or end the tries at that start (U2)?
UP = W(R(r"(?P<b>\d+)(?P<a>\d)?"), test("a", lt(5)))
for u in order(["U1", "U2"]):
    def e6(u=u):
        UNK["v"] = u
        r = "%s ; over DIG4: %s" % (ans3(UP, "12", labs=("a", "b")), " ; ".join("%s holds %d" % (m, cnt(DIG4, lambda s: (whole(UP, s) if m == "WHOLE" else search(UP, s) is not None))[0]) for m in ["WHOLE", "SEARCHED"]))
        UNK["v"] = "U1"; return r
    eline((6, u), "E6 UNKNOWN %s `/(?<b>\\d+)(?<a>\\d)?/ & (a: <5)` on `12` (first path: b = 12, a absent)" % {"U1": "U1 (rejects and backtracks, as FALSE)", "U2": "U2 (ends the tries at this start)"}[u], e6)
# E7 ATOMIC (a labelled extra: the MEANING of predicates_future.md items 14 / 19, no spelling).
AT = [("`t2 & q` (q := t2 & late) on `9:30`", W(T2, late_f), W(Atomic(T2), late_f), "9:30", ("h", "m")),
      ("`t2 & !q` on `9:30` (item 14's example)", Diff(T2, q), Diff(Atomic(T2), q), "9:30", ("h", "m")),
      ("`t2 & !q` on `9:30 10:15`", Diff(T2, q), Diff(Atomic(T2), q), "9:30 10:15", ("h", "m")),
      ("`(B | A) & (l: <20)` on `25`", W(Alt(Bd, Ad), l20), W(Atomic(Alt(Bd, Ad)), l20), "25", ("l",)),
      ("`(B | A) & (l: <20)` on `25 13`", W(Alt(Bd, Ad), l20), W(Atomic(Alt(Bd, Ad)), l20), "25 13", ("l",)),
      ("`P & (a: \"1\")` on `123`", W(PAB, a1), W(Atomic(PAB), a1), "123", ("a", "b"))]
for nm, P1, P2_, s, labs in order(AT):
    eline((7, nm), "E7 ATOMIC %s: the rule %s ; atomic %s" % (nm, ans3(P1, s, labs=labs), ans3(P2_, s, labs=labs)), lambda: "")
eline((7, "z"), "E7 ATOMIC vs (i) and (iii) over DIG4 for `(B | A) & (l: <20)` (holds; report)", lambda: " ; ".join(
    "atomic vs (%s) WHOLE %d SEARCHED %d" % (rd, cnt(DIG4, lambda s: whole(W(Atomic(Alt(Bd, Ad)), l20), s) != whole(W(Alt(Bd, Ad), l20), s, rd))[0],
                                             cnt(DIG4, lambda s: report(W(Atomic(Alt(Bd, Ad)), l20), s, None, ("l",)) != report(W(Alt(Bd, Ad), l20), s, rd, ("l",)))[0]) for rd in ["i", "iii"]))
flush()

# ======================================================================================================== PART F
print("== PART F: THE REMAINING OWNER QUESTIONS RE-RUN: each candidate on a WHOLE value, a SEARCHED text and a several-match FIND-ALL text (RULE; MOVED = the line differs from rev 23.2's (iii))")
def fq(k, slug, cand, P, wt, st, ft, labs=(), cmp="C1"):
    mv((k, slug, cand), "F %s [%s]" % (slug, cand), lambda rd: "WHOLE on `%s` %s ; SEARCHED on `%s` %s ; FIND-ALL on `%s` %s" % (
        wt, "HOLDS" if whole(P, wt, rd, cmp) else "FAILS", st,
        (lambda r: "FAILS" if r is None else "HOLDS `%s`@%d%s" % (st[r[0]:r[1]], r[0], show_labels(r[2], labs)))(search(P, st, 0, rd, cmp)),
        ft, fa(P, ft, rd, cmp, labs)))
S9, T30 = lt(9), lt(30)
MDOM = [a + b for a in "0123456789" for b in "0123456789"]
def joint_plain(r): return None if r.get("h") is None or r.get("m") is None else (S9(r["h"]) and T30(r["m"]))
def joint_comp(r):
    if r.get("h") is None: return None
    if r.get("m") is not None: return S9(r["h"]) and T30(r["m"])
    vals = set(bool(S9(r["h"]) and T30(mv_)) for mv_ in MDOM)
    return vals.pop() if len(vals) == 1 else None
def record_(r): return kand([None if r.get("h") is None else S9(r["h"]), None if r.get("m") is None else T30(r["m"])])
for cand, c in order([("today: joint UNKNOWN on an absent part", joint_plain), ("completion (item 18)", joint_comp), ("the record (h: <9, m: <30)", record_)]):
    fq(1, "record-under-not", cand, W(T2, NOT(c)), "10", "10", "10 9 10:15")
REPx = R(REPo, passre=r"(?P<h>\d)?;")
def ptest_alt(lab, S):                                       # a pass lacking the label makes the whole test UNKNOWN
    def c(r):
        ps = r["_passes"][lab] or [None]
        return None if any(v is None for v in ps) else kand([bool(S(v)) for v in ps])
    return c
for cand, c in order([("R1 nested pass table: `(h: <5)` Kleene AND over passes", ptest("h", lt(5))),
                      ("R1: `NOT (h: <5)`", NOT(ptest("h", lt(5)))), ("R1: `(h: !<5)`", ptest("h", lambda v: not lt(5)(v))),
                      ("no pass table: `(h: <5)` reads PCRE's last capture", test("h", lt(5)))]):
    fq(2, "pass-table", cand, W(REPx, c), "7;;", "7;;", "3;;7;;3;")
for cand, c in order([("Kleene AND (today)", NOT(ptest("h", lt(5)))), ("a pass lacking h makes it UNKNOWN", NOT(ptest_alt("h", lt(5))))]):
    fq(3, "pass-and", cand + ": `NOT (h: <5)`", W(REPx, c), "7;;", "7;;", "7;;3;7;;")
def some_exists(S): return lambda r: any(v is not None and S(v) for v in r["_passes"]["h"])
def some_three(S): return lambda r: kor([None if v is None else bool(S(v)) for v in r["_passes"]["h"]])
for cand, sm in order([("EXISTS, two-valued (today)", some_exists), ("three-valued some over the real passes", some_three)]):
    fq(4, "group-truth", cand + ": `NOT some((h: <5))`", W(REPx, NOT(sm(lt(5)))), ";", ";", ";;3;")
AH = R(r"a(?P<h>\d)|b(?P<k>\d)|c")
ch, ck = test("h", lt(5)), test("k", lt(5))
for cand, c in order([("Kleene OR (today)", NOT(lambda r: kor([ch(r), ck(r)]))), ("two-valued OR (rev 22)", lambda r: not (ch(r) is True or ck(r) is True))]):
    fq(5, "condition-or", cand + ": `NOT ((h: <5) | (k: <5))`", W(AH, c), "b7", "b7", "b7 a3 c a9")
for cn, c in order([("(h: <5)", ptest("h", lt(5)))]):
    fq(6, "when-meaning", "its body `(x & c & p) | (x & !(x & c))`, c = %s" % cn, when_body(c), "5;1;9", "5;1;9", "3;0;5 5;1;9")
    fq(6, "when-meaning", "the filter form `x & when(c, p)`, c = %s" % cn, when_filter(c), "5;1;9", "5;1;9", "3;0;5 5;1;9")
for cand, P_ in order([("`t2 & !(t2 & (h: <0))` (the ERROR by local polarity)", Diff(T2, W(T2, test("h", lt(0))))),
                       ("`t2 & NOT (h: <0)` (the WARNING: constant-always)", W(T2, NOT(test("h", lt(0))))),
                       ("`(B | A) & (l: <10)` without the branch condition", W(Alt(Bd, Ad), l10)),
                       ("`((B & (l: >50)) | A) & (l: <10)` (the branch position the draft says can admit)", W(Alt(W(Bd, g50), Ad), l10))]):
    fq(7, "polarity-rule", cand, P_, "12", "9:30 12", "12 9:30 25")
for cand, P_ in order([("`t2 & !q` (chain rule)", Diff(T2, q)), ("`!q & t2` (= the same, chain rule)", Diff(T2, q))]):
    fq(8, "complement-place", cand, P_, "9:30", "9:30", "9:30 10:45")
mv((8, "complement-place", "lone"), "F complement-place [a lone `!q` in a WHOLE place (the value is not a late time)]",
   lambda rd: "on `9:30` %s ; on `9` %s ; on `10:45` %s (an ERROR today in every mode)" % tuple("HOLDS" if not whole(q, v, rd) else "FAILS" for v in ["9:30", "9", "10:45"]))
NN = W(R(r"(?P<n>\d+)"), test("n", lt(100)))
SET100 = [str(k) for k in range(100)]
mv((9, "hit-list"), "F hit-list [the draft: the filtered argument's own rows, leftmost, non-overlapping] `occurrences(/(?<n>\\d+)/ & (n: <100))`",
   lambda rd: "on `1234` %s ; on `5 123` %s" % (fa(NN, "1234", rd), fa(NN, "5 123", rd)))
for cand, alt in order([("string-set, longest-first alternation", "|".join(sorted(SET100, key=lambda x: (-len(x), x)))),
                        ("string-set, shortest-first alternation", "|".join(sorted(SET100, key=lambda x: (len(x), x))))]):
    emit((9, "hit-list", cand), "  F hit-list [%s]: on `1234` %s ; on `5 123` %s" % (cand, ["`%s`@%d" % (m.group(0), m.start()) for m in re.finditer(alt, "1234")], ["`%s`@%d" % (m.group(0), m.start()) for m in re.finditer(alt, "5 123")]))
BODYn = R(r"(?:[\s\S]*?(?P<hit>\d+))*[\s\S]*")
for v in order(["1234", "5 123"]):
    def h2hits(v=v):
        a = accepted(W(BODYn, ptest("hit", lt(100))), v, 0)
        a = [x for x in a if x[0] == len(v)]
        return "none" if not a else ["%s" % h for h in a[0][1]["_passes"]["hit"]]
    emit((9, "hit-list", "H2", v), "  F hit-list [H2: the outer condition re-enters `occurrences`' body; its first surviving path's hits] on `%s`: %s" % (v, h2hits()))
class PosAhead:                                          # `/(?=[\s\S]*${B})${node}/` whose B's labels the outer row carries
    def __init__(self, node, B, mode): self.node, self.B, self.mode = node, B, mode
    def walk(self, s, i, inalt, cmp):
        bs = accepted(self.B, s, i)
        if self.mode == "LA1": bs = bs[:1]                   # PCRE: the lookahead keeps its first surviving path
        for _, brow in bs:
            for e, row, recs in self.node.walk(s, i, inalt, cmp):
                yield e, merge(row, brow), recs
LATEM = W(R(r"[\s\S]*?\d\d:(?P<lm>\d\d)"), test("lm", lambda v: numeral(v) and int(v) >= 30))
for la_ in order(["LA1", "LA2"]):
    fq(10, "lookahead-labels", la_ + (" (atomic, PCRE's)" if la_ == "LA1" else " (re-entered)") + ": `/(?=[\\s\\S]*${late_m})${t2}/ & (lm: \"50\")`",
       W(PosAhead(T2, LATEM, la_), test("lm", eq("50"))), "9:15", "9:15 10:45 11:50", "9:15 10:45 11:50 1", labs=("h", "lm"))
fq(11, "repeated-means", "`/(?:(?<h>\\d);)+/ & /\\d;/` & `(h: <5)`", W(And(R(r"(?:(?P<h>\d);)+"), R(r"\d;")), ptest("h", lt(5))), "3;", "7;3;", "3;7;3;")
fq(11, "repeated-means", "`/(?<h>\\d);/` & `(h: <5)`", W(R(r"(?P<h>\d);"), test("h", lt(5))), "3;", "7;3;", "3;7;3;")
for cm in order(["C1", "C2"]):
    fq(12, "nested-complement", "`t2 & contains(t2 & !q)`, complement %s" % cm,
       SF(T2, lambda s, i, e, cm=cm: bool(findall(Diff(T2, q), s[i:e], None, cm))), "9:30", "9:30", "9:30 10:45", cmp=cm)
for cand, P_ in order([("today `t2 & !q`", Diff(T2, q)), ("route (ii) `t2 & text.none(q)`", SF(T2, lambda s, i, e: not findall(q, s))),
                       ("route (i)(a) NA1 `/(?![\\s\\S]*${q})${t2}/`", NotAhead(T2, GAPQ, "NA1")), ("route (i)(a) NA2", NotAhead(T2, GAPQ, "NA2"))]):
    fq(13, "whole-text", cand, P_, "9:30", "9:30", "9:15 9:30 1")
flush()

# ======================================================================================================== PART G
# Rulings file R1 (the manager's framing, a CLAIM to test): "the table holds every path of the pattern in PCRE's
# preference order (two paths over one stretch with different labels are two rows); conditions filter; the first
# surviving row is reported", and atomic = "take the first row BEFORE filtering". Built INDEPENDENTLY of the program
# evaluator above (no Alt / Where / And / Diff nodes): each program is ONE regex (its `|` branches with their own
# group names), its table = every path of that regex at each start, a row = the path's labels (and pass lists), and
# the conditions are ONE keep(row) predicate over the finished row. Two forms of "conditions filter": PROVENANCE (a
# condition written inside a branch keeps or drops only that branch's rows: the row remembers its branch) and NAIVE
# (every condition filters every row of the table).
print("== PART G: the rulings-file R1 formulation (a table of every path, conditions filter, the first surviving row reported) vs the program evaluator (RULE)")
class Table:
    def __init__(self, pattern, keep, atomic=False): self.rx, self.keep, self.atomic = RX(pattern), keep, atomic
    def rows(self, s, i):
        out = []
        for e, caps, hist in self.rx.paths(s, i):
            r = self.rx.labels(s, caps); r["_passes"] = {l: self.rx.passes(s, hist, l) for l in self.rx.names}
            r["_s"], r["_i"], r["_e"] = s, i, e
            out.append((e, r))
        if self.atomic: out = out[:1]                    # atomic: the first row BEFORE filtering
        return [(e, r) for e, r in out if self.keep(r)]
def t_whole(T, s): return any(e == len(s) for e, _ in T.rows(s, 0))
def t_search(T, s, pos=0):
    for i in range(pos, len(s) + 1):
        rs = T.rows(s, i)
        if rs: return i, rs[0][0], rs[0][1]
    return None
def t_findall(T, s):
    out, pos = [], 0
    while pos <= len(s):
        r = t_search(T, s, pos)
        if r is None: break
        out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
    return out
def tri(T, P, pool, labs_t, labs_p):
    def tl(r): return (L(r),) if labs_t == ("l1", "l2") else tuple(r.get(l) for l in labs_t)
    def pl(r): return tuple(r.get(l) for l in labs_p)
    out = []
    for mode in ["WHOLE", "SEARCHED", "FIND-ALL"]:
        if mode == "WHOLE": d = cnt(pool, lambda s: t_whole(T, s) != whole(P, s))
        elif mode == "SEARCHED": d = cnt(pool, lambda s: (lambda a, b: (a is None) != (b is None) or (a is not None and (a[:2] != b[:2] or tl(a[2]) != pl(b[2]))))(t_search(T, s), search(P, s)))
        else: d = cnt(pool, lambda s: [(i, j, tl(r)) for i, j, r in t_findall(T, s)] != [(i, j, pl(r)) for i, j, r in findall(P, s)])
        out.append("%s %d%s" % (mode, d[0], "" if d[1] is None else " (first %r)" % d[1]))
    return "differ " + "; ".join(out)
def L(r): return r["l1"] if r.get("l1") is not None else r.get("l2")
def lv(S): return lambda r: L(r) is not None and S(L(r))
CBA = r"(?:(?P<l1>\d\d)|(?P<l2>\d)\d)"
KH2 = r"(?:(?P<k1>\d)(?:;(?P<h1>\d))*|(?P<k2>\d)(?:;(?P<h2>\d))*)"
def kh_keep(cpass):                                      # `(x & c & p) | (x & !(x & c))` read on one table row
    def keep(r):
        if r.get("k1") is not None:
            return cpass(r["_passes"]["h1"]) is True and between(3, 7)(r["k1"])
        s, i, e = r["_s"], r["_i"], r["_e"]          # branch 2: x's stretch is not a row of `x & c`
        return not any(e2 == e and cpass(rx_h) is True for e2, rx_h in [(e3, RX(KH.rx.pattern).passes(s, h3, "h")) for e3, c3, h3 in RX(KH.rx.pattern).paths(s, i)])
    return keep
def cp_lt5(ps): return kand([bool(lt(5)(v)) for v in ps] or [None])
REPA = r"(?:(?P<h>\d);)*"
GT = [("`(B | A) & (l: <20)`", Table(CBA, lv(lt(20))), W(Alt(Bd, Ad), l20), DSP, ("l1", "l2"), ("l",)),
      ("`(B & (l: <20)) | (A & (l: <20))`", Table(CBA, lv(lt(20))), Alt(W(Bd, l20), W(Ad, l20)), DSP, ("l1", "l2"), ("l",)),
      ("`((B & (l: >50)) | A) & (l: <10)` PROVENANCE", Table(CBA, lambda r: (r.get("l1") is None or gt(50)(r["l1"])) and lv(lt(10))(r)), W(Alt(W(Bd, g50), Ad), l10), DIG4, ("l1", "l2"), ("l",)),
      ("`((B & (l: >50)) | A) & (l: <10)` NAIVE (every condition on every row)", Table(CBA, lambda r: lv(gt(50))(r) and lv(lt(10))(r)), W(Alt(W(Bd, g50), Ad), l10), DIG4, ("l1", "l2"), ("l",)),
      ("`P & (a: \"1\")`", Table(PAB.rx.pattern, lambda r: r["a"] == "1"), W(PAB, a1), DSP, ("a", "b"), ("a", "b")),
      ("`P & !(P & (a: \"1\"))` (the complement's own table, filtered)", Table(PAB.rx.pattern, lambda r: not any(e2 == r["_e"] and rr["a"] == "1" for e2, rr in Table(PAB.rx.pattern, lambda x: True).rows(r["_s"], r["_i"]))), Diff(PAB, W(PAB, a1)), DIG4, ("a", "b"), ("a", "b")),
      ("loop `/(?:(?<h>\\d);)*/ & (h: <5)` (a row's passes; zero passes UNKNOWN)", Table(REPA, lambda r: cp_lt5(r["_passes"]["h"]) is True), W(R(REPA), ptest("h", lt(5))), RG3, (), ()),
      ("`when` expansion, c = (h: <5), the row remembers its branch", Table(KH2, kh_keep(cp_lt5)), when_body(ptest("h", lt(5))), KHPOOL, (), ()),
      ("ATOMIC `atomic(B | A) & (l: <20)`: first row before filtering", Table(CBA, lv(lt(20)), atomic=True), W(Atomic(Alt(Bd, Ad)), l20), DSP, ("l1", "l2"), ("l",)),
      ("ATOMIC `atomic(P & (a: \"1\"))`: first row before filtering vs the evaluator's atomic (its own condition applied inside)", Table(PAB.rx.pattern, lambda r: r["a"] == "1", atomic=True), Atomic(W(PAB, a1)), DIG4, ("a", "b"), ("a", "b"))]
for nm, T, P, pool, lt_, lp_ in order(GT):
    emit((nm,), "  G %s over %d texts: %s" % (nm, len(pool), tri(T, P, pool, lt_, lp_)))
emit(("z",), "  G witnesses: NAIVE `((B & (l: >50)) | A) & (l: <10)` on `12`: table %s, evaluator %s ; `atomic(P & (a: \"1\"))` on `123`: first-row-before-filtering %s, evaluator %s" % (
    "HOLDS" if t_whole(Table(CBA, lambda r: lv(gt(50))(r) and lv(lt(10))(r)), "12") else "FAILS", "HOLDS" if whole(W(Alt(W(Bd, g50), Ad), l10), "12") else "FAILS",
    "HOLDS" if t_whole(Table(PAB.rx.pattern, lambda r: r["a"] == "1", atomic=True), "123") else "FAILS", "HOLDS" if whole(Atomic(W(PAB, a1)), "123") else "FAILS"))
flush()

print("== MOVED LINES (PART C, D, F lines whose answer under the RULE differs from rev 23.2's (iii)): %d" % len(MOVED))
print("== ENGINE LINES THAT MOVE (PART B hunks): %d" % len(MOVED_B))
print("END")
