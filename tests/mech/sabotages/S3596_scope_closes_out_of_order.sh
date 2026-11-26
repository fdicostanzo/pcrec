# S3596 -- [ARENA-SCOPES] F1, design sabotage (4) (lane arenabuild, 2026-11-25):
# two closes swapped (Discipline row L1, innermost-first).
#
# The tree has one site that closes several scopes in sequence,
# `pcrec_scope_unwind`; the plant makes it close the OUTERMOST open scope
# first, which is two closes swapped. The shared `scope_check` refuses the
# non-innermost handle. Net: scope_check's unwind check (two scopes open on a
# detached arena: the refusal aborts and the check binary dies), core.
SAB_ID="S3596-scope-closes-out-of-order"
SAB_FILE="src/core/arena.c"
SAB_SUITES="core"
SAB_DESC="pcrec_scope_unwind closes the outermost open scope first (two closes swapped): the L1 check refuses the non-innermost handle; scope_check's unwind check dies"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3596."
SAB_REACH_POP="tests/core/scope_check.c|pcrec_scope_unwind\\(&a\\);|1"
SAB_COUNT=1
SAB_BEFORE='        Scope s = { a, a->open, mark_pay(a->open)->gen };'
SAB_AFTER='        LEnt *m = a->open;   /* SABOTAGE S3596: the outermost open scope first */
        while (mark_pay(m)->prev_open) m = mark_pay(m)->prev_open;
        Scope s = { a, m, mark_pay(m)->gen };'
