#!/usr/bin/env bash
# S808 ([REQ-HANDOFF-L1], lane rlhbuild) -- THE RE-ENTRY RE-ASKS THE GATE ONE
# BYTE LATE: its lower bound is `scan_position + 1`, so a landmark sitting AT
# the restart position is skipped and the next, LATER occurrence is taken (the
# re-entry's S464): a match whose landmark is there is jumped past.
# Detector: tests/litscan/handoff.rxt's dense-landmark byte blocks.
SAB_ID='S808-reentry-later-occurrence'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_HARNESS_TARGET='tests/litscan/handoff.rxt'
SAB_DESC='the forward scan'\''s re-entered handoff searches for the landmark from one byte past the restart position, so it can return a later occurrence than the least one and skip a match'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rlhbuild_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S808.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:\d{1,3}\.){3}\d{1,3}'\'' && grep -q '\''^#define RX_DFA_PREFILTER "handoff"'\'' "$REACH_TMP/o.c" && grep -q '\''^#define RX_REQ_HANDOFF "3"'\'' "$REACH_TMP/o.c" && echo REACH-BYTE-REENTRY'
SAB_REACH_EXPECT='REACH-BYTE-REENTRY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        .s = "subject", .n = "subject_length", .lo = posvar, .indent = indent,
        .on_miss = REQ_ON_MISS, .result = "landmark_position",'
SAB_AFTER='        .s = "subject", .n = "subject_length", .lo = dfa_fragf(cx, "%s + 1", posvar), .indent = indent,   /* SABOTAGE S808 */
        .on_miss = REQ_ON_MISS, .result = "landmark_position",'
