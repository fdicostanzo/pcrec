#!/usr/bin/env bash
# S600 ([START-TABLE] C4, lane stc4; docs/design/start_table.md §2.3, docs/dev/lanes/stc4_report.md) -- an ENTRY slot's choice made route-dependent: a total PRESENCE row routed on the VM route alone is inserted before `emitted`, so the slot answers differently on the VM route than on the DFA route `req_admit` asks.
# Detector (arm candoracle): tests/codegen/run_cand_oracle.sh. Since C4 the
# PRESENCE and FIRST readers ask on CAND_ROUTE_DFA (the route the C1 trace
# records) although §2.3 asks the entry slots on every route; that is honest
# only while the slot's answer does not depend on the route, so the trace
# build's `cand_hit_every` walks every other asked route and aborts
# (`row-differs-on-route`) on a different row. The default build's selection
# is unchanged by the plant (the DFA route never reaches the new row), so no
# artifact byte and no answer moves: the corpus arm is not named, by design.
SAB_ID='S600-cand-entry-row-route-dependent'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='an entry slot made route-dependent: a total PRESENCE row on the VM route alone precedes emitted, so the VM route chooses a row the DFA route req_admit asks on never does; the trace build cross-route check must abort'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc4_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S600.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .c = { "emitted", 0, cand_always }, .slot = CAND_SLOT_PRESENCE,'
SAB_AFTER='    { .c = { "emitted-vm", 0, cand_always }, .slot = CAND_SLOT_PRESENCE,   /* SABOTAGE S600 */
      .routes = CR_VM, .tok = "one-attempt", .map = CM_NONE, .hands = CT_VERDICT,
      .u.admit = { REQ_ADMIT_ONE_ATTEMPT, "S600" } },
    { .c = { "emitted", 0, cand_always }, .slot = CAND_SLOT_PRESENCE,'
