# S1871 ([XARCH-DEV] U3, lane u3tgt) -- the family guard is never placed: a SIMD target's artifact compiles silently for another CPU family instead of stopping at the kit's #error.
# Detector (arm cli): tests/cli/run_cli_tests.sh's "cpu targets U3" placement case (the guard is not there once).
SAB_ID="S1871-target-guard-dropped"
SAB_FILE="src/gen/memfn_targets.c"
SAB_SUITES="cli"
SAB_DESC="the kit's family guard is never placed, so a SIMD target's artifact compiles for another CPU family without refusing"
SAB_DOC_FIGURE="cli: the run_cli_tests.sh placement case reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1871."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    put_target_text(cx, c, t->family ? mf_family_c_of(t->family)->guard : "");'
SAB_AFTER='    put_target_text(cx, c, "");   /* SABOTAGE S1871 */'
