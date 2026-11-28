# S255 — [REVW.U L8-F6(c)] `pcrec_arena_alloc`'s `pcrec_ctx_nomem` ROUTE IS NEUTERED, SO
# EVERY ALLOCATION FAILURE ABORTS THE CALLER'S PROCESS — K7's worst case,
# restored, in the one file (`src/core/arena.c`) that had ZERO sabotage
# rows before this one (`docs/dev/reviews/lens_reports/lens8_error_cleanup.md`
# F6: "there are zero sabotage rows on the error-path discipline ... none
# plants in arena.c, sb.c ... or compile.c's attachment block").
#
# `if (a->cx) pcrec_ctx_nomem(pcrec_err_chan(a->cx));` (the channel read through
# `pcrec_err_chan` since [ARENA-SCOPES] F1) becomes `if (0) ...` — the
# arena's error channel is never consulted, so EVERY arena allocation
# failure falls straight to the unconditional `abort()` below it, on EVERY
# compile, not only the two Job buffers F1 missed. This is the sabotage
# K7's own fix note (`docs/dev/known_issues.md`) describes having been run
# by hand and never committed. RE-AIMED (lane f4flag, 2026-11-27): arena.c's
# four nomem refusals, `pcrec_arena_alloc`'s included, now share the one cold
# helper `arena_nomem`, so the plant sits in its body (same line, same
# effect on `pcrec_arena_alloc`, and the scope/registry routes with it).
SAB_ID="S255-arena-ctx-nomem-neutered"
SAB_FILE="src/core/arena.c"
SAB_SUITES="resource"
SAB_DESC="pcrec_arena_alloc's pcrec_ctx_nomem route (arena.c's one arena_nomem helper) is neutered (if (0) instead of if (a->cx)), so EVERY arena allocation failure falls to the unconditional abort() below it, restoring K7's worst case (the caller's process is killed with no diagnostic) on every compile"
SAB_DOC_FIGURE="tests/resource/run_resource_tests.sh Section 2 (ulimit -v, Linux) and Section 2b ([REVW.U L8-F6(b)] the allocation-failure injector, darwin-viable) are the two detectors; Section 2b's own W1/W2/W3 witnesses all route through pcrec_arena_alloc, so this plant is reachable from either. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S255."
SAB_COUNT=1
SAB_BEFORE='static void arena_nomem(const Arena *a)
{
    if (a->cx) pcrec_ctx_nomem(pcrec_err_chan(a->cx));
    abort();
}'
SAB_AFTER='static void arena_nomem(const Arena *a)
{
    if (0) pcrec_ctx_nomem(pcrec_err_chan(a->cx));   /* SABOTAGE S255: the error channel is never consulted */
    abort();
}'
