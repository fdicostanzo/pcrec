# S3643 -- [ARENA-SCOPES] SCOPE-4 (lane scope4, 2026-11-27), design sabotage (5) at
# the whole-set client: pcrec_clskit_emit_whole never closes its scope
# (Discipline L2). The sibling of S3613 (emit_kit).
#
# Nothing leaks at run time (compile_driver's handler-top unwind, or the
# teardown on the count/dump routes, releases the child), which is why L2 has
# its own runtime check: `pcrec_scope_check_closed` on the success path refuses
# every compile that emits a whole-set matcher. The scanner's L2-static rule
# reads the open without a close in the same function (core arm).
SAB_ID="S3643-clskit-whole-scope-left-open"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="harness core"
SAB_DESC="pcrec_clskit_emit_whole's pcrec_scope_close deleted: scratch_builder_check's L2-static rule flags the open (core arm) and the success-path check_closed refuses every whole-set-emitting compile (harness)"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3643."
SAB_COUNT=1
SAB_BEFORE='    emit_whole_body(c, pcrec_scope_arena(&sc), fn, f, iv, n);
    pcrec_scope_close(&sc);'
SAB_AFTER='    emit_whole_body(c, pcrec_scope_arena(&sc), fn, f, iv, n);
    /* SABOTAGE S3643: the scope is never closed */'
