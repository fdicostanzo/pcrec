#!/usr/bin/env bash
# S1660 ([INLINE-C] stage 1b fix, lane ic1bfix; review r2 CON-2) -- every lookaround is treated as sealing its choice points, the non-atomic (?*...) included
#
# Witness and reach: run_callouts_tests.sh arm 5: (?*a+)(?C1)a+c must be `repeated` and `once` refused on it.
SAB_ID="S1660-callout-every-lookaround-seals"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='every lookaround is treated as sealing its choice points, the non-atomic (?*...) included'
SAB_REACH='"$PCREC" -p rx --features all --emit-ir --pattern '\''(?*a+)(?C1)a+c'\'' | grep -qP '\''\trepeated\t'\'' && echo REACH-CALLOUT-NONATOMIC-LOOK'
SAB_REACH_EXPECT='REACH-CALLOUT-NONATOMIC-LOOK'
SAB_COUNT=1
SAB_BEFORE='        return a->u.look.atomic ? NULL : co_choice(cx, a->l);'
SAB_AFTER='        return NULL; /* [SABOTAGE S1660] */'
