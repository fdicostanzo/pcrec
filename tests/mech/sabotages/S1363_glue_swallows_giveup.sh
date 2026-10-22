# S1363 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: the glue ignores the iterator's code when it ends early.
# Witness: the `giveup` cell (`--step-budget=100`): rc STEPS expected.
# Reach (K35): token giveup (cell giveup); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1363-glue-swallows-giveup"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the glue ignores the iterator'\''s code when it ends early'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1363.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"            if (it->rc < 0) return it->rc;\n"'
SAB_AFTER='"            (void)0;   /* SABOTAGE S1363 */\n"'
