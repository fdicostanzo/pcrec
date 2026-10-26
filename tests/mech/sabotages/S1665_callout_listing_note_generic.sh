#!/usr/bin/env bash
# S1665 ([INLINE-C] stage 1b guide, lane ic1bguide) -- the listing note for a live-choice site reverts to a generic sentence, not the refusal reason
#
# Witness and reach: run_callouts_tests.sh arm 5 (the per-culprit once-refusal rows).
SAB_ID="S1665-callout-listing-note-generic"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='the listing note for a live-choice site reverts to a generic sentence, not the refusal reason'
SAB_REACH='"$PCREC" -p rx --features all --emit-ir --pattern '\''(?*a+)(?C1)a+c'\'' | grep -qF '\''keeps the quantifier at offset 4'\'' && echo REACH-GUIDE-NOTE-SAME'
SAB_REACH_EXPECT='REACH-GUIDE-NOTE-SAME'
SAB_COUNT=1
SAB_BEFORE='        a->u.callout.why = co_culprit(cx, live);   /* same text as the refusal */'
SAB_AFTER='        a->u.callout.why = "a choice point before the site can be resumed"; /* [SABOTAGE S1665] */'
