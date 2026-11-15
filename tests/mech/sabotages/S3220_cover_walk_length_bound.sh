#!/usr/bin/env bash
# S3220 ([COVER-CAP] stage 1, lane covs1; docs/design/cover_cap.md §5.4 plant (a)) -- a length bound is put back on the cover walk (j < 32): the exact stretch of a longer shape is cut at 32 positions and its record states 32
# Witness: facts `a{40}(?:b|cc)`: statement-fits|41|41|... becomes a 32-position record; no other plant cuts a one-row line short.
# Shared witness (review r9 covs1 CHECKS-3, cross-plant matrix): S3223 (LOUD) and S3224 flip `a{40}(?:b|cc)` too; detection holds because each row runs its plant alone.
SAB_ID='S3220-cover_walk_length_bound'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='a length bound is put back on the cover walk (j < 32): the exact stretch of a longer shape is cut at 32 positions and its record states 32'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the cloud mechrows run owed by lane covs1 (docs/dev/lanes/covs1_report.md).'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'a{40}(?:b|cc)'"'"' '"'"'--facts'"'"' --why'
SAB_REACH_EXPECT='REACH-FACTS-EQUAL
REACH-WHY=[statement-fits]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (;; j++) {
        uint8_t first[32], *set;'
SAB_AFTER='    for (; j < 32; j++) {   /* SABOTAGE S3220 */
        uint8_t first[32], *set;'
