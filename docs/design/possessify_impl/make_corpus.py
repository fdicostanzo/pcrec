#!/usr/bin/env python3
"""make_corpus.py — the PRODUCER of tests/possessify/possessify.rxt.

Committed for R24 M-F1/M-F2's reason: a corpus whose expectations were
hand-written, or produced by a script nobody kept, cannot be re-derived when
the oracles move. Every expectation in that file came from HERE, from BOTH
oracles (python3 `re`, and libpcre2 10.46 through ctypes — see gen_rxt.py),
and a cell the two disagreed on was REPORTED rather than resolved.

Every family is emitted twice: as written, and CAPTURE-WRAPPED. The second
half is the one that tests the emitter — a capture-free pattern routes to the
DFA and never reaches src/gen/emit_vm.c, so on this file's first version 33 of
38 patterns were DFA-routed and only three carried a possessified quantifier.

Usage: python3 make_corpus.py <out.rxt>
"""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_rxt import emit

R = ["", "a", "aa", "aaa", "aaaa", "aaaaa", "b", "ab", "abab", "ababab",
     "ac", "aac", "aaac", "aaaac", "aaaaac", "c", "bc", "abc", "aabc",
     "za", "zaa", "zaaa", "zaaaa", "zac", "zaac", "zaaac", "q", "aq"]

VERDICT_POS = [
 (["EXACT-COUNT arm, greedy. m == n leaves the loop one exit, so the arm holds",
   "for either preference and needs no reference to what follows (§2.2)."],
  "a{2,2}c", R),
 (["EXACT-COUNT arm, LAZY. The arm is preference-independent because top and",
   "bottom of §2.3's exit chain are the same position -- which is why it",
   "survived every attack the R24 panel made [R24 H8]."],
  "a{2,2}?c", R),
 (["EXACT-COUNT over a class: the shape real bounded repeats actually take.",
   "52 of the 76 possessifiable verdicts on the realistic pattern set (§2.6)."],
  "[ab]{3,3}c", R),
 (["EXACT-COUNT over a multi-byte body. Reaches further than PCRE2's own",
   "item-wise auto-possessification, which compares one repeated ITEM (§2.9)."],
  "(?:ab){2,2}c", R),
 (["EXACT-COUNT with a capture inside the loop: the group must still report",
   "the last iteration that entered it."],
  "(a){2,2}c", R),
 (["DISJOINTNESS arm, greedy, bounded."], "a{0,4}c", R),
 (["DISJOINTNESS arm, greedy, unbounded -- §2.2's chain argument does not",
   "depend on n being finite."], "a{3,}c", R),
 (["DISJOINTNESS arm over a star."], "a*c", R),
 (["DISJOINTNESS arm, multi-byte alternation body. One-unambiguous (the",
   "branches differ in their first byte) and prefix-free."], "(?:a|bc){0,4}d",
  R + ["bcd", "abcd", "abcbcd", "bcbc", "ad"]),
 (["DISJOINTNESS arm, LAZY, with a NON-NULLABLE remainder -- the side of",
   "[R24 S-F1]'s conjunct that still possessifies. A verdict-positive lazy",
   "quantifier is forced to the SAME maximal exit a greedy one tops out at:",
   "at any non-maximal exit the body could iterate again, so that byte is in",
   "FIRST(X), so by disjointness the follow cannot begin there."],
  "a{1,3}?c", R),
 (["DISJOINTNESS arm, LAZY, unbounded, non-nullable remainder."], "a+?c", R),
 (["The example engine_m4.md §2.5 uses, annotated by [R24 C-F1] as SURVIVING",
   "the correction: the body is non-nullable and admits a unique iteration,",
   "so the repaired rule admits it too even though the refuted",
   "disjoint-follow-ONLY rule is what originally admitted it."],
  "z(ab)*y", ["zy", "zaby", "zababy", "zababab", "zab", "zaby!", "ab", "zabay"]),
 (["Several quantifiers in one pattern, landing on DIFFERENT strategies --",
   "the mixed artifact a scalar stamp would misreport."],
  "a{2,2}b{0,4}c", R + ["aabc", "aabbc", "aabbbbc", "aabbbbbc", "aac"]),
]

