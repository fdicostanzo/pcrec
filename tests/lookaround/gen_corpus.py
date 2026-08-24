#!/usr/bin/env python3
"""tests/lookaround/gen_corpus.py — module `lookaround` ([M6.6.2]): the corpus
GENERATOR, and the reason it exists is the `# pcre2-only` marking.

R32 C3 found a test plan that marked two corpus files python-verifiable in the
direction that LOSES the oracle, and design §7 (the D27 goal-facts list) records
the same species in this module twice over: the charter EXPECTED python to lack
quantified lookaround (G8) and to disagree about captures in a negative
lookahead (G9), and BOTH are refuted — python agrees on all fourteen quantified
forms and on all 27 capture cells. Marking a block `# pcre2-only` by hand from
either expectation would have thrown a working oracle away.

So the marking is COMPUTED. Every cell below is driven through libpcre2 10.46
(the committed ctypes binding at docs/design/eng_brep_measurements/probes/) AND
through python3 `re` in the same pass; the EXPECTATION is libpcre2's (D26: PCRE2
is the source of truth), and a block carries `# pcre2-only` exactly when python
diverged or could not compile it, with the first divergence and the cell count
written above the marking.

WHAT IT DOES NOT DO, and this is the point of the file: it never asks pcrec
anything. An expectation derived from the compiler under test is not an
expectation.

Usage:  python3 tests/lookaround/gen_corpus.py [outdir]     (default: this dir)
"""
import os
import re as pyre
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "design",
                                "eng_brep_measurements", "probes"))
try:
    import pcre2_ctypes as P
except Exception as e:                                      # noqa: BLE001
    sys.stderr.write("gen_corpus: libpcre2 unavailable: %s\n" % e)
    sys.exit(3)

LA = "lookaround"


def cell(pat, feats, cases, note=None, perr=False):
    """One .rxt block. `cases` is a list of (subject, startpos)."""
    return {"pat": pat, "feats": feats, "cases": cases,
            "note": note, "perr": perr}


# ===========================================================================
#  lookahead.rxt — `(?=` and `(?!`: bodies, contexts, degenerate forms
# ===========================================================================
LOOKAHEAD = [
 cell("(?=ab)abc", LA, [("abc", 0), ("abd", 0), ("xabc", 0), ("ab", 0)],
      "THE SHAPE ITSELF: the assertion consumes nothing, so the body's bytes "
      "are matched a SECOND time by what follows."),
 cell("a(?=b)bc", LA, [("abc", 0), ("abd", 0)],
      "A lookahead in the MIDDLE, where the entry position is not the "
      "attempt position -- the cursor restore is what makes `b` still match."),
 cell("ab(?=c)", LA, [("abc", 0), ("abd", 0), ("ab", 0)],
      "TRAILING, so the reported END is the assertion's entry: (0,2) on "
      "\"abc\" and not (0,3). Zero width is a claim about the SPAN."),
 cell("ab(?!c)", LA, [("abd", 0), ("abc", 0), ("ab", 0)],
      "The negative form trailing, including the end-of-subject case: an "
      "empty remainder cannot match `c`, so the assertion HOLDS."),
 cell("(?=a)b", LA, [("b", 0), ("ab", 0), ("a", 0)],
      "THE ERASED-LOOKAROUND CELL, CAPTURE-FREE ON PURPOSE (R33 C2-12). "
      "src/ir/nfa.c lowers an A_LOOK to an EPSILON, so the DFA prefilter is "
      "built from the lookaround-ERASED pattern -- which for this cell is "
      "`b`, and `b` MATCHES \"b\" where the truth is NOMATCH. Only SR-8's "
      "VM_ONLY stamp stands between the sound reading (a filter) and the "
      "miscompile (a machine), and sabotage row S126 flips THE `(?=...)` "
      "ROW's own `engines` to prove it. The cell must be CAPTURE-FREE: "
      "`(a)(?=b)c` keeps the VM regardless of the flip, because delivering a "
      "capture slot is already VM-forcing, and would mask the row."),
 cell("(?!x)abc", LA, [("abc", 0), ("xabc", 0)],
      "A LEADING negative assertion, which is the shape a prefilter has to "
      "survive (design §5): the lookaround-erased pattern is `abc`."),
 cell("(?=a|b)[ab]c", LA, [("ac", 0), ("bc", 0), ("cc", 0)],
      "An ALTERNATION body. The assertion succeeds on either branch and the "
      "class re-matches whichever one it was."),
 cell("(?=(?=a)a)ab", LA, [("ab", 0), ("bb", 0)],
      "NESTED LOOKAHEADS. Two mark slots and two cursor slots are live at "
      "once, which is why the entry label re-sets them on every entry."),
 cell("(?=(?!x)a)ab", LA, [("ab", 0), ("xb", 0)],
      "A NEGATIVE nested inside a POSITIVE -- the inner form's pushed frame "
      "must not survive into the outer assertion's own bookkeeping."),
 cell("(?=a+b)aab", LA, [("aab", 0), ("aa", 0), ("ab", 0)],
      "A QUANTIFIED body: the body backtracks internally before it succeeds."),
 cell("(?=(a+)b)a+b", LA, [("aab", 0), ("aaab", 0), ("ab", 0)],
      "§3.2.1's ROW 1, BY NAME. The body and the follow are THE SAME BYTES, "
      "so an unscoped `v->fmin` bounds the body at 1+2=3 and this cell "
      "becomes a MISSED MATCH. Sabotage row S132."),
 cell("(?!(a+)b)a+b", LA, [("aab", 0), ("aac", 0)],
      "§3.2.1's ROW 2, BY NAME, AND IT IS THE DANGEROUS ONE. An unsound "
      "prune inside a NEGATIVE assertion prunes the body to FAIL, which "
      "makes the assertion HOLD -- a FALSE MATCH, not a missed one. This "
      "cell goes from nomatch to (0,3) under S132."),
 cell("(?=(a|ab))a", LA, [("abab", 0), ("ab", 0)],
      "The atomicity DISCRIMINATOR's body without the backreference; the "
      "discriminating cell itself needs `backrefs` and is below."),
 cell(r"(?=(a|ab))\1$", LA + ",backrefs", [("abab", 0), ("aa", 0)],
      "§2.2's ATOMICITY DISCRIMINATOR, the atomic half. The lookahead keeps "
      "its FIRST success (\"a\"), so \\1 is \"a\" and \"a\" does not end the "
      "subject -> NOMATCH. Its NON-ATOMIC twin `(?*(a|ab))\\1$` answers "
      "(2,4) on the same subject and lives in nonatomic_ahead.rxt; the two "
      "cells together are what fix the two families apart. Sabotage row "
      "S122 deletes the cut and this cell is its detector."),
 cell("a(?=)b", LA, [("ab", 0), ("ac", 0)],
      "§2.6's DEGENERATE BODIES. An empty body always succeeds, so the "
      "positive form is a NO-OP -- and it needs no special case: "
      "`pcrec_parse_body` returns an A_EMPTY and §3's shape swallows it."),
 cell("a(?!)b", LA, [("ab", 0)],
      "...and the negative form with an empty body is `(*FAIL)`."),
 cell("(?:(?!))|a", LA, [("a", 0), ("b", 0)],
      "§2.6's third degenerate cell: an always-failing branch beside a "
      "matching one."),
 cell("(?=)", LA, [("", 0), ("abc", 0)],
      "A lookahead as the WHOLE pattern, matching empty at offset 0."),
 cell("(?=b)bc", LA, [("abc", 1), ("abc", 0)],
      "STARTPOS. A lookahead's entry position is the attempt position, so "
      "the assertion is evaluated at `startpos` and not at 0."),
 cell("(?!a)b", LA, [("ab", 1), ("ab", 0), ("b", 0)],
      "The negative form under startpos, same axis."),
 cell("(?=abc)ab", LA, [("abc", 0), ("abd", 0)],
      "The body reaches PAST what the pattern consumes -- the assertion "
      "inspects bytes the match never claims."),
 cell("(?=a)(?=ab)abc", LA, [("abc", 0), ("acb", 0)],
      "TWO assertions in sequence at the same position: independent slots, "
      "independent marks, and both restores must land on the same byte."),
 cell(r"(?=a)\Kb", "assertions," + LA, [("ab", 0), ("b", 0)],
      "§2.7's FOUR COMPILING CELLS, the half a too-broad `\\K` check breaks. "
      "The refusal is about `\\K` INSIDE the assertion; once the assertion "
      "has closed, `\\K` is the ordinary construct module `assertions` "
      "already ships. A check that latched on \"a lookaround was seen\" "
      "would wrongly refuse these, so sabotage row S128's prediction names "
      "BOTH sets and the row cannot go green by being too broad."),
 cell(r"a(?=b)\Kc", "assertions," + LA, [("abc", 0), ("abd", 0)], None),
 cell(r"a\Kb", "assertions," + LA, [("ab", 0)],
      "...and the control with no lookaround at all, which must be untouched "
      "by anything this module does."),
 cell("(?=(?:aa|a)b)a+b", LA, [("aab", 0), ("ab", 0)],
      "A body whose iteration can end in TWO places, which is the shape "
      "atomic_groups_design.md had to rebuild its own measurement around."),
]

