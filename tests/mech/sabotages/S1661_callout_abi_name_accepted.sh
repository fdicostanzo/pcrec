#!/usr/bin/env bash
# S1661 ([INLINE-C] stage 1b fix, lane ic1bfix; review r2 ADV-1) -- a binding whose symbol the shared ABI block already declares is accepted (`(?C"ref")` binds the typedef `rx_callout_ref`)
#
# Witness and reach: run_callouts_tests.sh arm 6: every fixed rx_callout_* name read off an emitted artifact must be refused as a binding.
SAB_ID="S1661-callout-abi-name-accepted"
SAB_FILE="src/parse/mod_callouts.c"
SAB_SUITES="callouts"
SAB_DESC='a binding whose symbol the shared ABI block already declares is accepted'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''a(?C"ref")'\'' 2>&1 | grep -qF '\''already declares'\'' && echo REACH-CALLOUT-ABI-NAME'
SAB_REACH_EXPECT='REACH-CALLOUT-ABI-NAME'
SAB_COUNT=1
SAB_BEFORE='    if (co_abi_name(sym))'
SAB_AFTER='    if (co_abi_name(sym) && 0) /* [SABOTAGE S1661] */'
