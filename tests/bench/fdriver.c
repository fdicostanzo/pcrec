/*
 * fdriver.c — FIND-ALL throughput timing driver for tests/bench.
 *
 * Why it exists (2026-08-26, [OPT-3] STEP 1): `bdriver.c` times ONE
 * `rx_search` call over the whole subject. The comparative bench
 * (pcrec-bench, `bench/email/NOTES.md` "Regime coverage") times its 1 MB
 * subjects in the FIND-ALL regime — search, restart at the match end,
 * repeat — and the two are different cost classes on a subject with tens
 * of thousands of matches (the restart pays a reverse scan per match).
 * Attributing a per-byte cost against a bench number therefore needs a
 * driver that runs the bench's loop, not bdriver's.
 *
 * The find-all loop below is transcribed from pcrec-bench's own
 * `testees/pcrec/driver.c` (its `find_all` branch): restart at
 * `caps[0][1]`, and force progress with `pos + 1` when the match was
 * empty, stopping once `pos > len`. Same restart rule, so the counts and
 * the per-call work match the bench's.
 *
 * Usage: fdriver <subject-file> <iterations> [findall|first]
 *   default mode is findall.
 *
 * Prints exactly one line:
 *   bytes=<n> iters=<k> mode=<m> secs=<s> nsperbyte=<v> mbps=<v>
 *   count=<c> [start=<s> end=<e>]
 *
 * Compiled together with a gen.c/gen.h pair from
 * `pcrec -p rx -o <dir>/gen.c -- PATTERN`, exactly like bdriver.c.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "gen.h"

int main(int argc, char **argv)
{
    if (argc != 3 && argc != 4) {
        fprintf(stderr, "usage: %s <subject-file> <iterations> [findall|first]\n",
                argc > 0 ? argv[0] : "fdriver");
        return 2;
    }

    const char *path = argv[1];
    char *end = NULL;
    long iters = strtol(argv[2], &end, 10);
    if (end == argv[2] || iters <= 0) {
        fprintf(stderr, "fdriver: iterations must be a positive integer, got '%s'\n",
                argv[2]);
        return 2;
    }
    const char *mode = (argc == 4) ? argv[3] : "findall";
    int find_all;
    if (!strcmp(mode, "findall"))    find_all = 1;
    else if (!strcmp(mode, "first")) find_all = 0;
    else { fprintf(stderr, "fdriver: mode must be findall or first\n"); return 2; }

    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); return 2; }
    if (fseek(f, 0, SEEK_END) != 0) { perror(path); fclose(f); return 2; }
    long fsize = ftell(f);
    if (fsize < 0) { perror(path); fclose(f); return 2; }
    if (fseek(f, 0, SEEK_SET) != 0) { perror(path); fclose(f); return 2; }

    size_t n = (size_t)fsize;
    unsigned char *buf = malloc(n > 0 ? n : 1);
    if (!buf) { fprintf(stderr, "fdriver: out of memory (%zu bytes)\n", n); fclose(f); return 2; }
    size_t got = fread(buf, 1, n, f);
    fclose(f);
    if (got != n) {
        fprintf(stderr, "fdriver: short read on %s (%zu of %zu bytes)\n", path, got, n);
        free(buf); return 2;
    }

    ptrdiff_t caps[RX_NCAPS][2];
    memset(caps, 0, sizeof caps);
    /* `volatile` so the whole timed loop cannot be hoisted or folded: the
     * results are read after the clock stops, and without this a compiler
     * is free to notice the loop body is iteration-invariant. */
    volatile long count = 0;
    volatile long first_s = -1, first_e = -1;

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < iters; i++) {
        long c = 0;
        first_s = first_e = -1;
        if (find_all) {
            size_t pos = 0;
            for (;;) {
                int r = rx_search(buf, n, pos, caps);
                if (r == 0) break;
                if (r < 0) break;
                if (first_s < 0) { first_s = (long)caps[0][0]; first_e = (long)caps[0][1]; }
                c++;
                size_t e = (size_t)caps[0][1];
                pos = (e > pos) ? e : pos + 1;
                if (pos > n) break;
            }
        } else {
            int r = rx_search(buf, n, 0, caps);
            if (r == 1) { first_s = (long)caps[0][0]; first_e = (long)caps[0][1]; c = 1; }
        }
        count = c;
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    free(buf);

    double secs = (double)(t1.tv_sec - t0.tv_sec) +
                  (double)(t1.tv_nsec - t0.tv_nsec) / 1e9;
    double bytes = (double)n * (double)iters;
    double nspb  = (bytes > 0.0 && secs > 0.0) ? (secs * 1e9) / bytes : 0.0;
    double mbps  = secs > 0.0 ? (bytes / (1024.0 * 1024.0)) / secs : 0.0;

    printf("bytes=%zu iters=%ld mode=%s secs=%.6f nsperbyte=%.4f mbps=%.3f count=%ld",
           n, iters, mode, secs, nspb, mbps, (long)count);
    if (first_s >= 0) printf(" start=%ld end=%ld", (long)first_s, (long)first_e);
    printf("\n");
    return 0;
}
