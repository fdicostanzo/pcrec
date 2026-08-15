#!/usr/bin/env python3
"""Prototype A — path-sensitive closure memo keyed on (state, open-loop-context).

MEASUREMENT ARTIFACT, NOT A PROPOSED PATCH. It rewrites src/ir/dfa.c inside a
SCRATCH COPY of the tree (see mkproto.sh); the worktree's own src/ is never
touched. The design note docs/design/k18_memo_design.md is the deliverable.

The rewrite:
  * an open-loop STACK is maintained along the walk's own path; entries are
    pushed when a loop entry's BODY edge is taken and dropped when the frame
    that pushed them returns or a redirect truncates the stack;
  * each stack prefix is INTERNED to a small integer context id, so the memo
    key (state, ctx) is two ints;
  * the empty-iteration redirect fires on "this loop entry is OPEN on my
    path", not on "this state has been seen somewhere in this closure";
  * N_CLASS emission and ACCEPT keep a separate GLOBAL per-state dedup, so a
    context-split walk cannot duplicate threads in the DFA state's list.

PCREC_K18_STATS=1 in the environment makes the compiler print one
`K18STATS ...` line per pcrec_build_dfa call on stderr.
"""
import re
import sys

path = sys.argv[1]
src = open(path).read()

# ---- 1. replace the Clo struct + clo_visit + closure -----------------------

old_start = src.index("typedef struct {\n    Nfa      *nfa;")
old_end = src.index("/* ---- state interning ---- */")
old = src[old_start:old_end]
assert "clo_visit" in old and "static void closure" in old, "anchor drift"

