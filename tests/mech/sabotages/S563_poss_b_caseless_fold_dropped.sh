# S563 — [ART-POSS-ARMS]: ARM B IGNORES A CASELESS REFERENCE
# (src/opt/possessify.c; docs/design/poss_arms.md rev 2.1 §8.2's plant row,
# lane possbuild).
#
# The compare is caseless when the REFERENCE is (D62), so FIRST(\n) must be
# folded (§3.2). Witness `(a)A+(?i:\1)` on "aAA": 10.46 (0,3), the plant
# NOMATCH.
# Detectors (§8.1 item 5): the oracle-side .rxt cells in
# tests/possessify/possessify.rxt (harness) and the exhaustive possdiff
# (possdiff). REACH (§8.1 item 2) is SAB_REACH_POP: the witness is in the
# swept population.
SAB_ID="S563-poss-b-caseless-fold-dropped"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/possessify/possessify.rxt"
SAB_DESC='arm B never folds a caseless reference'\''s FIRST'
SAB_DOC_FIGURE="PREDICTED: harness on tests/possessify/possessify.rxt fails the witness block; possdiff diverges (or, for a termination/R-5 row, refuses) on it. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S563."
# [MECH-REACH] the site answers at HEAD: the stamp on a pattern whose verdict
# runs through the planted line.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern '\''(a)x+\1'\'' && grep -q "^#define RX_VM_POSS_ARMS 0x4u$" "$REACH_TMP/o.c" && echo REACH-S563'
SAB_REACH_EXPECT="REACH-S563"
SAB_REACH_POP='tests/possessify/possessify.rxt|^pattern \(a\)A\+\(\?i:\\1\)$|1
tests/possessify/arms_reach.tsv|^\(a\)A\+\(\?i:\\1\)[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (a->u.bref.caseless) bref_fold(q->cx, a->u.bref.ucp, acc.f);'
SAB_AFTER='    /* SABOTAGE S563: caseless reference not folded */'
