/* [OPT-REVEND] Q1 three-arm TIMING driver (STUDY, SCRATCH TIER).
 *
 *   timedrv3 SUBJECT.bin [fast_reps] [slow_reps] [rounds]
 *
 * Arms (prefixes): o = today's default artifact (W1 active), t = form B twin
 * (built from the W1-denied artifact), d = W1-denied artifact. Per round the
 * three are timed INTERLEAVED (o, t, d); o and t get fast_reps calls, d (a
 * whole-subject scan) slow_reps. Prints one TSV line: n, rc, span, then per
 * arm median/min/max over rounds of the per-call mean (ns). Asserts all three
 * answers agree (exit 1 and ANSWER-DIFF otherwise). */
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <time.h>
#include "o.h"
#include "t.h"
#include "d.h"

static double now(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}
static int cmpd(const void *a, const void *b)
{ double x = *(const double *)a, y = *(const double *)b; return (x > y) - (x < y); }
static void rep(const double *v, int n, double *med, double *mn, double *mx)
{
    double s[128]; for (int i = 0; i < n; i++) s[i] = v[i];
    qsort(s, n, sizeof *s, cmpd); *med = s[n / 2]; *mn = s[0]; *mx = s[n - 1];
}

int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb");
    int fr = argc > 2 ? atoi(argv[2]) : 2000, sr = argc > 3 ? atoi(argv[3]) : 3,
        rounds = argc > 4 ? atoi(argv[4]) : 31;
    static unsigned char buf[1 << 22];
    size_t n = f ? fread(buf, 1, sizeof buf, f) : 0;
    ptrdiff_t co[O_NCAPS][2], ct[T_NCAPS][2], cd[D_NCAPS][2];
    double so[128], st[128], sd[128];
    volatile int sink = 0;
    int ro = o_search(buf, n, 0, co), rt = t_search(buf, n, 0, ct), rd = d_search(buf, n, 0, cd);
    if (ro != rt || ro != rd || (ro == 1 && (co[0][0] != ct[0][0] || co[0][1] != ct[0][1] ||
                                             co[0][0] != cd[0][0] || co[0][1] != cd[0][1]))) {
        printf("ANSWER-DIFF o=%d t=%d d=%d\n", ro, rt, rd); return 1;
    }
    if (rounds > 128) rounds = 128;
    for (int r = 0; r < rounds; r++) {
        double t0 = now();
        for (int i = 0; i < fr; i++) sink += o_search(buf, n, 0, co);
        double t1 = now();
        for (int i = 0; i < fr; i++) sink += t_search(buf, n, 0, ct);
        double t2 = now();
        for (int i = 0; i < sr; i++) sink += d_search(buf, n, 0, cd);
        double t3 = now();
        so[r] = (t1 - t0) / fr; st[r] = (t2 - t1) / fr; sd[r] = (t3 - t2) / sr;
    }
    double a, b, c;
    printf("%zu\t%d\t%td,%td", n, ro, ro == 1 ? co[0][0] : -1, ro == 1 ? co[0][1] : -1);
    rep(so, rounds, &a, &b, &c); printf("\t%.1f\t%.1f\t%.1f", a, b, c);
    rep(st, rounds, &a, &b, &c); printf("\t%.1f\t%.1f\t%.1f", a, b, c);
    rep(sd, rounds, &a, &b, &c); printf("\t%.1f\t%.1f\t%.1f\n", a, b, c);
    return 0;
}
