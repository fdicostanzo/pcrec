#!/usr/bin/env bash
# S648 ([DEC-FALLBACK] B3, lane decfbB3) -- T1 row 6 (prefilter-collapse) loses its deny bit (S-F6): -fno-prefilter-collapse no longer keeps the size-cap rung from collapsing the prefilter
# Live from B3 (the walk is the dispatch, the sets routine the writer).
# Detector: tests/codegen/run_fallback_table.sh (a) seq-pfdrop: -fno-prefilter-collapse -e utf8 (\p{Xwd}) takes prefilter-collapse before drop-prefilter.
SAB_ID='S648-t1_size_collapse_deny_dropped'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="T1 row 6 (prefilter-collapse) loses its deny bit (S-F6): -fno-prefilter-collapse no longer keeps the size-cap rung from collapsing the prefilter"
SAB_DOC_FIGURE='Re-run: bash tests/mech/run_sabotage_matrix.sh S648. docs/dev/lanes/decfbB3_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .name = "prefilter-collapse", .deny = PCREC_NO_PREFILTER_COLLAPSE, .degrading = true,'
SAB_AFTER='    { .name = "prefilter-collapse", .deny = 0, .degrading = true,   /* SABOTAGE S648 */'
