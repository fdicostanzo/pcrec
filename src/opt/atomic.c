/* atomic.c — module `atomic-groups`' AST-level pass and its two walks
 * ([M6.4.2], docs/design/atomic_groups_design.md §5.3/§5.4).
 *
 * THREE THINGS LIVE HERE, and they are here together because they are the
 * three questions nothing else in the tree can answer about an `A_ATOMIC`:
 *
 *   pcrec_has_atomic      does this tree still carry a cut?  (H3's predicate)
 *   pcrec_ast_stamped_by  did a given registry row's producer build anything
 *                         in this tree?  (D65's built-status derivation, for
 *                         the rows that reach no doorway)
 *   pcrec_discharge_atomic delete every cut that is PROVABLY a no-op
 *
 * RECURSION DISCIPLINE (D10/DD-10/R1 R-2, and K20 the third time): `A_CAT` and
 * `A_ALT` spines are LEFT-NESTED and as long as the pattern, so every walk
 * below descends a spine ITERATIVELY and recurses only into the items hanging
 * off it, whose depth the parser's group-nesting cap bounds. A
 * 20,000-character pattern segfaulted pcrec once already for want of this.
 *
 * NONE OF THE THREE SWITCHES CARRIES A `default:` — mrl.c:18-24's rule. A node
 * kind added after this file is written must be a COMPILE ERROR at each of
 * them, because "can this construct contain a cut", "can it carry a producer's
 * stamp" and "is it transparent to the discharge" are three questions only the
 * author of the new kind can answer, and inheriting the wrong answer is silent
 * in all three cases. */

#include <string.h>

#include "core/internal.h"

/* ---- has_atomic: H3's predicate, and the free discharge's own postcondition
 *
 * Read at EMISSION (src/gen/emit_vm.c), which is AFTER the discharge has run,
 * so it answers "is there a cut in the artifact" rather than "did the pattern
 * text contain one". That distinction is the whole payoff of running the
 * discharge before engine selection: `[^"]*+"` compiles to a pure DFA with the
 * MRL ceiling intact, and `(?>a|ab)c` is VM-forced with the ceiling off. */
bool pcrec_has_atomic(const Ast *a)
{
    for (;;) {
        switch (a->k) {
        case A_ATOMIC:
            return true;
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
            return false;
        case A_CAP: case A_REP:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                if (pcrec_has_atomic(a->r)) return true;
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                if (pcrec_has_atomic(a->r)) return true;
                a = a->l;
            }
            continue;
        }
        return false;
    }
}

/* ---- stamped_by: "did THIS row's producer build anything here" ------------
 *
 * D65 derives a row's BUILT status by driving the row's own `syntax` through
 * the machinery that would compile it and reading the outcome. For the four
 * DOORWAY kinds that machinery is `doorway_route` + `doorway_call`, and the
 * outcome is an `ExtResult` (src/parse/syntax_dump.c). RK_QUANTSUFFIX reaches
 * no doorway at all — the possessive suffix is a quantifier suffix recognised
 * inside `p_rep`, deliberately — so its rows need a second arm, and this is the
 * signal that arm reads.
 *
 * IT IS THE SR-8 STAMP, NOT A SECOND FACT. `Ast.reg` is written by the
 * producer at construction and by nothing else, so "the row's producer ran" and
 * "a node carries the row" are the same statement. That is what makes the
 * DEFECT verdict reachable rather than decorative: a row whose `syntax` does
 * not actually exercise its own construct parses fine and stamps nothing, and
 * the derivation says DEFECT instead of quietly reporting `built`.
 *
 * Generic in the row, not special-cased to `atomic-groups`: the next
 * non-doorway kind gets this arm for free. */
bool pcrec_ast_stamped_by(const Ast *a, const RegRow *row)
{
    for (;;) {
        if (a->reg == row) return true;
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
            return false;
        case A_CAP: case A_REP: case A_ATOMIC:
            a = a->l;
            continue;
        case A_CAT:
            while (a->k == A_CAT) {
                if (pcrec_ast_stamped_by(a->r, row)) return true;
                a = a->l;
            }
            continue;
        case A_ALT:
            while (a->k == A_ALT) {
                if (pcrec_ast_stamped_by(a->r, row)) return true;
                a = a->l;
            }
            continue;
        }
        return false;
    }
}
