#!/usr/bin/env bash
# S726 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- C9-x86's plant: the w32 arm under an AVX-only guard compiles at x86-64-v3 and fails at sandybridge.
SAB_ID='S726-w32-under-avx-guard'
SAB_FILE='memfn/src/levels.def'
SAB_SUITES='simdfloor'
SAB_DESC='the w32 level is guarded by __AVX__ (AVX without AVX2 admits it), so sandybridge meets AVX2 intrinsics'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S726. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='         "defined(__x86_64__) && !defined(__ILP32__) && defined(__AVX2__)",'
SAB_AFTER='         "defined(__x86_64__) && !defined(__ILP32__) && defined(__AVX__)",   /* SABOTAGE S726 */'
