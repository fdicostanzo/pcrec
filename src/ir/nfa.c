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
 * recursion depth is bounded by the parser's group-nesting cap.
 *
 * [DD-14 wave G] **THAT LAST CLAUSE IS NO LONGER TRUE ON ITS OWN, AND THE
 * CORRECTION IS IN PLACE RATHER THAN IN A FOOTNOTE.** `compile_ast`'s `A_CALL`
 * arm follows `Ast.u.call.body`, and **A CALL EDGE IS NOT A NESTING EDGE** —
 * the parser's group cap bounds how deeply groups nest, not how far a chain of
 * subroutine calls reaches. What bounds this descent is the LINKAGE: only a
 * `CALL_SPLICE` callee is followed, and `src/opt/callgraph.c` sets that only
 * for a target that is not in a cycle (design §6.3 condition 1), so the descent
 * is over a DAG bounded by the number of call targets. `NB.splice_depth`
 * enforces exactly that bound and fails LOUDLY, because "the eligibility rule
 * must never say otherwise" is an assumption and a stack overflow is the one
 * failure a sabotage matrix cannot tell from an infrastructure fault —
 * MEASURED: sabotage row S175 segfaulted HERE before the counter existed. */

#include <stdlib.h>
#include <string.h>

#include "core/internal.h"
/* [K50] the encoding's character-start set: the gate's class (nfa.c) and
 * the class axis's fourth value (dfa.c) both come from the backend row. */
#include "gen/enc/enc.h"

typedef struct {
    Ctx *cx; Nfa *nfa; bool rev;
    /* [DD-14 wave G] HOW MANY SPLICED CALLS DEEP THIS BUILD IS. The `A_CALL`
     * arm below follows `u.call.body`, which is the AST's one back edge, and
     * it is safe to follow ONLY because a `CALL_SPLICE` callee is not in a
     * cycle (design §6.3 condition 1) — so the descent is over a DAG bounded
     * by the number of call targets. This counter is what turns "the
     * eligibility rule must never say otherwise" from an assumption into a
     * DIAGNOSTIC.
     *
     * THE COMMENT ABOVE THIS FILE'S HEADER SAYS "remaining recursion depth is
     * bounded by the parser's group-nesting cap", and wave G is what made that
     * sentence stop being true on its own: the call edge is not a nesting
     * edge and the parser's cap does not bound it. MEASURED the hard way —
     * sabotage row S175 (the eligibility rule admits a cycle) SEGFAULTED here
     * before this counter existed, in `compile_ast`, not in the emitter, and
     * a stack overflow is the one failure a sabotage matrix cannot tell from
     * an infrastructure fault. */
    int  splice_depth;

    /* [OPT-4] BUILD THE COUNT-COLLAPSED LANGUAGE (K39; docs/design/
     * prefilter_count_independence.md §3). Set only by `compile.c`'s build
     * gate, and only when this machine's sole customer is the VM hybrid's
     * PREFILTER — never when the DFA is the engine, where the language must
     * be exact.
     *
     * It is read at exactly one place, the `A_REP` arm, which is where the
     * count enters the machine and therefore the only place it can be made to
     * stop entering. A superset is what a filter is allowed to be: see the
     * `A_ATOMIC` and `A_LOOK` arms below, which have been over-approximating
     * for the same customer since [M6.4.2] and [M6.6.2], and whose consumers'
     * obligations (rejection sound, span START a lower bound, span END NOT an
     * upper bound) this flag joins rather than restates. */
    bool collapse;
} NB;

/* [M4.5b] A_CAP IS INVISIBLE HERE, and that is load-bearing in two places at
 * once (engine_m4.md §6.1 and §5.4).
 *
 * §6.1's STRUCTURAL half is that for a capture-only pattern the capture-erased
 * DFA is not an over-approximation — it is literally the SAME machine, because
 * D31 erases the group at parse time. [M4.5b] introduces A_CAP, which would
 * break that by inspection unless the NFA builder erases it again. It does,
 * here, by dereferencing every A_CAP before looking at a node's kind. The
 * consequence is stronger than "the languages agree": the NFA built for
 * `(a|b)+c` is STATE-FOR-STATE the NFA built for `(?:a|b)+c`, so the prefilter
 * pair and every downstream DFA/minimization/emission step is bit-identical to
 * what the same pattern compiles to today. §11.3's "two lowerings from one
 * parse" mitigation, obtained without a second tree — the VM emitter is the
 * ONE consumer that reads A_CAP.
 *
 * It must therefore be applied at EVERY place this file dispatches on `->k` or
 * walks a spine: compile_ast's entry, trie_key's spine head and leaves, and
 * the A_CAT/A_ALT spine flattening (whose `->l`/`->r` children can each be an
 * A_CAP). Missing one does not miscompile — the fallback is compile_ast's own
 * entry deref — but it does perturb trie ELIGIBILITY, which would show up as a
 * §5.4 byte-identity gate failure rather than as a wrong answer. */
