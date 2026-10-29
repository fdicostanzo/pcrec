#!/usr/bin/env bash
# S1668 ([INLINE-C] stage 1b, lane ic1bwritten) -- the parse does not record the as-written lookaround on the context node it builds
#
# Witness and reach: run_callouts_tests.sh arm 5 (the once-refusal rows for a lookaround the parse rewrote into a context node).
SAB_ID="S1668-callout_written_fact_unrecorded"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="callouts"
SAB_DESC='the parse does not record the as-written lookaround on the context node it builds'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''(?*a|b)(?C"x,once")c'\'' 2>&1 | grep -qF '\''non-atomic lookaround at offset 0'\'' && echo REACH-WRITTEN-RECORDED'
SAB_REACH_EXPECT='REACH-WRITTEN-RECORDED'
SAB_COUNT=1
SAB_BEFORE='                cn->u.ctx.written = w;'
SAB_AFTER='                (void)w; /* [SABOTAGE S1668] */'
