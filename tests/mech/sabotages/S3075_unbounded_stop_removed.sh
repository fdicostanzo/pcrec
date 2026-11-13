#!/usr/bin/env bash
# S3075 ([REQ-PAST-LAST], lane rpfix, review r2-reqpast CHK-2/CHK-3) -- THE
# UNBOUNDED ROW'S STOP IS REMOVED. At no bound the row's whole job is the
# re-ask after a failed attempt (a miss answers NOMATCH); the plant returns
# before it, so the attempts never ask again. ANSWERS DO NOT MOVE except by a
# give-up: the step-budget cell of tests/litscan/handoff_vm.rxt (`(a|aa|b)+cxyz`
# under steps=3000) and run_prechecks.sh [5.12l]'s presence pin (an unbounded
# attempt-loop artifact without its `landmark_position < attempt_position`
# re-ask) are the detectors; prechecks is named.
SAB_ID='S3075-unbounded-stop-removed'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='prechecks'
SAB_DESC='the unbounded attempt-loop row returns before its re-ask, so no attempt past the last occurrence is ever stopped'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rpfix_report.md, CHANGES); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3075.'
SAB_REACH='"$PCREC" --features all -p rx --engine=vm -o "$REACH_TMP/o.c" --pattern '\''a+xyz'\'' && grep -q '\''^#define RX_REQ_HANDOFF "unbounded"'\'' "$REACH_TMP/o.c" && grep -q '\''^ *if (landmark_position < attempt_position) {$'\'' "$REACH_TMP/o.c" && echo REACH-STOP'
SAB_REACH_EXPECT='REACH-STOP'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    long long k = req_handoff_k(cx);
    pcrec_sb_printf(c, "%s    if (landmark_position < %s) {\n", ind, pos);'
SAB_AFTER='    long long k = req_handoff_k(cx);
    if (k >= PCREC_W_UNBOUNDED) return;   /* SABOTAGE S3075: no stop */
    pcrec_sb_printf(c, "%s    if (landmark_position < %s) {\n", ind, pos);'
