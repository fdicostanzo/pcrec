#!/usr/bin/env bash
# S771 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- the row's deny unplumbed: `-fno-rev-end` is inert (the listing still shows the bit).
# Detector: run_rev_end.sh: the walk survives `-fno-rev-end` on every walking artifact, and the deny witness reads `rev-end`.
SAB_ID='S771-revend-deny-unplumbed'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend'
SAB_DESC='the row'\''s deny unplumbed: `-fno-rev-end` is inert (the listing still shows the bit)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S771.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\s+$" && grep -q "for (int revend_seed = 0;" "$REACH_TMP/o.c" && echo REACH-WALK'
SAB_REACH_EXPECT='REACH-WALK'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .c = { "rev-end", PCREC_NO_REV_END, locate_rev_end_applies }, .slot = CAND_SLOT_LOCATE,'
SAB_AFTER='    { .c = { "rev-end", 0, locate_rev_end_applies }, .slot = CAND_SLOT_LOCATE,   /* SABOTAGE S771 */'
