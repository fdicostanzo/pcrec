#!/usr/bin/env bash
# S595 ([START-TABLE] C2, lane stc2; docs/design/start_table.md §3.3 item 6, docs/dev/lanes/stc2_report.md) -- a route mis-key: N12 pred-memchr is routed on the DFA route instead of the ATTEMPT route, so the ATTEMPT walk falls to none where attempt_cand takes the predecessor-byte memchr.
# Detector (arm candoracle): tests/codegen/run_cand_oracle.sh, the both-walks
# oracle over named witnesses. cand_rows[] has no reader in a default build
# until C3, so no artifact byte and no answer moves: the corpus arm is not
# named, by design.
SAB_ID='S595-cand_row_route_miskeyed'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='a route mis-key: N12 pred-memchr is routed on the DFA route instead of the ATTEMPT route, so the ATTEMPT walk falls to none where attempt_cand takes the predecessor-byte memchr'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S595.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .slot = CAND_SLOT_NEXT, .routes = CR_ATTEMPT, .tok = "pred-memchr",'
SAB_AFTER='      .slot = CAND_SLOT_NEXT, .routes = CR_DFA, .tok = "pred-memchr",   /* SABOTAGE S595 */'
