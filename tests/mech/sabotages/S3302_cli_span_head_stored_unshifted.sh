#!/usr/bin/env bash
# S3302 -- lane formsfixf (review r37 H8: the CLI half of the forwarded value).
SAB_ID="S3302-cli-span-head-stored-unshifted"
SAB_FILE="cli/main.c"
SAB_SUITES="compound"
SAB_DESC="the CLI stores n, not n + 1 (the kit is sent one less): the accepted lever rows' forwarded-head comparison must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3302. lane formsfixf 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            st->harness.span_head = (unsigned)n + 1;'
SAB_AFTER='            st->harness.span_head = (unsigned)n;   /* SABOTAGE S3302 */'
