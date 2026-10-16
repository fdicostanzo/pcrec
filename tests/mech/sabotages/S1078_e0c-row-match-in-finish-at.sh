#!/usr/bin/env bash
# S1078 ([COMPOUND] E0c, lane e0c; docs/design/compound_entries.md §4.1, §5.1 E0c; docs/dev/lanes/e0c_report.md) -- entry_rows[] names `finish-at` as the DFA `<prefix>_match_in`'s combinator.
SAB_ID='S1078-e0c-row-match-in-finish-at'
SAB_FILE='src/gen/entries.c'
SAB_SUITES='codegen compound'
SAB_DESC='the table'"'"'s combinator column is the live selector: with the DFA _match_in row naming finish-at, pcrec_emit_entry calls the finish-at emitter, which the DFA'"'"'s forward text cannot feed, so every DFA artifact refuses as an internal error'
SAB_DOC_FIGURE='OWED: the single-row mech figure at the slot (lane e0c chain, build/v/mech-S1078.log); hand validation in docs/dev/lanes/e0c_report.md.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { PCREC_ENTRY_MATCH_IN,     sh_dfa,        PCREC_COMB_FORWARD,       PARTS(pr_to_match),      EM_ONESHOT },'
SAB_AFTER='    { PCREC_ENTRY_MATCH_IN,     sh_dfa,        PCREC_COMB_FINISH_AT,     PARTS(pr_to_match),      EM_ONESHOT },   /* SABOTAGE S1078 */'
