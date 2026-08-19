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
 * [M6.2 wave A] `\z` adds a THIRD view on the same machinery — `end_ok`,
 * true only at `pos == n`, where `$`/`\Z` are true at `n` AND before a final
 * newline. See make_state for the three-way canonicalization rule; it is the
 * one place in this file where getting the REFERENCE wrong (base instead of
 * the EOL view) costs byte-identity on every `$`-bearing pattern in the
 * corpus rather than costing correctness, which is exactly the kind of defect
 * a test suite full of correctness checks does not see.
 *
 * [M6.2 wave B] `\b`/`\B` add a fourth axis, and it is NOT a position view:
 * their truth depends on the two BYTES around the position, so the state
 * identity gains "the byte already consumed was a word character" and each
 * state gains a second closure for "the byte about to be consumed is one"
 * (`DState.up[UPC_WORD]`, `DState.wlist` in wave B's spelling). The class map
 * is refined by the word set so that bit is
 * constant inside a class, and the transition row for a class is then built
 * from the closure that class's word-ness selects — which is what keeps the
 * emitted hot path a single table read. See eqclasses, the Clo comment and
 * make_state.
 *
 * [M6.2 wave C] `(?m)` adds NO new machinery — it adds a second PROPERTY to
 * the two axes wave B built, which is why this file's diff for it is small.
 * `(?m)$` is true where the byte to the RIGHT is a newline, the axis `\b`'s
 * right-hand side already uses; `(?m)^` is true where the byte to the LEFT is
 * one, the axis `\b`'s left-hand side already uses. So the class axis stops
 * being a bool ("is a word character") and becomes the three-valued `UPC_*`
 * partition of the alphabet (see DState in core/internal.h), and the state
 * identity carries the same three values on the consumed side.
 *
 * THE ONE PLACE DIRECTION APPEARS is make_state's `reverse` mapping. `\b`'s
 * test is symmetric in its two operands, so wave B needed no notion of which
 * side was which; `(?m)$` is not symmetric — forward the byte it reads is the
 * one about to be CONSUMED, reverse it is the one already consumed — so the
 * closure names its two operands by SIDE (`left_*` / `right_*`) and exactly
 * one function maps a machine's consumed/upcoming pair onto them.
 *
 * `-DPCREC_NO_WORDCTX` compiles that axis out (`has_word` is pinned false, so
 * no refinement, no second closure, one interior start state, and the emitter
 * reproduces the pre-wave text). Same shape and same single consumer as the
 * two knobs below: tests/codegen/run_wordctx_identity.sh. Never defined in a
 * shipped build; under it a `\b` pattern compiles to something WRONG, which
 * is exactly why that script's control population must differ.
 *
 * `-DPCREC_NO_MLINECTX` compiles the NEWLINE half of the class axis out
 * (`has_nl` is pinned false, so no refinement by the newline set, no third
 * class view, and the emitter reproduces the pre-wave text). Same shape and
 * same single consumer as the knobs around it:
 * tests/codegen/run_mlinectx_identity.sh. Never defined in a shipped build;
 * under it a `(?m)$` pattern compiles to something WRONG — the assertion can
 * then only pass through `end_ok`, i.e. as `\z` — which is exactly why that
 * script's positive control cannot be silent.
 *
 * `-DPCREC_NO_ENDVAR` compiles the third view's INTERNING out (the closure
 * still runs; `endvar` stays -1, so `dfa_has_endvar` is false and the emitter
 * reproduces the pre-wave text). It exists for exactly one consumer,
 * tests/codegen/run_endvar_identity.sh, which builds a reference compiler
 * with it and diffs emitted C over the whole corpus — the same shape
 * `-DPCREC_NO_TRIE` has served since M2.8, and for the same reason: a
 * byte-identity claim wants a reference build, not a pinned historical
 * commit. It is never defined in a shipped build.
 *
 * Byte equivalence classes are computed per machine so transition tables are
 * ncls-wide instead of 256-wide. All scratch memory is arena-owned so
 * ctx_fail/longjmp cannot leak (R1 R-3a). */

