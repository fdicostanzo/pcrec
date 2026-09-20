# S256 — [REVW.U L8-F6(c)] `sb_grow`'s `pcrec_ctx_nomem` ROUTE IS NEUTERED, SO
# EVERY StrBuf REALLOC FAILURE ABORTS THE CALLER'S PROCESS — K7's worst
# case, restored, in `src/core/sb.c` (zero sabotage rows before this one,
# lens 8's F6 finding, same shape as S255 one file over — arena.c and
# sb.c are the two allocators every compile touches).
#
# `if (sb->cx) pcrec_ctx_nomem(sb->cx);` becomes `if (0) pcrec_ctx_nomem(sb->cx);` —
# the StrBuf's own error channel is never consulted, so EVERY realloc
# failure inside `sb_grow` falls to the unconditional `abort()`, on
# every ATTACHED buffer (csb, hsb, vmsb, irsb, scr_test, scr_desc — the
# whole `Job`, not only the two F1 missed) as well as the deliberately
# detached ones `syntax_dump.c` already expects to abort.
SAB_ID="S256-sb-ctx-nomem-neutered"
SAB_FILE="src/core/sb.c"
SAB_SUITES="resource"
SAB_DESC="sb_grow's pcrec_ctx_nomem route is neutered (if (0) instead of if (sb->cx)), so EVERY StrBuf realloc failure falls to the unconditional abort() below it, restoring K7's worst case on every compile's csb/hsb/vmsb/irsb/scr_test/scr_desc buffer, not only the two F1 missed"
SAB_DOC_FIGURE="tests/resource/run_resource_tests.sh Section 2 (ulimit -v, Linux) and Section 2b ([REVW.U L8-F6(b)] the allocation-failure injector, darwin-viable) are the two detectors; every witness writes emitted C through a StrBuf, so this plant is reachable from either. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S256."
SAB_COUNT=1
SAB_BEFORE='    if (!np) {
        if (sb->cx) pcrec_ctx_nomem(sb->cx);
        abort();   /* a detached buffer (syntax_dump.c) has no error channel */
    }'
SAB_AFTER='    if (!np) {
        if (0) pcrec_ctx_nomem(sb->cx);   /* SABOTAGE S256: the error channel is never consulted */
        abort();   /* a detached buffer (syntax_dump.c) has no error channel */
    }'
