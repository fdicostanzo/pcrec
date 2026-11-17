#!/usr/bin/env bash
# S3311 -- lane formsfixh (review r38 J6: the default pins' own floor).
SAB_ID="S3311-g2-default-pin-uncounted"
SAB_FILE="memfn/tests/g2/g2_win_gen.c"
SAB_SUITES="g2win"
SAB_DESC="the default-state pin counter counts nothing: its own floor (and the total equality) must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3311. lane formsfixh 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='long_pinned_def += st == 0;'
SAB_AFTER='long_pinned_def += 0;   /* SABOTAGE S3311 */'
