/* callgraph.c — [DD-14] THE CALL GRAPH: which groups are called, what each
 * callee reaches, and the two things that cannot be answered without it.
 *
 * Design: docs/design/subroutines_design.md §4.2 (`.body`), §4.3 (marking),
 * §4.4 (the back-edge rule), §4.4b (the `minw` fixpoint), §6.3 (the linkage).
 *
 * WHY THIS FILE EXISTS AT ALL, in one sentence: `Ast.u.call.body` is the AST's
 * first `Ast*` -> `Ast*` BACK EDGE, and every walker in `src/` is a bare
 * `const Ast *` descent with no context, no memo and no visited set — so a
 * question whose answer for a call genuinely IS the callee's ("how wide is
 * this?", "can it match empty?") is not expressible at the walker at all. It
 * needs a memoised fixpoint over the SCC-condensed graph, and that is what is
 * here. A WHOLE-TREE PREDICATE, by contrast, needs none of this and must not
 * follow the edge: it already visits the callee at the callee's own lexical
 * position, so following it is redundant AND non-terminating (`(a(?1))` hangs
 * the COMPILER, in predicates asked of every pattern).
 *
 * ================================================================
 * THE PASS ORDER IS THE POINT, AND IT IS THIS FILE'S OWN FINDING
 * ================================================================
 *
 * `.body` is a CACHE. `u.call.target` is the durable fact, and `.body` is
 * "which subtree is that group's, in the tree the emitter is about to walk".
 * Those are two different questions the moment a pass REBUILDS a node, and
 * pcrec has two such passes:
 *
 *   - `pcrec_altcls` (src/opt/altcls.c, run immediately after parse) allocates
 *     NEW nodes: its `A_REP`/`A_CAP` arms do `*r = *a; r->l = body;`, and its
 *     two stages rebuild spines and merge branches into a fresh `A_CLASS`. On
 *     `((?:a|b))(?1)` the tree's group 1 becomes a NEW `A_CAP` over `[ab]`.
 *   - `pcrec_discharge_atomic` (src/opt/atomic.c, from `pcrec_select_engine`)
 *     SPLICES an `A_ATOMIC` out, so a callee whose root was that node would be
 *     reached with the cut still in it.
 *
 * A `.body` captured at END OF PARSE — where wave A2's `PendingRef` comment
 * and design §4.2 both put it — therefore names, for `((?:a|b))(?1)`, a
 * subtree that is NO LONGER IN THE TREE. Under `CALL_LINKAGE` the callee
 * REGION would be emitted from the stale subtree while the LEXICAL occurrence
 * came from the new one: **TWO DIFFERENT PROGRAMS FOR ONE GROUP**, with §4.4c's
 * slot indices and §5.3's `W` computed over whichever of the two was handed
 * over — which is §5.3b's axis-C miscompile arriving by a third route.
 *
 * WAVE A2 FOUND IT (commit 513de65) and left wave B+C three answers: resolve
 * `.body` after the rewrites, have every rewriting pass update it, or exempt
 * callee subtrees from rewriting. **THIS FILE IMPLEMENTS THE FIRST**, and the
 * other two are worse for reasons worth writing down rather than re-deriving:
 * (b) puts the obligation on every FUTURE rewriting pass, with no diagnostic
 * when one forgets — the drift D24's registry exists to prevent, one level
 * down; (c) makes a called group's emitted code differ from an uncalled one's
 * for no semantic reason and would forfeit `altcls`'s wins on exactly the
 * bodies a recursive pattern runs most.
 *
 * SO THE BIND IS DRIVEN FROM `target` OVER THE FINAL TREE, and it is the only
 * writer of `.body` anywhere. `S144` is its detector, with `((?:a|b))(?1)` as
 * the altcls witness and `((?>a)b)(?1)` as the discharge witness.
 *
 * ================================================================
 * WHAT THIS FILE DOES *NOT* COMPUTE, AND WHY EACH LIVES ELSEWHERE
 * ================================================================
 *
 * `vm_nullable`'s fixpoint and `W` are both in `src/gen/emit_vm.c`, which is a
 * deviation from design §4.4b's "one mechanism, and this is the only list of
 * its consumers" and is the wave's largest amendment to the design. Both are
 * the same reason: the RECURRENCE lives there and cannot be moved.
 *
 *   - `vm_nullable` is `static` to the emitter and is the emitter's own
 *     definition of the property the empty-iteration guard is emitted on. A
 *     copy here would be a second answer to "can this match empty" for the two
 *     to disagree about, which is the failure mode `vm_marked`, `vm_cuts` and
 *     `vm_cursor_fits` are each ONE predicate to avoid.
 *   - `W` is a set of SLOT INDICES, and slot indices are assigned by
 *     `vm_count_slots`' own walk over the emitter's own rung decisions. They
 *     do not exist outside `emit_vm.c` and cannot be predicted from here
 *     without a second slot census — which `src/gen/CLAUDE.md` names as the
 *     standing hazard for exactly this family.
 *
 * What this file DOES own is the GRAPH those two fixpoints iterate over, and
 * it exports it (`pcrec_callgraph_targets`, `_body`, `_calls`) rather than
 * letting the emitter re-derive "which groups are called and what does each
 * one reach" — that half genuinely is one mechanism with three consumers. */

#include <string.h>

#include "core/internal.h"

/* Every distinct group number some `A_CALL` in this tree names, ascending, and
 * for each of them the region root and the transitive set of targets its
 * region can reach. `0` is a legal member and means THE ROOT (design §2.4:
 * `(?R)` re-runs the whole pattern, ANCHORS INCLUDED). */
