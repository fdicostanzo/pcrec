#!/usr/bin/env bash
# S780 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L3 (stage 2; LR-S3/LR-S4); docs/dev/lanes/revbuild_report.md) -- X1 on a HYBRID: the inlined walk's dead-seed skip deleted.
# Detector: run_rev_end.sh §4's hybrid witnesses under the sanitizer (`(\d+)$(?=\n)`, `(\d)$(?!\n)`) and the window twin's trailing-lookaround hybrids.
SAB_ID='S780-hybrid-dead-seed-unskipped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend revtwin'
SAB_DESC='X1 on a HYBRID: the inlined walk'\''s dead-seed skip deleted'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S780.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(\\d+)\$(?=\\n)" && grep -q "if (rx_reverse_is_dead(reverse_state)) continue;" "$REACH_TMP/o.c" && echo REACH-HYB-DEADSKIP'
SAB_REACH_EXPECT='REACH-HYB-DEADSKIP'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    emit_reverse_block(c, &rev, "revend", "continue;");'
SAB_AFTER='    emit_reverse_block(c, &rev, "revend", entry ? "continue;" : NULL);   /* SABOTAGE S780 */'
