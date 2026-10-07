#!/usr/bin/env bash
# S566 ([MEMFN] R4c', lane r4c2fix) -- THE PRE-CHECK'S SITE IS NEVER DEFINED.
#
# `emit_unanchored` stops calling `pcrec_emit_req_run_blocks`, so
# `job->mf_pre` stays NULL while the admission still EMITS a pre-check. Before
# R4c' `pcrec_emit_req_byte_check` read a NULL site as "declined" and emitted
# nothing: the pre-check vanished from every unanchored DFA artifact, NO
# ANSWER MOVED (it is an optimisation), and no suite could see it. It now
# refuses the compile as an internal error when the admission emits and no
# site was defined, so the harness on reqcube.rxt (unanchored DFA artifacts
# with an emitted pre-check, `frank|fred` among them) reads refused compiles
# as failed cells. Detector: that refusal, through the harness arm.
# SAB_REACH: on the clean tree `frank|fred` is an unanchored DFA artifact
# whose pre-check the admission emits, so the plant meets an emitted site.
SAB_ID="S566-precheck-site-never-defined"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="emit_unanchored no longer defines the pre-check's kit site (pcrec_emit_req_run_blocks deleted), so job->mf_pre is NULL where the admission emits a pre-check: pcrec_emit_req_byte_check must refuse the compile, not silently emit nothing"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/r4c2fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S566."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "frank|fred" && grep -q "^#define RX_DFA_SCAN \"unanchored\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_WHY \"emitted\"" "$REACH_TMP/o.c" && echo REACH-PRECHECK-EMITTED'
SAB_REACH_EXPECT="REACH-PRECHECK-EMITTED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='     * condition as its call below. */
    if (cx->job->fit.chosen == ENGM_DFA) pcrec_emit_req_run_blocks(cx, c);'
SAB_AFTER='     * condition as its call below. */
    /* SABOTAGE S566: the pre-check site is never defined */'
