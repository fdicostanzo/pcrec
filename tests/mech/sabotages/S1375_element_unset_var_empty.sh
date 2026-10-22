# S1375 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: the element renders an unset `${!name}` empty under RX_SUBST_STRICT.
# Witness: every strict `${!name}` cell's `vuerr` arm (a hand-built ctx, every variable unset) wants PCREC_ERR_UNSET_VAR.
# Reach (K35): token vuerr; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1375-element-unset-var-empty"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the element renders an unset `${!name}` empty under RX_SUBST_STRICT'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1375.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"            if (!ctx->vars[j].p) return PCREC_ERR_UNSET_VAR;\n", t->nvrefs);'
SAB_AFTER='"            if (0 && !ctx->vars[j].p) return PCREC_ERR_UNSET_VAR;\n", t->nvrefs);   /* SABOTAGE S1375 */'
