# S1538 -- [M4-SUBST] module subst-extended (lane substext; docs/spec/subst_api.md
# §2¶7-¶14a, §4¶7-¶8, §4¶14, §4¶22).
#
# Plant: the check accepts the no-map form on a composed rx.
# Witness: the `composed` cell of tests/subst/cells.tsv (`[$0]` on a composed rx, tests/subst/composed.rxt): the check with no map must be MISMATCH (subst_api.md §3¶3); sabotaged it is 0.
# Reach (K35): token S1538; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1538-composed-nomap-accepted"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the check accepts the no-map form on a composed rx'
SAB_DOC_FIGURE='Owed: lane substext queued this row (docs/dev/lanes/substext_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1538.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        || (!map && rx->ncaps > rx->ngroups + 1)\n"'
SAB_AFTER='"        || 0   /* SABOTAGE S1538 */\n"'
