#!/usr/bin/env python3
# Lane predspec23d (2026-11-17): evidence for docs/design/predicates_draft.md rev 23.2 (review r34's fixes; DESIGN
# ONLY; rules nothing). Finding A1 of review r34: the three earlier engines compare some numbers BY VALUE (leading
# zeros read away) where the draft's own section 2.2 reads an unpadded integer set as CANONICAL numerals (the `\d+`
# shape with no leading zero; a tuple holds only when EVERY component is canonical: `((h, m): >= (9, 0))` rejects
# `9:00`). This script re-runs EVERY line of the three engines with the comparison fixed, and prints each line that
# moves, before and after.
#
# How: the three engines (predspec23_evidence/predspec23_model.py, predspec23b_evidence/..., predspec23c_evidence/...)
# are READ, never edited: their source text is loaded, the value-compare sites listed in FIXES below are replaced
# (each replacement must match exactly once, else the script stops), and the patched text is executed in memory under
# the engine's own module name, so 23b's `import predspec23_model` and 23c's `import predspec23b_model` get the
# patched engines. Nothing else in the engines changes (their padded(...) forms, ptup_ge / ptup_between, stay padded:
# the draft spells those `padded`). The BEFORE text of each line is the committed .out file of that engine (the
# premise test: each engine re-run reproduces its committed .out byte for byte, ORDER lines aside).
#
# Value-compare sites fixed (each is an unpadded set in the draft):
#   23  late, setcomp_late, setcomp_late_m0  q's R = `>= (9, 30)`  (h, m) both canonical, else not in R
#   23  inR (+ I2b's hour test)              closing R = `(<10, <30)` both canonical
#   23b late                                 q's R (as above; B.q, B.late feed 23c)
#   23c L83's `<30`                          -> lt(30), the engines' own canonical set
#   23c inR_h, inR_m                         closing R in the record-twin lines
#   23c m_lt45                               `(m: <45)` in searchrow's T2 `when`
#   searchrow (docs/dev/lanes/searchrow_evidence/searchrow.py, the source of section R.5 A3/A4's numbers and section
#            R.7b's searched examples): late, (m: <45), (h: >20), (m = 0: <20), L34's (a: <5)/(b: <5), section 11's
#            <256, `when`'s (d: <50)/(d: <5), <17. Its late_m0 is spelled `padded` in the draft and stays padded.
# Added lines (PART X of this script, not in any engine): the closing example's re-chosen default `m = 0`, and the
# value-compare and canonical readings of the review's quoted rows side by side.
#
# Commands (W = the worktree; run from a scratch dir under $PCREC_TMPDIR, e.g. /var/tmp/pcrec-pcrec/scratch/predspec23d):
#   timeout 1800 python3 -I W/docs/dev/lanes/predspec23d_evidence/predspec23d_model.py > fwd.out
#   PREDSPEC23D_SWAP=1 timeout 1800 python3 -I W/docs/dev/lanes/predspec23d_evidence/predspec23d_model.py > swap.out
#   diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)        # must print nothing
#   PREDSPEC23D_SABOTAGE=1 (forward and swapped): the diff must print something (the swap check can fail)
# SWAP sets every engine's own SWAP (pools, condition / filter / pass lists, line computation reversed) and reverses
# this script's own orders. SABOTAGE sets every engine's own SABOTAGE (Kleene AND = "the first non-TRUE value";
# 23c's branch order under SWAP) AND this script's own: the canonical check of a tuple looks only at the FIRST
# component in the current order (h forward, m swapped), so every line that moved under A1 depends on order too
# (the engines' sabotage alone does not reach the T2 / closing lines, review r34 F-DOC-7 / SIMULATE-8); in PART Y the
# branch order of the BRANCH-SCOPE evaluator follows the evaluation order, and `some` reads only the first pass.
# REACH (measured, the sabotaged forward vs swapped diff): every moved line of PART A, PART X, and in PART Y the
# BRANCH-SCOPE, FIND-ALL, RECORD-UNDER-NOT, L30 and DE-MORGAN lines. NOT reached: PART Y's POLARITY t2 witnesses and
# DEFAULT-UNUSED lines (constant or 0-differ results the sabotage does not perturb), and the engine lines A1 did not
# move that the engines' own sabotage does not reach either (their PARTS 3-9 and 23c's CONDITION-OR; review r34
# SIMULATE-8): for those the swap check is a control that has not shown it can fail.
import os, sys, io, re, contextlib, types

