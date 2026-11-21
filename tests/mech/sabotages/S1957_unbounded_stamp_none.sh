#!/usr/bin/env bash
# S1957 ([REQ-PAST-LAST], lane reqpast) -- THE UNBOUNDED ROW STAMPS "none".
# `<PREFIX>_REQ_HANDOFF` must read "unbounded" where the attempt-loop handoff
# with an unbounded K runs (match_api.md §6.3.7¶11, tuning.md §2.41¶9); the
# plant stamps the absence value over a selection the artifact runs. NO ANSWER
# MOVES; the stamp pins of tests/memfn/run_handoff_reach.sh (`a+xyz`,
# `[^@ ]+@x` read "unbounded") are the detector (arm memfnreach).
SAB_ID='S1957-unbounded-stamp-none'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='memfnreach'
SAB_DESC='RX_REQ_HANDOFF reads "none" on an artifact that runs the unbounded attempt-loop handoff'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqpast_report.md, CHANGES); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1957.'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_handoff_reach.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: a+xyz (byte): reaches the attempt loop'\''s re row (RX_REQ_HANDOFF unbounded)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!pcrec_bound_bounded(k)) return "unbounded";   /* [REQ-PAST-LAST] */'
SAB_AFTER='    if (!pcrec_bound_bounded(k)) return "none";   /* SABOTAGE S1957 */'
# RE-ANCHORED 2026-11-20 (lane l3build, span_arms L3 RM-2, D-7): K is a `PfBound` (state +
# signed value); the stamp asks K once and tests its state through the bounded predicate. Intent unchanged.