struct CallGraph {
    int          ntarget;
    int         *target;      /* ascending, may begin with 0 */
    const Ast  **body;        /* body[i] is target[i]'s region root */
    unsigned char *reach;     /* reach[i*ntarget + j]: region i can reach j */
    /* [DD-14 wave G] THE EDGE MULTIPLICITY, which `reach` deliberately loses.
     * `site[i*ntarget + j]` is how many `A_CALL` nodes lie DIRECTLY in region
     * i's body naming target j — not transitive, not saturated. §6.3's size
     * budget is about COPIES, and a region that calls one callee four times
     * costs four expansions where `reach` says only "yes". */
    int         *site;
    /* [DD-14 wave G] `splice[i]`: may every call site naming target i be
     * emitted INLINE (design §6.3)? The decision is PER TARGET rather than
     * per site, which is a choice and not a forced one — see `cg_eligibility`.
     * `exp[i]` is the expansion that decision was made on, in AST nodes. */
    bool        *splice;
    long long   *exp;
};

/* ---- the whole-tree collection walks ------------------------------------
 *
 * ALL OF THEM ARE ITERATIVE ON `A_CAT`/`A_ALT` SPINES (D10/DD-10/K20, and
 * src/ir/nfa.c's R-2 hardening for the third time): a flat concatenation is as
 * long as the PATTERN, not as deep as its nesting, and this project has
 * segfaulted its own compiler on a 20,000-character literal once already.
 * NONE of them follows `u.call.body` — design §4.4's rule, and here it is not
 * merely redundant but load-bearing, because these walks run BEFORE the bind
 * and `.body` is NULL. */

typedef void (*CgVisit)(void *ud, const Ast *a);

static void cg_walk(const Ast *a, CgVisit f, void *ud)
{
    for (;;) {
        f(ud, a);
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF:
        /* THE BACK EDGE STOPS HERE. An `A_CALL` has no `l` and no `r`; its
         * callee is `u.call.body`, and following it is design §4.4's
         * non-terminating compile. */
        case A_CALL:
            return;
        case A_CAP: case A_REP: case A_ATOMIC: case A_LOOK:
            a = a->l;
            continue;
        case A_CAT: case A_ALT: {
            const AKind k = a->k;
            const Ast *t = a;
            for (; t->k == k; t = t->l) cg_walk(t->r, f, ud);
            a = t;
            continue;
        }
        }
        return;
    }
}

/* Pass 1: how many `A_CALL` nodes, and which targets. */
typedef struct { int ncap; bool *named; int ncall; } CgScan;

static void cg_scan(void *ud, const Ast *a)
{
    CgScan *s = ud;
    if (a->k != A_CALL) return;
    s->ncall++;
    int t = a->u.call.target;
    if (t >= 0 && t <= s->ncap) s->named[t] = true;
}

/* Pass 2: the region root for each group number. `group_root[0]` is the AST
 * ROOT and every other is the `A_CAP` whose `u.cap.no` matches.
 *
 * THE `A_CAP` ITSELF IS THE REGION, not its child, and the difference is
 * MEASURED (§5.3, `out/captures.txt` C3): `^((a)(?1)?(b))$` on "aabb" answers
 * g1 = (0,4), which requires the recursive call to have OVERWRITTEN group 1's
 * start with 1 and the return to have put 0 back. A region rooted at the
 * capture node's CHILD would write no group-1 slot at all and the restore set
 * would have nothing to restore — the design's own first draft, which its
 * prototype refuted at `g1 = (1,4)`: a wrong span on a correct match, which no
 * `m`/`n` expectation catches and only a `g` line does. */
typedef struct { int ncap; const Ast **root; } CgRoots;

static void cg_roots(void *ud, const Ast *a)
{
    CgRoots *r = ud;
    if (a->k != A_CAP) return;
    int g = a->u.cap.no;
    /* FIRST occurrence wins. A group number occurs once in a well-formed
     * tree; the guard is here because `--no-captures` deletes wrappers and a
     * future branch-reset construct would legitimately reuse a number, and a
     * silent second binding is the shape §4.4c's "two programs for one group"
     * warns about. */
    if (g > 0 && g <= r->ncap && !r->root[g]) r->root[g] = a;
}

/* Pass 3, per region: which targets does THIS subtree call. */
typedef struct {
    const struct CallGraph *cg;
    unsigned char *row;
    int           *cnt;
} CgEdges;

static int cg_index(const struct CallGraph *cg, int t)
{
    for (int i = 0; i < cg->ntarget; i++) if (cg->target[i] == t) return i;
    return -1;
}

static void cg_edges(void *ud, const Ast *a)
{
    CgEdges *e = ud;
    if (a->k != A_CALL) return;
    int i = cg_index(e->cg, a->u.call.target);
    if (i >= 0) { e->row[i] = 1; e->cnt[i]++; }
}

/* [DD-14 wave G] AST NODES IN A REGION, for §6.3's size budget. Counts what
 * `cg_walk` visits, which is exactly the subtree the emitter will walk for
 * this region and STOPS AT `A_CALL` — a nested call's own expansion is added
 * by `cg_eligibility`'s recurrence, not by this walk, because following
 * `.body` here is design §4.4's non-terminating descent. */
static void cg_count(void *ud, const Ast *a)
{
    (void)a;
    ++*(long long *)ud;
}

/* ---- the bind ----------------------------------------------------------- */

