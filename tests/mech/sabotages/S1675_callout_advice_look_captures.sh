#!/usr/bin/env bash
# S1675 ([INLINE-C] stage 1b advice, lane ic1badvice) -- the lookaround retry proof ignores live captures
#
# Witness and reach: run_callouts_tests.sh arm 7 (advice_check.py, the once
# advice against libpcre2).
SAB_ID="S1675-callout-advice-look-captures"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='the lookaround retry proof ignores live captures'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''(?*a+)(?C"x,once")a+c'\'' 2>&1 | grep -qF '\''that does not change what it matches'\'' && echo REACH-ADVICE-LOOK'
SAB_REACH_EXPECT='REACH-ADVICE-LOOK'
SAB_COUNT=1
SAB_BEFORE='        return co_look_retry_inert(c->l) && !pcrec_has_live_capture(c->l);'
SAB_AFTER='        return co_look_retry_inert(c->l); /* [SABOTAGE S1675] */'
