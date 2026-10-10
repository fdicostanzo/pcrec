/* docs/dev/optloop/et1twin/etdrv.c -- [ENG-TACTICS] stage 1 trigger lane
 * et1twin: the identity + timing driver for ONE search function over
 * generated artifacts (prefix `rx`, header "rx.h"). Built twice per cell:
 *   -DET_FN=rx_search   today's artifact, unmodified
 *   -DET_FN=tw_search   the hand twin (twin_<cell>.c, which #includes rx.c)
 *
 *   etdrv ident FILE...          per file: the bench's find-all loop
 *                                (advance to the match end, one byte past
 *                                an empty match) and single searches from
 *                                every startpos (stride 1 up to 4 KiB,
 *                                then every 4099th byte); prints counts and
 *                                FNV-1a hashes of every (pos, rc, s, e)
 *   etdrv spans FILE             the find-all spans, one per line
 *   etdrv time MODE FILE REPS    MODE findall|search: median of REPS
 *                                batches (each >= 40 ms) in ns per call
 *                                (one call = one whole find-all pass, or
 *                                one rx_search from 0), + ns/B
 *
 * p2drv.c prints the same `ident` lines from libpcre2-8, so the three
 * outputs are compared with diff. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "rx.h"

#ifndef ET_FN
#error "build with -DET_FN=rx_search or -DET_FN=tw_search"
#endif
int ET_FN(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);

static unsigned char *load(const char *path, size_t *n)
{
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); exit(2); }
    fseek(f, 0, SEEK_END); long len = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc((size_t)len + 1);
    if (fread(b, 1, (size_t)len, f) != (size_t)len) exit(2);
    fclose(f);
    *n = (size_t)len;
    return b;
}
static unsigned long long fnv(unsigned long long h, long long v)
{
    for (int i = 0; i < 8; i++) { h ^= (unsigned char)(v >> (8 * i)); h *= 1099511628211ULL; }
    return h;
}
static double now(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}
static int cmp(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}
static long findall(const unsigned char *b, size_t n, unsigned long long *h, FILE *out)
{
    ptrdiff_t caps[RX_NCAPS][2];
    size_t pos = 0; long cnt = 0;
    while (pos <= n) {
        int rc = ET_FN(b, n, pos, caps);
        if (rc != 1) { if (h) *h = fnv(*h, rc); break; }
        cnt++;
        if (h) { *h = fnv(*h, caps[0][0]); *h = fnv(*h, caps[0][1]); }
        if (out) fprintf(out, "%td\t%td\n", caps[0][0], caps[0][1]);
        pos = caps[0][1] > caps[0][0] ? (size_t)caps[0][1] : (size_t)caps[0][0] + 1;
    }
    return cnt;
}
int main(int argc, char **argv)
{
    if (argc < 3) return 2;
    if (!strcmp(argv[1], "ident")) {
        for (int a = 2; a < argc; a++) {
            size_t n; unsigned char *b = load(argv[a], &n);
            unsigned long long hf = 14695981039346656037ULL, hs = hf;
            long cnt = findall(b, n, &hf, NULL), hits = 0, tried = 0;
            ptrdiff_t caps[RX_NCAPS][2];
            for (size_t p = 0; p <= n; p += p < 4096 ? 1 : 4099) {
                int rc = ET_FN(b, n, p, caps);
                tried++;
                hs = fnv(hs, (long long)p); hs = fnv(hs, rc);
                if (rc == 1) { hits++; hs = fnv(hs, caps[0][0]); hs = fnv(hs, caps[0][1]); }
            }
            const char *base = strrchr(argv[a], '/');
            printf("%s\tn=%zu\tfa=%ld\tfa_h=%016llx\tsp=%ld/%ld\tsp_h=%016llx\n",
                   base ? base + 1 : argv[a], n, cnt, hf, hits, tried, hs);
            free(b);
        }
        return 0;
    }
    if (!strcmp(argv[1], "spans")) {
        size_t n; unsigned char *b = load(argv[2], &n);
        findall(b, n, NULL, stdout);
        return 0;
    }
    if (!strcmp(argv[1], "time") && argc >= 5) {
        int fa = !strcmp(argv[2], "findall");
        size_t n; unsigned char *b = load(argv[3], &n);
        int reps = atoi(argv[4]);
        double *t = malloc(sizeof(double) * (size_t)reps);
        ptrdiff_t caps[RX_NCAPS][2];
        long cnt = 0; long it = 0;
        for (int r = 0; r < reps; r++) {
            double t0 = now(), el;
            it = 0;
            do {
                cnt = fa ? findall(b, n, NULL, NULL) : ET_FN(b, n, 0, caps);
                it++;
                el = now() - t0;
            } while (el < 40e6);
            t[r] = el / (double)it;
        }
        qsort(t, (size_t)reps, sizeof(double), cmp);
        printf("%s\t%zu\t%s\tcnt=%ld\t%.1f ns/call\t%.4f ns/B\tmin=%.1f\tmax=%.1f\titers=%ld\n",
               strrchr(argv[3], '/') ? strrchr(argv[3], '/') + 1 : argv[3], n, argv[2], cnt,
               t[reps / 2], t[reps / 2] / (double)(n ? n : 1), t[0], t[reps - 1], it);
        return 0;
    }
    return 2;
}