HERE = os.path.dirname(os.path.abspath(__file__))
LANES = os.path.dirname(HERE)
SWAP = os.environ.get("PREDSPEC23D_SWAP") == "1"
SAB = os.environ.get("PREDSPEC23D_SABOTAGE") == "1"
for k in ("PREDSPEC23", "PREDSPEC23B", "PREDSPEC23C", "SEARCHROW"):
    os.environ[k + "_SWAP"] = "1" if SWAP else "0"
    os.environ[k + "_SABOTAGE"] = "1" if SAB else "0"
def order(xs): return list(reversed(list(xs))) if SWAP else list(xs)

def numeral(v): return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None
def CANON(*vs):
    """Section 2.2: a tuple is in an unpadded integer tuple set only when EVERY component is a canonical numeral."""
    vs = order(vs)
    if SAB: vs = vs[:1]                               # sabotage: only the first component in the current order
    return all(numeral(v) for v in vs)

FIXES = {
    "predspec23": [
        ('    return (int(r["h"]), int(r["m"])) >= (9, 30)\n',
         '    return PS23D_CANON(r["h"], r["m"]) and (int(r["h"]), int(r["m"])) >= (9, 30)\n'),
        ('    return not ((int(r["h"]), int(r["m"])) >= (9, 30))\n',
         '    return not (PS23D_CANON(r["h"], r["m"]) and (int(r["h"]), int(r["m"])) >= (9, 30))\n'),
        ('    return not ((int(r["h"]), int(r["m"] if r.get("m") is not None else "0")) >= (9, 30))\n',
         '    mm = r["m"] if r.get("m") is not None else "0"\n'
         '    return not (PS23D_CANON(r["h"], mm) and (int(r["h"]), int(mm)) >= (9, 30))\n'),
        ('def inR(h, m): return int(h) < 10 and int(m) < 30\n',
         'def inR(h, m): return PS23D_CANON(h, m) and int(h) < 10 and int(m) < 30\n'),
        ('("I2b", lambda ps: all((int(h) < 10) if m is None else inR(h, m) for h, m in ps))',
         '("I2b", lambda ps: all((numeral(h) and int(h) < 10) if m is None else inR(h, m) for h, m in ps))'),
    ],
    "predspec23b": [
        ('else (int(r["h"]), int(r["m"])) >= (9, 30)\n',
         'else (PS23D_CANON(r["h"], r["m"]) and (int(r["h"]), int(r["m"])) >= (9, 30))\n'),
    ],
    "searchrow": [
        ('    return (int(r["h"]), int(r["m"])) >= (9, 30)\n',
         '    return PS23D_CANON(r["h"], r["m"]) and (int(r["h"]), int(r["m"])) >= (9, 30)\n'),
        ('else int(r["m"]) < 45', 'else (numeral(r["m"]) and int(r["m"]) < 45)'),
        ('else int(r["h"]) > 20', 'else (numeral(r["h"]) and int(r["h"]) > 20)'),
        ('def m0_lt20(r): return int(r["m"] if r["m"] is not None else "0") < 20',
         'def m0_lt20(r): return (lambda v: numeral(v) and int(v) < 20)(r["m"] if r["m"] is not None else "0")'),
        ('[lambda r: int(r["a"]) < 5, lambda r: int(r["b"]) < 5]',
         '[lambda r: numeral(r["a"]) and int(r["a"]) < 5, lambda r: numeral(r["b"]) and int(r["b"]) < 5]'),
        ('[lambda r: int(r["n"]) < 256]', '[lambda r: numeral(r["n"]) and int(r["n"]) < 256]'),
        ('cd = lambda r: int(r["d"]) < 50; pd = lambda r: int(r["d"]) < 5',
         'cd = lambda r: numeral(r["d"]) and int(r["d"]) < 50; pd = lambda r: numeral(r["d"]) and int(r["d"]) < 5'),
        ('[lambda r: int(r["n"]) < 17]', '[lambda r: numeral(r["n"]) and int(r["n"]) < 17]'),
    ],
    "predspec23c": [
        ('m_lt45 = lambda r: None if r.get("m") is None else int(r["m"]) < 45\n',
         'm_lt45 = lambda r: None if r.get("m") is None else lt(45)(r["m"])\n'),
        ('"<30", lambda v: re.fullmatch(r"\\d+", v) is not None and int(v) < 30)', '"<30", lt(30))'),
        ('inR_h, inR_m = (lambda h: int(h) < 10), (lambda m: int(m) < 30)\n', 'inR_h, inR_m = lt(10), lt(30)\n'),
    ],
}

