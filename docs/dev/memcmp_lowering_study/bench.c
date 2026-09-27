/* [OPT-LITSCAN] memcmp-lowering study: microbench comparing the three
 * candidate compare forms P4's row could take, at a length L (compiled in
 * via -DL=n) on three input regimes: matching, first-byte mismatch, last-
 * byte mismatch. Scratch tier, light: N_CALLS iterations per arm, arms
 * interleaved per round and the BEST round kept (the box is shared).
 * Never committed as a benchmark harness pcrec runs — throwaway, per the
 * brief. Build: gcc-16 -O2 bench.c -o bench -DL=7 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#ifndef L
#define L 7
#endif

#define BUF_LEN 4096
#define N_POS   256          /* distinct candidate positions per buffer */
#define N_CALLS 2000000
#define N_ROUNDS 5

static unsigned char lit[L];

static void fill_lit(void) {
    for (int i = 0; i < L; i++) lit[i] = (unsigned char)('a' + (i % 26));
}

/* Three regimes over a shared subject buffer: MATCH (the literal is
 * planted at every candidate position), MISMATCH_FIRST (candidate's first
 * byte differs from lit[0]), MISMATCH_LAST (every byte but the last
 * matches). */
static unsigned char *make_subject(int regime) {
    unsigned char *s = malloc(BUF_LEN);
    for (int i = 0; i < BUF_LEN; i++) s[i] = (unsigned char)('A' + (i % 26));
    for (int p = 0; p + L <= BUF_LEN; p += (BUF_LEN / N_POS) > 0 ? (BUF_LEN / N_POS) : 1) {
        memcpy(s + p, lit, L);
        if (regime == 1) s[p] ^= 0xFF;             /* first byte mismatch */
        else if (regime == 2) s[p + L - 1] ^= 0xFF; /* last byte mismatch */
    }
    return s;
}

static int cmp_memcmp(const unsigned char *s, size_t pos, size_t n) {
    return pos + L <= n && !memcmp(s + pos, lit, L);
}

static int cmp_ifchain(const unsigned char *s, size_t pos, size_t n) {
    if (pos + L > n) return 0;
    for (int i = 0; i < L; i++) if (s[pos + i] != lit[i]) return 0;
    return 1;
}

#if L == 2
static int cmp_mask(const unsigned char *s, size_t pos, size_t n) {
    uint16_t w, c;
    if (pos + 2 > n) return 0;
    memcpy(&w, s + pos, 2);
    memcpy(&c, lit, 2);
    return w == c;
}
#elif L <= 4
static int cmp_mask(const unsigned char *s, size_t pos, size_t n) {
    uint32_t w, c = 0;
    if (pos + 4 > n) return 0;
    memcpy(&w, s + pos, 4);
    memcpy(&c, lit, L);
    return (w & (uint32_t)((1ULL << (8*L)) - 1)) == c;
}
#else
static int cmp_mask(const unsigned char *s, size_t pos, size_t n) {
    uint64_t w, c = 0;
    if (pos + 8 > n) return 0;
    memcpy(&w, s + pos, 8);
    memcpy(&c, lit, L <= 8 ? L : 8);
    uint64_t m = (L >= 8) ? ~0ULL : ((1ULL << (8*L)) - 1);
    return (w & m) == c;
}
#endif

static double now_s(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

typedef int (*cmpfn)(const unsigned char *, size_t, size_t);

static double time_arm(cmpfn fn, const unsigned char *s, size_t n) {
    volatile int sink = 0;
    double best = 1e18;
    for (int r = 0; r < N_ROUNDS; r++) {
        double t0 = now_s();
        size_t pos = 0;
        for (int i = 0; i < N_CALLS; i++) {
            sink += fn(s, pos, n);
            pos += 7;
            if (pos + L > n) pos = 0;
        }
        double dt = now_s() - t0;
        if (dt < best) best = dt;
    }
    (void)sink;
    return best;
}

int main(void) {
    fill_lit();
    const char *regime_name[3] = {"match", "mismatch_first", "mismatch_last"};
    printf("L=%d\n", L);
    for (int regime = 0; regime < 3; regime++) {
        unsigned char *s = make_subject(regime);
        /* interleave arms within each regime: run memcmp, ifchain, mask,
         * memcmp, ifchain, mask ... taking best-of-N per arm as time_arm
         * already does, but call them in rotation so a transient box load
         * spike does not land entirely inside one arm's timing window. */
        double t_memcmp = 1e18, t_ifchain = 1e18, t_mask = 1e18;
        for (int pass = 0; pass < 1; pass++) {
            double a = time_arm(cmp_memcmp, s, BUF_LEN);
            double b = time_arm(cmp_ifchain, s, BUF_LEN);
            double c = time_arm(cmp_mask, s, BUF_LEN);
            if (a < t_memcmp) t_memcmp = a;
            if (b < t_ifchain) t_ifchain = b;
            if (c < t_mask) t_mask = c;
        }
        printf("  %-15s memcmp=%.4fs (%.2f ns/call)  ifchain=%.4fs (%.2f ns/call)  mask=%.4fs (%.2f ns/call)\n",
               regime_name[regime],
               t_memcmp, t_memcmp * 1e9 / N_CALLS,
               t_ifchain, t_ifchain * 1e9 / N_CALLS,
               t_mask, t_mask * 1e9 / N_CALLS);
        free(s);
    }
    return 0;
}
