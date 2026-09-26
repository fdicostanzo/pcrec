/* [OPT-REQRUN-ENC] census item 3, rough Mac timing PROXY only (not the
 * bench's own box) -- reads a subject file, calls the emitted rx_search
 * once (find-first, matching the bench's search-short/throughput-cell
 * shape closely enough for a relative L-vs-R/S comparison), repeated
 * TRIALS times, reports the median wall ns. One process per (pattern,
 * candidate) pair -- run serially, never in parallel, per BOILERPLATE.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "RXHDR"

static long long now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static int cmp_ll(const void *a, const void *b)
{
    long long x = *(const long long *)a, y = *(const long long *)b;
    return (x > y) - (x < y);
}

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "usage: %s subject-file [trials]\n", argv[0]); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("fopen"); return 2; }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *buf = malloc((size_t)n);
    if (fread(buf, 1, (size_t)n, f) != (size_t)n) { fprintf(stderr, "short read\n"); return 2; }
    fclose(f);
    int trials = argc > 2 ? atoi(argv[2]) : 21;
    ptrdiff_t caps[RX_NCAPS][2];
    long long *t = malloc(sizeof(long long) * (size_t)trials);
    for (int i = 0; i < trials; i++) {
        long long t0 = now_ns();
        int rc = rx_search(buf, (size_t)n, 0, caps);
        long long t1 = now_ns();
        t[i] = t1 - t0;
        if (i == 0) fprintf(stderr, "rc=%d\n", rc);
    }
    qsort(t, (size_t)trials, sizeof(long long), cmp_ll);
    printf("median_ns %lld  min_ns %lld  max_ns %lld  n=%d trials=%d\n",
           t[trials / 2], t[0], t[trials - 1], (int)n, trials);
    return 0;
}
