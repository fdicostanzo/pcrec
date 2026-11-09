# S1867 ([XARCH-DEV] P1, lane p1cpu) -- the CLI stops checking the list at option parse: a bad token is refused only when a compile reaches it, so a query mode answers beside it.
# Detector (arm cli): tests/cli/run_cli_tests.sh's "cpu targets" cases.
SAB_ID="S1867-cli-parse-check-dropped"
SAB_FILE="cli/main.c"
SAB_SUITES="cli"
SAB_DESC="the CLI stops checking the list at option parse: a bad token is refused only when a compile reaches it, so a query mode answers beside it"
SAB_DOC_FIGURE="cli: the run_cli_tests.sh cpu-targets cell for this row reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1867."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (pcrec_memfn_simd_check(opt.flags, opt.memfn_simd, terr,
                                       sizeof terr) != 0)
                return cli_err("%s", terr);'
SAB_AFTER='            (void)terr;   /* SABOTAGE S1867 */'
