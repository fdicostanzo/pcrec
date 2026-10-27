#!/usr/bin/env bash
# S1671 ([INLINE-C] stage 1b advice, lane ic1badvice) -- the witness builder never runs, so no verdict can be PROVEN CHANGES
#
# Witness and reach: run_callouts_tests.sh arm 7 (advice_check.py, the once
# advice against libpcre2).
SAB_ID="S1671-callout-advice-no-witness"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='the witness builder never runs, so no verdict can be PROVEN CHANGES'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''(?:a|ab)(?C"x,once")c'\'' 2>&1 | grep -qF '\''(offset 0 of "abc")'\'' && echo REACH-ADVICE-WITNESS'
SAB_REACH_EXPECT='REACH-ADVICE-WITNESS'
SAB_COUNT=1
SAB_BEFORE='    *why = co_seal_witness(cx, w->root, c);'
SAB_AFTER='    *why = 0 ? co_seal_witness(cx, w->root, c) : NULL; /* [SABOTAGE S1671] */'
