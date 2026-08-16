/* runext.c -- per-anchor class-run extension microbenchmark.
 *
 * SELF-CONTAINED: libc + immintrin.h only, own main(), no project headers.
 * Build:  cc -O3 -mavx2 -std=gnu11 -Wall -Wextra -o runext runext.c
 * The resulting binary has no data files or arguments, so it can be copied to
 * another machine (Intel or AMD; Linux assumed) and run as-is.
 *
 * QUESTION MEASURED -----------------------------------------------------
 * Given an anchor position (an '@'), how fast can we measure the length of
 * the contiguous run of class [a-zA-Z.] bytes immediately BEFORE the anchor?
 * This models the left atom of a regex like  [a-zA-Z.]+@  where the run is
 * typically 5-15 bytes.  Every candidate has the signature
 *
 *     size_t f(const char *hay, size_t anchor)
 *
 * and returns the count of consecutive class bytes at hay[anchor-1],
 * hay[anchor-2], ...  It must never read at or below hay[0]-1: the scan stops
 * at offset 0.  anchor >= 1 is guaranteed by the caller.
 *
 * MICROBENCH HYGIENE ----------------------------------------------------
 * Every candidate is __attribute__((noinline)) and is reached through a
 * *volatile* function-pointer table.  Without both of those the compiler is
 * free to inline a candidate into the timing loop, hoist the table loads /
 * shuffle constants, and specialize on the anchor stride -- which would make
 * the numbers describe a program nobody will ever ship.
 */

#define _GNU_SOURCE
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <sys/mman.h>
#include <immintrin.h>

#ifndef __AVX2__
#error "runext.c needs -mavx2 (the 128-bit candidates are deliberately VEX-encoded too)"
#endif

/* ====================================================================== */
/* Class definition                                                       */
/* ====================================================================== */

/* GNU range designators (we are -std=gnu11).  1 == member of [a-zA-Z.] */
static const uint8_t cls_tbl[256] = {
    ['a' ... 'z'] = 1,
    ['A' ... 'Z'] = 1,
    ['.'] = 1,
};

/* ---------------------------------------------------------------------- *
 * shufti nibble tables for the class {0x61..0x7a, 0x41..0x5a, 0x2e}.
 *
 * Construction rule:  for each member byte b (all members are < 0x80)
 *     lo_tbl[b & 15] |= 1 << (b >> 4);
 *     hi_tbl[h]       = 1 << h        for h < 8,  0 for h >= 8
 * A byte is a member iff  (lo_tbl[b&15] & hi_tbl[b>>4]) != 0.
 *
 * Members by high nibble:  hi=2 -> {0x2e}
 *                          hi=4 -> 0x41..0x4f (A..O)
 *                          hi=5 -> 0x50..0x5a (P..Z)
 *                          hi=6 -> 0x61..0x6f (a..o)
 *                          hi=7 -> 0x70..0x7a (p..z)
 * Working the low-nibble column out by hand:
 *   j=0 : P(0x50,hi5) p(0x70,hi7)                 -> 0x20|0x80 = 0xA0
 *   j=1 : A Q a q     (hi 4,5,6,7)                -> 0x10|0x20|0x40|0x80 = 0xF0
 *   j=2..10 (0x2..0xa): B..J / R..Z / b..j / r..z -> 0xF0   (0x5a='Z', 0x7a='z'
 *                                                    are the last of their rows,
 *                                                    so j=10 still has all four)
 *   j=11: K(0x4b) k(0x6b) only; 0x5b='[' 0x7b='{' -> 0x10|0x40 = 0x50
 *   j=12: L l                                     -> 0x50
 *   j=13: M m                                     -> 0x50
 *   j=14: N(0x4e) n(0x6e) AND '.'(0x2e, hi=2)     -> 0x10|0x40|0x04 = 0x54
 *   j=15: O(0x4f) o(0x6f)                         -> 0x50
 * Spot checks of non-members:
 *   '@'=0x40 -> lo[0]=0xA0 & hi[4]=0x10 = 0     (critical: the anchor itself)
 *   ' '=0x20 -> lo[0]=0xA0 & hi[2]=0x04 = 0     (word separator)
 *   '['=0x5b -> lo[11]=0x50 & hi[5]=0x20 = 0
 *   '{'=0x7b -> lo[11]=0x50 & hi[7]=0x80 = 0
 *   '_'=0x5f -> lo[15]=0x50 & hi[5]=0x20 = 0
 *   '`'=0x60 -> lo[0]=0xA0  & hi[6]=0x40 = 0
 *   '0'=0x30 -> lo[0]=0xA0  & hi[3]=0x08 = 0
 *   '>'=0x3e -> lo[14]=0x54 & hi[3]=0x08 = 0    ('.'-column, wrong row)
 * Bytes >= 0x80 fall out for free: the lo lookup is done with the *unmasked*
 * data vector, and pshufb zeroes any lane whose index has bit 7 set.
 * ---------------------------------------------------------------------- */
