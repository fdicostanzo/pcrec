#!/usr/bin/env bash
# S770 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- R4: `empty` after `rev-end`, so an end-pinned pattern that matches nothing selects the walk.
# Detector: run_rev_end.sh: `[^\x00-\xff]$` reads `rev-end` where its body is `empty`.
SAB_ID='S770-empty-after-revend'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend'
SAB_DESC='R4: `empty` after `rev-end`, so an end-pinned pattern that matches nothing selects the walk'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S770.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "[^\\x00-\\xff]$" && grep -qF "#define RX_DFA_SCAN \"empty\"" "$REACH_TMP/o.c" && echo REACH-EMPTY-PIN'
SAB_REACH_EXPECT='REACH-EMPTY-PIN'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .c = { "empty", 0, locate_empty_applies }, .slot = CAND_SLOT_LOCATE,
      .routes = CR_DFA | CR_ATTEMPT, .tok = "empty", .map = CM_NONE, .hands = CT_VERDICT,
      .needs = { [CAND_ROUTE_DFA]     = { .front = CN(CAND_SLOT_PRESENCE) },
                 [CAND_ROUTE_ATTEMPT] = { .front = CAND_FRONT_DFA } },
      .u.locate = { .emit = { [CAND_ROUTE_DFA] = emit_empty_unanchored,
                              [CAND_ROUTE_ATTEMPT] = emit_empty_attempt },
                    .scan = { [CAND_ROUTE_DFA] = "empty", [CAND_ROUTE_ATTEMPT] = "empty" },
                    .nomatch = true, .whole = true, .fin = CT_VERDICT } },
'
SAB_AFTER='    /* SABOTAGE S770: empty moved after rev-end */
'
SAB_FILE2='src/gen/emit_dfa.c'
SAB_COUNT2=1
SAB_BEFORE2='                    .fin = CT_START | CT_VERDICT | CT_ENDSET } },
'
SAB_AFTER2='                    .fin = CT_START | CT_VERDICT | CT_ENDSET } },
    { .c = { "empty", 0, locate_empty_applies }, .slot = CAND_SLOT_LOCATE,
      .routes = CR_DFA | CR_ATTEMPT, .tok = "empty", .map = CM_NONE, .hands = CT_VERDICT,
      .needs = { [CAND_ROUTE_DFA]     = { .front = CN(CAND_SLOT_PRESENCE) },
                 [CAND_ROUTE_ATTEMPT] = { .front = CAND_FRONT_DFA } },
      .u.locate = { .emit = { [CAND_ROUTE_DFA] = emit_empty_unanchored,
                              [CAND_ROUTE_ATTEMPT] = emit_empty_attempt },
                    .scan = { [CAND_ROUTE_DFA] = "empty", [CAND_ROUTE_ATTEMPT] = "empty" },
                    .nomatch = true, .whole = true, .fin = CT_VERDICT } },
'