static const Ast *ast_bare(const Ast *a)
{
    while (a->k == A_CAP) a = a->l;
    return a;
}

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
    /* [LIM-2] N1: raise-only per-compile override (0 = the built-in
     * default), the same shape the two ART-SIZE emit-byte caps use --
     * cli/main.c's `raise_only_limits[]` is the one place a value gets in. */
    const long long max_nfa_states = b->cx->opt->max_nfa_states
                                    ? (long long)b->cx->opt->max_nfa_states
                                    : PCREC_MAX_NFA_STATES;
    if (nfa->n >= max_nfa_states)
        ctx_fail(b->cx, 0, "pattern too large (NFA exceeds %lld states; "
                 "raise with --max-nfa-states)", max_nfa_states);
    if (nfa->n == nfa->cap) {
        int ncap = nfa->cap ? nfa->cap * 2 : 64;
        /* [M4.7b/K7] realloc into a TEMPORARY, so a failure leaves the live
         * array owned by the Job for job_cleanup rather than losing it. */
        NState *nst = realloc(nfa->st, (size_t)ncap * sizeof(NState));
        if (!nst) ctx_nomem(b->cx);
        nfa->st = nst;
        nfa->cap = ncap;
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
    a = ast_bare(a);
    int nsp = 0;
    for (const Ast *t = a; ; t = ast_bare(t->l)) {
        nsp++;
        if (t->k != A_CAT) break;
    }
    /* nsp counts the spine head plus one per A_CAT node */
    const Ast **leaf = arena_alloc(&b->cx->arena, (size_t)nsp * sizeof(Ast *));
    int i = nsp;
    const Ast *t = a;
    while (t->k == A_CAT) { leaf[--i] = ast_bare(t->r); t = ast_bare(t->l); }
    leaf[--i] = t;
    if (i != 0) return false;   /* defensive: spine walk must be exact */

    for (int k = 0; k < nsp; k++)
        if (leaf[k]->k != A_CLASS) return false;

    uint8_t *seq = arena_alloc(&b->cx->arena, (size_t)nsp * 32);
    for (int k = 0; k < nsp; k++)
        /* [M5.0 stage 1] §2.5.1's AFTER row 7. This builder runs at
         * `compile.c:1018`, BELOW the encoding lowering, so every interval on
         * every leaf is byte-confined and the render is total — and if it is
         * not, `pcrec_cls_bits` says so by name rather than letting the trie
         * intern whatever the first 32 bytes of an interval list happen to
         * be. */
        pcrec_cls_bits(b->cx, leaf[b->rev ? (nsp - 1 - k) : k],
                       seq + (size_t)k * 32);
    out->seq = seq;
    out->len = nsp;
    return true;
}

