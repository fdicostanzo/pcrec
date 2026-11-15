#!/usr/bin/env bash
# S1136 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- C9 is tested at depth k only (revision 2's C9), so an eol view on a row before k is admitted
# kit_proof.md §6.3 S1136 (the K1 plant): `ab|a$\n` on "a\n" from 0: PCRE2 (0,2), the plant NOMATCH.
# RE-ANCHORED 2026-11-15 (lane covs1, [COVER-CAP] stage 1, cover_cap.md §5.4 R-12/FI-3):
# C9 is checked by the walk as it passes each depth (`kn_eol_rows`), the rows at k included;
# the plant clears the mark at every depth, so only the LAST depth's rows (k) count.
SAB_ID='S1136-cover_c9_depth_k_only'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C9 is tested at depth k only (revision 2'"'"'s C9), so an eol view on a row before k is admitted'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'ab|a$\n'"'"''
SAB_REACH_EXPECT='REACH-DECLINE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (int i = 0; i < w->nrow; i++) {
        int s = w->row[i].s, e = w->d->st[s].eolvar;'
SAB_AFTER='    w->eolview = false;   /* SABOTAGE S1136 */
    for (int i = 0; i < w->nrow; i++) {
        int s = w->row[i].s, e = w->d->st[s].eolvar;'
