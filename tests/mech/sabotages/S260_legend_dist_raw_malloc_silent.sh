# S260 — [D110/ALLOC-PINS] THE D105 DEFECT SHAPE IS REPLANTED INTO
# `emit_state_legend` (`src/gen/emit_dfa.c`) — A RAW `malloc` FOR ONE BFS
# SCRATCH ARRAY, SILENT `return` ON NULL
# (tests/core/alloc_check.c, tests/resource/run_resource_tests.sh Section 2b).
#
# D105 restructured `emit_state_legend` so its four BFS scratch arrays route
# through `pcrec_arena_alloc(&cx->arena, ...)`, which reaches `pcrec_ctx_nomem` and
# refuses the compile through the tree's one general recovery mechanism on
# an allocation failure. This sabotage reverts the FIRST of those four
# (`dist`) to a raw `malloc` with a silent `return` on NULL — the minimal
# plant that reintroduces D105's own silent-degradation path: on a forced
# failure of that one allocation, the legend is silently dropped (a
# correct compile, no diagnostic) rather than the compile being refused.
# Deliberately ONE array, not all four, per the brief's "minimal plant"
# instruction — one silently-degrading site is already the whole defect
# shape D105 eliminated.
SAB_ID="S260-legend-dist-raw-malloc-silent"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="resource"
SAB_DESC="emit_state_legend's dist array reverts to a raw malloc with a silent return on NULL (never reaching pcrec_ctx_nomem), replanting D105's own legend-class silent-degradation absorption"
SAB_DOC_FIGURE="tests/core/alloc_check.c's W1/W3 witnesses (the legend class) are D105's own repro: make alloc reads absorbed 0 -> nonzero under this plant on a forced failure of dist's allocation. tests/resource/run_resource_tests.sh Section 2b (D110) is the make-test-reachable detector: it now asserts alloc_check's own rc and the absence of any SUCCEEDED THROUGH line, not only the signal grep. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S260."
SAB_COUNT=1
SAB_BEFORE='    int *dist  = pcrec_arena_alloc(&cx->arena, (size_t)d->n * sizeof(int));
    int *queue = pcrec_arena_alloc(&cx->arena, (size_t)d->n * sizeof(int));'
SAB_AFTER='    int *dist  = malloc((size_t)d->n * sizeof(int));   /* SABOTAGE S260: raw malloc, silent NULL return */
    if (!dist) return;
    int *queue = pcrec_arena_alloc(&cx->arena, (size_t)d->n * sizeof(int));'
