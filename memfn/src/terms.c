/* SPDX-License-Identifier: 0BSD
 * Provenance: original pcrec-memory-functions text; no third-party source
 *   (memfn/PROVENANCE.md). The search below is R17-b's (lane r17b/r17b2,
 *   lane/memfn-r17 memfn/src/terms.c), ported text for text by R17-b' B1.
 *
 * memfn/src/terms.c — THE SET'S TERM COVER (R-17, R17-b; setfind.md rev 2.3
 * §3): `mf_set_terms`, the one primitive that turns a 256-bit byte set into
 * a short OR of lane-testable terms.
 *
 * R17-b' B1 (lane fdb1; r17b_prime.md rev 3 §1.3) PORTS THE SEARCH ONLY: the
 * finder table's rows R0 and R7 read a set site's cover SHAPE (its RANGE,
 * EQ and CUBE term counts), so the trace build's shadow needs the very cover
 * R17-b's form would render, and B4's mover census is predicted from it.
 * Nothing renders a cover at B1, so no byte moves. R17-b's other half (the
 * round trip `mf_cover_check`, the renderings `mf_cover_mask_w8` and
 * `mf_cover_member`, the test readers `mf_set_terms_probe`/`_text`) lands
 * with its form at B4.
 *
 * THE TERMS (§3.1): CUBE(M, V), the bytes x with (x & M) == V (EQ(b) is
 * CUBE(0xFF, b)); ARC(L, W), the modular run L, L+1, ..., L+W-1 (mod 256),
 * 1 <= W <= 128. A cover is a list of such terms whose union is the set
 * (DIRECT) or whose union is the set's complement (COMPLEMENT: the mask is
 * negated once). Every term of a cover lies inside its target (PURITY).
 *
 * THE SEARCH (§3.2-§3.3): bounded iterative deepening over the CANDIDATES of
 * each target, its prime cubes and its maximal arcs (a run longer than 128
 * gives every 128-long arc inside it); a cover of the fewest terms wins, then
 * direct before complement, then the least summed render cost (EQ 6, CUBE 7,
 * ARC 9: the operators of each term's exact SWAR spelling, counted, not
 * tuned), then the canonical key (the terms sorted by (kind, a, b), compared
 * as a sequence). The candidates are generated on the fly at each node (the
 * cubes from a containment table over all 3^8 cubes, the arcs from the
 * target's runs), so the search needs no arena. Lane r17b2 PRUNED it without
 * changing its answer (dfs carries the argument): a lower bound from members
 * no candidate holds together, a cost bound once a cover is found, and the
 * branch on the member with the fewest joint partners. Its answer equals the
 * unpruned search's, budget lifted, on every set of the population that
 * search completes on (docs/dev/lanes/r17b_report.md §6.2's resolution).
 *
 * D149: two constants decide which sets have a cover, and both are labelled
 * where they are defined (kit.h): MF_SET_K, the term limit (read from slot2,
 * MEASURED-UNOFFICIAL), and MF_SET_BUDGET, the node cap (DERIVED from the
 * measured node maximum over a stated population). Either one moving moves
 * bytes once a cover renders (B4): a pcrec abi event (§16.3).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "kit.h"

/* ---- 256-bit sets ---------------------------------------------------------- */

typedef struct { uint64_t w[4]; } bits256;

static int b_has(const bits256 *b, unsigned x) { return (b->w[x >> 6] >> (x & 63)) & 1; }
static void b_set(bits256 *b, unsigned x) { b->w[x >> 6] |= 1ull << (x & 63); }
static int b_empty(const bits256 *b) { return !(b->w[0] | b->w[1] | b->w[2] | b->w[3]); }

static void b_minus(bits256 *b, const bits256 *t)
{
    for (unsigned i = 0; i < 4; i++) b->w[i] &= ~t->w[i];
}

/* The members of term `t`. */
static bits256 term_bits(const mf_sterm *t)
{
    bits256 b = { { 0, 0, 0, 0 } };
    for (unsigned x = 0; x < 256; x++)
        if (t->kind == MF_ST_CUBE ? (x & t->a) == t->b
                                  : ((x - t->a) & 0xFFu) < (unsigned)t->b)
            b_set(&b, x);
    return b;
}

/* ---- the candidates of one target ------------------------------------------ */

/* Base-3 index of cube (M, V): per bit, 0/1 its cared value, 2 free. */
static unsigned cube_ix(unsigned m, unsigned v)
{
    unsigned ix = 0;
    for (int i = 7; i >= 0; i--)
        ix = ix * 3 + (((m >> i) & 1) ? (v >> i) & 1 : 2);
    return ix;
}

