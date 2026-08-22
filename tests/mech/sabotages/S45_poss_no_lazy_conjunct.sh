# S45 — [ENG-BREP] THE LAZY CONJUNCT REMOVED, restoring the rule that the R24
# panel refuted.
#
# eng_brep_design.md §2.2's disjointness arm holds unconditionally for a GREEDY
# quantifier and, for a LAZY one, only when the match cannot also END at the
# quantifier. The design note's first version claimed greedy, lazy and
# possessive agree on the span whenever the disjointness arm applies; they do
# not. On a NULLABLE remainder the follow's first-byte test is vacuous — there
# is no first byte to test — so a greedy loop is unharmed (it tops out at the
# exit chain's top, where the vacuous follow succeeds anyway) while a lazy loop
# stops at the BOTTOM of the same chain and reports a shorter span.
#
# Measured effect of the real defect, both oracles agreeing: `a{1,3}?` on
# "aaaa" is (0,1) lazy and (0,3) possessive. 316 diverging cells on the panel's
# instrument, and this lane's differential carries the same family
# (tests/possessify/patterns.txt's "nullable remainder" block).
#
# WHY THIS SABOTAGE IS THE IMPORTANT ONE. The defect was invisible to the
# design lane's own probe for a structural reason — a lazy quantifier has no
# possessive spelling, so its comparison helper returned None and the whole
# preference family left the differential without a word in the output. A
# check that cannot see this is a check that would have shipped the miscompile.
SAB_ID="S45-poss-no-lazy-conjunct"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="possdiff"
SAB_DESC="the lazy-only non-nullable-remainder conjunct dropped: a lazy quantifier on the disjointness arm is possessified even when the match can end at it"
SAB_DOC_FIGURE="tests/possessify/run_possdiff.sh: the lazy nullable-remainder family diverges"
SAB_COUNT=1
SAB_BEFORE='    if (base_ok && disjoint && lazy && may_end)      return false;'
SAB_AFTER='    if (false)                                       return false;  /* SABOTAGE S45 */'
