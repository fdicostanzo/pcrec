# S3020 ([CLI-OUTKEEP]) -- write_file stops treating "the existing file already holds these bytes" as done, so every identical rerun rewrites (and re-stamps) the output.
# Detector (arm cli): tests/cli/run_cli_tests.sh's "outkeep: an identical rerun ... untouched" cases.
SAB_ID="S3020-cli-outkeep-compare-dropped"
SAB_FILE="cli/main.c"
SAB_SUITES="cli"
SAB_DESC="write_file stops treating 'the existing file already holds these bytes' as done, so every identical rerun rewrites (and re-stamps) the output"
SAB_DOC_FIGURE="cli: the run_cli_tests.sh outkeep identical-rerun cells read red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S3020."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (same) return 0;'
SAB_AFTER='        if (same && !same) return 0;   /* SABOTAGE S3020 */'
