# S1546 (lane r30b, 2026-10-29; [MEMFN] R-30, memfn/docs/requests.md): THE LEAD IGNORED (the wrong order). The verify chain compares the whole run in its
# row's own order, so a candidate the window would have rejected after one compare can
# cost more (the R-30 never-slower argument's guard; answer-neutral). Section D's
# pinned led compare differs.
SAB_ID="S1546-lead-dropped-from-verify"
SAB_FILE="memfn/src/ofsskip.c"
SAB_SUITES="memfnfinder"
SAB_DESC="the verify chain ignores the lead and compares the whole run in its row's own order, so a candidate the window rejects no longer costs one compare"
SAB_DOC_FIGURE="OWED: read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1546."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (t->kind == MF_T_RUN && x->lead_len) {'
SAB_AFTER='        if (t->kind == MF_T_RUN && x->lead_len && 0) {   /* SABOTAGE S1546 */'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(a)(b)(c)(d)(e)(f)(g)(h)(i)\\9" && grep -qF "if (!memcmp(subject + cand + 1, \"bcdefghi\", 8) && rx_w8(subject + cand) == rx_w8(\"abcdefgh\")) return cand;" "$REACH_TMP/o.c" && echo REACH-R30-LED-COMPARE'
SAB_REACH_EXPECT="REACH-R30-LED-COMPARE"
