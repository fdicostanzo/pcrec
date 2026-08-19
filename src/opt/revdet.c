/* The REVERSE-DETERMINISTIC rung's analysis — docs/design/engine_m4.md §2.5,
 * docs/design/eng_brep_design.md §3, and this lane's own emitted-shape sketch
 * at docs/design/rungselect_impl/rungselect_design.md.
 *
 * WHAT IT DECIDES. `X{m,n}` over a body that is variable-length or
 * choice-bearing — so the span-loop cursor cannot have it — may still be
 * emitted as ONE body copy rather than `n` of them, provided the consumed run's
 * decomposition into iterations is UNIQUE and RECOVERABLE FROM THE RIGHT. This
 * pass finds those quantifiers and sets `Ast.revbody` to the body's REVERSED
 * AST; src/gen/emit_vm.c is what acts on the mark, and the reversed AST is also
 * the thing it emits the backward walk from. One field, so the verdict and the
 * material for it cannot disagree.
 *
 * THE RULE IS TWO UNIQUE-ITERATION CHECKS, NOT ONE, and each has a witness:
 *
 *   FORWARD — the body admits a unique iteration ((U1) one-unambiguous, (U2)
 *   prefix-free, non-nullable). This is what makes the emitted forward scan
 *   deterministic: from any boundary at most one iteration can run and it has
 *   exactly one end, so the boundary chain from the loop's entry is DETERMINED.
 *   It is eng_brep_design.md §2.3's own chain, and it is why the emitter may
 *   CUT the body's choice points at every iteration boundary. Witness for its
 *   necessity: `(aa?)` — §2.5's own counterexample — fails (U2), because its
 *   accepting position `a` (with `a?` empty) has an outgoing edge.
 *
 *   REVERSE — the REVERSED body admits a unique iteration too. This is what
 *   makes the retreat computable LOCALLY: from a boundary `q` there is at most
 *   one `p` with the body matching `[p,q)`, so a backward walk necessarily
 *   lands on the chain's own predecessor rather than on some other
 *   decomposition. Witness for its necessity: `(?:ab|b)` passes FORWARD (its
 *   initial positions `a` and `b` are byte-disjoint and neither accepting
 *   position continues) and fails REVERSE, because reversed it is `(?:ba|b)`
 *   whose two initial positions are both `b`. That is not a modelling
 *   artifact — on "abab" the boundaries are 0,2,4 and a backward walk from 4
 *   can genuinely stop at 3 (branch `b`) or at 2 (branch `ab`).
 *
 * The forward predicate is IMPORTED from src/opt/possessify.c
 * (`pcrec_uniq_iteration`) rather than reimplemented. Every conjunct in it is a
 * refutation somebody measured, and a second copy of that rule is the worst
 * place in this tree to keep two sources of truth.
 *
 * EVERY DECISION IS IN THE SOUND DIRECTION. Anything this pass cannot model
 * DECLINES, and a declined quantifier keeps exactly the machinery it has today
 * and matches exactly what it matches today. That is the invariant to preserve
 * when extending this file, and it is also why `-fno-revdet` is
 * byte-identity-safe: denying the pass leaves every node in the state the arena
 * zeroed it into.
 *
 * RECURSION DISCIPLINE (D10/DD-10/R1 R-2, and K20 the third time). A_CAT and
 * A_ALT spines are LEFT-NESTED and as long as the pattern, so both walks here
 * descend a spine ITERATIVELY and recurse only into the items hanging off it,
 * whose depth the parser's group-nesting cap bounds. The REVERSAL has the same
 * obligation and it is the harder half, because reversing a spine means
 * rebuilding one — see `rd_reverse`.
 */

#include <string.h>

#include "core/internal.h"
#include "core/limits.h"

/* ---- the shape scan ------------------------------------------------------
 *
 * Three of the rung's scope bounds are decided here rather than by the
 * automaton tests, because they are about what the BACKWARD EMITTER can
 * reproduce rather than about ambiguity. Each is a decline, so each costs a
 * shape and risks nothing.
 *
 *   - AN ASSERTION IN THE BODY declines. The Glushkov construction models
 *     `^`/`$` as absent, which possessify.c argues is sound in the direction a
 *     FORWARD-only claim needs (dropping an assertion over-approximates, and
 *     both (U1) and (U2) are inherited downward). That argument is not
 *     re-derived here for a walk that runs backward, so the shape declines
 *     rather than inheriting a proof about the other direction.
 *   - A NESTED QUANTIFIER declines unless its count is EXACT and positive. A
 *     fixed count is literal replication, which the backward emitter mirrors by
 *     emitting the reversed sub-body that many times. A ranged or unbounded one
 *     would need the backward emitter to reproduce a second whole ladder.
 *   - MORE THAN PCREC_MAX_REVDET_BODY_GROUPS capturing groups declines,
 *     because the capture recovery holds one span pair and one seen-flag per
 *     body group in emitted LOCALS. Same bound and same reason as the cursor
 *     rung's VM_MAX_BODY_CAPS: a group the table could not hold would report
 *     UNSET on a match it participated in, which is a silent wrong span.
 */
