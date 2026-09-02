/* [OPT-VMFL] STEP 0 (b): timing driver, two regimes.
 * Regime "match": repeat a single rx_search(buf,n,0,caps) call R times,
 * same subject every time (the "short-subject match loop").
 * Regime "findall": repeat a find-all pass over the subject R times,
 * advancing pos = (end>pos)?end:pos+1 after every call until pos>len,
 * reproducing pcrec-bench's testees/pcrec/driver.c:548-565 shape (the
 * "large-subject throughput loop", opt5_step0_profile.md's own model).
 * Reports total elapsed ns and total call count so the caller computes
 * ns/call; median-of-trials is taken across repeated PROCESS launches
 * (opt5m's own method), not inside one process, so page-fault/cache
 * warmup cost is identical between orig and twin runs. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "nest2-64_lib.h"

static double now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

int main(int argc, char **argv)
{
    if (argc < 4) {
        fprintf(stderr, "usage: %s match|findall SUBJECT REPEATS\n", argv[0]);
        return 2;
    }
    const char *regime = argv[1];
    FILE *f = fopen(argv[2], "rb");
    if (!f) { fprintf(stderr, "cannot open %s\n", argv[2]); return 2; }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *buf = malloc((size_t)n > 0 ? (size_t)n : 1);
    if (n > 0 && fread(buf, 1, (size_t)n, f) != (size_t)n) { fprintf(stderr, "short read\n"); return 2; }
    fclose(f);
    long repeats = strtol(argv[3], NULL, 10);

    ptrdiff_t caps[RX_NCAPS][2];
    long long total_calls = 0;

    /* warm-up, not timed */
    for (int w = 0; w < 3; w++) {
        if (strcmp(regime, "match") == 0) {
            rx_search(buf, (size_t)n, 0, caps);
        } else {
            size_t pos = 0;
            while (pos <= (size_t)n) {
                int rc = rx_search(buf, (size_t)n, pos, caps);
                if (rc == 1) {
                    size_t end = (size_t)caps[0][1];
                    pos = (end > pos) ? end : pos + 1;
                } else {
                    pos++;
                }
            }
        }
    }

    double t0 = now_ns();
    if (strcmp(regime, "match") == 0) {
        for (long r = 0; r < repeats; r++) {
            rx_search(buf, (size_t)n, 0, caps);
            total_calls++;
        }
    } else if (strcmp(regime, "findall") == 0) {
        for (long r = 0; r < repeats; r++) {
            size_t pos = 0;
            while (pos <= (size_t)n) {
                int rc = rx_search(buf, (size_t)n, pos, caps);
                total_calls++;
                if (rc == 1) {
                    size_t end = (size_t)caps[0][1];
                    pos = (end > pos) ? end : pos + 1;
                } else {
                    pos++;
                }
            }
        }
    } else {
        fprintf(stderr, "unknown regime %s\n", regime);
        return 2;
    }
    double t1 = now_ns();

    printf("elapsed_ns=%.1f total_calls=%lld ns_per_call=%.4f\n",
           t1 - t0, total_calls, (t1 - t0) / (double)total_calls);
    return 0;
}
