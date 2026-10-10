#!/usr/bin/env bash
# S787 ([START-LANDING] SL2, lane slbuild; docs/design/start_landing.md §7.5 row 9; docs/dev/lanes/slbuild_report.md) -- the body dispatch forks from the stamp: an end-minus-width selection emits the landing body.
# Detector: run_dfa_stamps.sh [start] (the stamp against the text) and run_start_landing.sh §2; the answers move too (no landing record).
SAB_ID='S787-dispatch-forks-from-stamp'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfastamps startlanding'
SAB_DESC='unanch_scan dispatches end-minus-width selections whose pattern also satisfies the one-character fact to the landing body, while the stamp and rx_info.search_form still read end-minus-width'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S787.'
SAB_REACH='"$PCREC" -p rx -o "$REACH_TMP/o.c" --pattern "[a-z]" && grep -q "^#define RX_DFA_START \"end-minus-width\"" "$REACH_TMP/o.c" && echo REACH-BOTH-APPLY'
SAB_REACH_EXPECT='REACH-BOTH-APPLY'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                        const CandRow *rr)
{
    unsigned act = rr->u.recover.act;'
SAB_AFTER='                        const CandRow *rr)
{
    unsigned act = rr->u.recover.act == CRA_END_MINUS_W && pcrec_fact_land_char(cx)->holds ? CRA_LANDING : rr->u.recover.act;   /* SABOTAGE S787 */'
