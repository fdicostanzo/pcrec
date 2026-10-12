#!/usr/bin/env bash
# S905 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-15) -- the lever stamps `"none"` on the plain artifact it forced, so a forced-off artifact reads as one the default build ships plain.
SAB_ID='S905-cmp15-lever-stamps-none'
SAB_FILE='src/core/compile.c'
SAB_SUITES='compound'
SAB_DESC='the lever stamps `"none"` on the plain artifact it forced, so a forced-off artifact reads as one the default build ships plain'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): @@FIG905@@. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        cx.comp_stamp = comp_state == COMP_FORCED ? "forced-off" : NULL;'
SAB_AFTER='        cx.comp_stamp = NULL;   /* SABOTAGE S905 */'
