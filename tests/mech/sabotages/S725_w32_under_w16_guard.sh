#!/usr/bin/env bash
# S725 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- C9-x86's plant: the w32 arm under the SSE2 guard does not compile at -march=x86-64.
SAB_ID='S725-w32-under-w16-guard'
SAB_FILE='memfn/src/levels.def'
SAB_SUITES='simdfloor'
SAB_DESC='the w32 level is guarded by the w16 guard (SSE2), so a plain x86-64 compile meets AVX2 intrinsics'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S725. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='         "defined(__x86_64__) && !defined(__ILP32__) && defined(__AVX2__)",'
SAB_AFTER='         "defined(__x86_64__) && !defined(__ILP32__) && defined(__SSE2__)",   /* SABOTAGE S725 */'
