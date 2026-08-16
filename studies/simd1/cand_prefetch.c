#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* ---------------------------------------------------------------------------
 * Software prefetch distance experiment, on top of the rare-position filter
 * from find_enzyme_rare2 (needle "enzyme", filtering on 'z' at offset 2 and
 * 'y' at offset 3 — see cand_rare.c for the frequency argument).
 *
 * On a straight-line sequential scan like this one, software prefetch is
 * usually redundant: the hardware stream prefetcher in the L2 (and the L1
 * streamer ahead of it) already recognizes the linear access pattern to
 * `hay` after a couple of strides and starts fetching ahead on its own, and
 * whatever it doesn't cover in time is often hidden anyway by out-of-order
 * execution overlapping the load latency with independent work in later
 * iterations. Adding an explicit _mm_prefetch to a loop the hardware
 * prefetcher already tracks well is frequently a net wash or a slight loss
 * (extra uop, extra pressure on the prefetch/fill-buffer machinery) rather
 * than a win.
 *
 * The open question these three variants probe is whether that changes at
 * larger corpus sizes and larger prefetch distances than a stream prefetcher
 * typically runs ahead by:
 *
 *   - pf512 / pf1024: distances well within what a stream prefetcher would
 *     normally reach on its own once it locks onto the pattern, included as
 *     a control to see whether software prefetch at "hardware-territory"
 *     distances is neutral, helpful, or actively harmful.
 *
 *   - pf4096: one full 4 KiB page ahead. This is the interesting case —
 *     hardware stream prefetchers are generally scoped to a single physical
 *     page and will not prefetch across a page boundary (the next page may
 *     not even be contiguous in physical memory), so a software prefetch
 *     that lands on the next page is doing something hardware structurally
 *     cannot: it warms both the cache line and, as a side effect of the
 *     translation the prefetch triggers, the TLB entry for that next page
 *     before the scan's real loads get there. Whether that pays for itself
 *     depends on whether the working set is large enough (beyond L3, so
 *     each miss is a real DRAM round trip) that hiding page-crossing and
 *     TLB-miss latency ahead of time is worth the extra instruction.
 *
 * All three keep find_enzyme_rare2's structure and bounds contract exactly;
 * the only change is one _mm_prefetch call added at the top of the vector
 * loop body. Correctness is identical to find_enzyme_rare2 — the prefetch
 * result is discarded and never touches the mask/verify logic.
 *
 * Bounds contract note: _mm_prefetch is exempt from the usual guard-page
 * rule. A prefetch of an address that is unmapped, or past the end of a
 * guard-paged allocation, is architecturally defined to be a no-op — it
 * cannot fault or raise any exception, unlike a real load. That makes
 * hay+i+offset a legal prefetch target even when i+offset is well past
 * hay+n; it is the one case in this codebase where reading (prefetching)
 * past the end of the buffer is safe by construction. The loads, compares,
 * and memcmp verifies below are NOT exempt and keep the same
 * `i + 32 + 5 <= n` bound as find_enzyme_rare2 for that reason.
 * ------------------------------------------------------------------------- */

/* Prefetch 512 bytes ahead — 16 vector-loop iterations' worth of `hay`,
 * comfortably inside the range a hardware stream prefetcher already covers
 * once it has locked onto the sequential access pattern. */
const char *find_enzyme_pf512(const char *hay, size_t n)
{
    if (n < 6) {
        return NULL;
    }

    const __m256i rare0 = _mm256_set1_epi8('z');
    const __m256i rare1 = _mm256_set1_epi8('y');

    size_t i = 0;
    /* Highest byte touched this iteration is i+5+31 (the widest verify);
     * i+32+5<=n keeps every load and every memcmp inside [hay, hay+n).
     * The prefetch target hay+i+512 is exempt from this bound (see file
     * header): it may legally land past hay+n. */
    for (; i + 32 + 5 <= n; i += 32) {
        _mm_prefetch(hay + i + 512, _MM_HINT_T0);

        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));

        __m256i m = _mm256_and_si256(_mm256_cmpeq_epi8(v2, rare0),
                                     _mm256_cmpeq_epi8(v3, rare1));
        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);

        while (mask) {
            int j = __builtin_ctz(mask);
            if (memcmp(hay + i + j, "enzyme", 6) == 0) {
                return hay + i + j;
            }
            mask &= mask - 1;
        }
    }

    for (; i + 6 <= n; i++) {
        if (hay[i] == 'e' && memcmp(hay + i, "enzyme", 6) == 0) {
            return hay + i;
        }
    }
    return NULL;
}

