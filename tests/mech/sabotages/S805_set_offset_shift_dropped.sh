#!/usr/bin/env bash
# S805 ([REQ-HANDOFF-L1], lane rlhbuild) -- THE SET OFFSETS LOSE THE LEFT
# FACTOR'S WIDTH: `rb_union` stores a right factor's member at its own offset,
# not `lmaxw + off`, so every byte landmark's K is understated -- dotted4's '.'
# reads K = 0 (the scan starts AT the landmark: the K = 0 plant, which
# rlhtwin measured visible where K - 1 .. 1 are equivalent mutants).
# Detectors: tests/litscan/handoff.rxt's byte-landmark blocks (answers) and
# run_prechecks.sh §5.12a's hand K table (structural).
SAB_ID='S805-set-offset-shift-dropped'
SAB_FILE='src/facts/req.c'
SAB_SUITES='harness prechecks'
SAB_HARNESS_TARGET='tests/litscan/handoff.rxt'
SAB_DESC='the necessary-set walk stores a right factor'\''s member at its own offset instead of after the left factor'\''s maximum width, so a byte landmark'\''s K is understated (dotted4'\''s K becomes 0) and the handoff starts the scan after matches that begin before the landmark'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rlhbuild_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S805.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:\d{1,3}\.){3}\d{1,3}'\'' && grep -q '\''^#define RX_DFA_PREFILTER "handoff"'\'' "$REACH_TMP/o.c" && grep -q '\''^#define RX_REQ_HANDOFF "3"'\'' "$REACH_TMP/o.c" && echo REACH-BYTE-REENTRY'
SAB_REACH_EXPECT='REACH-BYTE-REENTRY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        ro = pcrec_sat_add(lmaxw, r.off[i], PCREC_W_UNBOUNDED);'
SAB_AFTER='        ro = r.off[i];   /* SABOTAGE S805 */'
