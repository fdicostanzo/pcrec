#!/usr/bin/env bash
# S594 ([START-TABLE] C2, lane stc2; docs/design/start_table.md §3.3 item 6, docs/dev/lanes/stc2_report.md) -- a planted predicate difference in one cand_rows[] row: N9 memchr reads the memchr-bounded predicate, so the table no longer chooses the row dfa_pfs[] chooses.
# Detector (arm candoracle): tests/codegen/run_cand_oracle.sh, the both-walks
# oracle over named witnesses. cand_rows[] has no reader in a default build
# until C3, so no artifact byte and no answer moves: the corpus arm is not
# named, by design.
SAB_ID='S594-cand_row_predicate_differs'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='a planted predicate difference in one cand_rows[] row: N9 memchr reads the memchr-bounded predicate, so the table no longer chooses the row dfa_pfs[] chooses'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S594.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .c = { "memchr", 0, pf_memchr_applies },'
SAB_AFTER='    { .c = { "memchr", 0, pf_memchr_bounded_applies },   /* SABOTAGE S594 */'
