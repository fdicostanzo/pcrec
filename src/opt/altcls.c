/* [OPT-ALTCLS] ALTERNATION NORMALIZATION (docs/dev/plan.md's [OPT-ALTCLS]
 * row; since [RUN-POS-SET] stage 2b, docs/design/alt_normal_form.md §3.3, a
 * CALLER of the alternation owner, src/opt/altnf.c). An AST-to-AST REWRITE
 * run once, immediately after parse and before everything downstream
 * (engine selection, possessify/revdet/mrl, both machine builds, both
 * emitters) -- see internal.h's comment on `pcrec_altcls` for why that
 * placement is load-bearing rather than a style choice.
 *
 * WHAT THIS FILE OWNS: the WALK. It flattens every alternation spine it
 * reaches (transparent through non-capturing groups), normalizes inner
 * alternations first, and hands each branch list to `pcrec_altnf` with
 * the rules {M, P, S} less the denied ones (bit 10 removes the sibling
 * merge M; bit 11 removes prefix and suffix factoring P and S). The rules,
 * their soundness (the adjacency test that gates every moved branch; P's
 * fixed-width capture-free key; S's identical tail) and their order are
 * the owner's. Its two former stages (adjacent single-character merge,
 * literal-first-byte prefix factoring) were special cases of M and P and
 * are deleted: `(?:a|b)` merges, and `frank|fred` factors, as before.
 *
 * WHAT IT DOES NOT ENTER: lookaround bodies (until [VLOOKBEHIND]'s own row,
 * design §3.3 r4 SND-5: factoring inside a lookbehind can turn an accepted
 * pattern into a refused one), atomic bodies (the cut commits to the body's
 * order), call targets (shared subtrees), and the lowering's `A_WCLASS`.
 * Each such arm is a leaf below, with its reason.
 *
 * NO NEW CAPTURING GROUPS: the owner allocates A_CLASS/A_CAT/A_ALT/A_EMPTY
 * nodes only, so the group count never moves.
 *
 * RECURSION DISCIPLINE (D10/DD-10/R1 R-2, K20): the walk recurses on
 * NESTING depth only; alternation and concatenation spines are walked
 * iteratively. The owner's own recursion is on split depth, bounded by
 * `PCREC_MAX_ALTCLS_FACTOR_DEPTH`.
 *
 * D46: both levers deny (`PCREC_NO_ALTCLS_MERGE`/`PCREC_NO_ALTCLS_FACTOR`,
 * lib/pcrec.h) and both are stamped (`<PREFIX>_ALTCLS_MERGES`, the lists
 * the merge folded; `<PREFIX>_ALTCLS_FACTORED`, the P and S factorings;
 * src/gen/emit_dfa.c's `pcrec_emit_prologue`, shared by both emitters).
 *
 * Tests: tests/altcls/. Sabotage: tests/mech/sabotages/ (S66/S67, S1888-S1893). */

#include <string.h>

#include "core/internal.h"

static Ast *altcls_walk(Ctx *cx, Ast *a);

/* ---- spine/rebuild helpers -------------------------------------------- */

/* Flatten a (possibly trivial) LEFT-NESTED A_CAT spine into an ordered,
 * left-to-right atom array. A non-A_CAT node is a length-1 spine of itself.
 * Iterative (D10/DD-10/K20): the spine can be as long as the pattern. */
static size_t altcls_cat_flatten(Ctx *cx, Ast *a, Ast ***out)
{
    size_t n = 1;
    for (Ast *t = a; t->k == A_CAT; t = t->l) n++;
    Ast **arr = pcrec_arena_alloc(&cx->arena, n * sizeof(Ast *));
    Ast *t = a;
    size_t i = n - 1;
    while (t->k == A_CAT) { arr[i--] = t->r; t = t->l; }
    arr[0] = t;
    *out = arr;
    return n;
}

/* Rebuild a LEFT-NESTED A_CAT chain from an ordered array -- the same shape
 * parse.c's p_cat itself builds, so nothing downstream can tell a rebuilt
 * spine from a parsed one. n == 0 -> A_EMPTY (an all-consumed remainder,
 * e.g. peeling "f"'s only atom leaves nothing). */
static Ast *altcls_rebuild_cat(Ctx *cx, Ast **arr, size_t n)
{
    if (n == 0) return pcrec_ast_node(cx, A_EMPTY);
    Ast *res = arr[0];
    for (size_t i = 1; i < n; i++) {
        Ast *cat = pcrec_ast_node(cx, A_CAT);
        cat->l = res;
        cat->r = arr[i];
        res = cat;
    }
    return res;
}

/* Rebuild a LEFT-NESTED A_ALT chain from an ordered array -- p_alt_info's
 * own shape. Caller guarantees n >= 1. */
static Ast *altcls_rebuild_alt(Ctx *cx, Ast **arr, size_t n)
{
    Ast *res = arr[0];
    for (size_t i = 1; i < n; i++) {
        Ast *alt = pcrec_ast_node(cx, A_ALT);
        alt->l = res;
        alt->r = arr[i];
        res = alt;
    }
    return res;
}