def load(name, fixes=True):
    path = os.path.join(LANES, name + "_evidence", name + ("_model.py" if name != "searchrow" else ".py"))
    src = open(path).read()
    if fixes:
        for a, b in FIXES[name]:
            n = src.count(a)
            if n != 1: sys.exit("predspec23d: fix site for %s matched %d times: %r" % (name, n, a))
            src = src.replace(a, b)
    mod = types.ModuleType(name + "_model")
    mod.numeral = numeral
    mod.__file__ = path
    mod.PS23D_CANON = CANON                         # a name no engine uses (searchrow has its own CANON list)
    sys.modules[name + "_model"] = mod
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(src, path + " [patched by predspec23d]", "exec"), mod.__dict__)
    return mod, buf.getvalue()

print("ORDER: %s%s" % ("SWAPPED" if SWAP else "forward", " SABOTAGE" if SAB else ""))
OUT = {}
for name in ["predspec23", "predspec23b", "predspec23c", "searchrow"]:
    _, OUT[name] = load(name)
M23, B, C = (sys.modules[n + "_model"] for n in ["predspec23", "predspec23b", "predspec23c"])

def body(text): return [l for l in text.splitlines() if not l.startswith("ORDER:")]
print("== PART A: every engine line under section 2.2 (canonical numerals); lines that MOVED, before -> after")
def outpath(name): return os.path.join(LANES, name + "_evidence", name + ("_model.out" if name != "searchrow" else ".out"))
for name in ["predspec23", "predspec23b", "predspec23c", "searchrow"]:       # printing order fixed; SWAP reverses computation only
    before = body(open(outpath(name)).read())
    after = body(OUT[name])
    if len(before) != len(after): sys.exit("predspec23d: %s line count moved %d -> %d" % (name, len(before), len(after)))
    moved = [(a, b) for a, b in zip(before, after) if a != b]
    print("ENGINE %s: %d lines, %d moved" % (name, len(after), len(moved)))
    for a, b in moved:
        print("  BEFORE" + a)
        print("  AFTER " + b)
print("== PART B: every engine line under section 2.2, in full (the numbers rev 23.2 quotes)")
for name in ["predspec23", "predspec23b", "predspec23c", "searchrow"]:
    for l in body(OUT[name]): print("%s|%s" % (name, l))

# ---- PART X: the closing example's re-chosen default, and the review's quoted rows ----
print("== PART X: the closing example (1,111 lists, R = (<10, <30) canonical) with the re-chosen default")
LINES = {}
def emit(k, t): LINES[k] = t
CLPASS, CL, SUBO, INTENT, inR = M23.CLPASS, M23.CL, M23.SUBO, M23.INTENT, M23.inR
k_and, k_not = M23.k_and, M23.k_not
def jt(h, m, dh, dm, S):
    h = h if h is not None else dh; m = m if m is not None else dm
    if h is None or m is None: return None
    return bool(S(h, m))
notR = lambda h, m: not inR(h, m)
def rec_not(h, m):
    return k_not(k_and([None if h is None else M23.lt(10)(h), None if m is None else M23.lt(30)(m)]))
