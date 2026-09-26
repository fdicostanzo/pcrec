# S278 — [K66] THE PRE-CHECK'S WHOLE-RUN COMPARE REMOVED (src/gen/emit_dfa.c,
# `req_run_tests`, formerly `emit_req_run_rest`): a VM artifact with no DFA scan in front goes back to
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
# tests/base/k66_precheck_whole_run.rxt and must go RED; `prechecks` §5.9 is
# the structural second detector.
SAB_ID="S278-precheck-whole-run-removed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks harness"
SAB_HARNESS_TARGET="tests/base/k66_precheck_whole_run.rxt"
SAB_DESC="the [K66] whole-run compare of the necessary-run pre-check is never emitted, so a VM artifact with no DFA scan compares only the 8-byte window the prior cut from a longer run and a subject holding that window but not the whole run gives up on the step budget where the answer is NOMATCH — the window-dependent give-up K66 recorded"
SAB_DOC_FIGURE="tests/base/k66_precheck_whole_run.rxt is the answer-level detector: the two e...~#~#~#~# n cells and the two ...eeeeeeee!~#~#~#~# n cells of block 1 (byte) and the two ...eeeeeeee~# and two ...eeeeeeee!~#~#~#~# n cells of block 2 (utf8) fail as a steps give-up — corpus:8fail/8pass, the same 8 the pre-fix compiler (bbbf58e5) fails. tests/codegen/run_prechecks.sh section 5.9 reports the three rows expecting a whole-run compare finding none — prechecks:3fail/275pass (re-measured at landing on lane k66fix's rebase onto main, 2026-09-25). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S278."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree the
# K66 witness is an unguarded VM artifact whose REQ_RUN names an 8-byte window
# and which emits the 16-byte whole-run compare.
SAB_REACH='"$PCREC" --features all -e byte -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+eeeeeeee~#~#~#~#\\1" && grep -q "^#define RX_VM_PREFILTER \"none\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_RUN \"7e237e237e237e23@0\"" "$REACH_TMP/o.c" && grep -qF "if (!memcmp(subject + cand, \"eeeeeeee~#~#~#~#\", 16)) return cand;" "$REACH_TMP/o.c" && grep -qF "rx_reqrun_whole(subject, subject_length, search_from)" "$REACH_TMP/o.c" && echo REACH-K66-WHOLE-RUN-EMITTED'
SAB_REACH_EXPECT="REACH-K66-WHOLE-RUN-EMITTED"
# [OPT-LITSCAN] S1 step 6 re-anchor (lane s1step6, 2026-09-26): the whole
# run is now the second test of `req_run_tests`, the one derivation both the
# file-scope `rx_reqrun_whole` block and its call read, so the plant (return
# after the window's test) removes the block and the call together. Intent
# unchanged: the K66 whole-run compare is never emitted.
SAB_COUNT=1
SAB_BEFORE='    if (pcrec_artifact_has_dfa_scan(cx) || r->whole_len <= r->len) return 1;'
SAB_AFTER='    return 1;   /* SABOTAGE S278: the K66 whole-run compare never emitted */'
