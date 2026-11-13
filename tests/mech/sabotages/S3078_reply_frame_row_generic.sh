#!/usr/bin/env bash
# S3078 ([MEMFN] plan_frame.md 3.0b, row (E); lane b30b) -- REPLY FRAME ROW GENERIC.
#
# WHAT IT BREAKS AND WHO CATCHES IT: the reply's frame part writes E-generic as every framed ask's frame row: the kit's MF_TRACE agreement at every window-site define (compose.c define_sel, plan_frame.md §4.1) is red on run_finder.sh's TRACED --purity pass (its 81 E-func defines).
# The detector is tests/memfn/run_finder.sh's purity harness (arm_fixtures
# --purity, plain and, since 3.0b, the MF_TRACE fixture driver too); the
# population probe pins that run_finder.sh still runs the pass this row needs.
SAB_ID="S3078-reply-frame-row-generic"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="memfnfinder"
SAB_DESC='the reply'"'"'s frame part writes E-generic as every framed ask'"'"'s frame row: the kit'"'"'s MF_TRACE agreement at every window-site define (compose.c define_sel, plan_frame.md §4.1) is red on run_finder.sh'"'"'s TRACED --purity pass (its 81 E-func defines)'
SAB_DOC_FIGURE='Validated by plant at 3.0b (lane b30b, docs/dev/lanes/b30b_report.md), by hand on a copy of memfn/src: plain fx --purity 3 failed (the EMIT fixture), traced fxt --purity 2028 failed (the agreement). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3078.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fxt" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    snprintf(out->frame_row, sizeof out->frame_row, "%s", wf_frame_name(fp->erow));'
SAB_AFTER='    snprintf(out->frame_row, sizeof out->frame_row, "%s", wf_frame_name(E_GENERIC));   /* SABOTAGE S3078 */'
