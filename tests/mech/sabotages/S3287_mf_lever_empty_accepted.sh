#!/usr/bin/env bash
# S3287 -- lane formsfixd (review r36): G10: mf_lever's strict parse (g2_win_gen.c lever_controls).
SAB_ID="S3287-mf-lever-empty-accepted"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="g2win"
SAB_DESC="mf_lever accepts span-head= with no digits (as head 0): G2's lever controls must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3287. lane formsfixd 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    *bad = !*v;'
SAB_AFTER='    *bad = 0;   /* SABOTAGE S3287 */'
