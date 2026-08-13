/* AST -> priority Thompson NFA. Split edges are ordered: t1 is the preferred
 * (higher-priority) branch, which is how greedy/lazy and alternation order
 * survive into the DFA (see docs/dev/decisions.md D3).
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
 * measured 2022 NFA visits per closure at 2000 branches (1.01*nbr), 2.27
 * billion visits total, 11 s. Factoring shared prefixes collapses the start
 * closure to the node fan-out — measured 51.7 visits per closure on the same
 * input, a 39.1x reduction.
 *
 * (An R3 critic re-instrumented both builds and found my original per-closure
 * figures — 4045 and 103.5 — were exactly 2x high, from a counter that also
 * counted -1 targets. The RATIO, and therefore every conclusion, is unchanged
 * at 39.1x either way; the constants above are the corrected ones.)
 *
 * That collapse is a property of the INPUT, not a guarantee: with no shared
 * prefix at all the root fan-out IS nbr and the split chain is exactly as long
 * as the unfactored one. Do not cite it to justify a state-count bound
 * (R3 critic correction).
 *
 * State count alone falls only ~19% (18241 -> 14824 NFA states, measured
 * end-to-end on the 2000-branch random-word case), which is why the NFA cap is
 * re-derived separately rather than being fixed by this. An independent critic
 * measurement over realistic keyword sets puts the node saving at 25-40%
 * (English word samples 28-42%, the Public Suffix List 28.8%), so no realistic
 * 3600-word list drops under the old 20000 cap by factoring alone.
 *
 * The hazard is priority: naive trie DFS order is NOT alternation index order.
 * Two independent counter-examples, both CONFIRMED against python `re` and
 * against pcrec's own flat construction:
 *
 *   abc|a|abd            on "abd" -> [0,1)   but  a(?:bc|bd)|a   -> [0,3)
 *   [ab]p|[bc]x|[ab]xy   on "bxy" -> [0,2)   but  [ab](?:p|xy)|[bc]x -> [0,3)
 *
 * The first is fixed by rule 1 (partition the branch list by index around a
 * branch that ends here), the second by rule 2's run split: branches merge
 * only on bit-IDENTICAL classes, but two distinct groups can still OVERLAP,
 * and overlapping groups are not mutually exclusive so their order cannot be
 * changed. See disjoint_run_len for why that is a run split rather than a
 * whole-node bail — the bail version was a 56x compile-time cliff. */

/* One trie-eligible branch: its class bitmaps in match order (already
 * reversed by the caller in reverse mode) plus its alternation index, which
 * exists only to keep rule 1's partitions in priority order. */
typedef struct { const uint8_t *seq; int len; } TItem;

/* Compile-time off switch for the whole factoring path, used to build a
 * REFERENCE compiler that emits the pre-M2.8 unfactored construction
 * (`gcc -DPCREC_NO_TRIE ...`). The trie is required to be output-preserving:
 * it changes the NFA, and subset construction plus minimization must erase
 * the difference, so the two builds must emit byte-identical C. That is what
 * tests/codegen/run_trie_identity.sh checks, and it is a far stronger net
 * than sampling subjects: the .rxt corpus catches a broken disjointness guard
 * with 2 cases, the diff catches it on 64 of 500 (R3.3). The "14 of 500" that
 * stood here was never measured -- it was the original critic's figure for a
 * different corpus, repeated without re-running. 21 of 200 and 64 of 500 are
 * measured; the recipes are in tests/codegen/CLAUDE.md so they can be replayed.
 *
 * Never defined in a shipped build. TRIE_ENABLED is a constant 1 there, so
 * `1 && trie_key(...)` is the original expression: verified by rebuilding and
 * comparing nfa.o's .text/.rodata/.data/.bss against the pre-R3.3 object —
 * all four byte-identical, with the disassembly differing only in the object
 * filename. (The .o as a whole is NOT byte-identical, because adding this
 * comment moved DWARF line numbers. Stating that precisely rather than
 * "the object is identical" is the R3 lesson about claims made for guards.)
 *
 * Writing the switch as `&&` rather than #ifdef'ing the functions out is what
 * keeps -Wunused-function quiet in the reference build: trie_key and
 * trie_build are still REFERENCED, just never reached. */
