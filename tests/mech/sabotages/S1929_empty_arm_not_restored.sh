#!/usr/bin/env bash
# S1929 (lane sae2, 2026-11-09; span_arms E2, the walk-parameter table,
# docs/design/span_arms.md §3.7; manager ruling R1) -- T3's E-1 ROW IGNORES THE
# `empty` ARM.
#
# T3 row E-1 (src/facts/req.c `rb_zero_rows`: an `A_EMPTY` node is the unit)
# restores under the `empty` arm, so `--harness=restore=empty` runs the old cut
# and `make test-axes` compares the two forms. This plant drops the row's arm,
# so under the lever `abcd()efgh` keeps the joined run while the listing still
# names the arm. Detector: tests/codegen/run_facts_checks.sh [facts-arm].
SAB_ID="S1929-empty-arm-not-restored"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC="the zero-width rows' E-1 row (the empty string) carries no restored arm, so the harness lever's old form (the cut) is never produced for it while the listing still names the arm"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sae2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1929."
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --features all --harness=restore=empty --emit-facts --pattern "abcd()efgh" | grep -qP "^byte\treq_whole_run\t.*\t61626364\tharness:empty\t" && echo REACH-EMPTY-ARM-RESTORES'
SAB_REACH_EXPECT="REACH-EMPTY-ARM-RESTORES"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { rb_zero_empty,    RB_ZERO_EMPTY, PCREC_WALK_ARM(EMPTY) },'
SAB_AFTER='    { rb_zero_empty,    RB_ZERO_EMPTY, 0 },   /* SABOTAGE S1929 */'
