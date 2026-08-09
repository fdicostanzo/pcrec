/* AST -> priority Thompson NFA. Split edges are ordered: t1 is the preferred
 * (higher-priority) branch, which is how greedy/lazy and alternation order
 * survive into the DFA (see docs/decisions.md D3).
 *
 * The builder can target any Nfa and compile the pattern REVERSED (concat
 * order flipped recursively) — the reverse machine finds match starts in the
 * D7 unanchored engine. nfa_wrap_unanchored() adds the lowest-priority start
 * self-loop that makes the forward machine search from every position while
 * preserving leftmost-first priority.
 *
 * R1 hardening: patch lists are arena-owned so ctx_fail cannot leak (R-3b);
 * A_CAT/A_ALT left spines are flattened iteratively so flat concatenations or
 * alternations of any length cannot overflow the C stack (R-2); remaining
 * recursion depth is bounded by the parser's group-nesting cap. */

#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

typedef struct { Ctx *cx; Nfa *nfa; bool rev; } NB;

/* Dangling out-edges are encoded as state*2 + slot (slot 0 = t1, 1 = t2). */
typedef struct { int *v; int n, cap; } Patch;

static void patch_push(NB *b, Patch *p, int enc)
{
    if (p->n == p->cap) {
        int ncap = p->cap ? p->cap * 2 : 8;
        int *nv = arena_alloc(&b->cx->arena, (size_t)ncap * sizeof(int));
        memcpy(nv, p->v, (size_t)p->n * sizeof(int));
        p->v = nv;
        p->cap = ncap;
    }
    p->v[p->n++] = enc;
}

static void patch_join(NB *b, Patch *dst, Patch *src)
{
    for (int i = 0; i < src->n; i++) patch_push(b, dst, src->v[i]);
    src->v = NULL;
    src->n = src->cap = 0;
}

typedef struct { int start; Patch out; } Frag;

