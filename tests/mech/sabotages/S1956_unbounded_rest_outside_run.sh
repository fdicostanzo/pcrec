#!/usr/bin/env bash
# S1956 ([REQ-PAST-LAST], lane reqpast) -- THE UNBOUNDED ROW ADMITS A PART
# OUTSIDE THE RUN. As S1704 for the bounded row: the re-ask after each failed
# attempt stays linear only where every other part of the pre-check is a byte
# or slice of the whole run; the plant drops that conjunct, so `(a)\1xyz` (its
# set's `a` is not in the run `xyz`) takes the row and may rescan to the next
# `a` at every re-find. NO ANSWER MOVES (the re-ask is sound), so the decline
# pin of tests/memfn/run_handoff_reach.sh is the detector (arm memfnreach).
SAB_ID='S1956-unbounded-rest-outside-run'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='memfnreach'
SAB_DESC='the attempt-loop handoff with an unbounded K is admitted where a pre-check part is not a byte of the whole run'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqpast_report.md, CHANGES); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1956.'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_handoff_reach.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: (a)\1xyz (byte): declined (RX_REQ_HANDOFF none)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='           pcrec_fact_req_whole_run(s->cx)->whole_maxoff >= PCREC_W_UNBOUNDED &&
           req_parts_in_whole(s->cx);'
SAB_AFTER='           pcrec_fact_req_whole_run(s->cx)->whole_maxoff >= PCREC_W_UNBOUNDED;   /* SABOTAGE S1956 */'
