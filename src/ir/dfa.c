/* Priority subset construction (leftmost-first, see docs/dev/decisions.md D3).
 *
 * A DFA state is a priority-ordered list of N_CLASS NFA states. With
 * `prune` on (forward machines), epsilon closure walks split edges in
 * preference order and stops the instant ACCEPT is reached — lower-priority
 * threads are pruned and the state is marked accepting. With `prune` off
 * (the D7 reverse machine), ACCEPT is recorded but closure continues: the
 * reverse scan must keep every thread alive to find the EARLIEST accepting
 * position (the match start), so priority pruning would be wrong there.
 *
 * `$` is handled by EOL-variant states (R1 S-C1/S-C2): every pre-set is
 * closed twice, once with EOL assertions blocked and once passable; when the
 * views differ, the EOL view is interned as its own state (`eolvar`) and the
 * generated code switches to it exactly at EOL positions.
 *
 * Byte equivalence classes are computed per machine so transition tables are
 * ncls-wide instead of 256-wide. All scratch memory is arena-owned so
 * ctx_fail/longjmp cannot leak (R1 R-3a). */

#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

/* ---- byte equivalence classes ---- */

static void eqclasses(Nfa *nfa, Dfa *d)
{
    memset(d->clsmap, 0, 256);
    int ncls = 1;

    for (int i = 0; i < nfa->n; i++) {
        if (nfa->st[i].k != N_CLASS) continue;
        const uint8_t *bits = nfa->st[i].cls;
        int remap[256][2];
        for (int j = 0; j < ncls; j++) remap[j][0] = remap[j][1] = -1;
        int next = 0;
        for (int c = 0; c < 256; c++) {
            int in = cls_has(bits, (unsigned)c) ? 1 : 0;
            int *slot = &remap[d->clsmap[c]][in];
            if (*slot < 0) *slot = next++;
            d->clsmap[c] = (uint8_t)*slot;
        }
        ncls = next;
    }
    d->ncls = ncls;
    for (int c = 255; c >= 0; c--) d->rep[d->clsmap[c]] = (uint8_t)c;
}

/* ---- epsilon closure ---- */

/* Closure visit marks. Stamping with a monotone generation makes a closure
 * cost O(states actually visited) instead of O(|NFA|): the pre-M2.8 code
 * memset both mark arrays on every call, and closure() runs once per
 * (DFA state x byte class) x2, so total work was Theta(|DFA|*ncls*|NFA|) --
 * the quadratic behind R2-A4's "200 -> 25.6 ms, 1000 -> 239 ms". */
typedef struct {
    uint32_t *mark;   /* [0,n) = seen */
    uint32_t  gen;
    int       n;
} Marks;

static void marks_next(Marks *mk)
{
    if (++mk->gen == 0) {   /* wrap: stale stamps could alias, so clear */
        memset(mk->mark, 0, (size_t)mk->n * sizeof(uint32_t));
        mk->gen = 1;
    }
}

/* ---- K18: the open-loop context, and the memo keyed on it ---------------
 *
 * PCRE's empty-iteration rule is a property of the WALK'S OWN PATH: arriving
 * by epsilon at a loop entry the path is already inside means the iteration
 * in progress consumed nothing, which ENDS the loop, so the walk follows the
 * loop's EXIT edge at that priority position. The pre-K18 closure asked a
 * DIFFERENT question -- "has any path in this closure touched this state" --
 * and the two coincide only when a closure's walk is a single path. It is a
 * DFS over a branching epsilon graph, so they do not: K1 and K17 repaired the
 * arrivals that LAND on a loop entry, and K18 was the arrival that has to
 * reach one THROUGH an already-seen ordinary epsilon state, which the global
 * memo killed one hop short. Read docs/dev/known_issues.md K17 and K18
 * together, and docs/design/k18_memo_design.md §1 for the traced example.
 *
 * The repair keys the memo on (state, OPEN-LOOP CONTEXT) and re-states the
 * redirect as "this loop is OPEN on my path". BOTH halves are needed and
 * neither is sufficient: the context key alone does not terminate, and the
 * open-path redirect alone reproduces the shipped compiler's wrong answers
 * cell for cell (note §1.4, measured both ways).
 *
 * A context is an INTERNED CHAIN, and it is the open-loop stack's ONLY
 * representation: ctx 0 is the empty stack, every other ctx is (parent ctx,
 * loop-entry state). Two consequences the design note calls load-bearing:
 *
 *  - the SET is the invariant ("is this loop open on the path that reached
 *    it?"); the ORDERED chain is the implementation, chosen because the
 *    redirect must truncate to the re-arrived loop's POSITION. They coincide
 *    exactly while loop nesting is proper, which it is today -- and
 *    DFA_INVARIANT below is the standing check on that coincidence, the only
 *    thing that would notice a future construct breaking it (note §2a,
 *    R23 S13).
 *  - the chain is IMMUTABLE, so a walk carries its whole open-loop stack in
 *    one int, and so does a deferred branch. The design's hardest prototype
 *    bug (R23 S3: a redirect crossing a frame boundary rewrote an ANCESTOR
 *    frame's open-loop entries and silently lost redirects) is not
 *    EXPRESSIBLE here: there is no entry to overwrite. */

