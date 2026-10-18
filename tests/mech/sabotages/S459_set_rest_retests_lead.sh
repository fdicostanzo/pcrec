#!/usr/bin/env bash
# S459 ([K82], lane k82fix) -- K65'S REST RE-TESTS THE LEAD.
#
# On the no-DFA-scan VM route K65's rest memchrs every necessary-set member the
# first half did not test, and the lead is one the first half tested. This
# plant forgets it, so the same byte is memchr'd twice per call. Answer-
# invisible (both tests are sound). Detector: run_prechecks.sh §5.8's
# `(x?)([a-z]+)+Z.@#\1` row (rq_set "none" reads "90") and §5.9's
# `Q.abcdefghij` row (reads "81").
# [MEMFN] R17-b' B3b (lane b3b, 2026-10-18) RE-AIMED: the pre-check's presence
# decisions are the memfn kit's routed PRES rows (memfn/src/finder.c `fd_pres`,
# the ports in memfn/src/presence.c) and pcrec lays its parts out from their
# links, so the plant moves to the kit's line that makes the same choice.
# Here: pcrec's rest reads every verified member but the run's, the HEAD (the
# lead) included, so the lead is laid out twice; the kit's layout check refuses
# that define, so the pre-check suite fails loudly (intent unchanged: the same
# byte memchr'd twice).
SAB_ID="S459-set-rest-retests-lead"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks"
SAB_DESC="K65's whole-set half on the no-DFA-scan VM route no longer skips the byte the set-leads row already tested, so it memchrs it a second time"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/k82fix_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S459."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(x?)([a-z]+)+Z.@#\\1" && grep -q "!memchr(subject + search_from, 90," "$REACH_TMP/o.c" && ! grep -q "rq_set" "$REACH_TMP/o.c" && echo REACH-LEAD-NOT-RETESTED'
SAB_REACH_EXPECT="REACH-LEAD-NOT-RETESTED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (t->kind == MF_T_SET && cls->pres[i].verify && cls->pres[i].order == 2 &&'
SAB_AFTER='            if (t->kind == MF_T_SET && cls->pres[i].verify && cls->pres[i].order != 1 &&   /* SABOTAGE S459 */'
