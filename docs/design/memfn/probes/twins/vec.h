/* memfn twins: the vector layer every twin is written against, plus the
 * shared timing and guard-page helpers. One header, three ISAs:
 *
 *   NEON   (aarch64)              VW = 16, VHAVE_TBL = 1 (tbl)
 *   SSE2   (x86-64 baseline)      VW = 16, VHAVE_TBL = 0
 *   SSSE3  (-mssse3)              VW = 16, VHAVE_TBL = 1 (pshufb)
 *   AVX2   (-mavx2)               VW = 32, VHAVE_TBL = 1 (vpshufb, per lane:
 *                                 a 16-entry table is broadcast to both lanes)
 *
 * A "compare vector" has 0xFF in matching lanes and 0 elsewhere. vmask()
 * turns one into a bit mask with 1 << VMASK_SHIFT bits per lane (NEON: the
 * shrn nibble mask, 4 bits a lane; x86: movemask, 1 bit a lane), so the
 * first matching lane is ctz(mask) >> VMASK_SHIFT.
 *
 * Mac numbers are directional only (D144 addendum 1); the x86 builds are
 * for the Linux run (twins_linux_run.sh) and for a Rosetta 2 correctness
 * pass on the Mac (probes.mk twins-check-x86).
 */
#ifndef MEMFN_TWINS_VEC_H
#define MEMFN_TWINS_VEC_H

#include <setjmp.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

#define INL static inline __attribute__((always_inline))
#define OOL __attribute__((noinline))

#if defined(__ARM_NEON)
#include <arm_neon.h>
#define VISA "neon"
#define VW 16
#define VHAVE_TBL 1
#define VMASK_SHIFT 2
typedef uint8x16_t vu8;
INL vu8 vload(const uint8_t *p) { return vld1q_u8(p); }
INL vu8 vdup(uint8_t c) { return vdupq_n_u8(c); }
INL vu8 veq(vu8 a, vu8 b) { return vceqq_u8(a, b); }
INL vu8 vor(vu8 a, vu8 b) { return vorrq_u8(a, b); }
INL vu8 vand(vu8 a, vu8 b) { return vandq_u8(a, b); }
INL vu8 vsub(vu8 a, vu8 b) { return vsubq_u8(a, b); }
INL vu8 vle(vu8 a, vu8 b) { return vcleq_u8(a, b); } /* unsigned a <= b */
INL vu8 vnz(vu8 a) { return vtstq_u8(a, a); }        /* lanes != 0 */
INL vu8 vshr4(vu8 a) { return vshrq_n_u8(a, 4); }
/* t: a 16-entry table; i: indices 0..15 */
INL vu8 vtbl(vu8 t, vu8 i) { return vqtbl1q_u8(t, i); }
INL vu8 vtab(const uint8_t *t16) { return vld1q_u8(t16); }
INL uint64_t vmask(vu8 eq)
{
    return vget_lane_u64(vreinterpret_u64_u8(
        vshrn_n_u16(vreinterpretq_u16_u8(eq), 4)), 0);
}
#elif defined(__SSE2__)
#include <immintrin.h>
#if defined(__AVX2__)
#define VISA "avx2"
#define VW 32
#define VHAVE_TBL 1
typedef __m256i vu8;
INL vu8 vload(const uint8_t *p) { return _mm256_loadu_si256((const __m256i *)p); }
INL vu8 vdup(uint8_t c) { return _mm256_set1_epi8((char)c); }
INL vu8 veq(vu8 a, vu8 b) { return _mm256_cmpeq_epi8(a, b); }
INL vu8 vor(vu8 a, vu8 b) { return _mm256_or_si256(a, b); }
INL vu8 vand(vu8 a, vu8 b) { return _mm256_and_si256(a, b); }
INL vu8 vsub(vu8 a, vu8 b) { return _mm256_sub_epi8(a, b); }
INL vu8 vle(vu8 a, vu8 b) { return _mm256_cmpeq_epi8(_mm256_min_epu8(a, b), a); }
INL vu8 vnz(vu8 a)
{
    return _mm256_xor_si256(_mm256_cmpeq_epi8(a, _mm256_setzero_si256()),
                            _mm256_set1_epi8(-1));
}
INL vu8 vshr4(vu8 a) { return _mm256_and_si256(_mm256_srli_epi16(a, 4), _mm256_set1_epi8(0x0F)); }
INL vu8 vtbl(vu8 t, vu8 i) { return _mm256_shuffle_epi8(t, i); }
INL vu8 vtab(const uint8_t *t16)
{
    return _mm256_broadcastsi128_si256(_mm_loadu_si128((const __m128i *)t16));
}
INL uint64_t vmask(vu8 eq) { return (uint32_t)_mm256_movemask_epi8(eq); }
#else
#define VW 16
typedef __m128i vu8;
INL vu8 vload(const uint8_t *p) { return _mm_loadu_si128((const __m128i *)p); }
INL vu8 vdup(uint8_t c) { return _mm_set1_epi8((char)c); }
INL vu8 veq(vu8 a, vu8 b) { return _mm_cmpeq_epi8(a, b); }
INL vu8 vor(vu8 a, vu8 b) { return _mm_or_si128(a, b); }
INL vu8 vand(vu8 a, vu8 b) { return _mm_and_si128(a, b); }
INL vu8 vsub(vu8 a, vu8 b) { return _mm_sub_epi8(a, b); }
INL vu8 vle(vu8 a, vu8 b) { return _mm_cmpeq_epi8(_mm_min_epu8(a, b), a); }
INL vu8 vnz(vu8 a)
{
    return _mm_xor_si128(_mm_cmpeq_epi8(a, _mm_setzero_si128()), _mm_set1_epi8(-1));
}
INL vu8 vshr4(vu8 a) { return _mm_and_si128(_mm_srli_epi16(a, 4), _mm_set1_epi8(0x0F)); }
INL uint64_t vmask(vu8 eq) { return (uint32_t)_mm_movemask_epi8(eq); }
#if defined(__SSSE3__)
#define VISA "ssse3"
#define VHAVE_TBL 1
INL vu8 vtbl(vu8 t, vu8 i) { return _mm_shuffle_epi8(t, i); }
INL vu8 vtab(const uint8_t *t16) { return _mm_loadu_si128((const __m128i *)t16); }
#else
#define VISA "sse2"
#define VHAVE_TBL 0
#endif
#endif
#define VMASK_SHIFT 0
#else
#error "twins need NEON or SSE2 (both are the ISA baselines)"
#endif

