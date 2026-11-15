#!/usr/bin/env bash
# S3221 ([COVER-CAP] stage 1, lane covs1; docs/design/cover_cap.md §5.4 plant (b)) -- the walk compares ROWS, not their byte sets: a second row at a depth ends the exact stretch, so a language product reached by two rows is read as a branch
# Witness: facts `a[xy]c|b[xy]d`: exact/machine-inexact|-|2|[2],[2] becomes L = 1; the only witness with two rows of equal sets before L.
SAB_ID='S3221-cover_rows_by_identity'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='the walk compares ROWS, not their byte sets: a second row at a depth ends the exact stretch, so a language product reached by two rows is read as a branch'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the cloud mechrows run owed by lane covs1 (docs/dev/lanes/covs1_report.md).'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'a[xy]c|b[xy]d'"'"' '"'"'--facts'"'"' --why'
SAB_REACH_EXPECT='REACH-FACTS-EQUAL
REACH-WHY=[exact/machine-inexact]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (i == 0) memcpy(first, b32, 32);
            else if (memcmp(first, b32, 32)) w->stop = COVER_STOP_BRANCH;'
SAB_AFTER='            if (i == 0) memcpy(first, b32, 32);
            else w->stop = COVER_STOP_BRANCH;   /* SABOTAGE S3221 */'
