#!/usr/bin/env bash
# S745 ([OPT-REVEND] L0, lane lfl0; docs/design/locate_finish.md rev 2.1 §5 L0; docs/dev/lanes/lfl0_report.md) -- a `.needs` declaration dropped: RECOVER's `reverse-pass` no longer declares the reverse machine, so the path's members lose R and the membership folds skip a machine the artifact carries.
# Detector: test-codegen. MEASURED by plant at landing: run_dfa_uniform_fold.sh (250 corpus disagreements), run_premul_table.sh (2), run_search_pinned.sh (480 sweep failures) and run_form_census.sh (the `mixed` witness) all fail. The census's C5-L0 (studies/locate_finish/analyze.py) reads 3,656 disagreements.
SAB_ID='S745-needs-cell-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='codegen'
SAB_DESC='reverse-pass loses its needs (R): the member folds skip the reverse machine, RX_DFA_TABLE/RX_DFA_UNIFORM_FOLDS read without it'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/lfl0_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S745.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .needs = { [CAND_ROUTE_DFA] = { CAND_MR } },
      .u.recover = { .pinned = false } },'
SAB_AFTER='      /* SABOTAGE S745: the reverse machine'\''s needs dropped */
      .u.recover = { .pinned = false } },'