INL size_t vfirst(uint64_t m) { return (size_t)__builtin_ctzll(m) >> VMASK_SHIFT; }

/* ---- timing (D144 addendum 1: every timed loop >= 50 ms, REPEATS runs) -- */

#define MIN_LOOP_NS 50e6
#define REPEATS 3

static double now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

/* --quick (smoke only, never archived) lowers the floor to 5 ms */
static double g_min_loop_ns = MIN_LOOP_NS;

/* a timed body: run it reps times, return total ns */
typedef double (*tbody)(const void *ctx, long reps);

/* calibrate to >= MIN_LOOP_NS, then REPEATS timed runs: min/max ns per rep */
static void tmeasure(tbody f, const void *ctx, double *lo, double *hi)
{
    long reps = 1;
    double t;
    while ((t = f(ctx, reps)) < g_min_loop_ns)
        reps = (long)(reps * (t > 1e5 ? 1.2 * g_min_loop_ns / t : 16.0)) + 1;
    *lo = 1e300, *hi = 0;
    for (int k = 0; k < REPEATS; k++) {
        double x = f(ctx, reps) / reps;
        if (x < *lo) *lo = x;
        if (x > *hi) *hi = x;
    }
}

/* ---- guard pages (requirements.md N-6) ---------------------------------- */

/* A span of n bytes flush against a PROT_NONE page at its END (gend) and one
 * starting right after a PROT_NONE page at its START (gstart). A read past
 * either end faults; the fault is caught and counted. Page guards catch only
 * reads that CROSS the page, so the ASan build (exact-size malloc) runs too. */
static sigjmp_buf g_jb;
static volatile sig_atomic_t g_faults;
static void g_onfault(int sig) { (void)sig; g_faults++; siglongjmp(g_jb, 1); }
static uint8_t *g_area;
static size_t g_page, g_cap;

__attribute__((unused)) static void guard_init(size_t cap)
{
    g_page = (size_t)sysconf(_SC_PAGESIZE);
    g_cap = (cap + g_page - 1) / g_page * g_page;
    /* [guard][cap bytes][guard] */
    g_area = mmap(NULL, g_cap + 2 * g_page, PROT_READ | PROT_WRITE,
                  MAP_PRIVATE | MAP_ANON, -1, 0);
    if (g_area == MAP_FAILED) { perror("mmap"); exit(2); }
    mprotect(g_area, g_page, PROT_NONE);
    mprotect(g_area + g_page + g_cap, g_page, PROT_NONE);
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = g_onfault;
    sigaction(SIGSEGV, &sa, NULL);
    sigaction(SIGBUS, &sa, NULL);
}
__attribute__((unused)) static uint8_t *gstart(size_t off) { return g_area + g_page + off; }      /* s[-1] faults */
__attribute__((unused)) static uint8_t *gend(size_t n) { return g_area + g_page + g_cap - n; }    /* s[n] faults */

