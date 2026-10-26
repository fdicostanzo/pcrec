#!/usr/bin/env bash
# S1659 ([INLINE-C] stage 1b, lane ic1b; design S-IC27) -- the once check accepts a site inside a repeat (it refuses only a live choice point)
#
# Witness and reach: run_callouts_tests.sh arm 5: once must be refused on (?:(?C1)(a))+ and (?:a(?C1)){2}.
SAB_ID="S1659-callout-once-accepts-repeat"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='the once check accepts a site inside a repeat (it refuses only a live choice point)'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''(?:(?C1)(a))+'\'' && grep -qF '\''rx_callout_1.fn(&'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-ONCE'
SAB_REACH_EXPECT='REACH-CALLOUT-ONCE'
SAB_COUNT=1
SAB_BEFORE='    if (a->u.callout.once && c == CO_CLASS_REPEATED)'
SAB_AFTER='    if (a->u.callout.once && c == CO_CLASS_REPEATED && !rep) /* [SABOTAGE S1659] */'
