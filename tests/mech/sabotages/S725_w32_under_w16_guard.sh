#!/usr/bin/env bash
# S725 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the widest level's arm under the narrowest level's guard: the arm does not compile at the base target.
SAB_ID='S725-w32-under-w16-guard'
SAB_FILE='memfn/src/levels.def'
SAB_SUITES='simdfloor'
SAB_DESC='the widest level is guarded by the narrowest level's guard, so a base-target compile meets the widest level's intrinsics'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S725. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='         "defined(__x86_64__) && !defined(__ILP32__) && defined(__AVX2__)",'
SAB_AFTER='         "defined(__x86_64__) && !defined(__ILP32__) && defined(__SSE2__)",   /* SABOTAGE S725 */'
