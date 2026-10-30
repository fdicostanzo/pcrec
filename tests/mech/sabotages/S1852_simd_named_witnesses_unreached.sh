#!/usr/bin/env bash
# S1852 (lane fsfix, 2026-10-30) -- the vrun rows stop rendering at the default
# policy under -fmemfn-simd. The named SIMD witnesses of simd_guarded_check.py
# then render no SIMD site, so the simd-form-named floor (the control that does
# not ride the every-Nth corpus sample) is red.
SAB_ID='S1852-simd-named-witnesses-unreached'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='simdguarded'
SAB_DESC='the vrun rows serve only the SIZE policy class, so the named SIMD witnesses render no SIMD form'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1852. docs/dev/lanes/fsfix_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    [FLD_policy]          = CM(NONE) | CM(SIZE),      /* SIMD layer: never PORTABLE, never INLOOP */'
SAB_AFTER='    [FLD_policy]          = CM(SIZE),   /* SABOTAGE S1852 */'