# ===========================================================================
#  captures.rxt — the four polarity/outcome combinations, with `g` lines
# ===========================================================================
CAPTURES = [
 cell("(?=(a))a", LA, [("a", 0), ("b", 0)],
      "C1 -- RETENTION. A capture written inside a POSITIVE lookahead "
      "SURVIVES the assertion: nothing rewinds the trail, and that is the "
      "semantics rather than an omission. Only retention discriminates the "
      "invariant -- a cut that wrongly rewound the trail would get the UNDO "
      "half right by accident."),
 cell("(?:(?=(a))x|(a))", LA, [("ab", 0), ("ax", 0)],
      "C3 -- THE UNDO HALF. The first branch captures \"a\" inside the "
      "assertion and then FAILS on `x`; the ordinary trail rewind puts g1 "
      "back to UNSET, and g2 takes the match."),
 cell("(?!(a)x)ab", LA, [("ab", 0), ("axb", 0)],
      "C2 -- A NEGATIVE assertion's captures are DISCARDED. The body "
      "captured \"a\" and then failed on `x`; reaching the body-failed "
      "continuation means the fail label has already rewound the trail to "
      "that frame's mark. No snapshot machinery exists, or is needed."),
 cell("(?!(a)x)(a)", LA, [("ab", 0)],
      "...and this cell proves the answer is READ rather than truncated by "
      "libpcre2's trailing-unset rule: g1 unset, g2 (0,1). §3.3 names it."),
 cell("(?=(a)(b))ab", LA, [("ab", 0), ("ac", 0)],
      "TWO groups inside one assertion, both retained."),
 cell(r"(?=(a))\1", LA + ",backrefs", [("a", 0), ("b", 0)],
      "RETENTION FEEDING A BACKREFERENCE -- the sharpest form of C1, because "
      "the reference can only resolve if the capture survived the cut and "
      "the position restore."),
 cell("(?=(?=(a))a)ab", LA, [("ab", 0)],
      "A capture two assertions deep, retained through both."),
 cell("^(?=(a))*a$", LA, [("a", 0)],
      "C4 -- a QUANTIFIED lookaround's captures behave like ONE iteration."),
 cell("^(?=(a))*b$", LA, [("b", 0)],
      "...and when the assertion never succeeds, the group is UNSET."),
 cell("^(?!(a))*b$", LA, [("b", 0)],
      "...the negative form's group is unset for the other reason: it was "
      "written and then rewound."),
 cell("(?=(a)|(b))[ab]", LA, [("a", 0), ("b", 0)],
      "WHICH BRANCH the assertion committed to is observable in the groups."),
]

# ===========================================================================
#  quantified.rxt — `(?=a)*` and family, including the empty-iteration cells
# ===========================================================================
QUANTIFIED = [
 cell("^(?=a)*a$", LA, [("a", 0), ("b", 0)],
      "THE EMPTY-ITERATION CELL, and it is here because it must TERMINATE. "
      "A lookaround consumes nothing on every path, so `vm_nullable` MUST "
      "answer true for it or the star loses its empty-iteration guard. The "
      "failure is NOT a hang: every VM artifact carries a step budget, so "
      "the lost guard BURNS it and returns PCREC_ERR_STEPS. Sabotage row "
      "S127, whose detector has to notice an ERROR return."),
 cell("^(?:(?=a))*a$", LA, [("a", 0)], "The same, one group deeper."),
 cell("^(?:(?=a)|b)*a$", LA, [("a", 0), ("ba", 0)],
      "The same with a CONSUMING alternative beside the zero-width one."),
 cell("^(?:(?!x))*a$", LA, [("a", 0), ("x", 0)],
      "The same for the NEGATIVE form, whose body-failed frame is what the "
      "iteration keeps re-pushing."),
 cell("^(?:(?=(a)))*a$", LA, [("a", 0)],
      "The same with a CAPTURE inside, so the guard and the trail interact."),
 cell("(?=a)*a", LA, [("a", 0), ("ba", 0)],
      "§2.6: quantified lookaround SHIPS -- all fourteen forms compile in "
      "BOTH oracles, which REFUTES the charter's expectation that python "
      "lacks it (design §7, G8). Marking these `# pcre2-only` would have "
      "thrown a working oracle away."),
 cell("(?=a)+a", LA, [("a", 0), ("b", 0)], None),
 cell("(?=a)?a", LA, [("a", 0), ("b", 0)], None),
 cell("(?=a){2}a", LA, [("a", 0)], None),
 cell("(?=a){0,3}a", LA, [("a", 0)], None),
 cell("(?!a)?b", LA, [("b", 0), ("ab", 0)], None),
 cell("(?!a)*b", LA, [("b", 0)], None),
 cell("(?=a)*+a", LA + ",atomic-groups", [("a", 0)],
      "The POSSESSIVE spelling, which desugars to `A_ATOMIC(A_REP(A_LOOK))` "
      "-- a cut ABOVE an assertion that has a cut of its own."),
 cell("(?=a)*?a", LA, [("a", 0)], "The LAZY spelling."),
 cell("((?=a)*)a", LA, [("a", 0)],
      "A quantified assertion inside a CAPTURE: the group spans the empty "
      "run of iterations."),
 cell("(?:(?=a)a)+", LA, [("aa", 0), ("ab", 0)],
      "An assertion inside a CONSUMING loop -- the iteration is not empty, "
      "so this exercises the ordinary rung with the marks re-set per pass."),
]

# ===========================================================================
#  nonatomic_ahead.rxt — `(?*` only (design §10.2; wave B+C's half of the
#  split R33 C2-9 made). python `re` has no `(?*` at all (G5), so every block
#  here is expected to compute as `# pcre2-only` -- expected, still computed.
# ===========================================================================
NONATOMIC = [
 cell(r"(?*(a|ab))\1$", LA + ",backrefs", [("abab", 0), ("aa", 0)],
      "§2.2's ATOMICITY DISCRIMINATOR, the NON-ATOMIC half, and the cell "
      "that fixes `(?*` as a construct rather than a spelling. On \"abab\" "
      "it is (2,4) where `(?=(a|ab))\\1$` -- lookahead.rxt's own cell -- is "
      "NOMATCH: the body RETRIES, finds \"ab\", and \\1 ends the subject. "
      "Sabotage row S131 always emits the cut and this cell goes red."),
 cell("(?*a)b", LA, [("ab", 0), ("bb", 0)],
      "The plain shape: same answer as `(?=a)b`, which is the CONTROL that "
      "the two differ only where a retry is possible."),
 cell("(?*(a+)b)a+b", LA, [("aab", 0), ("aaab", 0)],
      "§3.2.1's ROW 3, BY NAME. The scoping is a property of the OVERLAP and "
      "NOT of the cut, so deleting `vm_cut` for this arm does NOT delete it "
      "-- an implementer following \"the atomic shape MINUS the cut\" would "
      "lose exactly this cell (it becomes NOMATCH)."),
 cell("a(?*b)bc", LA, [("abc", 0), ("abd", 0)],
      "Non-atomic in the MIDDLE: the cursor restore is the same line."),
 cell("(?*(a))a", LA, [("a", 0)],
      "Captures inside a non-atomic assertion are retained exactly as the "
      "atomic form's are -- the retention is the trail's, not the cut's."),
 cell("(?*x)a", LA, [("a", 0)],
      "A body that cannot succeed fails the whole assertion: the positive "
      "form is positive whether or not it is atomic."),
 cell("(?*a)*a", LA, [("a", 0)],
      "QUANTIFIED non-atomic, so the empty-iteration guard is exercised on "
      "the arm that allocates NO mark slot."),
 cell("(?=(?*a)a)ab", LA, [("ab", 0)],
      "A non-atomic assertion nested inside an ATOMIC one: the outer cut "
      "discards the inner body's live choice points, which is correct and "
      "is what makes `(?=` atomic in the first place."),
 cell("(?*(?=a)a)ab", LA, [("ab", 0)],
      "...and the other nesting order."),
 cell("(?*ab)abc", LA, [("abc", 0), ("abd", 0)], None),
]

