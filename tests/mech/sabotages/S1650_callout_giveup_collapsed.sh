#!/usr/bin/env bash
# S1650 ([INLINE-C] stage 1b, lane ic1b; design S-IC4) -- a callee's give-up (PCREC_ERR_STEPS..FLOOR) is collapsed to -1, a backtrack, instead of propagating
#
# Witness and reach: checks.c's give-up checks: a binding returning PCREC_ERR_STEPS (and FRAMES) must end the search with that code.
SAB_ID="S1650-callout-giveup-collapsed"
SAB_FILE="src/gen/callsite_rows.c"
SAB_SUITES="callouts"
SAB_DESC='a callee'\''s give-up (PCREC_ERR_STEPS..FLOOR) is collapsed to -1, a backtrack, instead of propagating'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''(a+)(?C"steps")b'\'' && grep -qF '\''callee_gave_up = 1'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-GIVEUP'
SAB_REACH_EXPECT='REACH-CALLOUT-GIVEUP'
SAB_COUNT=1
SAB_BEFORE='    { "give-up",   CS_GIVEUP,    cs_vm,       "r >= PCREC_ERR_FLOOR && r <= -2", false },'
SAB_AFTER='    { "give-up",   CS_FAIL /* [SABOTAGE S1650] */,    cs_vm,       "r >= PCREC_ERR_FLOOR && r <= -2", false },'
