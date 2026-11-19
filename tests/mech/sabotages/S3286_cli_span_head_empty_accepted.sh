#!/usr/bin/env bash
# S3286 -- lane formsfixd (review r36): G10: the CLI lever's strict parse (tests/compound/run_shell_checks.sh (4)'s refused rows).
SAB_ID="S3286-cli-span-head-empty-accepted"
SAB_FILE="cli/main.c"
SAB_SUITES="compound"
SAB_DESC="the CLI lever span-head option accepts an empty value (as head 0): the refused-spelling row must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3286. lane formsfixd 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            int bad = !*v;'
SAB_AFTER='            int bad = 0;   /* SABOTAGE S3286 */'
