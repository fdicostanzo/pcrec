#!/usr/bin/env bash
# S1676 ([INLINE-C] stage 1b advice, lane ic1badvice) -- the lookaround retry proof reads a callout site in the body as inert
#
# Witness and reach: run_callouts_tests.sh arm 7 (advice_check.py, the once
# advice against libpcre2).
SAB_ID="S1676-callout-advice-look-sites"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='the lookaround retry proof reads a callout site in the body as inert'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''(?*a+)(?C"x,once")a+c'\'' 2>&1 | grep -qF '\''that does not change what it matches'\'' && echo REACH-ADVICE-LOOK-SITE'
SAB_REACH_EXPECT='REACH-ADVICE-LOOK-SITE'
SAB_COUNT=1
SAB_BEFORE='        case A_KRESET: case A_CALLOUT: case A_CALL:'
SAB_AFTER='        case A_KRESET: case A_CALL: break; case A_CALLOUT: return true; /* [SABOTAGE S1676] */'
