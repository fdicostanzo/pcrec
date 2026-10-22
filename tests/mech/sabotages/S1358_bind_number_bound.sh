# S1358 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst.md).
#
# Plant: a numbered reference binds up to ngroups + 1 whatever ncaps delivers.
# Witness: the `nosuchnum` cell (`$1$2` on `(a)`): bind MISSING_REF row 1 expected.
# Reach (K35): token - (cell nosuchnum); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1358-bind-number-bound"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='a numbered reference binds up to ngroups + 1 whatever ncaps delivers'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1358.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"            if (e->number != 0 && (e->number > rx->ngroups || e->number >= rx->ncaps))\n"'
SAB_AFTER='"            if (e->number != 0 && (e->number > rx->ngroups + 1))   /* SABOTAGE S1358 */\n"'