#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

/* ---- byte equivalence classes ---- */

/* Refine the running partition by one byte set. Split out of eqclasses at
 * [M6.2 wave B] because the word set refines it too, and two hand copies of a
 * partition refinement is exactly the drift this project keeps recording. */
static int refine_by(Dfa *d, int ncls, const uint8_t *bits)
{
    int remap[256][2];
    for (int j = 0; j < ncls; j++) remap[j][0] = remap[j][1] = -1;
    int next = 0;
    for (int c = 0; c < 256; c++) {
        int in = cls_has(bits, (unsigned)c) ? 1 : 0;
        int *slot = &remap[d->clsmap[c]][in];
        if (*slot < 0) *slot = next++;
        d->clsmap[c] = (uint8_t)*slot;
    }
    return next;
}

/* [M6.2 wave B] `has_word` refines the partition by the WORD SET, and it must:
 * the context bit `\b` carries is "the byte was a word character", so a class
 * straddling the word boundary would make that bit non-constant inside a
 * class and the whole class-indexed scheme meaningless.
 *
 * IT IS AT MOST ONE EXTRA CLASS and that is measured, not argued
 * (assertions_design.md §3.4, min/median/max 0/+1/+2 over the 1030-pattern
 * `.rxt` corpus): a pattern's class map already separates the bytes the
 * pattern NAMES, so the only class that can straddle the word boundary is the
 * catch-all of bytes it never mentions.
 *
 * THE SET IS `pcrec_cls_word_esc` AND THERE IS NO SECOND SPELLING OF IT
 * ANYWHERE (§7.2 item 3). That table is what `\w` compiles from, it is
 * oracle-generated against libpcre2 and PC-4 re-measures it every run — and
 * whatever `\w` means, `\b` must agree with, which one definition with two
 * readers guarantees and two definitions cannot.
 *
 * [M6.2 wave C] THE NEWLINE SET REFINES IT ON EXACTLY THE SAME ARGUMENT, and
 * the set is `pcrec_cls_newline` — D64's ONE DEFINITION, consumed rather than
 * respelled as a `'\n'` comparison. It is the same oracle-generated table
 * `\N` compiles from, so `(?m)`'s idea of a line break and the rest of the
 * front end's cannot drift apart, and the day DD-11's typed definition lands
 * there is one table to rebind rather than a scatter of literals. */
