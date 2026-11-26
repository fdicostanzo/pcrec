# S3600 -- [ARENA-SCOPES] F1, design sabotage (6) (lane arenabuild, 2026-11-25):
# a scope may open on a scope's child arena (Discipline L5).
#
# A child arena is released by its parent's close; a scope inside it would
# outlive nothing and hide a second registry the parent never walks. The plant
# drops the refusal. Net: scope_check's L5 check (core).
SAB_ID="S3600-scope-open-on-child"
SAB_FILE="src/core/arena.c"
SAB_SUITES="core"
SAB_DESC="pcrec_scope_open no longer refuses a child arena (L5): scope_check's L5 check reads no refusal"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3600."
SAB_REACH_POP="tests/core/scope_check.c|L5: pcrec_scope_open on a child|1"
SAB_COUNT=1
SAB_BEFORE='    if (a->child) reg_fail(a, "a scope opened on a scope'"'"'s child arena");'
SAB_AFTER='    /* SABOTAGE S3600: a child arena may open a scope */'
