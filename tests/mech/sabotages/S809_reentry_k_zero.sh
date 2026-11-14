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
# RE-AIMED 2026-11-13 (lane s2tri, [RUN-POS-SET] flip 2 -> 128): the probe's
# witness dotted4 `(?:\d{1,3}\.){3}\d{1,3}` no longer hands off on the BYTE
# landmark '.': `\d` is now a run POSITION, so it hands off on the run
# [30-39]2e[30-39]@1 at K 2 (RX_REQ_HANDOFF "2", RX_REQ_RUN not none) and
# the probe's HANDOFF "3" read UNREACHED. The re-entry site itself is still
# reached (dotted4 re-enters at K 2), but this row's detector is handoff.rxt's
# dense-landmark BYTE blocks, so the probe now reads its loglines ipv4 block
# (byte landmark '.', dead dots before matches, RX_REQ_HANDOFF "3",
# RX_REQ_RUN "none", prefilter handoff, measured on the tip).
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o1.c" --pattern '\''(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])'\'' && grep -q '\''^#define RX_DFA_PREFILTER "handoff"'\'' "$REACH_TMP/o1.c" && grep -q '\''^#define RX_REQ_HANDOFF "3"'\'' "$REACH_TMP/o1.c" && grep -q '\''^#define RX_REQ_RUN "none"'\'' "$REACH_TMP/o1.c" && echo REACH-BYTE-REENTRY'
SAB_REACH_EXPECT='REACH-BYTE-REENTRY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "%s        %s = landmark_position - %lld;\n", ind, pos, k);'
SAB_AFTER='        pcrec_sb_printf(c, "%s        %s = landmark_position - %lld;\n", ind, pos, 0LL);   /* SABOTAGE S809 */'
