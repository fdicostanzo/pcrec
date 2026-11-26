# S3602 -- [ARENA-SCOPES] F1, design sabotage (10), THE SEEN GATE's (iii)
# (lane arenabuild, 2026-11-25; review r103 C20): W7's hand-kept-arena window
# loses its bookkeeping.
#
# alloc_check's test link records a hand-kept arena when it takes its first
# block (`__wrap_pcrec_arena_alloc`); the plant drops the record, so the
# window never opens. The W7 control (the planted strand) reads no trial and
# FAILs, and W3's filed `uprops_produce` row reads UNREACHED (red): a window
# that cannot see a stranded arena cannot pass its own gate.
SAB_ID="S3602-w7-hand-kept-window-blind"
SAB_FILE="tests/core/alloc_check.c"
SAB_SUITES="resource"
SAB_DESC="alloc_check's __wrap_pcrec_arena_alloc never records a hand-kept arena: the W7 control reads nothing and the uprops_produce known_stranded row reads UNREACHED"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3602."
SAB_REACH_POP="tests/core/alloc_check.c|uprops_produce tmp arena|1"
SAB_COUNT=1
SAB_BEFORE='        hk[hk_n++] = a;'
SAB_AFTER='        (void)a;   /* SABOTAGE S3602: the hand-kept arena is never recorded */'
