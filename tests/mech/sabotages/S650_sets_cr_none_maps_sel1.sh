#!/usr/bin/env bash
# S650 ([DEC-FALLBACK] B3, lane decfbB3) -- the sets routine maps a TO_NONE collapse-reason cell to CR_SEL1: sel1-drop leaves the collapse reason set, so the drop row applies again on the next overflow and the compile never ends its ladder
# Live from B3 (the walk is the dispatch, the sets routine the writer).
# Detector: tests/codegen/run_fallback_table.sh (a) seq-sel1cd/seq-look/seq-sel1d (the witnesses run to the attempt cap and refuse).
SAB_ID='S650-sets_cr_none_maps_sel1'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="the sets routine maps a TO_NONE collapse-reason cell to CR_SEL1: sel1-drop leaves the collapse reason set, so the drop row applies again on the next overflow and the compile never ends its ladder"
SAB_DOC_FIGURE='Re-run: bash tests/mech/run_sabotage_matrix.sh S650. docs/dev/lanes/decfbB3_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case FIT_CR_TO_NONE:    return CR_NONE;'
SAB_AFTER='    case FIT_CR_TO_NONE:    return CR_SEL1;   /* SABOTAGE S650 */'
