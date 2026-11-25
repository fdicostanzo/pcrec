# S3594 -- [ARENA-SCOPES] F1, design sabotage (1b) (lane arenabuild, 2026-11-25):
# the shared per-record release frees the entry's resource but never the
# record itself.
#
# Every release path (close, scope_free, unwind, the teardown) goes through
# `rec_release`, so every registry record strands: minimize's scope records on
# every compile it runs. Net: alloc_check (resource arm, section 2b), whose
# profiling pass reads heap live after pcrec_output_free.
SAB_ID="S3594-registry-record-not-freed"
SAB_FILE="src/core/arena.c"
SAB_SUITES="resource"
SAB_DESC="rec_release releases an entry's resource but never frees its record: every registry path strands one calloc per entry; alloc_check's profiling pass sees heap live after pcrec_output_free"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3594."
SAB_REACH_POP="src/core/arena.c|^    e->kind->release\\(e->payload\\);|1"
SAB_COUNT=1
SAB_BEFORE='    e->kind->release(e->payload);
    free(e);'
SAB_AFTER='    e->kind->release(e->payload);   /* SABOTAGE S3594: the record is never freed */'
