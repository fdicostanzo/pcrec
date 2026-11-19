#!/usr/bin/env bash
# S3304 -- lane formsfixf (review r37 H5: the force's pinned counter).
SAB_ID="S3304-g2-force-pin-uncounted"
SAB_FILE="memfn/tests/g2/g2_win_gen.c"
SAB_SUITES="g2win"
SAB_DESC="the force's long pins no longer counted apart: the split floors must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3304. lane formsfixf 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='long_pinned_force += st == 2;'
SAB_AFTER='long_pinned_force += 0;   /* SABOTAGE S3304 */'
