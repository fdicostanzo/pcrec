#!/usr/bin/env python3
"""Arm B: a backreference in the FOLLOW of a quantifier.  CLAIM = the
proposed predicate (FIRST(ref) = fold_if_ref_caseless(union of FIRST over
EVERY group the reference can read), nullable(ref) = any member body
nullable; then the EXISTING disjointness ladder incl. the lazy conjunct).
NAIVE = the claim a plausible narrower spelling would make (no fold / first
member only / body-nullability ignoring ACCEPT / unset-matches-empty), kept
to show each conjunct is load-bearing."""
import itertools
AL = ['a', 'b', 'x', ' ', 'A', '.']
rows = []
def add(mods, g, p, claim, naive=None):
    rows.append((mods, g, p, claim, naive))

# basic cross product: GROUP SEP? Q REF TAIL
GROUPS = [("(a)", {"a"}, False), ("(a|b)", {"a", "b"}, False), ("([ab]+)", {"a", "b"}, False),
          ("(ab)", {"a"}, False), ("(a?)", {"a"}, True), ("(a*)", {"a"}, True), ("(x)", {"x"}, False),
          ("([ax])", {"a", "x"}, False), ("(\\w+)", {"a", "b", "x", "A"}, False)]
QS = [("x+", "x++", {"x"}, True), ("x{1,3}", "x{1,3}+", {"x"}, True), ("x*", "x*+", {"x"}, True),
      ("x+?", "x++", {"x"}, False), ("[ .]+", "[ .]++", {" ", "."}, True), ("\\s+", "\\s++", {" "}, True),
      ("a+", "a++", {"a"}, True)]
TAILS = [("", set(), True), ("b", {"b"}, False), ("x", {"x"}, False), ("$", set(), True), ("\\b", None, False)]
for (G, gf, gn), (q, qp, qc, greedy), (t, tf, tnull) in itertools.product(GROUPS, QS, TAILS):
    for mid in ("", " "):
        g = G + mid + q + "\\1" + t
        p = G + mid + qp + "\\1" + t
        eff = set(gf)
        may_end = False
        if gn:
            if tf is None: eff = set(AL)             # \b widens (arm A does not apply: no Q before it)
            else: eff |= tf
            may_end = tnull
        claim = (not (qc & eff)) and (greedy or not may_end)
        add("no_auto_possess", g, p, "yes" if claim else "no")

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
add("no_auto_possess", "(?:x+\\1|(a))+", "(?:x++\\1|(a))+", "yes")
add("no_auto_possess", "(?:(a)|x+\\1)+", "(?:(a)|x++\\1)+", "yes")
add("no_auto_possess", "(a|x+\\1)+", "(a|x++\\1)+", "no")
add("no_auto_possess", "(x+)\\1", "(x++)\\1", "no")
add("no_auto_possess", "((a)|b)x+\\2", "((a)|b)x++\\2", "yes")
add("no_auto_possess", "(?<=(a))x+\\1", "(?<=(a))x++\\1", "yes")
add("no_auto_possess", "(?=(a))x+\\1", "(?=(a))x++\\1", "yes")
add("no_auto_possess", "(a)(\\1b)x+\\2", "(a)(\\1b)x++\\2", "no", "depth2-yes")
add("no_auto_possess", "(a)(?1)x+\\1", "(a)(?1)x++\\1", "yes")
add("no_auto_possess", "(?(DEFINE)(?<w>(a)))(?&w)x+\\2", "(?(DEFINE)(?<w>(a)))(?&w)x++\\2", "yes")
add("no_auto_possess", "(?:(?(DEFINE)(?<w>(x)))(?&w)|(a))x+\\2", "(?:(?(DEFINE)(?<w>(x)))(?&w)|(a))x++\\2", "no", "lexical-yes")
# (*ACCEPT) can close a group early, even EMPTY
add("no_auto_possess", "(?=((*ACCEPT)a))x+\\1x", "(?=((*ACCEPT)a))x++\\1x", "no", "bodynonnull-yes")
add("no_auto_possess", "(?=(a(*ACCEPT)b))x+\\1", "(?=(a(*ACCEPT)b))x++\\1", "yes")
# doubled-word, arm B half only
add("no_auto_possess", "\\b(\\w+)\\b\\s+\\1\\b", "\\b(\\w+)\\b\\s++\\1\\b", "yes")
add("no_auto_possess", "\\b(\\w+)\\b\\s+\\1\\b", "\\b(\\w++)\\b\\s++\\1\\b", "yes")
for k, (m, g, p, c, n) in enumerate(rows):
    print("B%04d\t%s\t%s\t%s\t%s\t%r" % (k + 1, m, g, p, c + ("|" + n if n else ""), AL))
