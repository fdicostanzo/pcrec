#!/usr/bin/env bash
# S809 ([REQ-HANDOFF-L1], lane rlhbuild) -- THE RE-ENTRY JUMPS TO THE LANDMARK
# ITSELF (K = 0 at the re-entry; the entry keeps its K): every match that
# begins before its landmark and after a restart is lost. The K = 0 plant is
# the visible one (K - 1 .. 1 are equivalent mutants on the reverse-pass
# bodies, rlhtwin_report.md §2.2). Detector: tests/litscan/handoff.rxt.
SAB_ID='S809-reentry-k-zero'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_HARNESS_TARGET='tests/litscan/handoff.rxt'
SAB_DESC='the forward scan'\''s re-entered handoff moves the scan to the landmark'\''s hit itself rather than K bytes before it, losing matches that begin before their landmark'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rlhbuild_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S809.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:\d{1,3}\.){3}\d{1,3}'\'' && grep -q '\''^#define RX_DFA_PREFILTER "handoff"'\'' "$REACH_TMP/o.c" && grep -q '\''^#define RX_REQ_HANDOFF "3"'\'' "$REACH_TMP/o.c" && echo REACH-BYTE-REENTRY'
SAB_REACH_EXPECT='REACH-BYTE-REENTRY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "%s        %s = landmark_position - %lld;\n", ind, pos, k);'
SAB_AFTER='        pcrec_sb_printf(c, "%s        %s = landmark_position - %lld;\n", ind, pos, 0LL);   /* SABOTAGE S809 */'
