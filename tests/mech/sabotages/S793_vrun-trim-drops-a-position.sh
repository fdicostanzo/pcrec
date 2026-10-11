#!/usr/bin/env bash
# S793 ([MEMFN] R-14, lane r14b, 2026-10-11) -- the trimmed verify dropping a position the filter did not prove. G2's SIMD family (its near-miss answers and its verify-read rule).
SAB_ID='S793-vrun-trim-drops-a-position'
SAB_FILE='memfn/src/runcmp.c'
SAB_SUITES='g2simd'
SAB_DESC='the trimmed words compare also skips the first position after each earlier window: one uncovered position is never compared'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S793. docs/dev/lanes/r14b_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        done = at + w;'
SAB_AFTER='        done = at + w + 1;   /* SABOTAGE S793 */'
