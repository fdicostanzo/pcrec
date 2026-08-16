#include <immintrin.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* ---------------------------------------------------------------------------
 * Find-all candidates (findall.h contract).
 *
 * Every function here reports EVERY occurrence start, ascending, overlapping
 * matches included, and returns the TOTAL count — which may exceed cap. There
 * is no early exit anywhere: a find-all scan always walks the whole haystack,
 * so the "did the filter reject this block" question that dominates find-first
 * is replaced by "what does it cost to turn a block mask into offsets".
 *
 * That is the axis these candidates measure:
 *
 *   - fused vs two-pass emission (chain_ctz vs chain_mask2p): bit-expanding
 *     each block's mask inline, versus storing a stream of masks in pass 1 and
 *     expanding it in pass 2.
 *   - exact-by-construction masks (the AND-chains) vs filter masks that must be
 *     rebuilt into exact ones (rare2): under find-all, EVERY candidate bit pays
 *     a verify, whereas find-first paid for at most one.
 *   - fused vs materialized factor pairing (pair_fused vs pair_merge).
 *
 * Memory contract, enforced by guard pages in the harness: never read at or
 * past hay+n, never before hay. n shorter than the minimum match returns 0
 * without touching memory. Every vector loop is bounded by
 * `i + 32 + (k-1) <= n`, so the highest byte a block touches, i+(k-1)+31, stays
 * inside [hay, hay+n); the scalar tail picks up the remainder.
 * ------------------------------------------------------------------------- */

/* The one emission point. Counting past cap is part of the contract: callers
 * size cap from a density estimate and detect truncation via count > cap. */
static inline void fa_emit(uint32_t *out, size_t cap, size_t *cnt, size_t off)
{
    if (*cnt < cap) {
        out[*cnt] = (uint32_t)off;
    }
    (*cnt)++;
}

/* ---------------------------------------------------------------------------
 * 1. "enzyme" (k=6), full AND-chain, fused bit-walk emission.
 * ------------------------------------------------------------------------- */

/* Six loads, six broadcast compares, five ANDs per block. The surviving mask is
 * exact by construction — a set bit IS a match, not a candidate — so there is no
 * verify step and the mask can be bit-walked straight into the output.
 *
 * The `while (mask)` needs no `if (mask)` guard in front of it: an empty mask
 * falls through on the first test, which is the same branch the `if` would have
 * executed. Adding the guard would only duplicate it. */
size_t fa_enzyme_chain_ctz(const char *hay, size_t n, uint32_t *out, size_t cap)
{
    size_t cnt = 0;

    if (n < 6) {
        return 0;
    }

    const __m256i be = _mm256_set1_epi8('e');
    const __m256i bn = _mm256_set1_epi8('n');
    const __m256i bz = _mm256_set1_epi8('z');
    const __m256i by = _mm256_set1_epi8('y');
    const __m256i bm = _mm256_set1_epi8('m');

    size_t i = 0;
    /* Highest byte touched this iteration is i+5+31; i+32+5<=n keeps every
     * load inside [hay, hay+n). */
    for (; i + 32 + 5 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));
        __m256i v4 = _mm256_loadu_si256((const __m256i *)(hay + i + 4));
        __m256i v5 = _mm256_loadu_si256((const __m256i *)(hay + i + 5));

        __m256i m = _mm256_cmpeq_epi8(v0, be);
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v1, bn));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v2, bz));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v3, by));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v4, bm));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v5, be));

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);

        while (mask) {
            fa_emit(out, cap, &cnt, i + (size_t)__builtin_ctz(mask));
            mask &= mask - 1;
        }
    }

    for (; i + 6 <= n; i++) {
        if (hay[i] == 'e' && memcmp(hay + i, "enzyme", 6) == 0) {
            fa_emit(out, cap, &cnt, i);
        }
    }
    return cnt;
}

/* ---------------------------------------------------------------------------
 * 2. "enzyme" (k=6), same AND-chain, TWO-PASS (mask-stream) emission.
 * ------------------------------------------------------------------------- */

