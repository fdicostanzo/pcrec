/* memfn R1 probe: the fixed per-call cost of a byte search, by binding form.
 *
 * Question (requirements.md §2): what does a FUNCTION CALL cost against an
 * INLINE body, by span length, so the binding-form criterion rests on a
 * number rather than an argument. Kernels, all "find the first byte == c in
 * s[0..n)", NULL if absent, never reading outside s[0..n):
 *
 *   libc       memchr (out of line: PLT/stub + the libc ISA ladder)
 *   scalar     static inline byte loop
 *   swar       static inline 8-byte SWAR, memcpy loads, byte-loop tail
 *   vec        static inline 16-byte vector loop, byte-loop tail
 *              (NEON on aarch64, SSE2 on x86-64)
 *   vec_ov     vec, but the tail is ONE overlapped final block ending at n
 *              (n >= 16); n < 16 is the byte loop
 *   vec_sm     vec_ov plus a loop-free short path for n < 16 (overlapping
 *              SWAR words / three probes): the "no call, no loop" floor
 *   *_ool      the same body behind __attribute__((noinline)): the call
 *              cost of OUR code, separated from libc's body
 *   pair_libc  two memchr calls, min of the hits (K82's pair arm)
 *   pair_vec   inline 16-byte two-byte search, overlapped final block,
 *              two overlapping SWAR words for 8..15, byte loop below 8
 *
 * Each span is the MISS case (the needle is absent, the whole span is read:
 * the gate that rejects), plus a hit-at-0 row for the pure entry cost.
 *
 * Two modes:
 *   dep   the next call's start pointer depends on this call's result
 *         (a true data dependency: latency, the "result feeds the next
 *         decision" bound)
 *   ind   calls are independent (throughput: the out-of-order core may
 *         overlap consecutive calls)
 *
 * Timing (D144 addendum 1): every timed loop is calibrated to >= 50 ms, run
 * REPEATS times; we print min and max ns/call so the spread (the noise
 * floor, same program) sits next to every number. The "loop" row is the
 * harness's own per-iteration overhead with no search in it. Mac numbers
 * are directional only; the same source is owed on the Linux x86 box.
 *
 * Correctness: --check runs every kernel against the scalar reference over
 * n in 0..300, every hit position (and none), alignments 0..15, with the
 * span ending exactly at the end of a heap allocation; build it with
 * -fsanitize=address to prove no over-read (make -f probes.mk check-asan).
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if defined(__ARM_NEON)
#include <arm_neon.h>
#define VEC_NAME "neon"
#elif defined(__SSE2__)
#include <emmintrin.h>
#define VEC_NAME "sse2"
#else
#error "probe needs NEON or SSE2 (both are the ISA baselines)"
#endif

#define INL static inline __attribute__((always_inline))
#define OOL __attribute__((noinline))

/* ---- kernels ---------------------------------------------------------- */

INL const uint8_t *k_scalar(const uint8_t *s, uint8_t c, size_t n)
{
    for (size_t i = 0; i < n; i++)
        if (s[i] == c)
            return s + i;
    return NULL;
}

INL const uint8_t *k_swar(const uint8_t *s, uint8_t c, size_t n)
{
    const uint64_t ones = 0x0101010101010101ull, highs = 0x8080808080808080ull;
    const uint64_t vc = ones * c;
    size_t i = 0;
    for (; i + 8 <= n; i += 8) {
        uint64_t w;
        memcpy(&w, s + i, 8);
        w ^= vc;
        /* exact zero-byte mask (no false positives above a true zero):
         * high bit of each byte set iff that byte of w is 0 */
        uint64_t z = ~(((w & ~highs) + ~highs) | w) & highs;
        if (z)
            return s + i + (__builtin_ctzll(z) >> 3); /* little-endian */
    }
    for (; i < n; i++)
        if (s[i] == c)
            return s + i;
    return NULL;
}

#if defined(__ARM_NEON)
/* 16 compare lanes -> a 64-bit nibble mask (the shrn trick: NEON has no
 * movemask). Bit 4k..4k+3 set iff lane k matched. */
