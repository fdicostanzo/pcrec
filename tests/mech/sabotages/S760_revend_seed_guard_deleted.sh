#!/usr/bin/env bash
# S760 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- the `match_end_position < search_from` seed guard deleted: a seed below the startpos walks.
# Detector: the answer net's startpos cells (`\s*$` from 3 on "ab\n", `b\z` from 2): a start below the startpos is reported.
SAB_ID='S760-revend-seed-guard-deleted'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='the `match_end_position < search_from` seed guard deleted: a seed below the startpos walks'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S760.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\s+$" && grep -q "for (int revend_seed = 0;" "$REACH_TMP/o.c" && echo REACH-WALK'
SAB_REACH_EXPECT='REACH-WALK'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_puts(c, "        if (match_end_position < search_from) break;\n"'
SAB_AFTER='    pcrec_sb_puts(c, "        (void)0;   /* SABOTAGE S760 */\n"'
