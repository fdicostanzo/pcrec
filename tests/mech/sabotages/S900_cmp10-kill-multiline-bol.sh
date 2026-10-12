#!/usr/bin/env bash
# S900 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-10) -- the split derivation also kills `(?m)^`, so Q loses every line-start match after the floor.
SAB_ID='S900-cmp10-kill-multiline-bol'
SAB_FILE='src/opt/derive.c'
SAB_SUITES='compound harness'
SAB_HARNESS_TARGET='tests/compound/split.rxt'
SAB_DESC='the split derivation also kills `(?m)^`, so Q loses every line-start match after the floor'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): compound arm 26 FAIL lines (B2: `never disagrees` on the (?m) cells, Q'\''s language moves), harness on split.rxt 33 of 13,839 cases. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (lb || a->u.anch.multiline) return (QRes){ a, false, false };'
SAB_AFTER='        if (lb) return (QRes){ a, false, false };   /* SABOTAGE S900 */'
