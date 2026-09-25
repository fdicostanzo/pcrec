# S277 — [K65] THE PRE-CHECK'S WHOLE-SET HALF REMOVED (src/gen/emit_dfa.c,
# `emit_req_set_rest`): a VM artifact with no DFA scan in front goes back to
# testing ONE member of the necessary set — the pick — so whether a subject
# lacking another member answers NOMATCH or gives up on the step budget
# follows a SPEED choice (docs/dev/known_issues.md K65; the pick differs by
# encoding, so the same subject flips with `-e`).
#
# ANSWER-DETECTABLE, like S274 one rule over: the plant is the defect, and it
# moves NOMATCH -> PCREC_ERR_STEPS. The `harness` arm is aimed at
# tests/base/k65_precheck_whole_set.rxt and must go RED; `prechecks` §5.7 is
# the structural second detector.
SAB_ID="S277-precheck-whole-set-removed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks harness"
SAB_HARNESS_TARGET="tests/base/k65_precheck_whole_set.rxt"
SAB_DESC="the [K65] whole-set half of the necessary-byte pre-check is never emitted, so a VM artifact with no DFA scan tests only the picked member and a subject lacking another member gives up on the step budget where the answer is NOMATCH — the pick-dependent give-up K65 recorded"
SAB_DOC_FIGURE="tests/base/k65_precheck_whole_set.rxt is the answer-level detector: the three '...Zb' n cells of block 1 (byte), the three '...@b' n cells of block 2 (utf8) and the three '...@#' n cells of block 3 (the run form) fail as a steps give-up — corpus:9fail/15pass, the same 9 the pre-fix compiler (5a2094e7) fails. tests/codegen/run_prechecks.sh section 5.7 reports the three rows expecting an rq_set array finding none — prechecks:3fail/263pass. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S277."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree the
# K65 witness is an unguarded VM artifact and emits the whole-set array.
SAB_REACH='"$PCREC" --features all -e byte -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+Z.@\\1" && grep -q "^#define RX_VM_PREFILTER \"none\"" "$REACH_TMP/o.c" && grep -q "static const unsigned char rq_set\[\] = { 64 };" "$REACH_TMP/o.c" && echo REACH-K65-WHOLE-SET-EMITTED'
SAB_REACH_EXPECT="REACH-K65-WHOLE-SET-EMITTED"
SAB_COUNT=1
SAB_BEFORE='    if (pcrec_artifact_has_dfa_scan(cx)) return;
    if (r->len >= 2) for (k = 0; k < r->len; k++) done[r->bytes[k]] = true;'
SAB_AFTER='    return;   /* SABOTAGE S277: the K65 whole-set half never emitted */
    if (r->len >= 2) for (k = 0; k < r->len; k++) done[r->bytes[k]] = true;'
