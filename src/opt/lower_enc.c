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
 * THE POSITION, AND THE INVARIANT THAT REPLACES THE ORDERING ARGUMENT
 * ============================================================================
 *
 * `pcrec_lower_enc` runs at `src/core/compile.c:1000`, between
 * `pcrec_postresolve` and the guarded `pcrec_build_nfa`. Two ordering
 * constraints hold it there:
 *
 *   1. IT MUST RUN BEFORE `pcrec_build_nfa` AND BEFORE `pcrec_emit_vm`.
 *      Those are the two consumers that can only express bytes, and the
 *      second is handed the AST ROOT rather than the IR — which is why
 *      "between the parser and the IR" is not a position at all for the VM
 *      half of this compiler. Getting this wrong is r54 E1: a silent
 *      miscompile, not a refusal.
 *   2. IT MUST RUN AFTER `pcrec_postresolve` (:999), which asks module
 *      `lookaround`'s fixed-width rule in CHARACTERS. After the lowering a
 *      two-byte character is an `A_CAT` of two byte classes, so a
 *      character-width walk over a lowered tree would answer 2 where the
 *      truth is 1.
 *
 * THE DESIGN NAMED A THIRD CONSTRAINT AND IT WAS MIS-STATED — utf8_design.md
 * §2.1.2 argued the pass must sit below `pcrec_callgraph_build` (:961)
 * because a `.body` captured before a REBUILDING pass goes stale. The rule is
 * real and the conclusion inverted: a rebuilding pass would have to run
 * ABOVE the graph, which collides head-on with constraint 2 and leaves no
 * legal slot at all. MEASURED in this wave (docs/dev/lanes/utf8s1_report.md
 * §4): a scratch REBUILDING lowering at :1000 moves 45 of `tests/recursion`'s
 * 179 artifacts — the call site's activation-private `W` save/restore block
 * comes out EMPTY, because `u.call.save` is derived through a `.body` that
 * now names abandoned nodes — and the same pass above :961 moves none.
 *
 * **RULED (manager, R2): the cure is this pass's SHAPE, not its slot.**
 *
 *   THE INVARIANT — `pcrec_lower_enc` SPLICES IN PLACE. It replaces a leaf
 *   `A_CLASS` by MUTATING THE PARENT'S CHILD POINTER, never by rebuilding
 *   the parent, and it NEVER REALLOCATES A NODE THAT IS OR CONTAINS A GROUP
 *   ROOT.
 *
 * That makes the staleness inexpressible rather than merely avoided. A group
 * root is an `A_CAP` node (plus the whole `root` for group 0), a leaf
 * `A_CLASS` is neither, and every node on the path from the root down to a
 * replaced leaf keeps its address — so every pointer
 * `pcrec_callgraph_build` captured at :961 still names the subtree the
 * emitter will walk, and the pass may sit below the graph after all.
 *
 * THE WALK IS WRITTEN SO THAT THE INVARIANT IS STRUCTURAL RATHER THAN
 * REMEMBERED. `lower_walk` is handed `Ast **slot` — the ADDRESS of the
 * pointer that holds the current node — so the only write it can make is
 * `*slot = repl`, one pointer, in a parent it does not otherwise touch.
 * There is no expression in this file that allocates a parent, and stage 2
 * extends it by filling in `lower_class` alone.
 *
 * THE ROOT IS THE ONE SLOT THAT IS NOT A PARENT'S FIELD, and it is handled
 * by the same mechanism: `pcrec_lower_enc` passes `&root` and returns it, so
 * a root-level bare class splices exactly like any other leaf and
 * `compile.c` publishes the result. That is sound for group 0's own `.body`
 * because a pattern whose ROOT is a bare `A_CLASS` has no group construct in
 * it at all, hence no `A_CALL`, hence no capture to strand — and rather than
 * leave that as an argument, the assertion at the bottom of this file checks
 * it at the one moment it could stop being true.
 *
 * STAGE 2 GAINS A CHECK FOR THE INVARIANT ITSELF (R2): no group root's node
 * ADDRESS may change across this pass. It is not written here because stage 1
 * splices nothing, so it would assert over an empty population — the
 * [MECH-REACH] shape this house has twice had to retire.
 *
 * ITERATIVE ON `A_CAT`/`A_ALT` SPINES (D10/DD-10/K20): a flat concatenation is
 * as long as the PATTERN and this project has segfaulted its own compiler on a
 * 20,000-character literal once already. IT DOES NOT FOLLOW `u.call.body` —
 * `src/opt/postresolve.c`'s walk header has the full argument, and both halves
 * apply here: following the back edge does not terminate on a recursive call,
 * and it is redundant because a class inside a called group is visited at its
 * own LEXICAL position by this same walk.
 *
 * IT DOES NOT FOLLOW `u.rep.revbody` EITHER, AND THAT IS A STAGE-2 GAP RATHER
 * THAN A DECISION — see the note at `lower_walk`'s `A_REP` arm. */

