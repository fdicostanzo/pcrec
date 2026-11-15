#!/usr/bin/env bash
# S1131 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- C8 is skipped: the machine and the slice are not asked for an exact product, so a hull is stated exact (exact_len := k)
# kit_proof.md §6.3 S1131: `ac|bd` is admitted with S_0 x S_1 = {a,b} x {c,d}; "ad": PCRE2 nomatch.
# RE-ANCHORED 2026-11-15 (lane covs1, [COVER-CAP] stage 1, cover_cap.md §5.4 READY-1):
# C8 is decision-redundant once the walk stops at L (C10 declines what C8 declines), so the
# `ac|bd` verdict cannot flip; the witness is the `facts` row `ac|bd`, whose VALUE carries
# the why (exact/machine-inexact -> end-at-k under the plant). The plant skips C8's test and
# keeps its MkEnd fill, the record's counted copy (the slice comparison it used to skip is
# deleted).
SAB_ID='S1131-cover_c8_skipped'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C8 is skipped: a walk that stopped at a branch is not named exact/machine-inexact, and C10 is left to decline it (end-at-k)'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'ac|bd'"'"' --facts'
SAB_REACH_EXPECT='REACH-FACTS-EQUAL'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    int k = st->w.k;
    if (st->w.stop == COVER_STOP_BRANCH) { st->detail = "machine-inexact"; return false; }'
SAB_AFTER='    int k = st->w.k;
    if (1) { st->cv->end.k = (uint8_t)(k <= MF_MAX_SPAN_POS ? k : 0); memcpy(st->cv->end.set, st->w.set, (size_t)st->cv->end.k * 32); return true; }   /* SABOTAGE S1131 */
    if (st->w.stop == COVER_STOP_BRANCH) { st->detail = "machine-inexact"; return false; }'
