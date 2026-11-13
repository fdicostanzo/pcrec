#!/usr/bin/env bash
# S3085 ([MEMFN] plan_frame.md 3.0b, row (S); lane b30b) -- CALL UNSTATED READ AS NONE.
#
# WHAT IT BREAKS AND WHO CATCHES IT: mf_wdecide reads call 0 (UNSTATED) as NONE: the fixture 'call 0 answers -1' is red.
# The detector is tests/memfn/run_finder.sh's purity harness (arm_fixtures
# --purity, plain and, since 3.0b, the MF_TRACE fixture driver too); the
# population probe pins that run_finder.sh still runs the pass this row needs.
SAB_ID="S3085-call-unstated-read-as-none"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='mf_wdecide reads call 0 (UNSTATED) as NONE: the fixture '"'"'call 0 answers -1'"'"' is red'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b, docs/dev/lanes/b30b_report.md), by hand on a copy of memfn/src: plain fx --purity 11 failed. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3085.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (call == MF_WCALL_UNSTATED || call > MF_WCALL_EMIT) return -1;'
SAB_AFTER='    if (call == MF_WCALL_UNSTATED) call = MF_WCALL_NONE;   /* SABOTAGE S3085 */
    if (call > MF_WCALL_EMIT) return -1;'
