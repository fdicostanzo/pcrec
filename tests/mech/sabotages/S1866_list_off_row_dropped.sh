# S1866 ([XARCH-DEV] P1, lane p1cpu) -- the list-while-SIMD-off row answers the portable target: a list beside the deny bit is silently ignored (the silent-deny row the ruling removed).
# Detector (arm cli): tests/cli/run_cli_tests.sh's "cpu targets" cases.
SAB_ID="S1866-list-off-row-dropped"
SAB_FILE="src/gen/memfn_targets.c"
SAB_SUITES="cli"
SAB_DESC="the list-while-SIMD-off row answers the portable target: a list beside the deny bit is silently ignored (the silent-deny row the ruling removed)"
SAB_DOC_FIGURE="cli: the run_cli_tests.sh cpu-targets cell for this row reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1866."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { 0,  1, ACT_LIST_OFF },  /* a list while SIMD is off: refused, never ignored */'
SAB_AFTER='    { 0,  1, ACT_PORTABLE },  /* SABOTAGE S1866 */'
