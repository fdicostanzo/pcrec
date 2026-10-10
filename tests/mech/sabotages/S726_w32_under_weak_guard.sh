#!/usr/bin/env bash
# S726 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- the widest level's arm under a guard one level too weak: it compiles at a mid target and fails at an older one.
SAB_ID='S726-w32-under-weak-guard'
SAB_FILE='memfn/src/levels.def'
SAB_SUITES='simdfloor'
SAB_DESC='the widest level is guarded by the next-lower level's guard, so an older target meets the widest level's intrinsics'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S726. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='         "defined(__x86_64__) && !defined(__ILP32__) && defined(__AVX2__)",'
SAB_AFTER='         "defined(__x86_64__) && !defined(__ILP32__) && defined(__AVX__)",   /* SABOTAGE S726 */'
