#!/usr/bin/env bash
# S1136 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- C9 is tested at depth k only (revision 2's C9), so an eol view on a row before k is admitted
# kit_proof.md §6.3 S1136 (the K1 plant): `ab|a$\n` on "a\n" from 0: PCRE2 (0,2), the plant NOMATCH.
SAB_ID='S1136-cover_c9_depth_k_only'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C9 is tested at depth k only (revision 2'"'"'s C9), so an eol view on a row before k is admitted'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'ab|a$\n'"'"''
SAB_REACH_EXPECT='REACH-DECLINE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (int j = 0; j <= st->w.k; j++)
        for (int i = 0; i < st->w.nlv[j]; i++) {
            int e = st->d->st[st->w.lv[j][i].s].eolvar;'
SAB_AFTER='    for (int j = st->w.k; j <= st->w.k; j++)   /* SABOTAGE S1136 */
        for (int i = 0; i < st->w.nlv[j]; i++) {
            int e = st->d->st[st->w.lv[j][i].s].eolvar;'
