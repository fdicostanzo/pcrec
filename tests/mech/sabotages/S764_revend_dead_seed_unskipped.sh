#!/usr/bin/env bash
# S764 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- the walk's dead-seed skip deleted (X1): a speculative seed whose state is dead reads `view[row(dead)]`.
# Detector: run_rev_end.sh §4: the X witnesses under -fsanitize=address,undefined (`\d+$(?=\n)` on "12": the seed at n is the dead state).
SAB_ID='S764-revend-dead-seed-unskipped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend'
SAB_DESC='the walk'\''s dead-seed skip deleted (X1): a speculative seed whose state is dead reads `view[row(dead)]`'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S764.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\d+$(?=\\n)" && grep -q "if (rx_reverse_is_dead(reverse_state)) continue;" "$REACH_TMP/o.c" && echo REACH-DEADSKIP'
SAB_REACH_EXPECT='REACH-DEADSKIP'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    emit_reverse_block(c, &rev, "revend", "continue;");'
SAB_AFTER='    emit_reverse_block(c, &rev, "revend", NULL);   /* SABOTAGE S764 */'