typedef struct {
    int  ngroups;
    bool ok;
} Shape;

static void rd_shape(Shape *S, const Ast *a)
{
    for (;;) {
        if (!S->ok) return;
        switch (a->k) {
        case A_CLASS:
            return;
        case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        /* [M6.2 wave B] DECLINE, which is always available and always safe. */
        case A_WORDB: case A_NWORDB:
            S->ok = false;
            return;
        case A_CAP:
            /* One entry per capno, not per emitted instance: a fixed-count
             * repeat around a group emits the group several times and they all
             * share one number and one pair of slots. */
            if (++S->ngroups > PCREC_MAX_REVDET_BODY_GROUPS) { S->ok = false; return; }
            a = a->l;
            continue;
        case A_REP:
            if (a->rmin != a->rmax || a->rmin < 1) { S->ok = false; return; }
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                rd_shape(S, a->r);
                if (!S->ok) return;
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                rd_shape(S, a->r);
                if (!S->ok) return;
                a = a->l;
            }
            continue;
        }
        S->ok = false;
        return;
    }
}

/* ---- reversal ------------------------------------------------------------
 *
 * The reversed AST of `X` is the AST whose language is `X` read right to left.
 * Only concatenation is asymmetric: `A_CAT`'s two children swap, recursively.
 * `A_ALT` keeps its branch order (branch order is PREFERENCE, and this tree is
 * only ever matched by an unambiguous walk where at most one branch can
 * succeed, but preserving it costs nothing and keeps the two trees readable
 * side by side). `A_CAP` keeps its number; the backward emitter is what knows
 * that a group's END is met before its START going that way. A fixed-count
 * `A_REP` keeps its count, since replicating a reversed body reverses the
 * replication.
 *
 * BOTH SPINES ARE REBUILT ITERATIVELY. A recursive `n->l = rev(a->r); n->r =
 * rev(a->l)` would recurse once per spine element, which is the K20 stack
 * overflow this project has now paid for three times — and a quantifier body IS
 * allowed to be a 20,000-element concatenation. So each spine is collected into
 * an arena array first and folded back into a left-nested chain, with recursion
 * only into the ITEMS, whose depth the parser's 250-group cap bounds.
 */
static Ast *rd_node(Ctx *cx, const Ast *src)
{
    Ast *n = arena_alloc(&cx->arena, sizeof *n);
    *n = *src;
    n->l = n->r = NULL;
    /* The copy is walk material, never a rung host: nothing analyses it and
     * nothing may read a stale verdict off it. */
    n->revbody = NULL;
    n->possessive = false;
    return n;
}

static Ast *rd_reverse(Ctx *cx, const Ast *a)
{
    switch (a->k) {
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    /* [M6.2 wave B] reversal is identity -- the predicate is symmetric in
     * the two bytes it reads (src/ir/nfa.c). */
    case A_WORDB: case A_NWORDB:
        return rd_node(cx, a);

    case A_CAP: case A_REP: {
        Ast *n = rd_node(cx, a);
        n->l = rd_reverse(cx, a->l);
        return n;
    }
    case A_CAT: case A_ALT: {
        const AKind kind = a->k;
        int n = 1;
        for (const Ast *t = a; t->k == kind; t = t->l) n++;
        const Ast **item = arena_alloc(&cx->arena, (size_t)n * sizeof *item);
        /* Walking a left-nested spine from the top visits the elements in
         * REVERSE text order, so `item[]` comes out reversed for free — which
         * is exactly what A_CAT wants and exactly what A_ALT must undo. */
        int i = 0;
        const Ast *t = a;
        while (t->k == kind) { item[i++] = t->r; t = t->l; }
        item[i] = t;                                  /* the spine's head */

        Ast *acc;
        if (kind == A_CAT) {
            acc = rd_reverse(cx, item[0]);            /* the LAST element first */
            for (int j = 1; j <= n - 1; j++) {
                Ast *c = rd_node(cx, a);
                c->l = acc;
                c->r = rd_reverse(cx, item[j]);
                acc = c;
            }
        } else {
            acc = rd_reverse(cx, item[n - 1]);        /* branch 1, the head */
            for (int j = n - 2; j >= 0; j--) {
                Ast *c = rd_node(cx, a);
                c->l = acc;
                c->r = rd_reverse(cx, item[j]);
                acc = c;
            }
        }
        return acc;
    }
    }
    return rd_node(cx, a);
}

/* ---- FIRST, and the property the BACKWARD EMITTER actually depends on ----
 *
 * The emitted backward walk has NO choice points: at an alternation it reads
 * the next byte and jumps straight to the one branch that can begin with it.
 * That is a strictly stronger thing to rely on than "the walk lands in the
 * right place", and it deserves to be CHECKED WHERE IT IS USED rather than
 * inherited from a proof three functions away.
 *
 * It IS implied by (U1): one-unambiguity says at most one position is live
 * after any prefix, so an alternation's branches cannot share a first byte —
 * at the top level that is the initial-position clause and inside the body it
 * is the follow-set clause. But "implied by" is how a dependency quietly
 * survives a change to the thing it depends on, so `rd_alt_disjoint` re-derives
 * it directly on the reversed tree the emitter will walk, and a failure
 * DECLINES like every other failure here.
 *
 * FIRST is simple on this restricted tree because every body that reaches here
 * is NON-NULLABLE and assertion-free: no nullability propagation, no widening
 * cases, and a concatenation's first set is its leftmost element's. */
