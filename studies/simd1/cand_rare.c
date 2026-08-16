#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* ---------------------------------------------------------------------------
 * Rare-position filter selection, demonstrated on the needle "enzyme" (k=6).
 *
 * All three functions here find the leftmost "enzyme" and differ only in which
 * needle positions feed the SIMD pre-filter. That choice is the whole story:
 * the vector work per 32-byte block is nearly identical, but the number of
 * blocks that survive the filter and fall into the scalar verify loop varies by
 * two orders of magnitude on English text.
 *
 * Approximate English letter frequencies for the six needle bytes:
 *
 *     position:   0    1    2     3    4    5
 *     byte:      'e'  'n'  'z'   'y'  'm'  'e'
 *     freq:     12.7% 6.7% 0.07% 2.0% 2.4% 12.7%
 *
 * A filter on positions p and q passes a lane with probability ~f(p)*f(q) if we
 * pretend adjacent letters are independent (they are not — English is heavily
 * correlated — but the ranking this gives is right, and that is all we need):
 *
 *     first+last ('e','e'):  0.127 * 0.127  ~= 1.6e-2   (worst available pair)
 *     rarest two ('z','y'):  0.0007 * 0.020 ~= 1.4e-5   (~1150x better)
 *
 * Per 32-lane block, the chance that *some* lane survives is
 * 1-(1-p)^32: about 40% for 'e'/'e' versus about 0.05% for 'z'/'y'. So the
 * first+last filter drops into the verify loop on roughly half of all blocks,
 * while the rare-pair filter rejects essentially every block with two loads,
 * two compares, one AND and one movemask.
 *
 * The lesson is that first+last is a default, not a rule. It is only a good
 * default because it needs no knowledge of the alphabet's distribution. When
 * the needle's byte frequencies are known, filtering on the two rarest
 * positions — wherever they sit in the needle — is strictly better, at the cost
 * of some offset arithmetic when those positions are interior.
 * ------------------------------------------------------------------------- */

/* Content-independent reference: compare all six needle positions in vector
 * registers and AND the masks together. A surviving lane is a confirmed match,
 * so there is no verify step and no dependence on how common the bytes are.
 * Six loads and six compares per block, always. */
const char *find_enzyme_chain(const char *hay, size_t n)
{
    if (n < 6) {
        return NULL;
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
        if (mask) {
            return hay + i + __builtin_ctz(mask);
        }
    }

    for (; i + 6 <= n; i++) {
        if (hay[i] == 'e' && memcmp(hay + i, "enzyme", 6) == 0) {
            return hay + i;
        }
    }
    return NULL;
}

/* Classic first+last filter — and, for this needle on English text, the worst
 * filter available. Both endpoints of "enzyme" are 'e', the single most common
 * letter in English at ~12.7%, so a lane passes with probability ~1.6% and
 * about 40% of 32-lane blocks carry at least one false candidate into the
 * verify loop. The vector work per block is cheap (two loads, two compares) but
 * the scalar memcmp path runs constantly, which is exactly what the filter was
 * supposed to prevent. Included as the deliberately bad baseline. */
const char *find_enzyme_fl(const char *hay, size_t n)
{
    if (n < 6) {
        return NULL;
    }

    const __m256i first = _mm256_set1_epi8('e');
    const __m256i last = _mm256_set1_epi8('e');

    size_t i = 0;
    /* Highest byte touched this iteration is i+5+31; i+32+5<=n keeps every
     * load inside [hay, hay+n). */
    for (; i + 32 + 5 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i));
        __m256i v5 = _mm256_loadu_si256((const __m256i *)(hay + i + 5));

        __m256i m = _mm256_and_si256(_mm256_cmpeq_epi8(v0, first),
                                     _mm256_cmpeq_epi8(v5, last));
        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);

        /* Bit j set means 'e' at i+j and 'e' at i+j+5, so the candidate match
         * starts at i+j and only the middle four bytes remain to check. */
        while (mask) {
            int j = __builtin_ctz(mask);
            if (memcmp(hay + i + j + 1, "nzym", 4) == 0) {
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

/* Same structure as find_enzyme_fl, but filtering on the two rarest positions
 * instead of the two endpoints: 'z' at needle offset 2 (~0.07% of English
 * letters) and 'y' at offset 3 (~2.0%). Per-lane pass probability is roughly
 * 0.0007*0.02 ~= 1.4e-5, so essentially every block is rejected outright and
 * the verify loop is entered only for genuine near-matches.
 *
 * Offset arithmetic. The filter positions are interior to the needle, so the
 * loads are shifted to make the mask bit index line up with the match start:
 * load 'z' candidates from hay+i+2 and 'y' candidates from hay+i+3. Lane j of
 * those vectors then holds hay[i+j+2] and hay[i+j+3] respectively, so bit j set
 * means 'z' at i+j+2 and 'y' at i+j+3 — which is exactly needle offsets 2 and 3
 * of a candidate whose first byte sits at i+j. The verify is therefore the
 * plain memcmp(hay+i+j, "enzyme", 6), same base as the first+last version.
 *
 * Bounds. Shifting the loads up by 2 and 3 costs nothing here: the highest byte
 * read by the loads is i+3+31 = i+34, below the i+5+31 = i+36 the chain already
 * reads, and the verify at bit j=31 touches up to i+31+5 = i+36 as well. Keeping
 * the chain's `i + 32 + 5 <= n` bound thus covers both the loads and every
 * verify. */
const char *find_enzyme_rare2(const char *hay, size_t n)
{
    if (n < 6) {
        return NULL;
    }

    const __m256i rare0 = _mm256_set1_epi8('z');
    const __m256i rare1 = _mm256_set1_epi8('y');

    size_t i = 0;
    /* Highest byte touched this iteration is i+5+31 (the widest verify);
     * i+32+5<=n keeps every load and every memcmp inside [hay, hay+n). */
    for (; i + 32 + 5 <= n; i += 32) {
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
