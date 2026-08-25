#!/usr/bin/env python3
"""[DD-14 wave G] §8.3's HAZARD, re-run against the CALL population.

`subroutines_design.md` §8.3 ends with an obligation rather than a switch:

    THE HAZARD THAT MUST BE CHECKED AND IS NOT CHECKED HERE.
    `lookaround_design.md` §5.4 found that a superset preserves the REJECTION
    and the match START but NOT the window END (8 violations of 45), and
    `backrefs_design.md` §11.2's planted-window hazard is the same shape.
    §8.3's `Sigma*` arm makes a *much* looser superset than lookaround erasure,
    so the window end is at least as exposed. **Wave G does not land without
    re-running `lookaround_measurements/probes/probe_prefilter_hazard.py`'s
    H1/H2/H3 against the call population**, and §12 P-7 is the prediction.

THE THREE HYPOTHESES ARE THAT PROBE'S, TRANSCRIBED RATHER THAN REINVENTED, and
they are separately falsifiable properties of whatever approximation the
prefilter is built from (`A` below):

  H1  REJECTION.   A matches nowhere  =>  P matches nowhere.
  H2  START.       leftmost-start(A) <= leftmost-start(P).
                   Too EARLY costs work; too LATE loses matches.
  H3  END.         end(A) >= end(P).  This is the one the atomic lane found
                   FALSE for its own construct, at 114 cells of silent match
                   loss, because `Vm.mrl_win` feeds the prefilter's window END
                   to the MRL pruning as a CEILING.

H3 IS MEASURED TWICE and only the SHARP form is the real one, for that probe's
reason: the naive comparison conflates an H2 failure with an H3 failure,
because when A's match starts EARLIER the two ends are not about the same
candidate at all. The sharp form fixes the start at the one the TRUE match uses
and asks whether A, ANCHORED THERE, ends at or after the true end.

============================================================================
WHAT CHANGED FOR THIS POPULATION, AND WHY THE ANSWER IS NOT A TABLE OF ZEROS
============================================================================

§8.3 wrote its obligation against the `Sigma*` arm, which wave G DID NOT BUILD.
The narrowing in `src/opt/select_engine.c` (`pcrec_has_linked_call`) makes that
arm unreachable: a pattern with a LINKED call gets no prefilter at all, so
nothing consumes a superset for it. What wave G DID build is the other arm —
`src/ir/nfa.c` INLINES a spliced callee's fragment — and that is not a superset
at all. It is EXACT, because `ast_bare` erases the `A_CAP` from the inlined
body exactly as it does from every other group in the tree.

SO A TABLE OF ZEROS IS THE PREDICTION, WHICH IS PRECISELY WHY IT PROVES
NOTHING ON ITS OWN. R32's finding against this project's own instruments is
that a population which COULD NOT have produced a violation reports zero and
means nothing. This probe therefore evaluates H1/H2/H3 over TWO approximations
on the SAME cells:

  INLINE   the callee's body substituted at the call site -- wave G's, and the
           one the shipped compiler builds its machine from.
  ERASE    the call deleted -- design §8.2's approximation, which that section
           REFUTES in one line ("`a(?1)b` with group 1 = `x` matches "axb";
           erasing the call gives `ab`, which does not").

**ERASE IS THE POSITIVE CONTROL AND IT MUST VIOLATE.** If both columns come
back clean, the population cannot tell a sound approximation from an unsound
one and the run is a hard FAILURE rather than a pass. That is the same
discipline `probe_prefilter_hazard.py`'s own H3-control family enforces, moved
from a family to a whole column because for calls the unsound alternative is a
DIFFERENT TRANSFORM rather than a different pattern shape.

============================================================================
THE PAIRS ARE HAND-WRITTEN AND EQUIVALENCE IS CHECKED FIRST
============================================================================

§8.3's own discipline, verbatim: *"EQUIVALENCE FIRST: 15 hand-written (call,
inlined) pairs across the three idioms, each verified against libpcre2 over 28
subjects -- 420 cells, 0 disagreements -- before any timing. A pair that
disagreed would have been disqualified, not fixed."* A general inliner written
here would be a SECOND implementation of the thing under test, and the two
agreeing would prove only that one author wrote both.

Nothing here is pcrec: libpcre2 is the source of truth (D26).

Usage:  python3 docs/design/subroutines_measurements/probes/probe_call_prefilter_hazard.py
Exit:   0 all hypotheses hold for INLINE and the controls fired; 1 otherwise.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sr_oracle as sr                                       # noqa: E402

# --------------------------------------------------------------------------
# THE POPULATION: (name, P, INLINE(P), ERASE(P))
#
# Every P uses the `{0}`-callee idiom, so every call is ACYCLIC and every one
# of them SPLICES under §6.3 — which is what makes the INLINE column the
# transform the shipped compiler actually performs. The three idioms of §8.3
# are all represented (numbered, named, and a definition called twice), and the
# shapes are chosen for where a prefilter's WINDOW is observable: a call at the
# head (H2's territory), a call at the tail (H3's), a call inside an
# alternation (where the atomic lane's 114 cells came from), and a call under a
# quantifier.
# --------------------------------------------------------------------------
PAIRS = [
    ("head-num",    r"(?:(x)){0}(?1)b",           r"(?:(x)){0}xb",           r"(?:(x)){0}b"),
    ("mid-num",     r"a(?:(x)){0}(?1)b",          r"a(?:(x)){0}xb",          r"a(?:(x)){0}b"),
    ("tail-num",    r"(?:(x)){0}ab(?1)",          r"(?:(x)){0}abx",          r"(?:(x)){0}ab"),
    ("named",       r"(?:(?<w>cat)){0}(?&w)x",    r"(?:(?<w>cat)){0}catx",   r"(?:(?<w>cat)){0}x"),
    ("named-twice", r"(?:(?<w>cat)){0}(?&w)x(?&w)",
                    r"(?:(?<w>cat)){0}catxcat",   r"(?:(?<w>cat)){0}x"),
    ("class-call",  r"(?:(?<a>[a-z]+)){0}(?&a)#(?&a)",
                    r"(?:(?<a>[a-z]+)){0}[a-z]+#[a-z]+",
                    r"(?:(?<a>[a-z]+)){0}#"),
    ("alt-call",    r"(?:(?<w>cat|dog)){0}(?&w)!(?&w)",
                    r"(?:(?<w>cat|dog)){0}(?:cat|dog)!(?:cat|dog)",
                    r"(?:(?<w>cat|dog)){0}!"),
    ("quant-call",  r"(?:(?<d>[0-9])){0}(?&d)+z",
                    r"(?:(?<d>[0-9])){0}[0-9]+z",
                    r"(?:(?<d>[0-9])){0}z"),
    # THE SHAPE THE ATOMIC LANE'S 114 CELLS CAME FROM: a branch that the
    # approximation makes PREFERRED and shorter. Erasing the call leaves the
    # first branch matching EMPTY at position 0, so the erased end is earlier
    # than the true end -- H3's failure, planted deliberately.
    ("alt-shorter", r"(?:(?<w>ab)){0}(?:(?&w)|abc)",
                    r"(?:(?<w>ab)){0}(?:ab|abc)",
                    r"(?:(?<w>ab)){0}(?:|abc)"),
    # DESIGN §8.2's OWN COUNTEREXAMPLE, as a cell: erasing gives a DIFFERENT
    # language rather than a bigger one, so H1 itself fails.
    ("sec82",       r"(?:(?<g>x)){0}a(?&g)b",     r"(?:(?<g>x)){0}axb",      r"(?:(?<g>x)){0}ab"),
]

SUBJECTS = [
    "", "x", "b", "xb", "axb", "ab", "abx", "abc", "cat", "catx", "xcat",
    "catxcat", "dog", "cat!dog", "dog!cat", "!", "abc#def", "#", "a#b",
    "12z", "z", "1z", "  xb  ", "yyxbyy", "abcabc", "ab", "xabx", "cAt",
]


def span(pat, subj):
    r = sr.search(pat.encode("latin-1"), subj.encode("latin-1"))
    return None if r is None else r[0]


def anchored_at(pat, subj, at):
    """The leftmost span of `pat` when the match is forced to START at `at`.

    `\\G` is PCRE2's own match-here device and is what
    `assertions/run_kreset_diff.sh` uses for the same purpose one module over:
    asking about `\\G(?:PAT)` at startpos `at` is the only way to get an
    anchored answer out of a binding with no anchored mode."""
    r = sr.search((r"\G(?:" + pat + ")").encode("latin-1"),
                  subj.encode("latin-1"), at)
    return None if r is None else r[0]


# --------------------------------------------------------------------------
# EQUIVALENCE FIRST (§8.3's rule). A pair that disagrees is DISQUALIFIED, not
# fixed: the INLINE column is supposed to be the same language, and a pair
# where it is not would make every hypothesis below measure the wrong thing.
# --------------------------------------------------------------------------
print("libpcre2:", sr.version())
print()
print("=== EQUIVALENCE FIRST: P vs INLINE(P), %d pairs x %d subjects" %
      (len(PAIRS), len(SUBJECTS)))
eq_cells = 0
eq_bad = 0
for name, p, inl, _er in PAIRS:
    for s in SUBJECTS:
        a, b = span(p, s), span(inl, s)
        eq_cells += 1
        if a != b:
            eq_bad += 1
            print("  DISQUALIFIED %-12s subj=%-10r P=%s INLINE=%s"
                  % (name, s, a, b))
print("  %d cells, %d disagreements" % (eq_cells, eq_bad))
if eq_bad:
    print("\n!! FAILED: the hand-written INLINE column is not the same language "
          "as its P. Every hypothesis below would be measuring a mistranscribed "
          "pattern rather than the compiler's approximation.")
    sys.exit(1)

# --------------------------------------------------------------------------
# H1 / H2 / H3, over BOTH approximations
# --------------------------------------------------------------------------
print()
print("=== H1/H2/H3 over %d cells, for each approximation" %
      (len(PAIRS) * len(SUBJECTS)))
print("%-8s %6s %6s %6s %8s %10s" %
      ("approx", "cells", "H1", "H2", "H3naive", "H3sharp"))

results = {}
for col in ("INLINE", "ERASE"):
    h1 = h2 = h3n = h3s = cells = differing = 0
    detail = []
    for name, p, inl, er in PAIRS:
        a_pat = inl if col == "INLINE" else er
        for s in SUBJECTS:
            cells += 1
            tp, ta = span(p, s), span(a_pat, s)
            if tp != ta:
                differing += 1
            if tp is not None and ta is None:
                h1 += 1
                detail.append((name, s, "H1", tp, ta))
                continue
            if tp is None:
                continue          # P does not match: H2/H3 say nothing
            if ta is not None and ta[0] > tp[0]:
                h2 += 1
                detail.append((name, s, "H2", tp, ta))
            if ta is not None and ta[1] < tp[1]:
                h3n += 1
            sharp = anchored_at(a_pat, s, tp[0])
            if sharp is None or sharp[1] < tp[1]:
                h3s += 1
                detail.append((name, s, "H3sharp", tp, sharp))
    results[col] = (h1, h2, h3n, h3s, cells, differing, detail)
    print("%-8s %6d %6d %6d %8d %10d" % (col, cells, h1, h2, h3n, h3s))

print()
for col in ("INLINE", "ERASE"):
    h1, h2, h3n, h3s, cells, differing, detail = results[col]
    print("%s: %d of %d cells give a DIFFERENT span from P" %
          (col, differing, cells))
    for d in detail[:6]:
        print("   %-12s subj=%-10r %-8s P=%s A=%s" % d)

# --------------------------------------------------------------------------
# THE VERDICT, and BOTH directions are required
# --------------------------------------------------------------------------
print()
ok = True
ih1, ih2, ih3n, ih3s, _c, idiff, _d = results["INLINE"]
eh1, eh2, eh3n, eh3s, _c, ediff, _d = results["ERASE"]

if ih1 or ih2 or ih3s:
    ok = False
    print("!! FAILED: the INLINE approximation -- the one src/ir/nfa.c builds "
          "the machine from -- violates H1=%d H2=%d H3sharp=%d. It is supposed "
          "to be EXACT, so any violation is a wave-G bug and not a tolerance."
          % (ih1, ih2, ih3s))
else:
    print("H1/H2/H3 HOLD for the INLINE approximation on every cell "
          "(H3 naive %d, which is 0 for the same reason the others are: the "
          "inlining is exact, so there is no earlier-start conflation to "
          "separate)." % ih3n)

if idiff != 0:
    ok = False
    print("!! FAILED: INLINE(P) differed from P on %d cells AFTER the "
          "equivalence check passed, which cannot happen and means the two "
          "sections are not asking about the same patterns." % idiff)

if not (eh1 or eh3s):
    ok = False
    print("!! FAILED: the ERASE column -- design §8.2's REFUTED approximation "
          "-- violated nothing. A population that cannot distinguish a sound "
          "approximation from an unsound one reports zeros for the INLINE "
          "column and means nothing by them (R32's finding against this "
          "project's own instruments).")
else:
    print("THE CONTROL FIRED: the ERASE approximation violates H1=%d H2=%d "
          "H3sharp=%d on the SAME cells, which is what makes the INLINE row "
          "above a measurement rather than a table of zeros." % (eh1, eh2, eh3s))

print()
print("VERDICT:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
