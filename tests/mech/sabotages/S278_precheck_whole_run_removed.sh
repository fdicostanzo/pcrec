# S278 — [K66] THE PRE-CHECK'S WHOLE-RUN COMPARE REMOVED (src/gen/emit_dfa.c,
# `emit_req_run_rest`): a VM artifact with no DFA scan in front goes back to
# comparing only the 8-byte WINDOW of a longer necessary run — the window the
# prior cut — so whether a subject holding that window but not another slice
# of the run answers NOMATCH or gives up on the step budget follows a SPEED
# choice (docs/dev/known_issues.md K66; the window differs by encoding, so the
# same subject flips with `-e`).
#
# ANSWER-DETECTABLE, like S277 one grain down: the plant is the defect, and it
# moves NOMATCH -> PCREC_ERR_STEPS. K65's whole-set half still skips every
# byte of the whole run under the plant, so no other half of the pre-check
# covers for it. The `harness` arm is aimed at
# tests/base/k66_precheck_whole_run.rxt and must go RED; `prechecks` §5.8 is
# the structural second detector.
SAB_ID="S278-precheck-whole-run-removed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks harness"
SAB_HARNESS_TARGET="tests/base/k66_precheck_whole_run.rxt"
SAB_DESC="the [K66] whole-run compare of the necessary-run pre-check is never emitted, so a VM artifact with no DFA scan compares only the 8-byte window the prior cut from a longer run and a subject holding that window but not the whole run gives up on the step budget where the answer is NOMATCH — the window-dependent give-up K66 recorded"
SAB_DOC_FIGURE="PENDING — measured below"
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree the
# K66 witness is an unguarded VM artifact whose REQ_RUN names an 8-byte window
# and which emits the 16-byte whole-run compare.
SAB_REACH='"$PCREC" --features all -e byte -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+eeeeeeee~#~#~#~#\\1" && grep -q "^#define RX_VM_PREFILTER \"none\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_RUN \"7e237e237e237e23@0\"" "$REACH_TMP/o.c" && grep -qF "!memcmp(subject + rp_c - 8, \"eeeeeeee~#~#~#~#\", 16)) break;" "$REACH_TMP/o.c" && echo REACH-K66-WHOLE-RUN-EMITTED'
SAB_REACH_EXPECT="REACH-K66-WHOLE-RUN-EMITTED"
SAB_COUNT=1
SAB_BEFORE='    if (pcrec_artifact_has_dfa_scan(cx) || r->whole_len <= r->len) return;'
SAB_AFTER='    return;   /* SABOTAGE S278: the K66 whole-run compare never emitted */'
