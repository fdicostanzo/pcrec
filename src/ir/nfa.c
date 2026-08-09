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
        if (p->n) memcpy(nv, p->v, (size_t)p->n * sizeof(int)); /* memcpy from
                    NULL is UB even with length 0 (R2 robustness NIT-1) */
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

/* X* : split(preferred: body | exit); body loops back to split */
static Frag frag_star(NB *b, const Ast *sub, bool greedy)
{
    int s = nst(b, N_SPLIT);
    Frag body = compile_ast(b, sub);
    Nfa *nfa = b->nfa;
    patch_to(b, &body.out, s);
    Frag f = { s, {0} };
    nfa->st[s].loop = 1;
    nfa->st[s].exit_is_t2 = greedy;
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

/* ---- M2.8: priority-preserving prefix trie for flat alternations ----
 *
 * Motivation (R2-A4) is compile TIME more than NFA size. `nfa_wrap_unanchored`
 * keeps the whole branch-selection split chain live at every subject position,
 * so a flat alternation makes every epsilon closure walk all `nbr` branches:
 * measured 4045 NFA visits per closure at 2000 branches (2*nbr), 2.36 billion
 * visits total, 11 s. Factoring shared prefixes collapses the start closure to
 * the node fan-out — measured 103.5 visits per closure on the same input.
 * State count alone falls only ~19% on prefix-poor inputs, which is why the
 * NFA cap is re-derived separately rather than being fixed by this.
 *
 * The hazard is priority: naive trie DFS order is NOT alternation index order.
 * Two independent counter-examples, both CONFIRMED against python `re` and
 * against pcrec's own flat construction:
 *
 *   abc|a|abd            on "abd" -> [0,1)   but  a(?:bc|bd)|a   -> [0,3)
 *   [ab]p|[bc]x|[ab]xy   on "bxy" -> [0,2)   but  [ab](?:p|xy)|[bc]x -> [0,3)
 *
 * The first is fixed by rule 1 (partition the branch list by index around a
 * branch that ends here), the second by the disjointness guard on rule 2
 * (branches merge only on bit-IDENTICAL classes, but two distinct groups can
 * still overlap, and then they are not mutually exclusive). */

/* One trie-eligible branch: its class bitmaps in match order (already
 * reversed by the caller in reverse mode) plus its alternation index, which
 * exists only to keep rule 1's partitions in priority order. */
typedef struct { const uint8_t *seq; int len; } TItem;

enum { TRIE_MAX_RDEPTH = 4096 };  /* nested branch points; flat beyond */

/* Chain fragments into a priority-ordered alternation; fr[0] is preferred.
 * Same shape the flat A_ALT path builds, so it is order-for-order identical
 * when the trie degenerates. */
static Frag chain_alts(NB *b, Frag *fr, int n)
{
    int cur = fr[n - 1].start;
    for (int j = n - 2; j >= 0; j--) {
        int s = nst(b, N_SPLIT);
        Nfa *nfa = b->nfa;
        nfa->st[s].t1 = fr[j].start;
        nfa->st[s].t2 = cur;
        cur = s;
    }
    Frag f = { cur, {0} };
    for (int j = 0; j < n; j++) patch_join(b, &f.out, &fr[j].out);
    return f;
}

/* Emit items[k].seq[depth..len) as a class chain; len == depth yields N_EPS
 * (the branch accepts here, so its out-edge dangles immediately). */
static Frag trie_tail(NB *b, const TItem *it, int depth)
{
    if (it->len == depth) return frag_single(b, N_EPS);
    Frag f = { -1, {0} };
    for (int k = depth; k < it->len; k++) {
        int s = nst(b, N_CLASS);
        memcpy(b->nfa->st[s].cls, it->seq + (size_t)k * 32, 32);
        Frag c = { s, {0} };
        patch_push(b, &c.out, s * 2);
        f = (f.start < 0) ? c : frag_cat2(b, f, c);
    }
    return f;
}

/* The pre-M2.8 shape for a sub-list: a split chain over unfactored suffixes.
 * Always safe, so it is the escape hatch for both the recursion cap and the
 * disjointness guard. */
static Frag trie_flat(NB *b, const TItem *items, int n, int depth)
{
    Frag *fr = arena_alloc(&b->cx->arena, (size_t)n * sizeof(Frag));
    for (int j = 0; j < n; j++) fr[j] = trie_tail(b, &items[j], depth);
    return n == 1 ? fr[0] : chain_alts(b, fr, n);
}

/* True iff every group's class bitmap is pairwise disjoint from every other's.
 * Singletons (one bit set) are distinct by construction — that is the keyword
 * case and the only one that has to be fast. */
static bool groups_disjoint(const TItem *sorted, const int *gstart, int ng, int depth)
{
    bool all_singleton = true;
    for (int g = 0; g < ng && all_singleton; g++) {
        const uint8_t *bits = sorted[gstart[g]].seq + (size_t)depth * 32;
        int pop = 0;
        for (int i = 0; i < 32 && pop < 2; i++) pop += __builtin_popcount(bits[i]);
        if (pop != 1) all_singleton = false;
    }
    if (all_singleton) return true;
    if (ng > 64) return false;   /* quadratic check not worth it; use flat */
    for (int g = 0; g < ng; g++)
        for (int h = g + 1; h < ng; h++) {
            const uint8_t *x = sorted[gstart[g]].seq + (size_t)depth * 32;
            const uint8_t *y = sorted[gstart[h]].seq + (size_t)depth * 32;
            for (int i = 0; i < 32; i++)
                if (x[i] & y[i]) return false;
        }
    return true;
}

static Frag trie_build(NB *b, const TItem *items, int n, int depth, int rdepth)
{
    Frag head = { -1, {0} };
    if (rdepth >= TRIE_MAX_RDEPTH) return trie_flat(b, items, n, depth);

    for (;;) {
        if (n == 1) {
            Frag t = trie_tail(b, &items[0], depth);
            return (head.start < 0) ? t : frag_cat2(b, head, t);
        }

        /* rule 1: some branch ENDS here. Partition the list by index around
         * it — everything before it, its accept, then everything after — so
         * no ordering has to serve two different matching chains at once. */
        int acc = -1;
        for (int k = 0; k < n; k++)
            if (items[k].len == depth) { acc = k; break; }
        if (acc >= 0) {
            Frag parts[3];
            int np = 0;
            if (acc > 0)
                parts[np++] = trie_build(b, items, acc, depth, rdepth + 1);
            parts[np++] = frag_single(b, N_EPS);
            if (acc < n - 1)
                parts[np++] = trie_build(b, items + acc + 1, n - acc - 1,
                                         depth, rdepth + 1);
            Frag body = (np == 1) ? parts[0] : chain_alts(b, parts, np);
            return (head.start < 0) ? body : frag_cat2(b, head, body);
        }

        /* rule 2: group by the class bitmap at `depth`, stable in index order
         * so groups come out ordered by their lowest index. */
        int *gstart = arena_alloc(&b->cx->arena, (size_t)n * sizeof(int));
        int *gcount = arena_alloc(&b->cx->arena, (size_t)n * sizeof(int));
        TItem *sorted = arena_alloc(&b->cx->arena, (size_t)n * sizeof(TItem));
        bool *used = arena_alloc(&b->cx->arena, (size_t)n);
        int ng = 0, m = 0;
        for (int k = 0; k < n; k++) {
            if (used[k]) continue;
            const uint8_t *key = items[k].seq + (size_t)depth * 32;
            gstart[ng] = m;
            int cnt = 0;
            for (int j = k; j < n; j++) {
                if (used[j]) continue;
                if (memcmp(items[j].seq + (size_t)depth * 32, key, 32) != 0) continue;
                used[j] = true;
                sorted[m++] = items[j];
                cnt++;
            }
            gcount[ng++] = cnt;
        }

        /* Distinct groups may still OVERLAP (`[ab]` vs `[bc]`), and then they
         * are not mutually exclusive, so no fixed order between them is right
         * for every subject. Only disjoint groups may be reordered. */
        if (ng > 1 && !groups_disjoint(sorted, gstart, ng, depth)) {
            Frag body = trie_flat(b, items, n, depth);
            return (head.start < 0) ? body : frag_cat2(b, head, body);
        }

        if (ng == 1) {   /* unbranched run: descend iteratively, no recursion */
            int s = nst(b, N_CLASS);
            memcpy(b->nfa->st[s].cls, items[0].seq + (size_t)depth * 32, 32);
            Frag c = { s, {0} };
            patch_push(b, &c.out, s * 2);
            head = (head.start < 0) ? c : frag_cat2(b, head, c);
            items = sorted;
            depth++;
            continue;
        }

        Frag *fr = arena_alloc(&b->cx->arena, (size_t)ng * sizeof(Frag));
        for (int g = 0; g < ng; g++) {
            const TItem *gi = sorted + gstart[g];
            int s = nst(b, N_CLASS);
            memcpy(b->nfa->st[s].cls, gi[0].seq + (size_t)depth * 32, 32);
            Frag sub = trie_build(b, gi, gcount[g], depth + 1, rdepth + 1);
            b->nfa->st[s].t1 = sub.start;
            Frag c = { s, sub.out };
            fr[g] = c;
        }
        Frag body = chain_alts(b, fr, ng);
        return (head.start < 0) ? body : frag_cat2(b, head, body);
    }
}

/* A branch is trie-eligible iff it is a left-leaning A_CAT chain (or a single
 * node) whose every leaf is A_CLASS — i.e. a fixed-length sequence of byte
 * classes. A_REP/A_ALT/A_EMPTY/A_BOL/A_EOL branches are not, and are chained
 * around the eligible runs at their original priority. Returns false and
 * leaves *out untouched when ineligible. In reverse mode the step order is
 * flipped, since rev(X.Y) = rev(Y).rev(X). */
static bool trie_key(NB *b, const Ast *a, TItem *out)
{
    int nsp = 0;
    for (const Ast *t = a; ; t = t->l) {
        nsp++;
        if (t->k != A_CAT) break;
    }
    /* nsp counts the spine head plus one per A_CAT node */
    const Ast **leaf = arena_alloc(&b->cx->arena, (size_t)nsp * sizeof(Ast *));
    int i = nsp;
    const Ast *t = a;
    while (t->k == A_CAT) { leaf[--i] = t->r; t = t->l; }
    leaf[--i] = t;
    if (i != 0) return false;   /* defensive: spine walk must be exact */

    for (int k = 0; k < nsp; k++)
        if (leaf[k]->k != A_CLASS) return false;

    uint8_t *seq = arena_alloc(&b->cx->arena, (size_t)nsp * 32);
    for (int k = 0; k < nsp; k++) {
        const uint8_t *src = leaf[b->rev ? (nsp - 1 - k) : k]->cls;
        memcpy(seq + (size_t)k * 32, src, 32);
    }
    out->seq = seq;
    out->len = nsp;
    return true;
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

        /* M2.8: factor shared prefixes. Eligible branches are grouped into
         * maximal runs of CONSECUTIVE indices; each run of 2+ becomes a trie,
         * everything else compiles as before. Contiguity is what keeps this
         * sound: "the first matching branch in index order wins" survives
         * replacing an index RANGE with a sub-alternation that itself picks
         * its first matching member. */
        TItem *keys = arena_alloc(&b->cx->arena, (size_t)nbr * sizeof(TItem));
        bool *elig = arena_alloc(&b->cx->arena, (size_t)nbr);
        for (int j = 0; j < nbr; j++)
            elig[j] = trie_key(b, br[j], &keys[j]);

        Frag *fr = arena_alloc(&b->cx->arena, (size_t)nbr * sizeof(Frag));
        int nf = 0;
        for (int j = 0; j < nbr; ) {
            if (!elig[j]) { fr[nf++] = compile_ast(b, br[j]); j++; continue; }
            int e = j;
            while (e < nbr && elig[e]) e++;
            if (e - j == 1) fr[nf++] = compile_ast(b, br[j]);
            else            fr[nf++] = trie_build(b, keys + j, e - j, 0, 0);
            j = e;
        }
        return nf == 1 ? fr[0] : chain_alts(b, fr, nf);
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
            /* X{m,n} tail is NESTED — (X(X(X)?)?)? — NOT chained optionals.
             * The two accept the same language but differ in BACKTRACK
             * PREFERENCE: with chained optionals a later copy's alternation
             * choice outranks an earlier copy's, so lazy bounded repeats pick
             * the wrong span (R2: '(?:ab|a){0,2}?b' on "abab" gave [0,2),
             * PCRE2/python give [0,4)). Built innermost-first and
             * iteratively, so depth cannot overflow the C stack. */
            Frag tail = frag_single(b, N_EPS);
            for (int i = rmin; i < rmax; i++) {
                Frag body = compile_ast(b, a->l);
                Frag cat = frag_cat2(b, body, tail);
                int s = nst(b, N_SPLIT);
                Nfa *nfa = b->nfa;
                Frag w = { s, {0} };
                if (a->greedy) {
                    nfa->st[s].t1 = cat.start;
                    patch_push(b, &w.out, s * 2 + 1);
                } else {
                    nfa->st[s].t2 = cat.start;
                    patch_push(b, &w.out, s * 2);
                }
                patch_join(b, &w.out, &cat.out);
                tail = w;
            }
            f = (f.start < 0) ? tail : frag_cat2(b, f, tail);
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

/* `^` in the REVERSE machine would need a position-dependent bot-variant
 * (checked at pp == 0), which the DFA does not build; `$` only needs the
 * eolvar the construction already computes. So ENG_UNANCH accepts EOL-only
 * patterns and `^` patterns stay on ENG_ATTEMPT (M2.7). */
bool nfa_has_bot(const Nfa *nfa)
{
    for (int i = 0; i < nfa->n; i++)
        if (nfa->st[i].k == N_BOT) return true;
    return false;
}

bool nfa_has_asserts(const Nfa *nfa)
{
    for (int i = 0; i < nfa->n; i++)
        if (nfa->st[i].k == N_BOT || nfa->st[i].k == N_EOL) return true;
    return false;
}