typedef struct { Ctx *cx; const Ast **root; int ncap; } CgBind;

static void cg_bind(void *ud, const Ast *a)
{
    CgBind *b = ud;
    if (a->k != A_CALL) return;
    Ast *n = (Ast *)a;          /* the tree is this compile's own arena */
    int t = n->u.call.target;
    const Ast *body = (t == 0) ? b->root[0]
                    : (t > 0 && t <= b->ncap) ? b->root[t] : NULL;
    if (!body)
        /* UNREACHABLE, and loud rather than silent because the two ways to get
         * here are both miscompiles: a target the resolver accepted whose
         * `A_CAP` a later pass DELETED (design §4.3's marking is what stops
         * `--no-captures` doing exactly that), or a target the resolver never
         * filled in. A NULL `.body` would emit a callee region for nothing. */
        ctx_fail(b->cx, 0, "internal error: subroutine call to group %d has no "
                           "body in the final tree", t);
    n->u.call.body = body;
    /* §6.3: WAVE B+C SHIPS THE CALL LINKAGE FOR EVERY SITE. It is one path, it
     * is correct for every shape including recursion, and it is what the four
     * gating questions are about; wave G replaces the ELIGIBLE sites with a
     * splice (implement-then-replace, which is not a parallel mechanism — the
     * splice consumes the same callee contract §5.4 and the same `W` §5.3 and
     * differs only in how control reaches the body). Set for EVERY node here
     * because the arena zeroes to `CALL_SPLICE`, which is the wrong default in
     * the UNSOUND direction: a spliced recursive call is an infinite emitter. */
    n->u.call.link = CALL_LINKAGE;
}

/* ---- the minw fixpoint (design §4.4b) ------------------------------------ */

typedef struct { const struct CallGraph *cg; const long long *val; } CgMinw;

static void cg_minw_publish(void *ud, const Ast *a)
{
    CgMinw *m = ud;
    if (a->k != A_CALL) return;
    int i = cg_index(m->cg, a->u.call.target);
    ((Ast *)a)->u.call.minw = i >= 0 ? m->val[i] : 0;
}

/* ---- the maxw fixpoint ([DD-14.LB]) --------------------------------------
 *
 * `minw`'s MIRROR, and mirrored in the sense that matters: `pcrec_minw`'s free
 * direction is DOWN and `pcrec_maxw`'s is UP, so this iteration starts at
 * `PCREC_W_UNBOUNDED` and descends where that one starts at `PCREC_MINW_MAX`
 * and descends too — both begin at the value that is SAFE to be wrong with and
 * approach the truth from the safe side, which for `maxw` is from ABOVE.
 *
 * A TARGET IN A CYCLE IS A FIXED POINT AT UNBOUNDED, WITH NO CYCLE TEST. The
 * `reach` closure two functions up could answer "is target i in a cycle"
 * directly (`reaches(i,i)`), and this fixpoint deliberately does not ask it:
 * `mrl_sat_add` saturates, so a body that calls back into its own SCC reads
 * the published `PCREC_W_UNBOUNDED`, computes `k + UNBOUNDED == UNBOUNDED`,
 * and never leaves the top. The same absorption gives the RIGHT answer for a
 * target that merely REACHES a cycle without being in one (`g = (?&h)x` with
 * `h` recursive is genuinely unbounded), which an `reaches(i,i)` test would
 * have got wrong unless it were widened into exactly this propagation. One
 * mechanism, and the cycle test would have been a second one.
 *
 * TERMINATION AND THE ROUND BOUND are `minw`'s argument unchanged, read in the
 * other direction: every arm of `pcrec_maxw`'s recurrence is a sum, a max or a
 * constant — a superior-function system in Knuth's sense — the values are
 * non-increasing and bounded below by 0, and each round settles at least one
 * more target, so `n` rounds suffice and the `n + 1`-th is ASSERTED to change
 * nothing. An under-run fixpoint here would leave a target at UNBOUNDED, which
 * is an OVER-estimate and therefore safe (a lookbehind refused that PCRE2
 * accepts is the tier-2 over-rejection this wave is removing, never a
 * miscompile); an over-run one is impossible.
 *
 * `maxw_known` IS PUBLISHED WITH `maxw` AND ONLY BY THIS LOOP. It is what
 * makes `pcrec_maxw`'s arm answer the OLD, sound `PCREC_W_UNBOUNDED` at every
 * timing before this pass — the parse hook's, above all, which is exactly
 * where the deferred re-check exists to avoid answering. */

typedef struct { const struct CallGraph *cg; const long long *val; } CgMaxw;

static void cg_maxw_publish(void *ud, const Ast *a)
{
    CgMaxw *m = ud;
    if (a->k != A_CALL) return;
    int i = cg_index(m->cg, a->u.call.target);
    /* A target the graph does not carry cannot happen (`cg_scan` collected
     * every `A_CALL`'s target and `cg_bind` has already failed loudly for a
     * target with no body), and if it somehow did, `maxw_known = false` is the
     * answer that costs an over-estimate rather than a miscompile — the same
     * polarity choice the field itself is. */
    Ast *n = (Ast *)a;
    if (i >= 0) { n->u.call.maxw = m->val[i]; n->u.call.maxw_known = true; }
    else        { n->u.call.maxw = PCREC_W_UNBOUNDED;
                  n->u.call.maxw_known = false; }
}

