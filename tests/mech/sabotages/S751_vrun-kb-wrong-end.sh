#!/usr/bin/env bash
# S751 ([MEMFN] R-13 follow-up, lane rankuse, 2026-10-09) -- the ranking read from its commonest end: G2's SIMD family's filter-load check.
SAB_ID='S751-vrun-kb-wrong-end'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the vrun filter reads the ranking from its wrong end (the most common position first)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S751. docs/dev/lanes/rankuse_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        int k = p->term[0].offset + p->rank_pos[i];'
SAB_AFTER='        int k = p->term[0].offset + p->rank_pos[p->rank_n - 1 - i];   /* SABOTAGE S751 */'
