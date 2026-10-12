#!/usr/bin/env bash
# S908 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-18) -- the call-site table emits its give-up row under a DFA part, a row for a code the callee cannot return.
SAB_ID='S908-cmp18-giveup-row-on-dfa-part'
SAB_FILE='src/gen/emit_compound.c'
SAB_SUITES='compound'
SAB_DESC='the call-site table emits its give-up row under a DFA part, a row for a code the callee cannot return'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): @@FIG908@@. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "give-up",   CS_PROPAGATE, cs_vm,      "r >= PCREC_ERR_FLOOR && r <= -2" },'
SAB_AFTER='    { "give-up",   CS_PROPAGATE, cs_always,  "r >= PCREC_ERR_FLOOR && r <= -2" },   /* SABOTAGE S908 */'
