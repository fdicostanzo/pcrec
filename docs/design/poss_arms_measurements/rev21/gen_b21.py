#!/usr/bin/env python3
"""rev 2.1 (possarms21), FROZEN at the sha recorded in poss_arms.md §8.3a.
Adds, over rev 2 (gen_b2.py):
  - N1: GATE-INSIDE-A-REFERENCED-GROUP groups (`((?=a))`, `((?=a)b?)`,
    `(?:((?=a))a)?`, `(\b)`, `((?<=a))`, ...). Each GROUPS row carries the
    group's TEXT model (first characters of the captured text; a zero-width
    item contributes nothing) AND its POSITION reading (first_of's "next
    character here": an A0-narrowed gate is non-nullable with S). The claim
    uses the text model; ablation tag `textpos` marks a row the position
    reading would claim (the rev-2 prototype's defect, S-id at build).
  - N2: tails `(?:\b|)`, `(?:(?=x)|)`, `(?=x)` (an empty BYPASS around a
    gate) and the bounded lazy `x{1,3}?`; ablation tag `lazy` marks a row
    A1-for-lazy (the plant ignores row 2's may_end) would claim.
  - column 9 `src`: `computed` (the cross product's predicate) or `hand`
    (a literal claim written per row), reported separately (R-3(b)).
rev 2 (possarms2): ../gen_b.py plus column 7 `abl` (B-B3's ablation tags,
the ablated predicate that would CLAIM the row) and column 8 `hi` (always 0
here), plus "C" rows: the arm x CALL cells (A-F1's two witnesses, the
panel's arm A/B call-target shapes) and B's depth-1 termination witness.
Ablation tags: nonnull (assume every member body non-nullable), nofold (no
fold at a caseless reference), firstmem (refs[0] only), firstnode (the
first A_CAP with the number only), bodynonnull ((*ACCEPT) ignored),
unsetfails (MATCH_UNSET_BACKREF ignored), cc (A1 continuation lexical only:
the call sites' joined contexts dropped).  Tags `depth2`/`lexical` mark a
WIDER rule that is sound (no divergence expected), not a conjunct.
Original docstring follows.

Arm B: a backreference in the FOLLOW of a quantifier.  CLAIM = the
proposed predicate (FIRST(ref) = fold_if_ref_caseless(union of FIRST over
EVERY group the reference can read), nullable(ref) = any member body
nullable; then the EXISTING disjointness ladder incl. the lazy conjunct).
NAIVE = the claim a plausible narrower spelling would make (no fold / first
member only / body-nullability ignoring ACCEPT / unset-matches-empty), kept
to show each conjunct is load-bearing."""
import itertools
AL = ['a', 'b', 'x', ' ', 'A', '.']
rows = []
def add(mods, g, p, claim, naive=None, src="hand", alpha=None):
    rows.append((mods, g, p, claim, naive, src, alpha or AL))

# basic cross product: GROUP SEP? Q REF TAIL
ALL = set(AL)
# (group, TEXT first, TEXT nullable, POSITION first, POSITION nullable)
GROUPS = [("(a)", {"a"}, False), ("(a|b)", {"a", "b"}, False), ("([ab]+)", {"a", "b"}, False),
          ("(ab)", {"a"}, False), ("(a?)", {"a"}, True), ("(a*)", {"a"}, True), ("(x)", {"x"}, False),
          ("([ax])", {"a", "x"}, False), ("(\\w+)", {"a", "b", "x", "A"}, False)]
GROUPS = [(G, f, n, f, n) for G, f, n in GROUPS] + [
    # N1: a zero-width gate inside the referenced group
    ("((?=a))", set(), True, {"a"}, False),
    ("((?!x))", set(), True, ALL - {"x"}, False),
    ("((?=[ab]))", set(), True, {"a", "b"}, False),
    ("((?=a)b?)", {"b"}, True, {"a"}, False),
    ("((?=a)a)", {"a"}, False, {"a"}, False),
    ("((?!x)a)", {"a"}, False, ALL - {"x"}, False),
    ("(\\b)", set(), True, ALL, False),
    ("(a\\b)", {"a"}, False, {"a"}, False),
    ("(\\ba)", {"a"}, False, ALL, False),
    ("(?:((?=a))a)?", set(), True, {"a"}, False),
    ("(?:((?=a))a|)", set(), True, {"a"}, False),
    ("((?<=a))", set(), True, ALL, False),
    ("((?<=a)b)", {"b"}, False, ALL, False),
]
QS = [("x+", "x++", {"x"}, True), ("x{1,3}", "x{1,3}+", {"x"}, True), ("x*", "x*+", {"x"}, True),
      ("x+?", "x++", {"x"}, False), ("[ .]+", "[ .]++", {" ", "."}, True), ("\\s+", "\\s++", {" "}, True),
      ("a+", "a++", {"a"}, True), ("x{1,3}?", "x{1,3}+", {"x"}, False)]
