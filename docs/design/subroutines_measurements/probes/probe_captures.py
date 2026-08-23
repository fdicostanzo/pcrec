"""[DD-14] §3 -- PER-LEVEL CAPTURE SEMANTICS, measured on libpcre2 10.46.

Charter question (i): what does a called group's captures look like AFTER
return, at recursion depth > 1, and after a FAILED call.

The charter's three questions are all ABOUT THE STATE AFTER THE FACT, and
after-the-fact measurement cannot separate two hypotheses that produce the
same table and completely different emitted code:

  H-NEVER   the callee's capture writes never happen -- a call runs the
            group's pattern with capturing switched off
  H-RESTORE the callee's capture writes DO happen and the RETURN puts the
            entry values back

Both answer "g1 is the caller's value" to every after-the-fact cell. They
differ in what a BACKREFERENCE inside the callee sees, in what a nested call
sees, and in whether the emitted code needs a save/restore at all. So this
probe carries a THIRD instrument -- `pcre2_set_callout`, which reads the LIVE
ovector at a chosen point INSIDE the called body (sr_oracle.callout_trace).

Axes:
  C1  after RETURN: the four shapes the charter names
  C2  DURING the call, by callout: is the callee writing the slots?
  C3  DEPTH > 1: three levels, each level's own view
  C4  after a FAILED call
  C5  INHERITANCE: what does the callee see of the CALLER's captures on
      entry -- the cell that decides whether a call is a fresh capture
      environment or the same one
  C6  the CALLED GROUP'S OWN capture while it is being called
  C7  \\K, and whether a call can move the reported start
  C8  the interaction with (?J) duplicate names
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

_out = set()


def cell(pat, subj, note="", opts=0):
    ce = sr.compile_err(pat, opts)
    if ce:
        _out.add("refuse")
        print("  %-38s %-14r ERR %-3d %s" % (pat, subj, ce[0], ce[2]))
        return ("ERR", ce[0])
    r = sr.search(pat, subj, 0, opts)
    _out.add("nomatch" if r is None else "match")
    print("  %-38s %-14r %-34r%s"
          % (pat, subj, r, ("  # " + note) if note else ""))
    return r


def trace(pat, subj, note="", opts=0):
    res, tr = sr.callout_trace(pat, subj, 0, opts)
    print("  %-38s %-12r -> %r" % (pat, subj, res))
    if note:
        print("      # %s" % note)
    if not tr:
        print("      !! NO CALLOUT FIRED -- this cell measured NOTHING")
        _out.add("vacuous")
    for t in tr:
        print("      C%-2d at pos %-3d capture_top=%-2d caps=%r"
              % (t["n"], t["pos"], t["top"], t["caps"]))
    _out.add("traced")
    return res, tr


print("=== C1: the capture state AFTER a call returns =======================")
cell(r"(a|b)(?1)", "ab", "the call matched 'b'; what is g1?")
cell(r"(a|b)(?1)", "ba", "and the other way round")
cell(r"^(?<x>a|b)(?&x)$", "ab", "by name, same question")
cell(r"^(a)((?1))$", "aa", "the call inside another group: g2 is the WRAPPER")
cell(r"^(a)(?:(?1))$", "aa", "non-capturing wrapper")
cell(r"^((a)|(b))(?1)$", "ab",
     "the call took the OTHER branch: are g2/g3 the caller's?")
cell(r"^((a)|(b))(?1)$", "ba", "mirror")
print()
print("# and the same six, asking whether the answer is 'the caller's value'")
print("# or 'unset' -- a call whose body captured and whose capture was")
print("# DISCARDED rather than restored looks different only here:")
cell(r"^(?:(?<x>a)|q)?(?&x)$", "a",
     "group x never ran lexically; the call ran it. Set or unset?")
cell(r"^(?(DEFINE)(?<x>a))(?&x)$", "a",
     "the DEFINE form: x can ONLY be reached through the call")
cell(r"^(?(DEFINE)(?<x>(a)(b)))(?&x)$", "ab",
     "and its inner groups")
print()

print("=== C2: the capture state DURING the call, by callout ================")
print("# `(?C1)` sits INSIDE the called body, so it fires once per LEVEL.")
trace(r"^(a(?C1))(?1)$", "aa",
      "C1 fires at the lexical run AND inside the call. If the two firings "
      "show DIFFERENT g1, the callee is writing the slots (H-RESTORE); if "
      "the second shows the caller's value untouched, H-NEVER")
trace(r"^((a)(?C1))(?1)$", "aa", "same, with an inner group to watch")
trace(r"^(?(DEFINE)((a)(?C1)))(?1)$", "a",
      "a body reachable ONLY by call: every firing is inside a call. "
      "(?1) not (?2): the FIRST version called the inner group, which does "
      "not contain the callout, and the cell fired nothing -- a probe that "
      "silently exercises nothing")
print()

print("=== C3: DEPTH > 1 -- three levels, each level's own view ==============")
trace(r"^(a(?1)?b(?C1))$", "aabb",
      "C1 fires once per level as each level's body completes")
trace(r"^((a)(?1)?(b)(?C1))$", "aabb",
      "with two inner groups; watch g2/g3 per level")
cell(r"^((a)(?1)?(b))$", "aabb", "and the AFTER-the-fact answer")
cell(r"^((a)(?1)?(b))$", "aaabbb", "three levels")
cell(r"^\((\w(?1)?\w)\)$", "(abcd)", "the classic balanced form")
print()
print("# THE DEPTH-ORDER QUESTION: after a recursion unwinds, whose values")
print("# survive -- the OUTERMOST level's or the innermost's?")
cell(r"^((a)(?1)?b)$", "aabb", "g2 at depth 2 is (1,2); after unwind?")
cell(r"^((a)(?1)?b)$", "aaabbb", "depth 3")
print()

print("=== C4: after a FAILED call ==========================================")
cell(r"^(?:(a)(?1)x|(a)y)$", "aay", "the call ran and then the follow failed")
cell(r"^(?:((a)(b))(?1)x|q(?1))$", "qab",
     "the first branch's call wrote g1..g3 and died; the second branch's "
     "call ran the same body")
cell(r"^(?:(a)(?1)x)?(a)y$", "ay", "the whole attempt was abandoned")
trace(r"^(?:((a)(?C1))(?1)x|(?1)y)$", "ay",
      "watch the slots across a failed call and a second call")
print()

print("=== C5: INHERITANCE -- what does the callee see of the CALLER? =======")
print("# The callee body contains a BACKREFERENCE to a group set OUTSIDE it.")
print("# If a call gets a fresh (all-unset) capture environment, the")
print("# reference is unset and, by PCRE2's default, FAILS. If it inherits,")
print("# it matches. One cell, two designs.")
cell(r"^(a)(b\1)(?2)$", "ababa",
     "group 2's body is `b\\1`; the call re-runs it. \\1 = 'a' if inherited")
cell(r"^(a)(b\1)(?2)$", "abab",
     "control: if \\1 were UNSET-and-empty the subject would be shorter")
cell(r"^(x)(?(DEFINE)(?<g>y\1))(?&g)$", "xyx",
     "a DEFINE body referencing an outer group")
cell(r"^(x)(?(DEFINE)(?<g>y\1))(?&g)$", "xy",
     "control: the same without the referenced text")
print("# and with PCRE2_MATCH_UNSET_BACKREF, where an unset reference matches")
print("# the empty string -- so the two designs become distinguishable by")
print("# LENGTH rather than by match/no-match:")
cell(r"^(a)(b\1)(?2)$", "ababa", "inherited", sr.PCRE2_MATCH_UNSET_BACKREF)
cell(r"^(a)(b\1)(?2)$", "abab", "would match if the call reset \\1",
     sr.PCRE2_MATCH_UNSET_BACKREF)
print()
print("# THE SAME QUESTION AT DEPTH: a recursive body referencing its own")
print("# group. At depth 2 the group's value is the DEPTH-2 one if writes")
print("# happen, the depth-1 one if they do not.")
cell(r"^((a|b)(?1)?\2)$", "abba", "self-referential recursion")
cell(r"^((a|b)(?1)?\2)$", "abab", "the other pairing")
trace(r"^((a|b)(?C1)(?1)?\2)$", "abba", "watch g2 per level")
print()

print("=== C6: the CALLED GROUP'S OWN capture while it is being called ======")
trace(r"^(a(?C1))(?1)$", "aa",
      "at the second firing, is g1 (0,1) [inherited], unset [reset], or "
      "(1,2) [being written by the callee]?")
trace(r"^(?(DEFINE)(?<g>a(?C1)))(?&g)(?&g)$", "aa",
      "two calls to the same body; the second sees the first's leavings?")
print()

print("=== C7: \\K and the reported start ===================================")
cell(r"^(a\Kb)(?1)$", "abab", "\\K inside a called group")
cell(r"^(?(DEFINE)(?<g>a\Kb))(?&g)$", "ab", "\\K reached only by a call")
cell(r"^(a)\K(?1)$", "aa", "\\K outside, call after")
cell(r"^(a(?1)?\Kb)$", "aabb", "\\K in a recursive body")
print()

print("=== C8: (?J) duplicate names and a call BY NAME ======================")
cell(r"^(?<a>x)(q)(?<a>y)$", "xqy", "the dupname declaration itself",
     sr.PCRE2_DUPNAMES)
cell(r"^(?<a>x)(q)(?<a>y)(?&a)$", "xqyx",
     "a call to a DUPLICATED name: which group does it run?",
     sr.PCRE2_DUPNAMES)
cell(r"^(?<a>x)(q)(?<a>y)(?&a)$", "xqyy",
     "or is it the LAST declaration?", sr.PCRE2_DUPNAMES)
cell(r"^(?<a>x|z)(q)(?<a>y)(?&a)$", "xqyz",
     "the first declaration's alternation, to be sure it RAN it",
     sr.PCRE2_DUPNAMES)
cell(r"^(?<a>x)(q)(?<a>y)\g<a>$", "xqyx",
     "\\g<name> to a duplicated name", sr.PCRE2_DUPNAMES)
for subj in ["xqyx", "xqyy"]:
    cell(r"^(?<a>x)(q)(?<a>y)\k<a>$", subj,
         "the BACKREFERENCE to the same duplicated name, for contrast",
         sr.PCRE2_DUPNAMES)
print()
print("# THE DISCRIMINATOR the rows above cannot give: make the FIRST")
print("# declaration UNSET. A call that runs 'the first DECLARATION' and a")
print("# reference that reads 'the first SET member' now disagree.")
for subj in ["qyx", "qyy", "qy"]:
    cell(r"^(?:(?<a>x)|q)(?<a>y)(?&a)$", subj,
         "CALL to a dupname whose first declaration did not run",
         sr.PCRE2_DUPNAMES)
for subj in ["qyx", "qyy"]:
    cell(r"^(?:(?<a>x)|q)(?<a>y)\k<a>$", subj,
         "REFERENCE, same shape", sr.PCRE2_DUPNAMES)
print()
print("# and does a CALL to a duplicated name RETRY into the later members")
print("# of the run on backtracking, the way the reference chain does?")
for subj in ["xqyxz", "xqyyz"]:
    cell(r"^(?<a>x)(q)(?<a>y)(?&a)z$", subj,
         "if the call retried the second declaration, 'xqyyz' matches",
         sr.PCRE2_DUPNAMES)
for subj in ["xqyx", "xqyy"]:
    cell(r"^(?<a>x)(q)(?<a>y)(?&a)$", subj, "no follow to force a retry",
         sr.PCRE2_DUPNAMES)
print()

print("=== REACHABILITY GUARD ==============================================")
print("outcomes populated:", sorted(_out))
need = {"match", "nomatch", "traced"}
missing = need - _out
if missing:
    print("!! VACUOUS: %s never occurred" % sorted(missing))
if "vacuous" in _out:
    print("!! at least one callout cell fired NO callout -- see the '!!' rows")
else:
    print("every callout cell fired at least one callout")
