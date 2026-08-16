# S48 — [ENG-BREP] THE ENCLOSING-LOOP TERM DROPPED FROM FOLLOW.
#
# eng_brep_design.md §2.2 computes FOLLOW transitively and INCLUDES FIRST(B)
# for the body B of every enclosing loop, because an enclosing loop can start
# another iteration once the inner quantifier's parent finishes. §8 of that
# note nominated this line as "the single most likely place for a soundness
# bug to be hiding"; the R24 panel attacked it with 42,336 pairs x 200
# subjects and found 0 divergences — and then ran the failing direction,
# where deliberately dropping the enclosing-FIRST term yields 172
# counterexamples [R24 H1]. The line is load-bearing AND correct.
#
# This sabotage is that failing-direction control, committed so it can be
# re-run rather than believed. The family it breaks is
# tests/possessify/patterns.txt's "ENCLOSING LOOPS" block: in `(?:a{0,2}a)+c`
# the inner `a{0,2}`'s follow looks like {a} from inside its own sequence, but
# the enclosing `+` can restart with `a` too, and only the enclosing term
# carries that.
SAB_ID="S48-poss-no-enclosing-first"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="possdiff"
SAB_DESC="FOLLOW loses the FIRST of every enclosing loop's body, so an inner quantifier is possessified against a follow that understates what can come next"
SAB_DOC_FIGURE="tests/possessify/run_possdiff.sh: the nested-quantifier family diverges (R24 H1 measured 172 counterexamples on its own instrument)"
SAB_COUNT=1
SAB_BEFORE="    uint8_t eff[32];
    memcpy(eff, follow, 32);
    bs_or(eff, encl);"
SAB_AFTER="    uint8_t eff[32];
    memcpy(eff, follow, 32);
    /* SABOTAGE S48: bs_or(eff, encl); */"