/* ---- [DD-14 wave G] SPLICE ELIGIBILITY (design §6.3) ---------------------
 *
 * §6.3's ruling, as landed: **a call site takes the CALL linkage into one
 * shared emitted region EXCEPT where the callee is not in a cycle AND the
 * spliced expansion fits a size budget, in which case it SPLICES** — the
 * callee's body emitted INLINE at the site, with its OWN exit. The lexical
 * occurrence of a called group is emitted EXACTLY AS IT IS TODAY either way;
 * wave G may share the BODY and never the EXIT (§3.5, S-SR18), so nothing
 * here reuses a lexical label.
 *
 * IT IS `implement-then-replace`, NOT A PARALLEL MECHANISM. The spliced site
 * consumes the SAME callee contract (§5.4) and the SAME `W` (§5.3) as the
 * linked one and differs only in how control reaches the body — which is what
 * makes §9.2's `A == B` control (`-fno-splice-calls`) a real differential
 * rather than two programs that happen to agree.
 *
 * ================================================================
 * CONDITION 1: NOT IN A CYCLE, AND IT IS ONE ARRAY LOOKUP
 * ================================================================
 *
 * `reaches(i, i)` over the transitive closure two functions up. A recursive
 * callee has no finite inlining, so a spliced one is an infinite emitter —
 * which is why `Ast.u.call.link`'s arena zero (`CALL_SPLICE`) is the WRONG
 * default and `cg_bind` sets `CALL_LINKAGE` on every node before this runs.
 * This function only ever UPGRADES, so a target this test declines cannot
 * reach the emitter as a splice by any path.
 *
 * Condition 2 of §6.3 — "the callee's target is statically resolved" — is
 * free (§4.2 resolves every call at end of parse or refuses the pattern) and
 * is not written as code here; it is listed in the design to make the shape
 * explicit for `[DD-11]`.
 *
 * ================================================================
 * CONDITION 3: THE SIZE BUDGET, AND HOW IT COMPOSES FOR NESTED SPLICES
 * ================================================================
 *
 * The question the design leaves open is what a callee that itself calls a
 * spliceable callee costs, and the answer has to be the size it will REACH
 * rather than the size it is written as — otherwise a chain of ten callees
 * each "small" expands to a product nobody bounded. So:
 *
 *     exp(i) = nodes(body[i])
 *            + SUM over targets j != i of  site[i][j] * (splice(j) ? exp(j) - 1 : 0)
 *     splice(i) = !reaches(i, i) && exp(i) <= PCREC_MAX_SPLICE_NODES
 *
 * `- 1` because the `A_CALL` node the expansion replaces is itself counted in
 * `nodes(body[i])`. The recurrence is WELL FOUNDED on the acyclic part: every
 * `j` a spliceable `i` reaches is settled before `i` is, which is what the
 * evaluation order below establishes, and a cyclic target is settled FIRST at
 * `exp = LLONG_MAX / 4` with `splice = false` — the same "settle the cycles,
 * then evaluate the DAG" shape `emit_vm.c`'s region-cost memo uses, and for
 * the same reason.
 *
 * THE SATURATING ADD IS NOT DECORATION. `nodes` is bounded by the pattern
 * length but `site[i][j]` multiplies, and a ten-deep chain of four-call
 * bodies reaches 4^10 before any budget test would have fired. The
 * accumulator saturates at the same ceiling a cyclic target starts at, so
 * "too big to count" and "cannot be counted" answer the budget test the same
 * way — which is the direction that DECLINES, and a declined site is correct.
 *
 * ================================================================
 * THE TOTAL, AND WHY IT IS DELIBERATELY THE CRUDER NUMBER
 * ================================================================
 *
 * The per-site budget bounds ONE expansion; nothing in it bounds a pattern
 * with three hundred sites each expanding to five hundred nodes. So a second
 * budget bounds the SUM of the added nodes, and eligible targets are dropped
 * — LARGEST CONTRIBUTION FIRST, ties by DESCENDING TARGET NUMBER so the rule
 * is deterministic and re-derivable from the artifact — until the total fits.
 *
 * IT COUNTS LEXICAL SITES, WHICH IS AN OVER-ESTIMATE WHEN A REGION IS NOT
 * EMITTED AND AN UNDER-ESTIMATE WHEN ONE IS, and it is stated rather than
 * fixed. The exact count is "how many copies of this site does the emitter
 * write", which depends on how many regions are emitted, which depends on
 * which sites splice — the very question being answered. A fixpoint over that
 * would be a second sizing mechanism (§4.4's "one mechanism" rule) for a
 * PERFORMANCE knob whose every outcome is correct, and PCREC_MAX_VM_NODES is
 * the hard backstop underneath it either way. What the approximation buys is
 * that the rule can be stated in one sentence and checked from the artifact's
 * own `<PREFIX>_VM_CALLS` stamp.
 *
 * DROPPING A TARGET ONLY EVER SHRINKS THE REAL TOTAL, so the eligibility of a
 * caller decided against the pre-drop `exp` is CONSERVATIVE — it may decline a
 * caller that would in fact have fit. That is the safe direction and it is not
 * re-run to a fixpoint, for the same reason.
 *
 * ================================================================
 * WHY THE DECISION IS PER TARGET AND NOT PER SITE
 * ================================================================
 *
 * A per-SITE rule could splice the first three calls to a big callee and link
 * the fourth, which is strictly more expressive. It is not taken, because the
 * artifact would then contain BOTH an inlined copy and a shared region for one
 * group, and "which linkage did this site take" would stop being answerable
 * from the pattern — every future reader of `<PREFIX>_VM_CALLS`, every
 * sabotage row over the splice, and §9.2's `A == B` control all read better
 * against a rule with one answer per callee. Per-site remains available and
 * costs nothing structural: `link` is already a per-NODE field. */

