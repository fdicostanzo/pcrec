#!/usr/bin/env bash
# S3226 ([COVER-CAP] stage 1, lane covs1f; review r9 covs1 CHECKS-5, the coordinator's plant V16) -- the walk's row comparison reads only the low 16 bytes of the 32-byte set (bytes 0x00-0x7f), so two rows whose next-byte sets differ only in the high half are read as one set and a branch is stated exact
# Witness: verdict u `aé|bè` (decline exact/machine-inexact; the rows at depth 2 differ only at A8/A9) becomes a cover that matches "aè" (PCRE2: no match); the facts u row of the same pattern moves to cover|3|3 too. Shared: no other row's plant flips either (they are ASCII-only witnesses).
SAB_ID='S3226-cover_set_compare_low_half'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='the walk compares only the low 16 bytes of the per-row next-byte set, so rows differing only in bytes 0x80-0xff are read as one set and a branch is stated exact'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh: verdict u aé|bè and facts u aé|bè); measured locally by lane covs1f on the review plant V16 (2 checks fail: verdict u and facts u aé|bè), the cloud mechrows figure owed (docs/dev/lanes/covs1f_report.md).'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'u'"'"' '"'"'aé|bè'"'"' --why'
SAB_REACH_EXPECT='REACH-DECLINE
REACH-WHY=[exact/machine-inexact]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            else if (memcmp(first, b32, 32)) w->stop = COVER_STOP_BRANCH;'
SAB_AFTER='            else if (memcmp(first, b32, 16)) w->stop = COVER_STOP_BRANCH;   /* SABOTAGE S3226 */'
