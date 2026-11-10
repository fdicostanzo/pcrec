#!/usr/bin/env bash
# S1922 (lane sar1fix, 2026-11-09; review 2026-11-09 r5 CHECK-1, span_arms §3.7) -- THE `rep` ARM DOES NOT RESTORE ROW 3.
#
# T2 row 3 of `rb_rep_rows` (src/facts/req.c), the variable repeat `X{m,n}`,
# names the restored arm `rep` (src/facts/walk_arms.def) beside row 2 (S1921's),
# so `--harness=restore=rep` runs the best-only copy for a variable repeat too.
# This plant drops the arm from row 3: the lever then compares the new form
# with itself for every variable repeat. `xy(?:ab){1,2}zw` restored lists `zw`
# (the best-only copy's three 2-byte runs go to the rarest scan byte); planted,
# today's `abzw`. Detector: tests/codegen/run_facts_checks.sh [facts-rep].
SAB_ID="S1922-rep-split-row-not-restored"
SAB_FILE="src/facts/req.c"
SAB_SUITES="facts"
SAB_DESC="the variable-repeat row of the necessary-run walk names no restored arm, so the harness lever's old form is never produced for a variable repeat while the listing still names the arm"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/sar1fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1922."
SAB_REACH='"$(dirname "$PCREC")/pcrec-harness" --features all --harness=restore=rep --emit-facts --pattern "xy(?:ab){1,2}zw" | grep -qP "^byte\treq_whole_run\t.*\t7a77\tharness:rep\t" && echo REACH-REP-SPLIT-RESTORES'
SAB_REACH_EXPECT="REACH-REP-SPLIT-RESTORES"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { rb_rep_any,    RB_REP_SPLIT, PCREC_WALK_ARM(REP) },'
SAB_AFTER='    { rb_rep_any,    RB_REP_SPLIT, 0 /* SABOTAGE S1922 */ },'