/* Invariant checks that stay in the SHIPPED build. `abort()` is this file's
 * existing idiom for a condition that cannot happen (tab_grow, intern), and
 * unlike <assert.h> it cannot be compiled out by a caller's -DNDEBUG -- which
 * matters here, because both invariants below are premises of a TERMINATION
 * argument (note §3) rather than performance hints. Both are O(open-loop
 * depth), which the corpus measures at <= 4. */
#define DFA_INVARIANT(cond) do { if (!(cond)) abort(); } while (0)

typedef struct {
    int parent;   /* enclosing context; -1 marks the reserved empty id 0 */
    int loop;     /* the loop-entry state this context opens */
    int depth;    /* chain length; ctx 0 has depth 0 */
} LCtx;

typedef struct {
    Arena  *ar;
    LCtx   *v;
    int     n, cap;
    int    *tab;      /* open-addressed (parent,loop) -> id, -1 = empty */
    size_t  tabcap;
} LCtxTab;

/* Geometric regrow out of the ARENA rather than realloc(). Every table in
 * this section is a local of pcrec_build_dfa and intern() can ctx_fail (i.e.
 * longjmp) straight past it, so heap ownership here would leak on the error
 * path -- the rule this file's header states as R1 R-3a. Growth is geometric,
 * so the abandoned copies total less than one live table. */
static void *arena_regrow(Arena *ar, void *old, size_t oldsz, size_t newsz)
{
    void *p = arena_alloc(ar, newsz);
    if (oldsz) memcpy(p, old, oldsz);
    return p;
}

static size_t lctx_slot(const LCtxTab *t, int parent, int loop)
{
    uint64_t k = ((uint64_t)(uint32_t)parent << 32) | (uint32_t)loop;
    size_t i = (size_t)((k * 1099511628211ull) >> 20) & (t->tabcap - 1);
    while (t->tab[i] >= 0 &&
           !(t->v[t->tab[i]].parent == parent && t->v[t->tab[i]].loop == loop))
        i = (i + 1) & (t->tabcap - 1);
    return i;
}

static void lctx_rehash(LCtxTab *t)
{
    t->tabcap = t->tabcap ? t->tabcap * 2 : 256;
    t->tab = arena_alloc(t->ar, t->tabcap * sizeof(int));
    for (size_t i = 0; i < t->tabcap; i++) t->tab[i] = -1;
    for (int i = 1; i < t->n; i++)   /* id 0 is the empty stack: never a key */
        t->tab[lctx_slot(t, t->v[i].parent, t->v[i].loop)] = i;
}

/* The context reached by opening `loop` on top of `parent`. Interning makes
 * context equality one integer comparison, which is what lets the memo key be
 * two ints wide. */
static int lctx_intern(LCtxTab *t, int parent, int loop)
{
    if (t->n == 0) {                 /* reserve id 0 for the empty stack */
        t->cap = 64;
        t->v = arena_alloc(t->ar, (size_t)t->cap * sizeof(LCtx));
        t->v[0].parent = -1;
        t->v[0].loop = -1;
        t->v[0].depth = 0;
        t->n = 1;
    }
    if (t->tabcap == 0 || (size_t)(t->n + 1) * 2 >= t->tabcap) lctx_rehash(t);
    size_t slot = lctx_slot(t, parent, loop);
    if (t->tab[slot] >= 0) return t->tab[slot];
    if (t->n == t->cap) {
        int ncap = t->cap * 2;
        t->v = arena_regrow(t->ar, t->v, (size_t)t->cap * sizeof(LCtx),
                            (size_t)ncap * sizeof(LCtx));
        t->cap = ncap;
    }
    t->v[t->n].parent = parent;
    t->v[t->n].loop = loop;
    t->v[t->n].depth = t->v[parent].depth + 1;
    t->tab[slot] = t->n;
    return t->n++;
}

