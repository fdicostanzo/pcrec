/* [OPT-REVEND] hand-twin TIMING driver (STUDY, SCRATCH TIER).
 *
 *   timedrv SUBJECT.bin [reps] [rounds]
 *
 * Links the unmodified artifact (prefix o) and its twin (prefix t). Per
 * round it times `reps` calls of each from search_from 0, INTERLEAVED
 * (o, t, o, t, ...) so a load change hits both; reports per arm the min
 * and the median over rounds of the per-call mean, in ns, plus ns/B, and
 * asserts the two answers agree. Not the bench: one core pinned by the
 * caller (taskset), no governor control, load1 recorded by the caller. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <time.h>
#include "o.h"
#include "t.h"

static double now(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}
static int cmpd(const void *a, const void *b)
{ double x = *(const double *)a, y = *(const double *)b; return (x > y) - (x < y); }

int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb");
    int reps = argc > 2 ? atoi(argv[2]) : 20, rounds = argc > 3 ? atoi(argv[3]) : 15;
    static unsigned char buf[1 << 22];
    size_t n = f ? fread(buf, 1, sizeof buf, f) : 0;
    ptrdiff_t co[O_NCAPS][2], ct[T_NCAPS][2];
    double so[64], st[64];
    volatile int sink = 0;
    int ro = o_search(buf, n, 0, co), rt = t_search(buf, n, 0, ct);
    if (ro != rt || (ro == 1 && (co[0][0] != ct[0][0] || co[0][1] != ct[0][1]))) {
        printf("ANSWER-DIFF orig=%d twin=%d\n", ro, rt); return 1;
    }
    if (rounds > 64) rounds = 64;
    for (int r = 0; r < rounds; r++) {
        double t0 = now();
        for (int i = 0; i < reps; i++) sink += o_search(buf, n, 0, co);
        double t1 = now();
        for (int i = 0; i < reps; i++) sink += t_search(buf, n, 0, ct);
        double t2 = now();
        so[r] = (t1 - t0) / reps; st[r] = (t2 - t1) / reps;
    }
    double mo = so[0], mt = st[0];
    for (int r = 1; r < rounds; r++) { if (so[r] < mo) mo = so[r]; if (st[r] < mt) mt = st[r]; }
    qsort(so, rounds, sizeof *so, cmpd); qsort(st, rounds, sizeof *st, cmpd);
    printf("n=%zu rc=%d span=%td,%td | orig min=%.0f med=%.0f ns (%.4f ns/B) | twin min=%.1f med=%.1f ns | x%.0f\n",
           n, ro, ro == 1 ? co[0][0] : -1, ro == 1 ? co[0][1] : -1,
           mo, so[rounds / 2], so[rounds / 2] / n, mt, st[rounds / 2], so[rounds / 2] / st[rounds / 2]);
    return 0;
}
