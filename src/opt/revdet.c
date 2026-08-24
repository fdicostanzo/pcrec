/* The REVERSE-DETERMINISTIC rung's analysis — docs/design/engine_m4.md §2.5,
 * docs/design/eng_brep_design.md §3, and this lane's own emitted-shape sketch
 * at docs/design/rungselect_impl/rungselect_design.md.
 *
 * WHAT IT DECIDES. `X{m,n}` over a body that is variable-length or
 * choice-bearing — so the span-loop cursor cannot have it — may still be
 * emitted as ONE body copy rather than `n` of them, provided the consumed run's
 * decomposition into iterations is UNIQUE and RECOVERABLE FROM THE RIGHT. This
 * pass finds those quantifiers and sets `Ast.u.rep.revbody` to the body's REVERSED
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
        /* [M6.2 wave B] DECLINE, which is always available and always safe.
         * [M6.2 wave D] `\G` declines with them, and it is the least
         * interesting decline in the file: a `\G` inside a quantifier body
         * can be true at most once per search by definition. */
        case A_WORDB: case A_NWORDB: case A_GSTART:
        /* [M6.2 wave E] `\K` declines too, and it is the ONLY member of this
         * list whose decline is a CORRECTNESS requirement rather than a
         * missed optimisation.
         *
         * This rung suppresses the per-iteration capture writes (emit_vm.c's
         * `v->nocap`) and RECOVERS the values afterwards by walking backwards
         * over the iteration BOUNDARIES — §3.4's derivation, which knows
         * where a group opened relative to the start of an iteration. `\K`
         * has no such derivation: its position is wherever the winning path
         * crossed it, which is not a function of the boundary lattice. A
         * suppressed `\K` write is therefore a write that is never recovered,
         * and the artifact would report the wrong start silently.
         *
         * Declining here is what makes that unreachable rather than
         * unlikely: rd_reverse and rd_alt_disjoint below both run only on a
         * body this scan approved. */
        case A_KRESET:
        /* [M6.6.2] DECLINES, and this is the arm the other three in this file
         * rest on: it is what makes them unreachable rather than merely
         * unlikely.
         *
         * The reason is `\K`'s, one construct out. This rung suppresses the
         * per-iteration capture writes and RECOVERS them by walking BACKWARDS
         * over the iteration boundaries (§3.4). A lookaround has no reversed
         * spelling at all: its body runs FORWARD even for a lookbehind
         * (design §3.5 — forward body plus an end-check, not a reverse
         * machine), and its verdict is a property of a sub-match at a position
         * the backward walk is not at. There is nothing on the boundary
         * lattice to recover.
         *
         * Declining costs a quantifier whose body holds a lookaround its
         * one-body-copy lowering, which is always available and always safe:
         * the denied build replicates, and replication is the ground truth. */
        case A_LOOK:
            S->ok = false;
            return;
        /* [DD-14] DECLINES, and like the four arms around it this one is what
         * makes the OTHER three in this file unreachable rather than merely
         * unlikely (design §4.4a sites 14-18).
         *
         * A call is not a revdet-able shape, and the reason is not the
         * lookaround's. This rung recovers an iteration boundary by matching a
         * REVERSED copy of the body from the right; a call's meaning is "run
         * the callee's program, then come back", and the callee is not part of
         * this subtree — it is reached through `u.call.body`, a BACK EDGE that
         * this scan must not follow (design §4.4) and that on a recursive
         * callee names a program with no bounded reversed spelling at all. A
         * `(?1)` in a quantifier body is a hole the boundary lattice cannot
         * see through.
         *
         * DECLINING IS ALWAYS AVAILABLE AND ALWAYS SAFE — this file's own
         * invariant. The denied build replicates, and replication is the
         * ground truth. Sabotage row S-SR16's site. */
        case A_CALL:
            S->ok = false;
            return;
        /* [M6.4.2] DECLINE, and it is an EXPLICIT arm rather than a
         * fallthrough on purpose — see rd_reverse below, where the same
         * omission is a miscompile rather than a missed optimisation.
         *
         * An atomic group is not reversal-invariant. The cut is defined
         * relative to the FORWARD priority order — "whatever the body matches
         * on its OWN first attempt" — and "the body's first success" is not a
         * property a backwards walk can reproduce: this rung recovers an
         * iteration boundary by matching the REVERSED body from the right,
         * which has its own first success at a different place. Declining
         * costs those patterns the rung and is always correct
         * (`revdet.c`'s own invariant: declining is always available and
         * always safe). Sabotage row S94 makes this arm ACCEPT instead. */
        case A_ATOMIC:
            S->ok = false;
            return;
        /* [M6.5.2] DECLINE, and it is an EXPLICIT arm rather than the
         * fall-out below for `A_ATOMIC`'s reason: `rd_reverse` runs only on a
         * body this scan approved, and its fallthrough COPIES, so a decline
         * that is safe only by accident here becomes a miscompile there.
         *
         * WHY IT MUST DECLINE. This rung recovers an iteration boundary by
         * matching the REVERSED body from the right, which requires the body's
         * language to be reversal-expressible from its own text. A
         * backreference's operand is not in its text — it is subject bytes a
         * capture published — and there is no reversed spelling of "compare
         * against what group k captured". Declining costs those bodies the
         * rung and is always correct (this file's own invariant: declining is
         * always available and always safe). Sabotage row S108 makes this arm
         * ACCEPT instead, because the `-Wswitch` alarm that brought a reader
         * here says an arm is MISSING, never which arm is right. */
        case A_BREF:
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
            if (a->u.rep.rmin != a->u.rep.rmax || a->u.rep.rmin < 1) { S->ok = false; return; }
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
     * nothing may read a stale verdict off it.
     *
     * [D70] GUARDED ON THE KIND, and the guard is load-bearing rather than
     * tidy. `rd_node` is the copy constructor for EVERY kind `rd_reverse`
     * handles — A_CLASS, A_EMPTY, the six position predicates, A_CAP, A_REP,
     * A_CAT, A_ALT, plus that function's tail fallthrough — so before the
     * union these two writes landed on nodes of every kind and were simply
     * DEAD for all but A_REP. After it they are writes THROUGH `u.rep` on
     * whatever payload the node actually owns: on an A_CLASS node they
     * overwrite bytes of `u.cls.bits`, i.e. they corrupt the reversed body's
     * class bitmap. The D70 migration survey caught this site; it is the one
     * generic walker in the tree that touched a per-kind field without
     * switching on `k`, and the guard is what makes the refactor
     * behaviour-preserving rather than a miscompiler. */
    if (n->k == A_REP) {
        n->u.rep.revbody = NULL;
        n->u.rep.possessive = false;
    }
    return n;
}

