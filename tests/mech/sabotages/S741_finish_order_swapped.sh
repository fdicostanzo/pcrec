#!/usr/bin/env bash
# S741 ([OPT-REVEND] L0, lane lfl0; docs/design/locate_finish.md rev 2.1 §5 L0; docs/dev/lanes/lfl0_report.md) -- FINISH's two rows swapped: `search-from` (undeniable) is walked before `verify-at`, so every DFA artifact's `_match` is the search-filter wrapper and the anchored machine is built for nothing.
# Detector: tests/codegen/run_cand_oracle.sh: the self-check aborts (`table-listing-order`: the `match` listing is out of table order; `table-finish-not-total` behind it) on every witness. MEASURED by plant at landing: 59 checks fail.
SAB_ID='S741-finish-order-swapped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='FINISH order swapped: search-from before verify-at, so every _match is search-filter; the self-check fails FINISH'\''s totality'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/lfl0_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S741.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "a" && grep -qF "#define RX_DFA_MATCH \"unwrapped\"" "$REACH_TMP/o.c" && echo REACH-UNWRAPPED'
SAB_REACH_EXPECT='REACH-UNWRAPPED'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-10 (lane revbuild, [OPT-REVEND] L2): verify-at gained its ENDSET and CR_VM cells and search-from its ENDSET/LOWER cells; the plant still moves verify-at after search-from. Intent
# unchanged.
SAB_BEFORE='    { .c = { "verify-at", 0, finish_available }, .slot = CAND_SLOT_FINISH,
      .routes = CR_DFA | CR_VM, .tok = "unwrapped", .map = CM_NONE,
      .hands = CT_START | CT_VERDICT,
      .list = { [CAND_ROUTE_DFA] = { "match", 1, "unwrapped", PCREC_NO_ANCHORED_DFA } },
      .desc = "the artifact'\''s own ENG_UNANCH _match, and its anchored machine built inside the DFA caps ([ENG-ABS])",
      .needs = { [CAND_ROUTE_DFA] = { CAND_MA },
                 [CAND_ROUTE_VM]  = { CAND_MVM, CAND_VM_ENTRY_CELLS } },
      .take = { [CAND_ROUTE_DFA] = { CAND_HAND_AT, CAND_HAND_ENDSET },
                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT } },
      .u.finish = { CAND_FIN_VERIFY } },
    { .c = { "search-from", 0, cand_always }, .slot = CAND_SLOT_FINISH,
'
SAB_AFTER='    /* SABOTAGE S741: verify-at moved after search-from */
    { .c = { "search-from", 0, cand_always }, .slot = CAND_SLOT_FINISH,
'
SAB_FILE2='src/gen/emit_dfa.c'
SAB_COUNT2=1
SAB_BEFORE2='                [CAND_ROUTE_VM]      = { CAND_HAND_ENDSET, CAND_HAND_LOWER } },
      .u.finish = { CAND_FIN_SEARCH } },
'
SAB_AFTER2='                [CAND_ROUTE_VM]      = { CAND_HAND_ENDSET, CAND_HAND_LOWER } },
      .u.finish = { CAND_FIN_SEARCH } },
    { .c = { "verify-at", 0, finish_available }, .slot = CAND_SLOT_FINISH,
      .routes = CR_DFA | CR_VM, .tok = "unwrapped", .map = CM_NONE,
      .hands = CT_START | CT_VERDICT,
      .list = { [CAND_ROUTE_DFA] = { "match", 1, "unwrapped", PCREC_NO_ANCHORED_DFA } },
      .desc = "the artifact'\''s own ENG_UNANCH _match, and its anchored machine built inside the DFA caps ([ENG-ABS])",
      .needs = { [CAND_ROUTE_DFA] = { CAND_MA },
                 [CAND_ROUTE_VM]  = { CAND_MVM, CAND_VM_ENTRY_CELLS } },
      .take = { [CAND_ROUTE_DFA] = { CAND_HAND_AT, CAND_HAND_ENDSET },
                [CAND_ROUTE_VM]  = { CAND_HAND_SPAN, CAND_HAND_AT } },
      .u.finish = { CAND_FIN_VERIFY } },
'
