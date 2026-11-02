# S1545 (lane r30b, 2026-10-29; [MEMFN] R-30, memfn/docs/requests.md): THE LEAD AT THE WRONG OFFSET. The led compare tests the window's bytes one byte to
# the right of where they lie in the whole run, so a candidate holding the whole run
# is rejected: the pre-check answers NOMATCH on a subject that matches (the harness
# arm's match cells) and section D's pinned led compare differs.
SAB_ID="S1545-lead-compares-wrong-bytes"
SAB_FILE="memfn/src/runcmp.c"
SAB_SUITES="memfnfinder harness"
SAB_HARNESS_TARGET="tests/base/k66_precheck_whole_run.rxt"
SAB_DESC="the whole run's led compare tests the window's bytes one byte off their place in the run, so the pre-check rejects subjects that match"
SAB_DOC_FIGURE="OWED: read the figure from a run: bash tests/mech/run_sabotage_matrix.sh S1545."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        rc_render(art, &w, base, off + (int32_t)at, NULL, 0, 0, 0, c))'
SAB_AFTER='        rc_render(art, &w, base, off + (int32_t)at + 1, NULL, 0, 0, 0, c))   /* SABOTAGE S1545 */'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(a)(b)(c)(d)(e)(f)(g)(h)(i)\\9" && grep -qF "if (!memcmp(subject + cand + 1, \"bcdefghi\", 8) && rx_w8(subject + cand) == rx_w8(\"abcdefgh\")) return cand;" "$REACH_TMP/o.c" && echo REACH-R30-LED-COMPARE'
SAB_REACH_EXPECT="REACH-R30-LED-COMPARE"
