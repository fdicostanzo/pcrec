#!/usr/bin/env bash
# S1075 ([COMPOUND] E0c, lane e0c; docs/design/compound_entries.md §4.1, §5.1 E0c; docs/dev/lanes/e0c_report.md) -- the finish-at emitter writes the search-and-filter pair where the FINISH row says verify-at (axis G's `unwrapped`).
SAB_ID='S1075-e0c-finish-verify-as-filter'
SAB_FILE='src/gen/emit_comb.c'
SAB_SUITES='anchoredmatch'
SAB_DESC='an unwrapped artifact stamps RX_DFA_MATCH "unwrapped" but its <prefix>_match wraps <prefix>_search and carries no anchored machine: the answers are the same and the stamp no longer names the body (spec §6.3)'
SAB_DOC_FIGURE='HAND-MEASURED by lane e0c 2026-10-16 (plant applied to a git-archive HEAD tree, run_anchored_match.sh): anchoredmatch 25fail/12pass -- every unwrapped witness stamps unwrapped with no anchored machine. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    switch (f->form) {'
SAB_AFTER='    switch (f->form == PCREC_FIN_VERIFY ? PCREC_FIN_FILTER : f->form) {   /* SABOTAGE S1075 */'