/* Same vector work as fa_enzyme_chain_ctz, but the emission is split in two so
 * the two halves can be costed separately.
 *
 * Pass 1 is fully branchless in the block body: compute the mask, store it,
 * advance. No data-dependent branch, so the scan runs at a fixed rate whatever
 * the match density is. Pass 2 walks the stored mask stream and bit-expands the
 * nonzero entries into offsets, which is where all the unpredictable branching
 * now lives.
 *
 * The intent is to separate the two costs that the fused version welds
 * together: streaming the haystack through the compare chain, and turning set
 * bits into output. The price of the split is a mask array — one uint32_t per
 * 32 bytes of haystack, i.e. 1/8 of a bit per input byte of extra traffic — and
 * a second walk over it, so the comparison against the fused version is a real
 * question, not a foregone one.
 *
 * Block b covers haystack positions [32*b, 32*b+31], so pass 2 recovers each
 * block's base as 32*b with no need to store it. Only the scalar tail has a base
 * that is not a multiple of 32, so it gets a single extra mask entry and an
 * explicitly remembered base. */
size_t fa_enzyme_chain_mask2p(const char *hay, size_t n, uint32_t *out, size_t cap)
{
    size_t cnt = 0;

    if (n < 6) {
        return 0;
    }

    /* nb blocks plus one tail entry; nb <= n/32, so n/32+2 always suffices. */
    uint32_t *masks = (uint32_t *)malloc(((n / 32) + 2) * sizeof(uint32_t));
    if (!masks) {
        /* Same answer, fused emission. Allocation failure is not expected in
         * the harness; this only keeps the function total. */
        return fa_enzyme_chain_ctz(hay, n, out, cap);
    }

    const __m256i be = _mm256_set1_epi8('e');
    const __m256i bn = _mm256_set1_epi8('n');
    const __m256i bz = _mm256_set1_epi8('z');
    const __m256i by = _mm256_set1_epi8('y');
    const __m256i bm = _mm256_set1_epi8('m');

    size_t nb = 0;
    size_t i = 0;

    /* Pass 1: branchless mask capture. */
    for (; i + 32 + 5 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));
        __m256i v4 = _mm256_loadu_si256((const __m256i *)(hay + i + 4));
        __m256i v5 = _mm256_loadu_si256((const __m256i *)(hay + i + 5));

        __m256i m = _mm256_cmpeq_epi8(v0, be);
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v1, bn));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v2, bz));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v3, by));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v4, bm));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v5, be));

        masks[nb++] = (uint32_t)_mm256_movemask_epi8(m);
    }

    /* Scalar tail, collected as one more partial mask so pass 2 has a single
     * shape to walk.
     *
     * The tail always fits in 32 bits. If the vector loop ran it exited with
     * i+37 > n, so i >= n-36 and the tail covers positions i..n-6, that is
     * n-5-i <= 31 of them. If it never ran then i = 0 and n <= 36 (and n >= 6),
     * so the count is n-5 <= 31 as well. Either way the shift below stays
     * under 32. */
    const size_t tail_base = i;
    uint32_t tail_mask = 0;
    for (; i + 6 <= n; i++) {
        uint32_t hit = (hay[i] == 'e' && memcmp(hay + i, "enzyme", 6) == 0) ? 1u : 0u;
        tail_mask |= hit << (i - tail_base);
    }
    masks[nb] = tail_mask;

    /* Pass 2: bit-expand the mask stream into ascending offsets. */
    for (size_t b = 0; b < nb; b++) {
        uint32_t mask = masks[b];
        const size_t base = b * 32;
        while (mask) {
            fa_emit(out, cap, &cnt, base + (size_t)__builtin_ctz(mask));
            mask &= mask - 1;
        }
    }
    {
        uint32_t mask = masks[nb];
        while (mask) {
            fa_emit(out, cap, &cnt, tail_base + (size_t)__builtin_ctz(mask));
            mask &= mask - 1;
        }
    }

    free(masks);
    return cnt;
}

