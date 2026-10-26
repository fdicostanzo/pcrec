#!/usr/bin/env bash
# S1648 ([INLINE-C] stage 1b, lane ic1b; design S-IC3) -- possessification's FIRST fold ignores a callout site (reads every site, check or consumer, as empty), so a quantifier before a site is possessified
#
# Witness and reach: shapes.rxt D1/P7, (\d+)(?C"le255") on 1234: possessified, the attempt at 0 cannot back off to 123 and the answer moves from [0,3).
SAB_ID="S1648-callout-possessify-ignores-site"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="callouts"
SAB_DESC='possessification'\''s FIRST fold ignores a callout site (reads every site, check or consumer, as empty), so a quantifier before a site is possessified'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''(\d+)(?C"le255")'\'' && grep -qF '\''rx_callout_le255.fn(&'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-POSSESSIFY'
SAB_REACH_EXPECT='REACH-CALLOUT-POSSESSIFY'
SAB_COUNT=1
SAB_BEFORE='    case A_VAR:
    case A_CALLOUT:
        return fst_row(a);'
SAB_AFTER='    case A_VAR:
        return fst_row(a);
    case A_CALLOUT: /* [SABOTAGE S1648] */
        return fst_empty(true);'
