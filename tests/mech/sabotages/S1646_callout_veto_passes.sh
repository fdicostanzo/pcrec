#!/usr/bin/env bash
# S1646 ([INLINE-C] stage 1b, lane ic1b; design S-IC1) -- a callout site treats its callee's -1 as a pass (the matchfn convention's fail row routed to success)
#
# Witness and reach: every vetoing shape in tests/callouts/shapes.rxt (P9 veto, the delimiter rows) matches where libpcre2 answers no match.
SAB_ID="S1646-callout-veto-passes"
SAB_FILE="src/gen/callsite_rows.c"
SAB_SUITES="callouts"
SAB_DESC='a callout site treats its callee'\''s -1 as a pass (the matchfn convention'\''s fail row routed to success)'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''a(?C"veto")b'\'' && grep -qF '\''r == -1) goto'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-FAIL-ROW'
SAB_REACH_EXPECT='REACH-CALLOUT-FAIL-ROW'
SAB_COUNT=1
SAB_BEFORE='    { "fail",      CS_FAIL,      cs_matchfn,  "r == -1", false },'
SAB_AFTER='    { "fail",      CS_SUCCESS /* [SABOTAGE S1646] */,      cs_matchfn,  "r == -1", false },'
