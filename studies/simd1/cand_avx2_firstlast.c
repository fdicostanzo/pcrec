#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* Muła-style first+last filter: broadcast the needle's first and last byte,
 * AND their equality masks, then verify only the surviving candidates. */
const char *find_hello_avx2_fl(const char *hay, size_t n)
{
    if (n < 5) {
        return NULL;
    }

    const __m256i first = _mm256_set1_epi8('h');
    const __m256i last = _mm256_set1_epi8('o');

    size_t i = 0;
    /* Highest byte touched this iteration is i+4+31; i+32+4<=n keeps every
     * load inside [hay, hay+n). */
    for (; i + 32 + 4 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i));
        __m256i v4 = _mm256_loadu_si256((const __m256i *)(hay + i + 4));

        __m256i m = _mm256_and_si256(_mm256_cmpeq_epi8(v0, first),
                                      _mm256_cmpeq_epi8(v4, last));
        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);

        while (mask) {
            int j = __builtin_ctz(mask);
            if (memcmp(hay + i + j + 1, "ell", 3) == 0) {
                return hay + i + j;
            }
            mask &= mask - 1;
        }
    }

    for (; i + 5 <= n; i++) {
        if (hay[i] == 'h' && memcmp(hay + i, "hello", 5) == 0) {
            return hay + i;
        }
    }
    return NULL;
}