/* Prefetch 1024 bytes ahead — still within reach of a stream prefetcher that
 * has ramped up its run-ahead distance, but far enough to start probing
 * whether extra distance alone (independent of crossing a page boundary)
 * buys anything once the corpus no longer fits in L2/L3. */
const char *find_enzyme_pf1024(const char *hay, size_t n)
{
    if (n < 6) {
        return NULL;
    }

    const __m256i rare0 = _mm256_set1_epi8('z');
    const __m256i rare1 = _mm256_set1_epi8('y');

    size_t i = 0;
    /* Highest byte touched this iteration is i+5+31 (the widest verify);
     * i+32+5<=n keeps every load and every memcmp inside [hay, hay+n).
     * The prefetch target hay+i+1024 is exempt from this bound (see file
     * header): it may legally land past hay+n. */
    for (; i + 32 + 5 <= n; i += 32) {
        _mm_prefetch(hay + i + 1024, _MM_HINT_T0);

        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));

        __m256i m = _mm256_and_si256(_mm256_cmpeq_epi8(v2, rare0),
                                     _mm256_cmpeq_epi8(v3, rare1));
        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);

        while (mask) {
            int j = __builtin_ctz(mask);
            if (memcmp(hay + i + j, "enzyme", 6) == 0) {
                return hay + i + j;
            }
            mask &= mask - 1;
        }
    }

    for (; i + 6 <= n; i++) {
        if (hay[i] == 'e' && memcmp(hay + i, "enzyme", 6) == 0) {
            return hay + i;
        }
    }
    return NULL;
}

/* Prefetch 4096 bytes ahead — one full page. This distance necessarily
 * crosses a 4 KiB boundary that hardware stream prefetchers will not cross
 * on their own, so the prefetch here warms both a cache line on the next
 * page and, incidentally, that page's TLB entry ahead of when the scan's
 * real loads would otherwise trigger the walk. This is the variant most
 * likely to show a benefit distinct from what the hardware already does,
 * and only at corpus sizes that push working set past L3. */
const char *find_enzyme_pf4096(const char *hay, size_t n)
{
    if (n < 6) {
        return NULL;
    }

    const __m256i rare0 = _mm256_set1_epi8('z');
    const __m256i rare1 = _mm256_set1_epi8('y');

    size_t i = 0;
    /* Highest byte touched this iteration is i+5+31 (the widest verify);
     * i+32+5<=n keeps every load and every memcmp inside [hay, hay+n).
     * The prefetch target hay+i+4096 is exempt from this bound (see file
     * header): it may legally land past hay+n. */
    for (; i + 32 + 5 <= n; i += 32) {
        _mm_prefetch(hay + i + 4096, _MM_HINT_T0);

        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));

        __m256i m = _mm256_and_si256(_mm256_cmpeq_epi8(v2, rare0),
                                     _mm256_cmpeq_epi8(v3, rare1));
        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);

        while (mask) {
            int j = __builtin_ctz(mask);
            if (memcmp(hay + i + j, "enzyme", 6) == 0) {
                return hay + i + j;
            }
            mask &= mask - 1;
        }
    }

    for (; i + 6 <= n; i++) {
        if (hay[i] == 'e' && memcmp(hay + i, "enzyme", 6) == 0) {
            return hay + i;
        }
    }
    return NULL;
}
