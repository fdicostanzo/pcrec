#!/usr/bin/env bash
# S750 ([MEMFN] R-13 follow-up, lane rankuse, 2026-10-09) -- KB taken from the run's end instead of the ranking: G2's SIMD family holds every rendered filter's loads to the rule over its generated rankings.
SAB_ID='S750-vrun-kb-ignores-rank-pos'
SAB_FILE='memfn/src/vrun.c'
SAB_SUITES='g2simd'
SAB_DESC='the vrun filter KB ignores the ranked positions (it takes the run tail positions in turn instead)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S750. docs/dev/lanes/rankuse_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        int k = p->term[0].offset + p->rank_pos[i];'
SAB_AFTER='        int k = p->term[0].offset + (int)p->term[0].run_len - 1 - (int)i;   /* SABOTAGE S750 */'