static int nst(NB *b, NKind k)
{
    Nfa *nfa = b->nfa;
    if (nfa->n >= PCREC_MAX_NFA_STATES)
        ctx_fail(b->cx, 0, "pattern too large (NFA exceeds %d states)", PCREC_MAX_NFA_STATES);
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

static void patch_to(NB *b, Patch *p, int target)
{
    Nfa *nfa = b->nfa;
    for (int i = 0; i < p->n; i++) {
        int s = p->v[i] >> 1;
        if (p->v[i] & 1) nfa->st[s].t2 = target;
        else             nfa->st[s].t1 = target;
    }
    p->v = NULL;
    p->n = p->cap = 0;
}

static Frag compile_ast(NB *b, const Ast *a);

static Frag frag_single(NB *b, NKind k)
{
    int s = nst(b, k);
    Frag f = { s, {0} };
    patch_push(b, &f.out, s * 2);
    return f;
}

/* one X: split(preferred: X | skip) for greedy; reversed for lazy */
static Frag frag_opt(NB *b, const Ast *sub, bool greedy)
{
    Frag body = compile_ast(b, sub);
    int s = nst(b, N_SPLIT);
    Nfa *nfa = b->nfa;
    Frag f = { s, {0} };
    if (greedy) {
        nfa->st[s].t1 = body.start;
        patch_push(b, &f.out, s * 2 + 1);   /* skip edge dangles */
    } else {
        nfa->st[s].t2 = body.start;
        patch_push(b, &f.out, s * 2);
    }
    patch_join(b, &f.out, &body.out);
    return f;
}

/* X* : split(preferred: body | exit); body loops back to split */
static Frag frag_star(NB *b, const Ast *sub, bool greedy)
{
    int s = nst(b, N_SPLIT);
    Frag body = compile_ast(b, sub);
    Nfa *nfa = b->nfa;
    patch_to(b, &body.out, s);
    Frag f = { s, {0} };
    if (greedy) {
        nfa->st[s].t1 = body.start;
        patch_push(b, &f.out, s * 2 + 1);
    } else {
        nfa->st[s].t2 = body.start;
        patch_push(b, &f.out, s * 2);
    }
    return f;
}

static Frag frag_cat2(NB *b, Frag a, Frag c)
{
    patch_to(b, &a.out, c.start);
    Frag f = { a.start, c.out };
    return f;
}

static Frag compile_ast(NB *b, const Ast *a)
{
    switch (a->k) {
    case A_CLASS: {
        Frag f = frag_single(b, N_CLASS);
        memcpy(b->nfa->st[f.start].cls, a->cls, 32);
        return f;
    }
    case A_EMPTY: return frag_single(b, N_EPS);
    case A_BOL:   return frag_single(b, N_BOT);
    case A_EOL:   return frag_single(b, N_EOL);
    case A_CAT: {
        /* flatten the left-leaning spine iteratively (R-2); in reverse mode
         * the sequence order flips: rev(X·Y) = rev(Y)·rev(X) */
        int nsp = 0;
        const Ast *t = a;
        while (t->k == A_CAT) { nsp++; t = t->l; }
        const Ast **rs = arena_alloc(&b->cx->arena, (size_t)nsp * sizeof(Ast *));
        int i = nsp;
        t = a;
        while (t->k == A_CAT) { rs[--i] = t->r; t = t->l; }
        /* forward order: t, rs[0], ..., rs[nsp-1] */
        Frag f;
        if (!b->rev) {
            f = compile_ast(b, t);
            for (int j = 0; j < nsp; j++)
                f = frag_cat2(b, f, compile_ast(b, rs[j]));
        } else {
            f = compile_ast(b, rs[nsp - 1]);
            for (int j = nsp - 2; j >= 0; j--)
                f = frag_cat2(b, f, compile_ast(b, rs[j]));
            f = frag_cat2(b, f, compile_ast(b, t));
        }
        return f;
    }
    case A_ALT: {
        /* flatten, then chain splits so branch order = priority order */
        int nbr = 1;
        for (const Ast *t2 = a; t2->k == A_ALT; t2 = t2->l) nbr++;
        const Ast **br = arena_alloc(&b->cx->arena, (size_t)nbr * sizeof(Ast *));
        int i = nbr;
        const Ast *t2 = a;
        while (t2->k == A_ALT) { br[--i] = t2->r; t2 = t2->l; }
        br[0] = t2;
        Frag *fr = arena_alloc(&b->cx->arena, (size_t)nbr * sizeof(Frag));
        for (int j = 0; j < nbr; j++) fr[j] = compile_ast(b, br[j]);
        int cur = fr[nbr - 1].start;
        for (int j = nbr - 2; j >= 0; j--) {
            int s = nst(b, N_SPLIT);
            Nfa *nfa = b->nfa;
            nfa->st[s].t1 = fr[j].start;   /* earlier branch preferred */
            nfa->st[s].t2 = cur;
            cur = s;
        }
        Frag f = { cur, {0} };
        for (int j = 0; j < nbr; j++) patch_join(b, &f.out, &fr[j].out);
        return f;
    }
    case A_REP: {
        int rmin = a->rmin, rmax = a->rmax;
        if (rmin == 0 && rmax == 0) return frag_single(b, N_EPS);

        Frag f = { -1, {0} };
        for (int i = 0; i < rmin; i++) {
            Frag c = compile_ast(b, a->l);
            f = (f.start < 0) ? c : frag_cat2(b, f, c);
        }
        if (rmax < 0) {
            Frag s = frag_star(b, a->l, a->greedy);
            f = (f.start < 0) ? s : frag_cat2(b, f, s);
        } else {
            /* X{r,n} tail = chained optionals X?X?... — language-equivalent to
             * the nested form for span-only matching (captures revisit in M4) */
            for (int i = rmin; i < rmax; i++) {
                Frag o = frag_opt(b, a->l, a->greedy);
                if (f.start < 0) { f = o; continue; }
                patch_to(b, &f.out, o.start);
                f.out = o.out;
            }
        }
        return f;
    }
    }
    ctx_fail(b->cx, 0, "internal error: bad AST node");
}

void pcrec_build_nfa(Ctx *cx, Ast *root, Nfa *nfa, bool reverse)
{
    NB b = { cx, nfa, reverse };
    Frag f = compile_ast(&b, root);
    int acc = nst(&b, N_ACCEPT);
    patch_to(&b, &f.out, acc);
    nfa->start = f.start;
}

/* Lowest-priority start self-loop: new_start = SPLIT(pattern [preferred],
 * any-byte -> new_start). Threads from earlier subject positions always
 * outrank later ones, so D3's accept-pruning yields the leftmost-first
 * match end in one pass (D7). */
void nfa_wrap_unanchored(Ctx *cx, Nfa *nfa)
{
    NB b = { cx, nfa, false };
    int sp = nst(&b, N_SPLIT);
    int any = nst(&b, N_CLASS);
    memset(nfa->st[any].cls, 0xff, 32);   /* every byte, including \n */
    nfa->st[sp].t1 = nfa->start;
    nfa->st[sp].t2 = any;
    nfa->st[any].t1 = sp;
    nfa->start = sp;
}

bool nfa_has_asserts(const Nfa *nfa)
{
    for (int i = 0; i < nfa->n; i++)
        if (nfa->st[i].k == N_BOT || nfa->st[i].k == N_EOL) return true;
    return false;
}
