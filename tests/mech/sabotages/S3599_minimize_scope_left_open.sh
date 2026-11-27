# S3599 -- [ARENA-SCOPES] F1, design sabotage (5) (lane arenabuild, 2026-11-25):
# minimize.c, the first scope client, never closes its scope (Discipline L2).
#
# Nothing leaks at run time (the teardown releases it), which is why L2 has
# its own runtime check: `pcrec_scope_check_closed` before the first take on
# the success path refuses, so every DFA compile refuses and the corpus goes
# red. The scanner's L2-static rule (core) reads the open without a close.
SAB_ID="S3599-minimize-scope-left-open"
SAB_FILE="src/opt/minimize.c"
SAB_SUITES="harness core"
SAB_DESC="pcrec_minimize_dfa's pcrec_scope_close deleted: the success-path check_closed refuses every DFA compile (corpus red) and scratch_builder_check's L2-static rule flags the open"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3599."
SAB_COUNT=1
SAB_BEFORE='    pcrec_scope_close(&sc);'
SAB_AFTER='    /* SABOTAGE S3599: the scope is never closed */'
