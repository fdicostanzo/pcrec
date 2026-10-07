#!/usr/bin/env bash
# S598 ([START-TABLE] C2, lane stc2; docs/design/start_table.md §3.3 item 6, docs/dev/lanes/stc2_report.md) -- a slot loses its total fallback: the last RETRY row, fixed, becomes deniable, so under -fno-hyb-reseed the walk can return NULL; the table self-check (totality per asked slot and route) fires.
# Detector (arm candoracle): tests/codegen/run_cand_oracle.sh, the both-walks
# oracle over named witnesses. cand_rows[] has no reader in a default build
# until C3, so no artifact byte and no answer moves: the corpus arm is not
# named, by design.
SAB_ID='S598-cand_slot_not_total'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='a slot loses its total fallback: the last RETRY row, fixed, becomes deniable, so under -fno-hyb-reseed the walk can return NULL; the table self-check (totality per asked slot and route) fires'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S598.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .c = { "fixed", 0, cand_always }, .slot = CAND_SLOT_RETRY,'
SAB_AFTER='    { .c = { "fixed", PCREC_NO_HYB_RESEED, cand_always }, .slot = CAND_SLOT_RETRY,   /* SABOTAGE S598 */'
