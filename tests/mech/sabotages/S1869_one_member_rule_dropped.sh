# S1869 ([XARCH-DEV] P1, lane p1cpu) -- the one-member rule is dropped: a list of two targets (of one family or two) is accepted and the first wins.
# Detector (arm cli): tests/cli/run_cli_tests.sh's "cpu targets" cases.
SAB_ID="S1869-one-member-rule-dropped"
SAB_FILE="src/gen/memfn_targets.c"
SAB_SUITES="cli"
SAB_DESC="the one-member rule is dropped: a list of two targets (of one family or two) is accepted and the first wins"
SAB_DOC_FIGURE="cli: the run_cli_tests.sh cpu-targets cell for this row reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1869."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (s->other) {'
SAB_AFTER='    if (0 && s->other) {   /* SABOTAGE S1869 */'
