#!/usr/bin/env bash
# S3321 -- lane formsfixj (review r39 K10: the 4095 row prints its OWN call's stderr).
SAB_ID="S3321-cli-span-head-max-minus-one"
SAB_FILE="cli/main.c"
SAB_SUITES="compound"
SAB_DESC="the CLI refuses the largest head (MAX - 1 bound): section (4)'s 4095 row must red (and carry the CLI's own refusal text, per-head stderr)"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3321. lane formsfixj 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE="(n = n * 10 + (unsigned long)(*v - '0')) > MF_SPAN_HEAD_MAX;"
SAB_AFTER="(n = n * 10 + (unsigned long)(*v - '0')) > MF_SPAN_HEAD_MAX - 1;   /* SABOTAGE S3321 */"
