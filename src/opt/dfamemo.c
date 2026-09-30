/* [OPT-RETRY-REUSE] The machine memo: a DFA built once per compile, not once
 * per retry attempt.
 *
 * `compile_driver` has ONE recovery point, so every retry ladder it runs —
 * [K53-SELRETRY]/[K59-PREMUL]'s drop rungs, [ART-SIZE]'s unroll ladder, the
 * [SEL-1]/[OPT-4] fallbacks — is a whole new pass of the pipeline over a fresh
 * arena. Most rungs change nothing a machine is BUILT from: dropping the
 * optional anchored machine, the premultiplied table's layout and the VM's
 * unroll K are all read after construction. K67 (`\p{L}+ -e utf8`) paid its
 * forward and reverse subset construction three times for one artifact.
 *
 * So the build is a pure function made explicit. `pcrec_build_min_dfa` looks
 * the machine up by EVERYTHING construction and minimization read, and on a
 * hit restores the stored machine instead of building it. Nothing is keyed on
 * which rung is running — a rung that changes a construction input (the
 * [OPT-4] collapsed NFA, a raised cap) misses on that input, by content, and
 * builds. That is the whole mechanism: no per-rung clause anywhere.
 *
 * THE KEY (entry_matches), and a new input must join it. `pcrec_build_dfa`
 * (src/ir/dfa.c) reads the NFA's states and count, its six parameters, and
 * four option fields: `encoding` (the context-set contributors), `engine` and
 * the two element budgets (`intern`'s refusals). It reads `subset_elems` as a
 * running budget, so the PRIOR value is keyed too: an identical machine
 * reached with more already charged might have been refused, and a hit must
 * mean "this build would have succeeded, with this machine". `minimize.c`
 * reads nothing but the machine. Nothing else is read; a reader added to
 * either file that this key does not name is a stale-memo miscompile, which
 * the identity gates (scripts/emit_sweep.py, scripts/cls_identity.py) are
 * what would see.
 *
 * THE VALUE is the minimized machine plus the `subset_elems` it charged, and
 * only a CLEAN build is stored: an optional machine that overflowed records
 * the overflow on `Ctx` as well as returning a partial machine, and a restore
 * cannot replay that, so it is simply not memoized (a mandatory machine's
 * overflow never returns here at all — it is a `pcrec_ctx_fail`).
 *
 * A RESTORE IS A DEEP COPY into the attempt's own storage, in the ownership
 * shape a fresh build leaves: `st` on the heap (job_cleanup frees it), every
 * per-state array in the attempt's arena, and no `tab` — the interning hash is
 * dead once construction ends (only `intern` reads it). */
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

struct DfaMemoEnt {
    DfaMemoEnt *next;
    /* the key */
    NState     *nst;             /* the NFA's states, copied */
    int         nn;
    int         root, maxstates;
    bool        prune, reverse, optional;
    int         encoding, engine;
    uint64_t    max_subset_elems, max_auto_dfa_elems;
    long long   subset_before;
    /* the value */
    Dfa         d;               /* every pointer into the memo's arena */
    long long   subset_charge;
};

/* True iff two NFA states are the same state, field by field (a memcmp would
 * also compare the struct's padding, which nothing initializes). */
static bool nstate_same(const NState *a, const NState *b)
{
    return a->k == b->k && a->t1 == b->t1 && a->t2 == b->t2 &&
           a->loop == b->loop && a->exit_is_t2 == b->exit_is_t2 &&
           a->ctxfn == b->ctxfn && memcmp(a->cls, b->cls, sizeof a->cls) == 0;
}

/* True iff entry `e` was built from exactly these inputs (see THE KEY). */
static bool entry_matches(const DfaMemoEnt *e, const Ctx *cx, const Nfa *nfa,
                          bool prune, bool reverse, int maxstates, int root,
                          bool optional)
{
    if (e->nn != nfa->n || e->root != root || e->maxstates != maxstates ||
        e->prune != prune || e->reverse != reverse || e->optional != optional ||
        e->encoding != cx->opt->encoding || e->engine != cx->opt->engine ||
        e->max_subset_elems != cx->opt->max_subset_elems ||
        e->max_auto_dfa_elems != cx->opt->max_auto_dfa_elems ||
        e->subset_before != cx->subset_elems)
        return false;
    for (int i = 0; i < nfa->n; i++)
        if (!nstate_same(&e->nst[i], &nfa->st[i])) return false;
    return true;
}

