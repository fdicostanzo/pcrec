/* d-01024 whole-subject match-compliance driver: anchored ptrdiff_t
 * <prefix>_match(ctx) on a 1024-byte non-a-z (digit) subject, which every
 * cls-upto-N pattern here fails immediately on ([a-z]{0,N} cannot consume
 * a digit byte) -- so this times the FAILED-CALL dispatch, ns/subject,
 * the same quantity the bench's ledger calls "d-01024". SYNTHESIZED
 * subject (digits "0"-"9" repeating x 1024), not drawn from the bench's
 * own subject generator -- said so in the memo. Scratch tier. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <time.h>

typedef struct rx_ctx {
    const unsigned char *subject;
    size_t                len;
    size_t                pos;
    size_t                ncap;
    const ptrdiff_t     (*caps)[2];
    void                 *user;
} rx_ctx;

typedef ptrdiff_t (*matchfn)(const rx_ctx *);

static double now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

extern matchfn get_fn(void);

static int cmp_d(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

int main(int argc, char **argv) {
    int iters = (argc > 1) ? atoi(argv[1]) : 1000000;
    int trials = (argc > 2) ? atoi(argv[2]) : 9;
    size_t len = (argc > 3) ? (size_t)atol(argv[3]) : 1024;
    unsigned char *subj = malloc(len);
    for (size_t i = 0; i < len; i++) subj[i] = (unsigned char)('0' + (i % 10));

    matchfn fn = get_fn();
    rx_ctx ctx = { subj, len, 0, 0, NULL, NULL };

    volatile ptrdiff_t sink = 0;
    for (int i = 0; i < iters; i++) sink += fn(&ctx);  /* warmup */

    double *t = malloc(sizeof(double) * (size_t)trials);
    for (int r = 0; r < trials; r++) {
        double t0 = now_ns();
        for (int i = 0; i < iters; i++) sink += fn(&ctx);
        double t1 = now_ns();
        t[r] = (t1 - t0) / iters;
    }
    (void)sink;
    qsort(t, trials, sizeof(double), cmp_d);
    printf("median_ns_per_set=%.3f min=%.3f max=%.3f\n", t[trials/2], t[0], t[trials-1]);
    free(subj);
    return 0;
}
