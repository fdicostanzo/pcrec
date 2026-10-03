/* scratch: the bench driver's three regimes over a list of subject files.
 * mode s = one search from 0 per subject (search_short), f = find-all
 * (throughput), m = rx_match_caps anchored at 0 (match). Each subject's
 * loop runs `iters` times; prints total ns per call summed over subjects
 * (median over `reps` passes) and an answer hash. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>
#include <time.h>
extern int rx_search(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
static uint64_t now_ns(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return (uint64_t)t.tv_sec * 1000000000ull + (uint64_t)t.tv_nsec; }
static int cmp(const void *a, const void *b) { double x = *(const double *)a, y = *(const double *)b; return x < y ? -1 : x > y; }
int main(int argc, char **argv)
{
    char mode = argv[1][0]; long iters = atol(argv[2]); int reps = atoi(argv[3]);
    int ns = argc - 4; unsigned char **b = malloc(ns * sizeof *b); size_t *n = malloc(ns * sizeof *n);
    for (int i = 0; i < ns; i++) {
        FILE *f = fopen(argv[4 + i], "rb"); fseek(f, 0, SEEK_END); n[i] = (size_t)ftell(f); fseek(f, 0, SEEK_SET);
        b[i] = malloc(n[i] + 1); if (fread(b[i], 1, n[i], f) != n[i]) return 2; fclose(f);
    }
    double t[64]; uint64_t h = 1469598103934665603ull; ptrdiff_t caps[1][2];
    for (int r = 0; r < reps; r++) {
        double tot = 0;
        for (int i = 0; i < ns; i++) {
            uint64_t t0 = now_ns();
            for (long it = 0; it < iters; it++) {
                if (mode == 's') { int k = rx_search(b[i], n[i], 0, caps); h ^= (uint64_t)(k * 31 + (k == 1 ? caps[0][0] : 0)); }
                else if (mode == 'm') { rx_ctx cx; memset(&cx, 0, sizeof cx); cx.subject = b[i]; cx.len = n[i]; cx.pos = 0; long long k = rx_match_caps(&cx, caps); h ^= (uint64_t)k; }
                else { size_t pos = 0; long c = 0;
                    while (pos <= n[i]) { int k = rx_search(b[i], n[i], pos, caps); if (k != 1) break; c++;
                        pos = caps[0][1] > caps[0][0] ? (size_t)caps[0][1] : (size_t)caps[0][0] + 1; }
                    h ^= (uint64_t)c; }
                h *= 1099511628211ull;
            }
            tot += (double)(now_ns() - t0) / iters;
        }
        t[r] = tot;
    }
    qsort(t, reps, sizeof t[0], cmp);
    printf("%.1f %.1f %016llx\n", t[reps / 2], t[0], (unsigned long long)h);
    return 0;
}