/* What the search reads about one target: its members, which cubes lie
 * inside it (`in[cube_ix]`), and its maximal runs on the byte circle. */
typedef struct {
    bits256  set;
    uint8_t  in[6561];
    unsigned nrun;
    uint8_t  run_lo[128];   /* a run's first member                      */
    uint16_t run_len[128];  /* its length (1..255: the target is not full) */
    /* What the search's pruning reads (pair_facts below): */
    bits256  joint[256];    /* member x: the members some candidate holds with x */
    unsigned nmem;
    uint8_t  by_joint[256]; /* the members, fewest joint partners first        */
} target;

/* Fills `in` by free-bit count: a cube with a free bit j lies inside the
 * target iff both its halves (bit j cared 0, cared 1) do. */
static void cubes_in(target *t)
{
    for (int f = 0; f <= 8; f++)
        for (unsigned m = 0; m < 256; m++) {
            if (8 - __builtin_popcount(m) != f) continue;
            unsigned free = ~m & 0xFFu;
            for (unsigned v = m;; v = (v - 1) & m) {      /* every V inside M */
                uint8_t c;
                if (f == 0) {
                    c = (uint8_t)b_has(&t->set, v);
                } else {
                    unsigned j = free & -free;
                    c = t->in[cube_ix(m | j, v)] && t->in[cube_ix(m | j, v | j)];
                }
                t->in[cube_ix(m, v)] = c;
                if (v == 0) break;
            }
        }
}

/* The target's maximal modular runs (the target is neither empty nor full). */
static void runs_of(target *t)
{
    unsigned z = 0;
    while (b_has(&t->set, z)) z++;              /* a non-member: runs start after one */
    t->nrun = 0;
    for (unsigned k = 1; k <= 256; k++) {
        unsigned x = (z + k) & 0xFFu;
        if (!b_has(&t->set, x)) continue;
        if (!b_has(&t->set, (x - 1) & 0xFFu)) {
            t->run_lo[t->nrun] = (uint8_t)x;
            t->run_len[t->nrun] = 0;
            t->nrun++;
        }
        t->run_len[t->nrun - 1]++;
    }
}

/* 1 iff cube (M, V) lies inside the target and no cube one free bit wider
 * does: a PRIME cube (§3.2). */
static int cube_prime(const target *t, unsigned m, unsigned v)
{
    if (!t->in[cube_ix(m, v)]) return 0;
    for (unsigned r = m; r; r &= r - 1) {
        unsigned j = r & -r;
        if (t->in[cube_ix(m & ~j, v & ~j)]) return 0;
    }
    return 1;
}

/* The candidates containing member `x`, in canonical order (cubes by M, then
 * arcs by L): written to `out`, their count returned. At most 256 cubes (one
 * per M) and 128 arcs. */
static unsigned cands_of(const target *t, unsigned x, mf_sterm *out)
{
    unsigned n = 0;
    for (unsigned m = 0; m < 256; m++)
        if (cube_prime(t, m, x & m))
            out[n++] = (mf_sterm){ MF_ST_CUBE, (uint8_t)m, (uint8_t)(x & m) };
    for (unsigned r = 0; r < t->nrun; r++) {
        unsigned lo = t->run_lo[r], len = t->run_len[r];
        unsigned off = (x - lo) & 0xFFu;
        if (off >= len) continue;
        if (len <= 128) {
            out[n++] = (mf_sterm){ MF_ST_ARC, (uint8_t)lo, (uint8_t)len };
            continue;
        }
        /* every 128-long arc of the run that holds x: offsets s in the run
           with s <= off < s + 128 and s + 128 <= len */
        unsigned s0 = off >= 127 ? off - 127 : 0, s1 = off < len - 128 ? off : len - 128;
        unsigned first = n;
        for (unsigned s = s0; s <= s1; s++)
            out[n++] = (mf_sterm){ MF_ST_ARC, (uint8_t)((lo + s) & 0xFFu), 128 };
        /* canonical order is by L as a byte value: rotate the wrapped part */
        for (unsigned i = first + 1; i < n; i++)
            for (unsigned j = i; j > first && out[j - 1].a > out[j].a; j--) {
                mf_sterm tmp = out[j - 1]; out[j - 1] = out[j]; out[j] = tmp;
            }
        break;
    }
    return n;
}

/* The pairs the pruning reads. Members x and y are JOINT iff some candidate
 * holds both, which by §3.2's dominance is iff some pure term does: the cube
 * spanned by the two (the bits where they agree, cared) lies inside the
 * target, or they sit in one run within 128 of each other (the target is not
 * full, so a run is a segment of the circle and the arc between them is the
 * only pure arc that can hold both). */
