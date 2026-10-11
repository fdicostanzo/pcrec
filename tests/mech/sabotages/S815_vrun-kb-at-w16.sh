#!/usr/bin/env bash
# S815 ([MEMFN] R-16, lane r16b, 2026-10-11) -- KB re-enabled at w16 (D147 addendum 16 undone). G2's SIMD family (the per-level filter rule) and the cli (?i)cat case.
SAB_ID='S815-vrun-kb-at-w16'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='cli g2simd'
SAB_DESC='the w16 level reads two filter positions: its helper ANDs KB into the mask again'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S815. docs/dev/lanes/r16b_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                     1 /* KA alone, D147 addendum 16 */ },'
SAB_AFTER='                     2 /* KA alone, D147 addendum 16 */ },   /* SABOTAGE S815 */'