/* The nearest enclosing context that opened `s`, or -1. Walking the parent
 * chain IS the open-loop stack scan, and it visits entries innermost-first --
 * the order the redirect's truncate-to-this-loop's-position needs. */
static int lctx_find(const LCtxTab *t, int ctx, int s)
{
    while (ctx > 0) {
        if (t->v[ctx].loop == s) return ctx;
        ctx = t->v[ctx].parent;
    }
    return -1;
}

/* The (state, ctx) memo for NON-EMPTY contexts, generation-stamped so a
 * closure resets in O(1) exactly as the per-state mark array does. Contexts
 * are a property of the NFA's loop nesting, so the tables are per-DFA-build:
 * re-found on every closure, not rebuilt. */
typedef struct {
    Arena    *ar;
    uint64_t *key;    /* (state << 32) | ctx */
    uint32_t *gen;
    size_t    cap;
    size_t    used;   /* live entries THIS generation */
    uint32_t  g;
} PMemo;

static void pmemo_next(PMemo *m)
{
    m->used = 0;
    if (++m->g == 0) {          /* wrap: stale stamps could alias, so clear */
        if (m->cap) memset(m->gen, 0, m->cap * sizeof(uint32_t));
        m->g = 1;
    }
}

static size_t pmemo_slot(const PMemo *m, uint64_t k)
{
    size_t i = (size_t)((k * 1099511628211ull) >> 20) & (m->cap - 1);
    while (m->gen[i] == m->g && m->key[i] != k) i = (i + 1) & (m->cap - 1);
    return i;
}

/* The table MUST grow. A fixed-capacity open-addressed table whose live set
 * outgrows it does not merely slow down, it does not terminate: every slot
 * carries the current generation and none matches the key, so the probe never
 * finds a free one. The design lane's first prototype had exactly that bug and
 * it presented as a compile that ran forever at 17 nested nullable stars while
 * 16 finished instantly -- a cliff sharp enough to read as an algorithmic
 * explosion when it was a full hash table (note §7). */
static void pmemo_grow(PMemo *m)
{
    PMemo nm = *m;
    nm.cap = m->cap ? m->cap * 2 : 256;
    nm.key = arena_alloc(m->ar, nm.cap * sizeof(uint64_t));
    nm.gen = arena_alloc(m->ar, nm.cap * sizeof(uint32_t));  /* zeroed != g */
    for (size_t i = 0; i < m->cap; i++) {
        if (m->gen[i] != m->g) continue;
        size_t j = pmemo_slot(&nm, m->key[i]);
        nm.gen[j] = m->g;
        nm.key[j] = m->key[i];
    }
    *m = nm;
}

/* true if newly inserted, i.e. this (state, ctx) has not been expanded in
 * this closure. Allocated on first use: a pattern that never opens a loop
 * (353 of the corpus's 555, note §2a) never touches this table at all. */
static bool pmemo_add(PMemo *m, int s, int ctx)
{
    uint64_t k = ((uint64_t)(uint32_t)s << 32) | (uint32_t)ctx;
    if (m->cap == 0) pmemo_grow(m);
    size_t i = pmemo_slot(m, k);
    if (m->gen[i] == m->g) return false;
    if ((m->used + 1) * 2 >= m->cap) {
        pmemo_grow(m);
        i = pmemo_slot(m, k);
    }
    m->gen[i] = m->g;
    m->key[i] = k;
    m->used++;
    return true;
}

/* A DEFERRED BRANCH: the split edge the walk has not taken yet, with the
 * open-loop context it must resume under. This stack IS the recursion the
 * pre-K18 closure did with C frames, made explicit -- see clo_walk. */
typedef struct {
    int s;      /* NFA state to resume at */
    int ctx;    /* the context that branch runs in */
    int push;   /* loop entry to open on resume, or -1 */
} Cont;

typedef struct {
    Arena *ar;
    Cont  *v;
    size_t n, cap;
} ContStack;

