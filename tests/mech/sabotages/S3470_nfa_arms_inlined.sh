# S3470 — [DD-10]/K152 (lane k152fix): THE NFA BUILDER'S ARMS POURED BACK INTO
# ITS DISPATCHER. (src/ir/nfa.c, compile_ast and its own-frame arms.)
#
# The K152 fix gave each arm of `compile_ast` (the CAT/ALT/REP recursions,
# the leaves, the tail-`$` and splice recursions, the atomic arm's row read
# and `trie_key`) its own frame with `PCREC_OWN_FRAME`, and gave `nfa_cat` ONE
# recursion site instead of four. This plant undoes both: every mark in
# nfa.c becomes always_inline (site 1, the 10 marks) and nfa_cat gets its
# two loops back (site 2). That rebuilds the pre-fix frame exactly
# (measured: `(?:abc|abd…abe)*` x250 440,176 B, as at base 2b4e56eab), and
# the compound-route nest `^(?:abc|abd…abe)*…|b$` (DEPTH_FAMILIES
# `litcompound`) dies on the 442,368-byte thread, as at base. Same answers.
#
# ONE ROW, NOT ONE PER PIECE: measured by plant (lane k152fix), each piece
# alone leaves the deepest row under the budget (marks dropped, sites kept
# single: 408,560 B; nfa_rep alone inlined: 408,560 B), and
# run_compile_stack.sh reads the budget, not the headroom, so a partial
# undo is invisible to it by design.
SAB_ID="S3470-nfa-arms-inlined"
SAB_FILE="src/ir/nfa.c"
SAB_SUITES="compilestack"
SAB_DESC='compile_ast'"'"'s own-frame arms are forced inline and nfa_cat gets its per-loop recursion sites back (the K152 fix undone): litcompound nested 250 deep dies on the budget thread'
SAB_DOC_FIGURE='docs/spec/limits.md §3.10; validated by plant at lane k152fix (litcompound DIED 139); exact re-run: bash tests/mech/run_sabotage_matrix.sh S3470.'
SAB_EXPECT='DETECTED'
SAB_COUNT='10'
SAB_BEFORE='static PCREC_OWN_FRAME '
SAB_AFTER='static inline __attribute__((always_inline)) /* SABOTAGE S3470 */ '
SAB_FILE2="src/ir/nfa.c"
SAB_COUNT2=1
SAB_BEFORE2='    Frag f = { -1, {0} };
    for (int j = 0; j <= nsp; j++) {
        const Ast *x = !b->rev ? (j == 0 ? t : rs[j - 1])
                               : (j == nsp ? t : rs[nsp - 1 - j]);
        Frag c = compile_ast(b, x);
        f = (j == 0) ? c : frag_cat2(b, f, c);
    }
    return f;'
SAB_AFTER2='    Frag f;   /* SABOTAGE S3470 */
    if (!b->rev) {
        f = compile_ast(b, t);
        for (int j = 0; j < nsp; j++)
            f = frag_cat2(b, f, compile_ast(b, rs[j]));
    } else {
        f = compile_ast(b, rs[nsp - 1]);
        for (int j = nsp - 2; j >= 0; j--)
            f = frag_cat2(b, f, compile_ast(b, rs[j]));
        f = frag_cat2(b, f, compile_ast(b, t));
    }
    return f;'