#ifdef PCREC_NO_TRIE
enum { TRIE_ENABLED = 0 };
#else
enum { TRIE_ENABLED = 1 };
#endif

/* Nested branch points before falling back to the unfactored construction.
 * This constant IS A STACK BUDGET and is stated as one, which is what D10
 * demanded for clo_visit and what the first version of this file failed to do
 * for itself (R3 critic finding F3).
 *
 * Measured frame for trie_build at -O2/gcc 15.2.0: 6 callee-saved pushes
 * (48 B) + `sub $0xd8` (216 B) + return address (8 B) = 272 B. 256 frames is
 * therefore ~68 KB, which fits inside a musl default 128 KB thread stack with
 * room to spare — the case that matters, since pcrec is a library and a
 * caller's thread stack is not ours to assume. 4096 would have been 1.1 MB.
 *
 * Reaching depth 256 needs 256 nested BRANCH POINTS on one root-to-leaf path;
 * unbranched runs descend iteratively and cost no stack, and duplicate
 * accepts are handled in one pass. Real keyword lists branch in the first few
 * bytes, so this is generous. Beyond it trie_flat is used: correct, merely
 * unfactored. */
enum { TRIE_MAX_RDEPTH = 256 };

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

/* Length of the longest PREFIX of `items` whose distinct class bitmaps at
 * `depth` are pairwise disjoint — i.e. the longest run that rule 2 may safely
 * group and reorder.
 *
 * Rule 2 orders groups by lowest index, which hoists every member of a group
 * to that index. That is only sound when two groups can never both match, and
 * bitmaps that OVERLAP can. The first version of this bailed the whole node to
 * `trie_flat` on any overlap, which is correct but is a CLIFF: one branch of a
 * 3600-word keyword list starting `[ab]` instead of a literal took compile
 * time from 0.80 s to 44.9 s — the entire M2.8 win lost to one character, and
 * invisible to KEYWORD-SCALE because its word list has no classes (R3 critic
 * finding). Splitting into maximal disjoint RUNS instead recovers it: the
 * offending branch becomes a run of its own and the other 3599 still factor.
 * Runs are contiguous index ranges chained in order, which is the same
 * argument that makes the eligible/ineligible run rule sound.
 *
 * O(n * 32) via a running union — group i is disjoint from all earlier groups
 * iff it is disjoint from their union. The previous O(ng^2) form additionally
 * gave up outright above 64 groups, which degenerated correct-and-disjoint
 * inputs for no reason; that cut is gone. */
