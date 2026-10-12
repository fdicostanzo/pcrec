/* lane lrvm twin timing (scratch tier, for a QUIET slot only): the bench's
 * find-all loop over each subject, best of R runs, ns per subject and the
 * answer checksum.   fatime R SUBJ... */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "rx.h"
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec / 1e9; }
int main(int argc, char **argv)
{
    int R = atoi(argv[1]); double sum = 0;
    for (int a = 2; a < argc; a++) {
        FILE *f = fopen(argv[a], "rb"); if (!f) return 2;
        fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
        unsigned char *b = malloc(n + 1); if (fread(b, 1, n, f) != (size_t)n) return 2; fclose(f);
        ptrdiff_t caps[RX_NCAPS][2]; double best = 1e30; unsigned long long ck = 0;
        for (int r = 0; r < R; r++) {
            double t0 = now(); size_t pos = 0; ck = 0;
            for (;;) {
                int rc = rx_search(b, n, pos, caps);
                if (rc != 1) break;
                size_t st = caps[0][0], en = caps[0][1];
                ck = ck * 1000003u + st * 31u + en;
                pos = en > st ? en : st + 1;
                if (pos > (size_t)n) break;
            }
            double t = now() - t0; if (t < best) best = t;
        }
        printf("%s\t%ld\tck=%016llx\t%.0f ns\n", argv[a], n, ck, best * 1e9);
        sum += best * 1e9; free(b);
    }
    printf("TOTAL\t%.0f ns\n", sum);
    return 0;
}
