# S3614 -- [ARENA-SCOPES] F2, D-11 (r103 C12) (lane f2f6, 2026-11-26): the art's
# mf_arena binder no longer binds the literal `&cx->arena`.
#
# The plant spells the same pointer through a cast, so every answer is
# identical and nothing but tests/core/scratch_builder_check.py's type-keyed
# binder rule can tell it from a binder of some other arena (a scope's child).
# Core arm.
SAB_ID="S3614-mf-arena-binder-not-attempt-arena"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="core"
SAB_DESC="pcrec_memfn_art binds its mf_arena through a cast instead of the literal &cx->arena: only scratch_builder_check.py's D-11 binder rule (core arm) flags it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3614."
SAB_REACH_POP="src/gen/memfn_sites.c|^        ma->u = &cx->arena;|1"
SAB_COUNT=1
SAB_BEFORE='        ma->u = &cx->arena;'
SAB_AFTER='        ma->u = (void *)&cx->arena;   /* SABOTAGE S3614 */'
