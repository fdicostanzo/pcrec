/* AST -> priority Thompson NFA. Split edges are ordered: t1 is the preferred
 * (higher-priority) branch, which is how greedy/lazy and alternation order
 * survive into the DFA (see docs/decisions.md D3).
 *
 * Checkpoint review R1 hardening: patch lists are arena-owned so a ctx_fail
 * longjmp cannot leak them (R-3b), and A_CAT/A_ALT left spines are flattened
 * iteratively so flat concatenations/alternations of any length cannot
 * overflow the C stack (R-2); remaining recursion depth is bounded by the
 * parser's group-nesting cap. */

#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

/* Dangling out-edges are encoded as state*2 + slot (slot 0 = t1, 1 = t2). */
typedef struct { int *v; int n, cap; } Patch;

static void patch_push(Ctx *cx, Patch *p, int enc)
{
    if (p->n == p->cap) {
        int ncap = p->cap ? p->cap * 2 : 8;
        int *nv = arena_alloc(&cx->arena, (size_t)ncap * sizeof(int));
        memcpy(nv, p->v, (size_t)p->n * sizeof(int));
        p->v = nv;
        p->cap = ncap;
    }
    p->v[p->n++] = enc;
}

static void patch_join(Ctx *cx, Patch *dst, Patch *src)
{
    for (int i = 0; i < src->n; i++) patch_push(cx, dst, src->v[i]);
    src->v = NULL;
    src->n = src->cap = 0;
}

typedef struct { int start; Patch out; } Frag;

static int nst(Ctx *cx, NKind k)
{
    Nfa *nfa = &cx->job->nfa;
    if (nfa->n >= PCREC_MAX_NFA_STATES)
        ctx_fail(cx, 0, "pattern too large (NFA exceeds %d states)", PCREC_MAX_NFA_STATES);
    if (nfa->n == nfa->cap) {
        nfa->cap = nfa->cap ? nfa->cap * 2 : 64;
        nfa->st = realloc(nfa->st, (size_t)nfa->cap * sizeof(NState));
        if (!nfa->st) abort();
    }
    NState *s = &nfa->st[nfa->n];
    memset(s, 0, sizeof(*s));
    s->k = k;
    s->t1 = s->t2 = -1;
    return nfa->n++;
}

static void patch_to(Ctx *cx, Patch *p, int target)
{
    Nfa *nfa = &cx->job->nfa;
    for (int i = 0; i < p->n; i++) {
        int s = p->v[i] >> 1;
        if (p->v[i] & 1) nfa->st[s].t2 = target;
        else             nfa->st[s].t1 = target;
    }
    p->v = NULL;
    p->n = p->cap = 0;
}

static Frag compile_ast(Ctx *cx, const Ast *a);

static Frag frag_eps(Ctx *cx)
{
    int s = nst(cx, N_EPS);
    Frag f = { s, {0} };
    patch_push(cx, &f.out, s * 2);
    return f;
}

/* one X: split(preferred: X | skip) for greedy; reversed for lazy */
static Frag frag_opt(Ctx *cx, const Ast *sub, bool greedy)
{
    Frag body = compile_ast(cx, sub);
    int s = nst(cx, N_SPLIT);
    Nfa *nfa = &cx->job->nfa;
    Frag f = { s, {0} };
    if (greedy) {
        nfa->st[s].t1 = body.start;
        patch_push(cx, &f.out, s * 2 + 1);   /* skip edge dangles */
    } else {
        nfa->st[s].t2 = body.start;
        patch_push(cx, &f.out, s * 2);
    }
    patch_join(cx, &f.out, &body.out);
    return f;
}

/* X* : split(preferred: body | exit); body loops back to split */
static Frag frag_star(Ctx *cx, const Ast *sub, bool greedy)
{
    int s = nst(cx, N_SPLIT);
    Frag body = compile_ast(cx, sub);
    Nfa *nfa = &cx->job->nfa;
    patch_to(cx, &body.out, s);
    Frag f = { s, {0} };
    if (greedy) {
        nfa->st[s].t1 = body.start;
        patch_push(cx, &f.out, s * 2 + 1);
    } else {
        nfa->st[s].t2 = body.start;
        patch_push(cx, &f.out, s * 2);
    }
    return f;
}

