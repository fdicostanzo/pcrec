#!/usr/bin/env bash
# S3517 ([MEMFN] R-47 unit U3, lane bsu3fix, review r76 CHECKS-2, 2026-11-21) -- a FAILED or
# timed-out -O0 compile is green again for the always_inline (V) selectors, as U3 first wrote it.
# The in-script control hands o0_compile_issues a failed and a timed-out result for the clean V
# mover's selectors and demands an issue for each one.
SAB_ID='S3517-o0-failed-compile-silent-for-v'
SAB_FILE='tests/memfn/simd_floor_check.py'
SAB_SUITES='simdfloor'
SAB_DESC='a failed -O0 compile records no issue for the selectors of the vector span (the always_inline ones)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3517. docs/dev/lanes/bsu3fix_report.md carries the lane run.'
SAB_REACH_POP='tests/memfn/simd_floor_check.py|^        why = .timeout. if r is None else|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE="        why = 'timeout' if r is None else"
SAB_AFTER=$'        if any("_vs" in fn for fn in sel): return []   # SABOTAGE S3517\n        why = \'timeout\' if r is None else'
