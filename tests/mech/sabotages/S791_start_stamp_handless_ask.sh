#!/usr/bin/env bash
# S791 ([START-LANDING] SL3, lane slbuild; docs/design/start_landing.md §7.5 row 13; docs/dev/lanes/slbuild_report.md) -- the start stamp reads a fresh EXISTS ask instead of the PATH's cell.
# Detector: run_dfa_stamps.sh [start] on every rev-end artifact whose width is fixed (`abc$`: the text carries the reverse walk, the stamp would read end-minus-width).
SAB_ID='S791-start-stamp-handless-ask'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfastamps'
SAB_DESC='<PREFIX>_DFA_START and rx_info.search_form read RECOVER with the composite'\''s EXISTS hand on every body, so a rev-end artifact of fixed width names end-minus-width over a reverse walk'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S791.'
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/o.c" --pattern "abc\$" && grep -q "^#define RX_DFA_START \"reverse-pass\"" "$REACH_TMP/o.c" && echo REACH-REVEND-START'
SAB_REACH_EXPECT='REACH-REVEND-START'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return a ? a : dfa_search_start_of(cx)->tok;'
SAB_AFTER='    return a ? a : dfa_search_start_at(cx, 0x43u)->tok;   /* SABOTAGE S791: 0x43 = CT_LOWER | CT_UPPER | CT_START, the composite EXISTS hand, on every body */'