CLX = [
    ("occurs.none(NOT ((h, m): R)) [joint]", "none", lambda h, m: k_not(jt(h, m, None, None, inR))),
    ("occurs.none(NOT (h: <10, m: <30)) [record twin]", "none", rec_not),
    ("occurs.none(((h, m): !R))", "none", lambda h, m: jt(h, m, None, None, notR)),
    ("occurs.none(((h, m = 99): !R))", "none", lambda h, m: jt(h, m, None, "99", notR)),
    ("occurs.none(((h, m = 00): !R)) [rev 23.1's spelling]", "none", lambda h, m: jt(h, m, None, "00", notR)),
    ("occurs.none(((h, m = 0): !R)) [rev 23.2's default]", "none", lambda h, m: jt(h, m, None, "0", notR)),
    ("((h = 0, m = 00): R) [rev 23.1's spelling]", "every", lambda h, m: jt(h, m, "0", "00", inR)),
    ("((h = 0, m = 0): R) [rev 23.2's default]", "every", lambda h, m: jt(h, m, "0", "0", inR)),
    ("((h, m = 0): R)", "every", lambda h, m: jt(h, m, None, "0", inR)),
]
def passes(s): return [(pm.group("h"), pm.group("m")) for pm in re.finditer(CLPASS, s)]
for name, kind, f in order(CLX):
    def acc(s, i, j, f=f, kind=kind):
        if re.fullmatch(CL, s[i:j]) is None: return False
        ps = passes(s[i:j])
        if kind == "none": return not any(f(h, m) is True for h, m in order(ps))
        return k_and([f(h, m) for h, m in (ps if ps else [(None, None)])]) is True
    wh = {s: acc(s, 0, len(s)) for s in order(SUBO)}
    parts = []
    for iname, g in INTENT:
        d = [s for s in order(SUBO) if wh[s] != g(passes(s))]
        parts.append("%s differ %d%s" % (iname, len(d), "" if not d else " first %r" % min(d, key=lambda x: (len(x), x))))
    se = sum(1 for s in order(SUBO) if any(acc(s, i, j) for i in range(len(s) + 1) for j in range(i, len(s) + 1)))
    emit((1, name), "  CLOSING-X %-56s WHOLE holds %d (%s) | SEARCHED holds %d" % (name, sum(wh.values()), "; ".join(parts), se))
for s in order(["", "3,", "3:05,", "3:15,", "12,", "3,3:15,"]):
    cells = []
    for name, kind, f in CLX:
        ps = passes(s)
        if kind == "none": v = not any(f(h, m) is True for h, m in ps)
        else: v = k_and([f(h, m) for h, m in (ps if ps else [(None, None)])]) is True
        cells.append("%s=%s" % (name.split(" [")[0], "H" if v else "F"))
    emit((2, s), "  CLOSING-X WHOLE on `%s`: %s" % (s, " ; ".join(cells)))
# the `t2` minute domain: which two-digit minutes are canonical (so can be in an unpadded minute set)
canon_m = [a + b for a in "0123456789" for b in "0123456789" if numeral(a + b)]
emit((3,), "  T2 MINUTES: %d of 100 two-digit minutes are canonical numerals (first %s, last %s); `00`-`09` are not" % (len(canon_m), canon_m[0], canon_m[-1]))
for k in sorted(LINES, key=lambda k: tuple(str(x) for x in k)): print(LINES[k])

# ---- PART Y: the numbers rev 23.2's new text quotes (review r34 A2, A3, A4, D2, D3); canonical sets throughout ----
print("== PART Y: review r34's witnesses, run (WHOLE / SEARCHED)")
LINES = {}
P2, test, ptest, NOT, lt = B.P2, B.test, B.ptest, B.NOT, B.lt
kand, knot = M23.k_and, M23.k_not
def hs(P, s): return "%s / %s" % ("HOLDS" if B.whole(P, s) else "FAILS",
                                  (lambda r: "FAILS" if r is None else "HOLDS `%s`@%d" % (s[r[0]:r[1]], r[0]))(B.searched(P, s)))