/* ---- stage 1 + dispatch ------------------------------------------------- */

/* Dispatch over an A_ALT spine: flattens the maximal left-nested run
 * (transparent through non-capturing groups, so `(?:a|b)|c` flattens
 * identically to `a|b|c`), walks each branch through `altcls_walk` (inner
 * alternations first), then hands the list to THE ALTERNATION OWNER
 * (`pcrec_altnf`, src/opt/altnf.c; [RUN-POS-SET] stage 2b) with rules
 * {M, P, S} less the denied ones: bit 10 removes M, bit 11 removes P and S.
 * The stamps add the owner's counts: the lists in which M folded, and the
 * P and S factorings. Returns `a` unchanged when nothing was rewritten.
 * Introduces no capturing group, ever: the owner allocates
 * A_CLASS/A_CAT/A_ALT/A_EMPTY nodes only. */
static Ast *altcls_walk_alt(Ctx *cx, Ast *a)
{
    /* Flatten the maximal LEFT-NESTED A_ALT spine. Transparent non-capturing
     * groups keep this flat across parens too -- `(?:a|b)|c` parses
     * IDENTICALLY to `a|b|c`, since `(?:...)` produces no wrapper node
     * (parse.c PARSE-1) -- so one flatten here reaches every branch a
     * capturing group does not wall off. */
    size_t n = 1;
    for (Ast *t = a; t->k == A_ALT; t = t->l) n++;
    Ast **br = pcrec_arena_alloc(&cx->arena, n * sizeof(Ast *));
    {
        Ast *t = a;
        size_t i = n - 1;
        while (t->k == A_ALT) { br[i--] = t->r; t = t->l; }
        br[0] = t;
    }

    bool any_rewritten = false;
    for (size_t k = 0; k < n; k++) {
        Ast *w = altcls_walk(cx, br[k]);
        if (w != br[k]) any_rewritten = true;
        br[k] = w;
    }

    Ast **was = pcrec_arena_alloc(&cx->arena, n * sizeof(Ast *));
    memcpy(was, br, n * sizeof(Ast *));
    bool factor = !pcrec_opt_has(cx->opt, PCREC_NO_ALTCLS_FACTOR);
    PcrecAnfRules rules = { .merge = !pcrec_opt_has(cx->opt, PCREC_NO_ALTCLS_MERGE),
                            .prefix = factor, .suffix = factor };
    PcrecAnfStats st = { 0 };
    int m = pcrec_altnf(cx, br, (int)n, rules, &st);
    cx->job->altcls_merges += st.merge_lists;
    cx->job->altcls_factored += st.factored;
    if ((size_t)m != n || memcmp(was, br, n * sizeof(Ast *)) != 0) any_rewritten = true;

    if (!any_rewritten) return a;   /* nothing moved; no trace */
    return altcls_rebuild_alt(cx, br, (size_t)m);
}

/* Flattens an A_CAT spine (altcls_cat_flatten) and applies altcls_walk to each
 * member, rebuilding the spine (altcls_rebuild_cat) only if some member
 * actually rewrote. */
static Ast *altcls_walk_cat(Ctx *cx, Ast *a)
{
    Ast **arr;
    size_t n = altcls_cat_flatten(cx, a, &arr);
    bool any_rewritten = false;
    for (size_t i = 0; i < n; i++) {
        Ast *w = altcls_walk(cx, arr[i]);
        if (w != arr[i]) any_rewritten = true;
        arr[i] = w;
    }
    if (!any_rewritten) return a;
    return altcls_rebuild_cat(cx, arr, n);
}

/* Recurses on NESTING depth only (an A_REP body, an A_CAP body), never on
 * spine length -- D10/DD-10/R1 R-2/K20's discipline, held the same way
 * possessify.c/revdet.c hold it. */