static Frag compile_ast(NB *b, const Ast *a)
{
    a = ast_bare(a);   /* [M4.5b]: the group erasure, re-applied — see above */
    switch (a->k) {
    case A_CLASS: {
        Frag f = frag_single(b, N_CLASS);
        /* [M5.0 stage 1] §2.5.1's AFTER row 8, and the one place the whole
         * milestone's shape is visible in three lines: an `N_CLASS` state's
         * `cls[32]` is a BYTE set and stays one — the 256-entry class
         * machinery, the DFA's equivalence classes and `d->rep[c]` are all
         * below the lowering and none of them changes. What changed is that
         * the 32 bytes are now RENDERED from a code-point interval list
         * instead of copied from one. */
        pcrec_cls_bits(b->cx, a, b->nfa->st[f.start].cls);
        return f;
    }
    case A_EMPTY: return frag_single(b, N_EPS);
    /* [M6.2 wave C] THE MODIFIER STOPS BEING STATE HERE. The parser resolved
     * the scoped `(?m)` onto the node (D62; src/parse/parse.c), and lowering
     * consumes that field ONCE, choosing between two assertions whose truth
     * conditions are different expressions over different inputs. Downstream
     * of this line there is no multiline flag to forget to read — which is
     * the compile-time alarm D62's control 3 accepts the loss of on the AST,
     * bought back on the IR where node kinds are the vocabulary. */
    case A_BOL:   return frag_single(b, a->u.anch.multiline ? N_BOT_M : N_BOT);
    case A_EOL:   return frag_single(b, a->u.anch.multiline ? N_EOL_M : N_EOL);
    /* [M6.2 wave A] `\z`. Reversal is identity, exactly as N_BOT/N_EOL's is:
     * an assertion about an absolute subject position is the same assertion
     * whichever direction the machine walks — the reverse machine simply
     * evaluates it at the position its own walk STARTS from, which is the
     * pattern's right end. */
    case A_END:   return frag_single(b, N_END);
    /* [M6.2 wave B] `\b` / `\B`. Reversal is identity here too, but for a
     * DIFFERENT reason than N_BOT/N_EOL/N_END's, and the difference is worth
     * a sentence because it is what the whole reverse half of this wave rests
     * on. Those three are absolute-position assertions, so reversing the
     * machine cannot change what they mean. A word boundary is not absolute —
     * it is a predicate on the two bytes AROUND the position — and it
     * survives reversal because that predicate is SYMMETRIC in them: `\b` is
     * "they differ" and `\B` is "they agree", and neither says which side is
     * which. See src/ir/dfa.c's Clo comment. */
    case A_WORDB:  return frag_single(b, N_WORDB);
    case A_NWORDB: return frag_single(b, N_NWORDB);
    /* [M6.2 wave D] `\G`. Reversal is identity for N_BOT/N_EOL/N_END's
     * reason — it is an absolute-position assertion — and no reverse machine
     * is ever built for a pattern carrying it anyway: `nfa_has_bot` answers
     * true below, so src/core/compile.c routes it to ENG_ATTEMPT, which has
     * no reverse pass. That is a consequence of the routing rather than a
     * requirement of this node, and it is stated here because the reverse
     * closure has no `\G` context to seed from (§4.2's start states are a
     * FORWARD-attempt property) and would need its own answer if the routing
     * ever changed. */
    case A_GSTART: return frag_single(b, N_GSTART);
    /* [M6.2 wave E] `\K` LOWERS TO NOTHING, and that is the design rather
     * than a shortcut (assertions_design.md §6.1-§6.3).
     *
     * Every other node in this switch contributes something to the LANGUAGE.
     * `\K` contributes nothing: `a\Kb` and `ab` match exactly the same
     * strings — what differs is only which offset is REPORTED as the start,
     * and reporting is not something an NFA does. So the honest lowering is
     * an epsilon, the same fragment A_EMPTY builds.
     *
     * THE CONSEQUENCE IS LOAD-BEARING AND IS WHY THIS ARM IS NOT A CORNER
     * CASE. A `\K` pattern is VM-forced (src/opt/select_engine.c), so the
     * only DFA ever built from this node is the hybrid's PREFILTER — and
     * because this arm erases the node, that prefilter is literally the
     * machine the `\K`-free pattern builds. Its span start is therefore the
     * PRE-`\K` start, which is exactly the quantity §6.3 rule 1 says the
     * prefilter may be used for (bounding the search) and exactly the
     * quantity it must not be used for (writing `caps[0][0]`). One arm buys
     * both halves; see `<prefix>_caps_out` in src/gen/emit_vm.c for the
     * second.
     *
     * Reversal is identity for the most trivial reason in the file: there is
     * nothing to reverse. */
    case A_KRESET: return frag_single(b, N_EPS);
    /* [M6.6.2] A LOOKAROUND LOWERS TO AN EPSILON, BODY AND ALL, and that is
     * the design (lookaround_design.md §5.2/§5.3) rather than a shortcut.
     *
     * It is a DIFFERENT claim from `\K`'s epsilon one arm up. `\K` contributes
     * nothing to the LANGUAGE, so erasing it is exact. Erasing a lookaround is
     * NOT exact — it throws away a filter — and the machine built from this
     * arm therefore recognises a strict SUPERSET. That is the whole point and
     * it is a one-line proof: a lookaround consumes nothing, so every string P
     * matches at a position, erase(P) also matches at that position, i.e.
     * L(P) is a subset of L(erase(P)) EVERYWHERE. Design §5.3.
     *
     * THE BODY IS NOT COMPILED, which is what makes the superset a superset
     * rather than a wrong machine. Splicing the body in as if it were
     * consuming text would demand bytes the outer match never consumes.
     *
     * THE CONSEQUENCE IS LOAD-BEARING, and it is `\K`'s consequence with one
     * clause deleted. A lookaround pattern is VM-forced
     * (src/opt/select_engine.c reads the six VM_ONLY rows' stamps), so the
     * only DFA ever built from this node is the hybrid's PREFILTER — literally
     * the machine the lookaround-free pattern builds. Its REJECTION is sound
     * (a position the superset rejects, the real pattern rejects too) and its
     * span START is sound (a lower bound), so the prefilter SHIPS. Its span
     * END is NOT an upper bound, which is why `Vm.mrl_win` must exclude a
     * lookaround-bearing artifact — the identical hazard an atomic group has,
     * measured for that construct at 114 cells of silent match loss. See
     * `pcrec_has_lookaround` (src/opt/atomic.c) and design §5.6.
     *
     * The general DFA construction — product construction with each body's
     * recognizer — is chartered as `[ENG-LOOK]` and is not this arm.
     * Reversal is identity for the same trivial reason `\K`'s is: an epsilon
     * has nothing to reverse. */
    case A_LOOK:   return frag_single(b, N_EPS);
    case A_CAT: {
        /* flatten the left-leaning spine iteratively (R-2); in reverse mode
         * the sequence order flips: rev(X·Y) = rev(Y)·rev(X) */
        int nsp = 0;
        const Ast *t = a;
        while (t->k == A_CAT) { nsp++; t = ast_bare(t->l); }
        const Ast **rs = arena_alloc(&b->cx->arena, (size_t)nsp * sizeof(Ast *));
        int i = nsp;
        t = a;
        while (t->k == A_CAT) { rs[--i] = t->r; t = ast_bare(t->l); }
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
        for (const Ast *t2 = a; t2->k == A_ALT; t2 = ast_bare(t2->l)) nbr++;
        const Ast **br = arena_alloc(&b->cx->arena, (size_t)nbr * sizeof(Ast *));
        int i = nbr;
        const Ast *t2 = a;
        while (t2->k == A_ALT) { br[--i] = t2->r; t2 = ast_bare(t2->l); }
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
        int rmin = a->u.rep.rmin, rmax = a->u.rep.rmax;
        /* [OPT-4] THE COUNT-COLLAPSE, and it is three lines because the whole
         * mechanism is a change of BOUNDS — the construction below is
         * untouched and every downstream stage sees an ordinary `A_REP`.
         *
         * `X{m,n}` becomes `X{min(m,1),}`. SOUND as a superset: every word of
         * `X{m,n}` is k copies of X with m <= k <= n; k >= 0 = min(0,1) when
         * m is 0 and k >= m >= 1 = min(m,1) otherwise, and k <= infinity
         * always. The proof never mentions n, which is exactly why the
         * resulting machine does not scale with the count.
         *
         * The guard is `rmin > 1 || rmax > 1`, not `n > 1`, so it covers the
         * whole family in one arm — `{m,n}`, `{n}`, `{m,}` with m >= 2, and
         * the lazy and nested spellings of all of them, since laziness is a
         * preference the DFA does not have and nesting is this same recursion.
         * A possessive bound needs nothing here: it parses to
         * `A_ATOMIC(A_REP(X))` and the `A_ATOMIC` arm below already erases the
         * wrapper before this arm sees the repeat. A repeat already satisfying
         * the guard's negation replicates nothing, so collapsing it would buy
         * no bytes and cost the filter its sharpness for free. */
        if (b->collapse && (rmin > 1 || rmax > 1)) {
            rmin = rmin ? 1 : 0;
            rmax = -1;
        }
        if (rmin == 0 && rmax == 0) return frag_single(b, N_EPS);

        Frag f = { -1, {0} };
        for (int i = 0; i < rmin; i++) {
            Frag c = compile_ast(b, a->l);
            f = (f.start < 0) ? c : frag_cat2(b, f, c);
        }
        if (rmax < 0) {
            Frag s = frag_star(b, a->l, a->u.rep.greedy);
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
                /* [M4.7b/K7] INHERIT `cat.out`'s array rather than copying into
                 * a fresh one. This loop runs n-m times and every iteration's
                 * out-set is the previous one PLUS this split's own exit, so
                 * copying it made NFA construction Theta((n-m)^2) in arena
                 * traffic while the state count — the only thing
                 * PCREC_MAX_NFA_STATES watches — stayed linear. That gap IS
                 * K7: `a{0,8000}` spent 332 MB per machine (664 MB for the
                 * forward/reverse pair) building 16,002 states worth 768 KB,
                 * and `a{0,65535}` needed ~34 GB it was SIGKILLed for, all
                 * without the cap ever having anything to object to. Growing
                 * one array geometrically instead makes the whole loop
                 * amortized O(1) per copy; measured below in this lane at
                 * 664 MB -> 5 MB for `a{0,8000}`.
                 *
                 * IT CANNOT CHANGE THE MACHINE, which is what makes this a
                 * fix and not a redesign. A Patch is an unordered SET of
                 * dangling edges — `patch_to` writes the same target into
                 * every entry and reads nothing about their order — and this
                 * rewrite calls `nst` exactly where the old one did, so state
                 * numbering is untouched. Only the order of entries within the
                 * patch array differs, and nothing observes that.
                 * `frag_cat2` above already inherits its right operand's array
                 * for the same reason; this is that idiom applied to the one
                 * site that had not adopted it. */
                Frag w = { s, cat.out };
                cat.out = (Patch){0};
                if (a->u.rep.greedy) {
                    nfa->st[s].t1 = cat.start;
                    patch_push(b, &w.out, s * 2 + 1);
                } else {
                    nfa->st[s].t2 = cat.start;
                    patch_push(b, &w.out, s * 2);
                }
                tail = w;
            }
            f = (f.start < 0) ? tail : frag_cat2(b, f, tail);
        }
        return f;
    }
    case A_CAP:
        break;   /* unreachable: ast_bare() above strips every A_CAP. Listed
                  * so -Wswitch keeps this exhaustive, and falling into the
                  * internal-error below rather than silently recursing means
                  * a future path that reaches here says so loudly. */
    /* [M6.4.2] TRANSPARENT — the body's machine, with the atomicity ERASED,
     * and it is the only sound choice this construction has.
     *
     * A DFA never backtracks in the first place: subset construction keeps
     * every alternative alive, which is exactly the NON-atomic semantics. So
     * there is no machine here that implements the cut, and the two available
     * answers are "refuse to build one" or "build the machine for the UNCUT
     * language and be honest about what it answers for". This arm takes the
     * second, and every consumer of the result has to know it:
     *
     *   - As the PREFILTER under a VM artifact, this machine answers for a
     *     strict SUPERSET of the pattern. Its REJECTION is still sound (no
     *     uncut match means no atomic match) and its span START is still a
     *     lower bound, so both keep working. Its span END is NOT an upper
     *     bound on the cut match's end — MEASURED at 122 refuting cells, and
     *     114 cells of live silent match loss on the emitted prefilter — which
     *     is why src/gen/emit_vm.c switches its MRL ceiling off whenever
     *     `pcrec_has_atomic` holds. atomic_groups_design.md §4.
     *   - As the ARTIFACT's own machine it is never used: an A_ATOMIC that
     *     survived the free discharge stamps VM_ONLY through `Ast.reg`, so
     *     src/opt/select_engine.c has already chosen the VM (or refused
     *     `--engine=dfa` by name) before this machine is built.
     *
     * The REJECTION-soundness half holds only in a POSITIVE context, and every
     * pattern module `atomic-groups` can compile is one: under negation a
     * smaller inner language is a LARGER outer one, and `(?!(?>a|ab)c)abc` is
     * the witness — but negative lookaround is module `lookaround` ([M6.6])
     * and refuses today. [M6.6] REOPENS that question; it is written here so
     * the lookaround lowering inherits it rather than rediscovering it.
     *
     * `[ENG-CUT]` is the chartered follow-on that would build a real cut
     * construction (cuts preserve regularity — Berglund et al.); until it
     * exists, a DFA lowering that simply ignored the atomicity would be a
     * MISCOMPILE, which is what registry.c's own row comment has warned about
     * since before there was a producer, and what sabotage row S91 injects. */
    case A_ATOMIC:
        return compile_ast(b, a->l);
    /* [M6.5.2] NO MACHINE, AND THE ANSWER IS TO FALL INTO THE ERROR BELOW —
     * deliberately, not for want of an idea.
     *
     * A backreference is not regular, so there is no NFA for it. Two
     * approximations exist and BOTH are refused here rather than in a comment:
     * erasing it to epsilon is a SUBSET (it deletes real matches, the one
     * failure class D26 refuses outright), and replacing it with a copy of the
     * referenced group's machine is the APPROACH §2 erasure, which is not even
     * a superset once that group's transitive closure holds an assertion or an
     * atomic/possessive operator — MEASURED at 12 of 18 positive-control cells
     * across the two reasons, plus 3 of 5 for the transitive one
     * (backrefs_design.md §7.2). Even where it IS a superset its leftmost SPAN
     * differs from the true one on a large fraction of subjects, so it cannot
     * serve as `engine_m4.md` §6.1's exact anchored window either.
     *
     * SO NOTHING BUILDS THIS MACHINE, and that is enforced upstream rather
     * than assumed: `src/opt/select_engine.c` forces `EngineFit.prefilter`
     * OFF for a backref-bearing pattern and refuses `-fprefilter` on one by
     * name, and the pattern is VM-forced by its rows' stamps, so
     * `src/core/compile.c`'s build condition (`chosen == ENGM_DFA ||
     * fit.prefilter`) is false. Reaching this line means one of those two
     * facts stopped being true, which is exactly when a loud internal error
     * is worth more than a machine that answers for a different language. */
    case A_BREF:
    /* [DD-14] NO MACHINE, AND IT FALLS INTO THE ERROR BELOW WITH `A_BREF` —
     * deliberately, and NOT because a call is as hopeless as a backreference.
     *
     * A call to a NON-RECURSIVE callee has an exact finite lowering: splice
     * the callee's machine in. A call in a CYCLE does not — that is a
     * context-free language and this is a finite automaton — and design §8.2
     * measured that the two available approximations are the same two
     * `A_BREF`'s arm refuses: erasing the call to epsilon is a SUBSET (it
     * deletes real matches, the failure class D26 refuses outright), and
     * bounding the recursion at a fixed depth is neither a subset nor a
     * superset of the true language.
     *
     * SO NOTHING BUILDS THIS MACHINE, enforced upstream exactly as it is for
     * a backreference: every `recursion` row is VM_ONLY so the pattern is
     * VM-forced by its stamps, and wave E forces `EngineFit.prefilter` OFF
     * for a call-bearing pattern, which makes `src/core/compile.c`'s build
     * condition (`chosen == ENGM_DFA || fit.prefilter`) false. Reaching this
     * line means one of those two facts stopped being true.
     *
     * WAVE G IS WHERE THIS ARM CHANGED, and it is the ONE site in the whole
     * module where following the call graph is the POINT rather than a hang.
     *
     * A SPLICED CALL INLINES THE CALLEE'S MACHINE, AND IT IS EXACT. Design
     * §8.3 calls this "the sound approximation" and only the second half of
     * that phrase is right: for an ACYCLIC callee the inlined fragment IS the
     * callee's language, with no over-approximation step at all. The only
     * thing erased is the CAPTURE, and `ast_bare` at the top of this function
     * erases those from every `A_CAP` in the tree already — which is why
     * `(?&atom)` and the hand-written body it names build the IDENTICAL
     * machine, and why §8.3 measured 8 of its 15 inlined equivalents compiling
     * to pcrec's pure DFA. THE BACK EDGE IS SAFE HERE ONLY BECAUSE OF THE
     * LINKAGE: `CALL_SPLICE` means `!reaches(i, i)` (design §6.3 condition 1),
     * so this descent is over a DAG and terminates, bounded a second time by
     * PCREC_MAX_SPLICE_NODES.
     *
     * §8.3's SECOND ARM — `Sigma*` for a callee in a cycle — IS DELIBERATELY
     * NOT BUILT, and the reason is that wave G made it unreachable rather than
     * unnecessary. `src/opt/select_engine.c` narrows both consumers to
     * `pcrec_has_linked_call`: a pattern with a LINKED call is VM-only AND
     * gets no prefilter, so neither the DFA engine's machine nor the hybrid's
     * is ever built for one and nothing would consume the superset. Building
     * it anyway would buy a prefilter for recursive patterns at the cost of
     * the loosest superset in the compiler, on the window-END exposure
     * `lookaround_design.md` §5.4 measured (8 violations of 45) and
     * `backrefs_design.md` §11.2 found again — an exposure this arm, being
     * exact, does not have at all. That is a real option and it is left OPEN
     * rather than refused; what is refused is shipping it without the
     * population §8.4 measured empty. Reaching the `ctx_fail` below with an
     * `A_CALL` means the narrowing stopped being true, which is exactly what
     * S-SR17's twin sabotages. */
    case A_CALL:
        if (a->u.call.link == CALL_SPLICE && a->u.call.body) {
            const int nt = pcrec_callgraph_ntargets(b->cx->callgraph);
            if (++b->splice_depth > nt)
                ctx_fail(b->cx, 0,
                         "internal error: a spliced subroutine call nested "
                         "more than %d deep while building the machine, so "
                         "the splice eligibility rule admitted a cycle", nt);
            Frag f = compile_ast(b, a->u.call.body);
            b->splice_depth--;
            return f;
        }
        ctx_fail(b->cx, 0,
                 "internal error: a LINKED subroutine call reached the machine "
                 "builder; a linked call is VM-only and carries no prefilter");
        break;
    }
    ctx_fail(b->cx, 0, "internal error: bad AST node");
}

