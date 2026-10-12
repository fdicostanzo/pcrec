#!/usr/bin/env bash
# S760 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- the `match_end_position < search_from` seed guard deleted: a seed below the startpos walks.
# Detector: the answer net's startpos cells (`\s*$` from 3 on "ab\n", `b\z` from 2): a start below the startpos is reported.
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# the seed guard is now F1's (`match_end_position >= search_from`), one guard
# for the one seed; detector: `a*$` from 3 on "aa\n" (the seed n-1 = 2 is below
# the startpos), in tests/endmark/b3_rows.rxt. Reach: `a*$` takes one-seed.
SAB_ID='S760-revend-seed-guard-deleted'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='endmark'
SAB_DESC='the `match_end_position < search_from` seed guard deleted: a seed below the startpos walks'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S760.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "a*$" | grep -F "form=one-seed" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='               "    if (match_end_position >= search_from) do {\n"
               "        size_t rewind_position = match_end_position;\n",
               rev->p, celln, revend_byte_literal(cx, nl), cellnl);'
SAB_AFTER='               "    if (1) do {   /* SABOTAGE S760 */\n"
               "        size_t rewind_position = match_end_position;\n",
               rev->p, celln, revend_byte_literal(cx, nl), cellnl);'