static void eqclasses(Nfa *nfa, Dfa *d, bool has_word, bool has_nl)
{
    memset(d->clsmap, 0, 256);
    int ncls = 1;

    for (int i = 0; i < nfa->n; i++) {
        if (nfa->st[i].k != N_CLASS) continue;
        ncls = refine_by(d, ncls, nfa->st[i].cls);
    }
    if (has_word) ncls = refine_by(d, ncls, pcrec_cls_word_esc);
    if (has_nl)   ncls = refine_by(d, ncls, pcrec_cls_newline);
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
    /* [M6.2 wave A] may a `\z` (N_END) assertion pass here — the THIRD
     * position view, on top of `bot_ok`/`eol_ok`. The invariant the caller
     * owes is `end_ok => eol_ok`: every position at which `\z` holds is one
     * at which `$`/`\Z` holds too, so a closure with end_ok set and eol_ok
     * clear describes no position the machine can be in. make_state is the
     * only caller and it never spells that combination. */
    bool      end_ok;
    bool      bot_ok;
    /* [M6.2 wave B, renamed by SIDE in wave C] THE TWO BYTES AROUND THIS
     * POSITION, described in SUBJECT ORDER rather than in walk order.
     *
     *   `left_*`  — the byte at `pos - 1`, i.e. `s[pos-1]`;
     *   `right_*` — the byte at `pos`, i.e. `s[pos]`.
     *
     * Out of subject on either side reads as FALSE for both properties, which
     * is the truth for both consumers: out-of-subject is non-word (`\b` at
     * offset 0 and at `n`), and it is not a newline (`(?m)^` at offset 0 and
     * `(?m)$` at `n` are true for POSITION reasons, carried by `bot_ok` and
     * `end_ok`, never by a byte that is not there).
     *
     * Wave B named these `cons_word`/`up_word` — by WALK ORDER — and could,
     * because `\b` holds iff its two operands DIFFER and `\B` iff they AGREE:
     * both tests are SYMMETRIC, so a machine reading them backwards gets the
     * same answer. `(?m)$` broke that: it reads ONE side, so the two machines
     * must agree about which. Naming them by side puts the whole of the
     * direction question in make_state's one mapping and leaves every
     * assertion arm below reading like the assertion's own definition.
     *
     * Which side is a per-STATE fact and which is a per-CLASS parameter still
     * differs by machine, and that too is make_state's business: one of the
     * two is read off the class of the transition that built the state, the
     * other is the class about to be consumed, and make_state closes each
     * pre-set once per live class-axis context of the latter. */
    bool      left_word;
    bool      right_word;
    bool      left_nl;
    bool      right_nl;
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
                 * RESUMES rather than now. That ordering is deliberate: a
                 * walk that never gets back to the body -- because the exit
                 * branch reached ACCEPT and pruning cut everything below it
                 * -- never mints the body's context at all. */
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
            case N_END:
                if (!cl->end_ok) break;
                s = st->t1;
                continue;
            /* [M6.2 wave C] `(?m)^` / `(?m)$`. `bot_ok`/`end_ok` carry the
             * position half — there is no byte out there to ask about — and
             * the byte half is the class axis. Neither arm reads `eol_ok`:
             * `(?m)$` has nothing to do with "before a FINAL newline", which
             * is plain `$`'s rule and is what `\Z` keeps under `(?m)`.
             *
             * `(?m)^` IS NOT THE MIRROR OF `(?m)$`, AND THAT IS MEASURED, not
             * inferred. assertions_design.md §3.7 and §9.3 both state the
             * rule as "`pos == 0` or `s[pos-1] == '\n'`" and BOTH ARE WRONG:
             * PCRE2's multiline `^` "does not match after a newline that ends
             * the string". So the newline half is guarded by `!end_ok` —
             * `pos < n` — and the asymmetry is real rather than an accident
             * of one implementation:
             *
             *     (?m)^   on "a\n"   matches at 0 only, NOT at 2
             *     (?m)$   on "a\n"   matches at 1 AND at 2
             *
             * python3 `re` DISAGREES with PCRE2 here and reports (2,2) for
             * the first, which is docs/dev/upstream_issues.md U11's second
             * entry and the reason the `(?m)^` corpus blocks are pcre2-only.
             * Found by tests/assertions/run_mline_diff.sh at `startpos > 0`,
             * where an earlier match no longer masks it. */
            case N_BOT_M:
                if (!cl->bot_ok && !(cl->left_nl && !cl->end_ok)) break;
                s = st->t1;
                continue;
            case N_EOL_M:
                if (!cl->end_ok && !cl->right_nl) break;
                s = st->t1;
                continue;
            case N_WORDB:
                if (cl->left_word == cl->right_word) break;
                s = st->t1;
                continue;
            case N_NWORDB:
                if (cl->left_word != cl->right_word) break;
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

/* The two neighbouring bytes' properties, travelling as one value so adding a
 * property to the class axis is one field rather than two parameters at every
 * call site (which is what wave B's four-bool signature would have become). */
typedef struct {
    bool left_word, right_word, left_nl, right_nl;
} Sides;

static void closure(Nfa *nfa, const int *pre, int npre, bool bot_ok, bool eol_ok,
                    bool end_ok, Sides sd, bool prune,
                    CloScratch *sc, int *out, int *nout, bool *accept)
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
               out, 0, false, eol_ok, end_ok, bot_ok,
               sd.left_word, sd.right_word, sd.left_nl, sd.right_nl,
               prune };
    for (int i = 0; i < npre; i++) {
        if (prune && cl.accept) break;
        clo_walk(&cl, pre[i]);
    }
    *nout = cl.nout;
    *accept = cl.accept;
}