void pcrec_revdet_first(const Ast *a, uint8_t *out)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS:
            memcpy(out, a->cls, 32);
            return;
        case A_CAP: case A_REP:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) a = a->l;   /* the leftmost element */
            continue;
        case A_ALT: {
            uint8_t acc[32], br[32];
            memset(acc, 0, 32);
            const Ast *t = a;
            while (t->k == A_ALT) {
                pcrec_revdet_first(t->r, br);
                for (int i = 0; i < 32; i++) acc[i] |= br[i];
                t = t->l;
            }
            pcrec_revdet_first(t, br);
            for (int i = 0; i < 32; i++) acc[i] |= br[i];
            memcpy(out, acc, 32);
            return;
        }
        default:
            /* Unreachable on a shape-scanned body; widening to ALL BYTES is
             * the sound direction, because it makes the disjointness test
             * below fail and the quantifier keep its machinery.
             *
             * [M6.2 wave C] ONE OF §8.3's FOUR `default:` SITES, inspected
             * for `Ast.multiline` awareness and needing none: widening is
             * opaque to what an assertion means, so it cannot be wrong about
             * WHERE a `$` is true. The full inspection is recorded at the
             * field itself (src/core/internal.h). */
            memset(out, 0xff, 32);
            return;
        }
    }
}

static bool rd_alt_disjoint(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB:
            return true;
        case A_CAP: case A_REP:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                if (!rd_alt_disjoint(a->r)) return false;
                a = a->l;
            }
            continue;
        case A_ALT: {
            uint8_t seen[32], br[32];
            memset(seen, 0, 32);
            /* Pairwise disjointness checked INCREMENTALLY against the union of
             * the branches already seen — the same shape, and for the same
             * reason, as possessify.c's `funion`/`fconflict` pair. */
            for (const Ast *t = a;; t = t->l) {
                const Ast *br_ast = (t->k == A_ALT) ? t->r : t;
                if (!rd_alt_disjoint(br_ast)) return false;
                pcrec_revdet_first(br_ast, br);
                for (int i = 0; i < 32; i++) {
                    if (seen[i] & br[i]) return false;
                    seen[i] |= br[i];
                }
                if (t->k != A_ALT) break;
            }
            return true;
        }
        }
        return false;
    }
}

/* ---- the walk ------------------------------------------------------------ */

typedef struct {
    Ctx  *cx;
    void *scratch;     /* one Glushkov workspace for the whole pass */
    int   marked;
} Rd;

static void rd_walk(Rd *R, Ast *a, bool in_rep);

static void rd_rep(Rd *R, Ast *a, bool in_rep)
{
    /* SINGLE LEVEL ONLY. A rung-selected quantifier nested inside another
     * quantifier's body stays on frames: eng_brep_design.md §8 item 4 names
     * nested bounded repeats as the largest unexplored corner, and §3.4's
     * capture derivation — which this rung's backward walk implements — is
     * explicitly single-level. Taken as a scope bound, not argued. */
    if (!in_rep && !(a->rmin == 0 && a->rmax == 0)) {
        Shape S = { 0, true };
        rd_shape(&S, a->l);
        if (S.ok) {
            const char *why = NULL;
            if (pcrec_uniq_iteration(R->scratch, a->l, &why)) {
                const Ast *rev = rd_reverse(R->cx, a->l);
                if (pcrec_uniq_iteration(R->scratch, rev, &why)
                    && rd_alt_disjoint(rev)) {
                    a->revbody = rev;
                    R->marked++;
                }
            }
        }
    }
    rd_walk(R, a->l, true);
}

static void rd_walk(Rd *R, Ast *a, bool in_rep)
{
    switch (a->k) {
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    case A_WORDB: case A_NWORDB:
        return;
    case A_CAP:
        rd_walk(R, a->l, in_rep);
        return;
    case A_REP:
        rd_rep(R, a, in_rep);
        return;
    case A_CAT:
        while (a->k == A_CAT) { rd_walk(R, a->r, in_rep); a = a->l; }
        rd_walk(R, a, in_rep);
        return;
    case A_ALT:
        while (a->k == A_ALT) { rd_walk(R, a->r, in_rep); a = a->l; }
        rd_walk(R, a, in_rep);
        return;
    }
}

int pcrec_revdet(Ctx *cx, Ast *root)
{
    Rd R;
    memset(&R, 0, sizeof R);
    R.cx = cx;
    R.scratch = pcrec_uniq_scratch(cx);
    rd_walk(&R, root, false);
    return R.marked;
}
