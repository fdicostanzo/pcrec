#!/usr/bin/env python3
# Lane predspec261 (2026-11-18): the evidence of docs/design/predicates_draft.md REVISION 26.1 (review r47's fixes and
# the owner's conditional rulings). DESIGN EVIDENCE ONLY; rules nothing.  EXTENDS predspec26's engine (copied, not
# imported; predspec26_evidence/ stays as committed): its parts N..OQ are kept, with r47's evidence fixes applied IN
# PLACE (C1: N3 replaced by the nested run NZ; C2: `outward` replaced by a reach classifier, the old one kept as
# sabotage s16; C3: CS3's `&` arm built by an independent FILTER model and drilled inside a loop; C4: `hole_ok` gives
# a backreference position its compile error and the count position its kind split, P6 rows added), and NEW PARTS:
#   R47  the review's answer-level and design-level witnesses (A1-A6, B1-B6), each re-run here;
#   COND the conditional (the guarded form; when-default; when-test; when-peek; when-alone), every mode.
#
# CONTROLS: as predspec26 (libpcre2-8 through ../rxmodel_evidence/pcre2h.py, run, never read: D181; Python `re`),
# plus: PCRE2's own conditional group `(?(?=A)B|C)` for the peek form; a direct Python semantic function (split
# enumeration with `re.fullmatch`) for the consumed form; a path-enumerating FILTER model (every path of the left
# operand recorded by a failing callout, then judged) for `&`; libpcre2 own-text vs in-subject runs for the reach
# classifier.  RULE-AS-CODE lines stay CONSISTENCY checks, never independent controls.
#
# Run (W = the worktree; from $PCREC_TMPDIR/scratch/predspec261; one process, seconds):
#   timeout 900 python3 -I -B W/docs/dev/lanes/predspec261_evidence/predspec261_model.py > fwd.out
#   PREDSPEC261_SABOTAGE=1 (all) or a comma list of s1..s28: deliberately wrong rules; the checks must fail:
#     s1 hit-carry OFF; s2 the count-hole product FIRST HOLE FASTEST; s3 removal of the PIECE; s4 a filter judged
#     BEFORE its holes are filled; s5 dynamic scoping of references; s6 the `_` prefix ignored; s7 a number allowed on
#     a composed pattern; s8 array arithmetic PAIRWISE; s9 a value REINTERPRETED as regex; s10 a lone complement
#     matching; s11 a quantified condition read as regex; s12 lookahead labels INVISIBLE; s13 a sequenced condition
#     tested ONCE (predspec26's thirteen, unchanged);
#     s14 the nullable argument read as rev 26's "at most one hit, the first" (A1);
#     s15 `0` inside a part read as the COMPOSED rx's match (A2 / NZ);
#     s16 the reach classifier replaced by rev 26's first/last-atom `outward` (C2);
#     s17 the `&` FILTER model judging only the FIRST path of its left operand (C3);
#     s18 `hole_ok` as rev 26 (backreference OPEN; any int a count) (C4, B3);
#     s19 the conditional read as the naive alternation `A B | C` (no guard);
#     s20 a bare pattern as the test PEEKED (not consumed) (when-peek);
#     s21 a missing else FAILS (when-default);
#     s22 a quantified group holding ONLY conditions accepted (B4);
#     s23 the value-hole model's equality case-SENSITIVE under `(?i)` (B5);
#     s24 the label model replaced by PCRE's capture (A3, A4, A5: the one rule's arm removed);
#     s25 count-hole copies lowered as a SEQUENCE of per-hole alternations (B1);
#     s26 a class member hole read as more characters in BOTH arms (B6);
#     s27 the program's `anything` replaced by a non-nullable operand (A6);
#     s28 one array bound ONCE for all its mentions (B2).
import os, sys, re, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rxmodel_evidence"))
import pcre2h as P                                           # noqa: E402

_sv = os.environ.get("PREDSPEC261_SABOTAGE", "")
SABS = set("s%d" % i for i in range(1, 29)) if _sv == "1" else set(x for x in _sv.split(",") if x)
def sab(k): return k in SABS

CHECKS = []
def check(name, ok):
    CHECKS.append((name, bool(ok)))
    return "OK" if ok else "FAILED"

NOTEMPTY_ATSTART = 0x00000008
DOTALL = 0x00000020
PCRE2_MATCH_UNSET_BACKREF = 0x00000200


def pool(alpha, n=5):
    out = [""]
    for k in range(1, n + 1):
        out += ["".join(t) for t in itertools.product(alpha, repeat=k)]
    return out


