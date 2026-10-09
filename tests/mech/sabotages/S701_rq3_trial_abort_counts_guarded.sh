#!/usr/bin/env bash
# S701 ([MEMFN] RQ-3, lane rq3, 2026-10-09) -- the size-term ladder's scratch
# abort (sb_grow) counts guarded bytes again, so SIMD text could abort a
# trial the cap it stands in for would admit, and move the ladder's K.
# Reached only through a ladder that runs: the witness's VM artifacts carry
# two blocks (3.24 MB) past the trial bound (3 x 1,000,000), so NEST8's
# trials abort and its UNROLL_K moves (the `ladder` named witness).
SAB_ID='S701-rq3-trial-abort-counts-guarded'
SAB_FILE='src/core/sb.c'
SAB_SUITES='simdguarded'
SAB_DESC="the ladder trial's scratch abort reads the uncut length, guarded bytes included, so a trial aborts on SIMD text"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S701. docs/dev/lanes/rq3_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (sb->abort_over && !sb->simd_open &&
        pcrec_sb_len_decide(sb) + need > sb->abort_over && sb->cx)'
SAB_AFTER='    if (sb->abort_over &&   /* SABOTAGE S701 */
        pcrec_sb_len_uncut(sb) + need > sb->abort_over && sb->cx)'
