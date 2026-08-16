#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* Saturating-subtract range test: for a value v and inclusive range
 * [lo,hi], shift so lo maps to 0 (t = v - lo; bytes below lo wrap around
 * mod 256, landing on large unsigned values), then a *saturating*
 * unsigned subtract of the range width (hi-lo) clamps to 0 exactly when
 * unsigned t <= hi-lo (i.e. v in [lo,hi]) and stays positive otherwise.
 * cmpeq against zero turns "in range" into an all-ones byte mask. This
 * is the standard branch-free idiom for testing an arbitrary [lo,hi]
 * byte range under AVX2, which has no unsigned-compare instruction, and
 * it works for any lo/hi (not just digits). */
const char *find_rng_digits(const char *hay, size_t n)
{
    if (n < 4) {
        return NULL;
    }

    const __m256i zero    = _mm256_setzero_si256();
    const __m256i lo_zero = _mm256_set1_epi8('0');
    const __m256i width9  = _mm256_set1_epi8(9); /* '9' - '0' */
    const __m256i bp      = _mm256_set1_epi8('p');
    const __m256i bx      = _mm256_set1_epi8('x');

    size_t i = 0;
    /* Highest byte touched this iteration is i+3+31; i+32+3<=n keeps every
     * load inside [hay, hay+n). */
    for (; i + 32 + 3 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));

        /* Position 0 and 1: '0'..'9' via saturating-subtract range test. */
        __m256i t0  = _mm256_sub_epi8(v0, lo_zero);
        __m256i in0 = _mm256_cmpeq_epi8(_mm256_subs_epu8(t0, width9), zero);

        __m256i t1  = _mm256_sub_epi8(v1, lo_zero);
        __m256i in1 = _mm256_cmpeq_epi8(_mm256_subs_epu8(t1, width9), zero);

        /* Position 2 and 3: plain literal bytes 'p' and 'x'. */
        __m256i m = _mm256_and_si256(in0, in1);
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v2, bp));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v3, bx));

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz(mask);
        }
    }

    for (; i + 4 <= n; i++) {
        char c0 = hay[i];
        char c1 = hay[i + 1];
        if (c0 >= '0' && c0 <= '9' &&
            c1 >= '0' && c1 <= '9' &&
            hay[i + 2] == 'p' && hay[i + 3] == 'x') {
            return hay + i;
        }
    }
    return NULL;
}
