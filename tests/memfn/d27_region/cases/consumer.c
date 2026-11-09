/* d27region consumer translation unit (match_api.md §6.3.10¶15 last two
 * sentences: "A consumer translation unit may therefore #include the
 * artifact and then use intrinsics, the C library or a second artifact,
 * for any target, after it").
 *
 * Built by d27/lib/d27.py with:
 *   -DART1='"path/a.c"' -DPFX1=prefix      the first artifact (included)
 *   -DART2='"path/b.c"' -DPFX2=prefix      optional second artifact
 *   -DSEPARATE                             include the .h files only
 *                                          (HDR1/HDR2), link the .o's
 *   -DHEADERS_FIRST                        the consumer's own headers
 *                                          come BEFORE the artifact(s)
 *   -DNOVEC                                the consumer itself uses no
 *                                          vector code (-mno-sse2,
 *                                          -mgeneral-regs-only builds)
 * argv[1]: a file of hex-encoded subjects, one per line.
 * Output lines (compared by d27.py against python3 re / plain C facts):
 *   A<k> <subject> <pos> <ret> <start> <end>   artifact k's _search
 *   C <subject> <sse2> <avx2> <libc> <memchr>  the consumer's own work
 *   M <__AVX2__> <__SSE4_2__> <__BMI2__>       predefined macros AFTER
 *                                              the artifact(s)
 */
#ifdef HEADERS_FIRST
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#if defined(__x86_64__) && !defined(NOVEC)
#include <emmintrin.h>
#include <immintrin.h>
#endif
#endif

#ifdef SEPARATE
#include HDR1
#ifdef HDR2
#include HDR2
#endif
#else
#include ART1
#ifdef ART2
#include ART2
#endif
#endif

/* After the artifact: the consumer's own headers (first read here unless
 * HEADERS_FIRST), so a header first read inside an artifact's region
 * would show up as a target mismatch below. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#if defined(__x86_64__) && !defined(NOVEC)
#include <emmintrin.h>
#include <immintrin.h>
#endif

#define CAT_(a, b) a##b
#define CAT(a, b) CAT_(a, b)

/* The consumer's own SSE2 use, in a function with the consumer's flags. */
static unsigned consumer_sse2(const unsigned char *p, size_t n, unsigned char c)
{
    unsigned k = 0;
    size_t i = 0;
#if defined(__x86_64__) && !defined(NOVEC)
    __m128i v = _mm_set1_epi8((char)c);
    for (; i + 16 <= n; i += 16) {
        __m128i x = _mm_loadu_si128((const __m128i *)(p + i));
        unsigned m = (unsigned)_mm_movemask_epi8(_mm_cmpeq_epi8(x, v));
        while (m) { k += m & 1u; m >>= 1; }
    }
#endif
    for (; i < n; i++)
        k += p[i] == c;
    return k;
}

/* The consumer's own AVX2 use: directly where its flags admit AVX2 (a
 * leaked __AVX2__ from an artifact's region would select this branch under
 * flags that do not admit it and fail to compile), else in a function the
 * consumer itself marks target("avx2"), called only on a CPU that has it. */
#if defined(__x86_64__) && !defined(NOVEC)
#if defined(__AVX2__)
static unsigned consumer_avx2(const unsigned char *p, size_t n, unsigned char c)
#else
__attribute__((target("avx2")))
static unsigned consumer_avx2(const unsigned char *p, size_t n, unsigned char c)
#endif
{
    unsigned k = 0;
    size_t i = 0;
    __m256i v = _mm256_set1_epi8((char)c);
    for (; i + 32 <= n; i += 32) {
        __m256i x = _mm256_loadu_si256((const __m256i *)(p + i));
        unsigned m = (unsigned)_mm256_movemask_epi8(_mm256_cmpeq_epi8(x, v));
        while (m) { k += m & 1u; m >>= 1; }
    }
    for (; i < n; i++)
        k += p[i] == c;
    return k;
}
#endif

/* The consumer's own fortified libc use (memcpy and strlen into a buffer
 * of known size: -D_FORTIFY_SOURCE=2 -O2 routes these through the
 * header's always-inline checking wrappers). */
static size_t consumer_libc(const unsigned char *s, size_t n)
{
    char buf[256];
    size_t m = n < sizeof buf - 1 ? n : sizeof buf - 1;
    memcpy(buf, s, m);
    buf[m] = '\0';
    return strlen(buf);
}

static long consumer_memchr(const unsigned char *s, size_t n)
{
    const unsigned char *q = n ? memchr(s, 'q', n) : NULL;
    return q ? (long)(q - s) : -1L;
}

static int hexval(int c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

static void run_one(int k, int (*search)(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]),
                    int idx, const unsigned char *s, size_t n)
{
    for (size_t pos = 0; pos <= n; pos++) {
        ptrdiff_t caps[64][2];
        int r = search(n ? s : NULL, n, pos, caps);
        printf("A%d %d %zu %d %td %td\n", k, idx, pos, r,
               r == 1 ? caps[0][0] : (ptrdiff_t)-1,
               r == 1 ? caps[0][1] : (ptrdiff_t)-1);
    }
}

int main(int argc, char **argv)
{
    static char line[8192];
    static unsigned char subj[4096];
    FILE *f;
    int idx = 0;
    if (argc != 2 || !(f = fopen(argv[1], "r"))) {
        fprintf(stderr, "usage: consumer SUBJECTS\n");
        return 2;
    }
    printf("M %d %d %d\n",
#ifdef __AVX2__
           1,
#else
           0,
#endif
#ifdef __SSE4_2__
           1,
#else
           0,
#endif
#ifdef __BMI2__
           1
#else
           0
#endif
    );
    while (fgets(line, sizeof line, f)) {
        size_t n = 0;
        for (char *p = line; p[0] && p[1] && hexval(p[0]) >= 0; p += 2)
            subj[n++] = (unsigned char)(hexval(p[0]) * 16 + hexval(p[1]));
        run_one(1, CAT(PFX1, _search), idx, subj, n);
#ifdef PFX2
        run_one(2, CAT(PFX2, _search), idx, subj, n);
#endif
        unsigned a2 = 0;
#if defined(__x86_64__) && !defined(NOVEC)
        __builtin_cpu_init();
        a2 = __builtin_cpu_supports("avx2") ? consumer_avx2(subj, n, 'q') : consumer_sse2(subj, n, 'q');
#else
        a2 = consumer_sse2(subj, n, 'q');
#endif
        printf("C %d %u %u %zu %ld\n", idx, consumer_sse2(subj, n, 'q'), a2,
               consumer_libc(subj, n), consumer_memchr(subj, n));
        idx++;
    }
    fclose(f);
    return 0;
}
