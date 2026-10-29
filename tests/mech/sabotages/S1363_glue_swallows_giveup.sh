# S1363 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: replace-all ignores the iterator's code when the find-all ends early.
# Witness: the `giveup` cell (`--step-budget=100`): replace-all returns STEPS.
# Reach (K35): token giveup (cell giveup); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1363-glue-swallows-giveup"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='replace-all ignores the iterator'\''s code when the find-all ends early'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1363.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (it->rc < 0) return it->rc;\n"'
SAB_AFTER='"    (void)0;   /* SABOTAGE S1363 */\n"'
