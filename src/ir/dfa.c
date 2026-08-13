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
    uint32_t *mark;   /* [0,n) = seen, [n,2n) = reent */
    uint32_t  gen;
    int       n;
} Marks;

static void marks_next(Marks *mk)
{
    if (++mk->gen == 0) {   /* wrap: stale stamps could alias, so clear */
        memset(mk->mark, 0, (size_t)mk->n * 2 * sizeof(uint32_t));
        mk->gen = 1;
    }
}

typedef struct {
    Nfa      *nfa;
    uint32_t *seen;
    uint32_t *reent;
    uint32_t  gen;
    int      *out;
    int       nout;
    bool      accept;
    bool      eol_ok;
    bool      bot_ok;
    bool      prune;
} Clo;

/* Every tail-position edge is a loop iteration rather than a call, so only a
 * split's PREFERRED branch still recurses. This matters because split chains
 * (alternations, bounded repeats) nest through t2: at -O2 gcc turned that into
 * a jump anyway, but at -O0 it did not, and a 200000-branch alternation
 * segfaulted where 100000 survived. Making it explicit lets the NFA cap be
 * derived from memory rather than from the optimiser's mood (M2.8). */
static void clo_visit(Clo *cl, int s)
{
    for (;;) {
        if (s < 0) return;
        if (cl->prune && cl->accept) return;
        if (cl->seen[s] == cl->gen) {
            /* PCRE empty-iteration rule: reaching a loop entry again by
             * epsilon means the iteration consumed nothing, which ENDS the
             * loop. Follow the exit edge once, here — at this priority
             * position, ahead of the loop body's lower-priority consuming
             * alternatives. Without this the exit/ACCEPT is only reached after
             * them and loses priority (R2 findings R2-S1 and K1). */
            const NState *ls = &cl->nfa->st[s];
            if (ls->loop && cl->reent[s] != cl->gen) {
                cl->reent[s] = cl->gen;
                s = ls->exit_is_t2 ? ls->t2 : ls->t1;
                continue;
            }
            return;
        }
        cl->seen[s] = cl->gen;
        const NState *st = &cl->nfa->st[s];
        switch (st->k) {
        case N_CLASS:  cl->out[cl->nout++] = s; return;
        case N_ACCEPT: cl->accept = true; return;
        case N_EPS:    s = st->t1; continue;
        case N_SPLIT:  clo_visit(cl, st->t1); s = st->t2; continue;
        case N_BOT:    if (!cl->bot_ok) return; s = st->t1; continue;
        case N_EOL:    if (!cl->eol_ok) return; s = st->t1; continue;
        }
        return;
    }
}

static void closure(Nfa *nfa, const int *pre, int npre, bool bot_ok, bool eol_ok,
                    bool prune, Marks *mk, int *out, int *nout, bool *accept)
{
    marks_next(mk);
    Clo cl = { nfa, mk->mark, mk->mark + nfa->n, mk->gen,
               out, 0, false, eol_ok, bot_ok, prune };
    for (int i = 0; i < npre; i++) {
        if (prune && cl.accept) break;
        clo_visit(&cl, pre[i]);
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
                      Marks *mk, int *scratch)
{
    int *scratch2 = scratch + nfa->n;
    int nout, nout2;
    bool accept, accept2;

    closure(nfa, pre, npre, bot_ok, false, prune, mk, scratch, &nout, &accept);
    closure(nfa, pre, npre, bot_ok, true, prune, mk, scratch2, &nout2, &accept2);

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

    Marks marks = {
        arena_alloc(&cx->arena, (size_t)nfa->n * 2 * sizeof(uint32_t)), 0, nfa->n
    };  /* arena memory is zeroed, so generation 1 starts clean */
    int *scratch = arena_alloc(&cx->arena, (size_t)nfa->n * 2 * sizeof(int));
    int *pre = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));

    int root = nfa->start;
    d->s0 = make_state(cx, nfa, d, prune, &root, 1, true, &marks, scratch);
    d->s1 = make_state(cx, nfa, d, prune, &root, 1, false, &marks, scratch);

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
            int tgt = make_state(cx, nfa, d, prune, pre, npre, false, &marks, scratch);
            d->st[si].tr[c] = tgt;
        }
    }
}
