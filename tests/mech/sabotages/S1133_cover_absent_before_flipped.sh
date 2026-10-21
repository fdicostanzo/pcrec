#!/usr/bin/env bash
# S1133 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- absent-before is flipped: a seeded entry equal to X reads FAILS where the subject start satisfies the context
# kit_proof.md §6.3 S1133: `\bcat` on "cat": PCRE2 (0,3), the plant 0.
SAB_ID='S1133-cover_absent_before_flipped'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='absent-before is flipped: a seeded entry equal to X reads FAILS where the subject start satisfies the context'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'\bcat'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (d->s0 == r0) e->absent_before = MK_ABS_SATISFIES;'
SAB_AFTER='    if (d->s0 == r0) e->absent_before = MK_ABS_FAILS;   /* SABOTAGE S1133 */'
