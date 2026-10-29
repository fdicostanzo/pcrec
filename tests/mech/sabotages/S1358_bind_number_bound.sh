# S1358 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: with no map, the check passes a numbered reference up to ngroups + 1 whatever ncaps delivers.
# Witness: the `nosuchnum` cell (`$1$2` on `(a)`): the nmchk arm (the check with no map) wants MISSING_REF row 1.
# Reach (K35): token nmchk; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1358-bind-number-bound"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='with no map, a numbered reference passes up to ngroups + 1 whatever ncaps delivers'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1358.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"            ok = !e->name && e->number >= 0 && e->number < rx->ncaps;\n"'
SAB_AFTER='"            ok = !e->name && e->number >= 0 && e->number <= rx->ngroups + 1;   /* SABOTAGE S1358 */\n"'
