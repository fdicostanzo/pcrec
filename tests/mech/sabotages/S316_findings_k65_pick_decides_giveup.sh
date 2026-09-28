# S316 — [FINDINGS] B2 F-12: K65's FIX REVERTED, SEEN THROUGH THE ANALYSES
# (src/gen/emit_dfa.c, `emit_req_set_rest`): a VM artifact with no DFA scan
# in front tests only the PICKED member of the necessary set again, so
# whether a subject lacking another member answers NOMATCH or gives up
# follows the pick — and under [FINDINGS] B2 the pick is whatever a user's
# bundle makes it, so every bundle becomes a give-up switch (design §6.2a,
# [r2 S-F1]; docs/dev/known_issues.md K65).
#
# THE SAME PLANT AS S277, A DIFFERENT DETECTOR, and that is the point of the
# row: S277 proves the corpus sees the revert under the DEFAULT's pick; this
# row proves the findings suite sees it under BUNDLES that move the pick —
# run_findings_tests.sh §9 compiles K65's repro under a bundle picking `Z` and
# one picking `@` and requires NOMATCH (exit 1) on every subject lacking
# either member; the sabotaged tree gives up (exit 3) under one of them.
SAB_ID="S316-findings-k65-pick-decides-giveup"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="findings"
SAB_DESC="the [K65] whole-set pre-check is never emitted, so on a VM route with no DFA front only the picked member is tested and a bundle that moves the pick turns a NOMATCH into a step-budget give-up — a rate switching a give-up, the transition design §6.2a forbids"
SAB_DOC_FIGURE="findings red on §9 (K65 witness cells exit 3 under the bundle whose pick misses the absent member, and under the default's). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S316."
SAB_REACH='python3 "$TREE/tests/findings/res_fixtures.py" "$REACH_TMP/r" && "$PCREC" --features all -p rx -I "$REACH_TMP/r/A" --analysis picka -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+Z.@\\1" && grep -q "^#define RX_VM_PREFILTER \"none\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_BYTE \"64\"" "$REACH_TMP/o.c" && grep -q "static const unsigned char rq_set\[\] = { 90 };" "$REACH_TMP/o.c" && echo REACH-FINDINGS-K65-WHOLE-SET-UNDER-BUNDLE'
SAB_REACH_EXPECT="REACH-FINDINGS-K65-WHOLE-SET-UNDER-BUNDLE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (pcrec_artifact_has_dfa_scan(cx)) return;
    if (r->len >= 2) for (k = 0; k < r->whole_len; k++) done[r->whole[k]] = true;'
SAB_AFTER='    return;   /* SABOTAGE S316: the K65 whole-set half never emitted */
    if (r->len >= 2) for (k = 0; k < r->whole_len; k++) done[r->whole[k]] = true;'