def cnt(pool, f):
    hits = [x for x in order(pool) if f(x)]
    return len(hits), (min(hits, key=lambda x: (len(x), x)) if hits else None)

# Y1 (A2, branch-scope): `|` of filtered branches under the three readings, own small evaluator.
# A program: branches [(regex, inner conds)], outer conds. Conditions read the row's labels (set-once here).
# (i)  no fallthrough: the row of a stretch is PCRE's one parse (the first branch whose regex matches it whole);
#      inner and outer conditions both filter that row; a rejected row sends the search to the next END only.
# (ii) fallthrough for inner AND outer conditions: a branch's row is rejected by its own or an outer condition and
#      the parse moves to the next branch (as PCRE does for a piece failing after the group).
# (iii) rev 23.1's scope rule: inner conditions fall through, outer ones read the row the inner ones left.
# SEARCHED: leftmost start; ends in the alternation's own preference order (branch-major; each branch's ends:
# re.match's end first, then the other whole-match ends longest first, as the engines do).
def br_ends(rx, s, i):
    m = re.compile(rx).match(s, i)
    first = [m.end()] if m else []
    return first + [j for j in range(len(s), i - 1, -1) if j not in first and re.fullmatch(rx, s[i:j])]
def ytrue(conds, row): return all(c(row) is True for c in conds)
def alt_accept(reading, brs, outer, s, i, j, only=None):
    """Does stretch [i, j) give a surviving row? only = the branch index whose ends are being tried (searched)."""
    seq = list(enumerate(brs))
    if SAB: seq = order(seq)                      # sabotage: the branch order follows the evaluation order
    if reading == "i":
        for k, (rx, inner) in seq:
            m = re.fullmatch(rx, s[i:j])
            if m:                                 # the one parse (branch-major: its row is tried among branch k's ends)
                return (only is None or only == k) and ytrue(inner, m.groupdict()) and ytrue(outer, m.groupdict())
        return False
    for k, (rx, inner) in seq:
        m = re.fullmatch(rx, s[i:j])
        if not m or not ytrue(inner, m.groupdict()): continue
        if reading == "ii":                       # the outer condition is one more piece of this branch
            if (only is not None and k != only) or not ytrue(outer, m.groupdict()): continue
            return True
        # (iii): this branch's row is THE row of the stretch; the outer condition reads it, no fallthrough
        return (only is None or only == k) and ytrue(outer, m.groupdict())
    return False
def alt_whole(reading, brs, outer, s): return alt_accept(reading, brs, outer, s, 0, len(s))
def alt_search(reading, brs, outer, s):
    for i in range(len(s) + 1):
        for k, (rx, _) in enumerate(brs):
            for j in br_ends(rx, s, i):
                if alt_accept(reading, brs, outer, s, i, j, k): return (i, j)
    return None
def alt_rep(reading, brs, outer, s):
    r = alt_search(reading, brs, outer, s)
    return "%s / %s" % ("HOLDS" if alt_whole(reading, brs, outer, s) else "FAILS",
                        "FAILS" if r is None else "HOLDS `%s`@%d" % (s[r[0]:r[1]], r[0]))
