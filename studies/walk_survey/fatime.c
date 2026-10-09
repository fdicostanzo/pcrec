/* walk_survey: plain (uninstrumented) find-all / search timing of one
 * artifact (prefix rx) on one subject: the bench's find-all loop (byte
 * advance), best of R runs.   fatime SUBJ MODE(findall|search) R */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "rx.h"
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec / 1e9; }
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb"); fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc(n + 1); if (fread(b, 1, n, f) != (size_t)n) return 2; fclose(f);
    int fa = !strcmp(argv[2], "findall"); int R = atoi(argv[3]);
    ptrdiff_t caps[RX_NCAPS][2]; double best = 1e30; long cnt = 0;
    for (int r = 0; r < R; r++) {
        double t0 = now(); cnt = 0;
        if (fa) {
            size_t pos = 0;
            for (;;) {
                int rc = rx_search(b, n, pos, caps);
                if (rc != 1) break;
                cnt++;
                size_t st = caps[0][0], en = caps[0][1];
                pos = en > st ? en : st + 1;
                if (pos > (size_t)n) break;
            }
        } else cnt = rx_search(b, n, 0, caps);
        double t = now() - t0; if (t < best) best = t;
    }
    printf("%s\t%ld\t%s\t%ld\t%.1f us\t%.3f ns/B\n", argv[1], n, argv[2], cnt, best * 1e6, best * 1e9 / n);
    return 0;
}
