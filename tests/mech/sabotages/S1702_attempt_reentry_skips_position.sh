#!/usr/bin/env bash
# S1702 ([REQRUN-VM], lane reqvm1) -- THE ATTEMPT LOOP's RE-ENTRY SKIPS A
# POSITION. After a failed attempt the loop advances one character, then the
# re-entry moves it to the whole run's next hit less K where that is ahead;
# the plant advances one more byte first, so the position right after a
# failed attempt is never tried when no move applies (a match beginning there
# is lost, or a later one reported). Detector: tests/litscan/handoff_vm.rxt.
SAB_ID='S1702-attempt-reentry-skips-position'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_HARNESS_TARGET='tests/litscan/handoff_vm.rxt'
SAB_DESC='the VM attempt loop'\''s re-entry advances the attempt one byte further before its move, skipping a start position'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1702.'
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''(?:xx|y)abc'\'' && grep -q '\''^#define RX_REQ_HANDOFF "1"'\'' "$REACH_TMP/o.c" && grep -q '\''if (landmark_position < attempt_position) {'\'' "$REACH_TMP/o.c" && echo REACH-ATTEMPT-REENTRY'
SAB_REACH_EXPECT='REACH-ATTEMPT-REENTRY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    emit_req_landmark_move(cx, c, ind, "attempt_position", NULL);'
SAB_AFTER='    pcrec_sb_printf(c, "%s    attempt_position++;   /* SABOTAGE S1702 */\n", ind);
    emit_req_landmark_move(cx, c, ind, "attempt_position", NULL);'
