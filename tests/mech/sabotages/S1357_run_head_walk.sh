# S1357 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: pcrec_subst_group_run does not walk back to the run's head after the bsearch.
# Witness: the `duprun3` cell (three `n` rows, bsearch lands on the middle): <c><b><a> expected.
# Reach (K35): token S1348 (cell duprun3); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1357-run-head-walk"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='pcrec_subst_group_run does not walk back to the run'\''s head after the bsearch'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1357.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    while (at > 0 && !strcmp(g[at - 1].name, name)) at--;\n"'
SAB_AFTER='"    /* SABOTAGE S1357 */\n"'