# ===========================================================================
#  lookbehind.rxt — `(?<=` and `(?<!`: fixed bodies, SAME-length alternatives
#  (design §10.2; wave D). EQUAL widths only: python `re` requires every
#  lookbehind alternative to have the SAME length (G10 — the divergence is
#  about DIFFERING widths, not about alternation at all), so this file stays
#  python-verifiable and `lookbehind_widths.rxt` next door carries the cells
#  that are not. Computed, still — a hand marking is what R32 C3 caught.
# ===========================================================================
LOOKBEHIND = [
 cell("(?<=a)b", LA, [("ab", 0), ("b", 0), ("xb", 0), ("a", 0), ("aab", 0)],
      "THE SHAPE ITSELF, and the second subject is design §3.4's B5 by name: "
      "`(?<=a)b` on \"b\" is NOMATCH because the START-OF-SUBJECT GUARD "
      "(`scan_position < k`) fires before the back-step is ever called. Its "
      "negative twin below answers (0,1) on the same subject, which is what "
      "makes the guard's ANSWER observable rather than just its existence."),
 cell("(?<=abc)x", LA, [("abcx", 0), ("bcx", 0), ("x", 0), ("abcxy", 0)],
      "A MULTI-CHARACTER fixed body. \"bcx\" is B5's second cell: two "
      "characters precede the `x` and the branch needs three."),
 cell("(?<=[ab][cd])x", LA, [("acx", 0), ("bdx", 0), ("aax", 0), ("cx", 0)],
      "CLASSES behind the cursor. Width 2, fixed, and the body is emitted by "
      "`vm_emit` unchanged -- a class test inside a lookbehind is the same "
      "one-line class test it is anywhere else (§3.5(3))."),
 cell("(?<=a{3})x", LA, [("aaax", 0), ("aax", 0), ("aaaax", 0)],
      "AN EXACT COUNT IS FIXED WIDTH, and it is the cell §3.4's follow ruling "
      "turns on: `a{3}` is lowered as an `A_REP` that takes a cursor rung "
      "with an MRL clamp whose literal MOVES with the follow, so a lookbehind "
      "whose body was left unscoped would get a different bound here. F3 "
      "measured exactly this pair."),
 cell("(?<=(?:ab){2})x", LA, [("ababx", 0), ("abx", 0), ("ababab", 0)],
      "...and the SHARPER half of that pair (R33's verifier's own cell): an "
      "exact count over a GROUP is fixed width too, and a reader is likelier "
      "to think a group is not a rung than to think `a{3}` is not."),
 cell("(?<=ab|cd)x", LA, [("abx", 0), ("cdx", 0), ("aex", 0), ("bx", 0),
                          ("x", 0)],
      "TWO BRANCHES OF THE SAME WIDTH -- the alternation cell python "
      "ACCEPTS (G10). Each branch gets its own back-step and its own retry "
      "frame; branch 1 failing retreats into branch 2 through the ordinary "
      "fail label."),
 cell("(?<=ab|cd|ef)x", LA, [("abx", 0), ("cdx", 0), ("efx", 0), ("ghx", 0)],
      "THREE same-width branches, so the chain is longer than the two-branch "
      "shape a reader would generalise from: the LAST branch pushes no retry "
      "frame at all, and only a third branch shows that the middle one does."),
 cell("(?<!a)b", LA, [("ab", 0), ("b", 0), ("xb", 0), ("bb", 0)],
      "THE NEGATIVE FORM, and \"b\" is B5's discriminating subject: (0,1) "
      "here where the positive form is NOMATCH. This is also the polarity on "
      "which a wrong width would be a FALSE MATCH rather than a decline, "
      "which is why §3.4's end-check returns HARD on this arm (ASK 2)."),
 cell("(?<!ab|cd)x", LA, [("abx", 0), ("cdx", 0), ("aex", 0), ("x", 0)],
      "The negative form with same-width branches: the assertion holds only "
      "when EVERY branch fails, which is what running out of branches means "
      "-- ordinary failure into the pushed `L_neg_ok` frame (§3.3)."),
 cell("(?<=)x", LA, [("x", 0), ("ax", 0), ("y", 0)],
      "§2.6's DEGENERATE BODY, behind. An empty body always succeeds, so the "
      "positive form is a NO-OP -- and it needs no special case: the body is "
      "an A_EMPTY of width 0, ONE branch, and the back-step steps back zero "
      "characters."),
 cell("(?<!)x", LA, [("x", 0), ("ax", 0)],
      "...and the negative form with an empty body is `(*FAIL)`."),
 cell("a(?<=a)b", LA, [("ab", 0), ("ac", 0), ("xab", 0)],
      "A lookbehind in the MIDDLE, where the entry position is not the "
      "attempt position -- the back-step is relative to the CURSOR, and the "
      "end-check is what proves the body landed back on it."),
 cell("(?<=(a)(b))c", LA, [("abc", 0), ("axc", 0)],
      "CAPTURES INSIDE A LOOKBEHIND, retained on success exactly as a "
      "lookahead's are (§3.5(1) measures this cell: g1=(0,1) g2=(1,2)). It "
      "is also the first reason the body cannot be a reverse DFA: the "
      "reverse pass is over the CAPTURE-ERASED pattern (D31) and none of "
      "this survives erasure."),
 cell("(?<=(aa)|(ab))c", LA, [("aac", 0), ("abc", 0), ("bac", 0)],
      "BRANCH ORDER AT EQUAL WIDTHS, which is the half of §2.4 level 1 that "
      "python can also verify: written order decides, and WHICH branch "
      "committed is observable in the groups. The differing-width half is in "
      "lookbehind_widths.rxt and is `# pcre2-only`."),
 cell("(?<=a)", LA, [("a", 0), ("ba", 0), ("b", 0), ("", 0)],
      "A lookbehind as the WHOLE pattern: a zero-width match AFTER an `a`, "
      "so the reported span is empty and its position is the assertion's."),
 cell("(?<=a(?=b))ab", LA, [("ab", 0), ("ac", 0), ("xab", 0)],
      "A NESTED LOOKAHEAD INSIDE A LOOKBEHIND, and it is width 1 -- a nested "
      "lookaround contributes 0 to both `minw` and `maxw` (§3.1(d)), so the "
      "branch stays FIXED and ships. It is also §3.2.1's uniform-scoping "
      "case: the inner assertion's cursor runs AHEAD of the entry position, "
      "so the lookbehind's own follow arithmetic does not hold inside it and "
      "the scoping has to be unconditional."),
 cell("(?<=(?<=a)b)c", LA, [("abc", 0), ("xbc", 0), ("bc", 0)],
      "A LOOKBEHIND INSIDE A LOOKBEHIND -- two position slots live at once, "
      "and the outer end-check must compare against the OUTER entry."),
 cell("(?<=a(?!b))x", LA, [("ax", 0), ("abx", 0), ("x", 0)],
      "A nested NEGATIVE lookahead inside a lookbehind: still width 1."),
 cell("(?<=a)b|(?<=bc)d", LA, [("abd", 0), ("bcd", 0), ("ab", 0), ("xcd", 0)],
      "One lookbehind per ALTERNATION BRANCH, so the two allocate different "
      "slots and neither's end-check may read the other's."),
 cell("((?<=a)b)+", LA, [("ab", 0), ("abb", 0), ("b", 0), ("abab", 0)],
      "A lookbehind inside a CAPTURE inside a QUANTIFIER: the assertion is "
      "re-entered per iteration and its slots are re-set on every entry."),
 cell("(?<=a)*b", LA, [("ab", 0), ("b", 0)],
      "A QUANTIFIED lookbehind, so the EMPTY-ITERATION guard is exercised "
      "behind as well as ahead: `vm_nullable` answers true for A_LOOK "
      "whatever its direction, and if it did not this cell would burn the "
      "step budget rather than hang (S127)."),
 cell("(?>(?<=a)b)", LA + ",atomic-groups", [("ab", 0), ("b", 0)],
      "A lookbehind inside an ATOMIC GROUP: two cut marks live at once, and "
      "the outer cut must not discard frames the inner one still owns."),
 cell("(?<=(?>ab))c", LA + ",atomic-groups", [("abc", 0), ("bc", 0)],
      "...and the other nesting order, an atomic group inside a lookbehind. "
      "Fixed width 2, because the cut removes MATCHES and never BYTES."),
 cell("(?<=a)(?<=ab)c", LA, [("abc", 0), ("xbc", 0), ("bc", 0)],
      "TWO LOOKBEHINDS IN SEQUENCE at the same position, of DIFFERENT depths "
      "-- design §2.3's B4 composite (`PCRE2_INFO_MAXLOOKBEHIND` is the MAX, "
      "not the sum). Independent slots, independent end-checks."),
 cell("(?<=ab)(?<=b)c", LA, [("abc", 0), ("bc", 0)],
      "...and the same pair written deepest-first."),
 cell("(?<=\\w)x", LA + ",classes", [("ax", 0), ("x", 0), (".x", 0), ("9x", 0)],
      "THE ASSERTION FAMILY's OWN BODY. `\\b` expands to "
      "`(?:(?<!\\w)(?=\\w)|(?<=\\w)(?!\\w))` and this is half of it -- one "
      "class, fixed width 1. §2.5's rule is exactly big enough for the whole "
      "family and that is MEASURED rather than arranged (§6.1)."),
 cell("(?<!\\w)x", LA + ",classes", [("ax", 0), ("x", 0), (".x", 0)],
      "...and the other half."),
 cell("(?<=\\n)x", LA, [("\nx", 0), ("x", 0), ("ax", 0)],
      "The third body the family uses, and the one `(?m)^`'s expansion "
      "needs."),
 cell("(?<=[^a])b", LA, [("xb", 0), ("ab", 0), ("b", 0)],
      "A NEGATED class behind the cursor."),
 cell("(?<=a{2})b", LA, [("aab", 0), ("ab", 0), ("aaab", 0)],
      "An exact count of 2, the smallest body where the guard and the "
      "back-step disagree about how much they each rule out."),
 cell("(?<!a{2})b", LA, [("aab", 0), ("ab", 0), ("b", 0)],
      "...negated, where a wrong width would be a FALSE MATCH."),
 cell(r"(?<=a)\Kb", "assertions," + LA, [("ab", 0), ("b", 0)],
      "§2.7's FOUR COMPILING CELLS, the lookbehind member. The refusal is "
      "about `\\K` INSIDE the assertion; once it has closed, `\\K` is the "
      "ordinary construct module `assertions` already ships. A check that "
      "latched on \"a lookaround was seen\" would wrongly refuse this."),
 cell(r"(?<=\Ga)b", "assertions," + LA, [("ab", 0), ("xab", 0)],
      "`\\G` INSIDE A LOOKBEHIND means what it means outside one -- an "
      "absolute position test against `startpos` -- and needs nothing from "
      "this module (§3.8). The startpos axis for it is in startpos.rxt."),
]