/* A copy of `n` bytes of `src` in arena `ar`, or NULL for a NULL/empty `src`. */
static void *arena_dup(Arena *ar, const void *src, size_t n)
{
    if (!src || !n) return NULL;
    void *p = pcrec_arena_alloc(ar, n);
    memcpy(p, src, n);
    return p;
}

/* Deep-copies machine `src` into `dst`: the state array into `st` (caller-
 * allocated, `src->n` entries), every per-state array into `ar`. Views of one
 * state that shared a list still share one copy. `tab` is left empty. */
static void dfa_copy(Dfa *dst, DState *st, const Dfa *src, Arena *ar)
{
    *dst = *src;
    dst->st = st;
    dst->cap = src->n;
    dst->tab = NULL;
    dst->tabcap = 0;
    for (int i = 0; i < src->n; i++) {
        const DState *o = &src->st[i];
        DState *s = &st[i];
        *s = *o;
        s->tr = arena_dup(ar, o->tr, (size_t)src->ncls * sizeof(int));
        s->up = arena_dup(ar, o->up, (size_t)src->natoms * sizeof(DView));
        if (!s->up) continue;
        for (int u = 0; u < src->natoms; u++) {
            int v = 0;
            while (v < u && o->up[v].list != o->up[u].list) v++;
            s->up[u].list = v < u ? s->up[v].list
                          : arena_dup(ar, o->up[u].list,
                                      (size_t)o->up[u].nlist * sizeof(int));
        }
    }
}

void pcrec_build_min_dfa(Ctx *cx, Nfa *nfa, Dfa *d, bool prune, bool reverse,
                         int maxstates, int root, bool optional)
{
    DfaMemo *m = cx->dfa_memo;
    for (const DfaMemoEnt *e = m ? m->head : NULL; e; e = e->next) {
        if (!entry_matches(e, cx, nfa, prune, reverse, maxstates, root, optional))
            continue;
        DState *st = malloc((size_t)(e->d.n ? e->d.n : 1) * sizeof(DState));
        if (!st) pcrec_ctx_nomem(cx);
        dfa_copy(d, st, &e->d, &cx->arena);
        cx->subset_elems += e->subset_charge;
        return;
    }

    const long long before = cx->subset_elems;
    pcrec_build_dfa(cx, nfa, d, prune, reverse, maxstates, root, optional);
    if (d->overflowed) return;   /* not minimized, and not memoized */
    pcrec_minimize_dfa(cx, d);
    if (!m) return;

    /* The entry is linked only once it is whole, so an allocation failure
     * part-way leaves the memo exactly as it was. */
    m->arena.cx = cx;
    DfaMemoEnt *e = pcrec_arena_alloc(&m->arena, sizeof *e);
    e->nst = arena_dup(&m->arena, nfa->st, (size_t)nfa->n * sizeof(NState));
    e->nn = nfa->n;
    e->root = root;
    e->maxstates = maxstates;
    e->prune = prune;
    e->reverse = reverse;
    e->optional = optional;
    e->encoding = cx->opt->encoding;
    e->engine = cx->opt->engine;
    e->max_subset_elems = cx->opt->max_subset_elems;
    e->max_auto_dfa_elems = cx->opt->max_auto_dfa_elems;
    e->subset_before = before;
    e->subset_charge = cx->subset_elems - before;
    DState *st = pcrec_arena_alloc(&m->arena,
                                   (size_t)(d->n ? d->n : 1) * sizeof(DState));
    dfa_copy(&e->d, st, d, &m->arena);
    e->next = m->head;
    m->head = e;
}

/* Frees every entry the memo holds; the memo is empty and reusable after. */
void pcrec_dfa_memo_free(DfaMemo *m)
{
    pcrec_arena_free(&m->arena);
    m->head = NULL;
}