static void cont_push(ContStack *k, int s, int ctx, int push)
{
    if (k->n == k->cap) {
        size_t ncap = k->cap ? k->cap * 2 : 128;
        k->v = arena_regrow(k->ar, k->v, k->cap * sizeof(Cont),
                            ncap * sizeof(Cont));
        k->cap = ncap;
    }
    k->v[k->n].s = s;
    k->v[k->n].ctx = ctx;
    k->v[k->n].push = push;
    k->n++;
}

/* Per-COMPILE closure scratch. THREAD SCOPING (note §5 item 11, TS-3): this
 * is an automatic local of pcrec_build_dfa (see its declaration) and every
 * buffer it holds comes from that compile's own arena, so two concurrent
 * pcrec_compile() calls share nothing here BY CONSTRUCTION. There is no
 * file-scope state in this file. Keep it that way: a cache across compiles is
 * the obvious temptation and it would need TS-3 run before it lands. */
typedef struct {
    Marks     seen;   /* ctx-0 memo: the pre-K18 per-state stamp array */
    Marks     emit;   /* global per-state dedup for the emitted thread list */
    PMemo     memo;   /* (state, ctx) memo, ctx != 0 only */
    LCtxTab   ctxs;
    ContStack ks;
} CloScratch;

typedef struct {
    Nfa      *nfa;
    LCtxTab  *ctxs;
    PMemo    *memo;
    ContStack *ks;
    uint32_t *seen0;   /* the empty-context fast path's stamp array */
    uint32_t *emitted; /* global per-state dedup for `out` */
    uint32_t  gen;     /* one generation for both arrays; see closure() */
    int      *out;
    int       nout;
    bool      accept;
    bool      eol_ok;
    bool      bot_ok;
    bool      prune;
} Clo;

/* Open loop `s` on top of `ctx`.
 *
 * §3 SETUP (ii), the termination argument's load-bearing premise, enforced
 * here: THE SET OF CONTEXTS IS FINITE, because a context is an open-loop
 * stack, the stack contains no repeats, and there are finitely many loop
 * states. "No repeats" is not a property of the NFA -- it is a property of
 * the WALK, and it holds only because a re-arrival at an already-open loop
 * REDIRECTS instead of pushing (clo_walk's first block). The invariant below
 * is that premise as a check rather than a parenthesis: with the open-set
 * test removed, the design's own half-prototype pushed a fresh copy of the
 * loop at every fresh context and did not terminate even with the stack
 * oversized 20,000x (R23 S5). It is NOT covered by the stack-top invariant at
 * the redirect, and vice versa: on the design lane's broken prototype the
 * stack-top check fired 358 times in 4,369 patterns while this one stayed
 * silent, and §3's proof rests on the one that stayed silent (R23 S9/S10). */
static int clo_open(Clo *cl, int ctx, int s)
{
    DFA_INVARIANT(lctx_find(cl->ctxs, ctx, s) < 0);
    return lctx_intern(cl->ctxs, ctx, s);
}

/* Walk the epsilon graph from `s` in preference order, emitting N_CLASS
 * states as a priority-ordered thread list.
 *
 * NO RECURSION AT ALL, which is a change from the pre-K18 closure and a
 * deliberate one (note §5 item 12, the rewrite lane's decision). That closure
 * recursed only on a split's PREFERRED branch, Theta(loop-nesting depth)
 * frames, because tail-position edges had already been made iterative (M2.8:
 * at -O0 gcc did not turn the t2 chain into a jump, and a 200000-branch
 * alternation segfaulted where 100000 survived). Keying the memo on the
 * context makes the SAME state descend once per context rather than once, and
 * the context count is itself ~d^2/2 -- MEASURED at 31,377 frames on 250
 * nested nullable stars, the deepest the parser accepts, against the old
 * closure's 253. That needs ~7 MB of the default 8 MB stack, and overflows
 * under AddressSanitizer at nesting depth 210.
 *
 * So the preferred-branch recursion becomes an explicit LIFO of deferred
 * branches, popped when a path dies. It is the same DFS in the same preorder
 * -- pushing t2 before descending t1 means everything t1 defers sits above
 * t2 and is popped first -- so the thread list is identical, which is checked
 * by emitted-source diff rather than argued. What changes is that C-stack
 * depth no longer depends on the pattern at all, the Theta(d^2) frames become
 * 12 bytes each of arena, and pcrec_compile() on a caller's thread stops
 * caring how big that thread's stack is (TS-3).
 *
 * Carrying `ctx` in the deferred branch is also what discharges the design's
 * hardest obligation for free: a redirect truncates the open-loop stack to a
 * depth that may be BELOW the point the deferred branch was created at, and
 * in a frame-based implementation the continuation then pushes over the
 * ancestor's entries and the ancestor's redirect scan reads the wrong loops
 * (R23 S3 -- a silently MISSED empty-iteration redirect, verbatim the defect
 * this code exists to repair). Here the branch's context is an immutable
 * interned chain that nothing can rewrite. */