# ===========================================================================
#  lookbehind_widths.rxt — DIFFERENT-length branches (design §10.2; G1's
#  cells). `# pcre2-only` by construction: python `re` refuses every pattern
#  here with "look-behind requires fixed-width pattern", and the divergence is
#  about DIFFERING widths rather than about alternation (G10). Computed, not
#  declared -- the marking is what this generator exists for.
# ===========================================================================
LOOKBEHIND_WIDTHS = [
 cell("(?<=a|bc)x", LA, [("ax", 0), ("bcx", 0), ("cx", 0), ("x", 0),
                         ("zbcx", 0), ("abcx", 0)],
      "THE HEADLINE CELL of §2.5: TWO top-level branches, each FIXED, of "
      "widths 1 and 2 -- legal in PCRE2, an ERROR in python (G1), and pcrec "
      "SHIPS it. \"cx\" is design §3.4's B5 cell that shows the branches are "
      "INDEPENDENT: neither `a` nor `bc` precedes the `x`, so the assertion "
      "fails through both. Its near-twin `(?<=(a|bc))x` -- ONE branch of "
      "width 1..2 -- is REFUSED and is in refused.rxt; the difference "
      "between those two lines is exactly the level-1/level-2 split §2.4 "
      "measured, and it is the thing in this module most likely to be read "
      "as a defect."),
 cell("(?<=a|bc|def)x", LA, [("ax", 0), ("bcx", 0), ("defx", 0), ("efx", 0),
                             ("x", 0)],
      "THREE branches of three DIFFERENT widths, so the chain is not the "
      "two-branch shape a reader generalises from and the middle branch's "
      "retry frame is load-bearing."),
 cell("(?<!a|bc)x", LA, [("ax", 0), ("bcx", 0), ("cx", 0), ("x", 0)],
      "The rule is POLARITY-BLIND (§2.3's own row). And this is the arm "
      "where a wrong per-branch width is a FALSE MATCH rather than a "
      "decline, which is why the end-check returns HARD here -- sabotage row "
      "S136 carries this spelling for exactly that reason."),
 cell("(?<=(a)|(aa))c", LA, [("aac", 0), ("ac", 0), ("c", 0)],
      "§2.4 LEVEL 1, MEASURED, AND IT IS THE SHARPEST CELL IN THE MODULE: "
      "top-level branches are tried in WRITTEN ORDER, so on \"aac\" branch 1 "
      "wins and g1=(1,2) -- the SHORTER match, written first. Compare the "
      "next cell, which is the same two branches the other way round and "
      "answers with the LONGER one. An implementation that ordered branches "
      "by width would get exactly one of these two right."),
 cell("(?<=(aa)|(a))c", LA, [("aac", 0), ("ac", 0)],
      "...the same two branches reversed: branch 1 wins again, g1=(0,2), the "
      "LONGER match. Written order, not length."),
 cell("(?<=(a)|(aa)|(aaa))c", LA, [("aaac", 0), ("aac", 0)],
      "Three widths, shortest written first."),
 cell("(?<=(aaa)|(aa)|(a))c", LA, [("aaac", 0), ("ac", 0)],
      "...and longest written first. Both answer through branch 1."),
 cell("(?<=x|abc)y", LA, [("xy", 0), ("abcy", 0), ("y", 0), ("bcy", 0)],
      "Widths 1 and 3, so the guard rules out the long branch on subjects "
      "where the short one is still viable."),
 cell("(?<=ab|c)x", LA, [("abx", 0), ("cx", 0), ("bx", 0), ("x", 0)],
      "The long branch written FIRST, which is the order that makes the "
      "guard fire on branch 1 and fall through to branch 2 rather than "
      "reaching the back-step."),
 cell("(?<=a|bc)*x", LA, [("ax", 0), ("bcx", 0), ("x", 0)],
      "A QUANTIFIED differing-width lookbehind: the empty-iteration guard "
      "and the per-branch retry frames at the same time."),
 cell("a(?<=a|xbc)b", LA, [("ab", 0), ("xbcb", 0)],
      "Mid-pattern, so the entry position is not the attempt position and "
      "the two branches step back from a CURSOR rather than from 0."),
 cell("(?<=|a)x", LA, [("x", 0), ("ax", 0), ("bx", 0)],
      "A ZERO-WIDTH BRANCH BESIDE A CONSUMING ONE, and it is here because it "
      "FOUND A DEFECT. Width 0 is a legal fixed width, so §2.5 admits this "
      "body -- and the emitted start-of-subject guard for it was "
      "`scan_position < 0`, an always-false comparison on a `size_t` that "
      "gcc REFUSES under the harness's `-Wall -Wextra -Werror` generated "
      "build (`-Wtype-limits`). The guard is now emitted only for k > 0, "
      "which is the condition being unsatisfiable rather than an exception "
      "for one body shape. Branch 1 is width 0 and always succeeds, so the "
      "assertion is a no-op and the second branch is never reached."),
 cell("(?<=a|)x", LA, [("x", 0), ("ax", 0)],
      "...and the zero-width branch written SECOND, which is the order that "
      "makes it the LAST branch -- the arm that emits `goto rx_fail` rather "
      "than a jump to the next branch, and therefore a different guard site "
      "from the cell above."),
 cell("(?<!a|)x", LA, [("x", 0), ("ax", 0)],
      "...and the negative form, where a zero-width branch that always "
      "succeeds makes the whole assertion `(*FAIL)`."),
]

