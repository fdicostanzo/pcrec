# S255 — [REVW.U L8-F6(c)] `arena_alloc`'s `ctx_nomem` ROUTE IS NEUTERED, SO
# EVERY ALLOCATION FAILURE ABORTS THE CALLER'S PROCESS — K7's worst case,
# restored, in the one file (`src/core/arena.c`) that had ZERO sabotage
# rows before this one (`docs/dev/reviews/lens_reports/lens8_error_cleanup.md`
# F6: "there are zero sabotage rows on the error-path discipline ... none
# plants in arena.c, sb.c ... or compile.c's attachment block").
#
# `if (a->cx) ctx_nomem(a->cx);` becomes `if (0) ctx_nomem(a->cx);` — the
# arena's error channel is never consulted, so EVERY arena allocation
# failure falls straight to the unconditional `abort()` below it, on EVERY
# compile, not only the two Job buffers F1 missed. This is the sabotage
# K7's own fix note (`docs/dev/known_issues.md`) describes having been run
# by hand and never committed.
SAB_ID="S255-arena-ctx-nomem-neutered"
SAB_FILE="src/core/arena.c"
SAB_SUITES="resource"
SAB_DESC="arena_alloc's ctx_nomem route is neutered (if (0) instead of if (a->cx)), so EVERY arena allocation failure falls to the unconditional abort() below it, restoring K7's worst case (the caller's process is killed with no diagnostic) on every compile"
SAB_DOC_FIGURE="tests/resource/run_resource_tests.sh Section 2 (ulimit -v, Linux) and Section 2b ([REVW.U L8-F6(b)] the allocation-failure injector, darwin-viable) are the two detectors; Section 2b's own W1/W2/W3 witnesses all route through arena_alloc, so this plant is reachable from either. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S255."
SAB_COUNT=1
SAB_BEFORE='        if (!b) {
            if (a->cx) ctx_nomem(a->cx);
            abort();
        }'
SAB_AFTER='        if (!b) {
            if (0) ctx_nomem(a->cx);   /* SABOTAGE S255: the error channel is never consulted */
            abort();
        }'