/* ---- state interning ---- */

/* [M6.2 wave B, one loop instead of two copies in wave C] EVERY class view
 * joins the key. Note this changes no state NUMBERING and therefore no
 * emitted byte on a machine without a class axis: a new state's index is
 * `d->n++`, i.e. insertion order, and the hash only picks which probe
 * sequence finds it. The per-view salt keeps the same list appearing in two
 * different views from cancelling. */
static uint32_t dhash(const DView *up, int eolvar, int endvar)
{
    uint32_t h = 2166136261u;
    for (int u = 0; u < UPC_N; u++) {
        for (int i = 0; i < up[u].nlist; i++) {
            h ^= (uint32_t)up[u].list[i];
            h *= 16777619u;
        }
        h ^= (uint32_t)up[u].accept + 0x9e37u + (uint32_t)u * 0x2545u;
        h *= 16777619u;
    }
    h ^= (uint32_t)(eolvar + 2);
    h *= 16777619u;
    h ^= (uint32_t)(endvar + 2);
    h *= 16777619u;
    return h;
}

static void tab_insert(Dfa *d, int idx)
{
    uint32_t h = dhash(d->st[idx].up, d->st[idx].eolvar, d->st[idx].endvar);
    size_t i = h & (d->tabcap - 1);
    while (d->tab[i] >= 0) i = (i + 1) & (d->tabcap - 1);
    d->tab[i] = idx;
}

static void tab_grow(Ctx *cx, Dfa *d)
{
    size_t newcap = d->tabcap ? d->tabcap * 2 : 256;
    free(d->tab);
    d->tab = malloc(newcap * sizeof(int));
    /* [M4.7b/K7] d->tab is already NULL here, so the Job's own cleanup frees
     * nothing twice; d->tabcap is stale but nothing reads it after a longjmp. */
    if (!d->tab) { d->tabcap = 0; ctx_nomem(cx); }
    for (size_t i = 0; i < newcap; i++) d->tab[i] = -1;
    d->tabcap = newcap;
    for (int s = 0; s < d->n; s++) tab_insert(d, s);
}

/* Are two class views the same closure? */
static bool view_same(const DView *a, const DView *b)
{
    return a->nlist == b->nlist && (bool)a->accept == (bool)b->accept &&
           (a->nlist == 0 ||
            memcmp(a->list, b->list, (size_t)a->nlist * sizeof(int)) == 0);
}

/* Intern a closed state (every view's list must already be a closure result).
 *
 * [M6.2 wave B] THE CLASS VIEWS ARE PART OF THE IDENTITY, not decoration hung
 * off it. That is what makes "the previous byte's class-axis context is part
 * of the state" true without a field to carry it: two pre-sets reached under
 * different contexts produce different closures wherever the context is live,
 * so they land here as different keys; where it is not live they produce the
 * same closures and MERGE, which is the whole reason §3.5's measured ratio is
 * 1.11x median rather than the theoretical 2x.
 *
 * [M6.2 wave C] The two hand-written view slots became a loop over `UPC_N`,
 * and the sharing rule generalized with it: a view whose closure equals an
 * EARLIER view's shares that view's storage, so a machine with no class axis
 * still allocates exactly one list per state and charges K7's budget exactly
 * once, as it did before either wave. */
