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
# RE-AIMED 2026-11-13 (lane s2tri, [RUN-POS-SET] flip 2 -> 128): the probe's
# witness dotted4 `(?:\d{1,3}\.){3}\d{1,3}` no longer hands off on the BYTE
# landmark '.': `\d` is now a run POSITION, so it hands off on the run
# [30-39]2e[30-39]@1 at K 2 (RX_REQ_HANDOFF "2", RX_REQ_RUN not none) and
# the probe's HANDOFF "3" read UNREACHED. The probe now reads the row's two
# detectors' own byte-landmark witnesses: run_prechecks.sh §5.12a's
# dotted4 shape `(?:.{1,3}\.){3}.{1,3}` (re-aimed there in 3d70b9997, its row
# names S805) and handoff.rxt's loglines ipv4 block (the '.' after a
# width-3 alternation, K = lmaxw = 3): both RX_REQ_HANDOFF "3", RX_REQ_RUN
# "none", prefilter handoff, measured on the tip.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o1.c" --pattern '\''(?:.{1,3}\.){3}.{1,3}'\'' && grep -q '\''^#define RX_DFA_PREFILTER "handoff"'\'' "$REACH_TMP/o1.c" && grep -q '\''^#define RX_REQ_HANDOFF "3"'\'' "$REACH_TMP/o1.c" && grep -q '\''^#define RX_REQ_RUN "none"'\'' "$REACH_TMP/o1.c" && "$PCREC" --features all -p rx -o "$REACH_TMP/o2.c" --pattern '\''(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])'\'' && grep -q '\''^#define RX_DFA_PREFILTER "handoff"'\'' "$REACH_TMP/o2.c" && grep -q '\''^#define RX_REQ_HANDOFF "3"'\'' "$REACH_TMP/o2.c" && grep -q '\''^#define RX_REQ_RUN "none"'\'' "$REACH_TMP/o2.c" && echo REACH-BYTE-REENTRY'
SAB_REACH_EXPECT='REACH-BYTE-REENTRY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        ro = pcrec_sat_add(lmaxw, r.off[i], PCREC_W_UNBOUNDED);'
SAB_AFTER='        ro = r.off[i];   /* SABOTAGE S805 */'