#include "core/internal.h"
#include "gen/enc/enc.h"

typedef struct {
    Ctx      *cx;
    unsigned  max_cp;    /* the BACKEND's, never a constant here */
} LowerCtx;

/* THE PER-CLASS RULE, and the ONE function stage 2 replaces.
 *
 * Returns the node that must REPLACE `a`, or NULL for "leave it alone". The
 * caller does the splicing, so this function cannot reach a parent even by
 * accident — which is the invariant in this file's header, expressed as a
 * signature rather than as a comment.
 *
 * THE BYTE INSTANCE ANSWERS NULL ALWAYS. Under `--encoding=byte` a code point
 * IS a byte, so an interval list already inside `[0, max_cp]` is the confined
 * form the render helper wants and the rewrite is the identity. What remains
 * is §2.1's rule stated where it can fire — and the arm is UNREACHABLE in
 * stage 1 by construction, because the parser range-checks `\x{...}` on its
 * literal input (§2.7.3) and a complement cannot exceed `max_cp`. That makes
 * it the assertion that those two facts stay true.
 *
 * `max_cp` is read from the backend rather than written as `0xFF` here so the
 * diagnostic names the encoding's own bound, and so this is the line stage 2
 * replaces rather than the one it has to remember to update. */
static Ast *lower_class(LowerCtx *lc, Ast *a)
{
    for (int i = 0; i < a->u.cls.n; i++)
        if (a->u.cls.iv[i].hi > lc->max_cp)
            ctx_fail(lc->cx, 0,
                     "internal error: a class holding code point U+%04X "
                     "survived to the encoding lowering, whose universe ends "
                     "at U+%04X", a->u.cls.iv[i].hi, lc->max_cp);
    return NULL;
}

/* `slot` is the ADDRESS of the pointer holding the current node — its
 * parent's `->l` or `->r`, or `&root` at the top. Writing through it is the
 * whole of the in-place splice, and it is the only write this walk makes. */
static void lower_walk(LowerCtx *lc, Ast **slot)
{
    for (;;) {
        Ast *a = *slot;
        switch (a->k) {
        case A_CLASS: {
            Ast *repl = lower_class(lc, a);
            /* THE SPLICE: one pointer, in a parent this walk never rebuilt. */
            if (repl) *slot = repl;
            return;
        }
        case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF:
        /* THE BACK EDGE STOPS HERE — see this file's header. */
        case A_CALL:
            return;
        case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK:
            /* [M5.0 STAGE-2 GAP, RECORDED WHERE IT BITES] `A_REP` also carries
             * `u.rep.revbody`, a REVERSED COPY of its body built by
             * `src/opt/revdet.c` inside `pcrec_select_engine` (compile.c:988)
             * — i.e. BEFORE this pass. This walk does not visit it, so under
             * stage 2 the forward body would be lowered and the reversed copy
             * would not, and the backward walk would hand `pcrec_cls_bits` a
             * code-point class.
             *
             * THAT IS LOUD RATHER THAN SILENT — the render helper `ctx_fail`s
             * by name, which is exactly what §2.1.4 built it for — and it is
             * harmless in stage 1, where nothing is spliced and every class is
             * byte-confined. It is named here rather than fixed because the
             * fix is a stage-2 decision (lower the reversed copy too, or move
             * the rung's analysis below the lowering) and building either now
             * would be unexercised structure. */
            slot = &a->l;
            continue;
        case A_CAT: case A_ALT: {
            /* The spine is walked ITERATIVELY with the slot carried down it,
             * so a 20,000-element concatenation costs no stack (K20). `s`
             * always holds the address of the pointer to the current spine
             * node, and recursion is into the ITEMS only. */
            const AKind k = a->k;
            Ast **s = slot;
            while ((*s)->k == k) {
                Ast *t = *s;
                lower_walk(lc, &t->r);
                s = &t->l;
            }
            slot = s;
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
    Ast *was = root;
    lower_walk(&lc, &root);

    /* THE ROOT ASSERTION — the one place the in-place-splice invariant could
     * stop holding, checked rather than argued.
     *
     * Replacing the ROOT is legal only because a pattern whose root is a bare
     * `A_CLASS` contains no group construct, hence no `A_CALL`, hence nothing
     * that captured group 0's `.body` at `pcrec_callgraph_build`. That is a
     * claim about a coincidence of two facts, and coincidences are what stop
     * being true — so it is asserted here, at the moment the root moves,
     * rather than left in a comment for stage 2 to rediscover.
     *
     * Unreachable in stage 1 (nothing splices), which is why it is written as
     * an internal error and not as a refusal: if it ever fires, the finding is
     * that the invariant needs a different repair, not that the pattern is
     * bad. */
    if (root != was && cx->callgraph)
        ctx_fail(cx, 0, "internal error: the encoding lowering replaced the "
                        "AST root of a call-bearing pattern — group 0's "
                        "cached body now names an abandoned node");
    return root;
}
