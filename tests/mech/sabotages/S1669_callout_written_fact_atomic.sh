#!/usr/bin/env bash
# S1669 ([INLINE-C] stage 1b, lane ic1bwritten) -- the as-written lookaround is recorded as atomic, so the fact holds no live choice
#
# Witness and reach: run_callouts_tests.sh arm 5 (the once-refusal rows for a lookaround the parse rewrote into a context node).
SAB_ID="S1669-callout_written_fact_atomic"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="callouts"
SAB_DESC='the as-written lookaround is recorded as atomic, so the fact holds no live choice'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''(?<*a|b)(?C"x,once")c'\'' 2>&1 | grep -qF '\''non-atomic lookaround at offset 0'\'' && echo REACH-WRITTEN-KIND'
SAB_REACH_EXPECT='REACH-WRITTEN-KIND'
SAB_COUNT=1
SAB_BEFORE='                w->u.look.atomic = false;'
SAB_AFTER='                w->u.look.atomic = true; /* [SABOTAGE S1669] */'
