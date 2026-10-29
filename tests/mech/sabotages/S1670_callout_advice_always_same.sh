#!/usr/bin/env bash
# S1670 ([INLINE-C] stage 1b advice, lane ic1badvice) -- every once-advice verdict reads PROVEN SAME, whatever the proofs say
#
# Witness and reach: run_callouts_tests.sh arm 7 (advice_check.py, the once
# advice against libpcre2).
SAB_ID="S1670-callout-advice-always-same"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='every once-advice verdict reads PROVEN SAME, whatever the proofs say'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''a+(?C"x,once")ab'\'' 2>&1 | grep -qF '\''that loses a match'\'' && echo REACH-ADVICE-CHANGES'
SAB_REACH_EXPECT='REACH-ADVICE-CHANGES'
SAB_COUNT=1
SAB_BEFORE='    switch (co_seal_verdict(w, c, &why)) {'
SAB_AFTER='    switch (co_seal_verdict(w, c, &why) & 0) { /* [SABOTAGE S1670] */'
