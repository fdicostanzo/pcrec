#!/usr/bin/env bash
# S3289 -- lane formsfixd (review r36): G13: the head grid's three copies.
SAB_ID="S3289-grid-rc-heads-drops-24"
SAB_FILE="memfn/tests/g2/g2_win_gen.c"
SAB_SUITES="g2win"
SAB_DESC="the generator's RC_HEADS drops 24 while cards.py's GRID keeps it: run_g2_win.sh's grid assert must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3289. lane formsfixd 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static const int RC_HEADS[] = { 1, 2, 4, 8, 16, 24, 32, 64 };'
SAB_AFTER='static const int RC_HEADS[] = { 1, 2, 4, 8, 16, 32, 64 };   /* SABOTAGE S3289 */'
