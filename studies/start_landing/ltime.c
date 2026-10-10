/* [START-LANDING] find-all timing of one artifact (prefix rx), RAW samples
 * (STUDY). The bench's find-all loop (advance to the end, one byte past an
 * empty match), R runs, every run's wall time printed so the caller computes
 * median and standard deviation over interleaved repeats.
 *   ltime SUBJ R   ->   cnt ck t1_us t2_us ... tR_us */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "rx.h"
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec / 1e9; }
int main(int argc, char **argv)
{
    if (argc != 3) return 2;
    FILE *f = fopen(argv[1], "rb"); fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc(n + 1); if (fread(b, 1, n, f) != (size_t)n) return 2; fclose(f);
    int R = atoi(argv[2]);
    ptrdiff_t caps[RX_NCAPS][2]; long cnt = 0; unsigned long long ck = 0;
    double *t = malloc(sizeof(double) * R);
    for (int r = 0; r < R; r++) {
        double t0 = now(); cnt = 0; ck = 0;
        size_t pos = 0;
        for (;;) {
            int rc = rx_search(b, n, pos, caps);
            if (rc != 1) break;
            cnt++;
            size_t st = caps[0][0], en = caps[0][1];
            ck = ck * 1000003u + st * 31u + en;
            pos = en > st ? en : st + 1;
            if (pos > (size_t)n) break;
        }
        t[r] = (now() - t0) * 1e6;
    }
    printf("%ld\t%016llx", cnt, ck);
    for (int r = 0; r < R; r++) printf("\t%.1f", t[r]);
    printf("\n");
    return 0;
}
