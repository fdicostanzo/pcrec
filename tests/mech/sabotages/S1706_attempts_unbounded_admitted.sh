#!/usr/bin/env bash
# S1706 ([REQRUN-VM], lane reqvm1) -- AN UNBOUNDED WHOLE-RUN K IS ADMITTED.
# A backreference, a variable or a subroutine call before the run, or an
# unbounded repeat, leaves `whole_maxoff` unbounded; the plant admits it. The
# move then never fires (no hit is that far ahead), so NO ANSWER MOVES; the
# decline pins of tests/memfn/run_handoff_reach.sh (`a+xyz`, `(a)\1xyz`
# read RX_REQ_HANDOFF "none") are the detector (arm memfnreach).
# RE-AIMED 2026-11-12 (lane reqpast, [REQ-PAST-LAST]): the bound moved into
# `req_handoff_entry_applies`' own return, and `a+xyz` is the unbounded row's
# witness now. Planted, an unbounded K is taken by the bounded rows above
# `handoff-attempts-unbounded`, so `(a)\1xyz` (a set-rest `a` outside the run)
# reaches `handoff-attempts-entry` and stamps "unbounded": its decline pin is
# the detector.
SAB_ID='S1706-attempts-unbounded-admitted'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='memfnreach'
SAB_DESC='the VM attempt loop handoff is admitted where the whole run has no finite maximum offset'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1706.'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_handoff_reach.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: (a)\1xyz (byte): declined (RX_REQ_HANDOFF none)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return req_handoff_vm_run(s) && k >= 0 && k < PCREC_W_UNBOUNDED;'
SAB_AFTER='    return req_handoff_vm_run(s) && k >= 0;   /* SABOTAGE S1706: unbounded admitted */'