VERDICT_NEG = [
 (["DECLINE, (U1) ambiguous body. THE 117-COUNTEREXAMPLE FAMILY (§2.4): the",
   "branches share a first byte, so one iteration has TWO possible ends and a",
   "retreat can move the exit position RIGHT rather than only left.",
   "`(a|ab){0,4}c` on \"abc\" is (0,3) greedy with group 1 = \"ab\" and would be",
   "(2,3) with group 1 unset if this were possessified."],
  "(a|ab){0,4}c", R + ["abc", "ababc", "abab", "abababc"]),
 (["DECLINE, (U1), the same ambiguity spelled the other way round. §2.4's",
   "\"one thing v1 got right by accident\": this family passed the first",
   "differential only because its follow set had no follow beginning with the",
   "body's SECOND byte."],
  "(?:ab|a){0,4}b", R + ["abb", "ababb", "aab", "abab"]),
 (["DECLINE, (U2) not prefix-free -- and it needs no alternation at all. The",
   "body is one-unambiguous; its accepting position `a` (with `b?` matching",
   "empty) simply has an outgoing edge. `(?:ab?){0,4}b` on \"ab\" is (0,2)",
   "greedy and NO MATCH possessive."],
  "(?:ab?){0,4}b", R + ["ab", "abab", "abb", "aab"]),
 (["DECLINE, nullable body. §2.3's chain is strictly increasing only because",
   "the body consumes; a nullable body has no chain."],
  "(?:a|){0,4}c", R),
 (["DECLINE, nullable body with a capture -- §5.3 names `(|a){m,n}` as its",
   "own dense cell because R24 measured it as the family where the ORACLES",
   "disagree (python vs libpcre2 on 106 of 15,600 cells, all of them this",
   "shape's captures). Every expectation here agreed three ways or it is not",
   "in this file."],
  "(|a){2,4}c", R),
 (["DECLINE, overlapping follow. FIRST(body) meets FOLLOW, so a retreat can",
   "genuinely help."], "a{0,4}a", R),
 (["DECLINE, SUBSUMED follow -- §2.7's named conservatism. FOLLOW contains",
   "`b` because of the `b?`, and a `b` at any retreat position was already",
   "consumable by the loop, so the retreat cannot actually help. PCRE2's",
   "auto-possessification does this subsumption reasoning; pcrec's first",
   "version deliberately does not, and this cell is what that costs."],
  "[ab]{0,4}b?c", R + ["abbc", "abc", "bbc", "abbbc"]),
 (["DECLINE, `^` in the follow. An assertion reached at the follow's first",
   "position widens FOLLOW to all bytes: `^` is DOWNWARD-closed, so a retreat",
   "CAN reach a position satisfying it from one that does not (80 of 240",
   "diverging cells on the panel's instrument)."],
  "a{0,4}^", R),
]

LAZY_GUARDS = [
 (["THE LAZY CONJUNCT'S OWN GUARD CELLS (D47.6, ruled into this corpus).",
   "",
   "These are the cells a regressed lazy conjunct would miscompile. The",
   "remainder is NULLABLE -- the match can simply END at the quantifier -- so",
   "the follow's first-byte test is VACUOUS and the disjointness argument",
   "says nothing. A greedy loop is unharmed (it tops out at the chain's top,",
   "where the vacuous follow succeeds anyway); a LAZY loop stops at the",
   "BOTTOM of the same chain and reports a shorter span.",
   "",
   "`a{1,3}?` on \"aaaa\" is (0,1) lazy and (0,3) possessive: 316 measured",
   "diverging cells, python and libpcre2 agreeing [R24 S-F1].",
   "",
   "The `z`-prefixed rows are the D47.6 lesson itself. The design lane's own",
   "sweep reported these as twenty FALSE declines; pulling them for",
   "inspection showed all twenty GENUINELY diverge, and the reason the sweep",
   "could not see it is that its random-subject alphabet was \"abcd \" -- so",
   "every z-prefixed pattern was swept essentially without its prefix. A",
   "generator whose alphabet omits a pattern character measures the",
   "generator."],
  "a{1,3}?", R),
 ([""], "za{1,3}?", R),
 ([""], "a{0,4}?", R),
 ([""], "za{0,2}?", R),
 (["A nullable remainder spelled as an optional follow rather than as the",
   "end of the pattern -- the same vacuity, one construct further out."],
  "a{1,3}?c?", R),
 ([""], "za{1,3}?c?", R),
 (["The GREEDY spelling of the same shape, which possessifies: the conjunct",
   "is scoped to lazy and provably does not disturb the family that was",
   "already clean (§2.4's v3 greedy rows are byte-identical to v2's)."],
  "a{1,3}", R),
 ([""], "za{1,3}", R),
]

