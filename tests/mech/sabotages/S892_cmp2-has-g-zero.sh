#!/usr/bin/env bash
# S892 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-2) -- the controller asks F only at offset 0 on a \G pattern (floor_any emitted false), so a \G floor match at a startpos > 0 is lost.
SAB_ID='S892-cmp2-has-g-zero'
SAB_FILE='src/core/compound.c'
SAB_SUITES='compound harness'
SAB_HARNESS_TARGET='tests/compound/split.rxt'
SAB_DESC='the controller asks F only at offset 0 on a \G pattern (floor_any emitted false), so a \G floor match at a startpos > 0 is lost'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): @@FIG892@@. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        sh->floor_any = w.rep[SPLIT_Q].has_g;'
SAB_AFTER='        sh->floor_any = false;   /* SABOTAGE S892 */'
