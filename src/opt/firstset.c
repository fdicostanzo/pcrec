/* [OPT-ALTCLS] STAGE 3 (docs/dev/plan.md's row, "(2b, STAGE 3 ... from the
 * `(?=[a-f])(?:a|...|f)` idea)"): FIRST-SET computation, the analysis half of
 * the entry-guard `src/gen/emit_vm.c`'s `vm_alt` may emit ahead of a branch
 * cascade. STRICTLY MEASURE-AT-BUILD (the row's own posture, D53): this file
 * supplies a SOUND fact the emitter can act on if the pinned measurement
 * says it earns its keep, and a measured-no leaves this file landed but its
 * consumer declining to use it — a legitimate, recordable outcome, not a
 * rollback.
 *
 * THE FACT. `pcrec_firstset(a, out)` fills `out` (a 256-bit byte-membership
 * bitmap, `Ast.cls`'s own shape) with every byte that COULD be the first
 * byte an ACCEPTING match of `a` consumes, and returns true. It returns
 * false (leaving `out` untouched) when the set cannot be bounded below "any
 * byte" — always safe, the declining convention every analysis in this
 * directory follows.
 *
 * WHY THIS NEEDS NO LOOKAHEAD MODULE, which the plan row calls out
 * explicitly: this is not `(?=...)` — nothing is inserted into the AST and
 * no new construct is parsed. It is a compile-time fact about a subtree the
 * emitter already has, planted the way `src/opt/mrl.c`'s `pcrec_minw` plants
 * its bound: computed once, consulted where useful, discarded with the rest
 * of the Job on completion.
 *
 * NULLABILITY IS NOT THIS FILE'S JOB. A node whose `pcrec_minw() == 0` can
 * match the empty string, and composing FIRST across a concatenation needs
 * that fact at every step (a nullable PREFIX means the next atom's own first
 * byte still matters) — `pcrec_minw` (mrl.c) is the one place it is
 * computed, and this file calls it rather than reimplementing a second
 * nullability predicate that could drift from the first (the
 * two-descriptions-of-one-fact shape this project keeps finding).
 *
 * THE A_CAT RULE, worked out once here because it is the one non-obvious
 * step. The spine is LEFT-NESTED (`A_CAT(prefix, last)`, `parse.c`'s own
 * shape), so `FIRST(prefix . last) = FIRST(prefix) ∪ FIRST(last) IF prefix
 * is nullable, else FIRST(prefix) alone` — the textbook rule, but applied at
 * EVERY level as the walk descends `a->l`. It requires no explicit "stop
 * once a mandatory atom is found" flag: `pcrec_minw` is monotone under
 * concatenation (a non-nullable sub-part makes the whole prefix
 * non-nullable, saturated arithmetic included), so the per-level check at
 * each `A_CAT` node cascades to the same answer a global stopping rule
 * would give, one level at a time. Verified by hand against `A_CAT(X1,
 * A_CAT(X2, X3))`-shaped chains where X1 is non-nullable: the top-level
 * check on `pcrec_minw(X1.X2)` already reads non-zero and excludes X3
 * without this file ever needing to ask "is X1 non-nullable" directly.
 *
 * SOUND IN ONE DIRECTION ONLY, the same rule every analysis here follows:
 * this function may OVER-approximate a set (include bytes that can never
 * actually start a match) with no consequence beyond a weaker guard, but
 * must never UNDER-approximate (exclude a byte a real match could start
 * with) — that would delete matches. Anything this file cannot model
 * exactly returns false rather than guess, which is always safe.
 *
 * `A_BOL`/`A_EOL` DECLINE, on purpose and matching precedent rather than
 * unexamined caution. `src/opt/possessify.c`'s own §2.5 refutation records
 * that a zero-width assertion breaks a first-byte-set model when it is
 * REACHED IN THE FOLLOW of a retreat — a different failure shape from this
 * file's simple forward composition, but the safe answer is the same one
 * that file already committed to: an assertion widens to "unknown" rather
 * than being reasoned about specially. Revisit only with the same kind of
 * measurement possessify.c's own conjuncts each earned.
 *
 * RECURSION DISCIPLINE (D10/DD-10/R1 R-2, K20 the third time), and the
 * technique is `src/opt/revdet.c`'s `pcrec_revdet_first` precedent exactly:
 * the OUTER walk down an `A_CAT`/`A_CAP`/`A_REP` chain is a plain loop
 * (`a = a->l; continue;`, no added stack frame — either spine can be as
 * long as the pattern), and the only RECURSIVE calls are into a single
 * ATOM (`A_CAT`'s `a->r`, or one `A_ALT` branch's `t->r`), which is
 * nesting-bounded, the amount K18 already proved safe (Θ(d), not Θ(d²)).
 * Needs no `Ctx`/arena for the identical reason `pcrec_revdet_first`
 * doesn't: nothing here is ever collected into an array.
 */

#include <string.h>

#include "core/internal.h"

static void firstset_or(uint8_t *acc, const uint8_t *bits)
{
    for (int i = 0; i < 32; i++) acc[i] |= bits[i];
}

bool pcrec_firstset(const Ast *a, uint8_t out[32])
{
    uint8_t acc[32] = {0};

    for (;;) {
        switch (a->k) {
        case A_CLASS:
            firstset_or(acc, a->cls);
            memcpy(out, acc, 32);
            return true;

        case A_CAT: {
            /* The prefix (a->l) being nullable is what makes the LAST atom
             * (a->r) reachable as a first byte at all -- see the header's
             * worked derivation for why this per-level check is sufficient
             * with no separate stopping flag. */
            if (pcrec_minw(a->l) == 0) {
                uint8_t rb[32];
                if (!pcrec_firstset(a->r, rb)) return false;
                firstset_or(acc, rb);
            }
            a = a->l;
            continue;
        }

        case A_CAP:
            /* D31 transparency: a capturing group contributes exactly its
             * body's FIRST set, so simply descend. */
            a = a->l;
            continue;

        case A_REP:
            /* rmax == 0 matches only the empty string -- it contributes NO
             * byte of its own (whatever `acc` already holds from atoms to
             * its right in an enclosing A_CAT is the final answer here).
             * Otherwise, whenever this node DOES iterate, its first byte is
             * the body's; rmin plays no role in that set (only in whether
             * zero iterations is ALSO a valid outcome, i.e. nullability,
             * which pcrec_minw already tracks and the A_CAT case above
             * already consults). */
            if (a->rmax == 0) { memcpy(out, acc, 32); return true; }
            a = a->l;
            continue;

        case A_ALT: {
            /* Maximal LEFT-NESTED spine, flattened iteratively -- every
             * branch always contributes regardless of preference, since any
             * one of them could be the match that starts here. */
            uint8_t br[32];
            const Ast *t = a;
            while (t->k == A_ALT) {
                if (!pcrec_firstset(t->r, br)) return false;
                firstset_or(acc, br);
                t = t->l;
            }
            if (!pcrec_firstset(t, br)) return false;
            firstset_or(acc, br);
            memcpy(out, acc, 32);
            return true;
        }

        case A_EMPTY:
            /* Zero-width, contributes no byte of its own. */
            memcpy(out, acc, 32);
            return true;

        case A_BOL:
        case A_EOL:
            /* DECLINE -- see the header's precedent note. */
            return false;
        }
        /* No default arm: see mrl.c's identical rule. A new AKind must be a
         * COMPILE ERROR here under -Wswitch (make strict), not a silent
         * inheritance of whatever a default returned. */
        return false;
    }
}