static void clo_walk(Clo *cl, int s)
{
    int ctx = 0;   /* the empty open-loop stack */

    for (;;) {
        /* Descend the current path until it dies. */
        while (s >= 0) {
            const NState *st = &cl->nfa->st[s];

            /* PCRE's empty-iteration rule, as a property of the PATH: this
             * loop entry is already OPEN on the walk that reached it, so the
             * iteration in progress consumed nothing. End the loop HERE, at
             * this priority position, ahead of the body's lower-priority
             * consuming alternatives -- without it the exit/ACCEPT is only
             * reached after them and loses priority (R2-S1, K1).
             *
             * NOT A ONE-SHOT (K17): the rule is a property of the ARRIVAL,
             * not of the loop, so a second epsilon arrival at the same open
             * loop ends it exactly like the first. And not a `seen` test
             * (K18): "seen anywhere in this closure" is the same predicate
             * only when the closure's walk is a single path.
             *
             * The truncation is what bounds the walk (note §3): a redirect
             * pops the loop AND everything above it, so the open-loop depth
             * strictly decreases at every redirect, and an infinite walk
             * would have to be an infinite suffix of redirects. */
            if (st->loop && ctx != 0) {
                int at = lctx_find(cl->ctxs, ctx, s);
                if (at >= 0) {
                    /* THE OPEN LOOP IS THE STACK TOP. Correctness only asks
                     * for SET membership, and this code only relies on set
                     * membership -- but the chain that implements the set
                     * also carries an ORDER, and the two coincide only while
                     * loop nesting is proper. A construct that broke proper
                     * nesting would over-distinguish contexts (a cost bug)
                     * and truncate to the wrong position (a correctness bug),
                     * and this is the only thing that would notice. It is
                     * also the assertion the design note asked for on
                     * evidence that could not have failed: it read 0 across
                     * the lane's own corpora and fired on 358 of the panel's
                     * 4,369 patterns (R23 S10). */
                    DFA_INVARIANT(at == ctx);
                    ctx = cl->ctxs->v[at].parent;
                    s = st->exit_is_t2 ? st->t2 : st->t1;
                    continue;
                }
            }

            /* The memo. An empty open-loop stack makes (state, 0) and `state`
             * the same key, so the pre-K18 per-state stamp array is an EXACT
             * representation of the memo there, and one store instead of a
             * hash probe. That fast path is not an optimisation to taste: on
             * a fuzz-found pattern the design's prototype did byte-identical
             * work to the shipped compiler and still took 7x as long, all of
             * it one hash probe replacing one array access 15.7 million times
             * (note §2a). Nearly all traffic is here -- 353 of 555 corpus
             * patterns never leave ctx 0. */
            if (ctx == 0) {
                if (cl->seen0[s] == cl->gen) break;
                cl->seen0[s] = cl->gen;
            } else if (!pmemo_add(cl->memo, s, ctx)) {
                break;
            }

            switch (st->k) {
            case N_CLASS:
                /* A GLOBAL per-state dedup, deliberately not per-context: a
                 * thread's future depends only on its NFA state, so the first
                 * (highest-priority) occurrence is the only one that can
                 * matter. It is also what keeps `out` within its nfa->n
                 * scratch, which a context-split walk would otherwise
                 * overrun. */
                if (cl->emitted[s] != cl->gen) {
                    cl->emitted[s] = cl->gen;
                    cl->out[cl->nout++] = s;
                }
                break;
            case N_ACCEPT:
                cl->accept = true;
                /* With prune on, lower-priority threads are cut: nothing
                 * deferred can matter any more. This is the ONLY place accept
                 * becomes true, and closure() will not start another walk, so
                 * dropping the deferred branches here is the whole of the
                 * pre-K18 "if (prune && accept) return" unwinding. */
                if (cl->prune) { cl->ks->n = 0; return; }
                break;
            case N_EPS:
                s = st->t1;
                continue;
            case N_SPLIT:
                if (!st->loop) {
                    cont_push(cl->ks, st->t2, ctx, -1);
                    s = st->t1;
                    continue;
                }
                if (st->exit_is_t2) {
                    /* Greedy: t1 is the BODY, so it runs with the loop open;
                     * t2 leaves the loop and resumes at this context. */
                    cont_push(cl->ks, st->t2, ctx, -1);
                    ctx = clo_open(cl, ctx, s);
                    s = st->t1;
                    continue;
                }
                /* Lazy: t1 is the EXIT and runs at this context; t2 is the
                 * body, so the deferred branch opens the loop when it
                 * resumes. Opening it there rather than now is what keeps the
                 * context set identical to the recursive formulation's -- a
                 * path that never reaches the body never mints its context. */
                cont_push(cl->ks, st->t2, ctx, s);
                s = st->t1;
                continue;
            case N_BOT:
                if (!cl->bot_ok) break;
                s = st->t1;
                continue;
            case N_EOL:
                if (!cl->eol_ok) break;
                s = st->t1;
                continue;
            }
            break;   /* the path ends here */
        }

        /* Resume the highest-priority branch this walk deferred. */
        if (cl->ks->n == 0) return;
        Cont k = cl->ks->v[--cl->ks->n];
        s = k.s;
        ctx = k.ctx;
        if (k.push >= 0) ctx = clo_open(cl, ctx, k.push);
    }
}