static void pair_facts(target *t)
{
    /* 16-bit tables: every value is <= 256 (the 5 KB frame this was, R-28) */
    uint16_t run_of[256], off_of[256], deg[256];
    uint8_t nib[16][16];
    for (unsigned r = 0; r < t->nrun; r++)
        for (unsigned j = 0; j < t->run_len[r]; j++) {
            run_of[(t->run_lo[r] + j) & 0xFFu] = (uint16_t)r;
            off_of[(t->run_lo[r] + j) & 0xFFu] = (uint16_t)j;
        }
    /* cube_ix of the spanned cube by nibbles: nib[diff][x] is the base-3
       value of four bits, 2 where x and y differ, x's bit where they agree */
    for (unsigned df = 0; df < 16; df++)
        for (unsigned x = 0; x < 16; x++) {
            unsigned v = 0;
            for (int i = 3; i >= 0; i--) v = v * 3 + (((df >> i) & 1) ? 2 : (x >> i) & 1);
            nib[df][x] = (uint8_t)v;
        }
    memset(t->joint, 0, sizeof t->joint);
    memset(deg, 0, sizeof deg);
    for (unsigned x = 0; x < 256; x++) {
        if (!b_has(&t->set, x)) continue;
        for (unsigned y = x; y < 256; y++) {
            if (!b_has(&t->set, y)) continue;
            unsigned df = x ^ y, d = off_of[y] > off_of[x] ? off_of[y] - off_of[x]
                                                         : off_of[x] - off_of[y];
            if (t->in[nib[df >> 4][x >> 4] * 81 + nib[df & 15][x & 15]]
                || (run_of[x] == run_of[y] && d < 128)) {
                b_set(&t->joint[x], y); b_set(&t->joint[y], x);
                deg[x]++; deg[y] += y != x;
            }
        }
    }
    uint16_t start[258] = { 0 };     /* by degree, ties in byte order */
    t->nmem = 0;
    for (unsigned x = 0; x < 256; x++)
        if (b_has(&t->set, x)) { start[deg[x] + 1]++; t->nmem++; }
    for (unsigned g = 1; g < 258; g++) start[g] += start[g - 1];
    for (unsigned x = 0; x < 256; x++)
        if (b_has(&t->set, x)) t->by_joint[start[deg[x]]++] = (uint8_t)x;
}

/* A LOWER BOUND on the terms any cover of `u` needs, counted up to `limit +
 * 1`: a greedy set of uncovered members, no two of them joint. No candidate
 * holds two of them, so each needs a term of its own. */
static unsigned lower_bound(const target *t, const bits256 *u, unsigned limit)
{
    bits256 rest = *u;
    unsigned n = 0;
    for (unsigned i = 0; i < t->nmem && n <= limit; i++) {
        unsigned x = t->by_joint[i];
        if (!b_has(&rest, x)) continue;
        n++;
        b_minus(&rest, &t->joint[x]);   /* joint[x] holds x itself */
    }
    return n;
}

/* The uncovered member with the fewest joint partners (first in `by_joint`):
 * the candidates holding it hold few other members, so its subtree tends to
 * be small. Any uncovered member is a sound branch (dfs). */
static unsigned branch_member(const target *t, const bits256 *u)
{
    for (unsigned i = 0;; i++)
        if (b_has(u, t->by_joint[i])) return t->by_joint[i];
}

/* ---- the objective and the search ------------------------------------------ */

/* The render cost of one term (§3.3 objective 3): EQ 6, CUBE 7, ARC 9. */
static unsigned term_cost(const mf_sterm *t)
{
    return t->kind == MF_ST_ARC ? 9 : t->a == 0xFF ? 6 : 7;
}

static int term_cmp(const mf_sterm *x, const mf_sterm *y)
{
    if (x->kind != y->kind) return x->kind < y->kind ? -1 : 1;
    if (x->a != y->a) return x->a < y->a ? -1 : 1;
    if (x->b != y->b) return x->b < y->b ? -1 : 1;
    return 0;
}

/* `c`'s terms sorted into canonical order (objective 4's key). */
static void cover_sort(mf_cover *c)
{
    for (unsigned i = 1; i < c->n; i++)
        for (unsigned j = i; j > 0 && term_cmp(&c->t[j - 1], &c->t[j]) > 0; j--) {
            mf_sterm tmp = c->t[j - 1]; c->t[j - 1] = c->t[j]; c->t[j] = tmp;
        }
}

/* 1 iff sorted cover `a` ranks before sorted cover `b` by objectives 2-4
 * (both have the same number of terms, objective 1). */
