#!/usr/bin/env bash
# S3312 -- lane formsfixh (review r38 J5: the forwarded-value grep names the true cause).
SAB_ID="S3312-cli-span-head-stored-plus-two"
SAB_FILE="cli/main.c"
SAB_SUITES="compound"
SAB_DESC="the CLI stores n + 2: the absolute '_j = 8; for (' grep must red with the forwarded-head text, not 'vacuous'"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3312. lane formsfixh 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            st->harness.span_head = (unsigned)n + 1;'
SAB_AFTER='            st->harness.span_head = (unsigned)n + 2;   /* SABOTAGE S3312 */'
