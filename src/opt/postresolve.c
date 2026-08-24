/* postresolve.c — [DD-14.LB] THE POST-RESOLUTION CHECKS: the rules that must
 * refuse a pattern AT A PATTERN OFFSET and cannot be decided until the call
 * graph exists.
 *
 * Design: docs/design/subroutines_design.md §3.4(d) and its 2026-08-24
 * amendment (the timing gap and this pass); docs/design/lookaround_design.md
 * §2.5 (the one rule this pass carries today).
 *
 * ================================================================
 * THE GAP THIS PASS EXISTS FOR, AND WHY IT IS A SHAPE AND NOT A CASE
 * ================================================================
 *
 * Two facts about this compiler collide, and neither is going to move:
 *
 *   A MODULE'S PARSE HOOK IS THE ONLY PLACE THAT HOLDS A PATTERN OFFSET.
 *   `Ast` carries no position of any kind — PARSE-1 says so and
 *   `AltInfo.last_bar` exists because of it — so a refusal raised anywhere
 *   downstream has nothing but offset 0 to point at, which for a caller is
 *   worse than no offset: it names a byte that is not the problem.
 *
 *   THE CALL GRAPH DOES NOT EXIST UNTIL AFTER PARSE, and cannot. `.body` is
 *   bound over the FINAL tree, after every rewriting pass, because it is a
 *   cache of "which subtree is that group's, in the tree the emitter will
 *   walk" (src/opt/callgraph.c's header, and wave A2's finding at 513de65). A
 *   forward call's target has not even been PARSED when the hook runs.
 *
 * So any rule whose answer depends on a callee is decided at a moment when it
 * cannot be raised, and raised at a moment when it cannot be decided. THE
 * RESOLUTION IS THREE MOVES, and they are the same three every time: the hook
 * RECORDS (the offset, on the node, in the module's own `u.*` payload), the
 * graph is BUILT, and this pass RE-ASKS the module's rule and refuses at the
 * recorded offset. That is why this file is a pass with a customer list and
 * not a call to one module's function: the shape recurs (§6.3's splice
 * eligibility, a variable-length lookbehind follow-on, the next module that
 * meets a call), and a second occurrence must extend a list rather than
 * invent a second post-graph timing.
 *
 * WHAT EACH SIDE OWNS. This file owns the WALK and the ORDER and knows nothing
 * about lookbehind widths; module `lookaround` owns the RULE and its three
 * refusal sentences and knows nothing about the call graph. Inlining the rule
 * here would be a SECOND derivation of "is this branch fixed-width" for the
 * hook's own to disagree with — which is the failure `Ast.u.look.widths` is
 * stored to prevent, one level down.
 *
 * ================================================================
 * ORDER IS PART OF THE CONTRACT
 * ================================================================
 *
 * The recorded constructs are visited in ASCENDING PATTERN OFFSET, so a
 * pattern with two offending lookbehinds refuses at the FIRST — which is what
 * the parse hook would have done, and what every other diagnostic in this
 * compiler does. The walk order is NOT that order and is not close to it: a
 * flat concatenation is LEFT-NESTED, so a spine walk reaches the RIGHTMOST
 * element first and would report the LAST offending construct in the pattern.
 * Sorting is two lines and the alternative is a diagnostic whose choice of
 * offset is an artifact of the tree shape.
 *
 * ================================================================
 * WHAT MAKES A SKIPPED PASS LOUD
 * ================================================================
 *
 * A recorded lookbehind that this pass never resolves reaches `vm_look_behind`
 * with `u.look.widths == NULL`, which that function already `ctx_fail`s on by
 * name. So deleting this pass is an INTERNAL ERROR on the first call-bearing
 * lookbehind rather than a NULL dereference or, worse, a compile that emits a
 * back-step of width zero. Sabotage row S-LB1 is that experiment. */

#include "core/internal.h"