static Ast *rd_reverse(Ctx *cx, const Ast *a)
{
    switch (a->k) {
    case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
    /* [M6.2 wave B] reversal is identity -- the predicate is symmetric in
     * the two bytes it reads (src/ir/nfa.c). [M6.2 wave D] and for `\G`
     * because it is an absolute-position assertion, N_BOT's own reason. */
    case A_WORDB: case A_NWORDB: case A_GSTART:
        return rd_node(cx, a);

    /* [M6.2 wave E] `\K` IS NOT REVERSAL-INVARIANT and must not be given the
     * arm above, which is why it gets an error instead of a copy.
     *
     * The seven kinds above survive reversal because each is a PREDICATE:
     * an absolute-position test means the same thing whichever way the
     * machine walks, and a word boundary's predicate is symmetric in the two
     * bytes it reads. `\K` is not a predicate — it records a position — so
     * mirroring the body would have to mirror where it records, and this
     * function has no notion of that.
     *
     * It is unreachable: rd_shape declines every body carrying one, and this
     * runs only on a body rd_shape approved. Reaching it means that decline
     * was removed, which is a change that MUST be noticed. The fallthrough at
     * the bottom of this function would have copied the node and produced a
     * plausible reversed body that reports the wrong start — the silent
     * outcome this arm exists to replace with a loud one (src/ir/nfa.c's
     * A_CAP arm is the same call). */
    case A_KRESET:
        ctx_fail(cx, 0, "internal error: \\K reached the reverse-deterministic "
                        "body reversal, which its shape scan must decline");

    /* [M6.5.2] `\K`'s treatment for `\K`'s reason, one construct further out.
     * A backreference is not a predicate and not reversal-invariant: it
     * compares subject text against subject text at a pair of positions the
     * FORWARD walk published, and there is no mirrored spelling of that.
     * Unreachable — `rd_shape` declines every body carrying one — and the
     * fallthrough this replaces would have COPIED the node into a reversed
     * body that compares the same span while the walk runs the other way.
     *
     * [M6.6.2] A LOOKAROUND JOINS THEM, and it is the strongest case of the
     * three. `\K` and `A_BREF` are merely not reversal-invariant; a
     * lookaround's body is not even reversed WHEN IT IS EMITTED FORWARD —
     * design §3.5 lowers a LOOKBEHIND as back-step + FORWARD body +
     * end-check, precisely because there is no reverse machine to write it
     * with. Producing a "reversed" A_LOOK here would be inventing a construct
     * that does not exist anywhere in this compiler.
     *
     * Unreachable: `rd_shape` declines every body carrying one (above), and
     * this runs only on a body `rd_shape` approved. The tail fallthrough at
     * the bottom of this function would have COPIED the node — through
     * `rd_node`, whose D70 kind guard means the copy would have kept a valid
     * `u.look` and therefore looked entirely plausible. That is the silent
     * outcome this arm replaces with a loud one.
     *
     * IT GETS ITS OWN `ctx_fail` RATHER THAN JOINING `A_BREF`'s, and the
     * reason is the one this file already applies to `\K` and `A_BREF`
     * separately: an internal error that names the WRONG CONSTRUCT sends the
     * next reader hunting in the wrong file. A shared arm here would have
     * reported "a backreference reached ..." for a lookaround. */
    case A_LOOK:
        ctx_fail(cx, 0, "internal error: a lookaround reached the "
                        "reverse-deterministic body reversal, which its shape "
                        "scan must decline");

    case A_BREF:
        ctx_fail(cx, 0, "internal error: a backreference reached the "
                        "reverse-deterministic body reversal, which its shape "
                        "scan must decline");

    /* [DD-14] THE SAME LOUD REFUSAL, and it gets its OWN `ctx_fail` for the
     * reason this file already applies to `\K`, `A_BREF` and `A_LOOK`
     * separately: an internal error that names the WRONG CONSTRUCT sends the
     * next reader hunting in the wrong file.
     *
     * A "reversed A_CALL" is a construct that exists nowhere in this
     * compiler, and the tail fallthrough is what makes the arm necessary
     * rather than decorative: `rd_node` copies the node and NULLs `l` and
     * `r`, which on an `A_CALL` changes nothing visible at all — `l` and `r`
     * are already unused — so the copy would carry a perfectly valid
     * `u.call` payload and a target the reversed program would then RUN
     * FORWARDS inside a backward walk. That is the most plausible-looking
     * wrong tree in the file.
     *
     * Unreachable: `rd_shape` declines every body carrying a call (above),
     * and this runs only on a body `rd_shape` approved. */
    case A_CALL:
        ctx_fail(cx, 0, "internal error: a subroutine call reached the "
                        "reverse-deterministic body reversal, which its shape "
                        "scan must decline");

    /* [M6.4.2] SAME TREATMENT AS `\K`, AND THE FALLTHROUGH IT REPLACES IS THE
     * MOST DANGEROUS ONE THIS MODULE HAD TO CLOSE.
     *
     * `rd_shape` above declines an atomic body by setting `S->ok = false`, and
     * its switch ends in a fallthrough that does the same — so an unhandled
     * kind there is safe BY ACCIDENT. This function's fallthrough is `rd_node`
     * at the bottom, which copies the node and NULLs `l` and `r`. An unhandled
     * `A_ATOMIC` would therefore have become an EMPTY-BODY ATOMIC GROUP in the
     * reversed body the emitter walks — a plausible-looking tree that matches
     * the wrong language, silently. And `-Wswitch` is only a WARNING on a
     * plain `make` (`-Werror` is `make strict` only, R5-Q1), so the diagnostic
     * that names this site does not by itself stop the build.
     *
     * It is unreachable for the same reason `\K`'s arm is: `rd_shape` declines
     * every body carrying one and this runs only on a body it approved.
     * Reaching it means that decline was removed, which is a change that MUST
     * be noticed loudly rather than compiled into a matcher. */
    case A_ATOMIC:
        ctx_fail(cx, 0, "internal error: an atomic group reached the "
                        "reverse-deterministic body reversal, which its shape "
                        "scan must decline");

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
            memcpy(out, a->u.cls.bits, 32);
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
        /* [DD-14] WIDENS TO ALL BYTES, and it is an EXPLICIT arm rather than
         * a fallthrough into the `default:` below so that the widening is a
         * DECISION on the record (design §4.4a site 16). The value is the same
         * one the default computes; what differs is that a reader of this
         * switch can see that a call was considered.
         *
         * WHY WIDENING IS THE SOUND DIRECTION HERE: this set feeds
         * `rd_alt_disjoint`, and an over-wide FIRST set makes the
         * disjointness test FAIL, which makes the quantifier keep its
         * machinery — always correct. The exact answer (the callee's own
         * FIRST set) needs the call graph and is not worth having: the
         * `A_CALL` arm in `rd_shape` above means no body carrying a call ever
         * reaches this function.
         *
         * IT DOES NOT FOLLOW `u.call.body`, which matters more here than at a
         * decline: this function RECURSES on `A_ALT` branches with no visited
         * set, so a `.body` descent would be design §4.4's hang. */
        case A_CALL:
            memset(out, 0xff, 32);
            return;
        default:
            /* Unreachable on a shape-scanned body; widening to ALL BYTES is
             * the sound direction, because it makes the disjointness test
             * below fail and the quantifier keep its machinery.
             *
             * [M6.2 wave C] ONE OF §8.3's FOUR `default:` SITES, inspected
             * for `Ast.u.anch.multiline` awareness and needing none: widening is
             * opaque to what an assertion means, so it cannot be wrong about
             * WHERE a `$` is true. The full inspection is recorded at the
             * field itself (src/core/internal.h).
             *
             * [M6.6.2] RE-INSPECTED FOR `A_LOOK`, one of the same four sites
             * (design §11's second table), and SOUND for the same reason
             * TWICE OVER. Widening is opaque to what a lookaround asserts, so
             * it cannot be wrong about it; and `rd_shape`'s new A_LOOK arm
             * declines every body carrying one, so this default is not even
             * reachable with a lookaround in hand. Note that this function's
             * own header calls the body reaching it "NON-NULLABLE and
             * assertion-free", which a lookaround is not — that description is
             * a statement of what the shape scan guarantees, so the decline
             * arm is what keeps it true, not this default.
             *
             * [DD-14] RE-INSPECTED BY HAND FOR `A_CALL` (design §4.4a site
             * 16) and SOUND — and unlike the other three `default:` sites
             * this one DID get an explicit arm, immediately above, computing
             * the same value. The arm is there because §4.4a asks for the
             * widening to be a DECISION on the record rather than a
             * fallthrough, not because the default was wrong: widening is
             * opaque to what a call runs, so it cannot be wrong about it, and
             * `rd_shape`'s own `A_CALL` decline means no body carrying one
             * reaches this function at all. The header's "NON-NULLABLE and
             * assertion-free" description of its input is a statement of what
             * the shape scan guarantees; a call is neither, and the decline
             * arm is again what keeps the description true. */
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
        case A_WORDB: case A_NWORDB: case A_GSTART:
            return true;
        /* [M6.2 wave E] `\K` DECLINES rather than joining the row above.
         * Unreachable (rd_shape rejects the body long before this runs), and
         * `false` is the sound direction here in the way `true` is not: a
         * decline keeps the quantifier's machinery, which is always correct,
         * where an approval would hand the emitter a rung whose backward walk
         * has no way to reproduce a `\K` write. */
        /* [M6.5.2] DECLINES with them, same sound direction: a decline keeps
         * the quantifier's machinery, which is always correct, where an
         * approval would hand the emitter a rung whose backward walk cannot
         * reproduce a match-time compare. Unreachable — `rd_shape` rejects
         * the body first. */
        case A_BREF:
        case A_KRESET:
            return false;
        /* [DD-14] DECLINES with them, same sound direction and same reason:
         * `false` keeps the quantifier's machinery, which is always correct,
         * where an approval would hand the emitter a rung whose backward walk
         * cannot reproduce a call at all. Unreachable — `rd_shape` declines
         * every body carrying one. `true` here is the only answer that could
         * be WRONG, and it is the one an accidental fallthrough would have
         * produced if this arm shared the leaf row above. */
        case A_CALL:
            return false;
        /* [M6.4.2] DECLINE, `\K`'s arm for `\K`'s reason: `false` is the sound
         * direction here in the way `true` is not — a decline keeps the
         * quantifier's machinery, which is always correct, where an approval
         * would hand the emitter a rung whose backward walk cannot reproduce
         * the forward cut. Unreachable (rd_shape rejects the body long
         * before), and written out rather than left to the switch's tail
         * because this file's two fallthroughs disagree about what is safe. */
        case A_ATOMIC:
        /* [M6.6.2] DECLINES, A_ATOMIC's arm for A_ATOMIC's reason: `false` is
         * the sound direction here in the way `true` is not. A decline keeps
         * the quantifier's machinery, which is always correct; an approval
         * would hand the emitter a rung whose backward walk cannot reproduce a
         * sub-match verdict. Unreachable (`rd_shape` rejects the body first),
         * and written out rather than left to a fallthrough because this
         * file's two fallthroughs disagree about what is safe. */
        case A_LOOK:
            return false;
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
    if (!in_rep && !(a->u.rep.rmin == 0 && a->u.rep.rmax == 0)) {
        Shape S = { 0, true };
        rd_shape(&S, a->l);
        if (S.ok) {
            const char *why = NULL;
            if (pcrec_uniq_iteration(R->scratch, a->l, &why)) {
                const Ast *rev = rd_reverse(R->cx, a->l);
                if (pcrec_uniq_iteration(R->scratch, rev, &why)
                    && rd_alt_disjoint(rev)) {
                    a->u.rep.revbody = rev;
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
    /* [M6.2 wave E] `\K` joins them here with no caveat: this walk only
     * HUNTS for A_REP nodes to offer the rung to, and a leaf of any kind
     * hosts none. The verdict about `\K` is rd_shape's, one level down.
     * [M6.5.2] `A_BREF` joins for the identical reason. */
    case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET: case A_BREF:
        return;
    /* [M6.6.2] DOES NOT DESCEND, and this is the ONE arm in this file where
     * the decline is a CHOICE rather than a correctness requirement — which is
     * why it is separated from A_ATOMIC's transparent arm below and says so.
     *
     * A_ATOMIC is transparent here because a quantifier that merely SITS
     * INSIDE an atomic group is an ordinary quantifier the emitter still has
     * to lower, and denying it the rung costs a real lowering for no reason.
     * The same argument would apply to a lookaround body — the rung's verdict
     * is local to the quantifier's own decomposition — so descending would
     * probably be sound. It is not taken, for a reason that is about EVIDENCE
     * rather than about the argument: nothing produces an A_LOOK in this wave,
     * so a rung granted inside a lookaround body could not be exercised by any
     * test in the tree, and "probably sound, entirely unmeasured" is the shape
     * this project has been bitten by. Declining is always safe (the denied
     * build replicates, and replication is the ground truth), so the cost is a
     * missed optimisation on a body that does not exist yet.
     *
     * A LATER WAVE MAY MAKE THIS DESCEND once there is a corpus that can go
     * red; the arm is written as a decline so that change is a deliberate one
     * with a measurement behind it. */
    case A_LOOK:
        return;
    /* [DD-14] DOES NOT DESCEND — and unlike `A_LOOK` above, THIS decline is
     * not a choice, because there is nowhere to descend TO. An `A_CALL` has
     * no `l` and no `r`; the callee hangs off `u.call.body`, a back edge that
     * design §4.4 forbids a walk like this one from following. This walk
     * hunts for `A_REP` nodes to offer the rung to, and every `A_REP` in the
     * callee is offered the rung when this same walk reaches the callee at
     * its own lexical position — so following the edge would offer each one
     * the rung TWICE (and never terminate on a recursive callee) for no gain.
     *
     * The verdict ABOUT a call is `rd_shape`'s, one level down, and it is a
     * decline: a quantifier whose body CONTAINS a call gets no rung. */
    case A_CALL:
        return;
    case A_CAP:
    /* [M6.4.2] TRANSPARENT, and NOT the same question the three arms above
     * answer. This walk only HUNTS for A_REP nodes to offer the rung to; the
     * verdict ABOUT an atomic group is `rd_shape`'s, one level down, and it is
     * a decline. A quantifier that merely SITS INSIDE an atomic group is an
     * ordinary quantifier the emitter still has to lower, and denying it the
     * rung here would cost `(?>(?:a|bc)*d)` its one-body-copy lowering for no
     * reason — the outer cut discards the loop's frames at the group's exit
     * either way. */
    case A_ATOMIC:
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
