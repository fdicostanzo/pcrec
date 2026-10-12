#!/usr/bin/env bash
# S814 ([REQ-HANDOFF-L1], lane rlhbuild) -- THE RE-ENTRY DOES NOT ROUND UP
# under a multibyte encoding: `c - K` may land on a continuation byte and the
# scan steps from inside a character. Detectors: run_prechecks.sh §5.12o
# (structural) and tests/litscan/handoff.rxt's utf8 blocks (answers).
SAB_ID='S814-reentry-roundup-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='prechecks harness'
SAB_HARNESS_TARGET='tests/litscan/handoff.rxt'
SAB_DESC='the re-entered handoff moves a utf8 scan to c - K without rounding it up to a character start'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rlhbuild_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S814.'
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o "$REACH_TMP/o.c" --pattern '\''.{1,3}:'\'' && grep -q '\''^#define RX_DFA_PREFILTER "handoff"'\'' "$REACH_TMP/o.c" && echo REACH-UTF8-REENTRY'
SAB_REACH_EXPECT='REACH-UTF8-REENTRY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (round.len > 0) pcrec_sb_splice(c, &round);
    pf_emit_ofs_reseed('
SAB_AFTER='    (void)round;   /* SABOTAGE S814: no round-up */
    pf_emit_ofs_reseed('
