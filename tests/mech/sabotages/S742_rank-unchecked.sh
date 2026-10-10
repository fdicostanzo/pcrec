#!/usr/bin/env bash
# S742 ([MEMFN] R-13 follow-up, lane rankuse, 2026-10-09) -- the ranking's vocabulary rule off: G2's SIMD family's malformed copies must be refused.
SAB_ID='S742-rank-unchecked'
SAB_FILE='memfn/src/compose.c'
SAB_SUITES='g2simd'
SAB_DESC='mf_define accepts a malformed position ranking (positions outside the run, twice, rank_n past the run or MF_RANK_MAX)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S742. docs/dev/lanes/rankuse_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (p->rank_n == 0) return 1;'
SAB_AFTER='    return 1;   /* SABOTAGE S742 */'
