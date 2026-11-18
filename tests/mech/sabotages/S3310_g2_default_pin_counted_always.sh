#!/usr/bin/env bash
# S3310 -- lane formsfixh (review r38 J6: the default pins counted directly, held equal to the total).
SAB_ID="S3310-g2-default-pin-counted-always"
SAB_FILE="memfn/tests/g2/g2_win_gen.c"
SAB_SUITES="g2win"
SAB_DESC="the default-state pin counter also counts the force's pins (8 -> 16): the total == default + force equality must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3310. lane formsfixh 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='long_pinned_def += st == 0;'
SAB_AFTER='long_pinned_def += 1;   /* SABOTAGE S3310 */'