/* ---- the final-tree walk ------------------------------------------------
 *
 * ITERATIVE ON `A_CAT`/`A_ALT` SPINES (D10/DD-10/K20, and src/ir/nfa.c's R-2
 * hardening): a flat concatenation is as long as the PATTERN, not as deep as
 * its nesting, and this project has segfaulted its own compiler on a
 * 20,000-character literal once already.
 *
 * IT DOES NOT FOLLOW `u.call.body`, and here that is load-bearing twice over.
 * Following it is design §4.4's non-terminating compile (`(a(?1))` hangs the
 * COMPILER); and it is also redundant, because a lookbehind written inside a
 * called group is visited at its own LEXICAL position by this same walk, and
 * its width table is a property of the node rather than of the path that
 * reached it. Descending the edge would visit some nodes twice and never
 * terminate on the recursive ones.
 *
 * IT IS A SECOND WALKER AND THAT IS THE HOUSE STYLE, not drift: `revdet.c`,
 * `possessify.c`, `select_engine.c`, `altcls.c` and `callgraph.c` each carry
 * their own descent, because what varies between them is precisely which
 * edges they follow and what they thread. What must NOT be duplicated is a
 * RULE, and no rule lives here. */
typedef void (*PrVisit)(void *ud, const Ast *a);

static void pr_walk(const Ast *a, PrVisit f, void *ud)
{
    for (;;) {
        f(ud, a);
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF:
        /* THE BACK EDGE STOPS HERE — see this walk's header. */
        case A_CALL:
            return;
        case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            const Ast *t = a;
            for (; t->k == k; t = t->l) pr_walk(t->r, f, ud);
            a = t;
            continue;
        }
        }
        /* No `default:` — mrl.c:18-24's rule. A node kind added after this
         * file is written must be a COMPILE ERROR here, because "can this
         * construct CONTAIN a recorded post-resolution check" is a question
         * only the author of the new kind can answer, and inheriting "no" is
         * the silent wrong answer: it would skip a recorded check and let a
         * pending lookbehind reach the emitter. */
        return;
    }
}

/* ---- customer 1: module `lookaround`'s §2.5 width rule ------------------- */

typedef struct { int n; Ast **at; } PrPend;

static void pr_count(void *ud, const Ast *a)
{
    PrPend *p = ud;
    if (pcrec_lookaround_width_pending(a)) p->n++;
}

/* Collected in ASCENDING `u.look.at` by insertion — see the file header on
 * order. The array is at most the pattern's lookaround count, so the quadratic
 * insert is bounded by a term the parser already bounds and needs no cap of
 * its own; a pattern with enough lookbehinds for it to matter has already paid
 * far more for its parse. */
static void pr_collect(void *ud, const Ast *a)
{
    PrPend *p = ud;
    if (!pcrec_lookaround_width_pending(a)) return;
    Ast *n = (Ast *)a;          /* the tree is this compile's own arena */
    int i = p->n++;
    while (i > 0 && p->at[i - 1]->u.look.at > n->u.look.at) {
        p->at[i] = p->at[i - 1];
        i--;
    }
    p->at[i] = n;
}

/* ------------------------------------------------------------------------- */

void pcrec_postresolve(Ctx *cx, Ast *root)
{
    /* ONE COUNTING WALK FIRST, and the early return is what makes this pass
     * free for every pattern that records nothing — which is every call-free
     * pattern in the corpus, since a lookbehind is only ever recorded when its
     * body carries an `A_CALL`. Nothing here allocates or touches a node
     * before that return, so a pattern compiled before this pass existed is
     * compiled byte-identically after it. */
    PrPend p = { 0, NULL };
    pr_walk(root, pr_count, &p);
    if (p.n == 0) return;

    const int want = p.n;
    p.at = arena_alloc(&cx->arena, (size_t)want * sizeof *p.at);
    p.n = 0;
    pr_walk(root, pr_collect, &p);
    if (p.n != want)
        /* UNREACHABLE: the two walks visit the same tree with the same
         * predicate. Loud rather than silent because the only way here is a
         * walk that is not deterministic over one tree, and the consequence of
         * shrugging would be a recorded lookbehind reaching the emitter
         * unresolved. */
        ctx_fail(cx, 0, "internal error: the post-resolution walk found %d "
                        "deferred checks and then collected %d", want, p.n);

    for (int i = 0; i < want; i++)
        pcrec_lookaround_fix_widths(cx, p.at[i]);
}
