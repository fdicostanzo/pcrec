#!/usr/bin/env bash
# S3288 -- lane formsfixd (review r36): G10: mf_lever's upper bound.
SAB_ID="S3288-mf-lever-top-plus-one"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="g2win"
SAB_DESC="mf_lever's top is one past MF_SPAN_HEAD_MAX: span-head=4096 is accepted, G2's lever controls must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3288. lane formsfixd 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE="        else if ((n = n * 10 + (unsigned long)(*v - '0')) > MF_SPAN_HEAD_MAX) *bad = 1;"
SAB_AFTER="        else if ((n = n * 10 + (unsigned long)(*v - '0')) > MF_SPAN_HEAD_MAX + 1) *bad = 1;   /* SABOTAGE S3288 */"
