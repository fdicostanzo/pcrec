# S1362 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: `${!name}` is read as the group `name`.
# Witness: the `var` cells (`${!v}-$1` on `(a)`): the setup MISSING_REF where X-a is expected.
# Reach (K35): token vars (cell var); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1362-var-is-group"
SAB_FILE="src/parse/subst_template.c"
SAB_SUITES="subst"
SAB_DESC='`${!name}` is read as the group `name`'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1362.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            var = x->explicit_var;'
SAB_AFTER='            var = false;   /* SABOTAGE S1362 */'