# ===========================================================================
#  startpos.rxt — `ms`/`ns` cells over a lookbehind (design §10.2, §3.8)
#
#  THE AXIS A STARTPOS-BLIND CORPUS WOULD MISS ENTIRELY. A lookbehind READS
#  SUBJECT BYTES BEFORE `startpos`, which is a CONTRACT question rather than a
#  syntax one, and both oracles agree on it. Sabotage row S135 clamps the
#  emitted guard to `scan_position - startpos < k` and its prediction is that
#  the `ms` cells here go red while every startpos-0 cell in the tree stays
#  green -- so a corpus without this file could not falsify it.
# ===========================================================================
STARTPOS = [
 cell("(?<=a)b", LA, [("ab", 1), ("ab", 0), ("aab", 2), ("aab", 1),
                      ("b", 0), ("xb", 1)],
      "§3.8's MEASURED CELL, BY NAME: `(?<=a)b` on \"ab\" AT STARTPOS 1 "
      "MATCHES (1,2). The assertion is evaluated against the REAL SUBJECT, "
      "not against the search window -- the VM's `subject` pointer is the "
      "whole subject and `scan_position` is an ABSOLUTE offset, so the "
      "back-step reaches before `startpos` with no extra plumbing. The "
      "startpos-0 cells beside it are the control that says this file is "
      "about the window and not about the pattern."),
 cell("(?<!a)b", LA, [("ab", 1), ("ab", 0), ("b", 0), ("xb", 1)],
      "...and the NEGATIVE half of the same measurement, which is the one "
      "that makes the fact unambiguous: at startpos 1 on \"ab\" this does "
      "NOT match. A clamped guard would make the `a` invisible and the "
      "negative assertion would HOLD -- a FALSE MATCH at exactly the "
      "position the positive cell above reports a real one."),
 cell("(?<=abc)x", LA, [("abcx", 3), ("abcx", 0), ("bcx", 1), ("bcx", 0)],
      "A THREE-character back-step reaching three bytes before the window "
      "start, and the shorter subject where it runs off the START OF THE "
      "SUBJECT instead -- the guard's real job, which is not the same "
      "question as the window's."),
 cell("(?<=ab)c", LA, [("abc", 2), ("abc", 0), ("abc", 1)],
      "The back-step landing EXACTLY on offset 0, the boundary case between "
      "the guard rejecting and the body running."),
 cell("(?<=ab|cd)x", LA, [("abx", 2), ("cdx", 2), ("abx", 0), ("cdcdx", 3)],
      "Multi-branch under a startpos, so EVERY branch's back-step is "
      "absolute rather than only the first one's."),
 cell("(?<=a|bc)x", LA, [("ax", 1), ("bcx", 2), ("bcx", 1), ("abcx", 2)],
      "DIFFERING widths under a startpos: the two branches reach different "
      "distances behind the same window start, which is the cell a clamp "
      "that happened to be right for width 1 would still fail."),
 cell(r"(?<=\Ga)b", "assertions," + LA, [("ab", 1), ("ab", 0), ("xab", 1),
                                         ("xab", 2)],
      "`\\G` INSIDE the lookbehind, which is the OTHER absolute-position "
      "reading in the same construct: `\\G` tests against `startpos` while "
      "the back-step ignores it, so this cell is where the two would be "
      "confused if either were wrong (§3.8)."),
 cell("a(?<=a)b", LA, [("aab", 1), ("ab", 0), ("aab", 0)],
      "A mid-pattern lookbehind under a startpos: the entry position is "
      "neither 0 nor `startpos`."),
 cell("(?<=(a)|(bc))x", LA, [("ax", 1), ("bcx", 2), ("abcx", 1)],
      "Captures inside a differing-width lookbehind reached from a window "
      "start -- the group spans are ABSOLUTE offsets too, and a clamped "
      "back-step would report them shifted rather than merely miss."),
]

# ===========================================================================
#  nonatomic_behind.rxt — `(?<*` (design §10.2, §3.6; wave D's half of the
#  `nonatomic.rxt` split R33 C2-9 made). `# pcre2-only`: python has no `(?<*`
#  at all (G5), and the two `(?<=` control cells here are differing-width
#  bodies python also refuses (G1). Computed, still.
# ===========================================================================
NONATOMIC_BEHIND = [
 cell(r"(?<*(a)|(ba))c\2", LA + ",backrefs", [("bacba", 0), ("bac", 0)],
      "§3.6's MEASURED WITNESS, BY NAME, and it is the ONE cell that goes "
      "red if the per-branch retry frames are cut. On \"bacba\" it is (2,5) "
      "with g1 UNSET and g2=(0,2): the assertion first succeeds through "
      "branch 1, the follow `\\2` fails because g2 is unset, and the failure "
      "RETREATS INTO BRANCH 2 -- re-running the back-step with THAT branch's "
      "own `k` and undoing branch 1's captures through the ordinary trail "
      "rewind. In the atomic form those frames are discarded by the cut; "
      "here they are LOAD-BEARING."),
 cell(r"(?<=(a)|(ba))c\2", LA + ",backrefs", [("bacba", 0), ("bac", 0)],
      "...AND ITS ATOMIC CONTROL, which is the half that makes the pair a "
      "measurement rather than an assertion: the same body one character "
      "different in the spelling is NOMATCH on the same subject, because "
      "`(?<=` keeps branch 1 and never reconsiders. Sabotage row S131 emits "
      "the cut on both and this pair collapses; S122 emits it on neither and "
      "it collapses the other way."),
 cell(r"(?<*(ba)|(a))c\2", LA + ",backrefs", [("baca", 0), ("bacba", 0)],
      "§3.6's F4 fourth row: the branch order reversed, so the retry goes "
      "from the LONGER branch to the shorter one."),
 cell(r"(?<*(a)|(ba))c", LA + ",backrefs", [("bac", 0), ("bacba", 0)],
      "F4's third row -- NO FOLLOW to force a retry, so the non-atomic form "
      "answers exactly as the atomic one would. It is the control that says "
      "the previous cells measure RE-ENTRY and not merely `(?<*`."),
 cell("(?<*a)b", LA, [("ab", 0), ("b", 0), ("xb", 0)],
      "The plain shape: the same answer as `(?<=a)b`, which is the CONTROL "
      "that the two spellings differ only where a retry is possible."),
 cell("(?<*ab)c", LA, [("abc", 0), ("bc", 0)],
      "A multi-character non-atomic body."),
 cell("(?<*a|bc)x", LA, [("ax", 0), ("bcx", 0), ("cx", 0), ("abcx", 0)],
      "DIFFERING widths, non-atomic: the branch frames stay live AND the "
      "widths differ, which is the combination §3.6's drawing exists for. "
      "NO MARK SLOT is allocated here at all -- that is how a reader tells "
      "the two families apart in the emitted C and in `--emit-ir`."),
 cell("(?<*a)*b", LA, [("ab", 0), ("b", 0)],
      "QUANTIFIED non-atomic behind, so the empty-iteration guard is "
      "exercised on the arm that allocates no mark."),
 cell("(?<=(?<*a)b)c", LA, [("abc", 0), ("bc", 0)],
      "A non-atomic lookbehind nested inside an ATOMIC one: the outer cut "
      "discards the inner body's live choice points, which is correct and is "
      "what makes `(?<=` atomic in the first place."),
 cell("(?<*(?<=a)b)c", LA, [("abc", 0), ("bc", 0)],
      "...and the other nesting order."),
 cell("(?<*(a))a", LA, [("aa", 0), ("a", 0)],
      "Captures inside a non-atomic lookbehind are retained exactly as the "
      "atomic form's are -- the retention is the TRAIL's, not the cut's."),
]

# ===========================================================================
#  workbudget.rxt — §3.7's LONG-SUBJECT LEADING multi-branch lookbehind
#  (R33 C1-6), so the `n·Σk_i` work-charge shape is MEASURED rather than
#  reasoned about. Every branch is width 2, so python verifies it (G10).
# ===========================================================================
_WB_LONG_NOMATCH = "z" * 1000
_WB_LONG_MATCH   = "z" * 997 + "abx"

