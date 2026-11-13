#!/usr/bin/env bash
# S3088 ([MEMFN] plan_frame.md 3.0b, row (V); lane b30b) -- PLAN FACE CALLS MEMBER.
#
# WHAT IT BREAKS AND WHO CATCHES IT: the plan face calls the define hooks' member callback: the counting hook, stating all six callbacks in the call fixtures, reads 1.
# The detector is tests/memfn/run_finder.sh's purity harness (arm_fixtures
# --purity, plain and, since 3.0b, the MF_TRACE fixture driver too); the
# population probe pins that run_finder.sh still runs the pass this row needs.
SAB_ID="S3088-plan-face-calls-member"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='the plan face calls the define hooks'"'"' member callback: the counting hook, stating all six callbacks in the call fixtures, reads 1'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b, docs/dev/lanes/b30b_report.md), by hand on a copy of memfn/src: plain fx --purity 11 failed. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3088.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (framed_refused(art, site)) return -1;'
SAB_AFTER='    if (def && def->member) def->member(def->u, 0, "b");   /* SABOTAGE S3088 */
    if (framed_refused(art, site)) return -1;'
