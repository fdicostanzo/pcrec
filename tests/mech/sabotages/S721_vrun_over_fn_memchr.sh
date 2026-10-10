#!/usr/bin/env bash
# S721 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- OVER widened to fn-memchr: answers stay right, so only a CLASS expectation sees it: G2's neg-exact class must render no SIMD text.
SAB_ID='S721-vrun-over-fn-memchr'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the vrun rows sit over fn-memchr too ([r9fu]'\''s filed form shipped unmeasured)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S721. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static const char *const vrun_over[] = { "fn-pair", NULL };'
SAB_AFTER='static const char *const vrun_over[] = { "fn-pair", "fn-memchr", NULL };   /* SABOTAGE S721 */'