def lab_lt(n): return lambda r: None if r.get("l") is None else lt(n)(r["l"])
def lab_gt(n): return lambda r: None if r.get("l") is None else (numeral(r["l"]) and int(r["l"]) > n)
def lab_eq(v): return lambda r: None if r.get("l") is None else r["l"] == v
Bd, Ad = r"(?P<l>\d\d)", r"(?P<l>\d)\d"             # B := /(?<l>\d\d)/, A := /(?<l>\d)\d/
Ba, Aa = r"(?P<l>aa)", r"(?P<l>a)a"                 # L60's B and A
YP = [("`(B | A) & (l: <20)` on `25`", [(Bd, []), (Ad, [])], [lab_lt(20)], "25"),
      ("`(B & (l: <20)) | (A & (l: <20))` on `25`", [(Bd, [lab_lt(20)]), (Ad, [lab_lt(20)])], [], "25"),
      ("`(B | A) & (l: <10)` on `12`", [(Bd, []), (Ad, [])], [lab_lt(10)], "12"),
      ("`((B & (l: >50)) | A) & (l: <10)` on `12`", [(Bd, [lab_gt(50)]), (Ad, [])], [lab_lt(10)], "12"),
      ("L60 `(B | A) & (l: \"a\")` on `aa`", [(Ba, []), (Aa, [])], [lab_eq("a")], "aa"),
      ("`(B & (l: \"a\")) | (A & (l: \"a\"))` on `aa`", [(Ba, [lab_eq("a")]), (Aa, [lab_eq("a")])], [], "aa")]
for nm, brs, outer, s in YP:
    emit((1, nm), "  BRANCH-SCOPE %s: (i) no fallthrough %s ; (ii) inner and outer fall through %s ; (iii) rev 23.1's scope rule %s" % (
        nm, alt_rep("i", brs, outer, s), alt_rep("ii", brs, outer, s), alt_rep("iii", brs, outer, s)))
DPOOL = M23.strings("0129", 3)                      # 85 texts over {0,1,2,9} to length 3
for rd in order(["i", "ii", "iii"]):
    for mode in order(["WHOLE", "SEARCHED"]):
        f = (lambda brs, outer, s: alt_whole(rd, brs, outer, s)) if mode == "WHOLE" else (lambda brs, outer, s: alt_search(rd, brs, outer, s) is not None)
        d, w = cnt(DPOOL, lambda s: f([(Bd, []), (Ad, [])], [lab_lt(20)], s) != f([(Bd, [lab_lt(20)]), (Ad, [lab_lt(20)])], [], s))
        emit((2, rd, mode), "  BRANCH-SCOPE reading (%s) %s (%d texts over {0,1,2,9} to length 3): `(B | A) & (l: <20)` vs `(B & (l: <20)) | (A & (l: <20))` differ %d first %r" % (rd, mode, len(DPOOL), d, w))

# Y2 (A3): find-all places. `when` body W vs the filter form F on KH; t2 & !q's hits; /a|aba/ vs /aba|a/.
pk, KH, KHP, KHPOOL, T2, T2POOL = B.pk, B.KH, B.KHP, B.KHPOOL, B.T2, B.T2POOL
for nm, c in order([("(h: <5)", ptest("h", lt(5))), ("(h = 0: <5)", ptest("h", lt(5), "0"))]):
    W = B.when_body(c, pk); F = C.filter_form(W)
    d, w = cnt(KHPOOL, lambda s: (len(B.findall(W, s)) >= 2) != (len(B.findall(F, s)) >= 2))
    emit((3, nm), "  FIND-ALL occurrences(min = 2) of the `when` expansion W vs the filter form F, c = %s, over KH (1,110): holds-or-not differ %d first %r" % (nm, d, w))
    emit((3, nm, "row"), "  FIND-ALL c = %s on `3;0;5`: W %s ; F %s" % (nm, B.fa(W, "3;0;5"), B.fa(F, "3;0;5")))
TQ = P2(T2, [], [B.q])
for s in order(["9:30", "10:45", "9:15", "09:30"]):
    emit((4, s), "  FIND-ALL `t2 & !q` hits on `%s`: %s" % (s, B.fa(TQ, s)))
for rx in order(["a|aba", "aba|a"]):
    emit((5, rx), "  FIND-ALL /%s/ on `aba`: %s" % (rx, ["`%s`@%d" % (m.group(0), m.start()) for m in re.finditer(rx, "aba")]))

