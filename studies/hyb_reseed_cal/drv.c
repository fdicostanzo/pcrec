/* studies/hyb_reseed_cal/drv.c — the find-all timing driver every table in
 * this study reads. Links one emitted artifact (`-p rx`), reads a subject
 * file, and runs `reps` find-all passes over it IN ONE PROCESS: after a
 * match the next search starts at the match end (or one UTF-8 character on
 * an empty match). Prints the match count, an FNV hash of every (start,end)
 * pair — two builds agree on the answers iff both agree — and the MEDIAN
 * and MIN ns per subject byte over the passes.
 *
 * NOT a fresh-launch median: the per-process layout lottery the plan row's
 * I-114 caveat names is NOT controlled here. table.py launches each binary
 * several times and takes the median of the per-launch medians, which
 * samples a few launches and no more. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>
#include <time.h>
extern int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
static uint64_t now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint64_t)t.tv_sec * 1000000000ull + (uint64_t)t.tv_nsec;
}
static void run_once(const unsigned char *s, size_t n, long *m, uint64_t *h)
{
    size_t pos = 0;
    long c = 0;
    uint64_t x = 1469598103934665603ull;
    ptrdiff_t caps[1][2];
    while (pos <= n) {
        int ok = rx_search(s, n, pos, caps);
        if (ok != 1) { if (ok < 0) x ^= 0xdead; break; }
        c++;
        x ^= (uint64_t)caps[0][0]; x *= 1099511628211ull;
        x ^= (uint64_t)caps[0][1]; x *= 1099511628211ull;
        if (caps[0][1] > caps[0][0]) pos = (size_t)caps[0][1];
        else { pos++; while (pos < n && (s[pos] & 0xC0) == 0x80) pos++; }
    }
    *m = c; *h = x;
}
static int cmp(const void *a, const void *b)
{
    double x = *(const double *)a, y = *(const double *)b;
    return x < y ? -1 : x > y;
}
int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "usage: %s SUBJECT [reps]\n", argv[0]); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc((size_t)sz + 1);
    if (fread(b, 1, (size_t)sz, f) != (size_t)sz) { perror("fread"); return 2; }
    fclose(f);
    int reps = argc > 2 ? atoi(argv[2]) : 11;
    if (reps < 1 || reps > 64) reps = 11;
    double t[64]; long m = 0; uint64_t h = 0;
    for (int i = 0; i < reps; i++) {
        long mm; uint64_t hh; uint64_t t0 = now_ns();
        run_once(b, (size_t)sz, &mm, &hh);
        t[i] = (double)(now_ns() - t0) / (double)sz;
        if (i == 0) { m = mm; h = hh; }
        else if (mm != m || hh != h) fprintf(stderr, "NONDET\n");
    }
    qsort(t, (size_t)reps, sizeof t[0], cmp);
    printf("matches=%ld hash=%016llx med_ns_per_B=%.4f min=%.4f\n",
           m, (unsigned long long)h, t[reps / 2], t[0]);
    return 0;
}
