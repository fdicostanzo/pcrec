/* [OPT-LITSCAN] second hot-loop follow-up (team-lead, 2026-09-27): should
 * P4 spell its own overlapping-load compare for odd L under gcc, instead
 * of relying on `memcmp()` (whose gcc lowering is a branchy, non-
 * overlapping power-of-two chain, §3 of the memo)? Three arms, all under
 * gcc-16 -O2, at every candidate position of a 1 MiB buffer whose content
 * is REALISTIC: mostly first-piece mismatches, a denser band of NEAR
 * MISSES (the literal with its last byte flipped — the shape that makes
 * gcc's multi-piece memcmp decomposition pay for every piece before
 * failing), and a sparse band of full matches.
 *   (a) memcmp   — P4's own current form: `pos+L<=n && !memcmp(...)`.
 *   (b) overlap  — the hand-written two-load form (§3/§5 of the memo),
 *                  EXACT bytes, no mask: `pos+L<=n` only.
 *   (c) wide     — one load of the smallest covering natural width,
 *                  masked to the low L bytes, its own wider bounds guard
 *                  (pos+W<=n) assumed already discharged by the caller.
 * Build: gcc-16 -O2 bench_hotloop2.c -o bench_hotloop2 -DL=7 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#ifndef L
#define L 7
#endif

#define BUF_LEN (1u << 20)
#define N_ROUNDS 7
#define N_REPEATS 300

static unsigned char lit[L];
static void fill_lit(void) { for (int i = 0; i < L; i++) lit[i] = (unsigned char)('a' + (i % 26)); }

/* (a) memcmp — P4's own shape */
static inline int cmp_memcmp_arm(const unsigned char *s, size_t pos, size_t n) {
    return pos + L <= n && !memcmp(s + pos, lit, L);
}

/* (b) overlap — exact bytes, two natural-width loads */
#if L <= 8
typedef uint32_t ov_t;
#define OV_W 4
#else
typedef uint64_t ov_t;
#define OV_W 8
#endif
static ov_t ov_v0, ov_v1;
static int ov_off1;
static void ov_init(void) {
    ov_t a = 0, b = 0;
    memcpy(&a, lit, OV_W);
    int off1 = L - OV_W; if (off1 < 0) off1 = 0;
    memcpy(&b, lit + off1, OV_W);
    ov_off1 = off1; ov_v0 = a; ov_v1 = b;
}
static inline int cmp_overlap_arm(const unsigned char *s, size_t pos, size_t n) {
    if (pos + L > n) return 0;
    ov_t a, b;
    memcpy(&a, s + pos, OV_W);
    memcpy(&b, s + pos + ov_off1, OV_W);
    return a == ov_v0 && b == ov_v1;
}

/* (c) wide — one load of the smallest covering width, masked, guard
 * ASSUMED DISCHARGED (no per-call check here; the driving loop's own
 * bound plays that role). */
#if L <= 8
typedef uint64_t wide_t;
#define WIDE_W 8
#else
typedef unsigned __int128 wide_t;
#define WIDE_W 16
#endif
static wide_t wide_target, wide_mask;
static void wide_init(void) {
    wide_t w = 0, m = 0;
    unsigned char mb[16];
    for (int i = 0; i < 16; i++) mb[i] = (i < L) ? 0xFF : 0x00;
    memcpy(&m, mb, WIDE_W);
    memcpy(&w, lit, L);
    wide_mask = m; wide_target = w & m;
}
static inline int cmp_wide_arm(const unsigned char *s, size_t pos) {
    wide_t w;
    memcpy(&w, s + pos, WIDE_W);
    return (w & wide_mask) == wide_target;
}

static double now_s(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(void) {
    fill_lit(); ov_init(); wide_init();

    unsigned char *buf = malloc(BUF_LEN);
    unsigned x = 777u;
    for (size_t i = 0; i < BUF_LEN; i++) {
        x = x * 1103515245u + 12345u;
        buf[i] = (unsigned char)(x >> 16);
    }
    /* dense near-miss band: the literal with its LAST byte flipped —
     * forces memcmp's decomposition to walk every piece before failing */
    for (size_t p = 0; p + L <= BUF_LEN; p += 797) {
        memcpy(buf + p, lit, L);
        buf[p + L - 1] ^= 0xFF;
    }
    /* sparse full-match band */
    for (size_t p = 0; p + L <= BUF_LEN; p += 4001)
        memcpy(buf + p, lit, L);

    size_t max_extent = WIDE_W > (size_t)L ? WIDE_W : (size_t)L;
    size_t n_pos = BUF_LEN - max_extent + 1;
    double total_iters = (double)n_pos * N_REPEATS;

    double best[3] = {1e18, 1e18, 1e18};
    volatile unsigned sink;
    /* arms interleaved round by round */
    for (int round = 0; round < N_ROUNDS; round++) {
        sink = 0;
        double t0 = now_s();
        for (int r = 0; r < N_REPEATS; r++)
            for (size_t pos = 0; pos < n_pos; pos++)
                sink += cmp_memcmp_arm(buf, pos, BUF_LEN);
        double dt = now_s() - t0;
        if (dt < best[0]) best[0] = dt;

        sink = 0;
        t0 = now_s();
        for (int r = 0; r < N_REPEATS; r++)
            for (size_t pos = 0; pos < n_pos; pos++)
                sink += cmp_overlap_arm(buf, pos, BUF_LEN);
        dt = now_s() - t0;
        if (dt < best[1]) best[1] = dt;

        sink = 0;
        t0 = now_s();
        for (int r = 0; r < N_REPEATS; r++)
            for (size_t pos = 0; pos < n_pos; pos++)
                sink += cmp_wide_arm(buf, pos);
        dt = now_s() - t0;
        if (dt < best[2]) best[2] = dt;
    }
    (void)sink;

    double ns[3];
    for (int i = 0; i < 3; i++) ns[i] = best[i] * 1e9 / total_iters;
    printf("L=%d  n_pos=%zu\n", L, n_pos);
    printf("  memcmp:  %.6f s  (%.4f ns/iter)\n", best[0], ns[0]);
    printf("  overlap: %.6f s  (%.4f ns/iter)  delta vs memcmp: %+.4f ns (%+.1f%%)\n",
           best[1], ns[1], ns[1]-ns[0], 100.0*(ns[1]-ns[0])/ns[0]);
    printf("  wide:    %.6f s  (%.4f ns/iter)  delta vs memcmp: %+.4f ns (%+.1f%%)  delta vs overlap: %+.4f ns (%+.1f%%)\n",
           best[2], ns[2], ns[2]-ns[0], 100.0*(ns[2]-ns[0])/ns[0], ns[2]-ns[1], 100.0*(ns[2]-ns[1])/ns[1]);
    free(buf);
    return 0;
}
