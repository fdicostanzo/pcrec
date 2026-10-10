#!/usr/bin/env bash
# S740 ([MEMFN] R-13 follow-up, lane rankuse, 2026-10-09) -- entries past rank_n read: G2 fills them with positions a reader would choose (rank_n 0 and 1 modes).
SAB_ID='S740-vrun-kb-ignores-rank-n'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the vrun filter reads ranking entries past rank_n (unspecified ones)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S740. docs/dev/lanes/rankuse_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (unsigned i = 0; i < p->rank_n; i++) {'
SAB_AFTER='    for (unsigned i = 0; i < MF_RANK_MAX; i++) {   /* SABOTAGE S740 */'
