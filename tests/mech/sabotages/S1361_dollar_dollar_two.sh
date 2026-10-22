# S1361 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: `$$` is copied as two dollars.
# Witness: the `dollar` cell (`x\ny$$$1`): one `$` expected.
SAB_ID="S1361-dollar-dollar-two"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='`$$` is copied as two dollars'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1361.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            st_lit(t, s + i + 1, 1);'
SAB_AFTER='            st_lit(t, s + i, 2);   /* SABOTAGE S1361 */'
