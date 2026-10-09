#!/usr/bin/env bash
# S703 ([MEMFN] RQ-3, lane rq3, 2026-10-09) -- the bracket counts each
# guarded region twice. Two detectors in the one arm: the ARITHMETIC (the
# stamp is twice the blocks' bytes and exceeds blocks x the witness row's
# declared bound, 1,700,000 < 2 x 1,620,166: D155 addendum 2's "stamped
# total <= sum of per-row bounds") and, on VM artifacts, the knee
# (pcrec_sb_len_decide's unsigned subtraction wraps, so the rung and
# VM_PROGRAM_BYTES move).
SAB_ID='S703-rq3-bracket-double-counts'
SAB_FILE='src/core/sb.c'
SAB_SUITES='simdguarded'
SAB_DESC="pcrec_sb_simd_close adds each region's uncut bytes to simd_guarded twice"
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S703. docs/dev/lanes/rq3_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    sb->simd_guarded += pcrec_sb_len_uncut(sb) - sb->simd_at_uncut;'
SAB_AFTER='    sb->simd_guarded += 2 * (pcrec_sb_len_uncut(sb) - sb->simd_at_uncut);   /* SABOTAGE S703 */'
