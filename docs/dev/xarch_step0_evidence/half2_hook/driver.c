/* THE HOOK driver: floor pattern ("#") on three --vm-entry-shape rungs
 * (1=plain, 2=shared, 3=forward), interleaved timing on this Mac/ARM box.
 * Scratch tier. Not part of pcrec's build. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "floor_s1.h"
#include "floor_s2.h"
#include "floor_s3.h"

static double now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

/* One "throughput" cell: search calls across the whole subject, no match
 * anywhere (worst case full scan), matching the bench's clean/no-hit
 * regime in spirit. subject_length bytes, search_from=0 each call. */
static double time_search(int shape, const unsigned char *subj, size_t len, int iters) {
    ptrdiff_t caps[1][2];
    double t0 = now_ns();
    volatile int sink = 0;
    for (int i = 0; i < iters; i++) {
        int r;
        if (shape == 1) r = rx_floor_s1_search(subj, len, 0, caps);
        else if (shape == 2) r = rx_floor_s2_search(subj, len, 0, caps);
        else r = rx_floor_s3_search(subj, len, 0, caps);
        sink += r;
    }
    double t1 = now_ns();
    (void)sink;
    return (t1 - t0) / iters;  /* ns per search call (= "throughput" cell unit) */
}

static int cmp_d(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

int main(int argc, char **argv) {
    size_t len = 128 * 1024;
    int iters = (argc > 1) ? atoi(argv[1]) : 200;
    int trials = (argc > 2) ? atoi(argv[2]) : 7;

    unsigned char *subj = malloc(len);
    /* "clean" subject: no '#' anywhere -- forces full scan to end on every
     * call, the worst-case / throughput-shaped regime. */
    for (size_t i = 0; i < len; i++) subj[i] = (unsigned char)('a' + (i % 26));

    double t1[64], t2[64], t3[64];
    if (trials > 64) trials = 64;

    /* interleaved A/B/C/A/B/C... rounds */
    for (int t = 0; t < trials; t++) {
        t1[t] = time_search(1, subj, len, iters);
        t2[t] = time_search(2, subj, len, iters);
        t3[t] = time_search(3, subj, len, iters);
    }

    qsort(t1, trials, sizeof(double), cmp_d);
    qsort(t2, trials, sizeof(double), cmp_d);
    qsort(t3, trials, sizeof(double), cmp_d);
    double m1 = t1[trials/2], m2 = t2[trials/2], m3 = t3[trials/2];

    printf("shape=plain(1)   median_ns=%.1f  min=%.1f max=%.1f\n", m1, t1[0], t1[trials-1]);
    printf("shape=shared(2)  median_ns=%.1f  min=%.1f max=%.1f\n", m2, t2[0], t2[trials-1]);
    printf("shape=forward(3) median_ns=%.1f  min=%.1f max=%.1f\n", m3, t3[0], t3[trials-1]);
    printf("ratio forward/plain  = %.4f\n", m3 / m1);
    printf("ratio forward/shared = %.4f\n", m3 / m2);
    printf("ratio shared/plain   = %.4f\n", m2 / m1);

    free(subj);
    return 0;
}