static int intern(Ctx *cx, Dfa *d, const DView *up, int eolvar, int endvar)
{
    if (d->tabcap == 0 || (size_t)d->n * 2 >= d->tabcap) tab_grow(cx, d);
    uint32_t h = dhash(up, eolvar, endvar);
    size_t i = h & (d->tabcap - 1);
    while (d->tab[i] >= 0) {
        DState *s = &d->st[d->tab[i]];
        if (s->eolvar == eolvar && s->endvar == endvar) {
            int u = 0;
            while (u < UPC_N && view_same(&s->up[u], &up[u])) u++;
            if (u == UPC_N) return d->tab[i];
        }
        i = (i + 1) & (d->tabcap - 1);
    }

    if (d->n >= d->maxstates)
        ctx_fail(cx, 0, "pattern too complex for the DFA engine (>%d states; "
                 "try --engine=vm)", d->maxstates);
    /* Which views need storage of their own, and which alias an earlier one.
     * Computed BEFORE anything is spent so the K7 charge below counts exactly
     * the lists this state will really own. */
    int owner[UPC_N];
    for (int u = 0; u < UPC_N; u++) {
        owner[u] = u;
        for (int v = 0; v < u; v++)
            if (view_same(&up[v], &up[u])) { owner[u] = v; break; }
    }
    /* [M4.7b/K7] The PREDICTIVE half of the cap, charged per interned state
     * BEFORE its lists are copied. The state-count cap above bounds `d->n`;
     * the memory this construction actually spends is sum(nlist), and the two
     * come apart by a whole factor on exactly the shape K7 reports. See
     * PCREC_MAX_SUBSET_ELEMS.
     *
     * A view that is a SECOND list is charged too — K7's bound is on what the
     * construction spends, and a wave that multiplied the lists without
     * multiplying the charge would have widened the cap it never touched.
     * Zero extra on every machine with no class axis, where all three views
     * are one list. */
    for (int u = 0; u < UPC_N; u++)
        if (owner[u] == u) cx->subset_elems += up[u].nlist;
    if (cx->subset_elems > PCREC_MAX_SUBSET_ELEMS)
        ctx_fail(cx, 0, "pattern too complex for the DFA engine (subset "
                 "construction exceeds %lld state-set elements; "
                 "try --engine=vm)",
                 (long long)PCREC_MAX_SUBSET_ELEMS);
    if (d->n == d->cap) {
        int ncap = d->cap ? d->cap * 2 : 64;
        /* [M4.7b/K7] realloc into a TEMPORARY: on failure d->st still points at
         * the live array the Job owns and job_cleanup will free it. */
        DState *nst = realloc(d->st, (size_t)ncap * sizeof(DState));
        if (!nst) ctx_nomem(cx);
        d->st = nst;
        d->cap = ncap;
    }
    DState *s = &d->st[d->n];
    for (int u = 0; u < UPC_N; u++) {
        int n = up[u].nlist;
        s->up[u].nlist  = n;
        s->up[u].accept = up[u].accept;
        if (owner[u] != u) {
            s->up[u].list = s->up[owner[u]].list;
        } else {
            s->up[u].list =
                arena_alloc(&cx->arena, (size_t)(n ? n : 1) * sizeof(int));
            if (n) memcpy(s->up[u].list, up[u].list, (size_t)n * sizeof(int));
        }
    }
    s->eolvar = eolvar;
    s->endvar = endvar;
    s->tr = arena_alloc(&cx->arena, (size_t)d->ncls * sizeof(int));
    for (int c = 0; c < d->ncls; c++) s->tr[c] = -2; /* unfilled */
    d->tab[i] = d->n;
    return d->n++;
}

/* Per-MACHINE facts, hoisted once by pcrec_build_dfa rather than recomputed
 * per state. `reverse` is the ONLY place in this file that knows a machine has
 * a direction, and it exists because `(?m)$` reads ONE of the two neighbouring
 * bytes where `\b` reads both symmetrically — see sides_of.
 *
 * `reverse` is passed in rather than derived from `prune`. The two coincide
 * today (D7: the reverse machine is the non-pruning one) and deriving one from
 * the other would be a coincidence load-bearing for correctness. */
