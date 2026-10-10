#!/usr/bin/env bash
# S723 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- RUN_WORDS counted over BRACKETED text (§R4.9.2.4 says unbracketed only): the stamp line moves ON vs OFF, a deleted line outside the switch's two stamps: C18 leg (c).
SAB_ID='S723-vrun-counts-run-words'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='simdfloor'
SAB_DESC='the guarded verify'\''s run compare counts toward RUN_WORDS, so -fmemfn-simd moves an unguarded stamp'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S723. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    art->words = words;'
SAB_AFTER='    (void)words;   /* SABOTAGE S723 */'
