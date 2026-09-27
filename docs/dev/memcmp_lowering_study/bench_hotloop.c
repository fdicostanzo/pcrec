/* [OPT-LITSCAN] follow-up (Frank, 2026-09-27): does the single-wide-load
 * form's one-fewer-load win over the overlapping-two-load form show up in
 * a TIGHT LOOP, once the single-wide form's own wider bounds guard
 * (pos + W <= n) is assumed already discharged by the caller (so neither
 * arm pays a per-position bounds check here — only the outer loop bound
 * does, established once)? Both arms use the SAME masking discipline
 * (the ASCII case-fold AND-mask, 0xDF per byte) so the comparison isolates
 * load count alone, not "masked vs unmasked". Scan a literal at every
 * candidate position of a 1 MiB buffer, for L in {5,6,7,10,12}.
 * Build: gcc-16 -O2 bench_hotloop.c -o bench_hotloop -DL=7 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#ifndef L
#define L 7
#endif

#define BUF_LEN (1u << 20)   /* 1 MiB */
#define N_ROUNDS 7
#define N_REPEATS 300

static unsigned char lit[L];
static void fill_lit(void) {
    for (int i = 0; i < L; i++) lit[i] = (unsigned char)('a' + (i % 26));
}

/* ---- overlapping two-load masked form: two natural-width loads, W < L
 * <= 2W, each AND-masked with the ASCII fold mask, safety pos + L <= n
 * only. ---- */
#if L <= 8
typedef uint32_t ov_t;
#define OV_W 4
#define OV_MASK 0xDFDFDFDFu
#else
typedef uint64_t ov_t;
#define OV_W 8
#define OV_MASK 0xDFDFDFDFDFDFDFDFULL
#endif
static ov_t ov_t0, ov_t1;
static int ov_off1;
static void ov_init(void) {
    ov_t a = 0, b = 0;
    memcpy(&a, lit, OV_W);
    int off1 = L - OV_W; if (off1 < 0) off1 = 0;
    memcpy(&b, lit + off1, OV_W);
    ov_off1 = off1;
    ov_t0 = a & (ov_t)OV_MASK;
    ov_t1 = b & (ov_t)OV_MASK;
}
static inline int cmp_overlap_masked(const unsigned char *s, size_t pos) {
    ov_t a, b;
    memcpy(&a, s + pos, OV_W);
    memcpy(&b, s + pos + ov_off1, OV_W);
    return (a & (ov_t)OV_MASK) == ov_t0 && (b & (ov_t)OV_MASK) == ov_t1;
}

/* ---- single-wide-load masked form: ONE load of the smallest natural
 * width W >= L (16 bytes via __uint128_t when L > 8), masked, one
 * compare. Its own bounds guard (pos + W <= n) is ASSUMED DISCHARGED —
 * the caller (here, the driving loop's own bound) already guarantees it,
 * per Frank's framing; this function does not re-check it. ---- */
#if L <= 8
typedef uint64_t wide_t;
#define WIDE_W 8
#define WIDE_MASK 0xDFDFDFDFDFDFDFDFULL
#else
typedef unsigned __int128 wide_t;
#define WIDE_W 16
#endif
static wide_t wide_target, wide_mask;
static void wide_init(void) {
    wide_t w = 0;
    memcpy(&w, lit, L);
#if L <= 8
    wide_mask = (wide_t)WIDE_MASK;
#else
    wide_t m = 0;
    unsigned char mb[16];
    for (int i = 0; i < 16; i++) mb[i] = 0xDF;
    memcpy(&m, mb, 16);
    wide_mask = m;
#endif
    wide_target = w & wide_mask;
}
static inline int cmp_wide_masked(const unsigned char *s, size_t pos) {
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
    fill_lit();
    ov_init();
    wide_init();

    unsigned char *buf = malloc(BUF_LEN);
    /* mostly-non-matching pseudo-random content; a handful of planted hits
     * so neither compare is a pure branch-predictor freebie. */
    unsigned x = 12345u;
    for (size_t i = 0; i < BUF_LEN; i++) {
        x = x * 1103515245u + 12345u;
        buf[i] = (unsigned char)(x >> 16);
    }
    for (size_t p = 0; p + L <= BUF_LEN; p += 4001) memcpy(buf + p, lit, L);

    /* The tight loop bound is the SAME for both arms — the wider of the
     * two forms' own extents (WIDE_W for the single-wide form, L for the
     * overlap form) — so both scan the identical position set and neither
     * arm's inner body does its own bounds test. */
    size_t max_extent = WIDE_W > L ? WIDE_W : (size_t)L;
    size_t n_pos = BUF_LEN - max_extent + 1;

    double best_ov = 1e18, best_wide = 1e18;
    volatile unsigned sink;

    for (int round = 0; round < N_ROUNDS; round++) {
        sink = 0;
        double t0 = now_s();
        for (int r = 0; r < N_REPEATS; r++) {
            for (size_t pos = 0; pos < n_pos; pos++)
                sink += cmp_overlap_masked(buf, pos);
        }
        double dt = now_s() - t0;
        if (dt < best_ov) best_ov = dt;
    }
    for (int round = 0; round < N_ROUNDS; round++) {
        sink = 0;
        double t0 = now_s();
        for (int r = 0; r < N_REPEATS; r++) {
            for (size_t pos = 0; pos < n_pos; pos++)
                sink += cmp_wide_masked(buf, pos);
        }
        double dt = now_s() - t0;
        if (dt < best_wide) best_wide = dt;
    }
    (void)sink;

    double total_iters = (double)n_pos * N_REPEATS;
    double ns_ov = best_ov * 1e9 / total_iters;
    double ns_wide = best_wide * 1e9 / total_iters;
    printf("L=%d  W_overlap=%d  W_wide=%d  n_pos=%zu  iters=%.0f\n",
           L, OV_W, WIDE_W, n_pos, total_iters);
    printf("  overlap-two-load: %.6f s  (%.4f ns/iter)\n", best_ov, ns_ov);
    printf("  single-wide-load: %.6f s  (%.4f ns/iter)\n", best_wide, ns_wide);
    printf("  delta (overlap - wide): %.4f ns/iter  (%.1f%% of wide)\n",
           ns_ov - ns_wide, 100.0 * (ns_ov - ns_wide) / ns_wide);
    free(buf);
    return 0;
}