typedef struct {
    bool prune;
    bool reverse;
    bool has_end;             /* a `pos == n`-only view must be computed */
    bool upc_live[UPC_N];     /* class-axis contexts needing their own closure */
} Mach;

/* Map a machine's (consumed, upcoming) class-axis pair onto the SUBJECT-ORDER
 * pair the closure reads. The forward machine consumes leftward-to-rightward,
 * so the byte it has consumed is at `pos - 1`; the reverse machine consumes
 * rightward-to-leftward, so the byte it has consumed is at `pos` and the one
 * it is about to consume is at `pos - 1`. That single swap is the whole of
 * direction in the subset construction.
 *
 * "No byte on this side" — start of subject forward, end of subject reverse —
 * arrives here as UPC_PLAIN, which yields false for both properties: exactly
 * the out-of-subject rule `\b`, `(?m)^` and `(?m)$` all want. */
static Sides sides_of(const Mach *m, int cons_upc, int up_upc)
{
    int lft = m->reverse ? up_upc   : cons_upc;
    int rgt = m->reverse ? cons_upc : up_upc;
    Sides sd;
    sd.left_word  = (lft == UPC_WORD);
    sd.right_word = (rgt == UPC_WORD);
    sd.left_nl    = (lft == UPC_NL);
    sd.right_nl   = (rgt == UPC_NL);
    return sd;
}

/* Build (and intern) the DFA state for pre-closure set `pre`; -1 = dead.
 *
 * THREE POSITION VIEWS SINCE [M6.2] WAVE A, and the canonicalization rule
 * below is the whole of it (assertions_design.md §3.3, as CORRECTED by R30
 * E3 — the first draft got this wrong by one sentence and the correction is
 * the reason tests/codegen/run_endvar_identity.sh exists):
 *
 *     base = closure(eol_ok=F, end_ok=F)   the interior view
 *     eolv = closure(eol_ok=T, end_ok=F)   where `$`/`\Z` pass
 *     endv = closure(eol_ok=T, end_ok=T)   where `\z` passes too (pos == n)
 *
 *     eolvar = interned iff eolv != base   ; -1 means "same as base"
 *     endvar = interned iff endv != eolv   ; -1 means "SAME AS THE EOL VIEW"
 *
 * `endvar` is canonicalized against the EOL VIEW, not against the base, and
 * that is the load-bearing line. Compare it against the base instead and
 * every eol-differing state of every `$`-bearing pattern interns a live
 * endvar identical in content to its eolvar — so a `\z`-free pattern's tables
 * change, its artifact stops being byte-identical to the pre-wave one, and
 * the zero-regression property this convention buys is gone.
 *
 * WITH THE RULE AS WRITTEN THE PROPERTY HOLDS BY CONSTRUCTION, not by a flag:
 * a pattern with no `\z` has no N_END state, so `end_ok` gates nothing, so
 * `endv == eolv` at every state, so `endvar` is -1 everywhere, so
 * `dfa_has_endvar` is false and the emitter emits today's text. No `has_z`
 * conditional is needed anywhere.
 *
 * TIMES THE CLASS AXIS ([M6.2] wave B, three-valued since wave C): each of
 * those position views is closed once per LIVE class-axis context, so the
 * worst case is nine closures and the pre-wave corpus is still two. The
 * guards are what make that true and each is PROVABLE rather than prudent:
 *
 *  - `has_end` off: `end_ok` gates nothing (no N_END, no N_EOL_M), so the
 *    third position view equals the second at every pre-set, element for
 *    element. Running it anyway costs a third of the subset construction's
 *    closure work on every pattern in the corpus, which is what
 *    tests/resource/'s CPU budget caught on `[a-z]{0,30000}` (57.6 s against
 *    a 45 s cap) the first time this landed without the guard.
 *  - `upc_live[u]` off: nothing in the machine reads the property that
 *    distinguishes context `u` from UPC_PLAIN, so their closures coincide.
 *    Sharing the BUFFER makes intern's aliasing test true, so such a machine
 *    pays no closure, no arena and no `subset_elems` for the axis — which is
 *    the whole content of the byte-identity claim
 *    tests/codegen/run_wordctx_identity.sh gates. */
