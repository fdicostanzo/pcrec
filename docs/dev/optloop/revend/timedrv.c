/* [OPT-REVEND] SCRATCH-TIER timing driver: min-of-N wall ns of one
 * <prefix>_search call over a file subject, search_from 0.  Links one
 * pcrec-emitted artifact (prefix rx).  Not the bench: no pinning, no
 * governor control; the figure is "what a linear scan costs", not a ledger
 * number.
 *   cc -O2 timedrv.c art.c -o drv ; ./drv subject.bin [reps] */
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <time.h>
#include "art.h"

static double now(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1e9 + t.tv_nsec;
}

int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb");
    int reps = argc > 2 ? atoi(argv[2]) : 7;
    static unsigned char buf[1 << 22];
    size_t n = f ? fread(buf, 1, sizeof buf, f) : 0;
    ptrdiff_t caps[RX_NCAPS][2] = {{0}};
    double best = 1e30;
    int rc = 0;
    for (int i = 0; i < reps; i++) {
        double t0 = now();
        rc = rx_search(buf, n, 0, caps);
        double dt = now() - t0;
        if (dt < best) best = dt;
    }
    printf("rc=%d span=%td,%td n=%zu min_ns=%.0f ns_per_B=%.4f\n", rc,
           rc == 1 ? caps[0][0] : -1, rc == 1 ? caps[0][1] : -1, n, best, best / n);
    return 0;
}
