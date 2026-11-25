# S3595 -- [ARENA-SCOPES] F1, design sabotage (2) (lane arenabuild, 2026-11-25;
# review r102 B10): `pcrec_scope_close` no longer releases down to its mark.
#
# The close's post-condition (`a->top == below`) is the control: with the walk
# gone it refuses with an internal error, so every compile that runs a scope
# (minimize.c's tables: every DFA compile) refuses and the corpus goes red.
# scope_check's drills also fail (core).
# Re-anchored by lane arenabuild2 (ruling R-3: the registry is one LIFO array).
SAB_ID="S3595-scope-close-walk-dropped"
SAB_FILE="src/core/arena.c"
SAB_SUITES="harness core"
SAB_DESC="pcrec_scope_close skips release_to_mark: the close's post-condition refuses every compile that opens a scope (minimize), so the corpus refuses; scope_check's drills fail"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3595."
SAB_REACH_POP="src/opt/minimize.c|pcrec_scope_open\\(|1"
SAB_COUNT=1
SAB_BEFORE='    release_above(a, s->mark - 1);
    a->open = prev;'
SAB_AFTER='    a->open = prev;   /* SABOTAGE S3595: nothing above the mark is released */'