static int make_state(Ctx *cx, Nfa *nfa, Dfa *d, const Mach *m,
                      const int *pre, int npre, bool bot_ok, int cons_upc,
                      CloScratch *sc, int *scratch)
{
    enum { V_BASE = 0, V_EOL = 1, V_END = 2, V_N = 3 };
    DView vw[V_N][UPC_N];

    for (int v = 0; v < V_N; v++) {
        for (int u = 0; u < UPC_N; u++) {
            if (v == V_END && !m->has_end) {
                vw[v][u] = vw[V_EOL][u];
                continue;
            }
            if (u != UPC_PLAIN && !m->upc_live[u]) {
                vw[v][u] = vw[v][UPC_PLAIN];
                continue;
            }
            bool acc;
            int nout;
            int *buf = scratch + (size_t)(v * UPC_N + u) * nfa->n;
            /* end_ok implies eol_ok — the Clo.end_ok invariant. */
            closure(nfa, pre, npre, bot_ok, v >= V_EOL, v >= V_END,
                    sides_of(m, cons_upc, u), m->prune, sc, buf, &nout, &acc);
            vw[v][u].list   = buf;
            vw[v][u].nlist  = nout;
            vw[v][u].accept = acc;
        }
    }

    bool live = false;
    for (int v = 0; v < V_N && !live; v++)
        for (int u = 0; u < UPC_N && !live; u++)
            live = vw[v][u].accept || vw[v][u].nlist > 0;
    if (!live) return -1;

    /* A position view differs when ANY of its class-axis closures differs —
     * the §3.6.2 composition read as an interning rule. Comparing only the
     * UPC_PLAIN half would merge a state whose `$` view differs from its base
     * view solely in what a word byte (or a newline) may then do, and the
     * merge would be silent. */
    int eolvar = -1, endvar = -1;
    {
        int u = 0;
        while (u < UPC_N && view_same(&vw[V_BASE][u], &vw[V_EOL][u])) u++;
        if (u < UPC_N) eolvar = intern(cx, d, vw[V_EOL], -1, -1);
    }
#ifndef PCREC_NO_ENDVAR
    {
        int u = 0;
        while (u < UPC_N && view_same(&vw[V_EOL][u], &vw[V_END][u])) u++;
        if (u < UPC_N) endvar = intern(cx, d, vw[V_END], -1, -1);
    }
#endif

    return intern(cx, d, vw[V_BASE], eolvar, endvar);
}

