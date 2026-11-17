#!/usr/bin/env bash
# S3300 -- lane formsfixf (review r37 H5: the default pass's pin).
SAB_ID="S3300-g2-pin-head-unpinned"
SAB_FILE="memfn/tests/g2/g2_win_gen.c"
SAB_SUITES="g2win"
SAB_DESC="pin_head() returns the pass's own head (the shipped-literal pin deleted): the default pass's pinned-sites floor must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3300. lane formsfixf 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static int pin_head(void) { return g_head < 0 ? G2W_SHIPPED_HEAD : g_head; }'
SAB_AFTER='static int pin_head(void) { return g_head; }   /* SABOTAGE S3300 */'