static const uint8_t shufti_lo[16] = {
    0xA0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0, 0xF0,
    0xF0, 0xF0, 0xF0, 0x50, 0x50, 0x50, 0x54, 0x50
};
static const uint8_t shufti_hi[16] = {
    0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
};

/* Scalar continuation shared by the vector remnants.  `len` bytes have already
 * been accepted, so the next byte to test is hay[anchor-1-len]; len == anchor
 * means the scan has reached offset 0 and must stop. */
static inline size_t scalar_back(const char *hay, size_t anchor, size_t len)
{
    while (len < anchor && cls_tbl[(uint8_t)hay[anchor - 1 - len]])
        len++;
    return len;
}

/* ====================================================================== */
/* Candidate 1: scalar table loop                                         */
/* ====================================================================== */

/* One load + table lookup + test + branch per byte.  The run-end branch is the
 * interesting cost: for a random run length it mispredicts once per anchor. */
__attribute__((noinline))
static size_t run_scalar_map(const char *hay, size_t anchor)
{
    size_t len = 0;
    while (len < anchor && cls_tbl[(uint8_t)hay[anchor - 1 - len]])
        len++;
    return len;
}

/* ====================================================================== */
/* Candidate 2: 128-bit shufti                                            */
/* ====================================================================== */

/* Deliberately 128-bit while compiled under -mavx2: every _mm_* intrinsic here
 * is VEX-encoded (vpshufb xmm, ...), so there is no legacy-SSE/AVX transition
 * penalty and no vzeroupper concern -- this is "AVX-128", not SSE.  The point
 * of the candidate is the 16-byte *width*, not the encoding. */

/* Returns 0xFF in lanes that are NOT class members (cmpeq-against-zero is the
 * only cheap way to get a mask, since the and-result can be 0x80 and would
 * read as negative to a signed cmpgt). */
static inline __m128i nonmember128(__m128i v, __m128i lo_t, __m128i hi_t)
{
    __m128i lo = _mm_shuffle_epi8(lo_t, v); /* unmasked index: >=0x80 -> 0 */
    __m128i hn = _mm_and_si128(_mm_srli_epi16(v, 4), _mm_set1_epi8(0x0f));
    __m128i hi = _mm_shuffle_epi8(hi_t, hn);
    return _mm_cmpeq_epi8(_mm_and_si128(lo, hi), _mm_setzero_si128());
}

