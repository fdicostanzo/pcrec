#!/usr/bin/env bash
# S738 ([OPT-REVEND] L0, lane lfl0; docs/design/locate_finish.md rev 2.1 §5 L0; docs/dev/lanes/lfl0_report.md) -- LOCATE's two rows swapped: `composite` (an undeniable `cand_always` row) is walked before `empty`, so the empty engine's body is the composite's walk and `empty` is never selected.
# Detector: tests/codegen/run_cand_oracle.sh: the trace build's self-check aborts `table-not-total LOCATE` (the last row routed on the DFA routes is no longer the undeniable fallback) on every witness. MEASURED by plant at landing: 59 of the oracle's checks fail.
SAB_ID='S738-locate-order-swapped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='LOCATE order swapped: composite before empty, so the empty engine emits a scan; the self-check fails the table as not total'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/lfl0_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S738.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\B\\b" && grep -qF "#define RX_DFA_SCAN \"empty\"" "$REACH_TMP/o.c" && echo REACH-EMPTY'
SAB_REACH_EXPECT='REACH-EMPTY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-10 (lane revbuild, [OPT-REVEND] L2): rev-end sits between empty and composite, and empty gained its DFA front, whole and fin; the plant still moves empty after the composite. Intent
# unchanged.
SAB_BEFORE='    { .c = { "empty", 0, locate_empty_applies }, .slot = CAND_SLOT_LOCATE,
      .routes = CR_DFA | CR_ATTEMPT, .tok = "empty", .map = CM_NONE, .hands = CT_VERDICT,
      .needs = { [CAND_ROUTE_DFA]     = { .front = CN(CAND_SLOT_PRESENCE) },
                 [CAND_ROUTE_ATTEMPT] = { .front = CAND_FRONT_DFA } },
      .u.locate = { .emit = { [CAND_ROUTE_DFA] = emit_empty_unanchored,
                              [CAND_ROUTE_ATTEMPT] = emit_empty_attempt },
                    .scan = { [CAND_ROUTE_DFA] = "empty", [CAND_ROUTE_ATTEMPT] = "empty" },
                    .nomatch = true, .whole = true, .fin = CT_VERDICT } },
'
SAB_AFTER='    /* SABOTAGE S738: empty moved after composite */
'
SAB_FILE2='src/gen/emit_dfa.c'
SAB_COUNT2=1
SAB_BEFORE2='                    .recover = CAND_HAND_EXISTS, .fin = CT_START } },
'
SAB_AFTER2='                    .recover = CAND_HAND_EXISTS, .fin = CT_START } },
    { .c = { "empty", 0, locate_empty_applies }, .slot = CAND_SLOT_LOCATE,
      .routes = CR_DFA | CR_ATTEMPT, .tok = "empty", .map = CM_NONE, .hands = CT_VERDICT,
      .needs = { [CAND_ROUTE_DFA]     = { .front = CN(CAND_SLOT_PRESENCE) },
                 [CAND_ROUTE_ATTEMPT] = { .front = CAND_FRONT_DFA } },
      .u.locate = { .emit = { [CAND_ROUTE_DFA] = emit_empty_unanchored,
                              [CAND_ROUTE_ATTEMPT] = emit_empty_attempt },
                    .scan = { [CAND_ROUTE_DFA] = "empty", [CAND_ROUTE_ATTEMPT] = "empty" },
                    .nomatch = true, .whole = true, .fin = CT_VERDICT } },
'
