# S257 — [REVW.U L8-F6(c)] `compile_driver`'s ATTACHMENT BLOCK DROPS
# `csb`/`hsb`'s `.cx` BACK-POINTER — F1's OWN SHAPE (fix-now #1 of the
# 2026-09-17 code review, `Job.scr_test`/`scr_desc`), REPRODUCED on the
# PRIMARY code-string buffer this time, in `src/core/compile.c`'s
# attachment block itself (zero sabotage rows before this one, lens 8's
# F6 finding).
#
# `cx.job->csb.cx = cx.job->hsb.cx = &cx;` is deleted outright, so `csb`
# (the buffer EVERY DFA/VM emitter writes the generated `.c` body into)
# and `hsb` (the paired `.h`) are never attached — any `sb_grow` failure
# on either takes `sb.c`'s unattached-buffer `abort()` branch instead of
# `ctx_nomem`'s diagnosed refusal, on every ordinary compile rather than
# only the two Job buffers F1's own incident involved.
SAB_ID="S257-compile-csb-attachment-dropped"
SAB_FILE="src/core/compile.c"
SAB_SUITES="resource"
SAB_DESC="compile_driver's attachment block drops csb/hsb's .cx back-pointer entirely (F1's own shape, reproduced on the primary code-string buffer rather than scr_test/scr_desc) -- any sb_grow failure on the generated .c/.h buffers aborts the caller's process instead of a diagnosed refusal, on every ordinary compile"
SAB_DOC_FIGURE="tests/resource/run_resource_tests.sh Section 2 (ulimit -v, Linux) and Section 2b ([REVW.U L8-F6(b)] the allocation-failure injector, darwin-viable) are the two detectors; every witness writes the generated .c body through csb, so this plant is reachable from either -- and it is the shape F6(c)'s own injector-based W2 witness already confirmed catches (SIGABRT, signal 6) when F1's own two buffers were the unattached ones. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S257."
SAB_COUNT=1
SAB_BEFORE='        cx.arena.cx = &cx;
        cx.job = calloc(1, sizeof(Job));
        if (cx.job) {
            cx.job->csb.cx = cx.job->hsb.cx = &cx;
            cx.job->vmsb.cx = cx.job->irsb.cx = &cx;
            cx.job->scr_test.cx = cx.job->scr_desc.cx = &cx;
        }'
SAB_AFTER='        cx.arena.cx = &cx;
        cx.job = calloc(1, sizeof(Job));
        if (cx.job) {
            /* SABOTAGE S257: csb/hsb attachment dropped entirely */
            cx.job->vmsb.cx = cx.job->irsb.cx = &cx;
            cx.job->scr_test.cx = cx.job->scr_desc.cx = &cx;
        }'