__attribute__((noinline))
static size_t run_xmm16(const char *hay, size_t anchor)
{
    const __m128i lo_t = _mm_loadu_si128((const __m128i *)shufti_lo);
    const __m128i hi_t = _mm_loadu_si128((const __m128i *)shufti_hi);
    size_t front = anchor; /* bytes [0,front) are still unscanned */
    size_t len = 0;

    while (front >= 16) {
        __m128i v = _mm_loadu_si128((const __m128i *)(hay + front - 16));
        /* bit j of m == membership of hay[front-16+j]; bit 15 is the byte
         * immediately before the un-scanned front. */
        uint32_t nm = (uint32_t)(uint16_t)_mm_movemask_epi8(nonmember128(v, lo_t, hi_t));
        uint32_t m = (~nm) & 0xFFFFu;

        /* Bit algebra: shifting the 16-bit mask to the TOP of a u32 puts the
         * byte adjacent to the front at bit 31, so "contiguous set bits
         * downward from bit 15" becomes "leading ones of a u32".  Complement
         * turns leading-one counting into leading-zero counting, which is what
         * the hardware gives us.  The low 16 bits of (m<<16) are zero, so the
         * complement is never zero and clz is never called on 0.  m==0xFFFF
         * yields r==16: the whole block is class, keep going. */
        unsigned r = (unsigned)__builtin_clz(~(m << 16));
        len += r;
        front -= r;
        if (r < 16)
            return len; /* found the run end inside this block */
    }
    /* Fewer than 16 bytes precede the front: a 16-byte back-load would read
     * below hay[0], so finish scalar. */
    return scalar_back(hay, anchor, len);
}

/* ====================================================================== */
/* Candidate 3: 256-bit shufti                                            */
/* ====================================================================== */

static inline __m256i nonmember256(__m256i v, __m256i lo_t, __m256i hi_t)
{
    /* vpshufb is per-128-bit-lane, hence the broadcast tables. */
    __m256i lo = _mm256_shuffle_epi8(lo_t, v);
    __m256i hn = _mm256_and_si256(_mm256_srli_epi16(v, 4), _mm256_set1_epi8(0x0f));
    __m256i hi = _mm256_shuffle_epi8(hi_t, hn);
    return _mm256_cmpeq_epi8(_mm256_and_si256(lo, hi), _mm256_setzero_si256());
}

__attribute__((noinline))
static size_t run_ymm32(const char *hay, size_t anchor)
{
    const __m256i lo_t = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)shufti_lo));
    const __m256i hi_t = _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)shufti_hi));
    size_t front = anchor;
    size_t len = 0;

    while (front >= 32) {
        __m256i v = _mm256_loadu_si256((const __m256i *)(hay + front - 32));
        /* bit j == membership of hay[front-32+j], so bit 31 is the byte just
         * before the front -- the mask already fills the u32 and needs no
         * pre-shift.  Counting leading member bits == counting leading zeros
         * of the *non*-member mask, which movemask hands us directly.  The
         * all-members block makes that zero, where __builtin_clz is undefined,
         * so spell out r=32 ("whole block is class, keep going"). */
        uint32_t nonmem = (uint32_t)_mm256_movemask_epi8(nonmember256(v, lo_t, hi_t));
        unsigned r = nonmem ? (unsigned)__builtin_clz(nonmem) : 32u;
        len += r;
        front -= r;
        if (r < 32)
            return len;
    }
    return scalar_back(hay, anchor, len);
}

/* ====================================================================== */
/* Candidate 4: 128-bit range compares (isolates shufti vs range)          */
/* ====================================================================== */

/* b in [lo,hi]  <=>  (uint8_t)(b-lo) <= hi-lo.  sub_epi8 wraps, subs_epu8
 * saturates to 0 exactly when the wrapped value is within the span, so the
 * cmpeq-against-zero result is the in-range mask (0xFF = in range).  Safe
 * because hi < 0xff, so an underflowing byte wraps above hi-lo. */
static inline __m128i in_range128(__m128i v, uint8_t lo, uint8_t hi)
{
    __m128i shifted = _mm_sub_epi8(v, _mm_set1_epi8((char)lo));
    __m128i sat = _mm_subs_epu8(shifted, _mm_set1_epi8((char)(uint8_t)(hi - lo)));
    return _mm_cmpeq_epi8(sat, _mm_setzero_si128());
}

__attribute__((noinline))
static size_t run_xmm16_range(const char *hay, size_t anchor)
{
    size_t front = anchor;
    size_t len = 0;

    while (front >= 16) {
        __m128i v = _mm_loadu_si128((const __m128i *)(hay + front - 16));
        __m128i mem = _mm_or_si128(
            _mm_or_si128(in_range128(v, 'a', 'z'), in_range128(v, 'A', 'Z')),
            _mm_cmpeq_epi8(v, _mm_set1_epi8('.')));
        /* cmpeq already gives 0xFF for members, so no inversion here. */
        uint32_t m = (uint32_t)(uint16_t)_mm_movemask_epi8(mem);
        unsigned r = (unsigned)__builtin_clz(~(m << 16));
        len += r;
        front -= r;
        if (r < 16)
            return len;
    }
    return scalar_back(hay, anchor, len);
}

