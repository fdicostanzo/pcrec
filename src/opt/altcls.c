/* [OPT-ALTCLS] ALTERNATION -> CLASS NORMALIZATION (docs/dev/plan.md's
 * [OPT-ALTCLS] row). Two stages, both AST-to-AST REWRITES run once,
 * immediately after parse and before everything downstream (engine
 * selection, possessify/revdet/mrl, both machine builds, both emitters) --
 * see internal.h's comment on `pcrec_altcls` for why that placement is load-
 * bearing rather than a style choice.
 *
 * STAGE 1 (single-char merge): `b|c` -> `[bc]`, `[ab]|[cd]` -> `[abcd]`,
 * `b|[cd]` -> `[bcd]`. Merges a maximal ADJACENT run of A_ALT branches that
 * are each a BARE A_CLASS (parse.c normalizes every literal to a singleton
 * class, so a plain-character branch is already an A_CLASS -- see p_cat's
 * "single atom stays bare" shape) into ONE A_CLASS whose bitmap is the
 * union.
 *
 * SOUNDNESS. Each merged branch consumes exactly one byte at the SAME
 * position, so leftmost-first preference AMONG THEM is indistinguishable --
 * same match set, same span. Captures are the one thing that could tell two
 * branches apart at identical span/position, and a captured branch cannot be
 * a bare A_CLASS in the first place: `(b)|c` parses as
 * `A_ALT(A_CAP(A_CLASS b), A_CLASS c)`, and the A_CAP node is what stops the
 * bare-A_CLASS test from matching it. So "bare A_CLASS" is not merely a
 * convenient predicate, it is the exact boundary the soundness argument
 * needs. Preference relative to UNMERGED (non-class) branches is preserved
 * by only ever merging ADJACENT runs in place -- a merged class occupies
 * exactly the branch-order SLOT its first member held, so a branch before or
 * after the run is never reordered past it.
 *
 * STAGE 2 (prefix factoring): `frank|fred` -> `fr(?:ank|ed)`,
 * `frank|fred|brad|bobby|janet` -> `fr(?:ank|ed)|b(?:rad|obby)|janet`.
 * Measured worth it 2026-08-17 (docs/dev/plan.md's row). PINNED
 * RE-MEASUREMENT (2026-08-18, docs/design/altcls_pinned_impl/): -7.61%
 * (n=27, best-of-9 x 3 interleaved rounds) on the quantified-form exemplar
 * over 30 concatenated names -- the number of record, superseding the
 * design-evening probe's unarchived -15.0..-15.6% figure (direction
 * confirmed, magnitude not reproduced; see the archive for what was and
 * was not tried closing the gap). Runs on STAGE 1's output (the interaction the
 * plan row calls out: "post-merge shapes re-enter possessify/MRL/counter
 * analyses ... so the pass runs before those" applies one level up too --
 * factoring a run that stage 1 already collapsed into one class has nothing
 * left to factor, which is the correct outcome, not a special case).
 *
 * SOUNDNESS. `frank|fred` and `fr(?:ank|ed)` accept the same strings by
 * construction: concatenation and alternation over BYTE-DISJOINT AST nodes
 * distribute exactly like `fr(ank|ed)` distributes algebraically over
 * `frank|fred` -- extracting a literal byte both branches start with and
 * factoring the remainder changes nothing about which strings are accepted
 * or their span, ONLY the shape of the automaton built from them. Preference
 * is preserved because grouping is, again, over a maximal ADJACENT run in
 * branch order, and within a group the remainders keep the SAME relative
 * order the original branches held (`cur[i]` tracks `branches[k+i]`
 * throughout `altcls_extend_prefix`/`altcls_factor_run`, never resorted).
 * NO NEW CAPTURING GROUPS are ever introduced -- this file allocates
 * A_CLASS/A_CAT/A_ALT/A_EMPTY nodes only, never A_CAP, so "the automatic
 * pass must emit non-capturing groups or it changes the group count" (the
 * plan row's own obligation) is discharged BY CONSTRUCTION: there is no AST
 * node for a non-capturing group in this tree at all (`(?:...)` is already
 * transparent at parse time -- see parse.c's PARSE-1 section), so factoring
 * simply never touches `Ctx.ncap` or emits the one node kind that would.
 *
 * THE GENERALIZATION LADDER'S BOUNDARY (docs/dev/plan.md, same row):
 * per-position class merging of MULTI-char branches is UNSOUND in general
 * (`frank|fred` -> `fr[ae][nd]k?` accepts cross-products it must not), which
 * is exactly why stage 2 is PREFIX FACTORING -- a correlation-preserving
 * rewrite -- rather than a wider class merge. The grouping key below is
 * deliberately narrow (a SINGLE literal byte, i.e. an A_CLASS with exactly
 * one bit set) rather than "the same class," which keeps the soundness
 * argument the simple distributive one above; a branch whose first atom is
 * a wider class, or anything other than a flat concatenation of A_CLASS
 * atoms (a nested alternation, a quantifier, a capturing group, an anchor),
 * is simply not a factoring candidate at that position -- it DECLINES, which
 * is always safe, and is passed through unchanged.
 *
 * RECURSION DISCIPLINE (D10/DD-10/R1 R-2, K20 the third time -- A_CAT/A_ALT
 * spines are LEFT-NESTED and can be as long as the pattern). Both stages
 * walk the ALTERNATION spine and each branch's CONCATENATION spine
 * ITERATIVELY. Stage 2's `altcls_extend_prefix` is the one place a naive
 * version of this file would have recursed once per shared PREFIX BYTE
 * (`frank|fred|frank2|fred2|...` sharing a long common run) -- that axis is
 * pattern-length-shaped, not branch-count-shaped, so it is an iterative loop
 * here. `altcls_factor_run`'s own recursion is on SPLIT depth (how many
 * times a group's branches fork into further sub-groups), which is
 * branch-count-shaped and bounded by `PCREC_MAX_ALTCLS_FACTOR_DEPTH`
 * (core/limits.h) -- exceeding it DECLINES the remaining sub-groups rather
 * than refusing the compile, the same safe-fallback shape the possessify/
 * revdet caps use.
 *
 * D46 (docs/dev/decisions.md): both stages are independently gated
 * (`PCREC_NO_ALTCLS_MERGE`/`PCREC_NO_ALTCLS_FACTOR`, lib/pcrec.h) and
 * independently stamped (`<PREFIX>_ALTCLS_MERGES`/`<PREFIX>_ALTCLS_FACTORED`,
 * src/gen/emit_dfa.c's `pcrec_emit_prologue` -- shared by both emitters,
 * since this pass runs before either engine exists, unlike possessify/
 * revdet's VM-only marks). See internal.h's declaration comment and
 * lib/pcrec.h's flag comments for the DENY-vs-FORCE shape argument; this
 * file only needs to know that a denied stage's counter stays at 0, which
 * both stages achieve by checking the flag before touching the counter at
 * all rather than computing-then-discarding.
 *
 * Tests: tests/altcls/. Sabotage: tests/mech/sabotages/ (S66/S67). */