# Y3 (A4, record-under-not): the joint, the record, and the critic's completion reading on `t2`.
# Completion (review r34 FIXINDUCED-2's alternative, unverified there): a joint with an absent part is UNKNOWN only
# when some value of the missing part could change the answer; the values tried are the label's own value set
# (m of t2: every `\d\d`, 100 texts).
MDOM = [a + b for a in "0123456789" for b in "0123456789"]
def joint_plain(S, T): return lambda r: None if r.get("h") is None or r.get("m") is None else (S(r["h"]) and T(r["m"]))
def joint_comp(S, T):
    def c(r):
        if r.get("h") is None: return None
        if r.get("m") is not None: return S(r["h"]) and T(r["m"])
        vals = set(bool(S(r["h"]) and T(mv)) for mv in order(MDOM))
        return vals.pop() if len(vals) == 1 else None
    return c
def record(S, T): return lambda r: kand([None if r.get("h") is None else S(r["h"]), None if r.get("m") is None else T(r["m"])])
S9, T30 = lt(9), lt(30)
LATE = lambda h, m: PS23D(h, m) and (int(h), int(m)) >= (9, 30)
PS23D = CANON
def late_tuple(padded):
    return lambda h, m: (re.fullmatch(r"\d+", h) is not None and re.fullmatch(r"\d+", m) is not None and (int(h), int(m)) >= (9, 30)) if padded else LATE(h, m)
def jt_tuple(R, comp):
    def c(r):
        if r.get("h") is None: return None
        if r.get("m") is not None: return R(r["h"], r["m"])
        if not comp: return None
        vals = set(bool(R(r["h"], mv)) for mv in order(MDOM))
        return vals.pop() if len(vals) == 1 else None
    return c
for nm, J in order([("joint (plain)", joint_plain(S9, T30)), ("joint (completion)", joint_comp(S9, T30)), ("record", record(S9, T30))]):
    emit((6, nm), "  RECORD-UNDER-NOT `t2 & NOT %s` with S = `<9`, T = `<30` on `10`: %s ; on `9`: %s ; on `10:15`: %s" % (
        nm, hs(P2(T2, [NOT(J)]), "10"), hs(P2(T2, [NOT(J)]), "9"), hs(P2(T2, [NOT(J)]), "10:15")))
for mode in order(["WHOLE", "SEARCHED"]):
    for a_nm, a_J in order([("joint (completion)", joint_comp(S9, T30)), ("joint (plain)", joint_plain(S9, T30))]):
        d, w = cnt(T2POOL, lambda s: B.holds(mode, P2(T2, [NOT(a_J)]), s) != B.holds(mode, P2(T2, [NOT(record(S9, T30))]), s))
        emit((7, mode, a_nm), "  RECORD-UNDER-NOT %s T2 (11,110) `t2 & NOT %s` vs `t2 & NOT record`: differ %d first %r" % (mode, a_nm, d, w))
for pd in order([False, True]):
    for comp in order([False, True]):
        emit((8, pd, comp), "  RECORD-UNDER-NOT the cost: `t2 & ((h, m): %s)` %s on `10`: %s" % (
            "padded(>= (9, 30))" if pd else ">= (9, 30)", "completion" if comp else "plain (UNKNOWN on an absent part)",
            hs(P2(T2, [jt_tuple(late_tuple(pd), comp)]), "10")))

# Y4 (D2): polarity witnesses.
SV, SVPOOL, REP, REPPASS, REPPOOL = M23.SV, M23.SVPOOL, M23.REP, M23.REPPASS, M23.REPPOOL
rp = lambda c: P2(REP, [c], passre=REPPASS)
notS = lambda S: (lambda v: not S(v))
for mode in order(["WHOLE", "SEARCHED"]):
    d, w = cnt(REPPOOL, lambda s: B.holds(mode, rp(NOT(ptest("h", lt(0)))), s) != B.holds(mode, rp(ptest("h", notS(lt(0)))), s))
    emit((9, mode), "  POLARITY L30 repeated edge %s REP (364) `NOT (h: <0)` vs `(h: !<0)` differ %d first %r" % (mode, d, w))
