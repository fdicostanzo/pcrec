"""[DD-14] §2 -- THE CONSTRUCT TABLE, measured on libpcre2 10.46 and python.

Every spelling PCRE2 has for "run that group's pattern again here", plus the
two spellings a reader confuses them with (`\\1` and `\\g{1}`, which are
BACKREFERENCES and belong to module `backrefs`). For each: does it compile,
WHICH GROUP does it reach, and is it a CALL or a REFERENCE -- three questions
whose answers a compile-status column alone cannot give.

THE CALL/REFERENCE DISCRIMINATOR, stated because everything downstream rests
on it. `(a|b)\\1` and `(a|b)(?1)` both compile and both look like "group 1
again". They are different constructs:

    (a|b)\\1   on "ab"  -> NO MATCH   (the reference wants the same TEXT)
    (a|b)(?1)  on "ab"  -> MATCH      (the call re-RUNS the alternation)

so the cell `(a|b)X` on "ab" separates them with one bit and no reasoning.
Every row below carries it.

REACHABILITY: a row that neither compiles nor refuses for the reason under
test measures nothing. The `note` column says which of the four outcomes
each row is, and the tail asserts that every one of the four is populated --
a table in which every row compiled would not be a table about refusals.

Axes:
  A1  the CALL spellings: compile, target, call-vs-reference
  A2  the two REFERENCE spellings that share a doorway with a call spelling
  A3  the RELATIVE forms and what they resolve to, at several distances
  A4  (?R) / (?0): whole-pattern recursion, and what "whole" includes
  A5  the DEFINE idiom, and what it is worth
  A6  REFUSALS: calls to groups that do not exist, and their error numbers
  A7  python `re`: the whole vocabulary, in one place
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "sr_oracle", os.path.join(_HERE, "sr_oracle.py"))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)

print("libpcre2:", sr.version())
print("python3 :", sys.version.split()[0])
print("sr_oracle.SELFCHECK:", sr.SELFCHECK or "none")
print()

_seen_outcomes = set()


def cell(pat, subj, want=None, note=""):
    ce = sr.compile_err(pat)
    if ce:
        _seen_outcomes.add("refuse")
        print("  %-34s %-12r ERR %-3d %s" % (pat, subj, ce[0], ce[2]))
        return ("ERR", ce[0])
    r = sr.search(pat, subj)
    _seen_outcomes.add("nomatch" if r is None else "match")
    flag = ""
    if want is not None:
        flag = "  <-- EXPECTED %r" % (want,) if r != want else "  ok"
    print("  %-34s %-12r %-40r%s%s"
          % (pat, subj, r, ("  # " + note) if note else "", flag))
    return r


print("=== A1: the CALL spellings ==========================================")
print("# each row: does it compile, and is it a CALL (matches 'ab') or a")
print("# REFERENCE (would need 'aa')?  The subject is 'ab' throughout, so a")
print("# match IS the call verdict and a no-match IS the reference verdict.")
for pat in [r"(a|b)(?1)", r"(a|b)(?-1)", r"(?<n>a|b)(?&n)",
            r"(?P<n>a|b)(?P>n)", r"(a|b)\g<1>", r"(?<n>a|b)\g<n>",
            r"(a|b)\g'1'", r"(?<n>a|b)\g'n'", r"(a|b)\g<-1>",
            r"(a|b)\g'-1'"]:
    cell(pat, "ab", note="CALL if it matches")
print()
print("# and the same ten against 'aa', where BOTH a call and a reference")
print("# match -- so this column alone would have told a reader nothing:")
for pat in [r"(a|b)(?1)", r"(a|b)(?-1)", r"(?<n>a|b)(?&n)",
            r"(?P<n>a|b)(?P>n)", r"(a|b)\g<1>", r"(?<n>a|b)\g<n>",
            r"(a|b)\g'1'", r"(?<n>a|b)\g'n'", r"(a|b)\g<-1>",
            r"(a|b)\g'-1'"]:
    cell(pat, "aa")
print()

print("=== A2: the REFERENCE spellings that share a doorway with a call =====")
print("# `\\g` is ONE escape selector serving TWO modules; the TAIL decides.")
for pat in [r"(a|b)\1", r"(a|b)\g1", r"(a|b)\g{1}", r"(a|b)\g{-1}",
            r"(?<n>a|b)\k<n>", r"(?P<n>a|b)(?P=n)", r"(?<n>a|b)\k'n'",
            r"(?<n>a|b)\k{n}", r"(?<n>a|b)\g{n}"]:
    cell(pat, "ab", note="REFERENCE if it does NOT match")
print()

print("=== A3: the RELATIVE forms, at several distances =====================")
print("# (?+N) counts groups to the RIGHT of the call, (?-N) to the LEFT.")
print("# The subjects are chosen so that the WRONG target gives a different")
print("# answer, not merely a different capture.")
cell(r"^(a)(?-1)$", "aa", note="(?-1) -> group 1")
cell(r"^(a)(b)(?-1)$", "abb", note="(?-1) -> group 2 (the NEAREST left)")
cell(r"^(a)(b)(?-2)$", "aba", note="(?-2) -> group 1")
cell(r"^(?+1)(a)$", "aa", note="(?+1) -> group 1, a FORWARD call")
cell(r"^(?+2)(a)(b)$", "bab", note="(?+2) -> group 2, forward past one")
cell(r"^(a)(?-01)$", "aa", note="leading zero in a relative call")
cell(r"^(a)\g<-1>$", "aa", note="\\g<-N> is the same relative rule")
cell(r"^\g<+1>(a)$", "aa", note="\\g<+N> forward")
cell(r"^(a)(b)(?2)$", "abb", note="ABSOLUTE (?2) for contrast")
print()
print("# the FORWARD call is the one that makes a call unlike a reference:")
print("# a forward REFERENCE can only ever be unset, a forward CALL works.")
cell(r"^(?+1)(a|b)$", "ab", note="forward CALL: runs group 1's pattern early")
cell(r"^\2(a|b)(c)$", "abc", note="forward REFERENCE, for contrast")
print()

print("=== A4: (?R) and (?0): what does 'the whole pattern' include? ========")
cell(r"\((a(?R)?b)\)", "(ab)", note="(?R) inside a group")
cell(r"^(a(?1)?b)$", "aabb", note="(?1) recursion, anchors OUTSIDE the group")
cell(r"^(a(?R)?b)$", "aabb",
     note="(?R) re-runs ^...$ TOO -- the anchors come with it")
cell(r"^(a(?R)?b)$", "ab", note="depth 1 only: the anchors still fit")
cell(r"(a(?R)?b)", "aabb", note="unanchored (?R): does it reach depth 2?")
cell(r"(a(?0)?b)", "aabb", note="(?0) is documented as a synonym for (?R)")
cell(r"(a)(?0)", "aa", note="a (?0) with no terminating alternative")
print()
print("# the SAME body written three ways, one subject, so the difference")
print("# between 'the whole pattern' and 'group 1' is a single cell:")
for p in [r"^(a(?R)?b)$", r"^(a(?0)?b)$", r"^(a(?1)?b)$"]:
    cell(p, "aabb")
print()

print("=== A5: the (?(DEFINE)...) idiom =====================================")
cell(r"^(?(DEFINE)(?<w>[a-z]+))(?&w)-(?&w)$", "foo-bar",
     note="the library-pattern idiom: define once, call twice")
cell(r"^(?(DEFINE)(?<w>[a-z]+))(?&w)-(?&w)$", "foo-",
     note="and it really is required to match")
cell(r"^(?:(?<w>[a-z]+))?(?&w)-(?&w)$", "foo-bar",
     note="a DEFINE-LESS spelling of the same intent: optional group")
cell(r"^(?!)(?<w>[a-z]+)|(?&w)-(?&w)$", "foo-bar",
     note="another DEFINE-less dodge: an unreachable branch")
cell(r"^(?<w>[a-z]+)?+(?&w)-(?&w)$", "foo-bar",
     note="possessive-optional dodge")
print("# what DEFINE actually costs a caller who cannot have it: the group")
print("# is still THERE, so it can match, and its capture is visible:")
cell(r"^(?:(?<w>[a-z]+))?(?&w)-(?&w)$", "foo-bar")
cell(r"^(?(DEFINE)(?<w>[a-z]+))(?&w)-(?&w)$", "foo-bar")
print()

print("=== A6: REFUSALS and their PCRE2 error numbers =======================")
for pat, why in [
        (r"(a)(?2)", "call to a group that does not exist"),
        (r"(a)(?9)", "call to a far group that does not exist"),
        (r"(a)(?-2)", "relative call past the start"),
        (r"(a)(?+2)", "relative call past the end"),
        (r"(?<n>a)(?&m)", "call to an undeclared NAME"),
        (r"(a)\g<2>", "\\g<N> to a group that does not exist"),
        (r"(a)\g<m>", "\\g<name> to an undeclared name"),
        (r"(a)(?0", "unterminated"),
        (r"(a)(?&)", "empty name"),
        (r"(a)\g<>", "empty \\g<>"),
        (r"(a)(?+0)", "relative zero, forward"),
        (r"(a)(?-0)", "relative zero, backward"),
        (r"(a)\g<0>", "\\g<0>: is it the whole pattern?"),
        (r"(a)\g'0'", "\\g'0'"),
]:
    r = cell(pat, "aa", note=why)
print()

print("=== A7a: TWO SPELLINGS THE CHARTER'S LIST DOES NOT HAVE ==============")
print("# A6 found `\\g<0>` and `\\g'0'` COMPILING. Group 0 is the whole")
print("# pattern, so these should be (?R) synonyms -- measured, not assumed:")
cell(r"(a\g<0>?b)", "aabb", note="\\g<0> as whole-pattern recursion")
cell(r"(a\g'0'?b)", "aabb", note="\\g'0' likewise")
cell(r"^(a\g<0>?b)$", "aabb",
     note="and it carries the anchors, exactly as (?R) does")
cell(r"(a(?R)?b)", "aabb", note="the (?R) control, same subject")
print()
print("# GROUP NUMBERS ABOVE 9: pcrec's registry has rows for (?1)..(?9)")
print("# only. Does PCRE2 accept a two-digit absolute call?")
cell("(a)" * 10 + r"(?10)", "a" * 11, note="(?10) with ten groups")
cell("(a)" * 12 + r"(?12)", "a" * 13, note="(?12)")
cell("(a)" * 10 + r"(?-10)", "a" * 11, note="(?-10), two-digit relative")
cell("(a)" * 10 + r"(?+1)(b)", "a" * 10 + "bb", note="(?+1) past ten groups")
print()

print("=== A7b: DEFINE-LESS EQUIVALENCE, swept ==============================")
print("# A5 found `^(?!)(?<w>X)|BODY$` reproducing DEFINE's semantics on one")
print("# cell. One cell is an anecdote. Here it is against the DEFINE form")
print("# over a subject set that includes the failing and the capturing ones.")
_define = r"^(?(DEFINE)(?<w>[a-z]+))(?&w)-(?&w)$"
_dodge = r"^(?!)(?<w>[a-z]+)|^(?&w)-(?&w)$"
_optional = r"^(?:(?<w>[a-z]+))?(?&w)-(?&w)$"
_agree = _disagree = 0
for subj in ["foo-bar", "foo-", "-bar", "a-b", "", "-", "foo-bar-baz",
             "FOO-bar", "foo bar", "x-y", "aaa-aaa"]:
    d = sr.search(_define, subj)
    g = sr.search(_dodge, subj)
    o = sr.search(_optional, subj)
    same_g = (d == g)
    same_o = (d == o)
    _agree += 1 if same_g else 0
    _disagree += 0 if same_g else 1
    print("  %-12r DEFINE=%-24r dodge=%-24r%s   optional=%-24r%s"
          % (subj, d, g, "" if same_g else "  <-- DIFFERS",
             o, "" if same_o else "  <-- DIFFERS"))
print("  the (?!)-branch dodge agrees with DEFINE on %d/%d subjects"
      % (_agree, _agree + _disagree))
if _agree + _disagree == 0:
    print("  !! VACUOUS: no subjects compared")
print()

print("=== A7: python `re` on the whole vocabulary ==========================")
print("# The D27 goal-facts question: which cells does python rule?")
for pat in [r"(a|b)(?1)", r"(a|b)(?-1)", r"(?<n>a|b)(?&n)",
            r"(?P<n>a|b)(?P>n)", r"(a|b)\g<1>", r"(a|b)\g'1'",
            r"(a(?R)?b)", r"(a)(?0)", r"(?(DEFINE)(?<x>a))(?&x)",
            r"(a|b)\1", r"(?P<n>a|b)(?P=n)", r"(?P<n>a|b)(?P=n)",
            r"(?<n>a|b)\k<n>", r"(a|b)\g{1}", r"(a)\g<0>"]:
    c, err = sr.pyre(pat)
    print("  %-34s %s" % (pat, "compiles" if err is None else err))
print()

print("=== REACHABILITY GUARD ==============================================")
print("outcomes populated by the cells above:", sorted(_seen_outcomes))
missing = {"match", "nomatch", "refuse"} - _seen_outcomes
if missing:
    print("!! VACUOUS: no cell produced %s -- this table is not measuring "
          "what it claims" % sorted(missing))
else:
    print("all three outcomes present: the table separates compile, match and "
          "no-match rather than reporting one of them everywhere")