void pcrec_build_nfa(Ctx *cx, Ast *root, Nfa *nfa, bool reverse, bool collapse)
{
    /* [OPT-4] REBUILDABLE IN PLACE. `compile.c`'s build gate measures the
     * exact machine and then, above the knee, rebuilds it collapsed into the
     * SAME `Nfa` — so this resets the state count rather than assuming a
     * fresh one. `st`/`cap` are deliberately kept: the array is Job-owned and
     * `nst` reuses it, so the second build costs no allocation. */
    nfa->n = 0;
    NB b = { cx, nfa, reverse, 0, collapse };
    Frag f = compile_ast(&b, root);
    int acc = nst(&b, N_ACCEPT);
    patch_to(&b, &f.out, acc);
    nfa->start = f.start;
    /* [OPT-K] The anchored start IS the start until a wrap moves the latter. */
    nfa->anch_start = f.start;
}

/* Lowest-priority start self-loop: new_start = SPLIT(pattern [preferred],
 * any-byte -> new_start). Threads from earlier subject positions always
 * outrank later ones, so D3's accept-pruning yields the leftmost-first
 * match end in one pass (D7).
 *
 * ===================================================================
 * [K50] THE POSITIONS THIS LOOP GENERATES ARE THE ENCODING'S CHARACTER
 * BOUNDARIES, and the caller's own position is NOT one of them.
 *
 * THE DEFECT. The self-loop consumes ONE BYTE, so the split above offered the
 * pattern at every byte offset. Under a multi-byte encoding that includes
 * offsets INSIDE a character, and utf8_design.md §5.5 asserted such offsets
 * were harmless because they "have no path". §2.6.1 of the same document had
 * already written down the refutation one section earlier: "no path" INVERTS
 * for a negative assertion, which succeeds exactly where its body has none.
 * So a mid-character offset does not waste an attempt, it ANSWERS — K50's
 * witness is `\B` over `61 CE B1` reporting `(2,2)` from an ordinary
 * `startpos = 0`, where libpcre2 10.46 under `PCRE2_UTF` answers `(3,3)` and
 * `(2,2)` is precisely its `options=0` BYTE answer.
 *
 * THE GATE IS ON THE SPLIT INTO THE PATTERN, NOT ON THE LOOP'S STEP. The loop
 * must still TRAVERSE ill-formed bytes: §2.6(c)'s ruled semantics require a
 * search to find matches AFTER one (`a` on `FF 63` gives `(1,2)`), so the
 * self-loop's class stays every byte and only the entry into the pattern is
 * conditioned. Two placements that look plausible and are not, recorded so
 * they are refuted once rather than re-derived:
 *
 *   - gating the loop's RE-ENTRY (`any -> gate -> sp`) kills the scan: the
 *     self-loop is the only forward advance, so a thread blocked at a
 *     continuation byte dies and `a` on `CE B1 61` is never found at all;
 *   - making the loop consume whole CHARACTERS needs a greedy, deterministic
 *     continuation skip, and a priority split cannot force one — the
 *     nondeterministic spelling still reaches every byte offset.
 *
 * WHY THERE ARE TWO SPLIT STATES. `sp0` is `nfa->start` and is UNGATED; the
 * self-loop returns to `sp1`, which is gated. So the position the CALLER
 * supplied enters the pattern whatever it is, and every position this loop
 * GENERATES is a boundary — which is exactly the rule Frank ruled (the engine
 * owns the positions it invents; the caller's own position is the caller's).
 *
 * That split of responsibility is what lets ONE machine serve both arms of
 * the `-fno-startpos-guard` axis: the deny arm keeps §2.6.1.1's permissive
 * mid-character answers VERBATIM because the automaton never had an opinion
 * about the caller's position, and the default arm refuses such a position at
 * the emitted ENTRY instead. A gate on `sp0` too would have made the deny arm
 * answer no-match where §2.6.1.1 rules `(1,1)`, and the axis would have been
 * a second automaton rather than a guard.
 *
 * UNDER AN ENCODING THAT RESTRICTS NOTHING there is no gate node and no
 * second split: `start_cls` is NULL, the construction below is the pre-K50
 * one state for state, and every `byte` artifact is unmoved. A tautological
 * gate is not emitted.
 *
 * [K50-NULLGATE] AND NEITHER IS A REDUNDANT ONE. `pcrec_startgate_needed`
 * (internal.h, which carries the proof) is the second conjunct: a match that
 * CONSUMES a byte already begins on a byte the backend's `start_cls` admits,
 * so only a NULLABLE pattern can ever answer at a position this loop would
 * otherwise have to gate. A non-nullable pattern's artifact is therefore the
 * pre-K50 one under every encoding, not just under `byte`. */
