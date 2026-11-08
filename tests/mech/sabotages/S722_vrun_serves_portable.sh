#!/usr/bin/env bash
# S722 ([MEMFN] R-13, R4e' batch 1, lane r13, 2026-10-09) -- target served: the SIMD layer renders at a target that admits none of its levels (the portable target, the default). G2's neg-portable class; and C18 finds no mover (ON == OFF, both SIMD), so its population floor is red.
# RE-AIMED 2026-11-08 (lane u3tgt, [XARCH-DEV] U3): unit U2 moved the rows' SIMD gate from the policy word (MF_P_PORTABLE_ONLY, retired) to the art's target field; the plant now lets both vrun rows' `target` field accept every target (each row's `~CM_NO_LEVEL(...)` exclusion nulled; the anchor stops before the level's name).
SAB_ID='S722-vrun-serves-portable'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd simdfloor'
SAB_DESC='the vrun rows serve every target, so -fno-memfn-simd renders SIMD text (the floor rule broken at the default)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S722. docs/dev/lanes/r13_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=2
SAB_BEFORE='= MF_ANY & ~CM_NO_LEVEL('
SAB_AFTER='= MF_ANY | 0 * CM_NO_LEVEL('
