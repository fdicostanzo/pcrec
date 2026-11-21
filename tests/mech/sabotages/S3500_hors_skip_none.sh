#!/usr/bin/env bash
# S3500 -- review r72 CHECKS-1 (lane bsu1fix): hors_skip returns -1: D-hors's probe position is re-tested in the candidate test
# The artifact re-tests a position its search head already proved: every answer stays right, so
# no corpus, oracle or G2 pin sees it. The detector is tests/codegen/run_skip_pins.sh (mech arm
# skippins): the literal counts of the probed/stopped position's spellings in the candidate test.
SAB_ID="S3500-hors-skip-none"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="skippins"
SAB_DESC="hors_skip returns -1: D-hors's probe position is re-tested in the candidate test"
SAB_DOC_FIGURE="tests/codegen/run_skip_pins.sh (arm skippins). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3500."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return ih >= 0 && w->grp[ih] < 0 ? ih : -1;'
SAB_AFTER='    (void)ih; return -1;   /* SABOTAGE S3500 */'