static Ast *altcls_walk(Ctx *cx, Ast *a)
{
    switch (a->k) {
    case A_CLASS:
    case A_EMPTY:
    case A_EOL:
    /* [M6.2 wave B] zero-width, so there is nothing for either stage to
     * merge or factor -- the same answer A_EOL already gives. Since
     * [DD-11.5] P2e `^`/`\A`/`\z` are A_CTX rows and take this arm too. */
    case A_CTX:
    /* [M6.2 wave D] `\G` likewise: zero-width, nothing to merge or factor. */
    case A_GSTART:
    /* [M6.5.2] A backreference is a LEAF to both stages and must stay one.
     * Stage 1 merges an alternation run of single-BYTE branches into one
     * class; a backreference consumes a variable number of bytes decided at
     * match time, so it is not a byte and `(a|\1)` must not become a class.
     * Stage 2 factors a shared literal PREFIX; a backreference has no
     * compile-time first byte to share. Taking the leaf arm is the answer to
     * both, and it is the same answer for the same reason `\G` gets it: the
     * node is opaque to a transformation that reasons about bytes. */
    case A_BREF:
    /* [VAR] A LEAF for the identical reason, one step stronger: a variable
     * consumes a match-time number of bytes AND its bytes are not in the
     * subject at all, so it is neither a single-byte branch stage 1 could
     * merge nor a compile-time first byte stage 2 could peel. */
    case A_VAR:
    case A_CALLOUT:
    /* [M6.2 wave E] `\K` likewise AS A LEAF — but it is the first kind here
     * that could be damaged by the two stages rather than merely unserved by
     * them, so the reason it is safe is written down instead of assumed.
     *
     * Stage 1 merges single-byte BRANCHES into one class; a branch that is or
     * begins with `\K` is not a single-byte class, so it never enters the
     * merge. Stage 2 peels a shared leading literal, and `altcls_branch_peel`
     * requires the flattened branch's FIRST element to be an A_CLASS — an
     * A_KRESET there stops the peel dead. So `\Kab|\Kac` is left alone
     * entirely, and `a\Kb|a\Kc` factors only the `a` that precedes both
     * copies, leaving each `\K` in the branch it was written in and at the
     * same distance from the branch's start. Neither stage can move a `\K`
     * across a byte, which is the only rewrite that would change the reported
     * start. */
    case A_KRESET:
    /* [M6.6.2] A LEAF TO BOTH STAGES, `A_BREF`'s arm for `A_BREF`'s reason
     * and one more of its own.
     *
     * Stage 1 merges an alternation run of single-BYTE branches into one
     * class. A lookaround is not a byte — it consumes none at all — so
     * `(a|(?=b))` must not become a class, and taking the leaf arm is what
     * says so. Stage 2 factors a shared literal PREFIX and needs a
     * compile-time first byte; a lookaround has none.
     *
     * THE BODY IS NOT WALKED EITHER, which is the extra half. Normalising an
     * alternation INSIDE a lookaround body would be sound (the body is an
     * ordinary sub-pattern) and is declined for the same reason the other
     * inert arms in this wave decline: no producer exists, so a rewrite in
     * there could not be exercised by any test, and this pass changes tree
     * SHAPE — the one class of edit a byte-identity gate is built to notice.
     * Declining costs an optimisation on a body that does not exist yet. */
    case A_LOOK:
    /* [DD-14] A LEAF TO BOTH STAGES, `A_BREF`'s arm for `A_BREF`'s reason.
     *
     * Stage 1 merges an alternation run of single-BYTE branches into one
     * class. A call is not a byte: it consumes whatever its callee consumes,
     * a quantity that is not even bounded for a recursive callee, so
     * `(a|(?1))` must not become a class. Stage 2 factors a shared literal
     * PREFIX and needs a compile-time first byte; a call's is the callee's,
     * which is not reachable from this node.
     *
     * THE CALLEE IS NOT WALKED FROM HERE, and for this pass that is not
     * merely the cautious choice — it is required. This walk REBUILDS nodes
     * (`altcls_rebuild_cat`, and the `A_REP` arm below allocates a fresh node
     * when the body changes), so reaching the callee through `u.call.body`
     * would rewrite a subtree that ANOTHER part of the tree still points at,
     * and the two would disagree about which nodes are shared. The callee's
     * own alternations are normalised when this same walk reaches the callee
     * at its LEXICAL position, which is the one place its rebuilt node can be
     * stored back. */
    case A_CALL:
        return a;
    /* [CLS-TREE] S3: made by the encoding lowering, below this pass. */
    case A_WCLASS:
        return a;
    case A_CAT:
        return altcls_walk_cat(cx, a);
    case A_ALT:
        return altcls_walk_alt(cx, a);
    case A_REP: {
        Ast *body = altcls_walk(cx, a->l);
        if (body == a->l) return a;
        Ast *r = pcrec_ast_node(cx, A_REP);
        *r = *a;
        r->l = body;
        return r;
    }
    case A_CAP: {
        Ast *body = altcls_walk(cx, a->l);
        if (body == a->l) return a;
        Ast *r = pcrec_ast_node(cx, A_CAP);
        *r = *a;
        r->l = body;
        return r;
    }
    /* [M6.4.2] DECLINE: an atomic group is not a class and never becomes one.
     *
     * Both stages here rewrite an ALTERNATION — merging single-byte branches
     * into one class, or factoring a common prefix out of several — and the
     * merge in particular is only sound because the branches it collapses are
     * INTERCHANGEABLE: a class has no branch order, so nothing downstream can
     * observe which member matched. Inside a cut that stops being true. The
     * body's OWN alternation order is exactly what the cut commits to
     * (`(?>a|ab)c` and `(?>ab|a)c` answer differently on "abc"), so a rewrite
     * that lost the order would change the language.
     *
     * Declining is always available and always safe here — this pass is a pure
     * optimisation — and it is the CONSERVATIVE answer rather than a claim
     * that no atomic body is ever rewritable. Walking INTO the body would be
     * defensible for the branches of an alternation the cut does not reorder,
     * and is deliberately not taken: the win is unmeasured and the analysis
     * that would justify it is [ENG-CUT]'s, not this row's. */
    case A_ATOMIC:
        return a;
    }
    return a;   /* unreachable under -Wswitch (make strict); mrl.c's rule */
}

/* Entry point: altcls_walk over the whole tree. */
Ast *pcrec_altcls(Ctx *cx, Ast *root)
{
    return altcls_walk(cx, root);
}