static int cover_better(const mf_cover *a, const mf_cover *b)
{
    if (a->complement != b->complement) return !a->complement;
    unsigned ca = 0, cb = 0;
    for (unsigned i = 0; i < a->n; i++) ca += term_cost(&a->t[i]);
    for (unsigned i = 0; i < b->n; i++) cb += term_cost(&b->t[i]);
    if (ca != cb) return ca < cb;
    for (unsigned i = 0; i < a->n; i++) {
        int c = term_cmp(&a->t[i], &b->t[i]);
        if (c) return c < 0;
    }
    return 0;
}

typedef struct {
    const target *t;
    int           complement;
    unsigned      nodes;
    int           aborted, found;
    unsigned      best_cost;
    mf_cover      cur, best;
} search;

/* The search at one depth k, exhaustive over the candidate covers of k terms
 * (§3.3), with three changes that keep its answer (the best k-term cover by
 * objectives 3-4, or none). Each rests on one fact: the depths below k have
 * no cover of this target (iterative deepening returned at the first depth
 * that had one), so every cover this search can record has EXACTLY k terms,
 * and a node `depth` terms short of k completes only with exactly `depth`
 * more.
 * - BRANCHING on the uncovered member with the fewest joint partners, not
 *   the lowest. Every cover holds that member in some term, a candidate holding
 *   it, so every k-term cover is still reached, and the best is ranked on
 *   the sorted cover, whatever the order it was reached in.
 * - THE LOWER BOUND: a node whose uncovered members need more terms than
 *   `depth` (lower_bound) has no completion, so cutting it loses no cover.
 * - THE COST BOUND: once a cover is recorded, a branch whose cost so far
 *   plus 6 (the cheapest term) per term still to choose exceeds the best
 *   cost cannot reach a cover ranked ahead of it (objective 3; equal cost is
 *   kept, objective 4 decides it), so cutting it loses no better cover. */
static void dfs(search *q, bits256 uncovered, unsigned depth, unsigned cost)
{
    if (q->aborted) return;
    if (b_empty(&uncovered)) {
        mf_cover c = q->cur;
        c.complement = q->complement;
        cover_sort(&c);
        if (!q->found || cover_better(&c, &q->best)) { q->best = c; q->best_cost = cost; }
        q->found = 1;
        return;
    }
    if (depth == 0) return;
    if (++q->nodes > MF_SET_BUDGET) { q->aborted = 1; return; }
    if (lower_bound(q->t, &uncovered, depth) > depth) return;
    mf_sterm cand[256 + 128];
    unsigned nc = cands_of(q->t, branch_member(q->t, &uncovered), cand);
    for (unsigned i = 0; i < nc && !q->aborted; i++) {
        unsigned c = cost + term_cost(&cand[i]);
        if (q->found && c + 6 * (depth - 1) > q->best_cost) continue;
        bits256 rest = uncovered, tb = term_bits(&cand[i]);
        b_minus(&rest, &tb);
        q->cur.t[q->cur.n++] = cand[i];
        dfs(q, rest, depth - 1, c);
        q->cur.n--;
    }
}

/* The two targets are ~30 KB, so they live on the heap (R-28: a stack frame
 * above 4 KB is a kit defect); a refused allocation is -1, not a decline. */
static int set_terms_in(target tg[2], const uint8_t set[32], unsigned K, mf_cover *out)
{
    unsigned members = 0;
    for (unsigned x = 0; x < 256; x++) {
        if ((set[x >> 3] >> (x & 7)) & 1) { b_set(&tg[0].set, x); members++; }
        else b_set(&tg[1].set, x);
    }
    if (members == 0 || members == 256 || K == 0 || K > MF_SET_K)
        return 0;                       /* §3.5: both edges decline */
    for (int i = 0; i < 2; i++) { cubes_in(&tg[i]); runs_of(&tg[i]); pair_facts(&tg[i]); }
    /* Per depth k, the set first: objective 2 ranks every direct cover ahead
       of every complement cover, so the complement's search at k can change
       the answer only where the set has no cover at k (result-preserving). */
    unsigned nodes = 0;
    for (unsigned k = 1; k <= K; k++) {
        for (int i = 0; i < 2; i++) {
            search q;
            memset(&q, 0, sizeof q);
            q.t = &tg[i];
            q.complement = i;
            dfs(&q, tg[i].set, k, 0);
            nodes += q.nodes;
            if (q.aborted) { out->nodes = nodes; return 0; }
            if (q.found) {
                *out = q.best;
                out->nodes = nodes;
                return 1;
            }
        }
    }
    out->nodes = nodes;
    return 0;
}

int mf_set_terms(const uint8_t set[32], unsigned K, mf_cover *out)
{
    memset(out, 0, sizeof *out);
    target *tg = calloc(2, sizeof *tg);
    if (!tg) return -1;
    int rc = set_terms_in(tg, set, K, out);
    free(tg);
    return rc;
}

