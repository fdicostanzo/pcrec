# S3615 -- [ARENA-SCOPES] F6, design sabotage (5) at the parse client (lane f2f6, 2026-11-26):
# uprops_produce never closes its scope (Discipline L2).
#
# Nothing leaks at run time (the teardown releases the child), which is why L2
# has its own runtime check: `pcrec_scope_check_closed` on the success path
# refuses every compile that decodes a `\p`, so the corpus goes red. The
# scanner's L2-static rule reads the open without a close.
SAB_ID="S3615-uprops-scope-left-open"
SAB_FILE="src/parse/mod_uprops.c"
SAB_SUITES="harness core"
SAB_DESC="uprops_produce's pcrec_scope_close deleted: the success-path check_closed refuses every \\p compile (corpus red) and scratch_builder_check's L2-static rule flags the open"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3615."
SAB_COUNT=1
SAB_BEFORE='    pcrec_scope_close(&sc);'
SAB_AFTER='    /* SABOTAGE S3615: the scope is never closed */'