INL uint64_t vmask(uint8x16_t eq)
{
    return vget_lane_u64(vreinterpret_u64_u8(
        vshrn_n_u16(vreinterpretq_u16_u8(eq), 4)), 0);
}
#define VMASK_SHIFT 2 /* ctz >> 2 = lane */
INL uint64_t veq1(const uint8_t *p, uint8_t c)
{
    return vmask(vceqq_u8(vld1q_u8(p), vdupq_n_u8(c)));
}
INL uint64_t veq2(const uint8_t *p, uint8_t a, uint8_t b)
{
    uint8x16_t v = vld1q_u8(p);
    return vmask(vorrq_u8(vceqq_u8(v, vdupq_n_u8(a)),
                          vceqq_u8(v, vdupq_n_u8(b))));
}
#else
#define VMASK_SHIFT 0
INL uint64_t veq1(const uint8_t *p, uint8_t c)
{
    __m128i v = _mm_loadu_si128((const __m128i *)p);
    return (uint64_t)_mm_movemask_epi8(_mm_cmpeq_epi8(v, _mm_set1_epi8((char)c)));
}
INL uint64_t veq2(const uint8_t *p, uint8_t a, uint8_t b)
{
    __m128i v = _mm_loadu_si128((const __m128i *)p);
    return (uint64_t)_mm_movemask_epi8(_mm_or_si128(
        _mm_cmpeq_epi8(v, _mm_set1_epi8((char)a)),
        _mm_cmpeq_epi8(v, _mm_set1_epi8((char)b))));
}
#endif

INL const uint8_t *k_vec(const uint8_t *s, uint8_t c, size_t n)
{
    size_t i = 0;
    for (; i + 16 <= n; i += 16) {
        uint64_t m = veq1(s + i, c);
        if (m)
            return s + i + (__builtin_ctzll(m) >> VMASK_SHIFT);
    }
    for (; i < n; i++)
        if (s[i] == c)
            return s + i;
    return NULL;
}

INL const uint8_t *k_vec_ov(const uint8_t *s, uint8_t c, size_t n)
{
    if (n < 16) {
        for (size_t i = 0; i < n; i++)
            if (s[i] == c)
                return s + i;
        return NULL;
    }
    size_t i = 0;
    for (; i + 16 <= n; i += 16) {
        uint64_t m = veq1(s + i, c);
        if (m)
            return s + i + (__builtin_ctzll(m) >> VMASK_SHIFT);
    }
    if (i < n) { /* one final block ending at n; bytes before i already missed */
        uint64_t m = veq1(s + n - 16, c);
        if (m)
            return s + n - 16 + (__builtin_ctzll(m) >> VMASK_SHIFT);
    }
    return NULL;
}

/* exact zero-byte mask of a word: bit 7 of byte k set iff byte k of w is 0 */
INL uint64_t zbytes64(uint64_t w)
{
    const uint64_t highs = 0x8080808080808080ull;
    return ~(((w & ~highs) + ~highs) | w) & highs;
}

/* vec_ov plus a LOOP-FREE short path below 16: two overlapping 8-byte SWAR
 * words for 8..15, two overlapping 4-byte words for 4..7, and three probes
 * s[0], s[n>>1], s[n-1] for 1..3 (which cover every position, in order).
 * Every load stays inside s[0..n). */
INL const uint8_t *k_vec_sm(const uint8_t *s, uint8_t c, size_t n)
{
    if (n >= 16)
        return k_vec_ov(s, c, n);
    const uint64_t vc = 0x0101010101010101ull * c;
    if (n >= 8) {
        uint64_t a, b;
        memcpy(&a, s, 8);
        memcpy(&b, s + n - 8, 8);
        uint64_t za = zbytes64(a ^ vc), zb = zbytes64(b ^ vc);
        if (za) return s + (__builtin_ctzll(za) >> 3);
        if (zb) return s + n - 8 + (__builtin_ctzll(zb) >> 3);
        return NULL;
    }
    if (n >= 4) {
        uint32_t a, b;
        memcpy(&a, s, 4);
        memcpy(&b, s + n - 4, 4);
        uint64_t za = zbytes64((uint64_t)(a ^ (uint32_t)vc) | 0xFFFFFFFF00000000ull);
        uint64_t zb = zbytes64((uint64_t)(b ^ (uint32_t)vc) | 0xFFFFFFFF00000000ull);
        if (za) return s + (__builtin_ctzll(za) >> 3);
        if (zb) return s + n - 4 + (__builtin_ctzll(zb) >> 3);
        return NULL;
    }
    if (n == 0) return NULL;
    if (s[0] == c) return s;
    if (s[n >> 1] == c) return s + (n >> 1);
    if (s[n - 1] == c) return s + n - 1;
    return NULL;
}

