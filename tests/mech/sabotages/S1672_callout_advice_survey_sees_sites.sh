#!/usr/bin/env bash
# S1672 ([INLINE-C] stage 1b advice, lane ic1badvice) -- the survey reads the check sites as written, so a site in the follow blocks every PROVEN SAME
#
# Witness and reach: run_callouts_tests.sh arm 7 (advice_check.py, the once
# advice against libpcre2).
SAB_ID="S1672-callout-advice-survey-sees-sites"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='the survey reads the check sites as written, so a site in the follow blocks every PROVEN SAME'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''a+(?C"x,once")b'\'' 2>&1 | grep -qF '\''that does not change what it matches'\'' && echo REACH-ADVICE-SAME'
SAB_REACH_EXPECT='REACH-ADVICE-SAME'
SAB_COUNT=1
SAB_BEFORE='        if (!site[i].u.callout.consume) {'
SAB_AFTER='        if (0 && !site[i].u.callout.consume) { /* [SABOTAGE S1672] */'