/* ---------------------------------------------------------------------------
 * 3. "enzyme" (k=6), rare-pair filter + per-candidate verify.
 * ------------------------------------------------------------------------- */

/* The rare-pair filter from cand_rare.c ('z' at needle offset 2, 'y' at offset
 * 3 — the two rarest bytes in the needle on English text), but under the
 * find-all contract.
 *
 * The filter mask is NOT exact: a set bit means only that 'z' and 'y' sit at the
 * right relative positions, so every set bit must be verified with the full
 * memcmp before it can be emitted. That is the difference the study is after.
 * Find-first paid for at most one verify in the entire scan — it returned on the
 * first success and the filter's job was to make failures rare. Find-all pays
 * for EVERY candidate bit, every time, because it must rebuild the filter mask
 * into an exact one before it can emit. The rare pair still keeps the candidate
 * count near the true match count on English text, which is precisely why it
 * survives the change of contract where a first+last filter would not.
 *
 * Offset arithmetic and bounds are as in cand_rare.c: loading 'z' candidates
 * from hay+i+2 and 'y' from hay+i+3 puts bit j at match start i+j, so the verify
 * is the plain memcmp at hay+i+j. The widest byte touched is the verify's
 * i+31+5 = i+36, so the chain's `i + 32 + 5 <= n` bound covers loads and
 * verifies alike. */
size_t fa_enzyme_rare2(const char *hay, size_t n, uint32_t *out, size_t cap)
{
    size_t cnt = 0;

    if (n < 6) {
        return 0;
    }

    const __m256i rare0 = _mm256_set1_epi8('z');
    const __m256i rare1 = _mm256_set1_epi8('y');

    size_t i = 0;
    for (; i + 32 + 5 <= n; i += 32) {
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));

        __m256i m = _mm256_and_si256(_mm256_cmpeq_epi8(v2, rare0),
                                     _mm256_cmpeq_epi8(v3, rare1));
        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);

        while (mask) {
            size_t off = i + (size_t)__builtin_ctz(mask);
            if (memcmp(hay + off, "enzyme", 6) == 0) {
                fa_emit(out, cap, &cnt, off);
            }
            mask &= mask - 1;
        }
    }

    for (; i + 6 <= n; i++) {
        if (hay[i] == 'e' && memcmp(hay + i, "enzyme", 6) == 0) {
            fa_emit(out, cap, &cnt, i);
        }
    }
    return cnt;
}

/* ---------------------------------------------------------------------------
 * 4. "wolf" (k=4), AND-chain, fused bit-walk emission.
 * ------------------------------------------------------------------------- */

/* Same shape as fa_enzyme_chain_ctz with a shorter needle: four loads, four
 * compares, three ANDs, and a `i + 32 + 3 <= n` bound because the highest byte a
 * block touches is i+3+31. */
size_t fa_wolf_chain(const char *hay, size_t n, uint32_t *out, size_t cap)
{
    size_t cnt = 0;

    if (n < 4) {
        return 0;
    }

    const __m256i bw = _mm256_set1_epi8('w');
    const __m256i bo = _mm256_set1_epi8('o');
    const __m256i bl = _mm256_set1_epi8('l');
    const __m256i bf = _mm256_set1_epi8('f');

    size_t i = 0;
    /* Highest byte touched this iteration is i+3+31; i+32+3<=n keeps every
     * load inside [hay, hay+n). */
    for (; i + 32 + 3 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));

        __m256i m = _mm256_cmpeq_epi8(v0, bw);
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v1, bo));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v2, bl));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v3, bf));

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);

        while (mask) {
            fa_emit(out, cap, &cnt, i + (size_t)__builtin_ctz(mask));
            mask &= mask - 1;
        }
    }

    for (; i + 4 <= n; i++) {
        if (hay[i] == 'w' && memcmp(hay + i, "wolf", 4) == 0) {
            fa_emit(out, cap, &cnt, i);
        }
    }
    return cnt;
}

/* ---------------------------------------------------------------------------
 * 5. "abab" (k=4, period 2), AND-chain — the self-overlap case.
 * ------------------------------------------------------------------------- */

