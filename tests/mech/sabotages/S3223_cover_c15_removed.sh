#!/usr/bin/env bash
# S3223 ([COVER-CAP] stage 1, lane covs1; docs/design/cover_cap.md §5.4 plant (d); RE-AIMED at stage 2 as the BYPASS row, lane covs2a, cover_cap.md §11.6.3) -- C15 width-limit always passes: a cover past the window search's width is admitted on the default arm
# Witness: verdict `[0-9a-f]{@D1}` (one past the shipped width default, loader.sh) on the default arm: decline becomes a cover past the default.
# Since the kit's raise (MF_WSPAN_POS 4095, lane memfn-span4k-raise) the planted tree COMPILES that cover and reads `cover`; the stage-1 path
# (kit bounds at 32, cover_window's named internal error, a failed compile, READYLIMIT-7) no longer applies (lane covs2g, r45read W20/W22).
# Shared (review r9 covs1 CHECKS-3, cross-plant matrix): the facts rows `a{600}(?:b|cc)` and `a{4095}` also lose width-limit under this plant;
# `[0-9a-f]{@D1}` is flipped by S3223 alone (the off-by-one row S3234 leaves it declined).
# RE-AIMED 2026-11-15 (lane covs2a, A4/A7): plant text re-anchored on cc_fits' return line with the width conjunct; REACH moved from the
# 40-letter literal (a cover at any default >= 40) to `[0-9a-f]{@D1}`, REACH-WHY width-limit.
SAB_ID='S3223-cover_c15_removed'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C15 width-limit always passes (the bypass): a cover past the window search'"'"'s width is admitted on the default arm, past the default'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh, the verdict row [0-9a-f]{@D1}); the measured figure is the cloud mech run owed by lane covs2a (docs/dev/lanes/covs2a_report.md).'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'[0-9a-f]{@D1}'"'"' --why'
SAB_REACH_EXPECT='REACH-DECLINE
REACH-WHY=[width-limit]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (st->w.stop == COVER_STOP_BRANCH) return true;
    return k <= cover_width_limit(st->cx) &&
           k <= MF_WSPAN_POS && k + 1 <= MF_WREACH && k < MF_MAX_FWD;'
SAB_AFTER='    if (st) return true;   /* SABOTAGE S3223 */
    if (st->w.stop == COVER_STOP_BRANCH) return true;
    return k <= cover_width_limit(st->cx) &&
           k <= MF_WSPAN_POS && k + 1 <= MF_WREACH && k < MF_MAX_FWD;'
