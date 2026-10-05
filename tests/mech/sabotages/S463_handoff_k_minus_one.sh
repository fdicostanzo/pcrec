#!/usr/bin/env bash
# S463 ([K82] (B), lane k82hbuild) -- THE HANDOFF STARTS ONE BYTE TOO LATE (K - 1).
#
# Witness: (?m)^x{2,5}(?i:cat) on "xxxxxCaT", the attempt route: (0,8) becomes
# NOMATCH. Detector: tests/litscan/handoff.rxt's maximum-offset rows on the
# attempt and hybrid routes. The design's own coverage report for this plant
# over every K > 0 mover is docs/dev/optloop/s4/k82hbuild/k82h_answers.py
# ONLY_K_POS=1 (litscan_k82h.md §4.2a (c)).
SAB_ID="S463-handoff-k-minus-one"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness prechecks"
SAB_HARNESS_TARGET="tests/litscan/handoff.rxt"
SAB_DESC='the handoff subtracts K - 1, so the scan starts one byte too late: a match that begins exactly K bytes before its window is lost on the attempt and hybrid routes (the unanchored scan'\''s reverse pass, bounded by search_from, re-finds its start, so that route hides it)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S463.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?m)^x{2,5}(?i:cat)'\'' && grep -q '\''^#define RX_REQ_HANDOFF "5"'\'' "$REACH_TMP/o.c" && echo REACH-HANDOFF-K5'
SAB_REACH_EXPECT='REACH-HANDOFF-K5'
SAB_REACH_POP='tests/litscan/handoff.rxt|^pattern \(\?m\)\^x\{2,5\}|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    long long k = pcrec_fact_req_run_maxoff(cx);
    StrBuf round = { 0 };'
SAB_AFTER='    long long k = pcrec_fact_req_run_maxoff(cx) - (pcrec_fact_req_run_maxoff(cx) > 0); /* SABOTAGE S463 */
    StrBuf round = { 0 };'
