#!/usr/bin/env bash
# S894 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-4) -- the CC_POST conjunct A5 always fails, so no pattern ships a compound: every answer stays right and the gain is gone.
SAB_ID='S894-cmp4-a5-false'
SAB_FILE='src/core/compound.c'
SAB_SUITES='compound'
SAB_DESC='the CC_POST conjunct A5 always fails, so no pattern ships a compound: every answer stays right and the gain is gone'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): compound arm 79 FAIL lines (the decline controls read A5 for concat-sqli'\''s shape, the trim and the floor-only form; the admitted manifest'\''s 97 rows are gone; G3'\''s cells stamp "none"). The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return w->rep[SPLIT_Q].never || !strcmp(w->facts[SPLIT_Q].locate, "rev-end");'
SAB_AFTER='    (void)w; return false;   /* SABOTAGE S894 */'
