#!/usr/bin/env bash
# S1653 ([INLINE-C] stage 1b, lane ic1b; design S-IC6b) -- the required-run and start-set facts read a consume (W_ANY) callout site as empty, so a run spans it and the start set skips past it
#
# Witness and reach: shapes.rxt a(?C"two,consume")b on axyb ([0,4)) and (?C"digits,consume")x on 12x ([0,3)).
SAB_ID="S1653-callout-consume-read-empty"
SAB_FILE="src/facts/req.c"
SAB_SUITES="callouts"
SAB_DESC='the required-run and start-set facts read a consume (W_ANY) callout site as empty, so a run spans it and the start set skips past it'
SAB_REACH='"$PCREC" -p rx --features all -o "$REACH_TMP/o.c" --pattern '\''a(?C"two,consume")b'\'' && grep -qF '\''rx_callout_two.fn(&'\'' "$REACH_TMP/o.c" && echo REACH-CALLOUT-CONSUME-FACTS'
SAB_REACH_EXPECT='REACH-CALLOUT-CONSUME-FACTS'
SAB_COUNT=1
SAB_BEFORE='    case KTEXT_ANY:  rb_gap_into(acc, PCREC_W_UNBOUNDED); return;'
SAB_AFTER='    case KTEXT_ANY:  if (a->k == A_CALLOUT) { rb_assert_into(acc); return; } /* [SABOTAGE S1653] */ rb_gap_into(acc, PCREC_W_UNBOUNDED); return;'
SAB_FILE2="src/facts/startset.c"
SAB_COUNT2=1
SAB_BEFORE2='    case KTEXT_ANY:  return ss_all();'
SAB_AFTER2='    case KTEXT_ANY:  return a->k == A_CALLOUT ? acc : ss_all(); /* [SABOTAGE S1653] */'
