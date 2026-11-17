#!/usr/bin/env bash
# S3301 -- lane formsfixf (review r37 H6: the lever controls' call).
SAB_ID="S3301-g2-lever-controls-call-deleted"
SAB_FILE="memfn/tests/g2/g2_win_gen.c"
SAB_SUITES="g2win"
SAB_DESC="the lever_controls call deleted: the 'lever controls ok=N of 8' equality must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3301. lane formsfixf 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        lever_controls(&refused_ok);'
SAB_AFTER='        (void)lever_controls;   /* SABOTAGE S3301 */'
