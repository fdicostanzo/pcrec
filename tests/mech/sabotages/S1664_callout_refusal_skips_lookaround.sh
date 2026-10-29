#!/usr/bin/env bash
# S1664 ([INLINE-C] stage 1b guide, lane ic1bguide) -- the non-atomic lookaround is not the live construct, so the refusal names only the inner quantifier
#
# Witness and reach: run_callouts_tests.sh arm 5 (the per-culprit once-refusal rows).
SAB_ID="S1664-callout-refusal-skips-lookaround"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='the non-atomic lookaround is not the live construct, so the refusal names only the inner quantifier'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''(?*a+)(?C"x,once")a+c'\'' 2>&1 | grep -qF '\''non-atomic lookaround at offset 0'\'' && echo REACH-GUIDE-LOOK-NAMED'
SAB_REACH_EXPECT='REACH-GUIDE-LOOK-NAMED'
SAB_COUNT=1
SAB_BEFORE='        return !a->u.look.atomic && co_choice(cx, a->l) ? a : NULL;'
SAB_AFTER='        return a->u.look.atomic ? NULL : co_choice(cx, a->l); /* [SABOTAGE S1664] */'
