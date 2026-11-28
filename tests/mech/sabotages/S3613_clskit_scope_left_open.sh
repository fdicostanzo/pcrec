# S3613 -- [ARENA-SCOPES] F2, design sabotage (5) at the second client (lane f2f6, 2026-11-26):
# pcrec_clskit_emit_kit never closes its scope (Discipline L2).
#
# Nothing leaks at run time (the teardown releases the child), which is why L2
# has its own runtime check: `pcrec_scope_check_closed` before the first take
# on the success path refuses every compile that emits a kit matcher, so the
# corpus goes red. (Anchored on the line before the close since [ARENA-SCOPES] SCOPE-4:
# emit_whole, S3643, has the same close line.) The scanner's L2-static rule reads the open without a close.
SAB_ID="S3613-clskit-scope-left-open"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="harness core"
SAB_DESC="pcrec_clskit_emit_kit's pcrec_scope_close deleted: the success-path check_closed refuses every kit-emitting compile (corpus red) and scratch_builder_check's L2-static rule flags the open"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3613."
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_puts(c, "}\n");
    pcrec_scope_close(&sc);'
SAB_AFTER='    pcrec_sb_puts(c, "}\n");
    /* SABOTAGE S3613: the scope is never closed */'
