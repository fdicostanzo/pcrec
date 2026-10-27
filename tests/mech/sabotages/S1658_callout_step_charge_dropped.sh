#!/usr/bin/env bash
# S1658 ([INLINE-C] stage 1b, lane ic1b; design S-IC26) -- the step charged per callout fire is dropped, so a site that always vetoes never spends the budget
#
# Witness and reach: checks.c, a(?C"veto") under --step-budget=5 over 20 a's must give up STEPS (it answers 0 without the charge; measured by hand on the artifact).
SAB_ID="S1658-callout-step-charge-dropped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="callouts"
SAB_DESC='the step charged per callout fire is dropped, so a site that always vetoes never spends the budget'
SAB_REACH='"$PCREC" -p rx --features all --step-budget=5 -o "$REACH_TMP/o.c" --pattern '\''a(?C"veto")'\'' && grep -qF '\''rx_callout_veto.fn(&'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-STEP'
SAB_REACH_EXPECT='REACH-CALLOUT-STEP'
SAB_COUNT=1
SAB_BEFORE='    if (v->has_budget)
        pcrec_sb_printf(b, "    if (--run->steps_left < 0) return %s_R_STEPS;\n",'
SAB_AFTER='    if (0 /* [SABOTAGE S1658] */ && v->has_budget)
        pcrec_sb_printf(b, "    if (--run->steps_left < 0) return %s_R_STEPS;\n",'