new = r'''
/* ==== PROTOTYPE A: path-sensitive closure memo (K18 measurement) ==========
 *
 * Open-loop contexts are interned: ctx 0 is the empty stack, and every other
 * ctx is (parent ctx, loop-entry state). Interning makes the memo key two
 * ints wide and makes context equality a single comparison. The table is
 * per-DFA-build, not per-closure: contexts are a property of the NFA's loop
 * nesting, so they are re-found, not rebuilt, on every closure. */
typedef struct { int parent; int loop; } LCtx;

typedef struct {
    LCtx  *v;
    int    n, cap;
} LCtxTab;

/* K18 measurement counters (PCREC_K18_STATS=1) */
typedef struct {
    long   closures;
    long   expansions;      /* (state,ctx) pairs expanded */
    long   visits;          /* clo_visit loop iterations */
    long   redirects;
    long   memo_probes;
    int    max_depth;
    int    max_ctx;         /* distinct contexts interned */
    long   nonstack_top;    /* redirects where the open loop was NOT stack top */
} K18Stats;

static K18Stats k18_stats;
static int k18_stats_on = -1;

static int lctx_intern(LCtxTab *t, int parent, int loop)
{
    for (int i = 0; i < t->n; i++)
        if (t->v[i].parent == parent && t->v[i].loop == loop) return i;
    if (t->n == t->cap) {
        t->cap = t->cap ? t->cap * 2 : 64;
        t->v = realloc(t->v, (size_t)t->cap * sizeof(LCtx));
        if (!t->v) abort();
    }
    t->v[t->n].parent = parent;
    t->v[t->n].loop = loop;
    return t->n++;
}

/* Open-addressed (state,ctx) memo, generation-stamped so a closure resets in
 * O(1) like the old per-state mark array did. */
typedef struct {
    uint64_t *key;    /* (state<<32)|ctx, +1 so 0 is empty */
    uint32_t *gen;
    size_t    cap;
    uint32_t  g;
} PMemo;

static void pmemo_init(PMemo *m, size_t want)
{
    size_t c = 1024;
    while (c < want * 4) c *= 2;
    m->cap = c;
    m->key = calloc(c, sizeof(uint64_t));
    m->gen = calloc(c, sizeof(uint32_t));
    if (!m->key || !m->gen) abort();
    m->g = 0;
}

static void pmemo_free(PMemo *m) { free(m->key); free(m->gen); }

static void pmemo_next(PMemo *m)
{
    if (++m->g == 0) {
        memset(m->gen, 0, m->cap * sizeof(uint32_t));
        m->g = 1;
    }
}

/* true if newly inserted (i.e. not already present this generation) */
static bool pmemo_add(PMemo *m, int s, int ctx)
{
    uint64_t k = ((uint64_t)(uint32_t)s << 32) | (uint32_t)ctx;
    size_t i = (size_t)((k * 1099511628211ull) >> 20) & (m->cap - 1);
    for (;;) {
        if (m->gen[i] != m->g) {
            m->gen[i] = m->g;
            m->key[i] = k;
            return true;
        }
        if (m->key[i] == k) return false;
        i = (i + 1) & (m->cap - 1);
    }
}

typedef struct { int loop; int ctx; } OpenEnt;

typedef struct {
    Nfa      *nfa;
    PMemo    *memo;
    LCtxTab  *ctxs;
    uint32_t *emit;    /* GLOBAL per-state dedup for N_CLASS output */
    uint32_t  gen;
    OpenEnt  *open;    /* the walk's own open-loop stack */
    int       depth;
    int       ctx;     /* interned id of open[0..depth) */
    int      *out;
    int       nout;
    bool      accept;
    bool      eol_ok;
    bool      bot_ok;
    bool      prune;
} Clo;

static void clo_visit(Clo *cl, int s)
{
    int save_depth = cl->depth;
    int save_ctx = cl->ctx;
    for (;;) {
        if (s < 0) break;
        if (cl->prune && cl->accept) break;
        if (k18_stats_on) k18_stats.visits++;

        const NState *st = &cl->nfa->st[s];

        /* --- the empty-iteration rule, now a property of the PATH --------
         * This loop entry is already OPEN on the walk that reached it, so the
         * iteration in progress consumed nothing: PCRE ends the loop here, at
         * this priority position, ahead of the body's consuming alternatives.
         * K17 read "already open" as "already seen anywhere in this closure",
         * which is the same predicate only when the closure's walk is a single
         * path. K18 is the case where it is not. */
        if (st->loop) {
            int at = -1;
            for (int i = cl->depth - 1; i >= 0; i--)
                if (cl->open[i].loop == s) { at = i; break; }
            if (at >= 0) {
                if (k18_stats_on) {
                    k18_stats.redirects++;
                    if (at != cl->depth - 1) k18_stats.nonstack_top++;
                }
                cl->depth = at;                                   /* pop L and anything above it */
                cl->ctx = at ? cl->open[at - 1].ctx : 0;
                s = st->exit_is_t2 ? st->t2 : st->t1;
                continue;
            }
        }

        if (k18_stats_on) k18_stats.memo_probes++;
        if (!pmemo_add(cl->memo, s, cl->ctx)) break;
        if (k18_stats_on) k18_stats.expansions++;

        switch (st->k) {
        case N_CLASS:
            if (cl->emit[s] != cl->gen) { cl->emit[s] = cl->gen; cl->out[cl->nout++] = s; }
            goto done;
        case N_ACCEPT: cl->accept = true; goto done;
        case N_EPS:    s = st->t1; continue;
        case N_SPLIT: {
            if (st->loop) {
                /* Push the loop only for the BODY edge. The preferred branch
                 * (t1) recurses and restores depth/ctx on return; the t2 tail
                 * stays iterative, and its push is unwound either by a
                 * redirect's truncation or by this frame's own return. */
                int body_is_t1 = st->exit_is_t2;   /* greedy: exit = t2, body = t1 */
                if (body_is_t1) {
                    cl->open[cl->depth].loop = s;
                    cl->ctx = lctx_intern(cl->ctxs, cl->ctx, s);
                    cl->open[cl->depth].ctx = cl->ctx;
                    cl->depth++;
                    if (k18_stats_on && cl->depth > k18_stats.max_depth)
                        k18_stats.max_depth = cl->depth;
                    clo_visit(cl, st->t1);
                    cl->depth--;
                    cl->ctx = cl->depth ? cl->open[cl->depth - 1].ctx : 0;
                    s = st->t2;
                    continue;
                }
                clo_visit(cl, st->t1);              /* t1 = exit (lazy) */
                cl->open[cl->depth].loop = s;
                cl->ctx = lctx_intern(cl->ctxs, cl->ctx, s);
                cl->open[cl->depth].ctx = cl->ctx;
                cl->depth++;
                if (k18_stats_on && cl->depth > k18_stats.max_depth)
                    k18_stats.max_depth = cl->depth;
                s = st->t2;
                continue;
            }
            clo_visit(cl, st->t1);
            s = st->t2;
            continue;
        }
        case N_BOT:    if (!cl->bot_ok) goto done; s = st->t1; continue;
        case N_EOL:    if (!cl->eol_ok) goto done; s = st->t1; continue;
        }
        break;
    }
done:
    cl->depth = save_depth;
    cl->ctx = save_ctx;
}

static void closure(Nfa *nfa, const int *pre, int npre, bool bot_ok, bool eol_ok,
                    bool prune, Marks *mk, PMemo *memo, LCtxTab *ctxs,
                    OpenEnt *openst, int *out, int *nout, bool *accept)
{
    marks_next(mk);
    pmemo_next(memo);
    if (k18_stats_on) k18_stats.closures++;
    Clo cl = { nfa, memo, ctxs, mk->mark, mk->gen, openst, 0, 0,
               out, 0, false, eol_ok, bot_ok, prune };
    for (int i = 0; i < npre; i++) {
        if (prune && cl.accept) break;
        clo_visit(&cl, pre[i]);
    }
    *nout = cl.nout;
    *accept = cl.accept;
}

'''

