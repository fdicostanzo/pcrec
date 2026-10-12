#!/usr/bin/env bash
# S910 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 the stamp classification (match_api.md §6.3.12)) -- the stamp catalogue classifies RX_DFA_SCAN as a pattern-level stamp, so a compound artifact stamps a scan shape its text does not have.
SAB_ID='S910-stamp-machine-as-pattern'
SAB_FILE='src/gen/stamp_kinds.c'
SAB_SUITES='codegen'
SAB_DESC='the stamp catalogue classifies RX_DFA_SCAN as a pattern-level stamp, so a compound artifact stamps a scan shape its text does not have'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): @@FIG910@@. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "DFA_SCAN",           false, SK_MACHINE_STR },'
SAB_AFTER='    { "DFA_SCAN",           false, SK_PATTERN },   /* SABOTAGE S910 */'
