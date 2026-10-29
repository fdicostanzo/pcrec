#!/usr/bin/env bash
# S1662 ([INLINE-C] stage 1b fix, lane ic1bfix; review r2 CON-1 = ADV-5) -- an empty item of a callout attribute list is skipped instead of refused
#
# Witness and reach: run_callouts_tests.sh arm 6: (?C"x,") and (?C"x,,once") must be refused as an empty callout attribute.
SAB_ID="S1662-callout-empty-attr-accepted"
SAB_FILE="src/parse/mod_callouts.c"
SAB_SUITES="callouts"
SAB_DESC='an empty item of a callout attribute list is skipped instead of refused'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''a(?C"x,")'\'' 2>&1 | grep -qF '\''empty callout attribute'\'' && echo REACH-CALLOUT-EMPTY-ATTR'
SAB_REACH_EXPECT='REACH-CALLOUT-EMPTY-ATTR'
SAB_COUNT=1
SAB_BEFORE='        if (j == i)
            return pcrec_ext_msgf(cx, "empty callout attribute (each item "'
SAB_AFTER='        if (j == i && 0) /* [SABOTAGE S1662] */
            return pcrec_ext_msgf(cx, "empty callout attribute (each item "'
