#!/usr/bin/env bash
# S1673 ([INLINE-C] stage 1b advice, lane ic1badvice) -- a lazy quantifier falls to the greedy row and is offered a seal
#
# Witness and reach: run_callouts_tests.sh arm 7 (advice_check.py, the once
# advice against libpcre2).
SAB_ID="S1673-callout-advice-lazy-sealed"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='a lazy quantifier falls to the greedy row and is offered a seal'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''a+?(?C"x,once")b'\'' 2>&1 | grep -qF '\''the lazy quantifier at offset 1'\'' && echo REACH-ADVICE-LAZY'
SAB_REACH_EXPECT='REACH-ADVICE-LAZY'
SAB_COUNT=1
SAB_BEFORE='    { A_REP, 1, "the lazy quantifier", "can be backtracked into",'
SAB_AFTER='    { A_REP, 2, "the lazy quantifier", "can be backtracked into", /* [SABOTAGE S1673] */'
