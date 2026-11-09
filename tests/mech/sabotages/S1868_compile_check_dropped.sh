# S1868 ([XARCH-DEV] P1, lane p1cpu) -- pcrec_compile stops checking the list: the library door accepts a bad token or a list beside SIMD off.
# Detector (arm cli): tests/cli/run_cli_tests.sh's "cpu targets" cases.
SAB_ID="S1868-compile-check-dropped"
SAB_FILE="src/core/compile.c"
SAB_SUITES="cli"
SAB_DESC="pcrec_compile stops checking the list: the library door accepts a bad token or a list beside SIMD off"
SAB_DOC_FIGURE="cli: the run_cli_tests.sh cpu-targets cell for this row reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1868."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (pcrec_memfn_simd_check(defo.flags, defo.memfn_simd, terr,
                                   sizeof terr) != 0) {
            if (err) snprintf(err->msg, sizeof(err->msg), "%s", terr);
            return -1;
        }'
SAB_AFTER='        (void)terr;   /* SABOTAGE S1868 */'