/* "abab" has period 2, so occurrences overlap: "ababab" contains starts 0 and 2,
 * and "abababab" contains 0, 2 and 4. The find-all contract requires all of
 * them.
 *
 * The lane-parallel chain gets this for free, and that is the point of including
 * it. Every lane j independently answers "does a match start at i+j", with no
 * notion of a previous match and nothing to skip past — so overlapping starts
 * appear as adjacent set bits in the same mask and the bit-walk emits them in
 * ascending order without any special handling. A skip-based scanner (anything
 * that advances by the match length after a hit, or by a shift table keyed on
 * the last match) has to be careful here or it silently drops start 2. This
 * function exists to prove the chain is not one of those; it is byte-identical
 * in structure to fa_wolf_chain. */
size_t fa_abab_chain(const char *hay, size_t n, uint32_t *out, size_t cap)
{
    size_t cnt = 0;

    if (n < 4) {
        return 0;
    }

    const __m256i ba = _mm256_set1_epi8('a');
    const __m256i bb = _mm256_set1_epi8('b');

    size_t i = 0;
    /* Highest byte touched this iteration is i+3+31; i+32+3<=n keeps every
     * load inside [hay, hay+n). */
    for (; i + 32 + 3 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));

        __m256i m = _mm256_cmpeq_epi8(v0, ba);
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v1, bb));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v2, ba));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v3, bb));

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);

        while (mask) {
            fa_emit(out, cap, &cnt, i + (size_t)__builtin_ctz(mask));
            mask &= mask - 1;
        }
    }

    for (; i + 4 <= n; i++) {
        if (hay[i] == 'a' && memcmp(hay + i, "abab", 4) == 0) {
            fa_emit(out, cap, &cnt, i);
        }
    }
    return cnt;
}

/* ---------------------------------------------------------------------------
 * 6/7. Factor pair: "wolf", then a gap of 0..64 arbitrary bytes, then "enzyme".
 *
 * Emit the ascending "enzyme" starts p for which some "wolf" start a satisfies
 *
 *     a + 4 <= p <= a + 68        equivalently   a in [p-68, p-4]
 *
 * (a+4 is the first byte after the wolf, so gap = p-(a+4) lies in [0, 64].)
 *
 * Worked check: a wolf at 100 makes enzymes at p in [104, 168] eligible — gap 0
 * puts the enzyme at 104, gap 64 puts it at 168, and 169 is one byte too far.
 * ------------------------------------------------------------------------- */

/* Pending-wolf queue for the fused pairer.
 *
 * `latest_ok` is the greatest wolf start already known to be <= (current p)-4;
 * the ring holds wolf starts seen but not yet old enough to qualify, in
 * ascending order. Because both the wolves and the enzymes are consumed in
 * ascending position order, advancing the queue against a rising threshold is
 * monotone: once a wolf moves into latest_ok it never needs to come back, and
 * latest_ok only ever increases. Only the GREATEST qualifying wolf matters —
 * if it fails the a >= p-68 test, every older one fails it too — so a single
 * long is enough state for the qualified side. */
typedef struct {
    uint32_t ring[128];
    size_t head;        /* next to pop  */
    size_t tail;        /* next to push; tail-head is the pending count */
    long latest_ok;     /* -1 until some wolf has qualified */
} fa_wq;

static inline void fa_wq_push(fa_wq *q, uint32_t a)
{
    q->ring[q->tail & 127u] = a;
    q->tail++;
}

/* Move every pending wolf at position <= thresh into latest_ok. They are popped
 * ascending, so the last one moved is the greatest — exactly what latest_ok
 * must hold. */
static inline void fa_wq_advance(fa_wq *q, long thresh)
{
    while (q->head != q->tail) {
        long a = (long)q->ring[q->head & 127u];
        if (a > thresh) {
            break;
        }
        q->latest_ok = a;
        q->head++;
    }
}

