/* grid1: the TIMED driver. slot25c's alpha/drv.c (vecspike's vdrv.c with
 * -DKEEP) with three extensions, nothing else changed in the method:
 *   - the subject may be a directory or a *.list manifest (gload.h): the
 *     STREAMED case. One pass is one buffer; the timed loops cycle through
 *     the buffers with one cursor that never resets, so consecutive passes
 *     see distinct data. ns/pass is per buffer.
 *   - GRID_OFF=k places every buffer k bytes past a 64-aligned block.
 *   - GRID_FIXED=N skips the clock: N passes, then the answer line with
 *     `passes=N` instead of `ns/pass=` (the check gate uses N = 0; F2's perf
 *     pass uses N > 0 and N = 0 to subtract the load). `cycle` folds a
 *     content fingerprint of the buffer each of the N passes is handed
 *     (read through the same cursor the timed loops use) and `cycleexp`
 *     the fingerprints of every buffer in order: with N = the buffer count
 *     they are equal exactly when the cursor visits every buffer once, in
 *     order (check.sh's leg C). Answers cannot show this: a planted match
 *     sits at the same offsets in every buffer of a streamed subject.
 *
 *   run SUBJECT first|all   ->  matches=M hash=H ns/pass=X
 *
 * Method (drv.c's): calibrate by doubling until one loop is >= 50 ms, then 7
 * rounds of that loop, the median. matches/hash: one pass over EVERY buffer,
 * folded with GRID_FOLD (one buffer: exactly drv.c's line). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>
#include <time.h>
#include "gload.h"
#ifdef KEEP
#include "keep.h"
#endif
extern int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
extern size_t rx_next_pos(const unsigned char *s, size_t n, size_t pos);
static uint64_t now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return (uint64_t)t.tv_sec*1000000000ull+t.tv_nsec;}
static int cmp(const void*a,const void*b){double x=*(double*)a,y=*(double*)b;return x<y?-1:x>y;}
static ptrdiff_t cp[64][2];
/* one pass: `first` = one call from 0; `all` = §3.1's find-all loop */
static long pass(const unsigned char *b, size_t n, int all, unsigned long *h)
{
    if (!all) { int r = rx_search(b, n, 0, cp); *h ^= r == 1 ? (unsigned long)cp[0][0] * 31u + cp[0][1] : 7u; return 1; }
    size_t p = 0; long k = 0;
#ifdef KEEP
    struct rx_keep st = {0};   /* V3-family: one state per find-all pass */
    while (p <= n && rx_search_keep(b, n, p, cp, &st) == 1) {
#else
    while (p <= n && rx_search(b, n, p, cp) == 1) {
#endif
        k++; *h = *h * 131u + (unsigned long)cp[0][0] * 31u + (unsigned long)cp[0][1];
        p = cp[0][1] > cp[0][0] ? rx_next_pos(b, n, (size_t)cp[0][1] - 1) : rx_next_pos(b, n, (size_t)cp[0][1]);
        if (cp[0][1] == cp[0][0] && (size_t)cp[0][1] >= n) break;
    }
    return k;
}
static size_t cur;
static unsigned long bufprint(const struct gbuf *b)
{
    unsigned long h = 1469598103934665603ul ^ b->n;
    for (size_t i = 0; i < b->n; i++) h = (h ^ b->p[i]) * 1099511628211ul;
    return h;
}
static long next_pass(int all, unsigned long *g)
{
    long k = pass(gbufs[cur].p, gbufs[cur].n, all, g);
    if (++cur == gnbuf) cur = 0;
    return k;
}
int main(int c, char **v)
{
    if (c < 3 || (strcmp(v[2], "first") && strcmp(v[2], "all"))) { fprintf(stderr, "usage: run SUBJECT first|all\n"); return 2; }
    int all = !strcmp(v[2], "all");
    gload(v[1], goff());
    unsigned long H = 0; long m = 0;
    for (size_t i = 0; i < gnbuf; i++) { unsigned long h = 0; m += pass(gbufs[i].p, gbufs[i].n, all, &h); GRID_FOLD(H, h); }
    const char *fx = getenv("GRID_FIXED");
    if (fx && *fx) {
        long N = atol(fx); unsigned long C = 0, E = 0;
        for (size_t i = 0; i < gnbuf; i++) GRID_FOLD(E, bufprint(&gbufs[i]));
        for (long i = 0; i < N; i++) { unsigned long g = 0; GRID_FOLD(C, bufprint(&gbufs[cur])); next_pass(all, &g); }
        printf("matches=%ld hash=%lx passes=%ld cycle=%lx cycleexp=%lx\n", m, H, N, C, E);
        return 0;
    }
    long it = 1; uint64_t t0;
    do { it *= 2; t0 = now(); unsigned long g = 0; for (long i = 0; i < it; i++) next_pass(all, &g); } while (now() - t0 < 50000000);
    double t[7];
    for (int k = 0; k < 7; k++) { unsigned long g = 0; t0 = now(); for (long i = 0; i < it; i++) next_pass(all, &g); t[k] = (double)(now() - t0) / it; }
    qsort(t, 7, sizeof t[0], cmp);
    printf("matches=%ld hash=%lx ns/pass=%.2f\n", m, H, t[3]);
    return 0;
}
