#!/usr/bin/env bash
# S700 ([MEMFN] RQ-3, lane rq3, 2026-10-09) -- the caps' decision view drops
# the guarded text's subtraction (D155 item 9 undone): the size term, its
# ladder, both D84 caps and every figure a refusal or --warn-emit-bytes note
# quotes would count SIMD bytes. Invisible on the plain build; the witness
# block's code alone exceeds both caps, so every witness compile refuses.
SAB_ID='S700-rq3-caps-count-guarded'
SAB_FILE='src/core/sb.c'
SAB_SUITES='simdguarded'
SAB_DESC="pcrec_sb_size_decide stops subtracting the guarded text: the caps, the size term and the quoted sizes count SIMD bytes"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S700. docs/dev/lanes/rq3_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    z.total  -= sb->simd_size.total;'
SAB_AFTER='    z.total  -= 0;   /* SABOTAGE S700 */'
