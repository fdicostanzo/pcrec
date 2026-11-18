#!/usr/bin/env bash
# S3285 -- lane formsfixd (review r36): G1: THE SHIPPED HEAD UNPINNED. WF_SPAN_HEAD 64 -> 63; G2's default pass pins its loops at its own literal 64 (exact pin, nothing below), and its per-family counts equal the head-64 pass's.
SAB_ID="S3285-shipped-head-63"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="g2win"
SAB_DESC="the shipped span head is 63, not G2's literal 64: G2's default pass pin and its equality with the head-64 pass must red"
SAB_DOC_FIGURE="Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3285. lane formsfixd 2026-11-17."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='enum { WF_SPAN_HEAD = 64 };'
SAB_AFTER='enum { WF_SPAN_HEAD = 63 };   /* SABOTAGE S3285 */'