# (tail, kind, FIRST, nullable): kind "b" is a \b reached at zero consumption
TAILS = [("", "plain", set(), True), ("b", "plain", {"b"}, False), ("x", "plain", {"x"}, False),
         ("$", "plain", set(), True), ("\\b", "b", None, False),
         ("(?:\\b|)", "b", None, True), ("(?=x)", "plain", {"x"}, False),
         ("(?:(?=x)|)", "plain", {"x"}, True)]
W = {"a", "b", "x", "A"}
def claim_of(gf, gn, q, qc, greedy, kind, tf, tnull, lazy_a1=False):
    """The rev-2.1 predicate. `lazy_a1`: the N2 ablation -- A1 admitted for a
    lazy loop with row 2's may_end ignored (what PROTO_SAB_LAZY does)."""
    eff = set(gf)
    may_end = False
    a1 = False
    if gn:
        if kind == "b":
            # \b reached at ZERO consumption when the reference is empty:
            # arm A1 values it from Q's LAST polarity (greedy, m >= 1);
            # otherwise (lazy, m = 0, mixed class) it widens.
            if (greedy or lazy_a1) and not q.startswith("x*") and (qc <= W or not (qc & W)):
                eff |= {c for c in AL if (c in W) != (qc <= W)}
                a1 = True
            else:
                eff = set(AL)
        else: eff |= tf
        may_end = tnull
    disjoint = not (qc & eff)
    if lazy_a1 and a1: return disjoint
    return disjoint and (greedy or not may_end)
for (G, gf, gn, pf, pn), (q, qp, qc, greedy), (t, kind, tf, tnull) in itertools.product(GROUPS, QS, TAILS):
    for mid in ("", " "):
        g = G + mid + q + "\\1" + t
        p = G + mid + qp + "\\1" + t
        claim = claim_of(gf, gn, q, qc, greedy, kind, tf, tnull)
        abl = []
        if not claim:
            if gn and (not (qc & set(gf))) and greedy and kind != "b": abl.append("nonnull")
            if claim_of(pf, pn, q, qc, greedy, kind, tf, tnull): abl.append("textpos")
            if not greedy and claim_of(gf, gn, q, qc, greedy, kind, tf, tnull, lazy_a1=True): abl.append("lazy")
        add("no_auto_possess", g, p, "yes" if claim else "no", ",".join(abl) + "-yes" if abl else None, src="computed")