static void closure(Nfa *nfa, const int *pre, int npre, bool bot_ok, bool eol_ok,
                    bool prune, CloScratch *sc, int *out, int *nout, bool *accept)
{
    marks_next(&sc->seen);
    /* The two stamp arrays advance in LOCKSTEP, which is what lets one `gen`
     * serve both. The 2^32 wrap is safe by inspection and will stay that way:
     * marks_next clears on wrap, both are cleared together, and nothing
     * reaches 2^32 closures in a compile -- a closure runs once per (DFA
     * state x byte class) x2 against DFA caps of 32,000 states. The invariant
     * is checked rather than commented because a future third array added to
     * only one side is exactly how this would break (note §5 item 13). */
    marks_next(&sc->emit);
    DFA_INVARIANT(sc->seen.gen == sc->emit.gen);
    pmemo_next(&sc->memo);
    sc->ks.n = 0;

    Clo cl = { nfa, &sc->ctxs, &sc->memo, &sc->ks,
               sc->seen.mark, sc->emit.mark, sc->seen.gen,
               out, 0, false, eol_ok, bot_ok, prune };
    for (int i = 0; i < npre; i++) {
        if (prune && cl.accept) break;
        clo_walk(&cl, pre[i]);
    }
    *nout = cl.nout;
    *accept = cl.accept;
}

/* ---- state interning ---- */

static uint32_t dhash(const int *list, int n, int accept, int eolvar)
{
    uint32_t h = 2166136261u;
    for (int i = 0; i < n; i++) {
        h ^= (uint32_t)list[i];
        h *= 16777619u;
    }
    h ^= (uint32_t)accept + 0x9e37u;
    h *= 16777619u;
    h ^= (uint32_t)(eolvar + 2);
    h *= 16777619u;
    return h;
}

static void tab_insert(Dfa *d, int idx)
{
    uint32_t h = dhash(d->st[idx].list, d->st[idx].nlist,
                       d->st[idx].accept, d->st[idx].eolvar);
    size_t i = h & (d->tabcap - 1);
    while (d->tab[i] >= 0) i = (i + 1) & (d->tabcap - 1);
    d->tab[i] = idx;
}

static void tab_grow(Dfa *d)
{
    size_t newcap = d->tabcap ? d->tabcap * 2 : 256;
    free(d->tab);
    d->tab = malloc(newcap * sizeof(int));
    if (!d->tab) abort();
    for (size_t i = 0; i < newcap; i++) d->tab[i] = -1;
    d->tabcap = newcap;
    for (int s = 0; s < d->n; s++) tab_insert(d, s);
}