WORKBUDGET = [
 cell("(?<=ab|cd|ef|gh)x", LA,
      [(_WB_LONG_NOMATCH, 0), (_WB_LONG_MATCH, 0), ("abx", 0), ("x", 0),
       ("ghx", 0)],
      "§3.7's CHARGE SHAPE, MEASURED. A LEADING multi-branch lookbehind is "
      "charged `RX_CHARGE_WORK(k_i)` once per branch TRIED per candidate "
      "start, and `rx_search`'s bump-along walks every position -- so one "
      "search over an n-byte subject charges up to `n · Σk_i`, here 8 per "
      "position. The first subject is 1000 bytes with NO match, so every "
      "position is tried and every branch is charged; the second is the same "
      "length with the match at the very end, so the same walk happens and "
      "then succeeds. Against `VM_DEFAULT_WORK_BUDGET = 1000000000` four "
      "branches summing to 20 reach the budget at a ~50 MB subject, which is "
      "`PCREC_ERR_WORK` where PCRE2 matches; this file measures the SHAPE at "
      "a size a corpus can carry, and the short cells beside it are the "
      "control that the answer does not depend on the length."),
 cell("(?<=ab|cd|ef|gh)x|q", LA,
      [(_WB_LONG_NOMATCH, 0), ("q" + "z" * 500, 0)],
      "THE SAME LEADING LOOKBEHIND WITH AN ESCAPE HATCH, which is the cell "
      "that separates \"the walk is charged\" from \"the walk happens at "
      "all\": the second subject matches at offset 0 through the OTHER "
      "branch, so almost none of the charge is incurred, while the first "
      "still pays for every position."),
 cell("(?<!ab|cd|ef|gh)x", LA,
      [(_WB_LONG_NOMATCH, 0), (_WB_LONG_MATCH, 0)],
      "The NEGATIVE form of the same shape: every branch is still tried at "
      "every position -- running out of branches is how the assertion HOLDS "
      "-- so the negative arm pays the full `n · Σk_i` on the subject where "
      "the positive one pays it too, and MATCHES where the positive one does "
      "not."),
]

# ===========================================================================
#  refused.rxt — the `perr` cells this wave owns
# ===========================================================================
REFUSED = [
 cell(r"(?=a\K)x", "assertions," + LA, None,
      "§2.7, AND THE AGREEMENT IS NOT AGREEMENT (design §7, G6). libpcre2 "
      "refuses this with err 199 BECAUSE `\\K` is not allowed in a "
      "lookaround; python3 `re` refuses it because it has no `\\K` AT ALL "
      "(\"bad escape\"). A reader must not take the matching verdicts as two "
      "oracles confirming one rule. pcrec's refusal is §2.7's parse-time "
      "check in `pcrec_laport_group`, and Frank ruled it PERMANENT on "
      "2026-08-23 -- the EXTRA bit that would enable the old semantics is "
      "not adopted and is not to be proposed from here.",
      perr=True),
 cell(r"(?!a\K)x", "assertions," + LA, None, None, perr=True),
 cell(r"(?*a\K)x", "assertions," + LA, None, None, perr=True),
 cell(r"(?=(a\K))x", "assertions," + LA, None,
      "THE THREE CELLS AN IMMEDIATE-CHILDREN CHECK WOULD MISS (R33 C1-7), "
      "and they are why `la_has_kreset` is a recursive walk rather than a "
      "look at the body node: `\\K` inside a nested CAPTURE, inside a nested "
      "non-capturing GROUP, and inside a nested LOOKAROUND.",
      perr=True),
 cell(r"(?=a(?:\K))x", "assertions," + LA, None, None, perr=True),
 cell(r"(?=(?:(?=\K)))x", "assertions," + LA, None, None, perr=True),
 cell(r"(?=\Ka)x", "assertions," + LA, None, None, perr=True),
 # ---- [WAVE D] §2.5's VARIABLE-WIDTH REFUSALS ----------------------------
 # A CAPABILITY LIMIT, and worded as one. The construct is REAL and the module
 # is ENABLED, so this is not "requires module 'lookaround'" -- what is missing
 # is the longest-first step-back loop §2.5 charters and this module does not
 # build. Every cell below is a `perr` for pcrec; libpcre2's own verdict is
 # recorded per block by the generator and it DIFFERS across the family, which
 # is the point: on the unbounded bodies pcrec AGREES with PCRE2 (err 125), and
 # on the bounded ones PCRE2 COMPILES what pcrec refuses.
 cell("(?<=(a|bc))x", LA, None,
      "THE CELL §2.5 EXISTS TO DISTINGUISH, and its near-twin `(?<=a|bc)x` "
      "SHIPS (lookbehind_widths.rxt). This is ONE top-level branch of width "
      "1..2; that is TWO branches of fixed widths 1 and 2. The difference is "
      "exactly §2.4's level-1/level-2 split: within ONE branch PCRE2 tries "
      "the step-back LENGTH longest-first, over a range whose ends come from "
      "the new `pcrec_maxw` analysis, and that loop runs in the OPPOSITE "
      "direction to every other ordered choice the emitter makes. §2.5 gives "
      "three reasons to charter it rather than ship it in the same wave as "
      "the analysis. THIS ASYMMETRY IS THE MOST LIKELY THING IN THIS MODULE "
      "TO BE CALLED A DEFECT and §12 P-3 says how to refute it.",
      perr=True),
 cell("(?<=a{2,3})x", LA, None,
      "A BOUNDED VARIABLE body: PCRE2 compiles it (capped by the compile "
      "context's `max_varlookbehind`, whose default bisects to 255), python "
      "refuses it, pcrec refuses it. G2's cell.", perr=True),
 cell("(?<=a?)x", LA, None, "Width 0..1 -- the smallest variable body there "
      "is, and still variable.", perr=True),
 cell("(?<=a{0,3})x", LA, None, None, perr=True),
 cell("(?<=a*)x", LA, None,
      "AND HERE pcrec AGREES WITH PCRE2, which is err 125 \"length of "
      "lookbehind assertion is not limited\". The refusals in this family are "
      "not one verdict: an unbounded body is refused by BOTH, a bounded one "
      "only by pcrec, and a block that did not record which would let a "
      "reader take agreement for confirmation.", perr=True),
 cell("(?<=a+)x", LA, None, None, perr=True),
 cell("(?<=a{2,})x", LA, None, None, perr=True),
 cell("(?<=a*?)x", LA, None, None, perr=True),
 cell("(?<=a*+)x", LA + ",atomic-groups", None,
      "The POSSESSIVE spelling of the same unbounded body: the rule is blind "
      "to the quantifier's strategy, because `pcrec_maxw` is.", perr=True),
 cell("(?<=(?>a*))x", LA + ",atomic-groups", None,
      "...and the ATOMIC-GROUP spelling. The cut removes MATCHES, never "
      "BYTES, so the width is unchanged and still unbounded.", perr=True),
 cell("(?<=(?:a|bc)d)x", LA, None,
      "ONE branch whose own INTERIOR alternation makes it variable (2..3). "
      "A `|`-counting scanner would read this as two branches and accept it, "
      "which is why the branch split comes from `AltInfo.nbr` -- the count "
      "the LOOP THAT DROVE THE PARSE produced -- and never from the text.",
      perr=True),
 cell("(?<=((a|bc)d))x", LA, None, None, perr=True),
 cell("(?<!a*)x", LA, None,
      "THE RULE IS POLARITY-BLIND (§2.3's own row): the same body behind a "
      "negative assertion is refused for the same reason.", perr=True),
 cell("(?<*a*)x", LA, None,
      "...and ATOMICITY-BLIND.", perr=True),
 cell("(?<!(a|bc))x", LA, None, None, perr=True),
 cell("(?<*(a|bc))x", LA, None, None, perr=True),
 cell(r"(a)(?<=\1)x", LA + ",backrefs", None,
      "A BACKREFERENCE INSIDE A LOOKBEHIND, and pcrec's refusal here is "
      "CONSERVATIVE rather than forced: PCRE2 accepts it (maxlb 1) because "
      "the referenced group is fixed-width, and so could pcrec -- but a "
      "backreference's width is decided at MATCH time by which alternative "
      "the referenced group took, so `pcrec_maxw` answers "
      "PCREC_W_UNBOUNDED for A_BREF and this refusal follows. §11's "
      "follow-on row carries the refinement.", perr=True),
 cell(r"(a|bc)(?<=\1)x", LA + ",backrefs", None,
      "...and the case that is NOT conservative: a backreference to a "
      "VARIABLE-width group. PCRE2 compiles it (maxlb 2), python refuses it, "
      "and no fixed-width analysis can accept it. G3.", perr=True),
 cell(r"(?=(?<=a*)b)x", LA, None,
      "THE INNER RULE APPLIES THROUGH THE OUTER: a variable-width lookbehind "
      "nested inside a lookAHEAD is still refused, by both oracles and by "
      "pcrec. The lookahead has no width rule of its own -- that is exactly "
      "why the assertion family's `\\Z` expansion `(?=\\n?\\z)` ships -- so "
      "this cell fixes that the refusal belongs to the LOOKBEHIND and is not "
      "a property of the enclosing construct.", perr=True),
 cell(r"(?<=\n?\z)x", "assertions," + LA, None,
      "§2.5's DISCRIMINATING ROW, and it is the one that stops \"the rule is "
      "exactly big enough for the assertion family\" from being a "
      "coincidence. `\\Z` IS `(?=\\n?\\z)` -- a lookAHEAD, where there is no "
      "width rule at all -- and every one of the nine [DD-11]/D66 expansions "
      "compiles under §2.5. THE SAME BODY ONE DIRECTION OVER is width 0..1 "
      "and is refused, which is this cell. §12 P-12 is how to refute the "
      "coincidence.", perr=True),
 cell(r"(?<=\w?)x", LA + ",classes", None,
      "...and the same shape with a class, so the refusal is about the "
      "OPTIONALITY and not about `\\n` or `\\z`.", perr=True),
 cell("(?=a", LA, None,
      "THE UNTERMINATED FORMS. The port owns its own closing-`)` "
      "diagnostic, exactly as mod_atomic_groups.c\'s does -- "
      "`pcrec_parse_body` stops AT the terminator without consuming it, and "
      "the caller consumes its own.",
      perr=True),
 cell("(?!a", LA, None, None, perr=True),
 cell("(?*a", LA, None, None, perr=True),
 cell("(?<=a", LA, None,
      "...and the three LOOKBEHIND spellings of the same thing, which wave D "
      "added because until it landed they were declined at the doorway and "
      "never reached the body parse that owns this diagnostic.", perr=True),
 cell("(?<!a", LA, None, None, perr=True),
 cell("(?<*a", LA, None, None, perr=True),
]

