#!/usr/bin/env bash
# S1651 ([INLINE-C] stage 1b, lane ic1b; design S-IC5) -- the slot-0 restore after a callout's call is dropped, so the attempt start the view was given leaks into \K's live register
#
# Witness and reach: checks.c A4, a\Kb(?C"see")c on abc: the reported start must stay 1 (\K), not the 0 the view was shown.
SAB_ID="S1651-callout-slot0-not-restored"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="callouts"
SAB_DESC='the slot-0 restore after a callout'\''s call is dropped, so the attempt start the view was given leaks into \K'\''s live register'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''a\Kb(?C"see")c'\'' && grep -qF '\''rx_co_start;'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-SLOT0'
SAB_REACH_EXPECT='REACH-CALLOUT-SLOT0'
SAB_COUNT=1
SAB_BEFORE='        "        slot_values[0] = %s_co_start;\n",'
SAB_AFTER='        "        (void)%s_co_start; /* [SABOTAGE S1651] */\n",'
