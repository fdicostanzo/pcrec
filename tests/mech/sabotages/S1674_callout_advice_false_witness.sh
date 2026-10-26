#!/usr/bin/env bash
# S1674 ([INLINE-C] stage 1b advice, lane ic1badvice) -- the witness check skips the sealed attempt, so every candidate subject is printed as a witness
#
# Witness and reach: run_callouts_tests.sh arm 7 (advice_check.py, the once
# advice against libpcre2).
SAB_ID="S1674-callout-advice-false-witness"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='the witness check skips the sealed attempt, so every candidate subject is printed as a witness'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''(?:a|ab)(?C"x,once")c'\'' 2>&1 | grep -qF '\''(offset 0 of "abc")'\'' && echo REACH-ADVICE-WITNESS-CHECK'
SAB_REACH_EXPECT='REACH-ADVICE-WITNESS-CHECK'
SAB_COUNT=1
SAB_BEFORE='            return NULL;   /* the sealed attempt matches too */'
SAB_AFTER='            (void)0;   /* [SABOTAGE S1674] */'
