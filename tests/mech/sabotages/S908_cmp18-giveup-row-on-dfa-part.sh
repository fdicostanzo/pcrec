#!/usr/bin/env bash
# S908 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-18) -- the call-site table emits its give-up row under a DFA part, a row for a code the callee cannot return.
# RE-ANCHORED 2026-10-26 (lane ic1bfix, [INLINE-C] stage 1b): the call-site
# table moved to src/gen/callsite_rows.c (one table, a `conv` column) and the
# give-up row's action is CS_GIVEUP (propagate + the callee-gave-up bit on a
# callout site; a part's edges keep plain propagation). Same plant: the row's
# applicability widened to cs_always, so a DFA part gains a row for a code it
# cannot return. S1650 plants the same line differently (its action).
SAB_ID='S908-cmp18-giveup-row-on-dfa-part'
SAB_FILE='src/gen/callsite_rows.c'
SAB_SUITES='compound'
SAB_DESC='the call-site table emits its give-up row under a DFA part, a row for a code the callee cannot return'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): compound arm 1 FAIL line (run_shell_checks.sh (1): 4 rows a DFA guards-off callee cannot return, one under each of the 4 part calls). The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "give-up",   CS_GIVEUP,    cs_vm,       "r >= PCREC_ERR_FLOOR && r <= -2", false },'
SAB_AFTER='    { "give-up",   CS_GIVEUP,    cs_always,   "r >= PCREC_ERR_FLOOR && r <= -2", false },   /* SABOTAGE S908 */'