/* [K50-NULLGATE] THE OMISSION'S OWN SOUNDNESS ARGUMENT, CHECKED RATHER THAN
 * ASSERTED IN PROSE, at the exact site that would commit the miscompile.
 *
 * `pcrec_startgate_needed` says the gate is unnecessary because a match that
 * CONSUMES a byte begins on a byte `start_cls` admits — so every class the
 * pattern can reach WITHOUT consuming must be a subset of `start_cls`, and no
 * accept may be reachable without consuming at all. Both are properties of the
 * MACHINE; the predicate is a property of the AST. Checking one against the
 * other here is two independent derivations meeting, not a restatement:
 * `pcrec_minw` walks `Ast` nodes and this walks `NState`s.
 *
 * `ctx_fail` and not `assert`: K7's rule that a library must not kill its
 * caller, and the same choice `pcrec_cls_bits` makes for the same reason — a
 * lowering that did not run is a diagnosed internal error at the site that
 * would have committed the miscompile, never a wrong answer in the field.
 *
 * The walk is the epsilon+assertion closure of the pattern's own start, which
 * is bounded by the state count and visits each state once. */
static void cstart_check_omission(Ctx *cx, Nfa *nfa, const unsigned char *scls)
{
    unsigned char *seen = arena_alloc(&cx->arena, (size_t)nfa->n);
    int *stack = arena_alloc(&cx->arena, (size_t)nfa->n * sizeof(int));
    int top = 0, c;

    memset(seen, 0, (size_t)nfa->n);
    stack[top++] = nfa->start;
    seen[nfa->start] = 1;

    while (top > 0) {
        int s = stack[--top];
        const NState *st = &nfa->st[s];

        if (st->k == N_CLASS) {
            /* Reached WITHOUT consuming, so this is a first byte of some
             * match. Every byte it admits must be one a character may start
             * at, or a match could begin mid-character and the gate we just
             * declined to build was load-bearing. */
            for (c = 0; c < 256; c++)
                if (cls_has(st->cls, (unsigned)c) && !cls_has(scls, (unsigned)c))
                    ctx_fail(cx, 0,
                             "internal error: [K50-NULLGATE] omitted the "
                             "character-boundary gate on a pattern whose first "
                             "byte may be 0x%02x, which this encoding does not "
                             "admit as a character start", (unsigned)c);
            continue;   /* consuming state: its successors are not first bytes */
        }
        if (st->k == N_ACCEPT)
            ctx_fail(cx, 0,
                     "internal error: [K50-NULLGATE] omitted the "
                     "character-boundary gate on a pattern that can ACCEPT "
                     "without consuming — the nullability predicate and the "
                     "machine disagree");

        /* Every other kind is an epsilon or an assertion: it advances the
         * walk without consuming a byte. Assertions are passed AS THOUGH THEY
         * HELD, which is the sound direction here — it can only widen the set
         * of classes the check inspects. */
        if (st->t1 >= 0 && !seen[st->t1]) { seen[st->t1] = 1; stack[top++] = st->t1; }
        if (st->k == N_SPLIT && st->t2 >= 0 && !seen[st->t2]) {
            seen[st->t2] = 1; stack[top++] = st->t2;
        }
    }
}

