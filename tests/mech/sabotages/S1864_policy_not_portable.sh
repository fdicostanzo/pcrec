# S1864 ([XARCH-DEV] P1, lane p1cpu) -- the policy bit stops being read off the set: a list that is the portable target alone no longer sets MF_P_PORTABLE_ONLY, so SIMD stays on.
# Detector (arm cli): tests/cli/run_cli_tests.sh's "cpu targets" cases.
SAB_ID="S1864-policy-not-portable"
SAB_FILE="src/gen/memfn_targets.c"
SAB_SUITES="cli"
SAB_DESC="the policy bit stops being read off the set: a list that is the portable target alone no longer sets MF_P_PORTABLE_ONLY, so SIMD stays on"
SAB_DOC_FIGURE="cli: the run_cli_tests.sh cpu-targets cell for this row reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1864."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return s.first == mf_portable_target() ? MF_P_PORTABLE_ONLY : 0u;'
SAB_AFTER='    return 0u;   /* SABOTAGE S1864 */'
