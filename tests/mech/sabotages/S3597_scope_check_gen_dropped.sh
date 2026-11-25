# S3597 -- [ARENA-SCOPES] F1, design sabotage (4b) (lane arenabuild, 2026-11-25;
# review r103 C5): the shared scope_check drops its generation-stamp compare.
#
# Net: scope_check's stale-handle drill (the FORGED handle carries the live
# mark's address and an old stamp, so only the stamp compare can refuse it), core.
# Re-anchored by lane arenabuild2 (ruling R-3: the registry is one LIFO array).
SAB_ID="S3597-scope-check-gen-dropped"
SAB_FILE="src/core/arena.c"
SAB_SUITES="core"
SAB_DESC="scope_check compares the handle's mark pointer only, not its stamp: a stale handle whose mark address was reused passes; scope_check's forged-handle drill sees it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3597."
SAB_REACH_POP="tests/core/scope_check.c|forged|2"
SAB_COUNT=1
SAB_BEFORE='    if (!(a->open && a->open == s->mark && rec_at(a, a->open)->gen == s->gen))'
SAB_AFTER='    if (!(a->open && a->open == s->mark))   /* SABOTAGE S3597: the stamp is not compared */'
