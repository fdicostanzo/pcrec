#!/usr/bin/env bash
# S597 ([START-TABLE] C2, lane stc2; docs/design/start_table.md §3.3 item 6, docs/dev/lanes/stc2_report.md) -- an inline decision restated wrongly as a row predicate: B3 vm-anchored tests the GSTART value of the start_anchor fact, so a ^-anchored VM artifact selects all where the VM entry emits attempt_max.
# Detector (arm candoracle): tests/codegen/run_cand_oracle.sh, the both-walks
# oracle over named witnesses. cand_rows[] has no reader in a default build
# until C3, so no artifact byte and no answer moves: the corpus arm is not
# named, by design.
SAB_ID='S597-cand_inline_predicate_flipped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='an inline decision restated wrongly as a row predicate: B3 vm-anchored tests the GSTART value of the start_anchor fact, so a ^-anchored VM artifact selects all where the VM entry emits attempt_max'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S597.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='{ return pcrec_fact_start_anchor(s->cx) == PCREC_SANCH_BOT; }'
SAB_AFTER='{ return pcrec_fact_start_anchor(s->cx) == PCREC_SANCH_GSTART; }   /* SABOTAGE S597 */'
