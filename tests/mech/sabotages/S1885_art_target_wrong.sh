# S1885 ([XARCH-DEV] U3, lane u3crit; review 2026-11-08-r5-xarch X-5a) -- pcrec states the WRONG target to the art: the portable one, while the artifact still carries the compile's guard and region, so a SIMD target's artifact renders no SIMD level. The value handed to the kit (S1870 skips the statement; S1865/S1866 plant the resolve table's rows, not the value).
# Detector (arm cli): tests/cli/run_cli_tests.sh's vrun cases at the 16- and 32-byte targets (measured: 7 cases red, the vrun-w16 one first).
SAB_ID="S1885-art-target-wrong"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="cli"
SAB_DESC="pcrec states the portable target to the art in place of the compile's, so a SIMD target's artifact carries its guard and region around no SIMD level"
SAB_DOC_FIGURE="cli: the run_cli_tests.sh vrun-w16 case reads red (7 vrun cases in all). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1885."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (mf_art_target(job->mf, pcrec_memfn_target(cx)))'
SAB_AFTER='        if (mf_art_target(job->mf, mf_portable_target()))   /* SABOTAGE S1885 */'