static inline int fa_wq_pairs(const fa_wq *q, size_t p)
{
    return q->latest_ok >= 0 && q->latest_ok >= (long)p - 68;
}

/* One pass, shared loads, O(1) carry state across blocks.
 *
 * Per block the same six loads v0..v5 feed both needles: "wolf" uses v0..v3,
 * "enzyme" uses all six. Both masks index from the same base, so bit j of W is a
 * wolf start at i+j and bit j of E is an enzyme start at i+j. Both are exact by
 * construction (full AND-chains), so no verify is needed on either side.
 *
 * Block order of operations:
 *   (a) advance the queue against i-4, then
 *   (b) append this block's W bits, ascending, then
 *   (c) walk this block's E bits ascending, advancing against p-4 and testing.
 *
 * Step (a) is what bounds the ring. Advancing against i-4 is always legal
 * because every enzyme still to come sits at p >= i, hence p-4 >= i-4, so any
 * wolf qualifying at threshold i-4 qualifies for all of them; it is the same
 * monotone advance the per-p step does, just pulled forward. Without it, a long
 * stretch of wolves with no enzymes between them would pile up unboundedly.
 * With it, after (a) every pending wolf sits at a >= i-3, and (b) adds only
 * positions in [i, i+31], so the pending set always lives inside the 35-position
 * window [i-3, i+31] and can never exceed 35 entries. The scalar tail adds at
 * most 36 more before the scan ends, so 71 is the true worst case and the ring's
 * 128 slots (a power of two, so the wrap is a mask) cannot overflow.
 *
 * A wolf and an enzyme in the same block interleave correctly even though the
 * wolves all go in first: eligibility is decided by the exact positions
 * (a <= p-4), never by block order, so a wolf at i+20 pushed before an enzyme at
 * i+5 is examined and correctly left pending. */
size_t fa_pair_fused(const char *hay, size_t n, uint32_t *out, size_t cap)
{
    size_t cnt = 0;

    /* The second factor is the one emitted, so nothing can be reported unless
     * an "enzyme" fits. */
    if (n < 6) {
        return 0;
    }

    fa_wq q;
    q.head = 0;
    q.tail = 0;
    q.latest_ok = -1;

    const __m256i be = _mm256_set1_epi8('e');
    const __m256i bn = _mm256_set1_epi8('n');
    const __m256i bz = _mm256_set1_epi8('z');
    const __m256i by = _mm256_set1_epi8('y');
    const __m256i bm = _mm256_set1_epi8('m');
    const __m256i bw = _mm256_set1_epi8('w');
    const __m256i bo = _mm256_set1_epi8('o');
    const __m256i bl = _mm256_set1_epi8('l');
    const __m256i bf = _mm256_set1_epi8('f');

    size_t i = 0;
    /* The enzyme chain is the wider of the two, touching i+5+31. */
    for (; i + 32 + 5 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));
        __m256i v4 = _mm256_loadu_si256((const __m256i *)(hay + i + 4));
        __m256i v5 = _mm256_loadu_si256((const __m256i *)(hay + i + 5));

        __m256i mw = _mm256_cmpeq_epi8(v0, bw);
        mw = _mm256_and_si256(mw, _mm256_cmpeq_epi8(v1, bo));
        mw = _mm256_and_si256(mw, _mm256_cmpeq_epi8(v2, bl));
        mw = _mm256_and_si256(mw, _mm256_cmpeq_epi8(v3, bf));

        __m256i me = _mm256_cmpeq_epi8(v0, be);
        me = _mm256_and_si256(me, _mm256_cmpeq_epi8(v1, bn));
        me = _mm256_and_si256(me, _mm256_cmpeq_epi8(v2, bz));
        me = _mm256_and_si256(me, _mm256_cmpeq_epi8(v3, by));
        me = _mm256_and_si256(me, _mm256_cmpeq_epi8(v4, bm));
        me = _mm256_and_si256(me, _mm256_cmpeq_epi8(v5, be));

        uint32_t W = (uint32_t)_mm256_movemask_epi8(mw);
        uint32_t E = (uint32_t)_mm256_movemask_epi8(me);

        /* (a) keep the pending window small — see the bound argument above. */
        fa_wq_advance(&q, (long)i - 4);

        /* (b) this block's wolves, ascending. */
        while (W) {
            fa_wq_push(&q, (uint32_t)(i + (size_t)__builtin_ctz(W)));
            W &= W - 1;
        }

        /* (c) this block's enzymes, ascending. */
        while (E) {
            size_t p = i + (size_t)__builtin_ctz(E);
            fa_wq_advance(&q, (long)p - 4);
            if (fa_wq_pairs(&q, p)) {
                fa_emit(out, cap, &cnt, p);
            }
            E &= E - 1;
        }
    }

    /* Scalar tail, same state machine byte by byte.
     *
     * The loop stops at the last position where an "enzyme" can start. Feeding
     * wolves past that point would be wasted work: a wolf at a can only pair
     * with p >= a+4, and no p beyond n-6 exists, so every wolf that can still
     * matter starts at a <= n-10 and is inside this loop's range. i+6 <= n also
     * guarantees i+4 <= n, so the wolf memcmp below is in bounds. */
    for (; i + 6 <= n; i++) {
        if (hay[i] == 'w' && memcmp(hay + i, "wolf", 4) == 0) {
            fa_wq_push(&q, (uint32_t)i);
        }
        if (hay[i] == 'e' && memcmp(hay + i, "enzyme", 6) == 0) {
            fa_wq_advance(&q, (long)i - 4);
            if (fa_wq_pairs(&q, i)) {
                fa_emit(out, cap, &cnt, i);
            }
        }
    }
    return cnt;
}