void pcrec_build_dfa(Ctx *cx, Nfa *nfa, Dfa *d, bool prune, bool reverse,
                     int maxstates)
{
    /* Hoisted once per machine, like `has_end` below and for the same reason.
     * The ALPHABET refinement has to happen before eqclasses returns, so
     * these cannot wait until the worklist. */
    bool has_word = false, has_nl = false, has_end = false;
    for (int i = 0; i < nfa->n; i++) {
        switch (nfa->st[i].k) {
#ifndef PCREC_NO_WORDCTX
        case N_WORDB: case N_NWORDB: has_word = true; break;
#endif
        /* [M6.2 wave C] BOTH `(?m)` kinds refine by the newline set, and both
         * make the `pos == n` view live. `(?m)^` needs the refinement because
         * its operand is the byte to the LEFT — which is a per-CLASS fact of
         * the transition that built the state — and needs the `pos == n` view
         * for nothing, but asking for it costs one closure on a construct
         * that has already been routed to ENG_ATTEMPT. `(?m)$` needs both:
         * `end_ok` IS its "or end of subject" half. */
        case N_BOT_M:
        case N_EOL_M:
#ifndef PCREC_NO_MLINECTX
            has_nl = true;
#endif
            has_end = true;
            break;
        case N_END:   has_end = true; break;
        default: break;
        }
    }
    d->clsctx = has_word || has_nl;

    eqclasses(nfa, d, has_word, has_nl);
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

    /* [M6.2 wave A] THREE closure buffers, not two — make_state computes
     * base / eol / end views.
     * [M6.2 wave B] SIX: each of those three had a word-view twin.
     * [M6.2 wave C] NINE: the class axis is three-valued. Allocated for the
     * worst case and INDEXED by (view, class-context); the guards in
     * make_state decide how many are actually written. */
    int *scratch = arena_alloc(&cx->arena,
                               (size_t)nfa->n * 3 * UPC_N * sizeof(int));
    int *pre = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));

    Mach m = { prune, reverse, has_end, { true, has_word, has_nl } };

    int root = nfa->start;
    /* THE START STATES, and mechanism 4 is why there is more than one
     * (assertions_design.md §3.8). `s0` is the boundary context: there is no
     * byte on the far side at all — neither a word character nor a newline —
     * so it needs no twins. `s1u[]` are the interior contexts, chosen at
     * runtime from the seed byte's class: `s[startpos-1]` for the forward
     * machine, `s[end]` for the reverse one. Without them a search at
     * `startpos > 0` evaluates a leading `\b` as if the window were the whole
     * subject, which §3.8.1 measures diverging from libpcre2 on 5 of 10
     * cells; [M6.2 wave C] adds `(?m)^`'s own use of the same dispatch, where
     * the seed byte is INSIDE the window at every attempt but the first. */
    d->s0 = make_state(cx, nfa, d, &m, &root, 1, true, UPC_PLAIN, &sc, scratch);
    d->s1u[UPC_PLAIN] =
        make_state(cx, nfa, d, &m, &root, 1, false, UPC_PLAIN, &sc, scratch);
    for (int u = UPC_PLAIN + 1; u < UPC_N; u++)
        d->s1u[u] = m.upc_live[u]
            ? make_state(cx, nfa, d, &m, &root, 1, false, u, &sc, scratch)
            : d->s1u[UPC_PLAIN];

    /* worklist: any state (including EOL variants) with an unfilled row */
    for (int si = 0; si < d->n; si++) {
        for (int c = 0; c < d->ncls; c++) {
            if (d->st[si].tr[c] != -2) continue;
            uint8_t b = d->rep[c];
            /* [M6.2 wave B] The class decides BOTH halves of the context, and
             * this is the line that makes the class views free on the hot
             * path:
             *
             *  - which of the source state's closures may consume `b` — the
             *    one closed for `b`'s own class-axis context, because that IS
             *    the byte those threads are about to consume; and
             *  - the context the TARGET is closed under, which is the same
             *    fact one position later.
             *
             * Both are compile-time facts of the class, so the emitted
             * transition is the pre-wave single table read. */
            int cu = upc_of_class(d, c);
            /* Read the source list ONCE, here, and never across the
             * make_state below — that call can realloc `d->st` out from under
             * a held pointer, which is what the pre-wave code's re-read at
             * every access was guarding against. */
            const int *src = d->st[si].up[cu].list;
            int nsrc = d->st[si].up[cu].nlist;
            int npre = 0;
            for (int j = 0; j < nsrc; j++) {
                int ns = src[j];
                if (cls_has(nfa->st[ns].cls, b)) pre[npre++] = nfa->st[ns].t1;
            }
            int tgt = make_state(cx, nfa, d, &m, pre, npre, false, cu,
                                 &sc, scratch);
            d->st[si].tr[c] = tgt;
        }
    }
}