# caseless at the reference vs at the group
add("no_auto_possess", "(a)A+(?i:\\1)", "(a)A++(?i:\\1)", "no", "unfolded-yes")
add("no_auto_possess", "(a)x+(?i:\\1)", "(a)x++(?i:\\1)", "yes")
add("no_auto_possess", "(?i:(a))A+\\1", "(?i:(a))A++\\1", "no", "unfolded-yes")
add("no_auto_possess", "(?i)(a)x+\\1", "(?i)(a)x++\\1", "yes")
add("no_auto_possess", "(a)(?i)A+\\1", "(a)(?i)A++\\1", "no")
# duplicate names: every member of the run
add("no_auto_possess,dupnames", "(?:(?<n>a)|(?<n>x))x+\\k<n>", "(?:(?<n>a)|(?<n>x))x++\\k<n>", "no", "firstmember-yes")
add("no_auto_possess,dupnames", "(?:(?<n>x)|(?<n>a))x+\\k<n>", "(?:(?<n>x)|(?<n>a))x++\\k<n>", "no")
add("no_auto_possess,dupnames", "(?:(?<n>a)|(?<n>b))x+\\k<n>", "(?:(?<n>a)|(?<n>b))x++\\k<n>", "yes")
add("no_auto_possess,dupnames", "(?<n>a)?(?<n>x)?x+\\k<n>", "(?<n>a)?(?<n>x)?x++\\k<n>", "no", "firstmember-yes")
# branch reset: every A_CAP with the number
add("no_auto_possess", "(?|(a)|(x))x+\\1", "(?|(a)|(x))x++\\1", "no", "firstnode-yes")
add("no_auto_possess", "(?|(a)|(b))x+\\1", "(?|(a)|(b))x++\\1", "yes")
# unset groups: PCRE2 fails, so they contribute nothing ...
add("no_auto_possess", "(?:(a)|b)x+\\1", "(?:(a)|b)x++\\1", "yes")
add("no_auto_possess", "(?:(a)|b)x+\\1x", "(?:(a)|b)x++\\1x", "yes")
# ... unless MATCH_UNSET_BACKREF, which makes the reference nullable
add("no_auto_possess,match_unset_backref", "(?:(a)|b)x+\\1x", "(?:(a)|b)x++\\1x", "no", "unsetfails-yes")
add("no_auto_possess,match_unset_backref", "(?:(a)|b)x+\\1", "(?:(a)|b)x++\\1", "yes")
# re-entered / forward / self references
# rev 2: CLAIM-vs-MARK found these two hand claims wider than the rule: the
# enclosing loop restarts with x, which ENCL unions UNGATED (the inherited
# conservatism, poss_arms.md §2.3); sound either way -- tagged `encl`.
add("no_auto_possess", "(?:x+\\1|(a))+", "(?:x++\\1|(a))+", "no", "encl-yes")
add("no_auto_possess", "(?:(a)|x+\\1)+", "(?:(a)|x++\\1)+", "no", "encl-yes")
add("no_auto_possess", "(a|x+\\1)+", "(a|x++\\1)+", "no")
add("no_auto_possess", "(x+)\\1", "(x++)\\1", "no")
add("no_auto_possess", "((a)|b)x+\\2", "((a)|b)x++\\2", "yes")
add("no_auto_possess", "(?<=(a))x+\\1", "(?<=(a))x++\\1", "yes")
add("no_auto_possess", "(?=(a))x+\\1", "(?=(a))x++\\1", "yes")
add("no_auto_possess", "(a)(\\1b)x+\\2", "(a)(\\1b)x++\\2", "yes")
add("no_auto_possess", "(a)(?1)x+\\1", "(a)(?1)x++\\1", "yes")
add("no_auto_possess", "(?(DEFINE)(?<w>(a)))(?&w)x+\\2", "(?(DEFINE)(?<w>(a)))(?&w)x++\\2", "yes")
add("no_auto_possess", "(?:(?(DEFINE)(?<w>(x)))(?&w)|(a))x+\\2", "(?:(?(DEFINE)(?<w>(x)))(?&w)|(a))x++\\2", "no", "lexical-yes")
# (*ACCEPT) can close a group early, even EMPTY
add("no_auto_possess", "(?=((*ACCEPT)a))x+\\1x", "(?=((*ACCEPT)a))x++\\1x", "no", "bodynonnull-yes")
add("no_auto_possess", "(?=(a(*ACCEPT)b))x+\\1", "(?=(a(*ACCEPT)b))x++\\1", "yes")
# doubled-word, arm B half only
add("no_auto_possess", "\\b(\\w+)\\b\\s+\\1\\b", "\\b(\\w+)\\b\\s++\\1\\b", "yes")
add("no_auto_possess", "\\b(\\w+)\\b\\s+\\1\\b", "\\b(\\w++)\\b\\s++\\1\\b", "yes")
# depth-1 termination witness (B-B3): a reference cycle through two groups
add("no_auto_possess", "(a\\2)(b\\1)x+\\1", "(a\\2)(b\\1)x++\\1", "yes")
add("no_auto_possess", "(a\\2)?(b\\1)?x+\\1", "(a\\2)?(b\\1)?x++\\1", "yes")
# N1's three 10.46 witnesses (re-check critic R): A0 + B together, the
# position reading of a zero-width gate as the first character of a TEXT.
ALC = AL + ["c"]
add("no_auto_possess", "(?:((?=a))a)?b+\\1b", "(?:((?=a))a)?b++\\1b", "no", "textpos-yes", alpha=ALC)
add("no_auto_possess", "((?=a)c?)ab+\\1b", "((?=a)c?)ab++\\1b", "no", "textpos-yes", alpha=ALC)
add("no_auto_possess", "(?:((?=a))a|)b+\\1b", "(?:((?=a))a|)b++\\1b", "no", "textpos-yes", alpha=ALC)
# rev 2.1: the depth-1 rule is gone (R-4); a deeper reference resolves through
# the memoized capture fact, so (a)(\1b)x+\2 is now CLAIMED (sound: rev 2's
# depth2 row measured 0 diverging) -- re-tagged a claim, hand-literal.
for k, (m, g, p, c, n, src, al) in enumerate(rows):
    tag = (n or "").replace("-yes", "")
    tag = {"unfolded": "nofold"}.get(tag, tag)
    print("B%04d\t%s\t%s\t%s\t%s\t%r\t%s\t0\t%s" % (k + 1, m, g, p, c, al, tag, src))
# arm x CALL rows (A-F1 / the panel's calls.txt additions)
CALLS = [
  ("(a+(?:\\b|))|b(?1)a", "(a++(?:\\b|))|b(?1)a", "no", "cc"),
  ("(?:b(?R)a|a+(?:\\b|))", "(?:b(?R)a|a++(?:\\b|))", "no", "cc"),
  ("(\\w+\\b)x(?1)", "(\\w++\\b)x(?1)", "yes", ""),
  ("(\\w+\\b)x(?1)y", "(\\w++\\b)x(?1)y", "yes", ""),
  ("(\\w+(?:\\b|))x(?1)a", "(\\w++(?:\\b|))x(?1)a", "no", "cc"),
  ("(a?)(x+\\1)b(?2)x", "(a?)(x++\\1)b(?2)x", "no", "cc"),
  ("(a)(x+\\1)b(?2)x", "(a)(x++\\1)b(?2)x", "yes", ""),
]
for k, (g, p, c, t) in enumerate(CALLS):
    print("C%04d\tno_auto_possess\t%s\t%s\t%s\t%r\t%s\t0\thand" % (k + 1, g, p, c, AL, t))