static void cg_publish_link(void *ud, const Ast *a)
{
    const struct CallGraph *cg = ud;
    if (a->k != A_CALL) return;
    int i = cg_index(cg, a->u.call.target);
    /* ONLY EVER AN UPGRADE. `cg_bind` has already written `CALL_LINKAGE` on
     * every node, and a target the graph somehow does not carry keeps it —
     * the sound direction, since a splice of an unknown callee has no body to
     * inline. */
    if (i >= 0 && cg->splice[i]) ((Ast *)a)->u.call.link = CALL_SPLICE;

}

/* The ceiling `exp` saturates at, and the value a cyclic target starts at.
 * Well below LLONG_MAX so a sum of several of them cannot overflow, and far
 * above PCREC_MAX_SPLICE_NODES so it is never mistaken for a passing size. */
#define CG_EXP_INF ((long long)1 << 40)

static long long cg_sat_add(long long a, long long b)
{
    if (a >= CG_EXP_INF || b >= CG_EXP_INF) return CG_EXP_INF;
    long long r = a + b;
    return r >= CG_EXP_INF ? CG_EXP_INF : r;
}

static long long cg_sat_mul(long long a, long long b)
{
    if (a <= 0 || b <= 0) return 0;
    if (a >= CG_EXP_INF || b >= CG_EXP_INF) return CG_EXP_INF;
    if (a > CG_EXP_INF / b) return CG_EXP_INF;
    return a * b;
}

static void cg_eligibility(Ctx *cx, struct CallGraph *cg, Ast *root)
{
    const int n = cg->ntarget;
    const size_t nn = (size_t)n;

    cg->splice = arena_alloc(&cx->arena, nn * sizeof *cg->splice);
    cg->exp    = arena_alloc(&cx->arena, nn * sizeof *cg->exp);

    /* THE DENIAL IS TOTAL AND IS TAKEN FIRST (lib/pcrec.h's
     * PCREC_NO_SPLICE_CALLS): §9.2's control needs the LINKAGE-linked artifact
     * to be exactly the one wave B+C shipped, so the flag must not leave a
     * trace anywhere else — not in the budget arithmetic, not in a stamp
     * computed from it. Returning here is what makes the denied build the
     * control rather than a fourth variant of it. */
    for (int i = 0; i < n; i++) { cg->splice[i] = false; cg->exp[i] = CG_EXP_INF; }
    if (cx->opt->flags & PCREC_NO_SPLICE_CALLS) return;

    /* Nodes per region, and the cycles settled first. */
    long long *nodes = arena_alloc(&cx->arena, nn * sizeof *nodes);
    bool *done = arena_alloc(&cx->arena, nn * sizeof *done);
    for (int i = 0; i < n; i++) {
        nodes[i] = 0;
        cg_walk(cg->body[i], cg_count, &nodes[i]);
        done[i] = pcrec_callgraph_reaches(cg, i, i);   /* cyclic: exp stays INF */
    }

    /* THE DAG EVALUATION. `nt` rounds suffice because each round settles at
     * least one more target — every unsettled target either has an unsettled
     * callee (and some target in that chain has none, the chain being acyclic
     * once the cycles are already done) or is itself ready. The `!changed`
     * arm is an ASSERTION rather than a break: reaching it means a target is
     * waiting on a callee that is waiting on it, which is a cycle the closure
     * above did not report, and a graph that disagrees with itself must say so
     * rather than silently leave a target at INF. */
    for (int round = 0; round <= n; round++) {
        bool changed = false, all = true;
        for (int i = 0; i < n; i++) {
            if (done[i]) continue;
            bool ready = true;
            for (int j = 0; j < n; j++)
                if (j != i && pcrec_callgraph_reaches(cg, i, j) && !done[j])
                    ready = false;
            if (!ready) { all = false; continue; }
            long long e = nodes[i];
            for (int j = 0; j < n; j++) {
                if (j == i || !cg->site[(size_t)i * nn + (size_t)j]) continue;
                if (!cg->splice[j]) continue;
                e = cg_sat_add(e, cg_sat_mul(cg->site[(size_t)i * nn + (size_t)j],
                                             cg->exp[j] - 1));
            }
            cg->exp[i]    = e;
            cg->splice[i] = e <= PCREC_MAX_SPLICE_NODES;
            done[i] = true;
            changed = true;
        }
        if (all) break;
        if (!changed)
            ctx_fail(cx, 0, "internal error: the subroutine splice-expansion "
                            "evaluation did not settle");
    }

    /* THE TOTAL. Lexical sites over the WHOLE tree — one walk, counted the way
     * the artifact's own stamp counts them. */
    int *lex = arena_alloc(&cx->arena, nn * sizeof *lex);
    for (int i = 0; i < n; i++) lex[i] = 0;
    { CgEdges e = { cg, arena_alloc(&cx->arena, nn), lex };
      memset(e.row, 0, nn);
      cg_walk(root, cg_edges, &e); }

    for (;;) {
        long long total = 0;
        for (int i = 0; i < n; i++)
            if (cg->splice[i])
                total = cg_sat_add(total, cg_sat_mul(lex[i], cg->exp[i] - 1));
        if (total <= PCREC_MAX_SPLICE_TOTAL) break;
        /* Drop the largest contributor; ties by descending target number, so
         * the rule is a function of the pattern and nothing else. */
        int worst = -1;
        long long worstc = -1;
        for (int i = 0; i < n; i++) {
            if (!cg->splice[i]) continue;
            long long c = cg_sat_mul(lex[i], cg->exp[i] - 1);
            if (c >= worstc) { worstc = c; worst = i; }
        }
        if (worst < 0) break;      /* nothing left to drop; unreachable */
        cg->splice[worst] = false;
    }

    cg_walk(root, cg_publish_link, cg);
}

