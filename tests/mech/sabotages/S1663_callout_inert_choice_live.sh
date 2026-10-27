#!/usr/bin/env bash
# S1663 ([INLINE-C] stage 1b fix, lane ic1bfix; review r2 SLOT-1) -- a choice inside a never-run group ((?(DEFINE)...), X{0}) counts as live before a callout site
#
# Witness and reach: run_callouts_tests.sh arm 5: (?(DEFINE)(?<d>a|b))x(?C1) and (?:a|b){0}x(?C1) must be once-per-match and accept `once`.
SAB_ID="S1663-callout-inert-choice-live"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='a choice inside a never-run group counts as live before a callout site'
SAB_REACH='"$PCREC" -p rx --features all --emit-ir --pattern '\''(?:a|b){0}x(?C1)'\'' | grep -qP '\''\tonce-per-match\t'\'' && echo REACH-CALLOUT-INERT'
SAB_REACH_EXPECT='REACH-CALLOUT-INERT'
SAB_COUNT=1
SAB_BEFORE='    if (co_inert(a)) return NULL;'
SAB_AFTER='    if (co_inert(a) && 0) return NULL; /* [SABOTAGE S1663] */'
