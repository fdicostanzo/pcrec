#!/usr/bin/env bash
# S1654 ([INLINE-C] stage 1b, lane ic1b; design S-IC11) -- row 9, the trap on a check's positive return, is removed, so a W_PRED callee returning 1 is not caught
#
# Witness and reach: the pred1 trap in run_callouts_tests.sh arm 4, a(?C"one") with a binding that returns 1.
SAB_ID="S1654-callout-pred-trap-removed"
SAB_FILE="src/gen/callsite_rows.c"
SAB_SUITES="callouts"
SAB_DESC='row 9, the trap on a check'\''s positive return, is removed, so a W_PRED callee returning 1 is not caught'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''a(?C"one")'\'' && grep -qF '\''if (r > 0) __builtin_trap();'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-PRED-TRAP'
SAB_REACH_EXPECT='REACH-CALLOUT-PRED-TRAP'
SAB_COUNT=1
SAB_BEFORE='    { "width",     CS_TRAP,      cs_pred,     "r > 0", false },'
SAB_AFTER='    { "width",     CS_TRAP,      cs_part /* [SABOTAGE S1654] */,     "r > 0", false },'
