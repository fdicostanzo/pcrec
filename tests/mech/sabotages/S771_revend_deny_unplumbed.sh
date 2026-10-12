#!/usr/bin/env bash
# S771 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- the row's deny unplumbed: `-fno-rev-end` is inert (the listing still shows the bit).
# Detector: run_rev_end.sh: the walk survives `-fno-rev-end` on every walking artifact, and the deny witness reads `rev-end`.
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# reach reads any form row (`\s+$`: tagged).
SAB_ID='S771-revend-deny-unplumbed'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend'
SAB_DESC='the row'\''s deny unplumbed: `-fno-rev-end` is inert (the listing still shows the bit)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S771.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\s+$" | grep -F "form=tagged" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .c = { "rev-end", PCREC_NO_REV_END, locate_rev_end_applies }, .slot = CAND_SLOT_LOCATE,'
SAB_AFTER='    { .c = { "rev-end", 0, locate_rev_end_applies }, .slot = CAND_SLOT_LOCATE,   /* SABOTAGE S771 */'
