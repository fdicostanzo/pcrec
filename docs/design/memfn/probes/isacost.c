/* memfn R1b probe: what does ISA SELECTION cost per call, by mechanism.
 *
 * Question (isa_selection.md §1): a search kernel can pick its ISA tier at
 * compile time (free), once (a pointer, an ifunc, a multiversioned
 * function) or on every call (a cached flag, __builtin_cpu_supports, a raw
 * CPU query). What does each cost per call, against a direct call and an
 * inline body, so the decision table rests on numbers.
 *
 * Kernels: "find the first byte == c in s[0..n)", NULL if absent, never
 * reading outside s[0..n) (requirements.md S-2):
 *
 *   base   the BASELINE tier, no -m flag needed: x86-64 SSE2, AArch64 NEON
 *          (callcost.c's vec_sm: loop-free below 16, overlapped final block)
 *   wide   the WIDER tier: x86-64 AVX2 in a target("avx2") function (so it
 *          compiles in a baseline TU and cannot inline into baseline code);
 *          AArch64 has no wider tier on the probe box (Apple: no SVE), so
 *          `wide` is a 64-byte-unrolled NEON stand-in with the same
 *          dispatch shape. The DISPATCH cost is what is measured; on
 *          AArch64 the kernel speed difference is not the point.
 *
 * Variants (rows), each "find" at span n, MISS case, independent calls:
 *
 *   loop        the harness alone
 *   base_inl    base, inline (B2, no selection: the compile-time baseline)
 *   base_ool    base behind noinline (B1b, direct call)
 *   wide_ool    wide behind noinline (direct call; what a dispatch reaches)
 *   wide_inl    wide inlined into a timed loop compiled for the wide ISA:
 *               the DECLARED-ISA artifact (target attribute on the caller,
 *               or a TU built with -mavx2). x86: skipped if the CPU lacks AVX2
 *   flag_hyb    a cached `static int` read + branch: inline base, or call
 *               wide_ool (the hybrid: a mutable static, LIBRARY-legal only)
 *   flag_ool    the same flag choosing between base_ool and wide_ool
 *   fnptr       an indirect call through a static pointer set once at init
 *   fnptr_lazy  a pointer that starts at a resolver and is rewritten on the
 *               first call (dispatch-once without a constructor)
 *   cpusup_hyb  __builtin_cpu_supports per call + branch (reads libgcc's /
 *               compiler-rt's __cpu_model or __aarch64_cpu_features; no
 *               static of ours). n/a where the builtin does not exist
 *   query_hyb   a raw CPU/OS query per call + branch, NO cache anywhere:
 *               x86 cpuid+xgetbv; Linux getauxval(AT_HWCAP); macOS
 *               sysctlbyname. The "check on every call, hold no state" form
 *   ifunc       a GNU ifunc (ELF only; resolver picks base_ool/wide_ool)
 *   fmv         compiler function multiversioning: target_clones (x86 ELF)
 *               or target_version (AArch64 clang), lowered by the toolchain
 *               (ifunc on ELF; on Mach-O a dyld __func_variants table with
 *               Apple clang, a lazily written pointer with LLVM clang)
 *
 * Plus detection rows (ns per detection, no search): det_query (the raw
 * query above), det_cpusup (__builtin_cpu_supports).
 *
 * --sel=auto|base|wide forces what the flag/pointer variants select (auto =
 * the detected answer), so both arms are timed on a box that has the wide
 * tier. The per-call-test variants (cpusup_hyb, query_hyb, ifunc, fmv) take
 * the real answer, printed in the header.
 *
 * --isa-report prints the compiled-for ISA level (from predefined macros:
 * the RX_ISA stamp design, isa_selection.md §1.2) against the running CPU's
 * level (from cpuid/xgetbv: the rx_check_cpu() design), and the verdict a
 * declared-ISA artifact's check would return. The check runs in code
 * compiled for the BASELINE (a target attribute on x86), the property a
 * real check needs: compiled with the TU's -march it could itself SIGILL.
 *
 * Timing (D144 addendum 1): every timed loop calibrated to >= 50 ms, run
 * REPEATS times, min..max printed. Mac numbers are directional only.
 *
 * Correctness: --check runs every runnable variant under --sel=base and
 * --sel=wide against a scalar reference over n 0..300, every hit position
 * (and none), alignments 0..31, the span ending at its allocation's end
 * (build with -fsanitize=address: probes.mk check-asan-isa).
 *
 * Every mutable static below is the probe standing in for a LIBRARY. None
 * of them is legal in an emitted artifact (match_api.md §5.3, TS-1).
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if defined(__x86_64__)
#include <immintrin.h>
#define ARCH "x86-64"
#define BASE_NAME "sse2"
#define WIDE_NAME "avx2"
#define WIDE_ATTR __attribute__((target("avx2")))
#elif defined(__aarch64__)
#include <arm_neon.h>
#define ARCH "aarch64"
#define BASE_NAME "neon"
#define WIDE_NAME "neon64"
#define WIDE_ATTR
#if defined(__APPLE__)
#include <sys/sysctl.h>
#elif defined(__linux__)
#include <sys/auxv.h>
#endif
#else
#error "probe needs x86-64 or AArch64"
#endif

#define INL static inline __attribute__((always_inline))
#define OOL __attribute__((noinline))

/* Which per-call mechanisms this toolchain/target has. */
#if defined(__x86_64__) || (defined(__aarch64__) && defined(__clang__))
#define HAVE_CPUSUP 1 /* gcc on darwin/aarch64 has no __builtin_cpu_supports */
#else
#define HAVE_CPUSUP 0
#endif
#if defined(__ELF__) && defined(__x86_64__)
#define HAVE_IFUNC 1
#define HAVE_FMV 1 /* target_clones */
#elif defined(__aarch64__) && defined(__clang__)
#define HAVE_IFUNC 0
#define HAVE_FMV 1 /* target_version */
#else
#define HAVE_IFUNC 0
#define HAVE_FMV 0
#endif

