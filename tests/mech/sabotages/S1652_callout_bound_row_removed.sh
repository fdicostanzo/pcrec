#!/usr/bin/env bash
# S1652 ([INLINE-C] stage 1b, lane ic1b; design S-IC6) -- row 10, a consumer's length bound (inside the subject, at a character start), is removed
#
# Witness and reach: the overlong and midchar traps in run_callouts_tests.sh arm 4 (a consumer returning past the end, or into a UTF-8 character).
SAB_ID="S1652-callout-bound-row-removed"
SAB_FILE="src/gen/callsite_rows.c"
SAB_SUITES="callouts"
SAB_DESC='row 10, a consumer'\''s length bound (inside the subject, at a character start), is removed'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''a(?C"far,consume")'\'' && grep -qF '\''(size_t)r > subject_length - scan_position'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-BOUND'
SAB_REACH_EXPECT='REACH-CALLOUT-BOUND'
SAB_COUNT=1
SAB_BEFORE='    { "bound",     CS_TRAP,      cs_consumes, NULL, false },'
SAB_AFTER='    { "bound",     CS_TRAP,      cs_pred /* [SABOTAGE S1652] */, NULL, false },'
