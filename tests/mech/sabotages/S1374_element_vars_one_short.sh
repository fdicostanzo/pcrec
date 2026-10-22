# S1374 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: the element takes a ctx with one variable too few.
# Witness: every `${!name}` cell's `vmis` arm (nvars one short) wants MISMATCH; reach token `vmis`.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1374-element-vars-one-short"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the element takes a ctx with one variable too few'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1374.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_printf(c, "\n        || !ctx->vars || ctx->nvars < %d", t->nvrefs);'
SAB_AFTER='        pcrec_sb_printf(c, "\n        || !ctx->vars || ctx->nvars < %d - 1", t->nvrefs);   /* SABOTAGE S1374 */'
