/* [M4.6d] MINIMUM-REMAINING-LENGTH (MRL) pruning: the minimum-width analysis.
 *
 * docs/design/k23_impl/k23_design.md §4.3, adopted by D51 ruling 1 as K23's
 * fix of record. `pcrec_minw(a)` is the least number of subject bytes any
 * match of `a` can consume. The EMITTER threads it as an accumulator down its
 * own walk (src/gen/emit_vm.c, `Vm.fmin`), so this file owes only the
 * per-node arithmetic; where the numbers are USED, and the lattice rule that
 * makes a clamp sound at stride > 1, live at the emission sites.
 *
 * WHY IT IS A SEPARATE FILE and not four lines inside the emitter: it is an
 * ANALYSIS over the AST, in the same class as possessify.c's and revdet.c's,
 * and it has the same property those two have — an error here is silent. A
 * `minw` that OVER-estimates deletes real matches, and it does so with no
 * compile error, no warning and no failing test unless the corpus happens to
 * contain the shape. It is therefore worth its own file, its own exhaustive
 * switch, and its own test corpus.
 *
 * THE SWITCH IS EXHAUSTIVE WITH NO DEFAULT ARM, and that is a design
 * obligation rather than a style preference (§4.2's failure mode 1, sharpened
 * by R26 V7). A node kind added after this file is written must be a COMPILE
 * ERROR here, not a silent inheritance of whatever a default arm returned.
 * Under -Wswitch (which `make strict` promotes to an error) a new AKind
 * member makes this function fail to build, which is exactly the alarm the
 * analysis cannot otherwise raise.
 *
 * EVERY CONSERVATIVE CASE UNDER-ESTIMATES, which is the safe direction: a
 * bound below the truth prunes less and can never delete a live position.
 *   - `A_CLASS` is 1 byte in BOTH encodings. Exact for ascii, deliberately
 *     LOOSE for utf8, where a class holding only non-ASCII code points really
 *     needs 2 or more (§9.5 keeps the tightening as an unbuilt option).
 *   - the zero-width nodes contribute 0.
 *   - an unbounded `A_REP` contributes `rmin * minw(body)` like any other.
 * Lookaround, backreferences and `(*ATOMIC)` have no producers today; when
 * they gain one, each contributes 0 here until someone measures otherwise,
 * and the exhaustive switch is what forces that decision to be made.
 */

#include <string.h>

#include "core/internal.h"

/* The saturation ceiling. `A_REP` multiplies, and a tower of bounded repeats
 * multiplies repeatedly, so an unsaturated `long long` can overflow — and a
 * WRAPPED product is not merely wrong, it is wrong in the UNSOUND direction
 * whenever it lands on a small positive value that still over-estimates some
 * program point. Saturating instead pins the error to the safe side twice
 * over: the saturated value is BELOW the true minimum (an under-estimate),
 * and it is so far above any addressable subject that the clamp it feeds is
 * simply "this position is doomed", which at 2^40 bytes of remaining subject
 * it certainly is.
 *
 * It is not reachable from anything pcrec compiles today — PCREC_MAX_REP_COUNT
 * bounds one quantifier and the nesting depth bounds the tower — which is
 * precisely why it is written down rather than argued away: the arithmetic
 * must be correct at the boundary nobody is watching.
 *
 * The value itself is PCREC_MINW_MAX in core/internal.h, shared with the
 * emitter's follow-min accumulator: two ceilings would let a long enough
 * concatenation of saturated subtrees overflow past the one that exists to
 * prevent exactly that. */
#define MRL_MINW_MAX PCREC_MINW_MAX

static long long mrl_sat_add(long long a, long long b)
{
    long long r = a + b;
    return r > MRL_MINW_MAX ? MRL_MINW_MAX : r;
}

static long long mrl_sat_mul(long long a, long long b)
{
    if (a <= 0 || b <= 0) return 0;
    if (a > MRL_MINW_MAX / b) return MRL_MINW_MAX;
    return a * b;
}

/* THE C-STACK DEPTH IS Θ(pattern depth), which is the rule K18 actually
 * teaches (k23_design.md §4.3's first bullet, corrected against this note's
 * own refuted prediction 2). `clo_visit` was not a problem because it
 * recursed; it was a problem because it recursed Θ(d²). Two shapes here are
 * NOT bounded by paren depth and are therefore walked ITERATIVELY, for
 * src/ir/nfa.c's R-2 reason: a left-leaning `A_CAT` spine and an `A_CAP`
 * chain are both as long as the pattern, not as deep as its nesting. What
 * remains recursive — an A_CAT's right child, an A_ALT's branches, an A_REP's
 * body — descends one paren level per frame. */
long long pcrec_minw(const Ast *a)
{
    long long acc = 0;

    for (;;) {
        switch (a->k) {
        case A_CLASS:
            return mrl_sat_add(acc, 1);
        case A_EMPTY:
        case A_BOL:
        case A_EOL:
        case A_END:
            return acc;
        case A_CAT:
            acc = mrl_sat_add(acc, pcrec_minw(a->r));
            a = a->l;
            continue;
        case A_CAP:
            a = a->l;
            continue;
        case A_ALT: {
            long long l = pcrec_minw(a->l), r = pcrec_minw(a->r);
            return mrl_sat_add(acc, l < r ? l : r);
        }
        case A_REP:
            /* `rmax == -1` (unbounded) is not special: the MINIMUM is rmin
             * copies whether or not there is a maximum. */
            return mrl_sat_add(acc, mrl_sat_mul(a->rmin, pcrec_minw(a->l)));
        }
        /* No default arm: see the header comment. Reaching here means a new
         * AKind was added and this switch was not extended, which -Wswitch
         * catches at build time; the trap is for a build that suppressed it. */
        return 0;
    }
}