/* Intern a closed state (list must already be a closure result). */
static int intern(Ctx *cx, Dfa *d, const int *list, int n, bool accept, int eolvar)
{
    if (d->tabcap == 0 || (size_t)d->n * 2 >= d->tabcap) tab_grow(d);
    uint32_t h = dhash(list, n, accept, eolvar);
    size_t i = h & (d->tabcap - 1);
    while (d->tab[i] >= 0) {
        DState *s = &d->st[d->tab[i]];
        if (s->nlist == n && (bool)s->accept == accept && s->eolvar == eolvar &&
            memcmp(s->list, list, (size_t)n * sizeof(int)) == 0)
            return d->tab[i];
        i = (i + 1) & (d->tabcap - 1);
    }

    if (d->n >= d->maxstates)
        ctx_fail(cx, 0, "pattern too complex for the DFA engine (>%d states; "
                 "VM engine arrives in M4)", d->maxstates);
    if (d->n == d->cap) {
        d->cap = d->cap ? d->cap * 2 : 64;
        d->st = realloc(d->st, (size_t)d->cap * sizeof(DState));
        if (!d->st) abort();
    }
    DState *s = &d->st[d->n];
    s->nlist = n;
    s->list = arena_alloc(&cx->arena, (size_t)(n ? n : 1) * sizeof(int));
    memcpy(s->list, list, (size_t)n * sizeof(int));
    s->accept = accept;
    s->eolvar = eolvar;
    s->tr = arena_alloc(&cx->arena, (size_t)d->ncls * sizeof(int));
    for (int c = 0; c < d->ncls; c++) s->tr[c] = -2; /* unfilled */
    d->tab[i] = d->n;
    return d->n++;
}

/* Build (and intern) the DFA state for pre-closure set `pre`; -1 = dead. */
static int make_state(Ctx *cx, Nfa *nfa, Dfa *d, bool prune,
                      const int *pre, int npre, bool bot_ok,
                      CloScratch *sc, int *scratch)
{
    int *scratch2 = scratch + nfa->n;
    int nout, nout2;
    bool accept, accept2;

    closure(nfa, pre, npre, bot_ok, false, prune, sc, scratch, &nout, &accept);
    closure(nfa, pre, npre, bot_ok, true, prune, sc, scratch2, &nout2, &accept2);

    if (!accept && !accept2 && nout == 0 && nout2 == 0) return -1;

    int eolvar = -1;
    if (accept2 != accept || nout2 != nout ||
        memcmp(scratch, scratch2, (size_t)nout * sizeof(int)) != 0)
        eolvar = intern(cx, d, scratch2, nout2, accept2, -1);

    return intern(cx, d, scratch, nout, accept, eolvar);
}

void pcrec_build_dfa(Ctx *cx, Nfa *nfa, Dfa *d, bool prune, int maxstates)
{
    eqclasses(nfa, d);
    /* R1 A-3: the binding constraint for table machines is total emitted
     * table entries (gcc time is flat in data size), not state count alone */
    d->maxstates = maxstates;
    if (d->maxstates > PCREC_MAX_TABLE_ENTRIES / d->ncls)
        d->maxstates = PCREC_MAX_TABLE_ENTRIES / d->ncls;

    /* Per-compile closure scratch: an automatic local, every buffer from this
     * compile's arena, nothing shared between compiles (see CloScratch).
     * Arena memory is zeroed, so generation 1 starts clean and the context
     * and memo tables start empty and allocate on first use. */
    CloScratch sc;
    memset(&sc, 0, sizeof sc);
    sc.seen.mark = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(uint32_t));
    sc.seen.n = nfa->n;
    sc.emit.mark = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(uint32_t));
    sc.emit.n = nfa->n;
    sc.memo.ar = sc.ctxs.ar = sc.ks.ar = &cx->arena;

    int *scratch = arena_alloc(&cx->arena, (size_t)nfa->n * 2 * sizeof(int));
    int *pre = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));

    int root = nfa->start;
    d->s0 = make_state(cx, nfa, d, prune, &root, 1, true, &sc, scratch);
    d->s1 = make_state(cx, nfa, d, prune, &root, 1, false, &sc, scratch);

    /* worklist: any state (including EOL variants) with an unfilled row */
    for (int si = 0; si < d->n; si++) {
        for (int c = 0; c < d->ncls; c++) {
            if (d->st[si].tr[c] != -2) continue;
            uint8_t b = d->rep[c];
            int npre = 0;
            /* d->st may move if make_state grows it: re-read each access */
            for (int j = 0; j < d->st[si].nlist; j++) {
                int ns = d->st[si].list[j];
                if (cls_has(nfa->st[ns].cls, b)) pre[npre++] = nfa->st[ns].t1;
            }
            int tgt = make_state(cx, nfa, d, prune, pre, npre, false, &sc, scratch);
            d->st[si].tr[c] = tgt;
        }
    }
}
