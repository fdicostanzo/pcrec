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
SAB_BEFORE='    long long k = kb.v;
    /* the re-ask'\''s condition, per sign of K: the kept hit is stale */'
SAB_AFTER='    long long k = kb.v;
    if (!pcrec_bound_bounded(kb)) return;   /* SABOTAGE S3075: no stop */
    /* the re-ask'\''s condition, per sign of K: the kept hit is stale */'
# RE-ANCHORED 2026-11-20 (lane l3build, span_arms L3 RM-2, D-7): K is a `PfBound` (state +
# signed value); the re-entry's value line `k = kb.v` follows the ask, and the anchor is that
# line plus the re-ask printf (the two-line site, review r51 READYL3-8). Intent unchanged.
# RE-ANCHORED 2026-11-20 (lane l3feat2, span_arms L3 feature): the re-ask's condition is now chosen per sign of K
# (D-8) before its printf, so the anchor is the value line plus that comment; the plant returns
# before the re-ask at no bound, as before. Its REACH grep stays valid: `a+xyz` is unbounded,
# whose condition is the plain `landmark_position < attempt_position`. Intent unchanged.
