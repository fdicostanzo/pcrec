# S3598 -- [ARENA-SCOPES] F1, design sabotage (4c) (lane arenabuild, 2026-11-25;
# review r103 C5): the shared scope_check drops its generation-stamp compare.
#
# The same plant as S3597, run under AddressSanitizer: the drill's real stale
# handle (a closed mark's position reused; since R-3 positions, not addresses,
# so the reuse is certain) is the half the position compare cannot refuse, and
# asan keeps the forged half honest (design C5).
# Re-anchored by lane arenabuild2 (ruling R-3: the registry is one LIFO array).
SAB_ID="S3598-scope-check-gen-dropped-asan"
SAB_FILE="src/core/arena.c"
SAB_SUITES="core"
SAB_REQUIRE="asan"
SAB_DESC="scope_check compares the handle's mark pointer only, not its stamp: a stale handle whose mark address was reused passes; scope_check's forged-handle drill sees it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3598."
SAB_REACH_POP="tests/core/scope_check.c|forged|2"
SAB_COUNT=1
SAB_BEFORE='    if (!(a->open && a->open == s->mark && rec_at(a, a->open)->gen == s->gen))'
SAB_AFTER='    if (!(a->open && a->open == s->mark))   /* SABOTAGE S3598: the stamp is not compared */'
