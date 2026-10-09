#!/usr/bin/env bash
# S702 ([MEMFN] RQ-3, lane rq3, 2026-10-09) -- the splice stops carrying the
# guarded record: the VM program's guarded bytes reach the artifact's buffer
# uncounted, so the caps see them and the stamp under-reports them. Detected
# twice on the witness's VM artifacts: refusals (the block's code exceeds
# the caps) and, had they compiled, a stamp short by one block.
SAB_ID='S702-rq3-splice-drops-record'
SAB_FILE='src/core/sb.c'
SAB_SUITES='simdguarded'
SAB_DESC="pcrec_sb_splice copies the text without its guarded record"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S702. docs/dev/lanes/rq3_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    dst->simd_guarded     += src->simd_guarded;'
SAB_AFTER='    dst->simd_guarded     += 0;   /* SABOTAGE S702 */
    return;'
