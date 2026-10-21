#!/usr/bin/env bash
# S1139 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- C9 is dropped: a row on the walk carrying a non-identity eol view is admitted
# kit_proof.md §6.3 S1139: `cat$` under -fno-rev-end, "9cat\n" from 0: PCRE2 (1,4), the plant none.
SAB_ID='S1139-cover_c9_dropped'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C9 is dropped: a row on the walk carrying a non-identity eol view is admitted'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'R'"'"' '"'"'cat$'"'"''
SAB_REACH_EXPECT='REACH-DECLINE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static bool cc_eol(CoverSt *st)
{
    for (int j = 0; j <= st->w.k; j++)'
SAB_AFTER='static bool cc_eol(CoverSt *st)
{
    if (st) return true;   /* SABOTAGE S1139 */
    for (int j = 0; j <= st->w.k; j++)'
