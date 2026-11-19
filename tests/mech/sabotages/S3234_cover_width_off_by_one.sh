#!/usr/bin/env bash
# S3234 ([COVER-CAP] stage 2 A7, lane covs2a; docs/design/cover_cap.md §11.6.3 OFF BY ONE) -- C15's width conjunct is off by one (k < width for k <= width): a cover exactly at the window search's width declines
# Witness: verdict `[0-9a-f]{@D}` (the shipped width default, loader.sh; the literal twin `@LD` too) expects cover and declines width-limit.
# Control: the bypass row S3223 leaves `@D` a cover; nothing else moves the comparison, and the kit's own bounds (32 at stage 1) admit k = D at D <= 32.
SAB_ID='S3234-cover_width_off_by_one'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C15'"'"'s width conjunct is off by one (k < width): a cover exactly at the window search'"'"'s width declines width-limit'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh, the verdict row [0-9a-f]{@D}); the measured figure is the cloud mech run owed by lane covs2a (docs/dev/lanes/covs2a_report.md).'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'[0-9a-f]{@D}'"'"' --why'
SAB_REACH_EXPECT='REACH-COVER
REACH-WHY=[cover]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return k <= cover_width_limit(st->cx) &&'
SAB_AFTER='    return k < cover_width_limit(st->cx) &&   /* SABOTAGE S3234 */'