EOL = [
 (["THE `$`-FOLLOW EXEMPTION (D47.5, [R24 S-F2]) -- the only §2 rule whose",
   "correctness depends on a pattern OPTION rather than on structure.",
   "",
   "`$` in the follow is MEASURED safe at 0 of 720 diverging cells, on an",
   "upward-closure argument: `$` holds only at the subject end (and before a",
   "final newline), which is the top one or two positions, and a retreat",
   "moves strictly LEFT -- so no retreat position below a failing maximal",
   "exit can satisfy it. Under `(?m)` that argument collapses per-line and",
   "the same sweep gives 180 of 720 diverging, which is why D47.5 rules the",
   "gate a LIVE check on the compile's own multiline state rather than a",
   "comment about what pcrec does not support yet.",
   "",
   "pcrec refuses `(?m)` today (module `assertions`), and that module's plan",
   "row inherits D47.5's test obligation: a `(?m)` pattern whose `$`-follow",
   "quantifier must NOT possessify. The newline subjects below are here",
   "because `$` in pcrec means end-of-subject OR before a final newline, so",
   "the exemption's argument has to hold for both."],
  "a{0,4}$", R + ["aaa\n", "a\n", "\n", "aaaa\n", "caaa\n"]),
 ([""], "[ab]{0,4}$", R + ["abab\n", "ab\n", "b\n"]),
 ([""], "a{1,3}?$", R + ["aaa\n", "a\n"]),
 ([""], "a{0,4}c$", R + ["aac\n", "ac\n", "c\n"]),
]

NESTED = [
 (["THE TRANSITIVE-FOLLOW LINE (§2.2), which §8 nominated as \"the single",
   "most likely place for a soundness bug to be hiding\" and which survived a",
   "42,336-pair targeted attack at 0 divergences [R24 H1].",
   "",
   "An inner quantifier's FOLLOW must include FIRST(B) for the body B of",
   "every ENCLOSING loop, because the enclosing loop can start another",
   "iteration once the inner one's parent finishes. Dropping that term yields",
   "172 counterexamples on the panel's instrument; here it is the difference",
   "between the two blocks below -- `(?:a{0,2}b)+c` possessifies its inner",
   "quantifier and `(?:a{0,2}a)+c` must not, and the ONLY thing that",
   "distinguishes them is the enclosing body's first set."],
  "(?:a{0,2}b)+c", ["abc", "aabc", "ababc", "aabaabc", "bc", "c", "aaabc", "ab",
                    "abab", "aabaab", "aabc!", "abbc"]),
 ([""], "(?:a{0,2}a)+c", ["ac", "aac", "aaac", "aaaac", "aaaaac", "c", "a",
                          "aa", "aaa", "aaaa"]),
 ([""], "(?:[ab]{0,2}c)+d", ["cd", "acd", "abcd", "accd", "ababccd", "d",
                             "abc", "abcabcd"]),
 (["A capture inside a nested loop: §3.4's finding is that a group inside a",
   "loop keeps the value from the last iteration that ENTERED it, and a later",
   "iteration that does not enter it does not clear it."],
  "(?:(a){0,2}b)+c", ["abc", "aabc", "ababc", "babc", "bbc", "bc", "abbc"]),
 (["The LAZY inner spelling of the same nesting -- §5.3 makes greedy AND",
   "lazy mandatory at every shape, because a sweep that spells every shape",
   "greedy is structurally incapable of exercising the lazy conjunct."],
  "(?:a{0,2}?b)+c", ["abc", "aabc", "ababc", "bc", "c", "aaabc"]),
]