static int disjoint_run_len(const TItem *items, int n, int depth)
{
    /* 257 is a HARD bound, not a heuristic: every bitmap in `known` is
     * non-empty and disjoint from all the others, and a 256-bit universe holds
     * at most 256 such sets, plus at most one empty bitmap (duplicates of
     * which are caught as duplicates). So the array can never overflow. */
    enum { MAX_GROUPS = 257 };
    uint8_t seen[32] = {0};              /* union of the distinct bitmaps */
    uint8_t known[MAX_GROUPS][32];
    int nknown = 0;

    for (int k = 0; k < n; k++) {
        const uint8_t *b = items[k].seq + (size_t)depth * 32;
        bool dup = false;
        for (int g = 0; g < nknown && !dup; g++)
            dup = memcmp(known[g], b, 32) == 0;
        if (dup) continue;               /* same group: no new overlap */
        bool clash = false;
        for (int i = 0; i < 32 && !clash; i++) clash = (seen[i] & b[i]) != 0;
        if (clash) return k;             /* run ends just before this item */
        if (nknown >= MAX_GROUPS) return k;   /* unreachable; cheap belt */
        memcpy(known[nknown++], b, 32);
        for (int i = 0; i < 32; i++) seen[i] |= b[i];
    }
    return n;
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

        /* rule 1: some branch ENDS here. Split the list by index around EVERY
         * branch that ends at this depth — segment, accept, segment, accept,
         * ... — so no ordering has to serve two different matching chains at
         * once.
         *
         * Done in one pass rather than by recursing on the tail. Recursing
         * cost one frame per accept, so `a|a|...|a` (9000 duplicate branches,
         * every one of them ending at depth 1) recursed 9000 deep and
         * SEGFAULTED at a 1 MB stack — where the pre-trie construction
         * handled the same pattern at 128 KB, because its deep recursion was
         * in tail position and gcc turned it into a jump. That was a
         * regression against this file's own R-2 hardening ("flat
         * alternations of any length cannot overflow the C stack"), found by
         * the R3 critic panel. Each segment contains NO branch ending at this
         * depth, so it goes to rule 2 and its recursion is bounded by branch
         * points, not by branch count. */
        bool has_acc = false;
        for (int k = 0; k < n; k++)
            if (items[k].len == depth) { has_acc = true; break; }
        if (has_acc) {
            /* at most one accept and one segment per item, plus a trailing
             * segment */
            Frag *parts = arena_alloc(&b->cx->arena,
                                      (size_t)(2 * n + 1) * sizeof(Frag));
            int np = 0, seg = 0;
            for (int k = 0; k < n; k++) {
                if (items[k].len != depth) continue;
                if (k > seg)
                    parts[np++] = trie_build(b, items + seg, k - seg,
                                             depth, rdepth + 1);
                parts[np++] = frag_single(b, N_EPS);
                seg = k + 1;
            }
            if (seg < n)
                parts[np++] = trie_build(b, items + seg, n - seg,
                                         depth, rdepth + 1);
            Frag body = (np == 1) ? parts[0] : chain_alts(b, parts, np);
            return (head.start < 0) ? body : frag_cat2(b, head, body);
        }

        /* Rule 2 may only reorder groups that can never both match, so before
         * grouping, cut the list into maximal runs whose distinct bitmaps are
         * pairwise disjoint. Runs are contiguous index ranges chained in
         * order, which preserves priority for the same reason the
         * eligible/ineligible run rule does. Bailing the whole node instead
         * (the first version) cost 0.80 s -> 44.9 s on a 3600-word list when a
         * single branch began `[ab]`. */
        int runlen = disjoint_run_len(items, n, depth);
        if (runlen < n) {
            Frag *runs = arena_alloc(&b->cx->arena, (size_t)n * sizeof(Frag));
            int nr = 0, off = 0;
            while (off < n) {
                int len = disjoint_run_len(items + off, n - off, depth);
                if (len <= 0) len = 1;   /* always make progress */
                runs[nr++] = trie_build(b, items + off, len, depth, rdepth + 1);
                off += len;
            }
            Frag body = (nr == 1) ? runs[0] : chain_alts(b, runs, nr);
            return (head.start < 0) ? body : frag_cat2(b, head, body);
        }

        /* rule 2: group by the class bitmap at `depth`, stable in index order
         * so groups come out ordered by their lowest index. Every group here
         * is pairwise disjoint from every other by the run cut above. */
        int *gstart = arena_alloc(&b->cx->arena, (size_t)n * sizeof(int));
        int *gcount = arena_alloc(&b->cx->arena, (size_t)n * sizeof(int));
        TItem *sorted = arena_alloc(&b->cx->arena, (size_t)n * sizeof(TItem));
        /* relies on arena_alloc zeroing (src/core/arena.c); read below
         * before any explicit write. If a "skip the memset for large
         * allocations" fast path is ever added there, this grouping
         * silently corrupts and miscompiles — R3 critic latent finding. */
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
         * sound. Note the invariant is NOT the loose "first matching branch
         * in index order wins" — D3 deliberately keeps lower-priority threads
         * alive past an accept so a later higher-priority one can override.
         * The property a run fragment must have is stronger: its DFS leaf
         * order, restricted to any set of branches that can match at one
         * start, must equal index order. Composition is sound GIVEN that, so
         * this rule is conditional on rule 2 being right, not independent of
         * it (R3 critic correction). Contiguity is safe against empty
         * branches for a structural reason: every eligible branch consumes at
         * least one byte, since all its leaves are A_CLASS. */
        TItem *keys = arena_alloc(&b->cx->arena, (size_t)nbr * sizeof(TItem));
        bool *elig = arena_alloc(&b->cx->arena, (size_t)nbr);
        for (int j = 0; j < nbr; j++)
            elig[j] = TRIE_ENABLED && trie_key(b, br[j], &keys[j]);

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