/* [DD-13b.W1.3] see the call site in `pcrec_callgraph_build` for why this is
 * a separate walk and not a branch inside `cg_publish_link`. */
typedef struct { Ctx *cx; const struct CallGraph *cg; } CgDeliver;

static void cg_force_deliver_splice(void *ud, const Ast *a)
{
    const CgDeliver *d = ud;
    if (a->k != A_CALL || !a->u.call.delivers) return;
    const int i = cg_index(d->cg, a->u.call.target);
    if (i < 0)
        ctx_fail(d->cx, 0,
                 "internal error: a delivering call to group %d is not in the "
                 "call graph", a->u.call.target);
    /* A CALLEE THAT CANNOT BE SPLICED CANNOT BE DELIVERED FROM, and that is a
     * REFUSAL rather than a silent downgrade to a delivery that does not
     * happen. Two causes, and the message names which, because the two have
     * different answers: a CYCLE is a property of the definition (a spliced
     * recursive call is an infinite emitter), while the budget and the denial
     * flag are properties of this build. */
    if (a->u.call.link != CALL_SPLICE && !d->cg->splice[i]) {
        if (pcrec_callgraph_reaches(d->cg, i, i))
            ctx_fail(d->cx, 0,
                     "a delivering call names a RECURSIVE definition (group "
                     "%d); delivery needs the callee inlined AT THE SITE so "
                     "the site can keep what it matched, and a recursive "
                     "callee has no finite inlining. Call it plainly, or "
                     "deliver from a non-recursive definition that wraps it",
                     a->u.call.target);
        ctx_fail(d->cx, 0,
                 "a delivering call names a definition (group %d) this build "
                 "did not inline at the site, so there is nothing for the site "
                 "to keep: it exceeded the subroutine inlining budget, or "
                 "-fno-splice-calls denied it",
                 a->u.call.target);
    }
    ((Ast *)a)->u.call.link = CALL_SPLICE;
}

/* ---- WAVE A2's SECOND OBLIGATION, DISCHARGED BY MEASUREMENT --------------
 *
 * `mod_lookaround.c`'s `la_has_kreset` cannot see through a call: it runs
 * inside the PARSE HOOK, where it must, because that is the only place with a
 * pattern OFFSET to refuse at — and at that instant `u.call.body` is NULL and
 * a FORWARD call's target has not been parsed at all. Wave A2 recorded the
 * gap at the site and left this wave THREE answers: re-run the check after
 * resolution over the graph, refuse a call inside a lookaround body outright,
 * or MEASURE what 10.46 does with the combination.
 *
 * **THE THIRD ONE IS THE ANSWER, AND THE FIRST TWO ARE OVER-REJECTIONS.**
 * MEASURED on libpcre2 10.46 through the committed ctypes binding:
 *
 *     (?=(a\Kb))x                    REFUSED, error 199 — `\K` LEXICALLY
 *                                    inside the assertion, which is §2.7's
 *                                    rule and is unchanged
 *     (?=(?1))(a\Kb)      on "ab"    (1,2) g1=(0,2)   ACCEPTED
 *     (?=(?1))(a\Kb)      on "xab"   (2,3) g1=(1,3)
 *     (?=(?1))(a\Kb)c     on "abc"   (1,3) g1=(0,2)
 *     x(?=(?1))(a\Kb)     on "xab"   (2,3) g1=(1,3)
 *     (?!(?1))(a\Kb)c     on "abc"   NOMATCH
 *     ^(?:((?:a)\Kb)){0}(?=(?1))ab$  on "ab" (1,2)  — the ISOLATING cell,
 *                                    where the `\K` is reachable ONLY through
 *                                    the call inside the lookahead
 *
 * PCRE2's rule is LEXICAL. A `\K` reached THROUGH A CALL is not refused, and
 * an implementation that refused it would decline patterns 10.46 compiles.
 *
 * AND pcrec ALREADY REPRODUCES ALL SEVEN, which is what turns "do not refuse"
 * from a decision into a measurement: this lane built the check, measured the
 * oracle, then deleted the check and re-measured pcrec — 7 of 7 agreeing,
 * the isolating cell included. The reason is STRUCTURAL rather than lucky and
 * it is design §3.4(b)'s own: `W` excludes slots 0 and 1 BY CONSTRUCTION, so
 * a `\K` inside a callee survives the RETURN, and `vm_look`'s positive arm
 * restores the CURSOR from `SLOT_LOOK_POS` rather than slot 0, so it survives
 * the ASSERTION too. `\K` is a PATH FACT at both boundaries, which is exactly
 * what 10.46 measures it to be.
 *
 * SO THERE IS NO CHECK HERE, and this comment is what stands in its place —
 * because "no rule" is a CLAIM, and design §3.4(e2) makes the same point
 * about `\G`/`\A`/`\z` composing with a call: the absence of a rule is
 * something a panel should be able to check. The cells are in
 * `tests/recursion/kreset.rxt`. */

