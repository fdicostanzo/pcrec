# S1361 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: `$$` is copied as two dollars.
# Witness: the `dollar` cell (`x\ny$$$1`): one `$` expected.
# Reach (K35): token - (cell dollar); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1361-dollar-dollar-two"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='`$$` is copied as two dollars'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1361.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            st_lit(t, i + 1, 1);'
SAB_AFTER='            st_lit(t, i, 2);   /* SABOTAGE S1361 */'
