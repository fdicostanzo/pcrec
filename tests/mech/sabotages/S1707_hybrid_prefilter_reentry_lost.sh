#!/usr/bin/env bash
# S1707 ([REQRUN-VM], lane reqvm1) -- THE VM HYBRID's PREFILTER LOSES ITS
# RE-ENTRY. NEXT's `handoff` row re-enters inside the hybrid's inlined
# prefilter's forward scan (bench subst case 2's shape); the plant restores
# the decline of every VM-finish artifact. NO ANSWER MOVES (the re-entry is an
# optimisation), so the `RX_DFA_PREFILTER "handoff"` rows of tests/memfn/
# run_handoff_reach.sh are the detector (arm memfnreach).
SAB_ID='S1707-hybrid-prefilter-reentry-lost'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='memfnreach'
SAB_DESC='the VM hybrid'\''s prefilter forward scan no longer re-enters the handoff'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1707.'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_handoff_reach.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: /(phpmyadmin|wp-admin)/[a-z]+\.php: reaches the VM hybrid handoff (RX_REQ_HANDOFF 6)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!s->forward) return false;
    u = req_use_read(cx, CAND_SLOT_NEXT);'
SAB_AFTER='    if (!s->forward || cand_finish_of(cx) == CAND_ROUTE_VM) return false;   /* SABOTAGE S1707 */
    u = req_use_read(cx, CAND_SLOT_NEXT);'
