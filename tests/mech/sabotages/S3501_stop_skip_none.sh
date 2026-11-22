#!/usr/bin/env bash
# S3501 -- review r72 CHECKS-1 (lane bsu1fix): stop_skip returns -1: the search's stop position is re-tested in the candidate test
# The artifact re-tests a position its search head already proved: every answer stays right, so
# no corpus, oracle or G2 pin sees it. The detector is tests/codegen/run_skip_pins.sh (mech arm
# skippins): the literal counts of the probed/stopped position's spellings in the candidate test.
SAB_ID="S3501-stop-skip-none"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="skippins"
SAB_DESC="stop_skip returns -1: the search's stop position is re-tested in the candidate test"
SAB_DOC_FIGURE="tests/codegen/run_skip_pins.sh (arm skippins). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3501."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return w->stop_alone ? w->stop_ix : -1;'
SAB_AFTER='    (void)w; return -1;   /* SABOTAGE S3501 */'
