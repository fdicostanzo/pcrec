#!/usr/bin/env bash
# S896 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-6) -- a part's search entry is compiled EXPORTED, so every compound artifact carries `<prefix>__f_search`/`__q_search` as globals the plain artifact does not.
SAB_ID='S896-cmp6-part-exported'
SAB_FILE='src/core/compound.c'
SAB_SUITES='compound'
SAB_DESC='a part'\''s search entry is compiled EXPORTED, so every compound artifact carries `<prefix>__f_search`/`__q_search` as globals the plain artifact does not'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): compound arm 73 FAIL lines (B1: `part symbols are global`, kz__f_search/kz__q_search on every witness; G4'\''s nm -g against the plain artifact). The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    const PcrecEntryReq req = { 0, part_kept(part->need) };'
SAB_AFTER='    const PcrecEntryReq req = { part_kept(part->need) & PCREC_ENTRY_BIT(PCREC_ENTRY_SEARCH), part_kept(part->need) };   /* SABOTAGE S896 */'
