# S3594 -- [ARENA-SCOPES] F1, design sabotage (1b) (lane arenabuild, 2026-11-25;
# re-aimed by lane arenabuild2, ruling R-3): the registry's record storage is
# never freed. At F1 records were one calloc each and the plant dropped the
# per-record free; since R-3 they live in ONE array per Arena, freed by
# `pcrec_arena_free`, so the plant drops that free.
#
# Every arena whose registry was ever used (the attempt arena of every compile
# that runs minimize) strands its array. Net: alloc_check (resource arm,
# section 2b), whose profiling pass reads heap live after pcrec_output_free.
SAB_ID="S3594-registry-record-not-freed"
SAB_FILE="src/core/arena.c"
SAB_SUITES="resource"
SAB_DESC="pcrec_arena_free releases every entry but never frees the registry's array: every arena whose registry was used strands it; alloc_check's profiling pass sees heap live after pcrec_output_free"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3594."
SAB_REACH_POP="src/core/arena.c|^    free\\(a->rec\\);|1"
SAB_COUNT=1
SAB_BEFORE='    free(a->rec);
    a->rec = NULL;'
SAB_AFTER='    a->rec = NULL;   /* SABOTAGE S3594: the registry array is never freed */'
