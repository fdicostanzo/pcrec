#!/usr/bin/env bash
# S1921 (lane sar1, 2026-11-09; span_arms R1, the walk-parameter table, docs/design/span_arms.md §3.7) -- THE `rep` ARM DOES NOT RESTORE ROW 2.
#
# Each power-arm row of `rb_rep_rows` (src/facts/req.c) names the restored
# arm `rep` (src/facts/walk_arms.def) that passes it over, so
# `--harness=restore=rep` runs today's best-only copy and `make test-axes`
# compares the two forms. This plant drops the arm from the exact-repeat row:
# the lever then compares the new form with itself for every `X{m}`.
# Detector: tests/codegen/run_facts_checks.sh [facts-rep].
SAB_ID="S1921-rep-row-not-restored"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC="the exact-repeat row of the necessary-run walk names no restored arm, so the harness lever's old form is never produced for an exact repeat while the listing still names the arm"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sar1_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1921."
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --features all --harness=restore=rep --emit-facts --pattern "xy(?:ab){2}zw" | grep -qP "^byte\treq_whole_run\t.*\t7a77\tharness:rep\t" && echo REACH-REP-RESTORES'
SAB_REACH_EXPECT="REACH-REP-RESTORES"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { rb_rep_exact,  RB_REP_EXACT, PCREC_WALK_ARM(REP) },'
SAB_AFTER='    { rb_rep_exact,  RB_REP_EXACT, 0 /* SABOTAGE S1921 */ },'
# RE-AIMED REACH (lane sar1fix, 2026-11-09, review r5): under the restored arm
# the best-only copy's three 2-byte runs tie and go to the rarest scan byte,
# `zw`; the plant keeps the new run `xyababzw`.