/* The two-pass alternative to fa_pair_fused: materialize both factor lists with
 * the standalone find-all scanners, then merge them.
 *
 * This costs two full passes over the haystack instead of one (the fused version
 * derives both masks from a single set of loads) plus two intermediate arrays,
 * and buys a merge loop that is trivially obviously correct. That trade is the
 * measurement.
 *
 * The two-pointer merge is the same monotone advance the fused version runs
 * inline, with the queue replaced by an index into a sorted array: for each
 * enzyme p ascending, walk the wolf pointer up to the greatest wolf <= p-4, then
 * emit iff that wolf exists and is >= p-68.
 *
 * Sizing: n/8+16 entries per side is far above any density the study feeds it —
 * it allows a match every 8 bytes for needles of length 4 and 6. Truncation is
 * therefore treated as impossible here; the clamps below only keep the merge
 * from reading past what was actually stored if that assumption were ever
 * violated. */
size_t fa_pair_merge(const char *hay, size_t n, uint32_t *out, size_t cap)
{
    size_t cnt = 0;

    if (n < 6) {
        return 0;
    }

    const size_t side_cap = (n / 8) + 16;
    uint32_t *wolves = (uint32_t *)malloc(side_cap * sizeof(uint32_t));
    uint32_t *enzymes = (uint32_t *)malloc(side_cap * sizeof(uint32_t));
    if (!wolves || !enzymes) {
        /* Same answer, single pass. Not expected in the harness. */
        free(wolves);
        free(enzymes);
        return fa_pair_fused(hay, n, out, cap);
    }

    size_t nw = fa_wolf_chain(hay, n, wolves, side_cap);
    size_t ne = fa_enzyme_chain_ctz(hay, n, enzymes, side_cap);
    if (nw > side_cap) {
        nw = side_cap;
    }
    if (ne > side_cap) {
        ne = side_cap;
    }

    size_t wi = 0;
    long latest_ok = -1;
    for (size_t ei = 0; ei < ne; ei++) {
        long p = (long)enzymes[ei];
        while (wi < nw && (long)wolves[wi] <= p - 4) {
            latest_ok = (long)wolves[wi];
            wi++;
        }
        if (latest_ok >= 0 && latest_ok >= p - 68) {
            fa_emit(out, cap, &cnt, (size_t)p);
        }
    }

    free(wolves);
    free(enzymes);
    return cnt;
}