void nfa_wrap_unanchored(Ctx *cx, Nfa *nfa)
{
    const PcrecEnc *e = pcrec_enc_by_id(cx->opt->encoding);
    NB b = { cx, nfa, false, 0, false };
    int sp = nst(&b, N_SPLIT);
    int any = nst(&b, N_CLASS);
    memset(nfa->st[any].cls, 0xff, 32);   /* every byte, including \n */
    nfa->st[sp].t1 = nfa->start;
    nfa->st[sp].t2 = any;
    nfa->st[any].t1 = sp;

    if (e && e->start_cls && !pcrec_startgate_needed(cx))
        cstart_check_omission(cx, nfa, e->start_cls);

    if (e && e->start_cls && pcrec_startgate_needed(cx)) {
        /* The loop's own split, and the gate in front of its pattern branch.
         * `sp` above keeps naming the caller's ungated entry and stays
         * `nfa->start`; the self-loop is re-pointed at `sp1`. */
        int gate = nst(&b, N_CSTART);
        int sp1  = nst(&b, N_SPLIT);
        memcpy(nfa->st[gate].cls, e->start_cls, 32);
        nfa->st[gate].t1 = nfa->start;   /* still the pattern's own start */
        nfa->st[sp1].t1  = gate;
        nfa->st[sp1].t2  = any;
        nfa->st[any].t1  = sp1;
    }

    nfa->start = sp;
    /* [OPT-K] `anch_start` deliberately does NOT move: it keeps naming the
     * pattern's own first state, which is what the offset-k prefix walk
     * (src/opt/prefix_k.c) needs and what `start` stops being here. */
}

