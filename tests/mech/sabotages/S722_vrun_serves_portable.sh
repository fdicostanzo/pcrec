#!/usr/bin/env bash
# S722 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- policy served: the SIMD layer renders under MF_P_PORTABLE_ONLY. G2's neg-portable class; and C18 finds no mover (ON == OFF, both SIMD), so its population floor is red.
SAB_ID='S722-vrun-serves-portable'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd simdfloor'
SAB_DESC='the vrun rows serve every policy, so -fno-memfn-simd renders SIMD text (the floor rule broken at the default)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S722. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    [FLD_policy]          = CM(NONE) | CM(SIZE),      /* SIMD layer: never PORTABLE, never INLOOP */'
SAB_AFTER='    [FLD_policy]          = MF_ANY,   /* SABOTAGE S722 */'
