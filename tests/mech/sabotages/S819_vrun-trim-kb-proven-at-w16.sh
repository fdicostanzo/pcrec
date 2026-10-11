#!/usr/bin/env bash
# S819 ([MEMFN] R-16, lane r16b, 2026-10-11) -- the trim takes KB as proven at w16, where the mask no longer reads it. G2's SIMD family (the verify rule, and its answers).
SAB_ID='S819-vrun-trim-kb-proven-at-w16'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the w16 verify skips the ranked KB position although the w16 mask filtered on KA alone'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S819. docs/dev/lanes/r16b_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    unsigned np = vrun_proven(x, k2, proven);'
SAB_AFTER='    unsigned np = vrun_proven(x, vrun_kb(x, &ops_of[MF_NLEVEL - 1]), proven);   /* SABOTAGE S819 */'