INL const uint8_t *k_pair_vec(const uint8_t *s, uint8_t a, uint8_t b, size_t n)
{
    if (n < 16) { /* vec_sm's loop-free short path, two needles */
        const uint64_t va = 0x0101010101010101ull * a, vb = 0x0101010101010101ull * b;
        if (n >= 8) {
            uint64_t x, y;
            memcpy(&x, s, 8);
            memcpy(&y, s + n - 8, 8);
            uint64_t zx = zbytes64(x ^ va) | zbytes64(x ^ vb);
            uint64_t zy = zbytes64(y ^ va) | zbytes64(y ^ vb);
            if (zx) return s + (__builtin_ctzll(zx) >> 3);
            if (zy) return s + n - 8 + (__builtin_ctzll(zy) >> 3);
            return NULL;
        }
        for (size_t i = 0; i < n; i++)
            if (s[i] == a || s[i] == b)
                return s + i;
        return NULL;
    }
    size_t i = 0;
    for (; i + 16 <= n; i += 16) {
        uint64_t m = veq2(s + i, a, b);
        if (m)
            return s + i + (__builtin_ctzll(m) >> VMASK_SHIFT);
    }
    if (i < n) {
        uint64_t m = veq2(s + n - 16, a, b);
        if (m)
            return s + n - 16 + (__builtin_ctzll(m) >> VMASK_SHIFT);
    }
    return NULL;
}

INL const uint8_t *k_pair_libc(const uint8_t *s, uint8_t a, uint8_t b, size_t n)
{
    const uint8_t *p = memchr(s, a, n), *q = memchr(s, b, n);
    if (!p) return q;
    if (!q) return p;
    return p < q ? p : q;
}

OOL const uint8_t *k_scalar_ool(const uint8_t *s, uint8_t c, size_t n) { return k_scalar(s, c, n); }
OOL const uint8_t *k_vec_ool(const uint8_t *s, uint8_t c, size_t n) { return k_vec_sm(s, c, n); }

/* ---- the variant table ------------------------------------------------ */

enum { V_LOOP, V_LIBC, V_SCALAR, V_SWAR, V_VEC, V_VEC_OV, V_VEC_SM,
       V_SCALAR_OOL, V_VEC_OOL, V_PAIR_LIBC, V_PAIR_VEC, NV };
static const char *const vname[NV] = {
    "loop", "libc", "scalar", "swar", VEC_NAME, VEC_NAME "_ov", VEC_NAME "_sm",
    "scalar_ool", VEC_NAME "_sm_ool", "pair_libc", ("pair_" VEC_NAME),
};

/* One call of variant v. A switch on a loop-invariant v: gcc/clang unswitch
 * it out of the timed loop (checked in the disassembly, probes.mk asm). */
INL const uint8_t *call(int v, const uint8_t *s, size_t n)
{
    switch (v) {
    case V_LOOP:       return s;
    case V_LIBC:       return memchr(s, 'Z', n);
    case V_SCALAR:     return k_scalar(s, 'Z', n);
    case V_SWAR:       return k_swar(s, 'Z', n);
    case V_VEC:        return k_vec(s, 'Z', n);
    case V_VEC_OV:     return k_vec_ov(s, 'Z', n);
    case V_VEC_SM:     return k_vec_sm(s, 'Z', n);
    case V_SCALAR_OOL: return k_scalar_ool(s, 'Z', n);
    case V_VEC_OOL:    return k_vec_ool(s, 'Z', n);
    case V_PAIR_LIBC:  return k_pair_libc(s, 'Z', 'z', n);
    default:           return k_pair_vec(s, 'Z', 'z', n);
    }
}

/* ---- timing ----------------------------------------------------------- */

static double now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* Instantiated per variant (constant v) so each timed loop is its own
 * straight-line code. expect: the pointer every call returns. */
#define TIMER(V)                                                              \
    OOL static double run_##V(const uint8_t *buf, size_t n, const uint8_t *expect, \
                              long reps, int dep)                             \
    {                                                                         \
        const uint8_t *s = buf;                                               \
        double t0 = now_ns();                                                 \
        if (dep) {                                                            \
            for (long r = 0; r < reps; r++) {                                 \
                const uint8_t *p = call(V, s, n);                             \
                /* off == 0, but only known after p is: a data dependency */ \
                uintptr_t off = (uintptr_t)p ^ (uintptr_t)expect;             \
                s = buf + off;                                                \
            }                                                                 \
        } else {                                                              \
            for (long r = 0; r < reps; r++) {                                 \
                const uint8_t *q = s;                                         \
                __asm__ volatile("" : "+r"(q));                               \
                const uint8_t *p = call(V, q, n);                             \
                __asm__ volatile("" : : "r"(p));                              \
            }                                                                 \
        }                                                                     \
        __asm__ volatile("" : : "r"(s));                                      \
        return now_ns() - t0;                                                 \
    }
