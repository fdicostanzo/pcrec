#!/usr/bin/env bash
# S1649 ([INLINE-C] stage 1b, lane ic1b; design S-IC3b) -- possessify's position reader reads a W_PRED callout site's path as empty (transparent), the P7 witness
#
# Witness and reach: shapes.rxt D1/P7, (\d+)(?C"le255") on 1234 ([0,3) with the site opaque).
SAB_ID="S1649-callout-pred-path-read-empty"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="callouts"
SAB_DESC='possessify'\''s position reader reads a W_PRED callout site'\''s path as empty (transparent), the P7 witness'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''(\d+)(?C"le255")'\'' && grep -qF '\''rx_callout_le255.fn(&'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-PRED-PATH'
SAB_REACH_EXPECT='REACH-CALLOUT-PRED-PATH'
SAB_COUNT=1
SAB_BEFORE='static First fst_row(const Ast *a)
{
    const KindRow row = pcrec_ast_row(a);
    First r;'
SAB_AFTER='static First fst_row(const Ast *a)
{
    const KindRow row = pcrec_ast_row(a);
    First r;
    if (a->k == A_CALLOUT && !a->u.callout.consume) return fst_empty(true); /* [SABOTAGE S1649] */'