def W(rx, s):
    """WHOLE value: the first path that spans the whole text (anchored both ends)"""
    r = rx.match(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
    return r


def S(rx, s):
    return rx.match(s, 0)


def F(rx, s):
    """PCRE2's global loop (R.1.2)"""
    out, pos, ne = [], 0, False
    while pos <= len(s):
        r = rx.match(s, pos, (NOTEMPTY_ATSTART | P.PCRE2_ANCHORED) if ne else 0)
        if r is None:
            if ne:
                ne = False
                pos += 1
                continue
            break
        out.append(r)
        ne = r[1] == r[0]
        pos = r[1]
    return out


def lab(r, keys):
    return "" if not keys else " " + ", ".join("%s = %s" % (k, "unset" if r[2].get(k) is None else "`%s`" % r[2][k]) for k in keys)


def fW(rx, s, keys=()):
    r = W(rx, s)
    return "FAILS" if r is None else "HOLDS" + lab(r, keys)


def fS(rx, s, keys=()):
    r = S(rx, s)
    return "FAILS" if r is None else "`%s`@%d%s" % (s[r[0]:r[1]], r[0], lab(r, keys))


def fF(rx, s, keys=()):
    return "[" + ", ".join("`%s`@%d%s" % (s[a:b], a, lab((a, b, l), keys)) for a, b, l in F(rx, s)) + "]"


def row(rx, s, mode, keys=()):
    if mode == "W":
        r = W(rx, s)
        return None if r is None else tuple(r[2].get(k) for k in keys)
    if mode == "S":
        r = S(rx, s)
        return None if r is None else (r[0], r[1]) + tuple(r[2].get(k) for k in keys)
    return tuple((a, b) + tuple(l.get(k) for k in keys) for a, b, l in F(rx, s))


def diff3(r1, r2, texts, keys1=(), keys2=None):
    keys2 = keys1 if keys2 is None else keys2
    out, first = [], None
    for m in "WSF":
        n = 0
        for s in texts:
            if row(r1, s, m, keys1) != row(r2, s, m, keys2):
                n += 1
                first = first or (m, s)
        out.append(n)
    return out, first


def show(rx, w, s_, f_, keys=()):
    return "WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (w, fW(rx, w, keys), s_, fS(rx, s_, keys), f_, fF(rx, f_, keys))


def num(v):
    """the canonical-numeral test of §2.4: a value is a number only in the \\d+ shape without leading zeros"""
    return v is not None and re.fullmatch(r"0|[1-9]\d*", v) is not None


print("predspec261 evidence; libpcre2-8 %s%s" % (P.version(), " ; SABOTAGE %s" % ",".join(sorted(SABS, key=lambda x: int(x[1:]))) if SABS else ""))
for line, ok in P.selfcheck():
    print("selfcheck: %s ; %s" % (line, check("selfcheck " + line[:30], ok)))
POOL3 = pool("37,")          # 364 texts
print("pools: `37,` length <= 5: %d texts" % len(POOL3))

# =====================================================================================================================
print("\n== PART N: number-names (only when there is no ambiguity) and its addendum (0 is always the entire match)")
# N1: the SHOWN witness of the sub-point: a number on a group whose NAME is shared inside one literal.
# (a) the label h (the one label rule: entering the loop resets h, the label is the last pass's own; unset on 0 passes)
# (b) group 1's own capture.  Model: libpcre2, the two groups renamed apart, the condition a callout.
la = P.Pcre(r'(?<g1>\d)(?:,(?<g2>\d))*(?C"t")', {"t": lambda c: num(c.get("g2")) and int(c.get("g2")) < 5})
lb = P.Pcre(r'(?<g1>\d)(?:,(?<g2>\d))*(?C"t")', {"t": lambda c: num(c.get("g1")) and int(c.get("g1")) < 5})
d, first = diff3(la, lb, POOL3)
print("N1 `/(?<h>\\d)(?:,(?<h>\\d))*/ & (1: <5)`: (a) the label h vs (b) group 1's own: %d / %d / %d of %d (holds and stretch), first %s"
      % (d[0], d[1], d[2], len(POOL3), first))
print("   (a) %s" % show(la, "3,7", "7,3", "3,7 7,3"))
print("   (b) %s" % show(lb, "3,7", "7,3", "3,7 7,3"))
print("   the record (shown): \"differ on 7 of 364 texts whole and 277 searched\" ; %s" % check("N1 shown 7/277 reproduced", d[0] == 7 and d[1] == 277))
print("   THE MANAGER'S READING (the sub-point falls under \"only when there is no ambiguity\" and is REFUSED): the two meanings a reader")
print("   can give `1` there DIFFER on the run above, so the number is ambiguous there: SUPPORTED (the run shows the ambiguity the rule refuses)")


# N2: RULE-AS-CODE: where a number may stand.  A program is ('lit', groups) | ('seq', ...) | ('hole', ...) | ('alt', ...)
# | ('rep', x) | ('and', ops); groups: list of names (None = unnamed) in opening-parenthesis order.
def number_allowed(prog, n):
    if n == 0:
        return True                                   # the addendum: 0 is always the entire match
    if sab("s7"):                                     # sabotage: the nearest literal's group
        while prog[0] != "lit":
            prog = prog[-1] if prog[0] != "and" else [p for p in prog[1] if p[0] != "cond"][-1]
        return n <= len(prog[1])
    if prog[0] == "and":
        pats = [p for p in prog[1] if p[0] != "cond"]
        if len(pats) != 1:
            return False                              # more than one pattern operand in an `&` chain
        prog = pats[0]
    if prog[0] != "lit":
        return False                                  # a sequence, an inserted pattern, an alternation, a repeat's operand
    g = prog[1]
    if n > len(g):
        return False                                  # no such group: the unknown-label error
    nm = g[n - 1]
    return nm is None or g.count(nm) == 1             # a shared name is ambiguous (THE MANAGER'S READING, N1)


LIT1 = ("lit", [None])
WIT = [
    ("one literal `/(\\d),(\\d)/`, 1", ("lit", [None, None]), 1, True),
    ("one literal, shared name `/(?<h>\\d)(?:,(?<h>\\d))*/`, 1", ("lit", ["h", "h"]), 1, False),
    ("a sequence `A SEQ B`, 1", ("seq", LIT1, LIT1), 1, False),
    ("an inserted pattern `/${A},(\\d)/`, 1", ("hole", LIT1), 1, False),
    ("an alternation of patterns `(A | B)`, 1", ("alt", LIT1, LIT1), 1, False),
    ("a repeat's operand `A+`, 1", ("rep", LIT1), 1, False),
    ("an `&` chain with two patterns `A & B & (1: ..)`, 1", ("and", [LIT1, LIT1, ("cond",)]), 1, False),
    ("an `&` chain with one pattern `A & (1: ..)`, 1", ("and", [LIT1, ("cond",)]), 1, True),
    ("0 on a sequence", ("seq", LIT1, LIT1), 0, True),
    ("0 on an inserted pattern", ("hole", LIT1), 0, True),
    ("0 on an alternation of patterns", ("alt", LIT1, LIT1), 0, True),
    ("0 on a repeat's operand", ("rep", LIT1), 0, True),
    ("0 on an `&` chain with two patterns (THE MANAGER'S READING (1))", ("and", [LIT1, LIT1, ("cond",)]), 0, True),
]
for nm_, prog, n, want in WIT:
    got = number_allowed(prog, n)
    print("N2 RULE-AS-CODE %-70s -> %-8s ; %s" % (nm_, "allowed" if got else "REFUSED (name the group)", check("N2 " + nm_, got == want)))

# N3 (rev 26) is WITHDRAWN (review r47 C1: its two arms were the same span on every call, so it could not fail).
# NZ REPLACES IT (r47 A2): a `0` written in a condition INSIDE a part X, X placed in a pattern hole `/x${X}y/`,
# X := `/\d+/ & (0: /3\d*/)`.  The zero-place LAW (`A & B` = `A & (0: B)`) gives X the program `/\d+/ & /3\d*/`, so the
# control is the LAW's program `x(?<p>(?=3)\d+)y` (itself checked against python `re` `x3\d*y`, WHOLE).  Arms: `0` =
# the part's own match (the stretch of X, group p) vs `0` = the COMPOSED rx's entire match (the outer final match).
NZPOOL = pool("x37y", 6)                                       # 5,461 texts; minimum witness length 3 (`x3y`)
nz_law = P.Pcre(r'x(?<p>(?=3)\d+)y')
nz_law_py = sum(1 for t in NZPOOL if (re.fullmatch(r'x3\d*y', t) is None) != (W(nz_law, t) is None))
nz_own = P.Pcre(r'x(?<p>\d+)(?C"t")y', {"t": lambda c: re.fullmatch(r'3\d*', c.get("p")) is not None})
nz_comp = P.Pcre(r'x(?<p>\d+)y(?C"t")', {"t": lambda c: re.fullmatch(r'3\d*', c.stretch()) is not None})
nz_arm = nz_comp if sab("s15") else nz_own
d_own, f_own = diff3(nz_arm, nz_law, NZPOOL, ("p",))
d_comp, f_comp = diff3(nz_comp, nz_law, NZPOOL, ("p",))
print("NZ `/x${X}y/`, X := `/\\d+/ & (0: /3\\d*/)`, vs the LAW's program (LAW vs python `re` `x3\\d*y` WHOLE: %d differ), %d texts over `x37y` length <= 6:"
      % (nz_law_py, len(NZPOOL)))
print("    `0` = the part's own match%s: %d / %d / %d differ ; `0` = the composed rx's entire match: %d / %d / %d differ, first %s"
      % (" (SABOTAGED s15: composed)" if sab("s15") else "", d_own[0], d_own[1], d_own[2], d_comp[0], d_comp[1], d_comp[2], f_comp))
print("    the composed reading never matches: %s ; %s" % (all(S(nz_comp, t) is None for t in NZPOOL),
      check("NZ zero inside a part = the part's own match", nz_law_py == 0 and d_own == [0, 0, 0] and d_comp[0] > 0)))
print("    (r47 V2 printed 0/0/0 and 15/470/470; the `&` row's `0` and the HOLE row's `0` now say where the `0` is WRITTEN)")

# N4: THE MANAGER'S READING (2): inside a loop body or a hit-list argument, 0 written in that part's own condition is
# that part's own match for the current pass / hit.  The run: zero-place's LAW (`A & B` = `A & (0: B)`) inside an
# occurrences argument holds under "the part's own match" and fails under PCRE's group 0 (the match start to here).
GAP = r'[^\d]*'
occ_own = P.Pcre(r'\A(?:' + GAP + r'(?<hit>\d+)(?C"t"))*' + GAP + r'\z', {"t": lambda c: re.fullmatch(r'3\d*', c.get("hit") or "") is not None})
occ_g0 = P.Pcre(r'\A(?:' + GAP + r'(?<hit>\d+)(?C"t"))*' + GAP + r'\z', {"t": lambda c: re.fullmatch(r'3\d*', c.stretch()) is not None})
occ_law = P.Pcre(r'\A(?:' + GAP + r'(?<hit>(?=3)\d+))*' + GAP + r'\z')
POOLN4 = pool("3 7", 5)
def hits(rx, s):
    return W(rx, s) is not None
dd = [sum(1 for s in POOLN4 if hits(occ_own, s) != hits(occ_law, s)), sum(1 for s in POOLN4 if hits(occ_g0, s) != hits(occ_law, s))]
print("N4 every number a hit (gaps without digits): `occurrences(/\\d+/ & (0: /3\\d*/))` vs `occurrences(/\\d+/ & /3\\d*/)` (the LAW inside a hit), WHOLE over %d texts: 0 = the hit's own match %d differ ; 0 = PCRE's group 0 %d differ ; %s"
      % (len(POOLN4), dd[0], dd[1], check("N4 zero in a hit is the hit's own", dd[0] == 0 and dd[1] > 0)))
print("   THE MANAGER'S READING (2) SUPPORTED: only the part's-own reading keeps the LAW in that place (as rev 24.4's zero-place run found at the top)")

# =====================================================================================================================
print("\n== PART H: hit-carry (it carries: `occurrences` is a rewrite) and the nullable argument (a warning)")
# occurrences(r, min = 2) on a stretch: the one-pattern lazy-gap loop, \A(?:[\s\S]*?(?:R)){2,}[\s\S]*\z, the condition
# c := NOT (h: >= 5) a callout BEFORE the group.  hit-carry RULED: before its group c reads the PREVIOUS hit's h, which is
# what PCRE's capture state gives at that point.  Sabotage s1: c reads its own hit only (h reset at each hit start).
def c_not_ge5(ctx):
    h = None if sab("s1") and ctx.span("h") is not None and ctx.span("h")[0] < ctx.pos and ctx.span("h")[1] <= ctx.pos and ctx.pos > 0 and False else ctx.get("h")
    if sab("s1"):
        h = None                                       # its own hit has not set h before the group
    return not (num(h) and int(h) >= 5)
HC = P.Pcre(r'\A(?:[\s\S]*?(?:(?C"c")(?<h>\d))){2,}[\s\S]*\z', {"c": c_not_ge5})
HCs = P.Pcre(r'(?:[\s\S]*?(?:(?C"c")(?<h>\d))){2,}[\s\S]*', {"c": c_not_ge5})
print("H1 `occurrences(/${c}(?<h>\\d)/, min = 2)`, c := NOT (h: >= 5): WHOLE `73` %s ; SEARCHED `73` %s ; FIND-ALL `3x73` %s"
      % (fW(HC, "73", ("h",)), fS(HCs, "73", ("h",)), fF(HCs, "3x73", ("h",))))
print("   the record's witness under \"it carries\" (shown with the leaning, rev 25.1's PART C C2): WHOLE `73` FAILS / SEARCHED FAILS / FIND-ALL [`3x73`@0 h = `7`] ; %s"
      % check("H1 carries", W(HC, "73") is None and S(HCs, "73") is None and [(a, b, l["h"]) for a, b, l in F(HCs, "3x73")] == [(0, 4, "7")]))
HA = P.Pcre(r'\A(?:[\s\S]*?(?:(?<h>\d)(?C"c"))){2,}[\s\S]*\z', {"c": lambda c: not (num(c.get("h")) and int(c.get("h")) >= 5)})
print("H2 the condition AFTER its label (his \"put the condition after the label to get the normal behavior\"): WHOLE `73` %s ; `33` %s ; `37` %s (before its group, carried: `37` %s) ; %s"
      % (fW(HA, "73", ("h",)), fW(HA, "33", ("h",)), fW(HA, "37", ("h",)), fW(HC, "37", ("h",)), check("H2 after = own hit", W(HA, "73") is None and W(HA, "33") is not None and W(HA, "37") is None and W(HC, "37") is not None)))
# THE MANAGER'S CONSEQUENCE: R.1.9's "its hits are those of a plain search" holds only for an argument with no
# condition before its group.  Run: the hit list (the stretch, whole) of the carried argument vs the plain search's
# hits filtered per hit, over `37x` length <= 5.
POOLX = pool("37x")
HP = P.Pcre(r'\A(?:[\s\S]*?(?:(?<h>\d))){2,}[\s\S]*\z')
nd = sum(1 for s in POOLX if (W(HC, s) is None) != (W(HP, s) is None))
print("H3 THE MANAGER'S CONSEQUENCE (R.1.9's \"its hits are those of a plain search\" holds only with no condition before its group): carried vs the argument's plain hits (rev 25.1's NO candidate: c before its group reads nothing set, so it always holds), WHOLE %d of %d texts differ ; %s"
      % (nd, len(POOLX), check("H3 carried != plain", nd == 84)))
print("   SUPPORTED: rev 25.1's PART C C2 printed WHOLE 84 of 364 for the same pair; here %d" % nd)
# the nullable argument: a WARNING, PCRE's meaning kept (THE MANAGER'S READING): occurrences(/\d*/) on `a1`, the
# one-pattern loop with the empty hit, and the plain find-all of the argument
NU = P.Pcre(r'\d*')
print("H4 the nullable argument `/\\d*/` (a warning, ruled): PCRE's FIND-ALL of it on `a1b` %s" % fF(NU, "a1b"))
TR = []
NUL = P.Pcre(r'\A(?:[\s\S]*?(?<hit>\d*)(?C"r"))*[\s\S]*\z', {"r": lambda c: TR.append((c.span("hit"), c.get("hit"))) or True})
okn = W(NUL, "a1b") is not None
print("H5 the same argument under the REWRITE (the one-pattern loop, hit-carry's premise), WHOLE `a1b`: %s ; hits recorded by a callout %s (one empty hit at 0: PCRE ends a loop on an empty iteration; §2.6's first refusal's fact)" % ("HOLDS" if okn else "FAILS", TR))
print("   THE MANAGER'S READING (\"the program keeps PCRE's meaning for the empty hit, as the empty search does\"): AMBIGUOUS on the run: PCRE's LOOP (the rewrite) gives ONE hit, PCRE's find-all (the empty search's meaning) gives FOUR; NOT SUPPORTED as worded; the ruled premise (a rewrite) ENTAILS the loop's one hit (told, not asked); the `pcrec.` name: NOT RUNNABLE (a name)")
check("H5 loop gives one empty hit", TR == [((0, 0), "")])
check("H4 nullable meaning exists", [(a, b) for a, b, _ in F(NU, "a1b")] == [(0, 0), (1, 2), (2, 2), (3, 3)])

# =====================================================================================================================
print("\n== PART P: product-order (count holes only; first slowest), removal (the whole copy), name-hole (an error)")
def copies(holes, order_first_slowest=True):
    """the cartesian product of the holes' values, first hole slowest (the ruled order) unless s2"""
    prod = list(itertools.product(*holes))
    if not order_first_slowest or sab("s2"):
        prod = [tuple(reversed(t)) for t in itertools.product(*reversed(holes))]
    return prod
def count_copies(tmpl, holes):
    return "(?|" + "|".join(tmpl.format(*t) for t in copies(holes)) + ")"
# P1: the shown witness `/(?<x>\d{${a}})(?<y>\d{${b}})/`, a, b := [1, 2], WHOLE `123`
p1 = P.Pcre(count_copies(r"(?<x>\d{{{0}}})(?<y>\d{{{1}}})", [[1, 2], [1, 2]]).replace("(?|", "(?J)(?|", 1) if False else
            "(?|" + "|".join(r"(?<x>\d{%d})(?<y>\d{%d})" % t for t in copies([[1, 2], [1, 2]])) + ")")
print("P1 `/(?<x>\\d{${a}})(?<y>\\d{${b}})/`, a, b := [1, 2], the copies in product order: %s ; WHOLE `123` %s ; %s"
      % (p1.pattern, fW(p1, "123", ("x", "y")), check("P1 first slowest x=1 y=23", (lambda r: r and r[2]["x"] == "1" and r[2]["y"] == "23")(W(p1, "123")))))
# P2: the manager's python run shown to him: a sequence of two alternations is the product in first-slowest order
r1 = re.fullmatch(r"(?P<x>\d|\d\d)(?P<y>\d|\d\d)", "123")
r2 = re.fullmatch(r"(?P<x>\d\d|\d)(?P<y>\d\d|\d)", "123")
print("P2 python `re` (the manager's run, shown): `(?P<x>\\d|\\d\\d)(?P<y>\\d|\\d\\d)` whole `123` x = `%s`, y = `%s` ; longest first x = `%s`, y = `%s` ; %s"
      % (r1["x"], r1["y"], r2["x"], r2["y"], check("P2 shown python run", (r1["x"], r1["y"], r2["x"], r2["y"]) == ("1", "23", "12", "3"))))
# the same with libpcre2 on the pool: the sequence of alternations vs the copies (labels compared)
seqalt = P.Pcre(r"(?<x>\d|\d\d)(?<y>\d|\d\d)")
POOLD = pool("123", 5)
d, first = diff3(seqalt, p1, POOLD, ("x", "y"))
print("P3 libpcre2: the sequence of two alternations vs the first-slowest copies, labels x, y: %d / %d / %d of %d ; %s"
      % (d[0], d[1], d[2], len(POOLD), check("P3 seq-of-alts = first slowest", d == [0, 0, 0])))
print("   THE MANAGER'S READING (\"first slowest is the order regex itself gives a sequence of alternations\"): SUPPORTED")
# P4: removal, the whole copy: `/a|\d{${m},${M}}/`, m := [5], M := [2]
def remove(tmpl_whole, tmpl_piece, holes):
    keep = []
    for t in copies(holes):
        m_, M_ = t
        if m_ <= M_:
            keep.append(t)
    if sab("s3"):                                      # the piece holding the hole removed
        return tmpl_piece.format("|".join(r"\d{%d,%d}" % t for t in keep) or "(?!)")
    return "(?:" + "|".join(tmpl_whole.format(*t) for t in keep) + ")" if keep else "(?!)"
p4 = P.Pcre(remove(r"a|\d{{{0},{1}}}", r"a|(?:{0})", [[5], [2]]))
print("P4 removal `/a|\\d{${m},${M}}/`, m := [5], M := [2]: %s ; %s ; %s"
      % (p4.pattern, show(p4, "a", "xa", "a xa"), check("P4 whole copy removed: never matches", W(p4, "a") is None and S(p4, "xa") is None and F(p4, "a xa") == [])))
print("   the record (shown): the whole copy removed, \"the program never matches, not even `a`\" REPRODUCED")
print("   THE MANAGER'S READING (every copy removed -> the can-never-match warning reports it): RULE-AS-CODE only; the program above matches nothing on any text: %s"
      % check("P4b never matches", all(S(p4, s) is None for s in pool("a5", 4))))
# P5: name-hole: an array in a group-name hole is a compile error (the shown join reproduced first)
pj = P.Pcre(r"(?:(?<a>\d)|(?<b>\d))")
r = W(pj, "7")
print("P5 the joining reading he was shown (WITHDRAWN): `(?:(?<a>\\d)|(?<b>\\d))` on `7`: a = %s, b = %s (the second copy dead) ; %s"
      % (r[2]["a"], r[2]["b"], check("P5 shown join reproduced", r[2]["a"] == "7" and r[2]["b"] is None)))
def hole_ok(position, values):
    """RULE-AS-CODE: what each hole position takes (each position its own rules).  Rev 26.1 (review r47 C4, B3):
    a BACKREFERENCE position is a compile error (R.1.0's HOLE POSITIONS row, THE DRAFT'S READING since rev 25.1); a
    COUNT position takes values that are counts (a non-negative integer: THE DRAFT'S READING of the split, B3): a
    value that is not a count (-1, text) is the kind error; a count too large for a copy (70000 > 65535) is legal
    here and its copy is REMOVED (`legal`, removal) -- see count_copy_legal.  Sabotage s18: rev 26's classifier."""
    if position == "count":
        if sab("s18"):
            return all(isinstance(v, int) for v in values)
        return all(isinstance(v, int) and v >= 0 for v in values)
    if position == "name":
        return len(values) == 1                               # one name; an array is a compile error
    if position == "pattern":
        return True                                           # an alternation inside the group (no copies)
    if position == "backreference":
        return None if sab("s18") else False                  # a compile error (THE DRAFT'S READING, rev 25.1)
    return None                                               # class, option: OPEN (other-holes)
def count_copy_legal(m):
    """a copy is legal when PCRE compiles it (libpcre2, not a rule): `\\d{m}`"""
    try:
        P.Pcre(r"\d{%d}" % m)
        return True
    except Exception:
        return False
for pos_, vals, want in (("name", ["a", "b"], False), ("name", ["a"], True), ("count", [2, 4], True), ("count", ["2", "x"], False),
                         ("count", [2, "x"], False), ("count", [-1], False), ("count", [70000], True), ("class", ["a", "b"], None),
                         ("backreference", ["h"], False)):
    got = hole_ok(pos_, vals)
    print("P6 RULE-AS-CODE a %-13s hole given %-12s -> %s ; %s" % (pos_, vals, {True: "accepted", False: "COMPILE ERROR", None: "OPEN (no ruling)"}[got], check("P6 %s %s" % (pos_, vals), got == want)))
print("P6b libpcre2 (the control for the split): `\\d{-1}` compiles as TEXT (WHOLE `1{-1}` %s); `\\d{70000}` legal copy: %s; `\\d{65535}`: %s ; %s"
      % (fW(P.Pcre(r"\d{-1}"), "1{-1}"), count_copy_legal(70000), count_copy_legal(65535),
         check("P6b pcre split", W(P.Pcre(r"\d{-1}"), "1{-1}") is not None and not count_copy_legal(70000) and count_copy_legal(65535))))
print("    so -1 would silently become literal text (the kind error keeps it out); 70000 is a count with no legal copy (removed, and if every copy is removed the warning)")
# the count-hole kind ruling: PCRE would read `\d{x}` as literal text, so the error is the language's
px = P.Pcre(r"\d{x}")
print("P7 a count hole must produce counts (ruled): PCRE itself accepts `\\d{x}` as text (WHOLE `1{x}` %s), so the refusal is the language's rule, not PCRE's ; %s"
      % (fW(px, "1{x}"), check("P7 pcre reads {x} as text", W(px, "1{x}") is not None)))

# =====================================================================================================================
print("\n== PART AL: array-lift (operations on arrays combine on the product, first operand slowest)")
def lift(op, a, b):
    a = a if isinstance(a, list) else [a]
    b = b if isinstance(b, list) else [b]
    if sab("s8"):
        return [op(x, y) for x, y in zip(a, b)] if len(a) == len(b) else [op(x, b[0]) for x in a] if len(b) == 1 else None
    return [op(x, y) for x in a for y in b]
add, mul = (lambda x, y: x + y), (lambda x, y: x * y)
T = [("[2, 4] + 1", lift(add, [2, 4], 1), [3, 5]), ("[2, 4] + [1, 10]", lift(add, [2, 4], [1, 10]), [3, 12, 5, 14]),
     ("[2, 4] * [1, 10]", lift(mul, [2, 4], [1, 10]), [2, 20, 4, 40]), ("1 + [2, 4]", lift(add, 1, [2, 4]), [3, 5]),
     ("[1, 2] + [10, 20, 30]", lift(add, [1, 2], [10, 20, 30]), [11, 21, 31, 12, 22, 32])]
for nm_, got, want in T:
    print("AL1 %-22s = %-26s ; %s" % (nm_, got, check("AL1 " + nm_, got == want)))
print("   the three hand-worked arrays he was shown REPRODUCED (rows 1-3); rows 4-5 extend the rule (a single value first; unequal lengths)")
n1 = lift(add, [2, 4], 1)
pr = P.Pcre("(?|" + "|".join(r"\d{%d}" % k for k in n1) + ")")
print("AL2 `rx.repeat(rx.digit, n + 1)`, n := [2, 4]: n + 1 = %s, copies %s ; %s ; %s"
      % (n1, pr.pattern, show(pr, "123", "123456", "12345 678"), check("AL2 count from lifted array", W(pr, "123") is not None and W(pr, "1234") is None)))
dup = lift(add, [1, 2], [2, 1])
print("AL3 a repeated result is harmless (THE MANAGER'S READING): [1, 2] + [2, 1] = %s ; as count copies the first occurrence wins: `(?|\\d{3}|\\d{2}|\\d{4}|\\d{3})` vs without the repeat: %s"
      % (dup, (lambda a, b: "%d / %d / %d of %d differ" % (tuple(diff3(a, b, POOLD)[0]) + (len(POOLD),)))(P.Pcre(r"(?|\d{3}|\d{2}|\d{4}|\d{3})"), P.Pcre(r"(?|\d{3}|\d{2}|\d{4})"))))
check("AL3 repeat harmless", diff3(P.Pcre(r"(?|\d{3}|\d{2}|\d{4}|\d{3})"), P.Pcre(r"(?|\d{3}|\d{2}|\d{4})"), POOLD)[0] == [0, 0, 0])

# =====================================================================================================================
print("\n== PART HF: hole-in-filter (fill the holes first, then judge the operand as a filter)")
def outward_r26(rx_text):
    """REV 26's classifier (KEPT ONLY AS SABOTAGE s16; review r47 C2): reads only the first and last atom"""
    t = rx_text
    while t.startswith("(?:"):
        t = t[3:]
    e = rx_text
    while e.endswith(")"):
        e = e[:-1]
    return bool(re.match(r"\\[bBGK]|\(\?<[=!]", t)) or bool(re.search(r"\\[bBGK]$|\(\?[=!][^()]*$", e))


INF = float("inf")
def rx_parse(t):
    """a parser for the regex subset the witnesses use (atoms, classes, groups, lookarounds, quantifiers, `|`)"""
    i = 0
    def alt():
        nonlocal i
        branches = [seq()]
        while i < len(t) and t[i] == "|":
            i += 1
            branches.append(seq())
        return ("alt", branches)
    def seq():
        nonlocal i
        items = []
        while i < len(t) and t[i] not in "|)":
            items.append(quant(atom()))
        return ("seq", items)
    def atom():
        nonlocal i
        c = t[i]
        if t.startswith("${", i):                              # an UNFILLED hole (only under sabotage s4): opaque
            i = t.index("}", i) + 1
            return ("char",)
        if c == "\\":
            e = t[i + 1]; i += 2
            if e in "bB":
                return ("edge",)
            if e in "GKAzZ":
                return ("anchor",)
            return ("char",)
        if c == "[":
            j = i + 1
            if t[j] == "^": j += 1
            if t[j] == "]": j += 1
            while t[j] != "]":
                j += 2 if t[j] == "\\" else 1
            i = j + 1
            return ("char",)
        if c in "^$":
            i += 1
            return ("anchor",)
        if c == "(":
            for pre, kind in (("(?<=", "behind"), ("(?<!", "behind"), ("(?=", "ahead"), ("(?!", "ahead"), ("(?:", "group")):
                if t.startswith(pre, i):
                    i += len(pre); break
            else:
                if t.startswith("(?<", i) or t.startswith("(?P<", i):
                    i = t.index(">", i) + 1
                else:
                    i += 1
                kind = "group"
            body = alt()
            assert t[i] == ")"
            i += 1
            return (kind, body) if kind != "group" else ("group", body)
        i += 1
        return ("char",)
    def quant(x):
        nonlocal i
        if i < len(t) and t[i] in "*+?{":
            if t[i] == "{":
                j = t.index("}", i)
                parts = t[i + 1:j].split(",")
                lo = int(parts[0]); hi = lo if len(parts) == 1 else (INF if parts[1] == "" else int(parts[1]))
                i = j + 1
            else:
                lo, hi = {"*": (0, INF), "+": (1, INF), "?": (0, 1)}[t[i]]
                i += 1
            if i < len(t) and t[i] in "?+":
                i += 1
            return ("rep", x, lo, hi)
        return x
    n = alt()
    assert i == len(t), (t, i)
    return n
def rx_w(n):
    """(min, max) width"""
    k = n[0]
    if k == "char": return (1, 1)
    if k in ("edge", "anchor", "ahead", "behind"): return (0, 0)
    if k == "group": return rx_w(n[1])
    if k == "seq":
        ws = [rx_w(x) for x in n[1]]
        return (sum(w[0] for w in ws), sum(w[1] for w in ws))
    if k == "alt":
        ws = [rx_w(x) for x in n[1]]
        return (min(w[0] for w in ws), max(w[1] for w in ws))
    if k == "rep":
        w = rx_w(n[1])
        return (w[0] * n[2], INF if (n[3] == INF and w[1] > 0) else w[1] * n[3])
def rx_reach(n, pre, post):
    """True if some piece can read outside the operand's stretch: an edge where the operand's own text before
    (pre) or after (post) it can be empty; an anchor; a lookahead wider than the shortest text after it; a lookbehind
    wider than the shortest text before it (the draft's sentence, R.1.4 operand-context, as a reach rule)"""
    k = n[0]
    if k == "char": return False
    if k == "edge": return pre == 0 or post == 0
    if k == "anchor": return True
    if k == "ahead": return rx_w(n[1])[1] > post or rx_reach(n[1], pre, 0)
    if k == "behind": return rx_w(n[1])[1] > pre or rx_reach(n[1], 0, post)
    if k == "group": return rx_reach(n[1], pre, post)
    if k == "alt": return any(rx_reach(x, pre, post) for x in n[1])
    if k == "rep": return rx_reach(n[1], pre, post)
    if k == "seq":
        ws = [rx_w(x)[0] for x in n[1]]
        return any(rx_reach(x, pre + sum(ws[:j]), post + sum(ws[j + 1:])) for j, x in enumerate(n[1]))
def outward(rx_text):
    """REV 26.1's reach classifier (review r47 C2): every piece, not only the first and last atom"""
    if sab("s16"):
        return outward_r26(rx_text)
    return rx_reach(rx_parse(rx_text), 0, 0)
def judge_filter(operand_text, holes):
    if sab("s4"):
        return "accepted" if not outward(operand_text) else "FILTER ERROR"
    filled = operand_text
    for k, v in holes.items():
        filled = filled.replace("${%s}" % k, "(?:%s)" % v)
    return "FILTER ERROR" if outward(filled) else "accepted"
for desc, op, holes, want in (("`/\\d+/ & /${num}/`, num := `/\\b\\d+\\b/`", "${num}", {"num": r"\b\d+\b"}, "FILTER ERROR"),
                              ("`/\\d+/ & num` (written out)", r"\b\d+\b", {}, "FILTER ERROR"),
                              ("`/\\d+/ & /${d}/`, d := `/\\d+/`", "${d}", {"d": r"\d+"}, "accepted"),
                              ("`/\\d+/ & /1${e}2/`, e := `/\\b/` (inside, both sides digits)", "1${e}2", {"e": r"\b"}, "accepted")):
    got = judge_filter(op, holes)
    print("HF1 RULE-AS-CODE %-62s -> %-12s ; %s" % (desc, got, check("HF1 " + desc, got == want)))
print("   the record's witness (shown): the leaning \"the filter error\" -> REJECTED in every mode, as written out")
# HF2 (review r47 C2): the classifier against an INDEPENDENT control: libpcre2 runs the operand on the stretch's own
# text (WHOLE) and in the subject from the stretch's start with its end tied by a callout; an operand READS OUTSIDE if
# the two differ on some (subject, stretch).  The classifier must be SOUND (never accept an operand that reads outside).
def reads_outside(B, texts):
    own = P.Pcre(B)
    tied = {}
    for t in texts:
        for a_ in range(len(t) + 1):
            for b_ in range(a_, len(t) + 1):
                rx = tied.setdefault(b_, P.Pcre(B + r'(?C"e")', {"e": (lambda bb: lambda c: c.pos == bb)(b_)}))
                if (W(own, t[a_:b_]) is not None) != (rx.match(t, a_, P.PCRE2_ANCHORED) is not None):
                    return (t, a_, b_)
    return None
HFPOOL = pool("12a", 4)                                       # 121 texts; the witnesses need length 3
HFOPS = [r"(?=\d\d\d)\d+", r"(?:\d+\b)[a-z]*", r"\b\d+\b", r"\d+", r"\d+\b", r"1\b2", r"\d(?=\d)\d", r"\d(?<=\d)",
         r"(?<=\d)\d", r"\d+(?!\d)", r"a?\ba", r"(?:\d|a)+", r"\d(?=\d\d)\d", r"[a-z]*\d"]
unsound, over = [], []
for B in HFOPS:
    emp = reads_outside(B, HFPOOL)
    cl = outward(B)
    print("HF2 %-20s classifier %-12s ; libpcre2 own-text vs in-subject: %s"
          % (B, "FILTER ERROR" if cl else "accepted", "reads outside at %r stretch [%d,%d)" % emp if emp else "never reads outside (%d texts, every stretch)" % len(HFPOOL)))
    if emp and not cl:
        unsound.append(B)
    if cl and not emp:
        over.append(B)
print("    SOUND (no accepted operand reads outside): %s ; conservative refusals (refused, never read outside on the pool): %s ; %s"
      % (not unsound, over or "none", check("HF2 reach classifier sound", not unsound)))
print("    r47's two witnesses `(?=\\d\\d\\d)\\d+` and `(?:\\d+\\b)[a-z]*` (the filled hole d := `/\\d+\\b/` in `/${d}[a-z]*/`): %s"
      % check("HF2 r47 witnesses refused", outward(r"(?=\d\d\d)\d+") and judge_filter(r"${d}[a-z]*", {"d": r"\d+\b"}) == "FILTER ERROR"))

# =====================================================================================================================
print("\n== PART REF: a reference uses the namespace of the rx it is written in (the last mention there); a name that rx does not define is a compile error")
def resolve_backref(parts, k):
    """parts: list of (rx_name, [('set', name) | ('ref', name)]) in sequence; resolve the k-th part's refs"""
    out = []
    for i, (nm_, items) in enumerate(parts):
        defined = set(n for t, n in items if t == "set")
        for t, n in items:
            if t == "ref":
                if n in defined:
                    out.append((nm_, n, "%s's own `%s`" % (nm_, n)))
                elif sab("s5") and any(n in set(m for t2, m in it2 if t2 == "set") for _, it2 in parts[:i]):
                    out.append((nm_, n, "the surroundings' `%s`" % n))
                else:
                    out.append((nm_, n, "COMPILE ERROR (`%s` not defined in %s)" % (n, nm_)))
    return out
CASES = [("B := `/(?<h>\\d)\\k<h>/` after A := `/(?<h>\\d)/`", [("A", [("set", "h")]), ("B", [("set", "h"), ("ref", "h")])], "B's own `h`"),
         ("B := `/\\k<h>/` after A", [("A", [("set", "h")]), ("B", [("ref", "h")])], "COMPILE ERROR (`h` not defined in B)"),
         ("B := `/\\k<h>(?<h>\\d)/` after A", [("A", [("set", "h")]), ("B", [("ref", "h"), ("set", "h")])], "B's own `h`")]
for desc, parts, want in CASES:
    got = resolve_backref(parts, 1)[-1][2]
    print("REF1 RULE-AS-CODE %-50s -> %-40s ; %s" % (desc, got, check("REF1 " + desc, got == want)))
# the run: B's own group, modelled by renaming the parts' groups apart before splicing (one model of the ruled answer)
own = P.Pcre(r"(?<h>\d)(?<h2>\d)\k<h2>")
print("REF2 `A SEQ B`, B's own group (renamed apart `(?<h>\\d)(?<h2>\\d)\\k<h2>`): %s ; %s"
      % (show(own, "733", "1733 737", "737 733 747"), check("REF2 shown 733 holds 737 fails", W(own, "733") is not None and W(own, "737") is None)))
wo = P.Pcre(r"(?J)(?P<h>\d)(?P<h>\d)(?P=h)")
print("     the written-out regex under PCRE's duplicate names `(?J)(?P<h>\\d)(?P<h>\\d)(?P=h)` (= `(?J)(?<h>\\d)(?<h>\\d)\\k<h>`): WHOLE `733` %s, `737` %s (the reverse, as shown) ; %s"
      % (fW(wo, "733"), fW(wo, "737"), check("REF2 written-out reverse", W(wo, "733") is None and W(wo, "737") is not None)))
fw = P.Pcre(r"(?<h>\d)\k<h2>(?<h2>\d)")
print("REF3 B := `/\\k<h>(?<h>\\d)/` after A, B's own h unset at its reference (renamed `(?<h>\\d)\\k<h2>(?<h2>\\d)`): matches on no text of `3779` length <= 4: %s ; with PCRE's MATCH_UNSET_BACKREF it would match `37`: %s"
      % (check("REF3 forward ref never matches", all(S(fw, s) is None for s in pool("37", 4))), fW(P.Pcre(r"(?<h>\d)\k<h2>(?<h2>\d)", opts=PCRE2_MATCH_UNSET_BACKREF), "37")))
print("   the manager's \"(its h, unset at that point on a first pass)\": SUPPORTED; what the reference then DOES (fail, as PCRE's default) is THE DRAFT'S READING (regex by default)")

print("REF4 a backreference INSIDE ONE literal with two groups of one name, `/(?<h>\\d);(?:(?<h>\\d)|x)\\k<h>/` (read \"as labels are\"): three readings")
bl = P.Pcre(r'(?<h1>\d);(?:(?<h2>\d)|x)(?(<h2>)\k<h2>|(?!))')
bc = P.Pcre(r'(?<h1>\d);(?:(?<h2>\d)|x)(?(<h2>)\k<h2>|\k<h1>)')
bj = P.Pcre(r'(?J)(?P<h>\d);(?:(?P<h>\d)|x)(?P=h)')
for nm_, rx in (("THE LABEL (the one rule: entering the alternation resets h)", bl), ("the last-SET group's capture", bc), ("PCRE `(?J)` (first set group)", bj)):
    print("     %-62s WHOLE `3;x3` %s, `3;77` %s, `3;73` %s ; SEARCHED `3;x3 3;77` %s" % (nm_, fW(rx, "3;x3"), fW(rx, "3;77"), fW(rx, "3;73"), fS(rx, "3;x3 3;77")))
POOLB = pool("37;x", 4)
for (n1, r1_), (n2, r2_) in (((("label", bl)), ("last set", bc)), (("label", bl), ("(?J)", bj)), (("last set", bc), ("(?J)", bj))):
    d, first = diff3(r1_, r2_, POOLB)
    print("     %s vs %s: %d / %d / %d of %d differ, first %s" % (n1, n2, d[0], d[1], d[2], len(POOLB), first))
check("REF4 three readings differ", W(bl, "3;x3") is None and W(bc, "3;x3") is not None and W(bj, "3;73") is not None and W(bl, "3;73") is None)

# =====================================================================================================================
print("\n== PART EX: the export rule (public unless `_`; a binding shows its own public labels and its public part labels)")
# a binding: name -> list of items: ('lit', [labels]) | ('part', partlabel or None, binding name)
B = {
    "year": [("lit", ["v"])],
    "month": [("lit", ["v"])],
    "date": [("part", "y", "year"), ("lit", []), ("part", "m", "month")],
    "pdate": [("part", "_y", "year"), ("lit", []), ("part", "m", "month")],
    "hdate": [("part", "_", "year"), ("lit", []), ("part", "m", "month")],
    "priv": [("lit", ["_t", "v"])],
    "outer": [("part", "d", "date"), ("lit", ["x"])],
}
def public(n):
    return sab("s6") or not n.startswith("_")
def exported(b):
    """what is visible OUTSIDE binding b: bare names = the public labels of its own literals; paths = its public part labels"""
    bare, paths = set(), set()
    for it in B[b]:
        if it[0] == "lit":
            bare |= set(n for n in it[1] if public(n))
        else:
            pl, sub = it[1], it[2]
            if pl is None or pl == "_" or not public(pl):
                continue
            sb, sp = exported(sub)
            paths |= set(pl + "." + n for n in sb) | set(pl + "." + p for p in sp)
    return bare, paths
def visible_inside(b):
    """inside binding b: every label of its own literals; through each part: its exported labels bare (last mention) and by path"""
    bare, paths = [], set()
    for it in B[b]:
        if it[0] == "lit":
            bare += it[1]
        else:
            pl, sub = it[1], it[2]
            if pl == "_":
                continue                                   # [_ = A]: A's labels invisible everywhere outside A
            sb, sp = exported(sub)
            bare += sorted(sb)
            if pl is not None:
                paths |= set(pl + "." + n for n in sb) | set(pl + "." + p for p in sp)
    return bare, paths
def ref(b, name, where):
    if where == "outside":
        bare, paths = exported(b)
        if "." in name:
            return "visible (path)" if name in paths else "ERROR (not visible)"
        return "visible" if name in bare else "ERROR (not visible)"
    bare, paths = visible_inside(b)
    if "." in name:
        return "visible (path)" if name in paths else "ERROR (not visible)"
    return "visible (last mention)" if name in bare else "ERROR (not visible)"
VT = [("date", "m.v", "outside", "visible (path)"), ("date", "y.v", "outside", "visible (path)"), ("date", "v", "outside", "ERROR (not visible)"),
      ("year", "v", "outside", "visible"), ("date", "v", "inside", "visible (last mention)"), ("date", "y.v", "inside", "visible (path)"),
      ("pdate", "_y.v", "inside", "visible (path)"), ("pdate", "_y.v", "outside", "ERROR (not visible)"), ("pdate", "m.v", "outside", "visible (path)"),
      ("hdate", "v", "inside", "visible (last mention)"), ("hdate", "_.v", "inside", "ERROR (not visible)"), ("hdate", "m.v", "outside", "visible (path)"),
      ("priv", "_t", "inside", "visible (last mention)"), ("priv", "_t", "outside", "ERROR (not visible)"), ("priv", "v", "outside", "visible"),
      ("outer", "d.m.v", "outside", "visible (path)"), ("outer", "m.v", "outside", "ERROR (not visible)"), ("outer", "x", "outside", "visible")]
for b, n, w, want in VT:
    got = ref(b, n, w)
    print("EX1 RULE-AS-CODE %-6s %-6s %-7s -> %-24s ; %s" % (b, n, w, got, check("EX1 %s %s %s" % (b, n, w), got == want)))
print("   bindings: year := /(?<v>\\d{4})/ ; month := /(?<v>\\d\\d)/ ; date := [y = year] SEQ \"-\" SEQ [m = month] ; pdate := [_y = year] SEQ .. ; hdate := [_ = year] SEQ .. [m = month] ;")
print("   priv := /(?<_t>\\d)(?<v>\\d)/ ; outer := [d = date] SEQ /(?<x>.)/  (hdate's inside `v` is month's: year's is closed by `[_ = ..]`)")
# the run: `year & (v: >= 2000)`, and `date & (m.v: <= 12)` by renaming the parts' labels apart (y.v -> y_v, m.v -> m_v)
yr = P.Pcre(r'(?<v>\d{4})(?C"t")', {"t": lambda c: int(c.get("v")) >= 2000})
print("EX2 `year & (v: >= 2000)`: %s ; %s" % (show(yr, "2025", "x1999 2001", "1999 2001 2025"), check("EX2 year works", W(yr, "2025") is not None and W(yr, "1999") is None)))
dt = P.Pcre(r'(?<y_v>\d{4})-(?<m_v>\d\d)(?C"t")', {"t": lambda c: int(c.get("m_v")) <= 12})
print("EX3 `date & (m.v: <= 12)` (paths as renamed groups): %s ; %s" % (show(dt, "2025-11", "2025-13 2025-12", "2025-13 2025-12 2026-01", ("y_v", "m_v")),
      check("EX3 date path", W(dt, "2025-11") is not None and W(dt, "2025-13") is None)))
print("   THE MANAGER'S READINGS: \"pass-through is answered by statement 3\" (outer: `d.m.v` by path, bare `m.v` not): RULE-AS-CODE, consistent; NOT RUNNABLE independently (visibility has no regex model)")

# =====================================================================================================================
print("\n== PART CS: condition-in-sequence (yes; `&` stays): the condition tested where it stands")
def lt5(c):
    h = c.get("h")
    return num(h) and int(h) < 5
if sab("s13"):
    cs_seq = P.Pcre(r'(?:(?<h>\d);)*(?C"t")', {"t": lt5})
else:
    cs_seq = P.Pcre(r'(?:(?<h>\d)(?C"t");)*', {"t": lt5})
cs_and = P.Pcre(r'(?:(?<h>\d);)*(?C"t")', {"t": lt5})
print("CS1 `([h = rx.digit] SEQ (h: <5) SEQ \";\")*` on `7;3;` WHOLE %s ; `([h = rx.digit] SEQ \";\")* & (h: <5)` WHOLE %s ; %s"
      % (fW(cs_seq, "7;3;", ("h",)), fW(cs_and, "7;3;", ("h",)), check("CS1 shown (fails / holds)", W(cs_seq, "7;3;") is None and W(cs_and, "7;3;") is not None)))
print("    the manager's hand-worked answer (shown): the sequenced form FAILS (each pass tested), the `&` form HOLDS (the last mention) REPRODUCED")
POOLS = pool("37;")
d, first = diff3(cs_seq, cs_and, POOLS, ("h",))
print("CS2 the two forms over %d texts (labels compared): %d / %d / %d differ, first %s" % (len(POOLS), d[0], d[1], d[2], first))
# CS3 (review r47 C3: rev 26's two arms were byte-identical patterns).  REBUILT: the `&` arm by the FILTER MODEL,
# built without the sequenced pattern: every path of the left operand at a start is enumerated in PCRE's order (a
# recording callout that always fails at the operand's end), each path's labels judged by the condition, the first
# path that holds (and, WHOLE, spans the text) is the answer; FIND-ALL is PCRE2's global loop over that matcher.
# The sequenced arm is libpcre2 with the condition a callout written last.  Drilled at one level and INSIDE A LOOP
# (the labels set in the loop's passes).  Sabotage s17: the filter model judges only the FIRST path.
class FilterAnd:
    def __init__(self, left, cond, keys):
        self.keys, self.cond = keys, cond
        self.rec = P.Pcre(left + r'(?C"rec")', {"rec": self._rec})
        self.paths = None
    def _rec(self, c):
        self.paths.append((c.start, c.pos, {k: c.get(k) for k in self.keys}))
        return False
    def match(self, s, pos, opts=0):
        anch = bool(opts & P.PCRE2_ANCHORED)
        endanch = bool(opts & P.PCRE2_ENDANCHORED)
        ne = bool(opts & NOTEMPTY_ATSTART)
        for st in ([pos] if anch else range(pos, len(s) + 1)):
            self.paths = []
            self.rec.match(s, st, P.PCRE2_ANCHORED)
            cands = self.paths[:1] if sab("s17") else self.paths
            for a_, b_, l in cands:
                if endanch and b_ != len(s):
                    continue
                if ne and a_ == b_ == pos:
                    continue
                if self.cond(l):
                    return (a_, b_, l)
        return None
def lt5l(l):
    return num(l.get("h")) and int(l.get("h")) < 5
CS3CASES = [("one level `[a = /\\d+/] SEQ [h = rx.digit]`", r'(?<a>\d+)(?<h>\d)', ("a", "h"), pool("375", 5)),
            ("inside a loop `([a = /\\d+/] SEQ [h = rx.digit] SEQ \";\")*`", r'(?:(?<a>\d+)(?<h>\d);)*', ("a", "h"), pool("37;", 6))]
for desc, left, keys, pl in CS3CASES:
    seq_ = P.Pcre(left + r'(?C"t")', {"t": lt5})
    fil = FilterAnd(left, lt5l, keys)
    d, first = diff3(seq_, fil, pl, keys)
    # the arm can move: the condition read NOT at the end of the left operand but before its last group
    print("CS3 %-62s condition written LAST in sequence vs `&` by the FILTER model, %d texts: %d / %d / %d differ%s ; %s"
          % (desc, len(pl), d[0], d[1], d[2], " (SABOTAGED s17: first path only), first %s" % (first,) if sab("s17") else "",
             check("CS3 last = & (" + desc[:20] + ")", d == [0, 0, 0])))
print("    witness length the drill reaches: `735` (one level: path a=73 h=5 fails, a=7 h=3 holds; the first-path model FAILS it)")

# quantified-condition: an error (RULED), covering the nine operators; a group with pattern text is not this case
QOPS = ["+", "+?", "++", "*", "*?", "*+", "?", "??", "?+"]
def quant_ok(operand_kind):
    if sab("s11"):
        return True
    if operand_kind == "group of conditions only":       # r47 B4: such a group IS a condition for this rule
        return sab("s22")
    return operand_kind != "cond"
for k, want in (("cond", False), ("group of conditions only", False), ("seqcond-in-group-with-pattern", True), ("pattern", True)):
    got = all(quant_ok(k) for _ in QOPS)
    print("CS4 RULE-AS-CODE a postfix quantifier (all nine) on a %-31s -> %s ; %s" % (k, "accepted" if got else "COMPILE ERROR", check("CS4 " + k, got == want)))
# the shown witness of quantified-condition (as regex, the alternative NOT taken): `?` never fails
qq = P.Pcre(r'(?<h>\d)(?:(?C"t"))?', {"t": lt5})
print("CS5 the witness he was shown, read as regex (NOT adopted): `[h = rx.digit] SEQ (h: <5)?` %s" % show(qq, "7", "73", "7 3", ("h",)))
check("CS5 shown regex reading", W(qq, "7") is not None and [(a, b) for a, b, _ in F(qq, "7 3")] == [(0, 1), (2, 3)])

# =====================================================================================================================
print("\n== PART LA: lookahead-labels (visible, as in PCRE)")
r = re.fullmatch(r"(?=\d*(?P<l>\d)\b)(?P<f>\d)\d*", "1234")
fa = [(m.start(), m.group("l"), m.group("f")) for m in re.finditer(r"(?=\d*(?P<l>\d)\b)(?P<f>\d)\d*", "1234 4321 77")]
print("LA1 python `re` (shown): whole `1234` l = `%s`, f = `%s` ; find-all `1234 4321 77` l/f %s ; %s"
      % (r["l"], r["f"], ["%s/%s" % (a, b) for _, a, b in fa], check("LA1 shown python", (r["l"], r["f"]) == ("4", "1") and [(a, b) for _, a, b in fa] == [("4", "1"), ("1", "4"), ("7", "7")])))
ng = re.fullmatch(r"(?!\d*(?P<l>x))(?P<f>\d)\d*", "1234")
print("    a negative lookahead leaves its group unset: l = %s ; %s" % (ng["l"], check("LA1 negative unset", ng["l"] is None)))
def l_gt_f(c):
    l, f = c.get("l"), c.get("f")
    if sab("s12"):
        l = None
    return num(l) and num(f) and int(l) > int(f)
la1 = P.Pcre(r'(?=\d*(?<l>\d)\b)(?<f>\d)\d*(?C"t")', {"t": l_gt_f})
print("LA2 `/(?=\\d*(?<l>\\d)\\b)(?<f>\\d)\\d*/ & (l: > f)` (the condition's effect, hand-worked in the record, RUN): %s ; %s"
      % (show(la1, "1234", "4321 1234", "1234 4321 77", ("l", "f")), check("LA2 visible", W(la1, "1234") is not None and [(a, b) for a, b, _ in F(la1, "1234 4321 77")] == [(0, 4)])))
lo = P.Pcre(r'(?=\d*(?<l>\d)\b)(?<f>\d)')
print("LA3 a label set in a lookahead may lie outside the matched text (for item 24): SEARCHED `1234` %s" % fS(lo, "1234", ("l", "f")))
lb = P.Pcre(r'(?<=(?<b>\d))x')
print("LA4 THE MANAGER'S READING (the same for a lookbehind): `(?<=(?<b>\\d))x` SEARCHED `a7x` %s ; SUPPORTED as regex behaviour ; %s"
      % (fS(lb, "a7x", ("b",)), check("LA4 lookbehind label set", S(lb, "a7x")[2]["b"] == "7")))

# =====================================================================================================================
print("\n== PART CX: complement-place (the error is at the USE; rx that can match, rx that can filter) and lone-complement-match")
# kinds: can_match, can_filter; programs: ('lit', text) | ('not', x) | ('and', [ops]) | ('seq', [ops]) | ('occ', x) | ('hole', x)
def can_filter(x):
    k = x[0]
    if k == "lit":
        return not outward(x[1])
    if k == "not":
        return can_filter(x[1])
    if k in ("and", "seq"):
        return all(can_filter(o) for o in x[1]) and (k == "and" or all(can_match(o) for o in x[1]))
    return False
def can_match(x):
    k = x[0]
    if k == "lit":
        return True
    if k == "not":
        return sab("s10")
    if k == "and":
        return all(can_filter(o) for o in x[1]) and any(can_match(o) for o in x[1])
    if k in ("seq",):
        return all(can_match(o) for o in x[1])
    if k in ("occ", "hole"):
        return can_match(x[1])
    return False
digits, seven, eight = ("lit", r"\d+"), ("lit", r"7\d*"), ("lit", r"8\d*")
not_seven = ("not", seven)
neither = ("and", [("not", seven), ("not", eight)])
# a USE that needs a match: the program itself, a sequence operand, an occurrences argument, a pattern hole
CT = [("not_seven := not seven (bound)", "bind", not_seven, "legal"),
      ("digits & not_seven", "program", ("and", [digits, not_seven]), "legal"),
      ("neither := not seven & not eight (bound)", "bind", neither, "legal"),
      ("not_seven run alone (whole or searched)", "program", not_seven, "ERROR at that use"),
      ("digits SEQ not_seven", "program", ("seq", [digits, not_seven]), "ERROR at that use"),
      ("occurrences(not_seven)", "program", ("occ", not_seven), "ERROR at that use"),
      ("/x${not_seven}y/ (THE MANAGER'S READING, agreed)", "program", ("seq", [("lit", "x"), ("hole", not_seven), ("lit", "y")]), "ERROR at that use"),
      ("anything & not_seven", "program", ("and", [("lit", r"[\s\S]*"), not_seven]), "legal"),
      ("`/\\b\\d+\\b/` as an `&` operand (match-only)", "program", ("and", [digits, ("lit", r"\b\d+\b")]), "ERROR at that use"),
      ("`/\\b\\d+\\b/` as a program (match-only)", "program", ("lit", r"\b\d+\b"), "legal")]
for desc, use, x, want in CT:
    got = "legal" if (use == "bind" or can_match(x)) else "ERROR at that use"
    print("CX1 RULE-AS-CODE %-50s -> %-18s ; %s" % (desc, got, check("CX1 " + desc, got == want)))
# the runs in the table he agreed to: digits & not_seven, whole `123` holds, `712` fails
def not7(c):
    return re.fullmatch(r"7\d*", c.stretch()) is None
dn = P.Pcre(r'\d+(?C"t")', {"t": not7})
print("CX2 `digits & not_seven` (shown): WHOLE `123` %s, `712` %s ; %s" % (fW(dn, "123"), fW(dn, "712"), check("CX2 shown", W(dn, "123") is not None and W(dn, "712") is None)))
# the manager's simulation of `any & not seven` (a SEARCH; his note, kept only for its last clause), run under PCRE2's
# global loop (R.1.2) with a callout as the filter
anyg = P.Pcre(r'.*(?C"t")', {"t": not7})
anyl = P.Pcre(r'.*?(?C"t")', {"t": not7})
print("CX3 the manager's simulation, RUN on libpcre2 with PCRE2's global loop: `any := /.*/`: FIND-ALL `712` %s ; `x712 55` %s"
      % (fF(anyg, "712"), fF(anyg, "x712 55")))
gl = [(a, b) for a, b, _ in F(anyg, "712")]
print("    the record: \"on `712` the hits are an empty match at 0, `12` at 1, an empty match at 3\" ; %s" % check("CX3 712 reproduced", gl == [(0, 0), (1, 3), (3, 3)]))
ll = F(anyl, "712")
print("    lazy `any := /.*?/`: FIND-ALL `712` %s ; the record: \"with a lazy any every hit is empty\" -> %s"
      % (fF(anyl, "712"), "REPRODUCED" if all(a == b for a, b, _ in ll) else "NOT REPRODUCED under PCRE2's global loop (the retry after an empty match takes a non-empty hit; the manager's script stepped one character)"))
# "as a whole value every spelling of anything agrees": `/.*/` without dotall vs `[\s\S]*` vs `.*?`, on texts with a newline
spell = [("/.*/", P.Pcre(r'.*(?C"t")', {"t": not7})), ("/.*?/", P.Pcre(r'.*?(?C"t")', {"t": not7})),
         ("/(?s).*/", P.Pcre(r'(?s).*(?C"t")', {"t": not7})), ("/[\\s\\S]*/", P.Pcre(r'[\s\S]*(?C"t")', {"t": not7}))]
POOLNL = pool("7a\n", 4)
base = [W(spell[3][1], s) is not None for s in POOLNL]
for nm_, rx in spell:
    nd = sum(1 for i, s in enumerate(POOLNL) if (W(rx, s) is not None) != base[i])
    print("CX4 `%s & not seven` as a WHOLE value vs `[\\s\\S]* & not seven`, %d texts over `7a\\n`: %d differ" % (nm_, len(POOLNL), nd))
nd_dot = sum(1 for i, s in enumerate(POOLNL) if (W(spell[0][1], s) is not None) != base[i])
print("    THE MANAGER'S CLAUSE \"as a whole value every spelling of anything agrees\": NOT SUPPORTED for `/.*/` without dot-all (%d texts with a newline differ); SUPPORTED for spellings that match a newline ; %s"
      % (nd_dot, check("CX4 dot without s differs", nd_dot > 0)))
print("    so `anything` must be defined to match newlines (THE MANAGER'S READING for the rx module: any text including newlines) for his whole-value point to hold")

# =====================================================================================================================
print("\n== PART VH: the value hole fleshed out (`/(?<y>\\d{4})-${$y + 1}/`; UNRULED)")
# THE CALLOUT MODEL: at the hole the value's text L is known (the label read where the hole is written); matching the
# literal L at the current place is modelled by a lazy capture `(?<v>[\s\S]*?)` and a callout that accepts only v == L:
# the lazy capture tries every length, and exactly one equals L, so the model matches L there and nowhere else.
def vh(pre, post, f, opts=0, keys=("y",)):
    return P.Pcre(pre + r'(?<v>[\s\S]*?)(?C"eq")' + post, {"eq": lambda c: (lambda L: L is not None and c.get("v") == L)(f(c))}, opts)
def plus1_canon(c):
    y = c.get("y")
    return None if y is None else str(int(y) + 1)
def plus1_width(c):
    y = c.get("y")
    return None if y is None else str(int(y) + 1).zfill(len(y))
# control: `${$y}` (the value itself) must equal the backreference `\k<y>`
cv = vh(r'(?<y>\d{1,2})-', r'', lambda c: c.get("y"))
cb = P.Pcre(r'(?<y>\d{1,2})-\k<y>')
POOLV = pool("12-", 5)
d, first = diff3(cv, cb, POOLV, ("y",))
print("VH0 CONTROL: the callout model of `${$y}` vs PCRE's `\\k<y>` on `(?<y>\\d{1,2})-..`: %d / %d / %d of %d differ ; %s"
      % (d[0], d[1], d[2], len(POOLV), check("VH0 model = backreference", d == [0, 0, 0])))
c1 = vh(r'(?<y>\d{4})-', r'', plus1_canon)
print("VH1 `/(?<y>\\d{4})-${$y + 1}/` (canonical numeral): %s" % show(c1, "2025-2026", "x2025-2026", "2025-2026 2030-2032 2030-2031", ("y",)))
print("    the hand-worked answer of the draft (HOLDS / `2025-2026`@1 / [`2025-2026`@0]) ; %s"
      % check("VH1 hand-worked", W(c1, "2025-2026") is not None and S(c1, "x2025-2026")[0] == 1 and [(a, b) for a, b, _ in F(c1, "2025-2026 2030-2032")] == [(0, 9)]))
c2 = vh(r'(?<y>\d{4})-', r'', plus1_width)
for t in ("0099-100", "0099-0100", "9999-10000", "0999-1000"):
    print("VH2 width: `%s` canonical %s ; width kept %s" % (t, fW(c1, t), fW(c2, t)))
check("VH2 width readings differ", (W(c1, "0099-100") is not None) and (W(c2, "0099-0100") is not None) and W(c1, "0099-0100") is None)
# literal text, never regex syntax: a value with `.` in it
def lit_or_rx(c):
    return c.get("y")
cl = vh(r'(?<y>[\d.]+)-', r'', lit_or_rx)
crx = P.Pcre(r'(?<y>[\d.]+)-(?<v>[\s\S]*?)(?C"eq")', {"eq": lambda c: re.fullmatch(re.escape(c.get("y")) if not sab("s9") else c.get("y").replace(".", "."), c.get("v")) is not None if False else (re.fullmatch(c.get("y"), c.get("v")) is not None)})
print("VH3 literal vs reinterpreted: `/(?<y>[\\d.]+)-${$y}/` on `1.5-1x5`: as literal text %s ; as regex syntax %s ; %s"
      % (fW(cl if not sab("s9") else crx, "1.5-1x5"), fW(crx, "1.5-1x5"), check("VH3 literal text", W(cl if not sab("s9") else crx, "1.5-1x5") is None and W(crx, "1.5-1x5") is not None)))
# an unset label: the year optional
cu = vh(r'(?:(?<y>\d{4}))?-', r'', plus1_canon)
cu_e = P.Pcre(r'(?:(?<y>\d{4}))?-(?<v>[\s\S]*?)(?C"eq")', {"eq": lambda c: c.get("v") == ("" if c.get("y") is None else str(int(c.get("y")) + 1))})
print("VH4 unset label `/(?<y>\\d{4})?-${$y + 1}/`: FAIL reading (as PCRE's unset backreference) WHOLE `-` %s, `2025-2026` %s ; EMPTY reading (as MATCH_UNSET_BACKREF) WHOLE `-` %s"
      % (fW(cu, "-"), fW(cu, "2025-2026"), fW(cu_e, "-")))
# inside a loop: the value read where it is written (after its group: the current pass)
cloop = P.Pcre(r'(?:(?<y>\d{4})-(?<v>[\s\S]*?)(?C"eq");)*', {"eq": lambda c: c.get("v") == str(int(c.get("y")) + 1)})
print("VH5 in a loop `/(?:(?<y>\\d{4})-${$y + 1};)*/`: %s" % show(cloop, "2025-2026;2030-2031;", "2025-2026;2030-2032;", "2025-2026;2030-2032;", ("y",)))
check("VH5 loop per pass", W(cloop, "2025-2026;2030-2031;") is not None and W(cloop, "2025-2026;2030-2032;") is None)
# inside a hit-list argument, written BEFORE its group: hit-carry, the previous hit's value; unset on the first hit
cprev = P.Pcre(r'\A(?:[\s\S]*?(?:(?<v>[\s\S]*?)(?C"eq")-(?<y>\d{4}))){2,}[\s\S]*\z',
               {"eq": lambda c: c.get("v") == ("" if c.get("y") is None else str(int(c.get("y")) + 1))})
print("VH6 in an `occurrences` argument BEFORE its group `/${$y + 1}-(?<y>\\d{4})/`, min = 2, the unset value read as EMPTY: WHOLE `-2025 2026-2030` %s ; `-2025 2027-2030` %s"
      % (fW(cprev, "-2025 2026-2030", ("y",)), fW(cprev, "-2025 2027-2030", ("y",))))
check("VH6 hit-carry value", W(cprev, "-2025 2026-2030") is not None and W(cprev, "-2025 2027-2030") is None)

# =====================================================================================================================
print("\n== PART RS: the two questions held back (nested-complement; group-truth / pass-table), re-stated under hit-carry")
# nested-complement: `t2 & contains(t2 & !q)`: a `contains` argument is a hit-list argument; a condition inside it
# written before its group would now carry; with `!q` (a complement, a filter) nothing reads a label before its group,
# so hit-carry does not move it.  Run: contains(/(?<h>\d)/ & !/7/) vs the same with h read carried (no reader): equal.
# nested-complement asked whether a `contains` argument FILTERS PATHS like a program (re-entered by its own condition,
# the one-pattern model) or judges the plain search's committed hits.  hit-carry RULED on the premise "occurrences is a
# simple regex rewrite ... what the user provides gets inserted into a template hole like usual": the argument is part
# of ONE pattern, so a complement inside it rejects a path and the loop tries the next.  Run: contains(/\d+/ & !/7\d*/)
# as the one-pattern model vs the committed reading (the plain find-all's hits, then judged).
nc1 = P.Pcre(r'\A[\s\S]*?(?<hit>\d+)(?C"t")[\s\S]*\z', {"t": lambda c: re.fullmatch(r'7\d*', c.get("hit")) is None})
def committed(s):
    return any(re.fullmatch(r'7\d*', m.group()) is None for m in re.finditer(r'\d+', s))
POOLC = pool("17 ", 5)
nd = sum(1 for s in POOLC if (W(nc1, s) is not None) != committed(s))
first = next((s for s in POOLC if (W(nc1, s) is not None) != committed(s)), None)
print("RS1 nested-complement: `contains(/\\d+/ & !/7\\d*/)` WHOLE, the one-pattern model (libpcre2) vs the committed hits (python `re` find-all, then judged): %d of %d texts differ, first `%s` (one-pattern %s, committed %s)"
      % (nd, len(POOLC), first, "HOLDS" if W(nc1, first) else "FAILS", "HOLDS" if committed(first) else "FAILS"))
print("    hit-carry's premise (a rewrite into a template hole) ENTAILS the one-pattern answer: the question is ENTAILED, not open ; %s" % check("RS1 readings differ", nd > 0))
# group-truth / pass-table: `some((h: <5))` over a loop reads each pass's own label; a condition inside the loop body
# before its group reads the previous pass (pass-start-read); hit-carry extends that to hit lists.  The pass forms are
# requests over the finished table, not conditions inside a pass: run `REP & some((h: <5))` vs the per-pass own reading.
REP = r'(?:(?<h>\d)?;)*'
def some_own(s):
    m = re.fullmatch(r'(?:(\d)?;)*', s)
    if m is None:
        return None
    vals = [g for g in re.findall(r'(\d)?;', s)]
    return any(v != "" and int(v) < 5 for v in vals)
print("RS2 group-truth / pass-table: the pass forms read each pass's OWN labels after the loop (some-own); hit-carry concerns a condition INSIDE a pass before its group, which the pass forms are not: the 11-18 rulings do NOT entail an answer to whether `occurs.none(NOT c)` and `NOT some(c)` should agree; it stays asked (re-stated in §R.8; its counts are rev 24.x's E12, NOT re-run here)")

# =====================================================================================================================
print("\n== PART OQ: the new owner questions' witnesses (other-holes, zero-in-sequence)")
POOLC2 = pool("abxyz-", 3)
def d1(a, b):
    ra, rb = re.compile(a), re.compile(b)
    out = []
    for f in (lambda r, t: r.fullmatch(t) is not None, lambda r, t: (lambda m: m and m.span())(r.search(t)), lambda r, t: [m.span() for m in r.finditer(t)]):
        out.append(sum(1 for t in POOLC2 if f(ra, t) != f(rb, t)))
    return out
print("OQ1 other-holes, a class MEMBER `/[${c}x]/`, c := [a, b]: more characters `[abx]` vs one copy per member `(?:[ax]|[bx])`: %s of %d differ (whole / searched / find-all, python `re`)" % (d1(r"[abx]", r"(?:[ax]|[bx])"), len(POOLC2)))
print("OQ2 other-holes, a RANGE END `/[${lo}-z]/`, lo := [a, x]: one copy per member `(?:[a-z]|[x-z])` vs the members as more characters `[ax-z]`: %s of %d differ" % (d1(r"(?:[a-z]|[x-z])", r"[ax-z]"), len(POOLC2)))
check("OQ1 member readings agree", d1(r"[abx]", r"(?:[ax]|[bx])") == [0, 0, 0])
check("OQ2 range readings differ", d1(r"(?:[a-z]|[x-z])", r"[ax-z]") != [0, 0, 0])
zs = P.Pcre(r'(?<h>\d)(?C"t")\d', {"t": lambda c: c.stretch() == "7"})
print("OQ3 zero-in-sequence `[h = rx.digit] SEQ (0: \"7\") SEQ rx.digit`, `0` read as the match SO FAR (a callout's start to here): %s ; the other reading (the entire match, unknown at that point) is a compile error"
      % show(zs, "73", "373", "73 77 37"))
check("OQ3 so-far reading runs", W(zs, "73") is not None and W(zs, "37") is None)

# =====================================================================================================================
print("\n== PART R47: review r47's answer-level and design-level witnesses, re-run (A1-A6, B1-B6; A2 is NZ above)")
# A1: the nullable argument under the loop rewrite.  The trace: a callout after the hit group records every visit; the
# rewrite's tail `[\s\S]*\z` always succeeds, so the first path is the answer and no visit is backtracked.
def nul_trace(s, mn):
    TR = []
    q = "*" if mn == 0 else "{%d,}" % mn
    rx = P.Pcre(r'\A(?:[\s\S]*?(?<hit>\d*)(?C"r"))' + q + r'[\s\S]*\z', {"r": lambda c: TR.append(c.span("hit")) or True})
    return TR if W(rx, s) is not None else None
def nul_verified(s, mn):
    """r47 V1's sentence, computed from python `re` (no loop): the plain search's hits up to AND INCLUDING the first
    empty hit; the first `min` always taken (padded by empty hits where the list stops short)"""
    out = []
    for m in re.finditer(r'\d*', s):
        out.append(m.span())
        if m.start() == m.end():
            break
    while len(out) < mn:
        out.append((out[-1][1], out[-1][1]))
    return out
def nul_r26(s, mn):
    """rev 26's sentence: at most one hit, the first, possibly empty"""
    return [next(re.finditer(r'\d*', s)).span()]
nul_model = nul_r26 if sab("s14") else nul_verified
NULPOOL = pool("1a", 5)                                        # 63 texts; the witness needs a non-empty FIRST hit (`1a`, length 2)
for mn in (0, 1, 2, 3):
    nd_v = sum(1 for t in NULPOOL if nul_trace(t, mn) != nul_model(t, mn))
    nd_26 = sum(1 for t in NULPOOL if nul_trace(t, mn) != nul_r26(t, mn))
    print("A1 `occurrences(/\\d*/%s)` the loop's hits vs %s: %d of %d differ ; vs rev 26's \"at most one hit, the first\": %d differ"
          % ("" if mn == 0 else ", min = %d" % mn, "rev 26 (SABOTAGED s14)" if sab("s14") else "r47's verified sentence", nd_v, len(NULPOOL), nd_26))
    check("A1 verified sentence = loop, min %d" % mn, nd_v == 0)
for t, mn in (("1a", 0), ("12a3", 0), ("a1b", 0), ("", 2), ("ab", 3)):
    print("A1 witness `%s`%s: the loop's hits %s" % (t, "" if mn == 0 else " min = %d" % mn, ["`%s`@%d" % (t[a_:b_], a_) for a_, b_ in nul_trace(t, mn)]))
print("    rev 26's witness `a1b` has an EMPTY FIRST hit, so it cannot tell the sentences apart; `1a` and `12a3` can ; %s"
      % check("A1 witnesses", nul_trace("1a", 0) == [(0, 1), (1, 1)] and nul_trace("12a3", 0) == [(0, 2), (2, 2)] and nul_trace("", 2) == [(0, 0), (0, 0)]))

# the one label rule as a MODEL (r47 V4, V6, V13's construction): an empty marker group `(?<ps>)` at the start of
# every pass of the outermost loop; a label counts only if its group's span starts at or after the marker.
# Sabotage s24 removes the rule (the label = PCRE's capture), so every witness below must stop differing.
def label_of(c, g):
    sp, ps = c.span(g), c.span("ps")
    if sab("s24"):
        return c.get(g)
    return c.get(g) if (sp is not None and ps is not None and sp[0] >= ps[0]) else None
def lt5v(v):
    return num(v) and int(v) < 5
# A3 number-in-loop: `/(?:(\d)?;)*/ & (1: <5)` (group 1 named g for the wrapper)
a3cap = P.Pcre(r'(?:(?<g>\d)?;)*(?C"t")', {"t": lambda c: lt5v(c.get("g"))})
a3lab = P.Pcre(r'(?:(?<ps>)(?<g>\d)?;)*(?C"t")', {"t": lambda c: lt5v(label_of(c, "g"))})
a3py = sum(1 for t in POOL3 if (W(a3cap, t) is not None) != (lambda m: m is not None and lt5v(m.group(1)))(re.fullmatch(r'(?:(\d)?;)*', t)))
POOLA3 = pool("37;", 5)
d, first = diff3(a3cap, a3lab, POOLA3)
print("A3 number-in-loop `/(?:(\\d)?;)*/ & (1: <5)`: regex's capture (vs python `re` group(1), WHOLE: %d differ) vs the label (one rule), %d texts: %d / %d / %d differ, first %s ; WHOLE `3;;` capture %s, label %s ; %s"
      % (a3py, len(POOLA3), d[0], d[1], d[2], first, fW(a3cap, "3;;"), fW(a3lab, "3;;"), check("A3 number-in-loop readings part", a3py == 0 and d[0] > 0)))
print("    SEARCHED `3;;` capture %s, label %s ; FIND-ALL `3;; 7;3;` capture %s, label %s" % (fS(a3cap, "3;;"), fS(a3lab, "3;;"), fF(a3cap, "3;; 7;3;"), fF(a3lab, "3;; 7;3;")))
# A4 backref-label: one name, plain PCRE patterns; the label model replaces `\k<h>` by a lazy capture + equality callout
VQ = r'(?<v>[\s\S]*?)(?C"eq")'
def eqlab(c):
    L = label_of(c, "h")
    return L is not None and c.get("v") == L
a4p1 = P.Pcre(r'(?:(?<h>\d)?-\k<h>;)*')
a4l1 = P.Pcre(r'(?:(?<ps>)(?<h>\d)?-' + VQ + ';)*', {"eq": eqlab})
a4p2 = P.Pcre(r'(?:(?:(?<h>\d);)*,)*=\k<h>')
a4l2 = P.Pcre(r'(?:(?<ps>)(?:(?<h>\d);)*,)*=' + VQ, {"eq": eqlab})
a4pc = P.Pcre(r'(?:(?<h>\d)-\k<h>;)*')
a4lc = P.Pcre(r'(?:(?<ps>)(?<h>\d)-' + VQ + ';)*', {"eq": eqlab})
dc, _ = diff3(a4lc, a4pc, pool("37-;", 5))
d1_, f1_ = diff3(a4l1, a4p1, pool("37-;", 7))
d2_, f2_ = diff3(a4l2, a4p2, pool("3;,=", 6))
print("A4 backref-label CONTROL (no optional, one depth) `/(?:(?<h>\\d)-\\k<h>;)*/`: label model vs `\\k` %d / %d / %d of %d" % (dc[0], dc[1], dc[2], len(pool("37-;", 5))))
print("A4 witness 1 `/(?:(?<h>\\d)?-\\k<h>;)*/` (an optional in a loop), %d texts over `37-;` length <= 7: %d / %d / %d differ, first %s ; WHOLE `3-3;-3;` PCRE %s, label %s"
      % (len(pool("37-;", 7)), d1_[0], d1_[1], d1_[2], f1_, fW(a4p1, "3-3;-3;", ("h",)), fW(a4l1, "3-3;-3;")))
print("    SEARCHED `3-3;-3;` PCRE %s, label %s ; FIND-ALL `3-3;-3; 7-7;` PCRE %s, label %s" % (fS(a4p1, "3-3;-3;"), fS(a4l1, "3-3;-3;"), fF(a4p1, "3-3;-3; 7-7;"), fF(a4l1, "3-3;-3; 7-7;")))
print("A4 witness 2 `/(?:(?:(?<h>\\d);)*,)*=\\k<h>/` (two loops deep), %d texts over `3;,=` length <= 6: %d / %d / %d differ, first %s ; WHOLE `3;,,=3` PCRE %s, label %s"
      % (len(pool("3;,=", 6)), d2_[0], d2_[1], d2_[2], f2_, fW(a4p2, "3;,,=3"), fW(a4l2, "3;,,=3")))
print("    SEARCHED `3;,,=3` PCRE %s, label %s ; FIND-ALL `3;,,=3 3;,=3` PCRE %s, label %s" % (fS(a4p2, "3;,,=3"), fS(a4l2, "3;,,=3"), fF(a4p2, "3;,,=3 3;,=3"), fF(a4l2, "3;,,=3 3;,=3")))
print("    both are PLAIN PCRE patterns: reading `\\k` \"as labels are\" changes their answers ; %s"
      % check("A4 backref one name parts", dc == [0, 0, 0] and d1_[0] > 0 and d2_[0] > 0))
# A5 hit-carry-depth: `(occurrences(/${c}(?<h>\d)/, min = 1) SEQ ",")*`, c := NOT (h: >= 5) before the group
def c_cap(c):
    return not (num(c.get("h")) and int(c.get("h")) >= 5)
def c_one(c):
    h = label_of(c, "h")
    return not (num(h) and int(h) >= 5)
A5POOL = pool("37x,", 6)                                       # 5,461 texts; the witness `7,3,` has length 4
for gap, tail in ((r'[^,\d]*?', r'[^,\d]*'), (r'[^,]*?', r'[^,]*')):
    rw = P.Pcre(r'(?:(?:' + gap + r'(?:(?C"c")(?<h>\d))){1,}' + tail + r',)*', {"c": c_cap})
    one = P.Pcre(r'(?:(?<ps>)(?:' + gap + r'(?:(?C"c")(?<h>\d))){1,}' + tail + r',)*', {"c": c_one})
    d, first = diff3(rw, one, A5POOL, ("h",))
    rw1 = P.Pcre(r'(?:' + gap + r'(?:(?C"c")(?<h>\d))){1,}' + tail, {"c": c_cap})
    one1 = P.Pcre(r'(?<ps>)(?:' + gap + r'(?:(?C"c")(?<h>\d))){1,}' + tail, {"c": c_one})
    dd1, _ = diff3(rw1, one1, pool("37x", 5), ("h",))
    print("A5 hit-carry-depth, gaps `%s`: the rewrite (h carried, PCRE's capture) vs the one rule (reset per outer pass), %d texts: %d / %d / %d differ, first %s ; CONTROL at one depth (`37x` <= 5): %d / %d / %d"
          % (gap, len(A5POOL), d[0], d[1], d[2], first, dd1[0], dd1[1], dd1[2]))
    if gap == r'[^,\d]*?':
        print("    WHOLE `7,3,` rewrite %s, one rule %s ; SEARCHED `7,3,` rewrite %s, one rule %s ; FIND-ALL `7,3, 3,7,` rewrite %s, one rule %s"
              % (fW(rw, "7,3,", ("h",)), fW(one, "7,3,", ("h",)), fS(rw, "7,3,"), fS(one, "7,3,"), fF(rw, "7,3, 3,7,"), fF(one, "7,3, 3,7,")))
        check("A5 two depths part, one depth agrees", d[0] > 0 and dd1 == [0, 0, 0])
# A6: the program `anything & not_seven` (r47 V7: not_seven = "not exactly `7`")
any_arm = r'\d+' if sab("s27") else r'[\s\S]*'
a6 = P.Pcre(any_arm + r'(?C"t")', {"t": lambda c: re.fullmatch(r'7', c.stretch()) is None})
a6d = P.Pcre(r'\d+(?C"t")', {"t": lambda c: re.fullmatch(r'7', c.stretch()) is None})
A6POOL = pool("7a\n", 5)
hw = sum(W(a6, t) is not None for t in A6POOL); hs = sum(S(a6, t) is not None for t in A6POOL); hf = sum(len(F(a6, t)) > 0 for t in A6POOL)
pyw = sum((W(a6, t) is not None) != (t != "7") for t in A6POOL)
print("A6 `anything & not_seven`%s, %d texts over `7a\\n` length <= 5: WHOLE holds on %d (vs python `text != \"7\"`: %d differ) ; SEARCHED holds on %d ; FIND-ALL non-empty on %d"
      % (" (SABOTAGED s27: anything := /\\d+/)" if sab("s27") else "", len(A6POOL), hw, pyw, hs, hf))
print("    `7`: %s ; SEARCHED is vacuous (greedy `anything` backs off to the empty stretch) ; %s" % (show(a6, "7", "7", "7 77"), check("A6 searched vacuous", hs == len(A6POOL) and hf == len(A6POOL) and hw == len(A6POOL) - 1)))
print("    the searched advice `digits & not_seven` (a non-nullable positive operand): WHOLE holds on %d, SEARCHED on %d, FIND-ALL non-empty on %d ; %s"
      % (sum(W(a6d, t) is not None for t in A6POOL), sum(S(a6d, t) is not None for t in A6POOL), sum(len(F(a6d, t)) > 0 for t in A6POOL), show(a6d, "7", "a7 77", "7 12 77")))
# B1: product order for NON-ADJACENT count holes
combos = list(itertools.product([1, 2], [1, 2]))
b1cop = P.Pcre("(?|" + "|".join(r"\d{%d}(?<m>\d*?)\d{%d}" % t for t in combos) + ")")
b1seq = P.Pcre(r"(?:\d{1}|\d{2})(?<m>\d*?)(?:\d{1}|\d{2})")
b1arm = b1seq if sab("s25") else b1cop
d, first = diff3(b1arm, b1seq, POOLD, ("m",))
b1py = re.fullmatch("|".join(r"\d{%d}(\d*?)\d{%d}" % t for t in combos), "111")
print("B1 `/\\d{${a}}(?<m>\\d*?)\\d{${b}}/`, a, b := [1, 2]: the copies (first slowest) vs a sequence of per-hole alternations, %d texts: %d / %d / %d differ, first %s ; WHOLE `111` copies %s, sequence %s (python `re` copies m = `%s`)"
      % (len(POOLD), d[0], d[1], d[2], first, fW(b1arm, "111", ("m",)), fW(b1seq, "111", ("m",)), [g for g in b1py.groups() if g is not None][0]))
b1g = diff3(P.Pcre("(?|" + "|".join(r"\d{%d}(?<m>\d*)\d{%d}" % t for t in combos) + ")"), P.Pcre(r"(?:\d{1}|\d{2})(?<m>\d*)(?:\d{1}|\d{2})"), POOLD, ("m",))[0]
print("    a greedy middle: %d / %d / %d ; adjacent holes (P3): 0 / 0 / 0 ; %s" % (b1g[0], b1g[1], b1g[2], check("B1 non-adjacent holes part", d[0] > 0)))
# B2: one array, two mentions: independent per mention
nB = [2, 5]
def mentions(xs, f):
    return [f(a, a) for a in xs] if sab("s28") else [f(a, b) for a in xs for b in xs]
nmn = mentions(nB, lambda a, b: a - b)
pairs = mentions(nB, lambda a, b: (a, b + 1))
def compiles(pat):
    try:
        P.Pcre(pat)
        return True
    except Exception:
        return False
legal = [t for t in pairs if compiles(r"\d{%d,%d}" % t)]
b2 = P.Pcre("(?|" + "|".join(r"\d{%d,%d}" % t for t in legal) + ")")
print("B2 n := [2, 5]: `n - n` = %s ; `repeat(digit, n, n + 1)` copies %s (the copy (5,3) removed: libpcre2 refuses `\\d{5,3}`) ; WHOLE `1234` %s (only through the cross copy (2,6)) ; %s"
      % (nmn, b2.pattern, fW(b2, "1234"), check("B2 per mention", nmn == [0, -3, 3, 0] and W(b2, "1234") is not None)))
# B4: a group holding ONLY conditions, quantified, read as regex (the meaning the punt keeps out)
for pat, desc in ((r'(?<h>\d)(?:(?C"t"))?', "`[h = rx.digit] SEQ ((h: <5))?`"), (r'(?<h>\d)(?:(?C"t")(?C"t"))*', "`[h = rx.digit] SEQ ((h: <5) SEQ (h: <5))*`"),
                  (r'(?<h>\d)(?C"t")', "`[h = rx.digit] SEQ (h: <5)` (unquantified)")):
    rx = P.Pcre(pat, {"t": lt5})
    print("B4 read as regex %-48s WHOLE `7` %s, `3` %s" % (desc, fW(rx, "7"), fW(rx, "3")))
check("B4 regex reading vanishes", W(P.Pcre(r'(?<h>\d)(?:(?C"t"))?', {"t": lt5}), "7") is not None)
# B5: the value hole under `(?i)` and with an optional label in a loop
def ceq(c):
    y, v = c.get("y"), c.get("v")
    return y is not None and (v == y if sab("s23") else v.casefold() == y.casefold())
b5k = P.Pcre(r'(?i)(?<y>[a-b])-\k<y>')
b5x = P.Pcre(r'(?i)(?<y>[a-b])-(?<v>[\s\S]*?)(?C"eq")', {"eq": lambda c: c.get("y") is not None and c.get("v") == c.get("y")})
b5c = P.Pcre(r'(?i)(?<y>[a-b])-(?<v>[\s\S]*?)(?C"eq")', {"eq": ceq})
B5POOL = pool("aAbB-", 5)
dx, fx = diff3(b5x, b5k, B5POOL, ("y",))
dcf, _ = diff3(b5c, b5k, B5POOL, ("y",))
print("B5(b) `(?i)` `/(?<y>[a-b])-${$y}/`, %d texts over `aAbB-` length <= 5: the exact-equality model (rev 26's VH) vs `\\k<y>`: %d / %d / %d differ, first %s ; a CASELESS-equality model%s vs `\\k<y>`: %d / %d / %d ; %s"
      % (len(B5POOL), dx[0], dx[1], dx[2], fx, " (SABOTAGED s23: exact)" if sab("s23") else "", dcf[0], dcf[1], dcf[2], check("B5 caseless control", dx[0] > 0 and dcf == [0, 0, 0])))
print("    WHOLE `a-A`: `\\k` %s, exact model %s" % (fW(b5k, "a-A"), fW(b5x, "a-A")))
b5pk = P.Pcre(r'(?:(?<y>\d)?-\k<y>;)*')
b5pm = P.Pcre(r'(?:(?<y>\d)?-(?<v>[\s\S]*?)(?C"eq");)*', {"eq": lambda c: c.get("y") is not None and c.get("v") == c.get("y")})
dpk, _ = diff3(b5pm, b5pk, pool("37-;", 7))
print("B5(a) an optional label in a loop `/(?:(?<y>\\d)?-${$y};)*/`: the callout model (PCRE's capture) vs `\\k<y>`: %d / %d / %d of %d (the anchor \"the backreference's own behaviour\") ; the label (one rule, pass-start-read) parts from both: A4 witness 1, WHOLE `3-3;-3;` ; %s"
      % (dpk[0], dpk[1], dpk[2], len(pool("37-;", 7)), check("B5 loop anchors part", dpk == [0, 0, 0] and d1_[0] > 0)))
# B6: a class MEMBER hole once the literal has other parts
more_ = P.Pcre(r'(?<g>\w*)[xy]')
cop_ = P.Pcre(r'(?<g>\w*)[xy]') if sab("s26") else P.Pcre(r'(?|(?<g>\w*)x|(?<g>\w*)y)')
B6POOL = pool("xya", 4)
d, first = diff3(more_, cop_, B6POOL, ("g",))
print("B6 `/(\\w*)[${c}]/`, c := [x, y]: more characters `(\\w*)[xy]` vs one copy per member, %d texts over `xya` length <= 4: %d / %d / %d differ, first %s ; SEARCHED `xy` more %s, copies %s ; %s"
      % (len(B6POOL), d[0], d[1], d[2], first, fS(more_, "xy", ("g",)), fS(cop_, "xy", ("g",)), check("B6 member readings part with other parts", d[1] > 0)))

# =====================================================================================================================
print("\n== PART COND: the conditional (RULED: the guarded form; when-default; when-test; when-peek), every mode")
# A := `\d`, B := `\d\d`, C := `\w` (the when-test entry's table).  Regex arms (the guarded form written in regex):
#   peek `when(peek(A), B, else = C)` = `(?=A)B|(?!A)C` ; consumed `when(A, B, else = C)` = `AB|(?!A)C` (+ a warning) ;
#   no else: `(?=A)B|(?!A)` and `AB|(?!A)`.  CONTROLS: PCRE2's own conditional group `(?(?=A)B|C)` (peek forms) and
# a direct Python semantic function (if the test holds at the start: the then-branch from there (peek) or after A
# (consumed), else the else-branch; no fall-through), built from `re.fullmatch` / `re.match` on the pieces only.
CA, CB, CC = r'\d', r'\d\d', r'\w'
class SemCond:
    """if-then-else at a start position; first path in PCRE order (then-branch paths, else-branch paths)"""
    def __init__(self, A, B, C, consumed):
        self.A, self.B, self.C, self.cons = A, B, C, consumed
    def ends(self, s, st, piece):
        if piece is None:
            return [st]                                        # a missing branch matches nothing (the empty match)
        # PCRE order for these fixed / greedy pieces: longest first
        return [e for e in range(len(s), st - 1, -1) if re.fullmatch(piece, s[st:e])]
    def at(self, s, st):
        test = re.match(self.A, s[st:]) is not None           # the test holds at st (a peek)
        if test:
            if not self.cons:
                return self.ends(s, st, self.B)
            out = []
            for i in self.ends(s, st, self.A):
                out += self.ends(s, i, self.B)
            return out
        return self.ends(s, st, self.C)
    def match(self, s, pos, opts=0):
        anch = bool(opts & P.PCRE2_ANCHORED); endanch = bool(opts & P.PCRE2_ENDANCHORED); ne = bool(opts & NOTEMPTY_ATSTART)
        for st in ([pos] if anch else range(pos, len(s) + 1)):
            for e in self.at(s, st):
                if endanch and e != len(s):
                    continue
                if ne and st == e == pos:
                    continue
                return (st, e, {})
        return None
def guarded(A, B, C, consumed):
    if sab("s20") and consumed:
        consumed = False                                       # sabotage: the bare pattern peeked
    then = (A + B) if consumed else ("(?=" + A + ")" + B)
    if sab("s19"):
        return P.Pcre(then + "|" + (C if C is not None else ""))   # sabotage: no guard on the else branch
    if C is None and sab("s21"):
        return P.Pcre(then)                                    # sabotage: a missing else fails
    return P.Pcre(then + "|(?!" + A + ")" + (C if C is not None else ""))
CPOOL = pool("12x", 5)                                         # 364 texts; the witnesses need length 1-3
FORMS = [("when(peek(A), B, else = C)", False, CC, r'(?(?=\d)\d\d|\w)'),
         ("when(peek(A), B)            (no else)", False, None, r'(?(?=\d)\d\d|)'),
         ("when(A, B, else = C)        (A bare: consumed, warns)", True, CC, None),
         ("when(A, B)                  (A bare, no else)", True, None, None)]
for desc, cons, C, native in FORMS:
    g = guarded(CA, CB, C, cons)
    sem = SemCond(CA, CB, C, cons)
    d, first = diff3(g, sem, CPOOL)
    line = "COND %-52s regex `%s`: vs the semantic function %d / %d / %d of %d" % (desc, g.pattern, d[0], d[1], d[2], len(CPOOL))
    ok = d == [0, 0, 0]
    if native:
        dn, _ = diff3(g, P.Pcre(native), CPOOL)
        line += " ; vs PCRE2's `%s` %d / %d / %d" % (native, dn[0], dn[1], dn[2])
        ok = ok and dn == [0, 0, 0]
    print(line + " ; " + check("COND " + desc[:30], ok))
    print("     %s" % show(g, "12", "x123", "12 x 123 1x 7"))
# the when-test entry's table (shown to him, python `re`), REPRODUCED, and on libpcre2
pk, cs = r'(?=\d)\d\d|(?!\d)\w', r'\d\d\d|(?!\d)\w'
tab = [(t, re.fullmatch(pk, t) is not None, re.fullmatch(cs, t) is not None) for t in ("12", "123", "x", "1")]
print("COND the when-test table (python `re`, whole value): %s" % " ; ".join("`%s` peek %s, consumed %s" % (t, "holds" if a else "fails", "holds" if b else "fails") for t, a, b in tab))
shown = [("12", True, False), ("123", False, True), ("x", True, True), ("1", False, False)]
pcre_tab = [(t, W(P.Pcre(pk), t) is not None, W(P.Pcre(cs), t) is not None) for t in ("12", "123", "x", "1")]
print("     the record's table: `12` holds/fails, `123` fails/holds, `x` holds/holds, `1` fails/fails: %s ; libpcre2 the same: %s"
      % (check("COND when-test table reproduced", tab == shown), check("COND when-test table libpcre2", pcre_tab == shown)))
r = re.fullmatch(r'(?=(?P<d>\d))\d\d', "37")
print("COND THE MANAGER'S READING (when-test): a label set by a peeked A is readable in B: python `(?=(?<d>\\d))\\d\\d` on `37` d = `%s` ; libpcre2 %s ; %s"
      % (r["d"], fW(P.Pcre(r'(?=(?<d>\d))\d\d'), "37", ("d",)), check("COND peek label", r["d"] == "3")))
el = P.Pcre(r'(?=(?<d>\d))\d\d|(?!(?<e>\d))\w')
print("     in the else branch A's labels are unset (a negative peek sets nothing): `x` %s" % fW(el, "x", ("d", "e")))
# the question of the afternoon: A ? B : C vs (A|B|fail)|C, the manager's run (A := (?=\d), B := \d\d, C := \w)
naive, guard = r'(?=\d)\d\d|\w', r'(?=\d)\d\d|(?!\d)\w'
nv = [m.group() for m in re.finditer(naive, "1x 12 a")]; gv = [m.group() for m in re.finditer(guard, "1x 12 a")]
print("COND the question's run (python `re`): whole `1` naive %s, guarded %s ; find-all `1x 12 a` naive %s, guarded %s ; %s"
      % ("HOLDS" if re.fullmatch(naive, "1") else "FAILS", "HOLDS" if re.fullmatch(guard, "1") else "FAILS", nv, gv,
         check("COND question run reproduced", re.fullmatch(naive, "1") and not re.fullmatch(guard, "1") and nv == ["1", "x", "12", "a"] and gv == ["x", "12", "a"])))
# when-default, hand-worked in the record: A := a digit is next, B := two digits, no else
wd = guarded(CA, CB, None, False)
print("COND when-default hand-worked (whole `12` holds, whole `1` fails, no digit next: holds without consuming): WHOLE `12` %s, `1` %s ; SEARCHED `x` %s ; %s"
      % (fW(wd, "12"), fW(wd, "1"), fS(wd, "x"), check("COND when-default hand-worked", W(wd, "12") is not None and W(wd, "1") is None and (lambda r: r is not None and r[:2] == (0, 0))(S(wd, "x")))))
# a CONDITION as the test: consumes nothing (THE MANAGER'S READING in when-peek), B starts where the test stood
def hlt5(c):
    return lt5(c)
cnd = P.Pcre(r'(?<h>\d)(?:(?C"c")\d\d|(?C"n")\w)', {"c": hlt5, "n": lambda c: not hlt5(c)})
class SemCondLabel(SemCond):
    def at(self, s, st):
        if not re.match(r'\d', s[st:]):
            return []
        h, p = s[st], st + 1
        piece = r'\d\d' if int(h) < 5 else r'\w'
        return [e for e in range(len(s), p - 1, -1) if re.fullmatch(piece, s[p:e])]
d, first = diff3(cnd, SemCondLabel(None, None, None, False), pool("17x", 5))
print("COND `[h = rx.digit] SEQ when((h: <5), rx.digit{2}, else = rx.word)` (a condition as the test: consumes nothing), regex vs semantic %d / %d / %d of %d ; %s ; %s"
      % (d[0], d[1], d[2], len(pool("17x", 5)), show(cnd, "112", "x7x", "112 7x 17"), check("COND condition test consumes nothing", d == [0, 0, 0])))
# when-alone: "when(x) is the same as x" (his lean's words) vs when-default applied to both missing branches
wa = [("`x` (his words: when(x) is the same as x)", P.Pcre(r'\d')),
      ("peek, both branches defaulted `(?=x)|(?!x)`", P.Pcre(r'(?=\d)|(?!\d)')),
      ("bare (consumed), both defaulted `x|(?!x)`", P.Pcre(r'\d|(?!\d)'))]
for desc, rx in wa:
    print("COND when-alone %-48s WHOLE `` %s ; %s" % (desc, fW(rx, ""), show(rx, "a", "a1", "1a2")))
print("     (x := rx.digit; the subjects use `a` for a non-digit)")
check("COND when-alone readings differ", W(wa[0][1], "") is None and W(wa[1][1], "") is not None and W(wa[2][1], "") is not None)

# =====================================================================================================================
print("\n== CHECKS: %d of %d OK%s" % (sum(ok for _, ok in CHECKS), len(CHECKS),
      " ; FAILED: " + ", ".join(n for n, ok in CHECKS if not ok) if any(not ok for _, ok in CHECKS) else ""))
