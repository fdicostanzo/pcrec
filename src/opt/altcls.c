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

/* ---- dispatch ------------------------------------------------------------ */

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
    Ast **br;
    size_t n = (size_t)pcrec_spine_flatten(cx, a, A_ALT, &br);

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
    return pcrec_spine_build(cx, A_ALT, br, m);
}

/* Flattens an A_CAT spine and applies altcls_walk to each member, rebuilding
 * the spine only if some member actually rewrote. */
static Ast *altcls_walk_cat(Ctx *cx, Ast *a)
{
    Ast **arr;
    size_t n = (size_t)pcrec_spine_flatten(cx, a, A_CAT, &arr);
    bool any_rewritten = false;
    for (size_t i = 0; i < n; i++) {
        Ast *w = altcls_walk(cx, arr[i]);
        if (w != arr[i]) any_rewritten = true;
        arr[i] = w;
    }
    if (!any_rewritten) return a;
    return pcrec_spine_build(cx, A_CAT, arr, (int)n);
}

/* Recurses on NESTING depth only (an A_REP body, an A_CAP body), never on
 * spine length -- D10/DD-10/R1 R-2/K20's discipline, held the same way
 * possessify.c/revdet.c hold it. */
static Ast *altcls_walk(Ctx *cx, Ast *a)
{
    switch (a->k) {
    /* THE LEAVES. Since stage 2b this walk only FINDS alternations; whether
     * a branch holding one of these nodes may be merged, factored or moved
     * past another is decided by the owner (src/opt/altnf.c) from each
     * branch's description: rule M's adjacency test (`anf_passes`, reading
     * `PdHead`'s width bounds and its `writes` bit), P's fixed-width
     * capture-free key and S's identical tail. A node the owner cannot
     * describe exactly (a backreference, a variable, a call, a callout, `\K`,
     * a lookaround) makes its branch decline those rules; nothing here
     * argues their soundness. What this switch decides is only which bodies
     * the WALK enters. */
    case A_CLASS:
    case A_EMPTY:
    case A_EOL:
    case A_CTX:
    case A_GSTART:
    case A_BREF:
    case A_VAR:
    case A_CALLOUT:
    case A_KRESET:
    /* A lookaround body is not walked: normalizing inside one is sound as a
     * sub-pattern, but factoring inside a lookbehind can turn an accepted
     * pattern into a refused one (design §3.3 r4 SND-5), so it waits for
     * [VLOOKBEHIND]'s own row. */
    case A_LOOK:
    /* A call's callee is not walked from here, and that is required: this
     * walk REBUILDS nodes (`pcrec_spine_build`, and the `A_REP`/`A_CAP` arms
     * below allocate a fresh node when the body changes), so reaching the
     * callee through `u.call.body` would rewrite a subtree another part of
     * the tree still points at. The callee's alternations are normalized
     * when the walk reaches the callee at its LEXICAL position, the one
     * place its rebuilt node can be stored back. */
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
    /* An atomic body is not walked: the cut commits to the body's own
     * alternation order (`(?>a|ab)c` and `(?>ab|a)c` answer differently on
     * "abc"), and the owner's rules are argued for an alternation whose
     * branches backtrack freely. Walking into a body the cut does not reorder
     * would be defensible and is [ENG-CUT]'s analysis, not this pass's. */
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
