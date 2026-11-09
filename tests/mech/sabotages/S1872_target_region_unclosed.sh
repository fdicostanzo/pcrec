# S1872 ([XARCH-DEV] U3, lane u3tgt) -- the target's region is never closed: everything after the part, `main` included, compiles for the target.
# Detector (arm cli): tests/cli/run_cli_tests.sh's "cpu targets U3" placement case (the close is not there once).
SAB_ID="S1872-target-region-unclosed"
SAB_FILE="src/gen/memfn_targets.c"
SAB_SUITES="cli"
SAB_DESC="the target's region is never closed, so main and anything after the part compile for the target"
SAB_DOC_FIGURE="cli: the run_cli_tests.sh placement case reads red. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1872."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    put_target_text(cx, c, mf_target_c_of(pcrec_memfn_target(cx))->region_close);'
SAB_AFTER='    put_target_text(cx, c, "");   /* SABOTAGE S1872 */'
