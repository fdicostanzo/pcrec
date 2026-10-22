# S1375 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: the element renders an unset `${!name}` empty under --unset=error.
# Witness: every --unset=error `${!name}` cell's `vuerr` arm wants PCREC_ERR_UNSET_VAR; reach token `vuerr`.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1375-element-unset-var-empty"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the element renders an unset `${!name}` empty under --unset=error'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1375.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            pcrec_sb_printf(c, "        if (!ctx->vars[%d].p) return PCREC_ERR_UNSET_VAR;\n", it->ref);'
SAB_AFTER='            pcrec_sb_printf(c, "        if (0 && !ctx->vars[%d].p) return PCREC_ERR_UNSET_VAR;\n", it->ref);   /* SABOTAGE S1375 */'
