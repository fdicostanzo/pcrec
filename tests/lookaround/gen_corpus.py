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
 cell("(?=a", LA, None,
      "THE UNTERMINATED FORMS. The port owns its own closing-`)` "
      "diagnostic, exactly as mod_atomic_groups.c\'s does -- "
      "`pcrec_parse_body` stops AT the terminator without consuming it, and "
      "the caller consumes its own.",
      perr=True),
 cell("(?!a", LA, None, None, perr=True),
 cell("(?*a", LA, None, None, perr=True),
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
 cell("(?<=a)b", LA, None,
      "D65's SPLIT, AND THIS IS THE CELL THAT MEASURES IT. Module "
      "`lookaround` is ENABLED and `(?<=...)` still refuses -- with the "
      "enabled-but-unbuilt wording, not \"requires module\", because "
      "telling a caller to enable something they have already enabled is an "
      "actionable-sounding lie. The refusal comes from "
      "`pcrec_laport_group`'s own tail check (the port ACCEPTS `=` `!` `*` "
      "and DECLINES the three `<` tails at WANT_RESULT), which is exactly "
      "what `--list-syntax` reads as `unbuilt`. WAVE D DELETES THIS BLOCK "
      "and moves the cell to lookbehind.rxt.", perr=True),
 cell("(?<!a)b", LA, None, "The same for the negative lookbehind.", perr=True),
 cell("(?<*a)b", LA, None,
      "...and for the non-atomic lookbehind, the row SR-9's 256-tail sweep "
      "had to split out of the named-group path.", perr=True),
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
 ("refused.rxt", REFUSED,
  "the `perr` cells this wave owns -- §2.7's `\\K` refusal and the "
  "unterminated forms"),
 ("gated.rxt", GATED,
  "the module gate and D65's `built` column, cell by cell"),
]

HEADER = """\
# tests/lookaround/%s -- module `lookaround` ([M6.6.2] wave B+C): %s
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