/* deterministic generator for the fuzz passes */
static uint64_t rng_state = 0x9E3779B97F4A7C15ull;
__attribute__((unused)) static uint64_t rng(void)
{
    uint64_t x = rng_state;
    x ^= x >> 12, x ^= x << 25, x ^= x >> 27;
    rng_state = x;
    return x * 0x2545F4914F6CDD1Dull;
}

__attribute__((unused)) static uint8_t *slurp(const char *path, size_t *n)
{
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); exit(2); }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    uint8_t *b = malloc((size_t)len + 1);
    if (fread(b, 1, (size_t)len, f) != (size_t)len) { perror(path); exit(2); }
    fclose(f);
    *n = (size_t)len;
    return b;
}

/* ---- the find-first skeleton every set kernel shares --------------------
 * FIND_BODY(CLS, PRED): the first i in [0, n) whose byte is in the set, or
 * n. CLS(v) maps a loaded vector to its compare vector; PRED(c) is the
 * same membership test on one byte (the n < VW path). Shape: 4×VW blocks
 * tested through one OR (memchr's unroll), then VW blocks, then ONE
 * overlapped final block ending at n (its lanes before i already missed,
 * so its first hit is >= i). Every load stays inside s[0..n). Identical for
 * every classifier, so a row-to-row difference is the classifier's. */
#define FIND_BODY(CLS, PRED)                                                  \
    size_t i = 0;                                                             \
    if (n >= VW) {                                                            \
        for (; i + 4 * VW <= n; i += 4 * VW) {                                \
            vu8 c0 = CLS(vload(s + i)), c1 = CLS(vload(s + i + VW));          \
            vu8 c2 = CLS(vload(s + i + 2 * VW)), c3 = CLS(vload(s + i + 3 * VW)); \
            if (vmask(vor(vor(c0, c1), vor(c2, c3)))) {                       \
                uint64_t m;                                                   \
                if ((m = vmask(c0))) return i + vfirst(m);                    \
                if ((m = vmask(c1))) return i + VW + vfirst(m);               \
                if ((m = vmask(c2))) return i + 2 * VW + vfirst(m);           \
                return i + 3 * VW + vfirst(vmask(c3));                        \
            }                                                                 \
        }                                                                     \
        for (; i + VW <= n; i += VW) {                                        \
            uint64_t m = vmask(CLS(vload(s + i)));                            \
            if (m) return i + vfirst(m);                                      \
        }                                                                     \
        if (i < n) {                                                          \
            uint64_t m = vmask(CLS(vload(s + n - VW)));                       \
            if (m) return n - VW + vfirst(m);                                 \
        }                                                                     \
        return n;                                                             \
    }                                                                         \
    for (; i < n; i++)                                                        \
        if (PRED(s[i])) return i;                                             \
    return n;

/* lanes of a vmask() result: VMASK_ONE keeps one bit per lane (NEON's shrn
 * mask has four), so m &= m - 1 steps one lane; lane_from(k) is the mask of
 * lanes >= k (k < VW) */
#if VMASK_SHIFT
#define VMASK_ONE 0x8888888888888888ull
#else
#define VMASK_ONE (~0ull)
#endif
INL uint64_t lane_from(size_t k) { return ~0ull << (k << VMASK_SHIFT); }

/* ITER_BODY(CLS, PRED): every i in [0, n) whose byte is in the set, written
 * to pos[] in order (at most cap; returns the count), the block mask kept
 * across hits instead of a find-first restart per hit. VW blocks, then the
 * overlapped final block with its already-done lanes masked off. */
#define ITER_BODY(CLS, PRED)                                                  \
    long cnt = 0;                                                             \
    size_t i = 0;                                                             \
    if (n >= VW) {                                                            \
        for (; i + VW <= n; i += VW) {                                        \
            uint64_t m = vmask(CLS(vload(s + i))) & VMASK_ONE;                \
            for (; m && cnt < cap; m &= m - 1) pos[cnt++] = i + vfirst(m);    \
        }                                                                     \
        if (i < n) {                                                          \
            uint64_t m = vmask(CLS(vload(s + n - VW))) & VMASK_ONE & lane_from(i - (n - VW)); \
            for (; m && cnt < cap; m &= m - 1) pos[cnt++] = n - VW + vfirst(m); \
        }                                                                     \
        return cnt;                                                           \
    }                                                                         \
    for (; i < n; i++)                                                        \
        if (PRED(s[i]) && cnt < cap) pos[cnt++] = i;                          \
    return cnt;

#endif