# ===========================================================================
#  gated.rxt — the MODULE GATE and D65's `built` column, cell by cell
# ===========================================================================
GATED = [
 cell("(?=a)ab", LA, [("ab", 0), ("b", 0)],
      "THE CONTROL, AND THE FILE IS WORTHLESS WITHOUT IT. Every other block "
      "here is a `perr`, and a file of nothing but refusals passes just as "
      "well on a compiler that refuses EVERYTHING -- which is exactly the "
      "state this file's own subject (a half-landed module gate) puts the "
      "compiler in. This block has module `lookaround` ON and must MATCH."),
 cell("(?=a)b", "", None,
      "THE GATE, CLOSED. With no module enabled the doorway answers "
      "\"(?=...) requires module 'lookaround'\" -- the promise D26 puts in "
      "tier 2, naming the construct and the module that owns it.",
      perr=True),
 cell("(?=a)b", "backrefs", None,
      "The WRONG module enabled buys nothing: the gate is per-row, not "
      "per-pattern.", perr=True),
 # [WAVE D] D65's SPLIT RETIRED HERE, and the three blocks that measured it
 # went with it. At wave B+C module `lookaround` was ENABLED and `(?<=...)`
 # still refused, with the enabled-but-unbuilt wording rather than "requires
 # module" -- the port ACCEPTED `=` `!` `*` and DECLINED the three `<` tails at
 # WANT_RESULT, which is exactly what `--list-syntax` read as `unbuilt`. Wave D
 # landed the back-step, deleted the decline, and all six rows read `built`, so
 # those three blocks would now be pinning a LIE. They are replaced by the
 # closed-gate cell below and by lookbehind.rxt, which asserts the same three
 # spellings COMPILE AND MATCH -- the count here going DOWN is the module
 # landing, and that file is the control that says so.
 cell("(?<=a)b", "", None,
      "THE GATE, CLOSED, ON A LOOKBEHIND. With no module enabled the doorway "
      "answers \"(?<=...) requires module 'lookaround'\" -- and this "
      "spelling needs its own cell rather than inheriting the `(?=a)b` one "
      "above, because `(?<` is THREE constructs and a name, split by tail at "
      "SR-9, so a doorway change could move the lookbehinds while leaving "
      "the lookahead row exactly where it was.", perr=True),
 cell("(?<*a)b", "", None,
      "...and the non-atomic lookbehind, the row SR-9's 256-tail sweep had "
      "to split out of the named-group path -- the tail most likely to be "
      "lost, since `*` is the one that is not a comparison operator.",
      perr=True),
 cell("(?<=(a|bc))x", LA, None,
      "AND THE ONE ENABLED-AND-BUILT REFUSAL THIS MODULE STILL OWES A GATE "
      "CELL: §2.5's variable-width limit is NOT the gate and NOT the "
      "`unbuilt` column -- module `lookaround` is enabled, the row is "
      "`built`, and the construct is real. It is the CAPABILITY tier, and "
      "the wording says so instead of telling a caller to enable something "
      "they already have. refused.rxt carries the family; this block is here "
      "so the three tiers sit in one file where a reader can see they are "
      "three different sentences.", perr=True),
 cell(r"(?=a\K)x", LA, None,
      "R33 C2-5's MASKING SHAPE, PINNED. Without `assertions` this cell is "
      "refused by the ASSERTIONS gate and never reaches §2.7's check at "
      "all, so a `\\K`-in-lookaround row whose detector forgot the feature "
      "would score green on a compiler with the check deleted. The same "
      "pattern WITH `--features assertions,lookaround` is in refused.rxt, "
      "and that is the one sabotage row S128 names.", perr=True),
 cell("(?<name>a)b", "named-groups", [("ab", 0)],
      "AND NO ROW OUTSIDE MODULE `lookaround` MOVED. `(?<` is three "
      "constructs and a name; this is the name, and it still belongs to "
      "module `named-groups` with its own producer."),
]

FILES = [
 ("lookahead.rxt", LOOKAHEAD,
  "`(?=` and `(?!`: bodies, contexts, degenerate forms (design §10.2)"),
 ("captures.rxt", CAPTURES,
  "the four polarity/outcome combinations, with `g` lines (design §10.2)"),
 ("quantified.rxt", QUANTIFIED,
  "`(?=a)*` and family, including §2.6's empty-iteration cells"),
 ("nonatomic_ahead.rxt", NONATOMIC,
  "`(?*` only -- the wave B+C half of the `nonatomic.rxt` split (R33 C2-9)"),
 ("lookbehind.rxt", LOOKBEHIND,
  "`(?<=` and `(?<!`: fixed bodies, SAME-length alternatives (design §10.2)"),
 ("lookbehind_widths.rxt", LOOKBEHIND_WIDTHS,
  "DIFFERENT-length branches -- G1's cells, and §2.4's preference order"),
 ("startpos.rxt", STARTPOS,
  "`ms`/`ns` cells over a lookbehind -- §3.8's reads-before-startpos contract"),
 ("nonatomic_behind.rxt", NONATOMIC_BEHIND,
  "`(?<*`, carrying §3.6's measured witness `(?<*(a)|(ba))c\\2` by name"),
 ("workbudget.rxt", WORKBUDGET,
  "§3.7's long-subject LEADING multi-branch lookbehind (R33 C1-6)"),
 ("refused.rxt", REFUSED,
  "the `perr` cells this wave owns -- §2.7's `\\K` refusal and the "
  "unterminated forms"),
 ("gated.rxt", GATED,
  "the module gate and D65's `built` column, cell by cell"),
]

