# S1865 ([XARCH-DEV] P1, lane p1cpu) -- the SIMD-on-no-list row answers the portable target: -fmemfn-simd alone renders the SIMD-off artifact.
# Detector (arm cli): tests/cli/run_cli_tests.sh's "cpu targets" cases.
SAB_ID="S1865-host-row-portable"
SAB_FILE="src/gen/memfn_targets.c"
SAB_SUITES="cli"
SAB_DESC="the SIMD-on-no-list row answers the portable target: -fmemfn-simd alone renders the SIMD-off artifact"
SAB_DOC_FIGURE="cli: the run_cli_tests.sh cpu-targets cell for this row reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1865."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { 1,  0, ACT_HOST },      /* SIMD on, no list: the host family'"'"'s default list */'
SAB_AFTER='    { 1,  0, ACT_PORTABLE },  /* SABOTAGE S1865 */'
