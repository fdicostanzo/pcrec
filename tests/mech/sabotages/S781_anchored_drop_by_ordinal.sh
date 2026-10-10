#!/usr/bin/env bash
# S781 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (LR-S12); docs/dev/lanes/revbuild_report.md) -- the anchored machine dropped by the ladder's ORDINAL rather than by its row having fired: the premul rung drops the machine the skipped anchored rung kept.
# Detector: run_rev_end.sh §3: the tie witness under the derived cap takes the premul rung without its anchored machine, grows past the cap and refuses.
SAB_ID='S781-anchored-drop-by-ordinal'
SAB_FILE='src/core/compile.c'
SAB_SUITES='revend'
SAB_DESC='the anchored machine dropped by the ladder'\''s ORDINAL rather than by its row having fired: the premul rung drops the machine the skipped anchored rung kept'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S781.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (cx->anchored_dropped) return;
'
SAB_AFTER='    if (cx->size_drop_rung >= SDR_NO_ANCHORED) return;   /* SABOTAGE S781: the ordinal again */
'
