/* lxrun (lane lxrun, 2026-10-05): survey_tim.c's x86-64 port for survey.md
 * §10.1 OWED -- the same method (miss case, independent calls, each timed
 * loop calibrated >= 50 ms, min..max of 3), the NEON/Arm-OR rows replaced by
 * StringZilla's westmere (SSE4.2) and haswell (AVX2) kernels and glibc's own
 * (ifunc-selected) memchr/memmem; musl's C memchr/memmem at the pinned commit
 * as the portable-C reference. Build with -msse4.2 -mavx2 -mbmi -mlzcnt
 * (survey_build.sh's x86 flags) so StringZilla's SZ_USE_* gates open. */
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

static sz_byteset_t set_dig, set_ws, set_hi, set_lower, set_notlower;
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

#define NV 17
static const char *const vname[NV] = {
    "loop", "glibc memchr", "musl memchr", "sz byte serial", "sz byte westmere", "sz byte haswell",
    "table find[0-9]", "sz set serial[0-9]", "sz set haswell[0-9]", "sz set haswell[\\s]", "sz set haswell[hi]",
    "table skip[a-z]", "sz notfrom hsw[a-z]", "glibc memmem Zqx", "musl memmem Zqx", "sz find wsm Zqx", "sz find hsw Zqx",
};
static const char Z = 'Z';
static inline __attribute__((always_inline)) const void *call(int v, const uint8_t *s, size_t n) {
    switch (v) {
    case 0: return s;
    case 1: return memchr(s, 'Z', n);
    case 2: return musl_memchr(s, 'Z', n);
    case 3: return sz_find_byte_serial((sz_cptr_t)s, n, &Z);
    case 4: return sz_find_byte_westmere((sz_cptr_t)s, n, &Z);
    case 5: return sz_find_byte_haswell((sz_cptr_t)s, n, &Z);
    case 6: return tab_find(s, n, tab_dig);
    case 7: return sz_find_byteset_serial((sz_cptr_t)s, n, &set_dig);
    case 8: return sz_find_byteset_haswell((sz_cptr_t)s, n, &set_dig);
    case 9: return sz_find_byteset_haswell((sz_cptr_t)s, n, &set_ws);
    case 10: return sz_find_byteset_haswell((sz_cptr_t)s, n, &set_hi);
    case 11: return tab_skip(s, n, tab_lower);
    case 12: return sz_find_byteset_haswell((sz_cptr_t)s, n, &set_notlower);
    case 13: return memmem(s, n, "Zqx", 3);
    case 14: return musl_memmem(s, n, "Zqx", 3);
    case 15: return sz_find_westmere((sz_cptr_t)s, n, "Zqx", 3);
    default: return sz_find_haswell((sz_cptr_t)s, n, "Zqx", 3);
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
TIMER(12) TIMER(13) TIMER(14) TIMER(15) TIMER(16)
typedef double (*runner)(const uint8_t *, size_t, long);
static const runner runners[NV] = {run_0, run_1, run_2, run_3, run_4, run_5, run_6, run_7, run_8,
                                   run_9, run_10, run_11, run_12, run_13, run_14, run_15, run_16};
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
    set_notlower = set_lower; sz_byteset_invert(&set_notlower);
    /* correctness spot-check: every kernel finds a planted needle at each n-1 */
    for (size_t j = 0; j < NN; j++) {
        size_t n = ns[j];
        for (int v = 1; v < NV; v++) {
            uint8_t save[3]; memcpy(save, buf + n - 1, 3);
            const char *plant = v >= 13 ? "Zqx" : v == 6 || v == 7 || v == 8 ? "7" : v == 9 ? " " : v == 10 ? "\xe9" : v == 11 || v == 12 ? "Z" : "Z";
            size_t at = v >= 13 ? (n >= 3 ? n - 3 : 0) : n - 1;
            if (v >= 13 && n < 3) continue;
            memcpy(save, buf + at, 3); memcpy(buf + at, plant, strlen(plant));
            const void *p = call(v, buf, n);
            memcpy(buf + at, save, 3);
            if (p != buf + at) { printf("CHECK FAIL %s n=%zu\n", vname[v], n); return 1; }
        }
    }
    printf("# lxrun survey_tim_x86, ns/call min..max of 3 loops >= 50 ms, case=miss, mode=ind (check: ok)\n%-20s", "n");
    for (size_t j = 0; j < NN; j++) printf(" %15zu", ns[j]);
    printf("\n");
    for (int v = 0; v < NV; v++) {
        printf("%-20s", vname[v]);
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
