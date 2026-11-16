#!/usr/bin/env bash
# S3260 ([COVER-CAP] stage 2, lane covs2b; review r18 CHECKS-1, the combined branch's W18) -- the window search's width falls back to the anchored ceiling less one, not to the built-in default: a compile that names no width admits every cover the kit's bounds admit
# Witness: verdict `[0-9a-f]{@D1}` (one past the shipped width default, loader.sh) on the default arm expects decline (width-limit) and reads cover.
# Why only now: until the kit's raise (MF_WSPAN_POS 32 -> 4095) the kit's own bounds declined k = D + 1 under the same name whatever the fallback read,
# so no row could tell the fallback apart (r18 CHECKS-1). Control: an explicit `--window-search-width` never reads the fallback (the `W` arm).
SAB_ID='S3260-cover_width_default_fallback_ceiling'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='cover_width_limit falls back to PCREC_ANCHORED_MAX_STATES - 1 where the caller names no width, not to the built-in default: a cover past the default is admitted on the default arm'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh, the verdict row [0-9a-f]{@D1}); by hand 2026-11-16 (lane covs2b): `--window-search-width=4094` on [0-9a-f]{33} reads cover, the default reads width-limit; the measured figure is the cloud mech run owed after lane covs2b.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'[0-9a-f]{@D1}'"'"' --why'
SAB_REACH_EXPECT='REACH-DECLINE
REACH-WHY=[width-limit]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return w ? w : PCREC_DEFAULT_WINDOW_SEARCH_WIDTH;'
SAB_AFTER='    return w ? w : PCREC_ANCHORED_MAX_STATES - 1;   /* SABOTAGE S3260 */'