TIMER(0) TIMER(1) TIMER(2) TIMER(3) TIMER(4) TIMER(5) TIMER(6) TIMER(7) TIMER(8) TIMER(9)
TIMER(10)
typedef double (*runner)(const uint8_t *, size_t, const uint8_t *, long, int);
static const runner runners[NV] = { run_0, run_1, run_2, run_3, run_4,
                                    run_5, run_6, run_7, run_8, run_9, run_10 };

#define MIN_LOOP_NS 50e6 /* D144 addendum 1: >= ~50 ms per timed loop */
#define REPEATS 3

static void measure(int v, const uint8_t *buf, size_t n, const uint8_t *expect,
                    int dep, double *lo, double *hi)
{
    long reps = 1024;
    double t;
    while ((t = runners[v](buf, n, expect, reps, dep)) < MIN_LOOP_NS)
        reps = (long)(reps * (t > 1e5 ? 1.2 * MIN_LOOP_NS / t : 16.0));
    *lo = 1e300, *hi = 0;
    for (int k = 0; k < REPEATS; k++) {
        double x = runners[v](buf, n, expect, reps, dep) / reps;
        if (x < *lo) *lo = x;
        if (x > *hi) *hi = x;
    }
}

/* ---- correctness ------------------------------------------------------ */

static int check(void)
{
    long cases = 0, bad = 0;
    for (size_t n = 0; n <= 300; n++)
        for (size_t al = 0; al < 16; al++) {
            /* the span ends exactly at the end of its allocation: an
             * over-read past n is an ASan heap-buffer-overflow */
            uint8_t *blk = malloc(al + n + 1);
            uint8_t *s = blk + al;
            for (size_t h = 0; h <= n; h++) { /* h == n: absent */
                for (size_t i = 0; i < n; i++)
                    s[i] = (uint8_t)('a' + (i * 7 + al) % 20); /* never Z, z */
                if (h < n) s[h] = (h & 1) ? 'z' : 'Z';
                const uint8_t *want1 = (h < n && !(h & 1)) ? s + h : NULL;
                const uint8_t *want2 = h < n ? s + h : NULL;
                for (int v = V_LIBC; v < NV; v++) {
                    const uint8_t *want = v >= V_PAIR_LIBC ? want2 : want1;
                    const uint8_t *got = call(v, s, n);
                    cases++;
                    if (got != want) {
                        if (bad++ < 10)
                            printf("BAD %s n=%zu al=%zu h=%zu\n", vname[v], n, al, h);
                    }
                }
            }
            free(blk);
        }
    printf("check: %ld cases, %ld bad\n", cases, bad);
    return bad != 0;
}

int main(int argc, char **argv)
{
    if (argc > 1 && !strcmp(argv[1], "--check"))
        return check();
    static const size_t ns[] = { 1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 128,
                                 256, 512, 1024, 4096 };
    const size_t NN = sizeof ns / sizeof ns[0];
    uint8_t *buf = aligned_alloc(64, 8192);
    for (int i = 0; i < 8192; i++)
        buf[i] = (uint8_t)('a' + i % 20);
    printf("# memfn callcost probe, vec=%s, ns/call min..max of %d loops >= %.0f ms\n",
           VEC_NAME, REPEATS, MIN_LOOP_NS / 1e6);
    for (int dep = 1; dep >= 0; dep--) {
        printf("\n## mode=%s  case=miss (whole span read)\n%-14s", dep ? "dep" : "ind", "n");
        for (size_t j = 0; j < NN; j++) printf(" %13zu", ns[j]);
        printf("\n");
        for (int v = 0; v < NV; v++) {
            printf("%-14s", vname[v]);
            for (size_t j = 0; j < NN; j++) {
                double lo, hi;
                measure(v, buf, ns[j], v == V_LOOP ? buf : NULL, dep, &lo, &hi);
                printf(" %6.2f..%-6.2f", lo, hi);
                fflush(stdout);
            }
            printf("\n");
        }
        printf("## mode=%s  case=hit-at-0, n=64 (entry cost)\n", dep ? "dep" : "ind");
        buf[0] = 'Z';
        for (int v = 1; v < NV; v++) {
            double lo, hi;
            measure(v, buf, 64, buf, dep, &lo, &hi);
            printf("%-14s %6.2f..%-6.2f\n", vname[v], lo, hi);
        }
        buf[0] = 'a';
    }
    return 0;
}
