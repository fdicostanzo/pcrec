/* HALF 2 throughput driver: sweeps a full search-to-completion pass over
 * each of the four altwide throughput subjects for one artifact, timing
 * the whole sweep (ns/set, matching the bench's own unit). Scratch tier.
 * Interleaved trials across testees are driven by the shell wrapper
 * (one binary per testee, invoked round-robin) rather than inside this
 * binary, so each run here is one arm's single trial. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <time.h>

typedef int (*search_fn)(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);

static double now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

static unsigned char *read_file(const char *path, size_t *len_out) {
    FILE *f = fopen(path, "rb");
    if (!f) { fprintf(stderr, "cannot open %s\n", path); exit(1); }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *buf = malloc((size_t)len);
    if (fread(buf, 1, (size_t)len, f) != (size_t)len) { fprintf(stderr, "short read\n"); exit(1); }
    fclose(f);
    *len_out = (size_t)len;
    return buf;
}

/* one full sweep: search-to-completion over the whole subject, following
 * matches to their end and continuing (a zero-length match advances by 1
 * to avoid an infinite loop). Returns elapsed ns. */
static double sweep(search_fn fn, const unsigned char *subj, size_t len) {
    ptrdiff_t caps[1][2];
    size_t pos = 0;
    volatile int sink = 0;
    double t0 = now_ns();
    for (;;) {
        int r = fn(subj, len, pos, caps);
        if (r != 1) { sink += r; break; }
        size_t end = (size_t)caps[0][1];
        pos = (end > pos) ? end : pos + 1;
        if (pos > len) break;
    }
    double t1 = now_ns();
    (void)sink;
    return t1 - t0;
}

extern search_fn get_fn(void);  /* provided per-artifact by a tiny stub .c */

int main(int argc, char **argv) {
    /* argv[1..4]: the four subject file paths, in a fixed order:
     * clean, sparse, dense, 512k-sparse. argv[5]: trial count. */
    if (argc < 6) { fprintf(stderr, "usage: driver s1 s2 s3 s4 trials\n"); return 1; }
    int trials = atoi(argv[5]);
    unsigned char *subj[4];
    size_t len[4];
    for (int i = 0; i < 4; i++) subj[i] = read_file(argv[1 + i], &len[i]);

    search_fn fn = get_fn();
    /* warmup, to settle branch predictor/cache before the timed rounds --
     * needed for subjects small enough that one sweep is microseconds, so
     * process/cache warmup would otherwise dominate the first few trials. */
    for (int i = 0; i < 4; i++) sweep(fn, subj[i], len[i]);
    double *totals = malloc(sizeof(double) * (size_t)trials);
    for (int t = 0; t < trials; t++) {
        double total = 0;
        for (int i = 0; i < 4; i++) total += sweep(fn, subj[i], len[i]);
        totals[t] = total;
    }
    /* median */
    for (int i = 0; i < trials; i++)
        for (int j = i + 1; j < trials; j++)
            if (totals[j] < totals[i]) { double tmp = totals[i]; totals[i] = totals[j]; totals[j] = tmp; }
    printf("median_ns_per_set=%.1f min=%.1f max=%.1f trials=%d\n",
           totals[trials / 2], totals[0], totals[trials - 1], trials);
    return 0;
}
