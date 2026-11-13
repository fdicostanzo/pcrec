#!/usr/bin/env bash
# S3079 ([MEMFN] plan_frame.md 3.0b, row (E2); lane b30b) -- PLAN FRAME PART EFUNC GENERIC.
#
# WHAT IT BREAKS AND WHO CATCHES IT: the plan function's frame part reports E-generic where E-func renders (a fault that moves no text): the agreement is red because its define side's frame part is the STORED record (plan_frame.md §4.1's field map), never the plan function.
# The detector is tests/memfn/run_finder.sh's purity harness (arm_fixtures
# --purity, plain and, since 3.0b, the MF_TRACE fixture driver too); the
# population probe pins that run_finder.sh still runs the pass this row needs.
SAB_ID="S3079-plan-frame-part-efunc-generic"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='the plan function'"'"'s frame part reports E-generic where E-func renders (a fault that moves no text): the agreement is red because its define side'"'"'s frame part is the STORED record (plan_frame.md §4.1'"'"'s field map), never the plan function'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b, docs/dev/lanes/b30b_report.md), by hand on a copy of memfn/src: plain fx --purity 0 failed (no fixture reads the fault: it moves no text), traced fxt --purity 2025 failed (the agreement). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3079.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fxt" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    fp->erow = (wf_frame_row)r;'
SAB_AFTER='    fp->erow = r == E_FUNC ? E_GENERIC : (wf_frame_row)r;   /* SABOTAGE S3079 */'