/* ------------------------------------------------------------------------- */

void pcrec_callgraph_build(Ctx *cx, Ast *root)
{
    const int ncap = (int)cx->ncap;

    cx->callgraph = NULL;

    /* WHICH TARGETS. One scan of the whole tree, which is also how "is there a
     * call at all" is answered — the early return below is what keeps a
     * call-free pattern's compile byte-identical to what it was before this
     * module, since nothing after it runs. */
    bool *named = arena_alloc(&cx->arena, (size_t)(ncap + 1) * sizeof *named);
    memset(named, 0, (size_t)(ncap + 1) * sizeof *named);
    CgScan sc = { ncap, named, 0 };
    cg_walk(root, cg_scan, &sc);
    if (sc.ncall == 0) return;

    struct CallGraph *cg = arena_alloc(&cx->arena, sizeof *cg);
    memset(cg, 0, sizeof *cg);
    for (int g = 0; g <= ncap; g++) if (named[g]) cg->ntarget++;
    cg->target = arena_alloc(&cx->arena, (size_t)cg->ntarget * sizeof *cg->target);
    cg->body   = arena_alloc(&cx->arena, (size_t)cg->ntarget * sizeof *cg->body);
    {
        int i = 0;
        for (int g = 0; g <= ncap; g++) if (named[g]) cg->target[i++] = g;
    }

    /* THE REGION ROOTS, over the FINAL tree — see this file's header. */
    const Ast **groot = arena_alloc(&cx->arena,
                                    (size_t)(ncap + 1) * sizeof *groot);
    memset(groot, 0, (size_t)(ncap + 1) * sizeof *groot);
    groot[0] = root;
    { CgRoots r = { ncap, groot }; cg_walk(root, cg_roots, &r); }

    { CgBind b = { cx, groot, ncap }; cg_walk(root, cg_bind, &b); }
    for (int i = 0; i < cg->ntarget; i++) cg->body[i] = groot[cg->target[i]];

    /* THE EDGES, then their TRANSITIVE CLOSURE by Warshall. The graph has one
     * node per DISTINCT CALLED GROUP, which is at most the group count, so the
     * cubic closure is bounded by the pattern's own group count and needs no
     * cap of its own — `PCREC_MAX_GROUP_DEPTH` and the parser's group
     * numbering already bound it. */
    const int n = cg->ntarget;
    /* `ntarget >= 1` here by construction (`sc.ncall > 0` implies at least one
     * target), and gcc cannot see it: without this the `n * n` allocation is
     * `-Wstringop-overflow=` at -O2, since a negative `int` widens to a size_t
     * near the top of the range. Written as an assertion rather than as a cast
     * so the impossible case fails loudly instead of allocating nothing. */
    if (n <= 0)
        ctx_fail(cx, 0, "internal error: call graph built with no target");
    const size_t nn = (size_t)n;
    cg->reach = arena_alloc(&cx->arena, nn * nn);
    memset(cg->reach, 0, nn * nn);
    /* [DD-14 wave G] The MULTIPLICITY beside the relation, filled by the same
     * walk so the two cannot disagree about which sites exist. */
    cg->site = arena_alloc(&cx->arena, nn * nn * sizeof *cg->site);
    memset(cg->site, 0, nn * nn * sizeof *cg->site);
    for (int i = 0; i < n; i++) {
        CgEdges e = { cg, cg->reach + (size_t)i * nn,
                          cg->site  + (size_t)i * nn };
        cg_walk(cg->body[i], cg_edges, &e);
    }
    for (int k = 0; k < n; k++)
        for (int i = 0; i < n; i++)
            if (cg->reach[(size_t)i * nn + (size_t)k])
                for (int j = 0; j < n; j++)
                    if (cg->reach[(size_t)k * nn + (size_t)j])
                        cg->reach[(size_t)i * nn + (size_t)j] = 1;
    cx->callgraph = cg;

    /* ---- [DD-14 wave G] THE LINKAGE (design §6.3) ------------------------
     *
     * BEFORE the two width fixpoints, and the order is not arbitrary: nothing
     * below reads `link`, but `src/opt/select_engine.c` does — it is what
     * separates "this pattern is structurally VM-only" from "this pattern has
     * an exact finite lowering and may carry a prefilter" (§8.1, §8.3) — and
     * this pass runs before engine selection precisely so that question has an
     * answer when it is asked. See `pcrec_callgraph_build`'s declaration. */
    cg_eligibility(cx, cg, root);

    /* ---- [DD-13b.W1.3] THE DELIVERING SITE'S FORCED SPLICE --------------
     *
     * AFTER eligibility and OUTSIDE it, so it runs on EVERY path — including
     * the `PCREC_NO_SPLICE_CALLS` early return, which never reaches
     * `cg_publish_link` at all. Putting the check inside that function was
     * the first shape and it had exactly that hole: under
     * `-fno-splice-calls` a delivering call would have kept `CALL_LINKAGE`
     * silently and delivered nothing, which is the failure this whole
     * mechanism exists to make impossible.
     *
     * KEYED ON THE FINAL `link` VALUE, which is the thing that actually
     * decides whether the site can keep anything, rather than on the
     * eligibility table that produced it. The denial flag, the cycle and the
     * size budget are three routes to one fact and this reads the fact.
     *
     * WHY DELIVERY NEEDS THE SPLICE, and it is TIMING rather than taste:
     * under `CALL_LINKAGE` the callee's SHARED region restores every slot in
     * its `W` at its own exit, BEFORE control reaches the caller's return
     * label (`vm_region`; `emit_vm.c`'s own note at the splice-save assertion
     * says the same thing from the other side) — so a copy at the site would
     * run after the callee's spans are already gone. Under `CALL_SPLICE` the
     * restore is emitted AT THE SITE, and a copy placed just before it sees
     * exactly what the callee matched.
     *
     * THIS IS THE RESERVED OPTION BEING TAKEN. §402-412 above declined
     * per-site splicing ON PURPOSE and reserved it — "Per-site remains
     * available and costs nothing structural: `link` is already a per-NODE
     * field" — and a delivering site is the consumer that earns it. The MIXED
     * state that section warns about (one callee with a spliced delivering
     * site and a shared region for its linkage sites) is now reachable;
     * `rgn_emit[i]` must stay TRUE for those linkage sites, and `vm_call`'s
     * "no emitted region" refusal is the loud detector if it ever does not. */
    { CgDeliver d = { cx, cg }; cg_walk(root, cg_force_deliver_splice, &d); }

    /* ---- THE `minw` FIXPOINT (design §4.4b) -----------------------------
     *
     * KLEENE ITERATION FROM INFINITY DOWNWARD, and the two halves of the
     * specification are two measured cells that no single cell implies:
     *
     *   `^(?(DEFINE)(?<g>(?&h)b)(?<h>x|(?&g)))(?&g)$` MATCHES "xb".."xbbbb".
     *      `g`'s ONLY branch is `(?&h)b`, so it has NO non-recursive branch at
     *      all — the withdrawn "least fixpoint over the non-recursive
     *      branches" gloss has nothing to minimise over, answers infinity, and
     *      the MRL prune then turns every one of those rows into NOMATCH.
     *   `^(?(DEFINE)(?<g>a(?&g)b))(?&g)$` matches NOTHING, at any length.
     *      There infinity IS the correct fixpoint, and a fix of the form
     *      "never answer infinity" would be wrong here.
     *
     * So infinity must be REACHABLE and must not be reached by an
     * approximation. `tests/recursion/mrl.rxt` carries both cells and is the
     * specification; neither alone is.
     *
     * AND `minw == infinity` IS A LEGAL COMPILE, not an error: `^(a(?1)b)$`
     * compiles on 10.46 and matches nothing, so a design that refused it would
     * diverge from the oracle for a convenience.
     *
     * TERMINATION AND THE ROUND BOUND. The values are non-increasing and
     * bounded below by 0, so the iteration terminates. The BOUND is Knuth's
     * generalisation of Dijkstra's argument for a superior-function system:
     * every arm of `pcrec_minw`'s recurrence is a sum, a min or a constant, so
     * each round settles at least one more target and `n` rounds suffice. The
     * loop runs `n + 1` and the extra round is ASSERTED to change nothing —
     * a bound that is merely believed is a bound that silently truncates a
     * fixpoint, and an under-run `minw` is an under-estimate (safe) while an
     * over-run one is impossible, so the assertion costs one round and buys
     * the claim. */
    {
        long long *val = arena_alloc(&cx->arena, nn * sizeof *val);
        for (int i = 0; i < n; i++) val[i] = PCREC_MINW_MAX;
        CgMinw m = { cg, val };
        for (int round = 0; round <= n; round++) {
            bool changed = false;
            cg_walk(root, cg_minw_publish, &m);
            for (int i = 0; i < n; i++) {
                long long nv = pcrec_minw(cg->body[i]);
                if (nv < val[i]) { val[i] = nv; changed = true; }
            }
            if (!changed) break;
            if (round == n)
                ctx_fail(cx, 0, "internal error: the subroutine minimum-width "
                                "fixpoint did not settle in %d rounds", n);
        }
        cg_walk(root, cg_minw_publish, &m);
    }

    /* ---- THE `maxw` FIXPOINT ([DD-14.LB]) — see cg_maxw_publish above --- */
    {
        long long *val = arena_alloc(&cx->arena, nn * sizeof *val);
        for (int i = 0; i < n; i++) val[i] = PCREC_W_UNBOUNDED;
        CgMaxw m = { cg, val };
        for (int round = 0; round <= n; round++) {
            bool changed = false;
            cg_walk(root, cg_maxw_publish, &m);
            for (int i = 0; i < n; i++) {
                long long nv = pcrec_maxw(cg->body[i]);
                if (nv < val[i]) { val[i] = nv; changed = true; }
            }
            if (!changed) break;
            if (round == n)
                ctx_fail(cx, 0, "internal error: the subroutine maximum-width "
                                "fixpoint did not settle in %d rounds", n);
        }
        cg_walk(root, cg_maxw_publish, &m);
    }
}

int pcrec_callgraph_ntargets(const struct CallGraph *cg)
{
    return cg ? cg->ntarget : 0;
}

int pcrec_callgraph_target(const struct CallGraph *cg, int i)
{
    return cg->target[i];
}

const Ast *pcrec_callgraph_body(const struct CallGraph *cg, int i)
{
    return cg->body[i];
}

int pcrec_callgraph_index(const struct CallGraph *cg, int target)
{
    return cg_index(cg, target);
}

bool pcrec_callgraph_reaches(const struct CallGraph *cg, int i, int j)
{
    return cg->reach[(size_t)i * (size_t)cg->ntarget + (size_t)j] != 0;
}

bool pcrec_callgraph_spliced(const struct CallGraph *cg, int i)
{
    return cg && cg->splice && cg->splice[i];
}