/* ====================================================================== */
/* Candidate table (volatile: see MICROBENCH HYGIENE above)                */
/* ====================================================================== */

typedef size_t (*runlen_fn)(const char *hay, size_t anchor);

#define NCAND 4
static const char *const cand_name[NCAND] = {
    "scalar_map", "xmm16_shufti", "ymm32_shufti", "xmm16_range"
};
static runlen_fn volatile g_fns[NCAND];

/* ====================================================================== */
/* Deterministic PRNG                                                     */
/* ====================================================================== */

static uint64_t sm_state;

static inline uint64_t sm64(void)
{
    uint64_t z = (sm_state += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}
static inline uint32_t sm32(void) { return (uint32_t)(sm64() >> 32); }
/* Unbiased enough for corpus generation, and branch-free. */
static inline uint32_t sm_below(uint32_t n) { return (uint32_t)(((uint64_t)sm32() * n) >> 32); }
static inline int sm_pct(uint32_t p) { return sm_below(100) < p; }

/* ====================================================================== */
/* Corpus                                                                 */
/* ====================================================================== */

#define CORPUS_N ((size_t)4 * 1024 * 1024)
#define MARGIN 300u
#define BASE_SEED 0x5EED1234ABCDEF01ULL

/* English-like filler: words of geometric length (mean ~6) made of letters,
 * mostly lowercase, single-space separated, ~2% of words followed by '.'.
 * Spaces terminate class runs naturally, so the base text has a realistic
 * distribution of "accidental" run lengths around any position. */
static void build_base(char *buf, size_t n)
{
    size_t i = 0;
    while (i < n) {
        /* geometric with p = 1/6 -> mean length 6 */
        uint32_t wlen = 1;
        while (wlen < 64 && sm_below(6) != 0)
            wlen++;
        for (uint32_t k = 0; k < wlen && i < n; k++) {
            int upper = (k == 0) ? sm_pct(8) : sm_pct(2);
            char c = (char)((upper ? 'A' : 'a') + (int)sm_below(26));
            buf[i++] = c;
        }
        if (i < n && sm_pct(2))
            buf[i++] = '.';
        if (i < n)
            buf[i++] = ' ';
    }
}

/* ====================================================================== */
/* Anchors                                                                */
/* ====================================================================== */

typedef struct {
    uint32_t pos; /* index of the '@' */
    uint32_t len; /* planted run length */
} anchor_t;

typedef enum { LEN_FIXED, LEN_UNIFORM } len_kind;

typedef struct {
    const char *name;
    len_kind kind;
    uint32_t a, b; /* fixed: a==b; uniform: inclusive [a,b] */
} len_dist;

static const len_dist dists[] = {
    { "L=5",      LEN_FIXED,   5,   5 },
    { "L=15",     LEN_FIXED,  15,  15 },
    { "L=50",     LEN_FIXED,  50,  50 },
    { "L=200",    LEN_FIXED, 200, 200 },
    { "U(3,20)",  LEN_UNIFORM, 3,  20 },
    { "U(3,60)",  LEN_UNIFORM, 3,  60 },
};
#define NDIST ((int)(sizeof(dists) / sizeof(dists[0])))

static const double densities[] = { 0.001, 0.01 };
#define NDENS ((int)(sizeof(densities) / sizeof(densities[0])))

/* The naive oracle -- an independent copy of the table loop, deliberately NOT
 * one of the candidates, so a bug shared with run_scalar_map cannot hide. */
static size_t oracle_runlen(const char *hay, size_t anchor)
{
    size_t len = 0;
    while (len < anchor) {
        uint8_t c = (uint8_t)hay[anchor - 1 - len];
        if (!(c == '.' || (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')))
            break;
        len++;
    }
    return len;
}

/* Plant anchors into `hay` (a fresh copy of the base text) and record them.
 *
 * PLACEMENT / DEVIATION FROM THE 260-BYTE RULE ---------------------------
 * The brief asked for random positions with >= 260 bytes between anchors.  At
 * the 1% density that is arithmetically impossible: 1% of 4 MiB is 41943
 * anchors and 41943 * 260 = 10.9 MB > 4 MiB.  (Even the correctness floor
 * L+2 is infeasible for L=200 at 1%: 41943 * 202 = 8.5 MB.)  So:
 *
 *   - Placement is stratified-with-jitter: the usable span is cut into `want`
 *     equal slots of width W and anchor i lands uniformly inside slot i,
 *     restricted so that the gap to its neighbour is >= `spacing`.  This is
 *     random per anchor, deterministic across machines, O(n), and cannot fail
 *     the way rejection sampling does at high occupancy.
 *   - `spacing` is the requested 260 wherever the density leaves room for it
 *     (that is every length at 0.1% density), and otherwise drops to the
 *     correctness floor maxL+2 -- all that is needed to keep the planted
 *     regions of neighbouring anchors disjoint.
 *   - If even the floor does not fit (L=200 at 1%), `want` is reduced to what
 *     fits and the achieved count is reported with a '*' in the table.
 */
static size_t plant(char *hay, const char *base, size_t n, const len_dist *d,
                    double density, anchor_t *out, size_t *out_spacing)
{
    memcpy(hay, base, n);

    size_t usable = n - 2 * (size_t)MARGIN;
    size_t maxL = d->b;
    size_t floor_sp = maxL + 2; /* run + the ' ' terminator, so regions stay disjoint */
    size_t want = (size_t)(density * (double)n);
    if (want < 1)
        want = 1;

    size_t spacing = floor_sp > 260 ? floor_sp : 260;
    size_t W = usable / want;
    if (W < spacing)
        spacing = floor_sp;
    if (W < spacing) { /* still too dense: give up count, not correctness */
        want = usable / spacing;
        W = usable / want;
    }
    size_t jit = W - spacing;

    for (size_t i = 0; i < want; i++) {
        size_t p = (size_t)MARGIN + i * W + sm_below((uint32_t)jit + 1u);
        uint32_t L = (d->kind == LEN_FIXED)
                         ? d->a
                         : d->a + sm_below(d->b - d->a + 1u);

        hay[p] = '@';
        for (uint32_t k = 1; k <= L; k++) {
            char c;
            if (sm_pct(5))
                c = '.';
            else
                c = (char)((sm_pct(15) ? 'A' : 'a') + (int)sm_below(26));
            hay[p - k] = c;
        }
        hay[p - L - 1] = ' '; /* hard stop for the run */

        out[i].pos = (uint32_t)p;
        out[i].len = L;
    }
    *out_spacing = spacing;
    return want;
}

/* ====================================================================== */
/* Timing                                                                 */
/* ====================================================================== */

static volatile size_t g_sink;

static double now_s(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec * 1e-9;
}

__attribute__((noinline))
static size_t sweep(int ci, const char *hay, const anchor_t *an, size_t na)
{
    runlen_fn f = g_fns[ci]; /* volatile load: defeats devirtualization */
    size_t s = 0;
    for (size_t i = 0; i < na; i++)
        s += f(hay, an[i].pos);
    return s;
}

#define MIN_SECS 0.050
#define TRIALS 5

static double bench(int ci, const char *hay, const anchor_t *an, size_t na)
{
    double t0 = now_s();
    g_sink += sweep(ci, hay, an, na);
    double one = now_s() - t0;
    if (one < 1e-9)
        one = 1e-9;

    size_t reps = (size_t)(MIN_SECS / one) + 1;
    if (reps > ((size_t)1 << 24))
        reps = (size_t)1 << 24;

    double best = 1e300;
    for (int t = 0; t < TRIALS; t++) {
        double s0 = now_s();
        for (size_t r = 0; r < reps; r++)
            g_sink += sweep(ci, hay, an, na);
        double el = now_s() - s0;
        if (el < best)
            best = el;
    }
    return best * 1e9 / ((double)reps * (double)na);
}

/* ====================================================================== */
/* Guard-page test                                                        */
/* ====================================================================== */

/* Place a short haystack at the very start of a readable page whose preceding
 * page is PROT_NONE.  Any candidate that does a 16- or 32-byte back-load when
 * fewer than 16/32 bytes precede the anchor will fault here rather than
 * silently returning a plausible number on some other machine. */
static int guard_test(void)
{
    long ps = sysconf(_SC_PAGESIZE);
    if (ps <= 0)
        ps = 4096;
    char *region = mmap(NULL, (size_t)ps * 2, PROT_READ | PROT_WRITE,
                        MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (region == MAP_FAILED) {
        fprintf(stderr, "guard: mmap failed\n");
        return 1;
    }
    if (mprotect(region, (size_t)ps, PROT_NONE) != 0) {
        fprintf(stderr, "guard: mprotect failed\n");
        return 1;
    }
    char *hay = region + ps; /* hay[-1] is unreadable */

    /* offset 7 is the case the brief called for; the others straddle the
     * 16- and 32-byte block boundaries, where an off-by-one in the "can I do
     * one more wide load?" test would step off the page. */
    static const size_t offs[] = { 7, 15, 16, 17, 31, 32, 33 };
    int bad = 0;

    for (size_t oi = 0; oi < sizeof(offs) / sizeof(offs[0]); oi++) {
        size_t a = offs[oi];
        memset(hay, ' ', 40);
        for (size_t k = 0; k < a; k++)
            hay[k] = (k % 7 == 3) ? '.' : (char)((k % 3 == 0 ? 'A' : 'a') + (int)(k % 26));
        hay[a] = '@';

        if (oracle_runlen(hay, a) != a) {
            fprintf(stderr, "guard: oracle disagrees at offset %zu\n", a);
            bad = 1;
        }
        for (int c = 0; c < NCAND; c++) {
            size_t got = g_fns[c](hay, a);
            if (got != a) {
                fprintf(stderr, "guard: %s(anchor=%zu) = %zu, want %zu\n",
                        cand_name[c], a, got, a);
                bad = 1;
            }
        }
    }
    munmap(region, (size_t)ps * 2);
    return bad;
}

/* ====================================================================== */
/* main                                                                   */
/* ====================================================================== */

static void print_isa(void)
{
    printf("build ISA:");
#ifdef __x86_64__
    printf(" x86-64");
#endif
#ifdef __SSE4_2__
    printf(" SSE4.2");
#endif
#ifdef __AVX__
    printf(" AVX");
#endif
#ifdef __AVX2__
    printf(" AVX2");
#endif
#ifdef __BMI__
    printf(" BMI");
#endif
#ifdef __BMI2__
    printf(" BMI2");
#endif
#ifdef __LZCNT__
    printf(" LZCNT");
#endif
#ifdef __AVX512F__
    printf(" AVX512F");
#endif
#ifdef __AVX512BW__
    printf(" AVX512BW");
#endif
    printf("\n");
}

int main(void)
{
    int rc = 0;

    g_fns[0] = run_scalar_map;
    g_fns[1] = run_xmm16;
    g_fns[2] = run_ymm32;
    g_fns[3] = run_xmm16_range;

    printf("=== runext: per-anchor class-run extension, class [a-zA-Z.] ===\n");
    print_isa();
    printf("self-contained binary (libc + immintrin only, no data files) -- copy and run anywhere\n");
    printf("corpus: %zu bytes English-like text, splitmix64 seed 0x%016llx\n",
           CORPUS_N, (unsigned long long)BASE_SEED);
    printf("timing: best of %d, each >= %.0f ms, reported as ns per anchor\n\n",
           TRIALS, MIN_SECS * 1e3);

    if (guard_test()) {
        fprintf(stderr, "GUARD-PAGE TEST FAILED\n");
        return 2;
    }
    printf("guard-page test: OK (no under-read below hay[0] at anchors 7..33)\n\n");

    char *base = malloc(CORPUS_N);
    char *hay = malloc(CORPUS_N + 64);
    anchor_t *an = malloc(sizeof(anchor_t) * (CORPUS_N / 8 + 16));
    if (!base || !hay || !an) {
        fprintf(stderr, "out of memory\n");
        return 2;
    }

    sm_state = BASE_SEED;
    build_base(base, CORPUS_N);

    int truncated_any = 0;

    for (int di = 0; di < NDENS; di++) {
        double dens = densities[di];
        size_t requested = (size_t)(dens * (double)CORPUS_N);

        printf("--- anchor density %.2f%% (%zu anchors requested) ---\n",
               dens * 100.0, requested);
        printf("%-10s %9s %6s", "dist", "anchors", "gap");
        for (int c = 0; c < NCAND; c++)
            printf(" %14s", cand_name[c]);
        printf("\n");

        for (int i = 0; i < NDIST; i++) {
            const len_dist *d = &dists[i];
            size_t spacing = 0;

            /* Re-seed per cell so a cell's corpus does not depend on which
             * cells ran before it. */
            sm_state = BASE_SEED ^ (0x100000001B3ULL * (uint64_t)(di * 64 + i + 1));
            size_t na = plant(hay, base, CORPUS_N, d, dens, an, &spacing);

            /* Every anchor must read back exactly the length we planted. */
            size_t oracle_sum = 0;
            for (size_t k = 0; k < na; k++) {
                size_t got = oracle_runlen(hay, an[k].pos);
                if (got != an[k].len) {
                    fprintf(stderr,
                            "SETUP VERIFY FAILED: %s d=%.3f anchor %zu at %u: "
                            "oracle=%zu planted=%u\n",
                            d->name, dens, k, an[k].pos, got, an[k].len);
                    return 3;
                }
                oracle_sum += got;
            }

            int truncated = (na < requested);
            truncated_any |= truncated;

            printf("%-10s %8zu%c %6zu", d->name, na, truncated ? '*' : ' ', spacing);
            for (int c = 0; c < NCAND; c++) {
                size_t s = sweep(c, hay, an, na);
                if (s != oracle_sum) {
                    fprintf(stderr,
                            "\nVERIFY FAILED: %s on %s d=%.3f: sum=%zu want=%zu\n",
                            cand_name[c], d->name, dens, s, oracle_sum);
                    printf(" %14s", "FAIL");
                    rc = 4;
                    continue;
                }
                printf(" %14.2f", bench(c, hay, an, na));
            }
            printf("\n");
            fflush(stdout);
        }
        printf("\n");
    }

    printf("notes:\n");
    printf("  * READ THE MIXED ROWS FIRST.  In the fixed-L rows every run has the\n");
    printf("    same length, so the scalar loop's exit branch is perfectly\n");
    printf("    predictable and scalar_map is flattered by an amount that does not\n");
    printf("    exist in real inputs.  U(3,20) and U(3,60) are the honest cells:\n");
    printf("    they pay the mispredict a real regex engine would pay.\n");
    printf("  * 'gap' is the enforced minimum byte distance between anchors.  It is\n");
    printf("    260 where the density allows, else maxL+2 (enough to keep planted\n");
    printf("    runs disjoint) -- 1%% density leaves only ~100 bytes per anchor, so\n");
    printf("    260 is arithmetically impossible there.\n");
    if (truncated_any)
        printf("  * rows marked '*' could not fit the requested anchor count at the\n"
               "    minimum gap; the count shown is what was planted, so the achieved\n"
               "    density for those rows is lower than the heading says.\n");
    printf("  * xmm16_* are VEX-encoded (AVX-128) because the file is built with\n"
           "    -mavx2; the 16 vs 32 comparison is about width, not encoding.\n");
    printf("  * xmm16_range vs xmm16_shufti isolates classification method at equal\n"
           "    width; ymm32_shufti vs xmm16_shufti isolates width at equal method.\n");

    free(base);
    free(hay);
    free(an);
    if (g_sink == 0x123456789ULL) /* never true; keeps the sink observable */
        printf("sink=%zu\n", g_sink);
    return rc;
}