typedef const uint8_t *(*kfn)(const uint8_t *, uint8_t, size_t);

/* ---- shared scalar pieces --------------------------------------------- */

INL uint64_t zbytes64(uint64_t w) /* bit 7 of byte k set iff byte k is 0 */
{
    const uint64_t highs = 0x8080808080808080ull;
    return ~(((w & ~highs) + ~highs) | w) & highs;
}

/* loop-free short path, n < 16: callcost.c's vec_sm short arm */
INL const uint8_t *k_short(const uint8_t *s, uint8_t c, size_t n)
{
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

/* ---- the baseline kernel (16-byte) ------------------------------------ */

#if defined(__x86_64__)
#define VSHIFT 0
INL uint64_t veq16(const uint8_t *p, uint8_t c)
{
    __m128i v = _mm_loadu_si128((const __m128i *)p);
    return (uint32_t)_mm_movemask_epi8(_mm_cmpeq_epi8(v, _mm_set1_epi8((char)c)));
}
#else
#define VSHIFT 2 /* nibble mask: ctz >> 2 = lane */
INL uint64_t vmask(uint8x16_t eq)
{
    return vget_lane_u64(vreinterpret_u64_u8(
        vshrn_n_u16(vreinterpretq_u16_u8(eq), 4)), 0);
}
INL uint64_t veq16(const uint8_t *p, uint8_t c)
{
    return vmask(vceqq_u8(vld1q_u8(p), vdupq_n_u8(c)));
}
#endif

INL const uint8_t *k_base(const uint8_t *s, uint8_t c, size_t n)
{
    if (n < 16)
        return k_short(s, c, n);
    size_t i = 0;
    for (; i + 16 <= n; i += 16) {
        uint64_t m = veq16(s + i, c);
        if (m) return s + i + (__builtin_ctzll(m) >> VSHIFT);
    }
    if (i < n) {
        uint64_t m = veq16(s + n - 16, c);
        if (m) return s + n - 16 + (__builtin_ctzll(m) >> VSHIFT);
    }
    return NULL;
}

/* ---- the wide kernel --------------------------------------------------- */

#if defined(__x86_64__)
/* AVX2, 32-byte blocks, overlapped final block; below 32 the baseline
 * path (SSE2 is a subset, so it inlines into this target("avx2") body). */
WIDE_ATTR INL uint64_t veq32(const uint8_t *p, uint8_t c)
{
    __m256i v = _mm256_loadu_si256((const __m256i *)p);
    return (uint32_t)_mm256_movemask_epi8(_mm256_cmpeq_epi8(v, _mm256_set1_epi8((char)c)));
}
WIDE_ATTR INL const uint8_t *k_wide(const uint8_t *s, uint8_t c, size_t n)
{
    if (n < 32)
        return k_base(s, c, n);
    size_t i = 0;
    for (; i + 32 <= n; i += 32) {
        uint64_t m = veq32(s + i, c);
        if (m) return s + i + __builtin_ctzll(m);
    }
    if (i < n) {
        uint64_t m = veq32(s + n - 32, c);
        if (m) return s + n - 32 + __builtin_ctzll(m);
    }
    return NULL;
}
#else
/* NEON, 64 bytes per iteration (four compares OR-reduced, then located),
 * overlapped final 16-byte blocks; below 64 the baseline path. */
INL const uint8_t *k_wide(const uint8_t *s, uint8_t c, size_t n)
{
    if (n < 64)
        return k_base(s, c, n);
    const uint8x16_t vc = vdupq_n_u8(c);
    size_t i = 0;
    for (; i + 64 <= n; i += 64) {
        uint8x16_t e0 = vceqq_u8(vld1q_u8(s + i), vc);
        uint8x16_t e1 = vceqq_u8(vld1q_u8(s + i + 16), vc);
        uint8x16_t e2 = vceqq_u8(vld1q_u8(s + i + 32), vc);
        uint8x16_t e3 = vceqq_u8(vld1q_u8(s + i + 48), vc);
        uint8x16_t any = vorrq_u8(vorrq_u8(e0, e1), vorrq_u8(e2, e3));
        if (vmaxvq_u8(any)) {
            uint64_t m;
            if ((m = vmask(e0))) return s + i + (__builtin_ctzll(m) >> 2);
            if ((m = vmask(e1))) return s + i + 16 + (__builtin_ctzll(m) >> 2);
            if ((m = vmask(e2))) return s + i + 32 + (__builtin_ctzll(m) >> 2);
            m = vmask(e3);
            return s + i + 48 + (__builtin_ctzll(m) >> 2);
        }
    }
    for (; i + 16 <= n; i += 16) {
        uint64_t m = veq16(s + i, c);
        if (m) return s + i + (__builtin_ctzll(m) >> 2);
    }
    if (i < n) {
        uint64_t m = veq16(s + n - 16, c);
        if (m) return s + n - 16 + (__builtin_ctzll(m) >> 2);
    }
    return NULL;
}
#endif

OOL const uint8_t *k_base_ool(const uint8_t *s, uint8_t c, size_t n) { return k_base(s, c, n); }
WIDE_ATTR OOL const uint8_t *k_wide_ool(const uint8_t *s, uint8_t c, size_t n) { return k_wide(s, c, n); }

/* ---- CPU detection: pure, static-free ---------------------------------- */

#if defined(__x86_64__)
/* All detection runs at the BASELINE whatever the TU's -march: a check that
 * could itself execute a VEX/EVEX instruction defeats its purpose. */
#define DET_ATTR __attribute__((target("arch=x86-64"), noinline))
/* macros, not inline functions: an inline callee compiled for the TU's
 * -march would not inline into the baseline-target caller */
#define cpuid2(leaf, sub, r)                                                  \
    __asm__ volatile("cpuid" : "=a"((r)[0]), "=b"((r)[1]), "=c"((r)[2]),      \
                     "=d"((r)[3]) : "a"(leaf), "c"(sub))
#define xgetbv0(x)                                                            \
    do {                                                                      \
        unsigned lo_, hi_;                                                    \
        __asm__ volatile("xgetbv" : "=a"(lo_), "=d"(hi_) : "c"(0));           \
        (x) = ((uint64_t)hi_ << 32) | lo_;                                    \
    } while (0)
/* The x86-64 psABI microarchitecture level the CPU (and OS) support, 1..4. */
DET_ATTR static int cpu_level(void)
{
    unsigned r1[4], r7[4], rx[4];
    cpuid2(0, 0, r1);
    unsigned maxleaf = r1[0];
    cpuid2(1, 0, r1);
    cpuid2(0x80000001u, 0, rx);
    if (maxleaf >= 7) cpuid2(7, 0, r7); else r7[0] = r7[1] = r7[2] = r7[3] = 0;
    unsigned c1 = r1[2], d1 = r1[3], b7 = r7[1], cx = rx[2];
    (void)d1;
    int v2 = (c1 & (1u << 0)) && (c1 & (1u << 9)) && (c1 & (1u << 13)) &&
             (c1 & (1u << 19)) && (c1 & (1u << 20)) && (c1 & (1u << 23)) &&
             (cx & (1u << 0)); /* sse3 ssse3 cx16 sse4.1 sse4.2 popcnt lahf */
    if (!v2) return 1;
    int osx = (c1 & (1u << 27)) != 0;
    uint64_t xcr0 = 0;
    if (osx) xgetbv0(xcr0);
    int ymm = osx && (xcr0 & 6) == 6;
    int v3 = ymm && (c1 & (1u << 28)) && (c1 & (1u << 12)) && (c1 & (1u << 29)) &&
             (c1 & (1u << 22)) && (b7 & (1u << 5)) && (b7 & (1u << 3)) &&
             (b7 & (1u << 8)) && (cx & (1u << 5));
             /* avx fma f16c movbe avx2 bmi1 bmi2 lzcnt, + OS ymm state */
    if (!v3) return 2;
    int zmm = (xcr0 & 0xe6) == 0xe6;
    int v4 = zmm && (b7 & (1u << 16)) && (b7 & (1u << 17)) && (b7 & (1u << 28)) &&
             (b7 & (1u << 30)) && (b7 & (1u << 31)); /* f dq cd bw vl */
    return v4 ? 4 : 3;
}
DET_ATTR static int query_wide(void) { return cpu_level() >= 3; }
#elif defined(__aarch64__)
#define DET_ATTR __attribute__((noinline))
/* No wider tier exists on the probe box; the query is a realistic one
 * (FEAT_DotProd) so the per-call cost is a real OS round trip. */
DET_ATTR static int query_wide(void)
{
#if defined(__APPLE__)
    int v = 0;
    size_t len = sizeof v;
    if (sysctlbyname("hw.optional.arm.FEAT_DotProd", &v, &len, NULL, 0) != 0)
        return 0;
    return v != 0;
#elif defined(__linux__)
    return (getauxval(AT_HWCAP) & (1ul << 20)) != 0; /* HWCAP_ASIMDDP */
#else
    return 0;
#endif
}
static int cpu_level(void) { return 1; } /* armv8-a: NEON is the baseline */
#endif

#if HAVE_CPUSUP
#if defined(__x86_64__)
#define CPUSUP() __builtin_cpu_supports("avx2")
#else
#define CPUSUP() __builtin_cpu_supports("dotprod")
#endif
#else
#define CPUSUP() 0
#endif

/* ---- the compiled-for level: the RX_ISA stamp design ------------------- */

#if defined(__x86_64__)
#if defined(__AVX512F__) && defined(__AVX512BW__) && defined(__AVX512CD__) && \
    defined(__AVX512DQ__) && defined(__AVX512VL__) && defined(__AVX2__) &&   \
    defined(__BMI2__) && defined(__FMA__) && defined(__MOVBE__)
#define ISA_COMPILED 4
#elif defined(__AVX2__) && defined(__BMI2__) && defined(__FMA__) && \
    defined(__MOVBE__) && defined(__F16C__) && defined(__LZCNT__)
#define ISA_COMPILED 3
#elif defined(__SSE4_2__) && defined(__POPCNT__) && defined(__SSSE3__)
#define ISA_COMPILED 2
#else
#define ISA_COMPILED 1
#endif
#define ISA_FAMILY "x86-64-v"
#else
#if defined(__ARM_FEATURE_SVE2)
#define ISA_COMPILED 3
#elif defined(__ARM_FEATURE_SVE)
#define ISA_COMPILED 2
#else
#define ISA_COMPILED 1 /* armv8-a + NEON */
#endif
#define ISA_FAMILY "aarch64-tier"
#endif

/* ---- dispatch state (LIBRARY stand-ins; artifact-illegal) -------------- */

static int g_wide;  /* the cached flag */
static kfn g_fp;    /* dispatch-once pointer, set at init */
static const uint8_t *lazy_resolve(const uint8_t *, uint8_t, size_t);
static kfn g_fp_lazy = lazy_resolve;
static int g_sel_forced = -1; /* --sel: -1 auto, 0 base, 1 wide */

static int sel_answer(void) { return g_sel_forced >= 0 ? g_sel_forced : query_wide(); }

static const uint8_t *lazy_resolve(const uint8_t *s, uint8_t c, size_t n)
{
    g_fp_lazy = sel_answer() ? k_wide_ool : k_base_ool;
    return g_fp_lazy(s, c, n);
}

#if HAVE_IFUNC
static kfn resolve_find(void)
{
    __builtin_cpu_init(); /* required before cpu_supports in a resolver */
    return __builtin_cpu_supports("avx2") ? k_wide_ool : k_base_ool;
}
const uint8_t *k_ifunc(const uint8_t *, uint8_t, size_t) __attribute__((ifunc("resolve_find")));
#endif

#if HAVE_FMV
#if defined(__x86_64__)
/* GNU vector extension, 32 bytes: the default clone lowers it to two SSE2
 * halves, the avx2 clone to one ymm compare. The macros (__AVX2__) do NOT
 * change per clone: the clone body cannot select intrinsics by #if. */
typedef uint8_t v32u8 __attribute__((vector_size(32)));
__attribute__((target_clones("avx2", "default")))
const uint8_t *k_fmv(const uint8_t *s, uint8_t c, size_t n)
{
    if (n < 16)
        return k_short(s, c, n);
    if (n < 32) {
        uint64_t a, b;
        for (size_t i = 0; i < n; i += 8) { /* two to four words */
            size_t at = i + 8 <= n ? i : n - 8;
            memcpy(&a, s + at, 8);
            b = zbytes64(a ^ (0x0101010101010101ull * c));
            if (b) return s + at + (__builtin_ctzll(b) >> 3);
        }
        return NULL;
    }
    v32u8 vc;
    memset(&vc, c, sizeof vc);
    for (size_t i = 0;; i += 32) {
        size_t at = i + 32 <= n ? i : n - 32;
        v32u8 v;
        memcpy(&v, s + at, 32);
        v32u8 eq = (v32u8)(v == vc);
        uint64_t w[4];
        memcpy(w, &eq, 32);
        for (int k = 0; k < 4; k++)
            if (w[k]) return s + at + 8 * k + (__builtin_ctzll(w[k]) >> 3);
        if (at + 32 >= n) return NULL;
    }
}
#else
__attribute__((target_version("dotprod")))
const uint8_t *k_fmv(const uint8_t *s, uint8_t c, size_t n) { return k_wide(s, c, n); }
__attribute__((target_version("default")))
const uint8_t *k_fmv(const uint8_t *s, uint8_t c, size_t n) { return k_base(s, c, n); }
#endif
#endif

/* ---- the variant table ------------------------------------------------- */

enum { V_LOOP, V_BASE_INL, V_BASE_OOL, V_WIDE_OOL, V_WIDE_INL, V_FLAG_HYB,
       V_FLAG_OOL, V_FNPTR, V_FNPTR_LAZY, V_CPUSUP_HYB, V_QUERY_HYB, V_IFUNC,
       V_FMV, V_DET_QUERY, V_DET_CPUSUP, NV };
static const char *const vname[NV] = {
    "loop", "base_inl", "base_ool", "wide_ool", "wide_inl", "flag_hyb",
    "flag_ool", "fnptr", "fnptr_lazy", "cpusup_hyb", "query_hyb", "ifunc",
    "fmv", "det_query", "det_cpusup",
};
static int cpu_has_wide; /* may the wide kernel run here at all */

static int runnable(int v)
{
    switch (v) {
    case V_WIDE_OOL: case V_WIDE_INL: return cpu_has_wide;
    case V_CPUSUP_HYB: case V_DET_CPUSUP: return HAVE_CPUSUP;
    case V_IFUNC: return HAVE_IFUNC;
    case V_FMV: return HAVE_FMV;
    default: return 1;
    }
}

/* One call of variant v (never V_WIDE_INL: its loop is its own function,
 * compiled for the wide target, below). */
INL const uint8_t *call(int v, const uint8_t *s, size_t n)
{
    switch (v) {
    case V_LOOP:       return s;
    case V_BASE_INL:   return k_base(s, 'Z', n);
    case V_BASE_OOL:   return k_base_ool(s, 'Z', n);
    case V_WIDE_OOL:   return k_wide_ool(s, 'Z', n);
    case V_FLAG_HYB:   return g_wide ? k_wide_ool(s, 'Z', n) : k_base(s, 'Z', n);
    case V_FLAG_OOL:   return g_wide ? k_wide_ool(s, 'Z', n) : k_base_ool(s, 'Z', n);
    case V_FNPTR:      return g_fp(s, 'Z', n);
    case V_FNPTR_LAZY: return g_fp_lazy(s, 'Z', n);
    case V_CPUSUP_HYB: return CPUSUP() ? k_wide_ool(s, 'Z', n) : k_base(s, 'Z', n);
    case V_QUERY_HYB:  return query_wide() ? k_wide_ool(s, 'Z', n) : k_base(s, 'Z', n);
#if HAVE_IFUNC
    case V_IFUNC:      return k_ifunc(s, 'Z', n);
#endif
#if HAVE_FMV
    case V_FMV:        return k_fmv(s, 'Z', n);
#endif
    case V_DET_QUERY:  return query_wide() ? s : s + 1;
    case V_DET_CPUSUP: return CPUSUP() ? s : s + 1;
    default:           return s;
    }
}

/* ---- timing ------------------------------------------------------------ */

static double now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

#define TIMED_BODY(CALL)                                                      \
    {                                                                         \
        double t0 = now_ns();                                                 \
        for (long r = 0; r < reps; r++) {                                     \
            const uint8_t *q = buf;                                           \
            __asm__ volatile("" : "+r"(q));                                   \
            const uint8_t *p = CALL;                                          \
            __asm__ volatile("" : : "r"(p));                                  \
        }                                                                     \
        return now_ns() - t0;                                                 \
    }
#define TIMER(V)                                                              \
    OOL static double run_##V(const uint8_t *buf, size_t n, long reps)        \
        TIMED_BODY(call(V, q, n))
TIMER(0) TIMER(1) TIMER(2) TIMER(3) TIMER(5) TIMER(6) TIMER(7)
TIMER(8) TIMER(9) TIMER(10) TIMER(11) TIMER(12) TIMER(13) TIMER(14)
/* the declared-ISA form: the caller is compiled for the wide target too */
WIDE_ATTR OOL static double run_4(const uint8_t *buf, size_t n, long reps)
    TIMED_BODY(k_wide(q, 'Z', n))

typedef double (*runner)(const uint8_t *, size_t, long);
static const runner runners[NV] = { run_0, run_1, run_2, run_3, run_4, run_5,
                                    run_6, run_7, run_8, run_9, run_10, run_11,
                                    run_12, run_13, run_14 };

#define MIN_LOOP_NS 50e6
#define REPEATS 3

static void measure(int v, const uint8_t *buf, size_t n, double *lo, double *hi)
{
    long reps = 256;
    double t;
    while ((t = runners[v](buf, n, reps)) < MIN_LOOP_NS)
        reps = (long)(reps * (t > 1e5 ? 1.2 * MIN_LOOP_NS / t : 16.0));
    *lo = 1e300, *hi = 0;
    for (int k = 0; k < REPEATS; k++) {
        double x = runners[v](buf, n, reps) / reps;
        if (x < *lo) *lo = x;
        if (x > *hi) *hi = x;
    }
}

/* ---- setup, correctness, report ---------------------------------------- */

static void select_arms(int forced)
{
    g_sel_forced = forced;
    g_wide = sel_answer() && cpu_has_wide;
    g_fp = g_wide ? k_wide_ool : k_base_ool;
    g_fp_lazy = lazy_resolve;
}

WIDE_ATTR OOL static const uint8_t *wide_inl_once(const uint8_t *s, size_t n)
{
    return k_wide(s, 'Z', n);
}

static long check_pass(long *cases)
{
    long bad = 0;
    for (size_t n = 0; n <= 300; n++)
        for (size_t al = 0; al < 32; al++) {
            uint8_t *blk = malloc(al + n + 1);
            uint8_t *s = blk + al;
            for (size_t h = 0; h <= n; h++) { /* h == n: absent */
                for (size_t i = 0; i < n; i++)
                    s[i] = (uint8_t)('a' + (i * 7 + al) % 20); /* never Z */
                if (h < n) s[h] = 'Z';
                const uint8_t *want = h < n ? s + h : NULL;
                for (int v = V_BASE_INL; v <= V_FMV; v++) {
                    if (!runnable(v)) continue;
                    const uint8_t *got = v == V_WIDE_INL ? wide_inl_once(s, n) : call(v, s, n);
                    ++*cases;
                    if (got != want && bad++ < 10)
                        printf("BAD %s n=%zu al=%zu h=%zu\n", vname[v], n, al, h);
                }
            }
            free(blk);
        }
    return bad;
}

static int check(void)
{
    long cases = 0, bad = 0;
    for (int sel = 0; sel <= 1; sel++) {
        select_arms(sel);
        bad += check_pass(&cases);
    }
    printf("check: %ld cases, %ld bad (sel=base and sel=wide)\n", cases, bad);
    return bad != 0;
}

/* What a declared-ISA artifact's rx_check_cpu() would answer: compiled-for
 * level from the preprocessor (the stamp), running level from the CPU. */
static int isa_report(void)
{
    int need = ISA_COMPILED, have = cpu_level();
    printf("compiled-for: %s%d (from predefined macros)\n", ISA_FAMILY, need);
    printf("running CPU : %s%d (from cpuid/xgetbv%s)\n", ISA_FAMILY, have,
#if defined(__x86_64__)
           ""
#else
           "; aarch64: NEON baseline only, SVE not probed by this build"
#endif
    );
    printf("cpusup(wide)=%d query(wide)=%d\n", CPUSUP(), query_wide());
    if (have >= need) {
        printf("verdict     : OK\n");
        return 0;
    }
    printf("verdict     : REFUSE (PCREC_ERR_ISA: artifact needs %s%d, CPU has %s%d)\n",
           ISA_FAMILY, need, ISA_FAMILY, have);
    return 3;
}

int main(int argc, char **argv)
{
    int forced = -1, do_check = 0;
#if defined(__x86_64__)
    cpu_has_wide = cpu_level() >= 3;
#else
    cpu_has_wide = 1;
#endif
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--check")) do_check = 1;
        else if (!strcmp(argv[i], "--isa-report")) return isa_report();
        else if (!strcmp(argv[i], "--sel=base")) forced = 0;
        else if (!strcmp(argv[i], "--sel=wide")) forced = 1;
        else if (!strcmp(argv[i], "--sel=auto")) forced = -1;
        else { fprintf(stderr, "usage: %s [--check|--isa-report|--sel=auto|base|wide]\n", argv[0]); return 2; }
    }
    if (do_check)
        return check();
    select_arms(forced);
    static const size_t ns[] = { 1, 8, 16, 32, 64, 256, 1024, 4096 };
    const size_t NN = sizeof ns / sizeof ns[0];
    uint8_t *buf = aligned_alloc(64, 8192);
    for (int i = 0; i < 8192; i++)
        buf[i] = (uint8_t)('a' + i % 20);
    printf("# memfn isacost probe, arch=%s base=%s wide=%s, ns/call min..max of %d loops >= %.0f ms\n",
           ARCH, BASE_NAME, WIDE_NAME, REPEATS, MIN_LOOP_NS / 1e6);
    printf("# compiled-for %s%d; cpu level %s%d; cpu_has_wide=%d\n", ISA_FAMILY, ISA_COMPILED,
           ISA_FAMILY, cpu_level(), cpu_has_wide);
    printf("# --sel=%s: flag/fnptr arms select %s; cpusup()=%d query()=%d (per-call variants follow these)\n",
           forced < 0 ? "auto" : forced ? "wide" : "base", g_wide ? "wide" : "base", CPUSUP(), query_wide());
    printf("# have: cpusup=%d ifunc=%d fmv=%d\n", HAVE_CPUSUP, HAVE_IFUNC, HAVE_FMV);
    printf("\n## mode=ind case=miss (whole span read)\n%-12s", "n");
    for (size_t j = 0; j < NN; j++) printf(" %13zu", ns[j]);
    printf("\n");
    for (int v = 0; v <= V_FMV; v++) {
        printf("%-12s", vname[v]);
        for (size_t j = 0; j < NN; j++) {
            if (!runnable(v)) { printf(" %13s", "n/a"); continue; }
            double lo, hi;
            measure(v, buf, ns[j], &lo, &hi);
            printf(" %6.2f..%-6.2f", lo, hi);
            fflush(stdout);
        }
        printf("\n");
    }
    printf("\n## detection only (ns per detection, no search)\n");
    for (int v = V_DET_QUERY; v < NV; v++) {
        if (!runnable(v)) { printf("%-12s n/a\n", vname[v]); continue; }
        double lo, hi;
        measure(v, buf, 1, &lo, &hi);
        printf("%-12s %6.2f..%-6.2f\n", vname[v], lo, hi);
    }
    return 0;
}
