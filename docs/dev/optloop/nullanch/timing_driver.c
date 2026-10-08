/* docs/dev/optloop/nullanch/timing_driver.c -- [NULLABLE-ANCH] STEP 0's
 * quick local timer (INDICATIVE, not a bench result). Links ONE generated
 * matcher (prefix `rx`, header "m.h") and times rx_search on a subject.
 *
 *   timing_driver SPEC [REPS]
 *
 * SPEC: `a*N!` etc. is spelled  CHAR:COUNT[:TAIL]  -- COUNT copies of CHAR
 * then the literal TAIL (default empty). `text:BYTES` is BYTES of lowercase
 * prose-like text (words of 3-8 letters separated by one space). Prints
 * `rc ns_per_call iters` for the median of REPS timed batches (each batch
 * runs until >= 40 ms or one call when a call alone exceeds that). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "m.h"

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
int main(int argc, char **argv)
{
    if (argc < 2) return 2;
    int reps = argc > 2 ? atoi(argv[2]) : 5;
    char *spec = strdup(argv[1]);
    unsigned char *subj; size_t n;
    if (!strncmp(spec, "text:", 5)) {
        n = (size_t)atol(spec + 5);
        subj = malloc(n + 1);
        unsigned s = 12345; size_t i = 0;
        while (i < n) {
            s = s * 1103515245u + 12345u;
            int w = 3 + (s >> 16) % 6;
            for (int k = 0; k < w && i < n; k++) { s = s * 1103515245u + 12345u; subj[i++] = 'a' + (s >> 16) % 26; }
            if (i < n) subj[i++] = ' ';
        }
    } else {
        char c = spec[0];
        char *p = strchr(spec, ':');
        size_t cnt = (size_t)atol(p + 1);
        char *tail = strchr(p + 1, ':');
        tail = tail ? tail + 1 : "";
        n = cnt + strlen(tail);
        subj = malloc(n + 1);
        memset(subj, c, cnt);
        memcpy(subj + cnt, tail, strlen(tail));
    }
    ptrdiff_t caps[RX_NCAPS][2];
    double *t = malloc(sizeof(double) * (size_t)reps);
    int rc = 0; long iters = 1;
    for (int r = 0; r < reps; r++) {
        long it = 0; double t0 = now(), el;
        do { rc = rx_search(subj, n, 0, caps); it++; el = now() - t0; } while (el < 40e6 && it < 100000000L);
        t[r] = el / (double)it; iters = it;
    }
    qsort(t, (size_t)reps, sizeof(double), cmp);
    printf("%d\t%.1f\t%ld\n", rc, t[reps / 2], iters);
    return 0;
}