src = src[:old_start] + new + src[old_end:]

# ---- 2. thread the new state through make_state / pcrec_build_dfa ---------

src = src.replace(
    """static int make_state(Ctx *cx, Nfa *nfa, Dfa *d, bool prune,
                      const int *pre, int npre, bool bot_ok,
                      Marks *mk, int *scratch)
{""",
    """static int make_state(Ctx *cx, Nfa *nfa, Dfa *d, bool prune,
                      const int *pre, int npre, bool bot_ok,
                      Marks *mk, int *scratch,
                      PMemo *memo, LCtxTab *ctxs, OpenEnt *openst)
{""")

src = src.replace(
    """    closure(nfa, pre, npre, bot_ok, false, prune, mk, scratch, &nout, &accept);
    closure(nfa, pre, npre, bot_ok, true, prune, mk, scratch2, &nout2, &accept2);""",
    """    closure(nfa, pre, npre, bot_ok, false, prune, mk, memo, ctxs, openst, scratch, &nout, &accept);
    closure(nfa, pre, npre, bot_ok, true, prune, mk, memo, ctxs, openst, scratch2, &nout2, &accept2);""")

src = src.replace(
    """    int *pre = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));

    int root = nfa->start;""",
    """    int *pre = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));

    if (k18_stats_on < 0) k18_stats_on = getenv("PCREC_K18_STATS") ? 1 : 0;
    if (k18_stats_on) memset(&k18_stats, 0, sizeof k18_stats);
    PMemo memo; pmemo_init(&memo, (size_t)nfa->n);
    LCtxTab ctxs = { NULL, 0, 0 };
    lctx_intern(&ctxs, -1, -1);   /* id 0 = empty stack */
    OpenEnt *openst = arena_alloc(&cx->arena, (size_t)(nfa->n + 2) * sizeof(OpenEnt));

    int root = nfa->start;""")

src = src.replace(
    """    d->s0 = make_state(cx, nfa, d, prune, &root, 1, true, &marks, scratch);
    d->s1 = make_state(cx, nfa, d, prune, &root, 1, false, &marks, scratch);""",
    """    d->s0 = make_state(cx, nfa, d, prune, &root, 1, true, &marks, scratch, &memo, &ctxs, openst);
    d->s1 = make_state(cx, nfa, d, prune, &root, 1, false, &marks, scratch, &memo, &ctxs, openst);""")

src = src.replace(
    """            int tgt = make_state(cx, nfa, d, prune, pre, npre, false, &marks, scratch);
            d->st[si].tr[c] = tgt;
        }
    }
}""",
    """            int tgt = make_state(cx, nfa, d, prune, pre, npre, false, &marks, scratch, &memo, &ctxs, openst);
            d->st[si].tr[c] = tgt;
        }
    }

    if (k18_stats_on) {
        k18_stats.max_ctx = ctxs.n;
        fprintf(stderr,
                "K18STATS nfa=%d dfa=%d closures=%ld visits=%ld expansions=%ld "
                "redirects=%ld nonstacktop=%ld maxdepth=%d ctxs=%d\\n",
                nfa->n, d->n, k18_stats.closures, k18_stats.visits,
                k18_stats.expansions, k18_stats.redirects,
                k18_stats.nonstack_top, k18_stats.max_depth, k18_stats.max_ctx);
    }
    pmemo_free(&memo);
    free(ctxs.v);
}""")

src = src.replace('#include <stdlib.h>\n#include <string.h>',
                  '#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>')
src = src.replace('#include "core/internal.h"',
                  '#include "core/internal.h"\n#include "core/limits.h"')

open(path, "w").write(src)
print("proto A applied to", path)