with open(sys.argv[1], "w") as f:
    f.write("""# tests/possessify/possessify.rxt — module-free corpus for [ENG-BREP]'s
# possessification rung (docs/design/eng_brep_design.md §2).
#
# EVERY EXPECTATION IN THIS FILE WAS PRODUCED BY BOTH ORACLES AND AGREED.
# Each (pattern, subject) cell's span and every capture slot were taken from
# python3 `re` AND from libpcre2 10.46, and a cell the two disagreed on was
# reported rather than resolved -- none survived into this file. That is D44's
# three-way rule applied where §5.3 says it earns itself: `(|a){m,n}` is
# measured as the family where the oracles themselves disagree (106 of 15,600
# cells at R24), so a two-way python-only check on it would have raised a
# FALSE alarm against pcrec.
#
# WHAT THIS FILE IS FOR, and what it is NOT for. It pins the ANSWERS around
# the possessification rule -- what each pattern matches, whether or not the
# rule fires on it. It cannot see the rule itself: a possessified quantifier
# and a backtracking one match identically by construction, which is the
# claim. The check that can see the rule is the pcrec-vs-pcrec differential
# (run_possdiff.sh), and the check that says WHICH quantifiers were
# possessified is the artifact's own <PREFIX>_VM_STRATS stamp
# (run_possessify_tests.sh). All three are needed and none substitutes for
# another.
""")
    n = 0
    ALL = [
        ("POSITIVE VERDICTS", VERDICT_POS),
        ("DECLINES, one per declining condition", VERDICT_NEG),
        ("THE LAZY CONJUNCT'S GUARD CELLS", LAZY_GUARDS),
        ("THE `$`-FOLLOW EXEMPTION AND ITS LIVE GATE", EOL),
        ("NESTED QUANTIFIERS AND THE TRANSITIVE FOLLOW", NESTED),
    ]
    for title, blocks in ALL:
        f.write("\n\n# " + "=" * 70 + "\n# " + title + "\n# " + "=" * 70 + "\n")
        n += emit(blocks, f)

    # ---- the same families, CAPTURE-WRAPPED so they reach the VM ----------
    #
    # WHY THIS HALF EXISTS. Under the default engine choice a capture-free
    # pattern routes to the DFA and never reaches src/gen/emit_vm.c, so
    # possessification is structurally invisible to it. Measured on the first
    # version of this file: 33 of 38 patterns were DFA-routed and only THREE
    # carried a possessified quantifier -- an oracle-verified corpus for a VM
    # rewrite that almost never ran the VM.
    #
    # Wrapping the whole pattern in one capture forces want_caps, so the
    # artifact is the VM's, while changing nothing the analysis sees: A_CAP is
    # transparent to FIRST, to FOLLOW and to the Glushkov construction, and
    # group 1 is the whole match. Every expectation here is produced by both
    # oracles exactly as above, so the capture slot is checked too.
    f.write("\n\n# " + "=" * 70 + "\n"
            "# THE SAME FAMILIES, CAPTURE-WRAPPED SO THEY REACH THE VM\n"
            "#\n"
            "# A capture-free pattern routes to the DFA and never reaches the\n"
            "# emitter this rung rewrites. Wrapping the whole pattern in one\n"
            "# group forces the VM artifact while changing nothing the analysis\n"
            "# sees -- A_CAP is transparent to FIRST, to FOLLOW and to the\n"
            "# Glushkov construction -- so these blocks pin the POSSESSIFIED\n"
            "# EMITTER's answers, with group 1 checked as the whole match.\n"
            "# " + "=" * 70 + "\n")
    for title, blocks in ALL:
        wrapped = [([("(capture-wrapped) " + h) if i == 0 and h else h
                     for i, h in enumerate(hdr)] or [""],
                    "(" + pat + ")", subs)
                   for hdr, pat, subs in blocks]
        n += emit(wrapped, f)
print("oracle disagreements:", n)
