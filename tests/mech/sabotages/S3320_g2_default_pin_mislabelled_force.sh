#!/usr/bin/env bash
# S3320 -- lane formsfixj (review r39 K7: J6's one-token mislabel).
SAB_ID="S3320-g2-default-pin-mislabelled-force"
SAB_FILE="memfn/tests/g2/g2_win_gen.c"
SAB_SUITES="g2win"
SAB_DESC="the default-state pin counter tests the force's state (st == 2): a one-state head pass reads pinned_def=0, its floor and equality must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3320. lane formsfixj 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='long_pinned_def += st == 0;'
SAB_AFTER='long_pinned_def += st == 2;   /* SABOTAGE S3320 */'
