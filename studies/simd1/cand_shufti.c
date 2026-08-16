#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* Shufti (nibble-lookup) membership test for S = {a,e,i,o,u,0,3,6,9,_}.
 *
 * Split each candidate byte b into a low nibble (b & 0xf) and a high
 * nibble (b >> 4). For every member of S, record its high nibble as a
 * single set bit, keyed by its low nibble:
 *     lo_tbl[b & 0xf] |= 1 << (b >> 4)
 * and hi_tbl[h] = 1 << h reproduces that same bit, keyed by high nibble
 * (0 for h in 8..15 - all members here are ASCII, so no member's high
 * nibble reaches 8).
 *
 * For a haystack byte, AND-ing lo_tbl[lo] with hi_tbl[hi] is nonzero
 * iff some member of S shares both nibbles with that byte. Since a
 * (lo,hi) nibble pair uniquely determines a byte value, that only
 * happens when the byte itself is a member - the test is exact, with
 * no false positives, for this character set.
 *
 * Table derivation, by hand, from the member bytes:
 *   a=0x61 -> lo=0x1 hi=0x6 : lo_tbl[1] |= 1<<6 = 0x40
 *   e=0x65 -> lo=0x5 hi=0x6 : lo_tbl[5] |= 1<<6 = 0x40
 *   i=0x69 -> lo=0x9 hi=0x6 : lo_tbl[9] |= 1<<6 = 0x40
 *   o=0x6f -> lo=0xf hi=0x6 : lo_tbl[f] |= 1<<6 = 0x40
 *   u=0x75 -> lo=0x5 hi=0x7 : lo_tbl[5] |= 1<<7 = 0x80
 *   0=0x30 -> lo=0x0 hi=0x3 : lo_tbl[0] |= 1<<3 = 0x08
 *   3=0x33 -> lo=0x3 hi=0x3 : lo_tbl[3] |= 1<<3 = 0x08
 *   6=0x36 -> lo=0x6 hi=0x3 : lo_tbl[6] |= 1<<3 = 0x08
 *   9=0x39 -> lo=0x9 hi=0x3 : lo_tbl[9] |= 1<<3 = 0x08
 *   _=0x5f -> lo=0xf hi=0x5 : lo_tbl[f] |= 1<<5 = 0x20
 * folding duplicate lo-nibble entries together gives:
 *   lo_tbl[0x0] = 0x08                    (from '0')
 *   lo_tbl[0x1] = 0x40                    (from 'a')
 *   lo_tbl[0x3] = 0x08                    (from '3')
 *   lo_tbl[0x5] = 0x40 | 0x80 = 0xc0      (from 'e', 'u')
 *   lo_tbl[0x6] = 0x08                    (from '6')
 *   lo_tbl[0x9] = 0x40 | 0x08 = 0x48      (from 'i', '9')
 *   lo_tbl[0xf] = 0x40 | 0x20 = 0x60      (from 'o', '_')
 *   all other entries 0x00
 * and hi_tbl[h] = 1<<h for h in 0..7, else 0.
 */
static const uint8_t lo_tbl[16] = {
    0x08, 0x40, 0x00, 0x08, 0x00, 0xc0, 0x08, 0x00,
    0x00, 0x48, 0x00, 0x00, 0x00, 0x00, 0x00, 0x60,
};
static const uint8_t hi_tbl[16] = {
    0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
};

static int is_scatter_member(char c)
{
    return memchr("aeiou0369_", c, 10) != NULL;
}

const char *find_shufti_scatter(const char *hay, size_t n)
{
    if (n < 3) {
        return NULL;
    }

    /* pshufb (_mm256_shuffle_epi8) shuffles within each 128-bit lane
     * independently, so both lanes need an identical copy of the table:
     * load the 16-byte table once and broadcast it into both lanes of a
     * ymm register. */
    const __m128i lo_tbl128 = _mm_loadu_si128((const __m128i *)lo_tbl);
    const __m128i hi_tbl128 = _mm_loadu_si128((const __m128i *)hi_tbl);
    const __m256i lo_tbl_v  = _mm256_broadcastsi128_si256(lo_tbl128);
    const __m256i hi_tbl_v  = _mm256_broadcastsi128_si256(hi_tbl128);

    const __m256i nibble_mask = _mm256_set1_epi8(0x0f);
    const __m256i zero        = _mm256_setzero_si256();
    const __m256i bz          = _mm256_set1_epi8('z');
    const __m256i bq          = _mm256_set1_epi8('q');

    size_t i = 0;
    /* Highest byte touched this iteration is i+2+31; i+32+2<=n keeps every
     * load inside [hay, hay+n). */
    for (; i + 32 + 2 <= n; i += 32) {
        __m256i v0 = _mm256_loadu_si256((const __m256i *)(hay + i + 0));
        __m256i v1 = _mm256_loadu_si256((const __m256i *)(hay + i + 1));
        __m256i v2 = _mm256_loadu_si256((const __m256i *)(hay + i + 2));

        __m256i lo = _mm256_shuffle_epi8(lo_tbl_v, _mm256_and_si256(v0, nibble_mask));

        /* Extracting the high nibble of every byte with a single AVX2 op:
         * there is no per-byte shift, but a 16-bit-lane shift right by 4
         * followed by masking to the low 4 bits of each byte recovers
         * exactly the high nibble of that byte - the bits that leak in
         * from the neighboring (lower-addressed) byte land above the
         * mask and are discarded. Bytes >= 0x80 land in hi nibble 8..15,
         * where hi_tbl is all zero, so they come out "not a member" for
         * free with no separate high-bit check needed. */
        __m256i hi_nib = _mm256_and_si256(_mm256_srli_epi16(v0, 4), nibble_mask);
        __m256i hi = _mm256_shuffle_epi8(hi_tbl_v, hi_nib);

        __m256i t = _mm256_and_si256(lo, hi); /* nonzero byte == member */

        /* Position 1 and 2: plain literal bytes 'z' and 'q'. */
        __m256i m = _mm256_cmpeq_epi8(v1, bz);
        m = _mm256_and_si256(m, _mm256_cmpeq_epi8(v2, bq));
        /* Fold the membership test (t != 0) into the AND chain without
         * materializing a separate not-equal mask: andnot(cmpeq(t,0), m)
         * clears exactly the lanes where t is zero, i.e. keeps m only
         * where position 0 was a member of S. */
        m = _mm256_andnot_si256(_mm256_cmpeq_epi8(t, zero), m);

        uint32_t mask = (uint32_t)_mm256_movemask_epi8(m);
        if (mask) {
            return hay + i + __builtin_ctz(mask);
        }
    }

    for (; i + 3 <= n; i++) {
        if (is_scatter_member(hay[i]) && hay[i + 1] == 'z' && hay[i + 2] == 'q') {
            return hay + i;
        }
    }
    return NULL;
}