emit((9, "row"), "  POLARITY L30 repeated edge on `3;;`: `NOT (h: <0)` %s ; `(h: !<0)` %s" % (hs(rp(NOT(ptest("h", lt(0)))), "3;;"), hs(rp(ptest("h", notS(lt(0)))), "3;;")))
T2S = T2POOL[::7]
PT = P2(T2)
WIT = [("`t2 & NOT (h: <0)`", P2(T2, [NOT(test("h", lt(0)))])),
       ("`t2 & !(t2 & (h: <0))`", P2(T2, [], [P2(T2, [test("h", lt(0))])])),
       ("`t2 & !(t2 & NOT (h: <0))`", P2(T2, [], [P2(T2, [NOT(test("h", lt(0)))])]))]
for nm, P in order(WIT):
    for mode in order(["WHOLE", "SEARCHED"]):
        c_, _ = cnt(T2S, lambda s: B.holds(mode, P, s))
        d, w = cnt(T2S, lambda s: B.holds(mode, P, s) != B.holds(mode, PT, s))
        emit((10, nm, mode), "  POLARITY %s %s (every 7th T2 text, %d): holds %d; vs plain `t2` differ %d first %r" % (nm, mode, len(T2S), c_, d, w))
SVP = lambda c: P2(SV, [c])
DU = [("SV", SVPOOL, "`P & !(P & (h = 9: <5))` vs `P & !(P & (h: <5))`", P2(SV, [], [SVP(test("h", lt(5), "9"))]), P2(SV, [], [SVP(test("h", lt(5)))])),
      ("SV", SVPOOL, "`NOT NOT (h = 9: <5)` vs `NOT NOT (h: <5)`", SVP(NOT(NOT(test("h", lt(5), "9")))), SVP(NOT(NOT(test("h", lt(5)))))),
      ("REP", REPPOOL, "`P & !(P & (h = \"x\": <5))` vs `P & !(P & (h: <5))`", P2(REP, [], [rp(ptest("h", lt(5), "x"))], passre=REPPASS), P2(REP, [], [rp(ptest("h", lt(5)))], passre=REPPASS))]
for pn, pool, nm, a, b in order(DU):
    for mode in order(["WHOLE", "SEARCHED"]):
        d, w = cnt(pool, lambda s: B.holds(mode, a, s) != B.holds(mode, b, s))
        emit((11, nm, mode), "  DEFAULT-UNUSED %s %s (%d) %s: differ %d first %r" % (mode, pn, len(pool), nm, d, w))

# Y5 (D3): pass-and + group-truth vs the De Morgan dual.
def some_exists(f): return lambda r: any(f(p) is True for p in (order(r["_real"])[:1] if SAB else order(r["_real"])))   # sabotage: first pass only
def some_kleene(f, key="_real"):
    def c(r):
        vs = [f(p) for p in (order(r[key])[:1] if SAB else order(r[key]))]
        if any(v is True for v in vs): return True
        if any(v is None for v in vs): return None
        return False
    return c
passlt5 = lambda p: None if p.get("h") is None else lt(5)(p["h"])
PLAIN = rp(ptest("h", lt(5)))
for nm, sm in order([("EXISTS (the draft's group-truth)", some_exists), ("three-valued some over the real passes", some_kleene),
                     ("three-valued some over the pass table (the null pass row on zero passes)", lambda f: some_kleene(f, "_passes"))]):
    DUAL = rp(NOT(sm(lambda p: knot(passlt5(p)))))
    for mode in order(["WHOLE", "SEARCHED"]):
        d, w = cnt(REPPOOL, lambda s: B.holds(mode, PLAIN, s) != B.holds(mode, DUAL, s))
        emit((12, nm, mode), "  DE-MORGAN %s REP (364) `(h: <5)` vs `NOT some(NOT (h: <5))` with some = %s: differ %d first %r" % (mode, nm, d, w))
    for s in order(["", "3;;", "7;;"]):
        emit((13, nm, s), "  DE-MORGAN on `%s`: `(h: <5)` %s ; `NOT some(NOT (h: <5))` [%s] %s" % (s, hs(PLAIN, s), nm, hs(DUAL, s)))
for k in sorted(LINES, key=lambda k: tuple(str(x) for x in k)): print(LINES[k])
print("END")