#include <string.h>

#include "core/internal.h"

static Ast *altcls_walk(Ctx *cx, Ast *a);

/* ---- shared spine/rebuild helpers -------------------------------------- */

/* Flatten a (possibly trivial) LEFT-NESTED A_CAT spine into an ordered,
 * left-to-right atom array. A non-A_CAT node is a length-1 spine of itself.
 * Iterative (D10/DD-10/K20): the spine can be as long as the pattern. */
static size_t altcls_cat_flatten(Ctx *cx, Ast *a, Ast ***out)
{
    size_t n = 1;
    for (Ast *t = a; t->k == A_CAT; t = t->l) n++;
    Ast **arr = arena_alloc(&cx->arena, n * sizeof(Ast *));
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

static Ast *altcls_class_from_bits(Ctx *cx, const uint8_t bits[32])
{
    Ast *c = pcrec_ast_node(cx, A_CLASS);
    memcpy(c->u.cls.bits, bits, 32);
    return c;
}

/* Exactly one bit set in a 256-bit class bitmap -> that byte value; -1
 * otherwise (empty, or more than one byte can start this branch). */
static int altcls_single_bit(const uint8_t cls[32])
{
    int found = -1;
    for (int byte = 0; byte < 32; byte++) {
        uint8_t v = cls[byte];
        if (!v) continue;
        if (v & (uint8_t)(v - 1)) return -1;   /* >1 bit in this byte */
        if (found >= 0) return -1;             /* a bit already found elsewhere */
        found = byte * 8 + __builtin_ctz((unsigned)v);
    }
    return found;
}

/* A branch is PEELABLE when its first atom (the flattened spine's element 0)
 * is a bare A_CLASS holding exactly one byte -- a single literal character.
 * On success, `*byte0_out` is that byte and `*rest_out` is the branch with
 * its first atom removed (A_EMPTY if nothing remains). Any other shape --
 * a wider class, an A_REP/A_ALT/A_CAP/A_BOL/A_EOL/A_EMPTY leading atom --
 * DECLINES (returns false), which stage 2 treats as "not a factoring
 * candidate here," always safe. */
static bool altcls_branch_peel(Ctx *cx, Ast *branch, int *byte0_out, Ast **rest_out)
{
    Ast **arr;
    size_t n = altcls_cat_flatten(cx, branch, &arr);
    if (arr[0]->k != A_CLASS) return false;
    int bit = altcls_single_bit(arr[0]->u.cls.bits);
    if (bit < 0) return false;
    *byte0_out = bit;
    *rest_out = altcls_rebuild_cat(cx, arr + 1, n - 1);
    return true;
}

/* ---- stage 2: prefix factoring ----------------------------------------- */

static Ast *altcls_factor_run(Ctx *cx, Ast **branches, size_t n, int depth);

/* Grows a group's shared literal prefix ITERATIVELY as far as every one of
 * the `n` members keeps agreeing on the next byte (D10/DD-10: prefix LENGTH
 * is pattern-shaped, not branch-shaped, so this axis must not cost a stack
 * frame per byte -- see the file header). `cur` is both input (the group,
 * in original branch order) and output (each member's remainder once the
 * whole shared prefix is removed). Returns the prefix itself, rebuilt as an
 * A_CAT chain of single-byte classes; the caller already knows `n >= 2` and
 * that `cur[0]`/`cur[1]` agree on at least one byte, so the returned prefix
 * is never empty. */
static Ast *altcls_extend_prefix(Ctx *cx, Ast **cur, size_t n)
{
    Ast **prefix = NULL;
    size_t plen = 0, pcap = 0;

    for (;;) {
        int byte0;
        Ast *rest0;
        if (!altcls_branch_peel(cx, cur[0], &byte0, &rest0)) break;

        Ast **next = arena_alloc(&cx->arena, n * sizeof(Ast *));
        next[0] = rest0;
        bool all_agree = true;
        for (size_t i = 1; i < n; i++) {
            int bytei;
            Ast *resti;
            if (!altcls_branch_peel(cx, cur[i], &bytei, &resti) || bytei != byte0) {
                all_agree = false;
                break;
            }
            next[i] = resti;
        }
        if (!all_agree) break;

        if (plen == pcap) {
            size_t ncap = pcap ? pcap * 2 : 4;
            Ast **grown = arena_alloc(&cx->arena, ncap * sizeof(Ast *));
            if (prefix) memcpy(grown, prefix, plen * sizeof(Ast *));
            prefix = grown;
            pcap = ncap;
        }
        uint8_t bits[32] = {0};
        cls_set(bits, (unsigned)byte0);
        prefix[plen++] = altcls_class_from_bits(cx, bits);

        for (size_t i = 0; i < n; i++) cur[i] = next[i];
    }
    return altcls_rebuild_cat(cx, prefix, plen);
}

/* Partitions `branches` (already stage-1-merged and, for each branch, walked
 * by the caller) into maximal ADJACENT runs sharing a first literal byte,
 * factors each run of size >= 2, and rebuilds the alternation. `depth`
 * counts SPLITS -- how many times a group's members forked into further
 * sub-groups -- capped at PCREC_MAX_ALTCLS_FACTOR_DEPTH; past the cap the
 * remaining sub-groups DECLINE (stay unfactored), never a refusal. */
static Ast *altcls_factor_run(Ctx *cx, Ast **branches, size_t n, int depth)
{
    if (n == 0) return pcrec_ast_node(cx, A_EMPTY);
    if (n == 1) return branches[0];
    if (depth >= PCREC_MAX_ALTCLS_FACTOR_DEPTH)
        return altcls_rebuild_alt(cx, branches, n);

    int *byte0 = arena_alloc(&cx->arena, n * sizeof(int));
    bool *peeled = arena_alloc(&cx->arena, n * sizeof(bool));
    for (size_t i = 0; i < n; i++) {
        Ast *rest_unused;
        peeled[i] = altcls_branch_peel(cx, branches[i], &byte0[i], &rest_unused);
    }

    Ast **out = arena_alloc(&cx->arena, n * sizeof(Ast *));
    size_t m = 0, k = 0;
    while (k < n) {
        if (peeled[k]) {
            size_t j = k + 1;
            while (j < n && peeled[j] && byte0[j] == byte0[k]) j++;
            if (j - k >= 2) {
                size_t grp = j - k;
                Ast **cur = arena_alloc(&cx->arena, grp * sizeof(Ast *));
                memcpy(cur, branches + k, grp * sizeof(Ast *));
                Ast *prefix = altcls_extend_prefix(cx, cur, grp);
                Ast *tail = altcls_factor_run(cx, cur, grp, depth + 1);
                Ast *cat = pcrec_ast_node(cx, A_CAT);
                cat->l = prefix;
                cat->r = tail;
                out[m++] = cat;
                cx->job->altcls_factored++;
                k = j;
                continue;
            }
        }
        out[m++] = branches[k];
        k++;
    }
    return altcls_rebuild_alt(cx, out, m);
}

/* ---- stage 1 + dispatch ------------------------------------------------- */

static Ast *altcls_walk_alt(Ctx *cx, Ast *a)
{
    /* Flatten the maximal LEFT-NESTED A_ALT spine. Transparent non-capturing
     * groups keep this flat across parens too -- `(?:a|b)|c` parses
     * IDENTICALLY to `a|b|c`, since `(?:...)` produces no wrapper node
     * (parse.c PARSE-1) -- so one flatten here reaches every branch a
     * capturing group does not wall off. */
    size_t n = 1;
    for (Ast *t = a; t->k == A_ALT; t = t->l) n++;
    Ast **br = arena_alloc(&cx->arena, n * sizeof(Ast *));
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

    if (!(cx->opt->flags & PCREC_NO_ALTCLS_MERGE)) {
        Ast **out = arena_alloc(&cx->arena, n * sizeof(Ast *));
        size_t m = 0, k = 0;
        while (k < n) {
            if (br[k]->k == A_CLASS) {
                size_t j = k + 1;
                while (j < n && br[j]->k == A_CLASS) j++;
                if (j - k >= 2) {
                    uint8_t bits[32];
                    memcpy(bits, br[k]->u.cls.bits, 32);
                    for (size_t x = k + 1; x < j; x++)
                        for (int b = 0; b < 32; b++) bits[b] |= br[x]->u.cls.bits[b];
                    out[m++] = altcls_class_from_bits(cx, bits);
                    cx->job->altcls_merges++;
                    any_rewritten = true;
                    k = j;
                    continue;
                }
            }
            out[m++] = br[k];
            k++;
        }
        br = out;
        n = m;
    }

    if (!(cx->opt->flags & PCREC_NO_ALTCLS_FACTOR)) {
        size_t before = (size_t)cx->job->altcls_factored;
        Ast *factored = altcls_factor_run(cx, br, n, 0);
        if ((size_t)cx->job->altcls_factored != before) any_rewritten = true;
        return factored;
    }

    if (!any_rewritten) return a;   /* both stages declined; no trace */
    return altcls_rebuild_alt(cx, br, n);
}

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
    case A_BOL:
    case A_EOL:
    case A_END:
    /* [M6.2 wave B] zero-width, so there is nothing for either stage to
     * merge or factor -- the same answer A_BOL/A_EOL/A_END already give. */
    case A_WORDB:
    case A_NWORDB:
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

Ast *pcrec_altcls(Ctx *cx, Ast *root)
{
    return altcls_walk(cx, root);
}
