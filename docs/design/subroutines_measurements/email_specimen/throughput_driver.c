/* throughput_driver.c -- find-all loop over one subject file, timed 5x.
 * Parameterized via -DHDR='"artifact.h"' -DSEARCH=prefix_search -DNCAPS=PREFIX_NCAPS.
 * Loads the subject once, then runs 5 timed find-all passes (CLOCK_MONOTONIC),
 * printing each rep's elapsed seconds and match count, plus the median.
 * A "giveup" during a pass aborts that pass and is reported, not silently
 * folded into the match count.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>
#include <time.h>

#include HDR

static double now(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec + (double)ts.tv_nsec / 1e9;
}

static int cmp_double(const void *a, const void *b) {
    double da = *(const double *)a, db = *(const double *)b;
    return (da > db) - (da < db);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s subjectfile\n", argc > 0 ? argv[0] : "tdriver");
        return 2;
    }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("fopen"); return 2; }
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *buf = malloc(sz > 0 ? (size_t)sz : 1);
    if (!buf) { fprintf(stderr, "oom\n"); return 2; }
    if (sz > 0 && fread(buf, 1, (size_t)sz, f) != (size_t)sz) {
        fprintf(stderr, "short read\n"); return 2;
    }
    fclose(f);

    double reps[5];
    long matchcount = -1;
    int giveup_code = 0;

    for (int rep = 0; rep < 5; rep++) {
        size_t pos = 0;
        long mc = 0;
        int gu = 0;
        double t0 = now();
        while (pos <= (size_t)sz) {
            ptrdiff_t caps[NCAPS][2];
            int found = SEARCH(buf, (size_t)sz, pos, caps);
            if (found == 1) {
                mc++;
                size_t end = (size_t)caps[0][1];
                pos = (end > pos) ? end : pos + 1;
            } else if (found == 0) {
                break;
            } else {
                gu = found;
                break;
            }
        }
        double t1 = now();
        reps[rep] = t1 - t0;
        if (rep == 0) { matchcount = mc; giveup_code = gu; }
    }

    double sorted[5];
    memcpy(sorted, reps, sizeof(reps));
    qsort(sorted, 5, sizeof(double), cmp_double);
    double median = sorted[2];

    printf("subject=%s bytes=%ld matches=%ld giveup=%d reps=[%.6f %.6f %.6f %.6f %.6f] median=%.6f\n",
           argv[1], sz, matchcount, giveup_code,
           reps[0], reps[1], reps[2], reps[3], reps[4], median);
    free(buf);
    return 0;
}
