#!/usr/bin/env bash
# S1667 ([INLINE-C] stage 1b, lane ic1bwritten) -- the once rule does not read the as-written fact off a context node, so a rewritten non-atomic lookaround is accepted
#
# Witness and reach: run_callouts_tests.sh arm 5 (the once-refusal rows for a lookaround the parse rewrote into a context node).
SAB_ID="S1667-callout_written_fact_unread"
SAB_FILE="src/opt/callout.c"
SAB_SUITES="callouts"
SAB_DESC='the once rule does not read the as-written fact off a context node, so a rewritten non-atomic lookaround is accepted'
SAB_REACH='"$PCREC" -p rx --features all -o /dev/null --pattern '\''(?*a|b)(?C"x,once")c'\'' 2>&1 | grep -qF '\''non-atomic lookaround at offset 0'\'' && echo REACH-WRITTEN-READ'
SAB_REACH_EXPECT='REACH-WRITTEN-READ'
SAB_COUNT=1
SAB_BEFORE='        const Ast *wr = a->u.ctx.written;'
SAB_AFTER='        const Ast *wr = NULL; /* [SABOTAGE S1667] */'
