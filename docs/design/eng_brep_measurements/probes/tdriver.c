/* tdriver.c — throughput driver for the ENG-BREP strategy probes.
 *
 * Compiled together with a pcrec-generated matcher (prefix `rx`, captures on).
 * argv[1] is the subject, argv[2] the repetition count. Prints
 *
 *     <ns per search>\t<span lo>\t<span hi>\t<group1 lo>\t<group1 hi>
 *
 * so a caller can check that two artifacts being COMPARED for speed actually
 * agree on the answer -- a throughput number for a matcher computing a
 * different span is not a comparison. The clock is CLOCK_MONOTONIC and the
 * subject is built once, outside the loop.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stddef.h>

int rx_search(const unsigned char *s, size_t n, size_t startpos,
              ptrdiff_t (*caps)[2]);

int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: tdriver SUBJECT REPS\n"); return 2; }
    const unsigned char *s = (const unsigned char *)argv[1];
    size_t n = strlen(argv[1]);
    long reps = strtol(argv[2], NULL, 10);
    ptrdiff_t caps[16][2];

    /* one warm run, also the answer the caller checks */
    memset(caps, 0, sizeof caps);
    int r0 = rx_search(s, n, 0, caps);

    struct timespec a, b;
    clock_gettime(CLOCK_MONOTONIC, &a);
    volatile int sink = 0;
    for (long i = 0; i < reps; i++)
        sink += rx_search(s, n, 0, caps);
    clock_gettime(CLOCK_MONOTONIC, &b);
    (void)sink;

    double ns = ((double)(b.tv_sec - a.tv_sec) * 1e9
                 + (double)(b.tv_nsec - a.tv_nsec)) / (double)reps;
    printf("%.1f\t%d\t%lld\t%lld\t%lld\t%lld\n", ns, r0,
           (long long)caps[0][0], (long long)caps[0][1],
           (long long)caps[1][0], (long long)caps[1][1]);
    return 0;
}
