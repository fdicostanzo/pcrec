/* [OPT-REVEND] revision 2 (lane revrev) FOUR-arm TIMING driver (STUDY,
 * SCRATCH TIER).
 *
 *   timedrv4 SUBJECT.bin [target_ns] [rounds]
 *
 * Arms (prefixes, each compiled in only when its macro is defined):
 *   o  today's default artifact (W1 active where it applies)  HAVE_O
 *   c  form C, walk-only (revision 2's primary)              HAVE_C
 *   a  form A, walk + anchored entry every call              HAVE_A
 *   b  form B, walk then the unchanged body from s*          HAVE_B
 * Every twin is built from the -fno-end-window artifact (the head-placed
 * walk, X7). Per arm, the call count per round is calibrated once so a round
 * costs about target_ns (min 1 call, max 20000). Arms are timed INTERLEAVED,
 * and the arm order ROTATES each round so no arm always runs first. Prints
 * one TSV line: n, rc, span, then per arm (o c a b; "-" where absent) the
 * median/min/max over rounds of the per-call mean (ns). Asserts every
 * present arm returns the same answer (ANSWER-DIFF, exit 1 otherwise). */
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include <time.h>
#ifdef HAVE_O
#include "o.h"
#endif
#ifdef HAVE_C
#include "c.h"
#endif
#ifdef HAVE_A
#include "a.h"
#endif
#ifdef HAVE_B
#include "b.h"
#endif

typedef int (*searchfn)(const unsigned char *, size_t, size_t, ptrdiff_t (*)[2]);
static searchfn arm[4] = {
#ifdef HAVE_O
    (searchfn)o_search,
#else
    0,
#endif
#ifdef HAVE_C
    (searchfn)c_search,
#else
    0,
#endif
#ifdef HAVE_A
    (searchfn)a_search,
#else
    0,
#endif
#ifdef HAVE_B
    (searchfn)b_search,
#else
    0,
#endif
};

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
    double target = argc > 2 ? atof(argv[2]) : 100000;
    int rounds = argc > 3 ? atoi(argv[3]) : 31;
    static unsigned char buf[1 << 22];
    size_t n = f ? fread(buf, 1, sizeof buf, f) : 0;
    ptrdiff_t cap[64][2];
    volatile int sink = 0;
    int rc0 = -99; ptrdiff_t s0 = -1, e0 = -1;
    if (rounds > 255) rounds = 255;
    long reps[4] = {0};
    for (int k = 0; k < 4; k++) {
        if (!arm[k]) continue;
        memset(cap, 0xff, sizeof cap);
        int rc = arm[k](buf, n, 0, cap);
        ptrdiff_t s = rc == 1 ? cap[0][0] : -1, e = rc == 1 ? cap[0][1] : -1;
        if (rc0 == -99) { rc0 = rc; s0 = s; e0 = e; }
        else if (rc != rc0 || s != s0 || e != e0) {
            printf("ANSWER-DIFF arm=%d rc=%d(%td,%td) vs %d(%td,%td)\n", k, rc, s, e, rc0, s0, e0);
            return 1;
        }
        double t0 = now(); long c = 0;
        do { sink += arm[k](buf, n, 0, cap); c++; } while (now() - t0 < 2e6 && c < 100000);
        double per = (now() - t0) / c;
        reps[k] = (long)(target / per); if (reps[k] < 1) reps[k] = 1; if (reps[k] > 20000) reps[k] = 20000;
    }
    static double v[4][256];
    for (int r = 0; r < rounds; r++)
        for (int j = 0; j < 4; j++) {
            int k = (j + r) % 4;
            if (!arm[k]) continue;
            double t0 = now();
            for (long i = 0; i < reps[k]; i++) sink += arm[k](buf, n, 0, cap);
            v[k][r] = (now() - t0) / reps[k];
        }
    printf("%zu\t%d\t%td,%td", n, rc0, s0, e0);
    for (int k = 0; k < 4; k++) {
        if (!arm[k]) { printf("\t-\t-\t-"); continue; }
        qsort(v[k], rounds, sizeof(double), cmpd);
        printf("\t%.1f\t%.1f\t%.1f", v[k][rounds / 2], v[k][0], v[k][rounds - 1]);
    }
    printf("\n");
    return 0;
}
