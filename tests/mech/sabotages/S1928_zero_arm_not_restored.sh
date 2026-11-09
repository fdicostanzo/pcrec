#!/usr/bin/env bash
# S1928 (lane sae2, 2026-11-09; span_arms E2, the walk-parameter table,
# docs/design/span_arms.md §3.7) -- T3's E-4 ROW IGNORES THE `zero` ARM.
#
# Each new row of T3 (src/facts/req.c `rb_zero_rows`) carries the restored
# arm that passes it over, so `--harness=restore=zero` runs today's cut and
# `make test-axes` compares the two forms. This plant drops the E-4 row's arm,
# so under the lever `foo\bbar` keeps the joined run while the listing still
# names the arm: the sweep compares the new form with itself. Detector:
# tests/codegen/run_facts_checks.sh [facts-arm] (the run under the lever is
# the new one).
SAB_ID="S1928-zero-arm-not-restored"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC="the zero-width rows' E-4 row carries no restored arm, so the harness lever's old form (the cut) is never produced for an assertion while the listing still names the arm"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sae2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1928."
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --features all --harness=restore=zero --emit-facts --pattern "foo\\bbar" | grep -qP "^byte\treq_whole_run\t.*\t626172\tharness:zero\t" && echo REACH-ZERO-ARM-RESTORES'
SAB_REACH_EXPECT="REACH-ZERO-ARM-RESTORES"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { rb_zero_any,      RB_ZERO_UNIT, PCREC_WALK_ARM(ZERO) },'
SAB_AFTER='    { rb_zero_any,      RB_ZERO_UNIT, 0 },   /* SABOTAGE S1928 */'
