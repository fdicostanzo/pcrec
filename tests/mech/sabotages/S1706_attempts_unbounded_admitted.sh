#!/usr/bin/env bash
# S1706 ([REQRUN-VM], lane reqvm1) -- AN UNBOUNDED WHOLE-RUN K IS ADMITTED.
# A backreference, a variable or a subroutine call before the run, or an
# unbounded repeat, leaves `whole_maxoff` unbounded; the plant admits it. The
# move then never fires (no hit is that far ahead), so NO ANSWER MOVES; the
# decline pins of tests/memfn/run_handoff_reach.sh (`a+xyz`, `(a)\1xyz`
# read RX_REQ_HANDOFF "none") are the detector (arm memfnreach).
SAB_ID='S1706-attempts-unbounded-admitted'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='memfnreach'
SAB_DESC='the VM attempt loop handoff is admitted where the whole run has no finite maximum offset'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1706.'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_handoff_reach.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: a+xyz (byte): declined (RX_REQ_HANDOFF none)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (r->whole_len < 2 || r->whole_maxoff < 0 || r->whole_maxoff >= PCREC_W_UNBOUNDED)'
SAB_AFTER='    if (r->whole_len < 2)   /* SABOTAGE S1706: unbounded admitted */'
