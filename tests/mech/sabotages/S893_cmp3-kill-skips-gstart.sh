#!/usr/bin/env bash
# S893 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-3) -- the split derivation leaves \G alive in Q (the kill skips A_GSTART), so Q matches at its own search start where P's \G is false.
# `\Gab|cd` (G+F) is UNREACHED until B5; the first build's witness is `\G\n|b$` (G+E).
SAB_ID='S893-cmp3-kill-skips-gstart'
SAB_FILE='src/opt/derive.c'
SAB_SUITES='compound harness'
SAB_HARNESS_TARGET='tests/compound/split.rxt'
SAB_DESC='the split derivation leaves \G alive in Q (the kill skips A_GSTART), so Q matches at its own search start where P'\''s \G is false'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): @@FIG893@@. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        q->killed_g++;
        return (QRes){ never_node(cx), true, false };'
SAB_AFTER='        return (QRes){ a, false, false };   /* SABOTAGE S893 */'
