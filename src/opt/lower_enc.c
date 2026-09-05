/* lower_enc.c — [M5.0] THE ENCODING LOWERING: the pass that turns a tree of
 * CODE-POINT classes into a tree the byte tier can express, and the one place
 * in this compiler that knows how an encoding spells a character.
 *
 * Design: docs/design/utf8_design.md §2.1 (where it runs and why), §2.1.2 (the
 * position, DERIVED from three ordering constraints rather than chosen),
 * §2.1.4 (the render helper this pass makes safe), §2.3 (stage 2's byte-
 * sequence construction, not here yet).
 *
 * ============================================================================
 * WHAT IT DOES TODAY, AND WHAT THAT IS NOT
 * ============================================================================
 *
 * STAGE 1 SHIPS THE BYTE INSTANCE ONLY. Under `--encoding=byte` a code point
 * IS a byte, so "render the interval list back to the confined form" is the
 * identity on a list already inside `[0, 0xFF]` — and the pass is therefore a
 * walk that CHECKS that confinement and publishes the tree unchanged. That is
 * not a placeholder and it is not dead structure: the check is the byte
 * backend's half of §2.1's rule ("anything touching above 0xFF is a compile
 * error"), and stage 2's `utf8` instance replaces the check on ITS side of the
 * same rule with §2.3's decomposition, at this same line, with this same
 * signature.
 *
 * THE ERROR IS UNREACHABLE IN STAGE 1, DELIBERATELY AND VERIFIABLY. Nothing
 * can put a code point above 0xFF into a class under `byte`: the two producers
 * that could — an explicit `\x{...}`/`\o{...}` value, and a range endpoint —
 * are range-checked on the parser's LITERAL INPUT (§2.7.3), and a COMPLEMENT
 * cannot reach past `PcrecEnc.max_cp`, which is 0xFF for this backend. So the
 * arm below is the assertion that those two facts stay true, in the one place
 * that would notice them stopping.
 *
 * ============================================================================
 * THE POSITION IS A REVIEWABLE FACT (§13 obligation 4)
 * ============================================================================
 *
 * `pcrec_lower_enc` runs at `src/core/compile.c:1000`, between
 * `pcrec_postresolve` and the guarded `pcrec_build_nfa`, and that line is
 * FORCED by three ordering constraints that together admit exactly one slot:
 *
 *   1. IT MUST RUN BEFORE `pcrec_build_nfa` (:1018) AND BEFORE
 *      `pcrec_emit_vm` (:1228). Those are the two consumers that can only
 *      express bytes, and the second one is handed the AST ROOT rather than
 *      the IR — which is why "between the parser and the IR" is not a
 *      position at all for the VM half of this compiler.
 *   2. IT MUST RUN AFTER `pcrec_callgraph_build` (:961). That pass is the
 *      only writer of `Ast.u.call.body`, and `.body` caches "which subtree is
 *      that group's, IN THE TREE THE EMITTER WILL WALK" — so it must run
 *      after the last pass that REBUILDS a node, and this pass will be exactly
 *      such a pass the moment stage 2's decomposition replaces an `A_CLASS`
 *      with an `A_CAT`/`A_ALT` of byte-range classes. Lowering immediately
 *      after the parser is the attractive position this constraint kills.
 *   3. IT MUST RUN AFTER `pcrec_postresolve` (:999). That pass asks module
 *      `lookaround`'s fixed-width rule in CHARACTERS; after the lowering a
 *      two-byte character is an `A_CAT` of two byte classes, and a
 *      character-width walk over a lowered tree would answer 2 where the
 *      truth is 1.
 *
 * CONSTRAINT 2 WAS CONFIRMED EMPIRICALLY RATHER THAN INHERITED, because the
 * design rests it on `compile.c:947-956`'s comment and a comment is not a
 * check. The experiment (this wave, docs/dev/lanes/utf8s1_report.md): move the
 * call above :961 in a scratch build and compile a call-bearing pattern whose
 * callee body this pass REBUILDS. The result is recorded there; the position
 * below is what it supports.
 *
 * A WAVE THAT MOVES THIS CALL has either found one of the three constraints
 * wrong — which is design prediction P-12 and is welcome — or has
 * reintroduced r54 E1. There is no third possibility, which is why the
 * constraints are written at the call site as well as here.
 *
 * ============================================================================
 * WHY THE WALK PUBLISHES A ROOT
 * ============================================================================
 *
 * It returns the (possibly new) root and `compile.c` assigns it back, even
 * though today's byte instance never rewrites anything. `compile.c:942`'s own
 * comment records the bug that makes that worth doing from the start:
 * `discharge_atomic` "now PUBLISHES the rewritten root — inside `select_engine`
 * the assignment was to a local, so a discharge at the very root was
 * discarded." A lowering that rewrote to a local would leave `emit_vm` walking
 * the UN-lowered tree, which is r54 E1 arriving by a second route. Getting the
 * plumbing right while it carries nothing is free; getting it right later,
 * under a rewrite that mostly works, is how that bug happened the first time.
 *
 * ITERATIVE ON `A_CAT`/`A_ALT` SPINES (D10/DD-10/K20): a flat concatenation is
 * as long as the PATTERN and this project has segfaulted its own compiler on a
 * 20,000-character literal once already. IT DOES NOT FOLLOW `u.call.body` —
 * `src/opt/postresolve.c`'s walk header has the full argument, and both halves
 * apply here: following the back edge does not terminate on a recursive call,
 * and it is redundant because a class inside a called group is visited at its
 * own LEXICAL position by this same walk. */

