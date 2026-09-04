/* lad_driver.c -- [CC-DIFF] STEP 2 the ns/call LADDER's timing driver.
 *
 * Protocol is isl1 report S12.2's, reused deliberately so the numbers are
 * COMPARABLE to the run-time arm already in evidence: <prefix>_search in a
 * FIND-ALL loop over a 131,072-byte subject, the answer checked EVERY round
 * by a checksum over every span (not a hit count -- a build that finds the
 * same NUMBER of matches in different places must part), median over rounds
 * reported with the per-round range beside it.
 *
 * WHAT ns/call MEANS HERE, and it is the whole point of the cell set. The VM
 * entry chain is a PER-CALL cost, so the metric is elapsed / (number of
 * rx_search invocations), and the subject is chosen DENSE (the bench's
 * t-128k-dense.bin, 1024 branch occurrences) so a pass makes ~1000 calls
 * rather than one. A cell that makes one call per pass measures the SCAN and
 * not the entry chain; the harness treats such a cell as VACUOUS and says so
 * rather than quoting it. That is docs/dev/learnings.md S3's [MECH-REACH]
 * shape -- a witness that stopped reaching its site.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>
#include "art.h"

static double now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (double)ts.tv_sec * 1e9 + (double)ts.tv_nsec;
}

/* one find-all pass; returns the number of rx_search CALLS made, and
 * accumulates a checksum over every span so the answer is checked and not
 * merely counted. */
static unsigned long pass(const unsigned char *s, size_t n,
                          unsigned long *hits, uint64_t *sum)
{
    ptrdiff_t caps[64][2];
    size_t pos = 0;
    unsigned long calls = 0, h = 0;
    uint64_t k = 1469598103934665603ULL;
    for (;;) {
        calls++;
        if (!rx_search(s, n, pos, caps)) break;
        h++;
        k = (k ^ (uint64_t)caps[0][0]) * 1099511628211ULL;
        k = (k ^ (uint64_t)caps[0][1]) * 1099511628211ULL;
        pos = (caps[0][1] > caps[0][0])
            ? (size_t)caps[0][1]
            : rx_next_pos(s, n, (size_t)caps[0][0]);
        if (pos > n) break;
    }
    *hits = h;
    *sum = k;
    return calls;
}

int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: %s SUBJECT ROUNDS [PASSES]\n", argv[0]); return 2; }
    int rounds = atoi(argv[2]);
    int passes = (argc > 3) ? atoi(argv[3]) : 1;

    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("subject"); return 2; }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *buf = malloc((size_t)len + 1);
    if (!buf || fread(buf, 1, (size_t)len, f) != (size_t)len) { fprintf(stderr, "read\n"); return 2; }
    fclose(f);

    /* warm the caches and establish the answer this cell must keep */
    unsigned long hits0 = 0, calls0;
    uint64_t sum0 = 0;
    calls0 = pass(buf, (size_t)len, &hits0, &sum0);

    double *ns = malloc(sizeof(double) * (size_t)rounds);
    for (int r = 0; r < rounds; r++) {
        unsigned long h = 0, calls = 0;
        uint64_t sum = 0;
        double t0 = now_ns();
        for (int p = 0; p < passes; p++) calls += pass(buf, (size_t)len, &h, &sum);
        double t1 = now_ns();
        if (h != hits0 || sum != sum0) {
            fprintf(stderr, "ANSWER MOVED between rounds: hits %lu vs %lu, sum %llu vs %llu\n",
                    h, hits0, (unsigned long long)sum, (unsigned long long)sum0);
            return 3;
        }
        ns[r] = (t1 - t0) / (double)calls;
    }
    /* median and range */
    for (int i = 1; i < rounds; i++) {
        double v = ns[i]; int j = i - 1;
        while (j >= 0 && ns[j] > v) { ns[j+1] = ns[j]; j--; }
        ns[j+1] = v;
    }
    double med = ns[rounds/2];
    /* calls_per_pass, hits, median ns/call, min, max, answer checksum */
    printf("%lu\t%lu\t%.4f\t%.4f\t%.4f\t%llu\n",
           calls0, hits0, med, ns[0], ns[rounds-1], (unsigned long long)sum0);
    return 0;
}
