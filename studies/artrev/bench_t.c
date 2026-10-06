/* bench_t.c -- [ARTREV] one timed unit of ONE arm: find-all over a subject file.
 *
 *   bench_t SUBJECT REPS      -> `ns_per_byte<TAB>matches<TAB>checksum`
 * One untimed warm pass, then REPS timed passes of the bench's find-all loop
 * (search from pos; advance to match end; step one char on an empty match).
 * REPS<=0: print the single-pass time in seconds as `PASS_S x` (calibration).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <time.h>
#include "artrev_abi.h"

static double now_s(void)
{ struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return (double)t.tv_sec + 1e-9 * (double)t.tv_nsec; }

static unsigned long pass(const unsigned char *s, size_t n, ptrdiff_t (*caps)[2], unsigned long *cnt)
{
    size_t pos = 0;
    unsigned long c = 0, sum = 0;
    for (;;) {
        int rc = art_search(s, n, pos, caps);
        if (rc != 1) { sum = sum * 1000003UL + (unsigned long)(rc + 100); break; }
        c++;
        sum = sum * 1000003UL + (unsigned long)caps[0][0] * 31UL + (unsigned long)caps[0][1];
        pos = (size_t)caps[0][1];
        if (caps[0][1] == caps[0][0]) pos = art_next_pos(s, n, pos);
        if (pos > n) break;
    }
    *cnt = c;
    return sum;
}

int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: bench_t SUBJECT REPS\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    fseek(f, 0, SEEK_END); long fl = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc((size_t)fl + 64);
    if (fread(s, 1, (size_t)fl, f) != (size_t)fl) return 2;
    fclose(f);
    size_t n = (size_t)fl;
    int reps = atoi(argv[2]);
    ptrdiff_t (*caps)[2] = malloc((size_t)art_ncaps() * sizeof *caps);
    unsigned long c = 0, sum = pass(s, n, caps, &c);       /* warm */
    if (reps <= 0) {
        double t0 = now_s(); pass(s, n, caps, &c);
        printf("PASS_S\t%.9f\n", now_s() - t0);
        return 0;
    }
    double t0 = now_s();
    for (int i = 0; i < reps; i++) sum = pass(s, n, caps, &c);
    double el = now_s() - t0;
    printf("%.5f\t%lu\t%lu\n", 1e9 * el / ((double)reps * (double)(n ? n : 1)), c, sum);
    return 0;
}
