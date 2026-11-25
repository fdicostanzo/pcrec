# S3593 -- [ARENA-SCOPES] F1, design sabotage (1) (lane arenabuild, 2026-11-25):
# `pcrec_arena_free` no longer releases the registry before the blocks.
#
# The teardown is the one release a refusal's longjmp reaches: every scope a
# refusal leaves open, its entries and the holds are freed there. The plant
# skips the walk. Nets: tests/core/scope_check.c's teardown checks (core) read
# the registry still populated, and alloc_check (resource arm, section 2b)
# reads minimize's scope tables and W6's part-text hold stranded.
SAB_ID="S3593-registry-teardown-walk-dropped"
SAB_FILE="src/core/arena.c"
SAB_SUITES="core resource"
SAB_DESC="pcrec_arena_free skips the registry walk: open scopes, their entries and the holds are never released by the teardown; scope_check's teardown checks and alloc_check's stranded-heap property see it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3593."
SAB_REACH_POP="src/core/arena.c|^    while \\(a->top\\) \\{|1
tests/core/scope_check.c|teardown: pcrec_arena_free releases|2"
SAB_COUNT=1
SAB_BEFORE='    while (a->top) {'
SAB_AFTER='    while (0 && a->top) {   /* SABOTAGE S3593: the registry is never released */'
