#!/usr/bin/env bash
# S459 ([K82], lane k82fix) -- K65'S REST RE-TESTS THE LEAD.
#
# On the no-DFA-scan VM route K65's rest memchrs every necessary-set member the
# first half did not test, and the lead is one the first half tested. This
# plant forgets it, so the same byte is memchr'd twice per call. Answer-
# invisible (both tests are sound). Detector: run_prechecks.sh §5.8's
# `(x?)([a-z]+)+Z.@#\1` row (rq_set "none" reads "90") and §5.9's
# `Q.abcdefghij` row (reads "81").
SAB_ID="S459-set-rest-retests-lead"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC="K65's whole-set half on the no-DFA-scan VM route no longer skips the byte the set-leads row already tested, so it memchrs it a second time"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/k82fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S459."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+Z.@#\\1" && grep -q "!memchr(subject + search_from, 90," "$REACH_TMP/o.c" && ! grep -q "rq_set" "$REACH_TMP/o.c" && echo REACH-LEAD-NOT-RETESTED'
SAB_REACH_EXPECT="REACH-LEAD-NOT-RETESTED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (req_lead_byte(cx) >= 0) done[req_lead_byte(cx)] = true;'
SAB_AFTER='    /* SABOTAGE S459: the lead not marked tested */'
