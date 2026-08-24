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
    bool         *has_kreset; /* region i contains a `\K`, through calls */
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

/* Pass 3, per region: which targets does THIS subtree call, and does it
 * contain a `\K` lexically. One walk answers both. */
typedef struct {
    const struct CallGraph *cg;
    unsigned char *row;
    bool kreset;
} CgEdges;

static int cg_index(const struct CallGraph *cg, int t)
{
    for (int i = 0; i < cg->ntarget; i++) if (cg->target[i] == t) return i;
    return -1;
}

static void cg_edges(void *ud, const Ast *a)
{
    CgEdges *e = ud;
    if (a->k == A_KRESET) { e->kreset = true; return; }
    if (a->k != A_CALL) return;
    int i = cg_index(e->cg, a->u.call.target);
    if (i >= 0) e->row[i] = 1;
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

/* ---- the `\K`-through-a-call check (wave A2's second obligation) --------- */

typedef struct { const struct CallGraph *cg; bool hit; } CgKr;

static void cg_kreset_reach(void *ud, const Ast *a)
{
    CgKr *k = ud;
    if (a->k == A_KRESET) { k->hit = true; return; }
    if (a->k != A_CALL) return;
    int i = cg_index(k->cg, a->u.call.target);
    if (i >= 0 && k->cg->has_kreset[i]) k->hit = true;
}

typedef struct { Ctx *cx; const struct CallGraph *cg; } CgLook;

static void cg_look_check(void *ud, const Ast *a)
{
    CgLook *l = ud;
    if (a->k != A_LOOK) return;
    CgKr k = { l->cg, false };
    cg_walk(a->l, cg_kreset_reach, &k);
    if (!k.hit) return;
    /* §2.7's refusal, raised HERE because it cannot be raised where it belongs.
     *
     * `mod_lookaround.c`'s `la_has_kreset` runs INSIDE THE PARSE HOOK — it has
     * to, because that is the only place with a pattern OFFSET — and at that
     * instant `u.call.body` is NULL and a FORWARD call's target has not been
     * parsed at all. The question "does the callee hold a `\K`" is not merely
     * forbidden there by the back-edge rule, it is UNANSWERABLE there. That
     * arm's own comment (added by wave A2) demanded one of three answers from
     * this wave: re-run the check after resolution over the call graph, refuse
     * a call inside a lookaround body outright, or measure what 10.46 does.
     *
     * THIS IS THE FIRST, and it is the only one that does not refuse a legal
     * pattern: `(?=(?1))` where group 1 holds NO `\K` is ordinary and must
     * compile (design §3.4(e) measured a call inside a lookahead behaving as
     * the construct it is wrapped in).
     *
     * THE OFFSET IS 0 AND THAT IS A REPORTED LIMITATION, not a placeholder.
     * No `Ast` node carries a source position, and by the time the graph
     * exists neither the assertion nor the `\K` has one to give — the parse
     * hook's version names the ASSERTION's offset for the same reason one step
     * earlier. D26 puts pcrec's own offsets in tier 2 against pcrec's own
     * convention, and "offset 0" is the honest reading of "this pattern",
     * which is the scope of the fact. The WORDING names the route so a user
     * can find it, which is the part that helps. */
    ctx_fail(l->cx, 0,
             "\\K is not allowed inside a lookaround, and this one reaches a "
             "\\K through a subroutine call");
}

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
    cg->has_kreset = arena_alloc(&cx->arena, nn * sizeof *cg->has_kreset);
    memset(cg->has_kreset, 0, nn * sizeof *cg->has_kreset);
    for (int i = 0; i < n; i++) {
        CgEdges e = { cg, cg->reach + (size_t)i * nn, false };
        cg_walk(cg->body[i], cg_edges, &e);
        cg->has_kreset[i] = e.kreset;
    }
    for (int k = 0; k < n; k++)
        for (int i = 0; i < n; i++)
            if (cg->reach[(size_t)i * nn + (size_t)k])
                for (int j = 0; j < n; j++)
                    if (cg->reach[(size_t)k * nn + (size_t)j])
                        cg->reach[(size_t)i * nn + (size_t)j] = 1;
    /* `\K` reachability rides the same closure: a region reaches a `\K` if it
     * holds one lexically or reaches a region that does. */
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            if (cg->reach[(size_t)i * nn + (size_t)j] && cg->has_kreset[j])
                cg->has_kreset[i] = true;

    cx->callgraph = cg;

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

    /* ---- §2.7's `\K` REFUSAL, RE-ASKED THROUGH THE GRAPH ---------------- */
    { CgLook l = { cx, cg }; cg_walk(root, cg_look_check, &l); }
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
