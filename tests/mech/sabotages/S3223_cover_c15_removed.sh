#!/usr/bin/env bash
# S3223 ([COVER-CAP] stage 1, lane covs1; docs/design/cover_cap.md §5.4 plant (d)) -- C15 statement-fits is removed (stage 1): a stretch past the kit window's 32 positions reaches MkEnd's fill, which refuses it with its named internal error (never an overrun)
# Witness: verdict 40-letter literal: decline becomes a failed compile (the named internal error); nothing else states a 40-position span at stage 1.
# Shared (review r9 covs1 CHECKS-3, cross-plant matrix): the facts row `a{40}(?:b|cc)` also goes LOUD under this plant (k = 41), so it is not the only 40+-position statement; the 40-letter verdict is flipped by S3223 alone.
SAB_ID='S3223-cover_c15_removed'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C15 statement-fits is removed (stage 1): a stretch past the kit window'"'"'s 32 positions reaches MkEnd'"'"'s fill, which refuses it with its named internal error (never an overrun)'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the cloud mechrows run owed by lane covs1 (docs/dev/lanes/covs1_report.md).'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'abcdefghijklmnopqrstuvwxyzabcdefghijklmn'"'"' --why'
SAB_REACH_EXPECT='REACH-DECLINE
REACH-WHY=[statement-fits]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (st->w.stop == COVER_STOP_BRANCH) return true;
    return k <= MF_WSPAN_POS && k + 1 <= MF_WREACH && k < MF_MAX_FWD;'
SAB_AFTER='    if (st) return true;   /* SABOTAGE S3223 */
    if (st->w.stop == COVER_STOP_BRANCH) return true;
    return k <= MF_WSPAN_POS && k + 1 <= MF_WREACH && k < MF_MAX_FWD;'