#include "core/internal.h"
#include "gen/enc/enc.h"

typedef struct {
    Ctx      *cx;
    unsigned  max_cp;    /* the BACKEND's, never a constant here */
} LowerCtx;

static void lower_node(LowerCtx *lc, const Ast *a)
{
    for (;;) {
        if (a->k == A_CLASS) {
            /* THE BYTE INSTANCE. Every interval inside `[0, 0xFF]` is already
             * the confined form the render helper wants, so the rewrite is the
             * identity and what remains is §2.1's rule stated where it can
             * fire. `max_cp` is read from the backend rather than written as
             * `0xFF` here so that the diagnostic names the encoding's own
             * bound, and so that this line is the one stage 2 replaces rather
             * than the one it has to remember to update. */
            for (int i = 0; i < a->u.cls.n; i++)
                if (a->u.cls.iv[i].hi > lc->max_cp)
                    ctx_fail(lc->cx, 0,
                             "internal error: a class holding code point "
                             "U+%04X survived to the encoding lowering, whose "
                             "universe ends at U+%04X",
                             a->u.cls.iv[i].hi, lc->max_cp);
            return;
        }
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF:
        /* THE BACK EDGE STOPS HERE — see this file's header. */
        case A_CALL:
            return;
        case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            const Ast *t = a;
            for (; t->k == k; t = t->l) lower_node(lc, t->r);
            a = t;
            continue;
        }
        }
        /* No `default:` — mrl.c:18-24's rule, and `postresolve.c`'s. A node
         * kind added after this file is written must be a COMPILE ERROR here,
         * because "can this construct CONTAIN a character set" is a question
         * only the author of the new kind can answer and inheriting "no" is
         * the silent wrong answer: it would leave a code-point class in a
         * subtree the emitter then reads as bytes, which is r54 E1 with the
         * lowering present and blind. */
        return;
    }
}

Ast *pcrec_lower_enc(Ctx *cx, Ast *root)
{
    const PcrecEnc *e = pcrec_enc_by_id(cx->opt->encoding);
    if (!e)
        ctx_fail(cx, 0, "internal error: no encoding row for id %d",
                 cx->opt->encoding);
    LowerCtx lc = { cx, e->max_cp };
    lower_node(&lc, root);
    return root;
}
