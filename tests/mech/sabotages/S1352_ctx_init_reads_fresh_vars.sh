# S1352 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: rx_subst_ctx_init reads it->vars on a FRESH iterator with no rx_iter_vars (F-R3-1).
# Witness: the `varunset` cell's dirty arm (`${!v}-$1`, no variables, every rx_iter field 0xA5): a wild pointer read.
# Reach (K35): token S1352 (cell varunset); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1352-ctx-init-reads-fresh-vars"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='rx_subst_ctx_init reads it->vars on a FRESH iterator with no rx_iter_vars (F-R3-1)'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1352.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (it->hdr == PCREC_ITER_BOUND\n"'
SAB_AFTER='"    if (1 || it->hdr == PCREC_ITER_BOUND   /* SABOTAGE S1352 */\n"'
