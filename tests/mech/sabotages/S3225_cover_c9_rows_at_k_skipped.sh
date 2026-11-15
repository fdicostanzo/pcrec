#!/usr/bin/env bash
# S3225 ([COVER-CAP] stage 1, lane covs1; docs/design/cover_cap.md §5.4 plant FI-3) -- C9 skips the rows at k: the eol-view check runs only on depths the walk passes without stopping, so a non-identity eol view on the row at k is admitted
# Witness: verdict `a(?:b|c)(?:$|q(?<=x))` (decline no-eol-view) becomes a cover that misses PCRE2's (0,2) on ab\n.
# Shared (review r9 covs1 CHECKS-3, cross-plant matrix): its witness is flipped by S1139 too, and this plant also flips S1139's `cat$` under -fno-rev-end (the eol view sits at depth k = 3; 9cat\n: pcrec none, PCRE2 (1,4)).
SAB_ID='S3225-cover_c9_rows_at_k_skipped'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C9 skips the rows at k: the eol-view check runs only on depths the walk passes without stopping, so a non-identity eol view on the row at k is admitted'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the cloud mechrows run owed by lane covs1 (docs/dev/lanes/covs1_report.md).'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'a(?:b|c)(?:$|q(?<=x))'"'"' --why'
SAB_REACH_EXPECT='REACH-DECLINE
REACH-WHY=[no-eol-view]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kn_eol_rows(w);                      /* C9, the rows at k included */
        if (viewed) { w->stop = COVER_STOP_VIEW; break; }   /* VIEW wins: k */
        if (w->nrow == 0) { w->stop = COVER_STOP_EMPTY; break; }
        if (kn_rows_accept(w)) { w->stop = COVER_STOP_ACCEPT; break; }'
SAB_AFTER='        if (viewed) { w->stop = COVER_STOP_VIEW; break; }   /* VIEW wins: k */
        if (w->nrow == 0) { w->stop = COVER_STOP_EMPTY; break; }
        if (kn_rows_accept(w)) { w->stop = COVER_STOP_ACCEPT; break; }
        kn_eol_rows(w);   /* SABOTAGE S3225 */'