/* `^` in the REVERSE machine would need a position-dependent bot-variant
 * (checked at pp == 0), which the DFA does not build; `$` only needs the
 * eolvar the construction already computes. So ENG_UNANCH accepts EOL-only
 * patterns and `^` patterns stay on ENG_ATTEMPT (M2.7).
 *
 * [M6.2 wave C] `(?m)^` JOINS THE BOT FAMILY, and it needs the same routing
 * for MORE reason, not less (assertions_design.md §3.7): plain `^`'s reverse
 * problem is the missing position-dependent variant, and `(?m)^` needs that
 * variant AND a byte-selected view on top of it. So this predicate becomes
 * "contains any BOT-family node" — the extension §3.7 asks for, and the
 * reason the reverse machine never has to evaluate N_BOT_M.
 *
 * `(?m)$` does NOT join: its truth at `pp` is a fact about `s[pp]`, the byte
 * the reverse walk has already consumed, which the state identity carries
 * (§3.5's mechanism mirrored). It stays on ENG_UNANCH.
 *
 * [M6.2 wave D] `\G` JOINS TOO, and the argument is `^`'s word for word with
 * `startpos` in place of 0 (assertions_design.md §4.2): `\G` is a START-STATE
 * property — true only at the first position of the one attempt whose
 * `start == startpos` — and ENG_ATTEMPT is the engine that HAS attempts. On
 * ENG_UNANCH there is a single wrapped scan with a self-loop and no notion of
 * where an individual candidate match began, so there is nothing for the bit
 * to be a property OF. That the reverse machine then never evaluates N_GSTART
 * is the same free consequence `(?m)^` gets here.
 *
 * This is NOT a `^` alias and the routing is the only thing they share:
 * `\Gfoo` at `startpos == 3` matches at 3 where `^foo` cannot, which is why
 * §4.1's `start_max` is a THIRD value rather than the existing `0`. */
bool nfa_has_bot(const Nfa *nfa)
{
    for (int i = 0; i < nfa->n; i++)
        if (nfa->st[i].k == N_BOT || nfa->st[i].k == N_BOT_M ||
            nfa->st[i].k == N_GSTART) return true;
    return false;
}

bool nfa_has_asserts(const Nfa *nfa)
{
    for (int i = 0; i < nfa->n; i++)
        if (nfa->st[i].k == N_BOT || nfa->st[i].k == N_EOL ||
            nfa->st[i].k == N_BOT_M || nfa->st[i].k == N_EOL_M) return true;
    return false;
}
