#!/usr/bin/env bash
# S795 ([MEMFN] R-14, lane r14b, 2026-10-11) -- the trim's position index off by one. G2's SIMD family.
SAB_ID='S795-vrun-trim-index-off-by-one'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the trim marks the position after the scanned one as proven (its run index off by one)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S795. docs/dev/lanes/r14b_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    proven[np++] = x->k - off;'
SAB_AFTER='    proven[np++] = x->k - off + 1;   /* SABOTAGE S795 */'
