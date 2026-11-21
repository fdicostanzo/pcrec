#!/usr/bin/env bash
# S1139 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- C9 is dropped: a row on the walk carrying a non-identity eol view is admitted
# kit_proof.md §6.3 S1139: `cat$` under -fno-rev-end, "9cat\n" from 0: PCRE2 (1,4), the plant none.
# Shared (review r9 covs1 CHECKS-3, cross-plant matrix): S1139 owns no witness only it flips: `R cat$` is flipped by S3225 too, and this plant also flips the S1136 and S3225 witnesses.
# RE-ANCHORED 2026-11-15 (lane covs1, [COVER-CAP] stage 1, cover_cap.md §5.4 R-12):
# C9 reads the walk's own mark (depths 0..k inclusive); the plant ignores it.
SAB_ID='S1139-cover_c9_dropped'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C9 is dropped: a row on the walk carrying a non-identity eol view is admitted'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'R'"'"' '"'"'cat$'"'"' --why'
SAB_REACH_EXPECT='REACH-DECLINE
REACH-WHY=[no-eol-view]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static bool cc_eol(CoverSt *st)
{
    return !st->w.eolview;'
SAB_AFTER='static bool cc_eol(CoverSt *st)
{
    if (st) return true;   /* SABOTAGE S1139 */
    return !st->w.eolview;'
