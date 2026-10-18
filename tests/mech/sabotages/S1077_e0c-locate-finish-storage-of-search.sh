#!/usr/bin/env bash
# S1077 ([COMPOUND] E0c, lane e0c; docs/design/compound_entries.md §4.1, §5.1 E0c; docs/dev/lanes/e0c_report.md) -- the locate-then-finish emitter reads the linkage of `<prefix>_search` for every body it writes, so the VM hybrid's embedded search is exported.
SAB_ID='S1077-e0c-locate-finish-storage-of-search'
SAB_FILE='src/gen/emit_comb.c'
SAB_SUITES='compound codegen'
SAB_DESC='the hybrid'"'"'s <prefix>_prefilter is defined without `static` (the search entry'"'"'s linkage, not its own row'"'"'s): an artifact exports an internal entry the closure keeps static'
SAB_DOC_FIGURE='OWED: the single-row mech figure at the slot (lane e0c chain, build/v/mech-S1077.log); hand validation in docs/dev/lanes/e0c_report.md.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-18 (lane e1, [ENTRY-TABLE] E1): the DFA engine body takes its ENTRY
# row (the search head reads its linkage and its part-layout mark from it), so the
# plant names the search entry's row where the body's own belongs; same defect.
SAB_BEFORE='        pcrec_emit_dfa_engine(cx, t->body, e);'
SAB_AFTER='        pcrec_emit_dfa_engine(cx, t->body, PCREC_ENTRY_SEARCH);   /* SABOTAGE S1077 */'
