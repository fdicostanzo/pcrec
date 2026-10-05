/* memfnsurvey timing: third-party kernels against libc, the R1 probe's
 * method (requirements.md §2.4: miss case, independent calls, each timed
 * loop calibrated >= 50 ms, min..max of 3). Mac numbers directional only. */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define SZ_DYNAMIC_DISPATCH 0
#include "stringzilla/find.h"

#define OOL __attribute__((noinline))
void *musl_memchr(const void *, int, size_t);
void *musl_memmem(const void *, size_t, const void *, size_t);
void *__memchr_aarch64(const void *, int, size_t);
void *__memchr_aarch64_mte(const void *, int, size_t);

static sz_byteset_t set_dig, set_ws, set_hi, set_lower;
static uint64_t tab_dig[4], tab_lower[4];
static inline int tin(const uint64_t *t, uint8_t c) { return (t[c >> 6] >> (c & 63)) & 1; }
static inline const uint8_t *tab_find(const uint8_t *s, size_t n, const uint64_t *t) {
    for (size_t i = 0; i < n; i++) if (tin(t, s[i])) return s + i;
    return 0;
}
static inline const uint8_t *tab_skip(const uint8_t *s, size_t n, const uint64_t *t) {
    for (size_t i = 0; i < n; i++) if (!tin(t, s[i])) return s + i;
    return 0;
}

#define NV 15
static const char *const vname[NV] = {
    "loop", "libc memchr", "arm-or memchr", "arm-or mte", "musl memchr", "sz byte serial", "sz byte neon",
    "table find[0-9]", "sz set neon[0-9]", "sz set neon[\\s]", "sz set neon[hi]", "table skip[a-z]",
    "sz notfrom[a-z]", "libc memmem Zqx", "sz find neon Zqx",
};
static const char Z = 'Z';
static inline __attribute__((always_inline)) const void *call(int v, const uint8_t *s, size_t n) {
    switch (v) {
    case 0: return s;
    case 1: return memchr(s, 'Z', n);
    case 2: return __memchr_aarch64(s, 'Z', n);
    case 3: return __memchr_aarch64_mte(s, 'Z', n);
    case 4: return musl_memchr(s, 'Z', n);
    case 5: return sz_find_byte_serial((sz_cptr_t)s, n, &Z);
    case 6: return sz_find_byte_neon((sz_cptr_t)s, n, &Z);
    case 7: return tab_find(s, n, tab_dig);
    case 8: return sz_find_byteset_neon((sz_cptr_t)s, n, &set_dig);
    case 9: return sz_find_byteset_neon((sz_cptr_t)s, n, &set_ws);
    case 10: return sz_find_byteset_neon((sz_cptr_t)s, n, &set_hi);
    case 11: return tab_skip(s, n, tab_lower);
    case 12: { sz_byteset_t b = set_lower; sz_byteset_invert(&b); return sz_find_byteset_neon((sz_cptr_t)s, n, &b); }
    case 13: return memmem(s, n, "Zqx", 3);
    default: return sz_find_neon((sz_cptr_t)s, n, "Zqx", 3);
    }
}
static double now_ns(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e9 + t.tv_nsec; }
#define TIMER(V)                                                                   \
    OOL static double run_##V(const uint8_t *buf, size_t n, long reps) {           \
        double t0 = now_ns();                                                      \
        for (long r = 0; r < reps; r++) {                                          \
            const uint8_t *q = buf;                                                \
            __asm__ volatile("" : "+r"(q));                                        \
            const void *p = call(V, q, n);                                         \
            __asm__ volatile("" : : "r"(p));                                       \
        }                                                                          \
        return now_ns() - t0;                                                      \
    }
TIMER(0) TIMER(1) TIMER(2) TIMER(3) TIMER(4) TIMER(5) TIMER(6) TIMER(7) TIMER(8) TIMER(9) TIMER(10) TIMER(11)
TIMER(12) TIMER(13) TIMER(14)
typedef double (*runner)(const uint8_t *, size_t, long);
static const runner runners[NV] = {run_0, run_1, run_2, run_3, run_4, run_5, run_6, run_7,
                                   run_8, run_9, run_10, run_11, run_12, run_13, run_14};
int main(void) {
    static const size_t ns[] = {1, 8, 12, 16, 32, 64, 256, 1024, 4096, 65536};
    const size_t NN = sizeof ns / sizeof ns[0];
    uint8_t *buf = aligned_alloc(64, 65536 + 64);
    for (int i = 0; i < 65536 + 64; i++) buf[i] = (uint8_t)('a' + i % 20); /* lowercase a..t: no Z, no digit */
    sz_byteset_init(&set_dig); sz_byteset_init(&set_ws); sz_byteset_init(&set_hi); sz_byteset_init(&set_lower);
    for (int c = '0'; c <= '9'; c++) { sz_byteset_add_u8(&set_dig, (uint8_t)c); tab_dig[c >> 6] |= 1ull << (c & 63); }
    for (int c = 'a'; c <= 'z'; c++) { sz_byteset_add_u8(&set_lower, (uint8_t)c); tab_lower[c >> 6] |= 1ull << (c & 63); }
    sz_byteset_add_u8(&set_ws, ' '); sz_byteset_add_u8(&set_ws, '\t'); sz_byteset_add_u8(&set_ws, '\n'); sz_byteset_add_u8(&set_ws, '\r');
    for (int c = 0x80; c < 256; c++) sz_byteset_add_u8(&set_hi, (uint8_t)c);
    printf("# memfnsurvey tim, ns/call min..max of 3 loops >= 50 ms, case=miss, mode=ind\n%-18s", "n");
    for (size_t j = 0; j < NN; j++) printf(" %15zu", ns[j]);
    printf("\n");
    for (int v = 0; v < NV; v++) {
        printf("%-18s", vname[v]);
        for (size_t j = 0; j < NN; j++) {
            long reps = 256; double t;
            while ((t = runners[v](buf, ns[j], reps)) < 50e6) reps = (long)(reps * (t > 1e5 ? 1.2 * 50e6 / t : 16.0));
            double lo = 1e300, hi = 0;
            for (int k = 0; k < 3; k++) { double x = runners[v](buf, ns[j], reps) / reps; if (x < lo) lo = x; if (x > hi) hi = x; }
            printf(" %7.2f..%-7.2f", lo, hi);
            fflush(stdout);
        }
        printf("\n");
    }
    return 0;
}
