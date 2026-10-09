#!/usr/bin/env bash
# S730 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- a rung arm left unbracketed (§R4.9.8 C18 row): C18 leg (c) holds the inserted bytes equal to SIMD_GUARDED_BYTES.
SAB_ID='S730-selector-endif-unbracketed'
SAB_FILE='memfn/src/ofsskip.c'
SAB_SUITES='simdfloor'
SAB_DESC='the selector'\''s closing #endif is written outside the simd bracket, so SIMD_GUARDED_BYTES undercounts'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S730. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        o->puts(o->u, "#endif\n");'
SAB_AFTER='        o->simd_close(o->u); o->puts(o->u, "#endif\n"); o->simd_open(o->u, 0);   /* SABOTAGE S730 */'
