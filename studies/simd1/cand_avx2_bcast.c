#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* Per-position broadcast compare: each of the five needle bytes gets its own
 * broadcast register; a lane surviving all five ANDs is a confirmed match
 * start, so no verify step is needed. */
const char *find_hello_avx2_bcast(const char *hay, size_t n)
{
    if (n < 5) {
        return NULL;
    }

    const __m256i bh = _mm256_set1_epi8('h');
    const __m256i be = _mm256_set1_epi8('e');
    const __m256i bl = _mm256_set1_epi8('l');
    const __m256i bo = _mm256_set1_epi8('o');

    size_t i = 0;
    /* Highest byte touched this iteration is i+4+31; i+32+4<=n keeps every
     * load inside [hay, hay+n). */
    for (; i + 32 + 4 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));
        __m256i v3 = _mm256_loadu_si256((const __m256i *)(hay + i + 3));
        __m256i v4 = _mm256_loadu_si256((const __m256i *)(hay + i + 4));

        __m256i m = _mm256_cmpeq_epi8(v0, bh);
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v1, be));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v2, bl));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v3, bl));
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v4, bo));

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz(mask);
        }
    }

    for (; i + 5 <= n; i++) {
        if (hay[i] == 'h' && memcmp(hay + i, "hello", 5) == 0) {
            return hay + i;
        }
    }
    return NULL;
}