static Frag frag_cat2(Ctx *cx, Frag a, Frag b)
{
    patch_to(cx, &a.out, b.start);
    Frag f = { a.start, b.out };
    return f;
}

static Frag compile_ast(Ctx *cx, const Ast *a)
{
    switch (a->k) {
    case A_CLASS: {
        int s = nst(cx, N_CLASS);
        memcpy(cx->job->nfa.st[s].cls, a->cls, 32);
        Frag f = { s, {0} };
        patch_push(cx, &f.out, s * 2);
        return f;
    }
    case A_EMPTY: return frag_eps(cx);
    case A_BOL: {
        int s = nst(cx, N_BOT);
        Frag f = { s, {0} };
        patch_push(cx, &f.out, s * 2);
        return f;
    }
    case A_EOL: {
        int s = nst(cx, N_EOL);
        Frag f = { s, {0} };
        patch_push(cx, &f.out, s * 2);
        return f;
    }
    case A_CAT: {
        /* flatten the left-leaning spine iteratively (R-2: a flat 100k-char
         * literal must not recurse 100k deep) */
        int nsp = 0;
        const Ast *t = a;
        while (t->k == A_CAT) { nsp++; t = t->l; }
        const Ast **rs = arena_alloc(&cx->arena, (size_t)nsp * sizeof(Ast *));
        int i = nsp;
        t = a;
        while (t->k == A_CAT) { rs[--i] = t->r; t = t->l; }
        Frag f = compile_ast(cx, t);
        for (int j = 0; j < nsp; j++)
            f = frag_cat2(cx, f, compile_ast(cx, rs[j]));
        return f;
    }
    case A_ALT: {
        /* flatten, then chain splits so branch order = priority order */
        int nbr = 1;
        for (const Ast *t2 = a; t2->k == A_ALT; t2 = t2->l) nbr++;
        const Ast **br = arena_alloc(&cx->arena, (size_t)nbr * sizeof(Ast *));
        int i = nbr;
        const Ast *t2 = a;
        while (t2->k == A_ALT) { br[--i] = t2->r; t2 = t2->l; }
        br[0] = t2;
        Frag *fr = arena_alloc(&cx->arena, (size_t)nbr * sizeof(Frag));
        for (int j = 0; j < nbr; j++) fr[j] = compile_ast(cx, br[j]);
        int cur = fr[nbr - 1].start;
        for (int j = nbr - 2; j >= 0; j--) {
            int s = nst(cx, N_SPLIT);
            Nfa *nfa = &cx->job->nfa;
            nfa->st[s].t1 = fr[j].start;   /* earlier branch preferred */
            nfa->st[s].t2 = cur;
            cur = s;
        }
        Frag f = { cur, {0} };
        for (int j = 0; j < nbr; j++) patch_join(cx, &f.out, &fr[j].out);
        return f;
    }
    case A_REP: {
        int rmin = a->rmin, rmax = a->rmax;
        if (rmin == 0 && rmax == 0) return frag_eps(cx);

        Frag f = { -1, {0} };
        for (int i = 0; i < rmin; i++) {
            Frag c = compile_ast(cx, a->l);
            f = (f.start < 0) ? c : frag_cat2(cx, f, c);
        }
        if (rmax < 0) {
            Frag s = frag_star(cx, a->l, a->greedy);
            f = (f.start < 0) ? s : frag_cat2(cx, f, s);
        } else {
            /* X{r,n} tail = chained optionals X?X?... — language-equivalent to
             * the nested form for span-only matching (captures revisit in M4) */
            for (int i = rmin; i < rmax; i++) {
                Frag o = frag_opt(cx, a->l, a->greedy);
                if (f.start < 0) { f = o; continue; }
                patch_to(cx, &f.out, o.start);
                f.out = o.out;
            }
        }
        return f;
    }
    }
    ctx_fail(cx, 0, "internal error: bad AST node");
}

void pcrec_build_nfa(Ctx *cx, Ast *root)
{
    Frag f = compile_ast(cx, root);
    int acc = nst(cx, N_ACCEPT);
    patch_to(cx, &f.out, acc);
    cx->job->nfa.start = f.start;
}