HEADER = """\
# tests/lookaround/%s -- module `lookaround` ([M6.6.2]): %s
#
# GENERATED BY tests/lookaround/gen_corpus.py, and that is a property rather
# than a convenience. Every expectation below was produced by driving the cell
# through libpcre2 10.46 (the committed ctypes binding at
# docs/design/eng_brep_measurements/probes/pcre2_ctypes.py) BEFORE it was
# written, and python3 `re` was driven over the SAME cells in the same pass; a
# block carries `# pcre2-only` exactly where python diverged or could not
# compile the pattern -- DETECTED, never assumed, with the first divergence and
# the cell count recorded above the marking. The generator never asks pcrec
# anything: an expectation derived from the compiler under test is not an
# expectation.
#
# WHY THE MARKING IS COMPUTED RATHER THAN DECLARED. Design §7 catalogues TWO
# expectations about this module that a hand-marking would have written in and
# that are REFUTED by measurement: python compiles all fourteen QUANTIFIED
# lookaround forms and agrees on all nine behavioural cells (G8), and the two
# oracles agree on all 27 CAPTURE cells including captures in a negative
# lookahead (G9). R32 C3 is the standing precedent -- a test plan that marked
# two files python-verifiable in the direction that LOSES the oracle.
#
# EVERY BLOCK NAMES `lookaround` IN ITS `features` LINE (R33 V-10): `std1` is a
# FROZEN named set, {classes, modifiers}, so it does not contain this module,
# and a corpus cell that forgot the feature would pass by REFUSAL -- S108's
# masking shape applied to a whole file.
#
# Design: docs/design/lookaround_design.md.
"""


def pcre_answer(pat, subj, sp, ng):
    rx = P.Compiled(pat)
    r = rx.search(subj, sp)
    if r is None:
        return ("n", None, [])
    groups = list(r[1])
    while len(groups) < ng:
        groups.append(None)
    return ("m", (r[0][0], r[0][1]), groups[:ng])


def py_answer(pat, subj, sp, ng):
    try:
        rx = pyre.compile(pat)
    except Exception as e:                                  # noqa: BLE001
        return ("ERR", str(e))
    try:
        m = rx.search(subj, sp)
    except Exception as e:                                  # noqa: BLE001
        return ("ERR", str(e))
    if m is None:
        return ("n",)
    out = ["m", m.start(), m.end()]
    for g in range(1, min(ng, rx.groups) + 1):
        out.append(m.span(g))
    return tuple(out)


def pcre_tuple(pat, subj, sp, ng):
    k = pcre_answer(pat, subj, sp, ng)
    if k[0] == "n":
        return ("n",)
    out = ["m", k[1][0], k[1][1]]
    for g in k[2]:
        out.append((-1, -1) if g is None else (g[0], g[1]))
    return tuple(out)


def quote(s):
    out = ['"']
    for ch in s:
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\t":
            out.append("\\t")
        elif ch == "\r":
            out.append("\\r")
        elif 32 <= ord(ch) < 127:
            out.append(ch)
        else:
            out.append("\\x%02x" % ord(ch))
    out.append('"')
    return "".join(out)


def wrap(text, prefix="# "):
    words, lines, cur = text.split(), [], prefix
    for w in words:
        if len(cur) + len(w) + 1 > 78 and cur.strip() != prefix.strip():
            lines.append(cur.rstrip())
            cur = prefix + w + " "
        else:
            cur += w + " "
    if cur.strip() != prefix.strip():
        lines.append(cur.rstrip())
    return "\n".join(lines)


def emit(fname, cells, what, outdir):
    body = [HEADER % (fname, what)]
    stats = {"blocks": 0, "cells": 0, "pcre2only": 0, "perr": 0,
             "pyverified": 0, "pycells": 0}
    for c in cells:
        stats["blocks"] += 1
        body.append("")
        if c["note"]:
            body.append(wrap(c["note"]))
        if c["perr"]:
            stats["perr"] += 1
            try:
                P.Compiled(c["pat"])
                verdict = ("libpcre2 10.46 ACCEPTS this pattern -- pcrec's "
                           "refusal is a CAPABILITY limit, stated as one "
                           "(D26 tier 2: which constructs are real is exact, "
                           "what pcrec builds is a separate statement)")
            except Exception as e:                          # noqa: BLE001
                verdict = "libpcre2 10.46 also refuses: %s" % \
                          str(e).split(": ", 1)[-1]
            try:
                pyre.compile(c["pat"])
                pyverdict, pyok = "python3 `re` ACCEPTS it", True
            except Exception as e:                          # noqa: BLE001
                pyverdict, pyok = "python3 `re` refuses: %s" % e, False
            body.append(wrap("MEASURED: " + verdict + "; " + pyverdict))
            if pyok:
                stats["pcre2only"] += 1
                body.append(wrap(
                    "python COMPILES this pattern, so it cannot verify a "
                    "`perr` block for it: the refusal is pcrec's own GATE or "
                    "CAPABILITY answer, not a syntax verdict either oracle "
                    "shares. tests/harness/CLAUDE.md's rule -- gate-only "
                    "constructs are `# pcre2-only` blocks like any other "
                    "python-inexpressible pattern."))
                body.append("# pcre2-only")
            else:
                stats["pyverified"] += 1
            body.append("pattern %s" % c["pat"])
            if c["feats"]:
                body.append("features %s" % c["feats"])
            body.append("perr")
            continue

        P.Compiled(c["pat"])          # a cell libpcre2 refuses is a bug HERE
        ng = _count_groups(c["pat"])

        lines, diverge, ncell = [], None, 0
        for subj, sp in c["cases"]:
            ncell += 1
            a = pcre_tuple(c["pat"], subj, sp, ng)
            b = py_answer(c["pat"], subj, sp, ng)
            if a != b and diverge is None:
                diverge = (subj, sp, a, b)
            if a[0] == "n":
                lines.append(("ns %d %s" % (sp, quote(subj))) if sp
                             else ("n %s" % quote(subj)))
            else:
                lines.append(("ms %d %s %d %d" % (sp, quote(subj), a[1], a[2]))
                             if sp else
                             ("m %s %d %d" % (quote(subj), a[1], a[2])))
                for gi, g in enumerate(a[3:], start=1):
                    lines.append("g %d %d %d" % (gi, g[0], g[1]))
        stats["cells"] += ncell
        if diverge is not None:
            stats["pcre2only"] += 1
            subj, sp, a, b = diverge
            body.append(wrap("python DIVERGES here, measured rather than "
                             "assumed: %r @%d pcre2=%r python=%r (%d cells in "
                             "this block)" % (subj, sp, a, b, ncell)))
            body.append("# pcre2-only")
        else:
            stats["pyverified"] += 1
            stats["pycells"] += ncell
        body.append("pattern %s" % c["pat"])
        if c["feats"]:
            body.append("features %s" % c["feats"])
        body.extend(lines)

    with open(os.path.join(outdir, fname), "w") as f:
        f.write("\n".join(body) + "\n")
    return stats


def _count_groups(pat):
    """Capture-group count, counted from the pattern text the way the .rxt
    `g` slot numbering does. Written here rather than taken from python `re`
    because half these patterns do not compile in python at all."""
    n, i, ln = 0, 0, len(pat)
    incls = False
    while i < ln:
        ch = pat[i]
        if ch == "\\":
            i += 2
            continue
        if incls:
            if ch == "]":
                incls = False
            i += 1
            continue
        if ch == "[":
            incls = True
            i += 1
            continue
        if ch == "(":
            if i + 1 < ln and pat[i + 1] == "?":
                pass                      # every `(?...` form is non-capturing
            else:
                n += 1
        i += 1
    return n


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else HERE
    total = {"blocks": 0, "cells": 0, "pcre2only": 0, "perr": 0,
             "pyverified": 0, "pycells": 0}
    for fname, cells, what in FILES:
        st = emit(fname, cells, what, outdir)
        for k in total:
            total[k] += st[k]
        sys.stderr.write(
            "%-22s %3d blocks  %4d cells  %2d pcre2-only  %2d perr  "
            "%2d python-verified blocks (%d cells)\n"
            % (fname, st["blocks"], st["cells"], st["pcre2only"], st["perr"],
               st["pyverified"], st["pycells"]))
    sys.stderr.write("%-22s %3d blocks  %4d cells  %2d pcre2-only  %2d perr  "
                     "%2d python-verified blocks (%d cells)\n"
                     % ("TOTAL", total["blocks"], total["cells"],
                        total["pcre2only"], total["perr"],
                        total["pyverified"], total["pycells"]))


if __name__ == "__main__":
    main()
