#!/usr/bin/env bash
# S790 ([START-LANDING] SL3, lane slbuild; docs/design/start_landing.md §7.5 row 8; docs/dev/lanes/slbuild_report.md) -- the RECOVER hand filter dropped: end-minus-width also takes the WINDOW hand.
# Detector: the rev-end walk's own assertion (its WINDOW ask must select reverse-pass) refuses every end-pinned fixed-width compile: run_rev_end.sh's witnesses and tests/assertions/rev_end.rxt; the trace build's self-check (table-recover-start-unproved) in run_cand_oracle.sh.
SAB_ID='S790-recover-hand-filter-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend candoracle harness'
SAB_DESC='end-minus-width takes the speculative WINDOW hand rev-end asks RECOVER with, so an end-pinned fixed-width pattern'\''s walk would read its start off an unverified end'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S790.'
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/o.c" --pattern "abc\$" && grep -q "^#define RX_DFA_SCAN \"rev-end\"" "$REACH_TMP/o.c" && echo REACH-REVEND-FIXED'
SAB_REACH_EXPECT='REACH-REVEND-FIXED'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .hands = CT_START, .list = { [CAND_ROUTE_DFA] = { "search-start", 2, "end-minus-width" } },
      .take = { [CAND_ROUTE_DFA] = { CAND_HAND_EXISTS } },'
SAB_AFTER='      .hands = CT_START, .list = { [CAND_ROUTE_DFA] = { "search-start", 2, "end-minus-width" } },
      .take = { [CAND_ROUTE_DFA] = { CAND_HAND_EXISTS, CAND_HAND_WINDOW } },   /* SABOTAGE S790 */'
