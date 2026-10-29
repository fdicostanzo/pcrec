# S1544 (lane r30b, 2026-10-29; [MEMFN] R-30, memfn/docs/requests.md): A RUN PART DROPPED WITH NOTHING IMPLYING IT. The use skips every run part the site
# does not keep (`ret_pred`), not only one a later part implies, so the whole run
# (K66's no-match proof on the route with no DFA scan) is never asked either: the K66
# subjects give up on the step budget where the answer is NOMATCH (the harness arm),
# and section D finds no `rx_reqrun_whole(` ask.
SAB_ID="S1544-run-part-dropped-without-whole"
SAB_FILE="memfn/src/precheck.c"
SAB_SUITES="memfnfinder harness"
SAB_HARNESS_TARGET="tests/base/k66_precheck_whole_run.rxt"
SAB_DESC="the pre-check's use skips every run part it does not keep, so a run part nothing implies (the whole run) is never asked and K66's subjects give up where the answer is NOMATCH"
SAB_DOC_FIGURE="OWED: read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1544."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (implied_by(art, s, i, &at) >= 0) continue;     /* R-30: not asked */'
SAB_AFTER='        if (implied_by(art, s, i, &at) >= 0 || (p->fn_ref && i != s->ret_pred)) continue;     /* SABOTAGE S1544 */'
SAB_REACH='"$PCREC" --features all -e byte -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+eeeeeeee~#~#~#~#\\1" && grep -qF "rx_reqrun_whole(subject, subject_length, search_from)" "$REACH_TMP/o.c" && ! grep -qF "rx_reqrun(" "$REACH_TMP/o.c" && echo REACH-R30-WINDOW-DROPPED'
SAB_REACH_EXPECT="REACH-R30-WINDOW-DROPPED"
