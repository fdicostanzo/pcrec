/*
 * bdriver.c — throughput timing driver for tests/bench.
 *
 * Usage: bdriver <subject-file> <iterations>
 *   Reads <subject-file> fully into memory (the length is tracked
 *   explicitly from fseek/ftell, never from strlen, since subjects may
 *   contain embedded NULs or arbitrary bytes), then calls
 *   rx_search(buf, n, 0, &m) against the whole buffer <iterations> times
 *   back to back, timing the loop with clock_gettime(CLOCK_MONOTONIC).
 *
 * Prints exactly one line to stdout:
 *   bytes=<n> iters=<k> secs=<s> mbps=<v> match=<0|1> [start=<s> end=<e>]
 * (start/end are only present when match=1) and exits 0.
 *
 * This file always does `#include "gen.h"` — it must be compiled together
 * with a gen.c/gen.h pair produced by `pcrec -p rx -o <dir>/gen.c -- PATTERN`
 * (see run_bench.sh, which always uses the fixed basename "gen" so this
 * driver never has to know the pattern or prefix).
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "gen.h"

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "usage: %s <subject-file> <iterations>\n",
                argc > 0 ? argv[0] : "bdriver");
        return 2;
    }

    const char *path = argv[1];
    char *end = NULL;
    long iters = strtol(argv[2], &end, 10);
    if (end == argv[2] || iters <= 0) {
        fprintf(stderr, "bdriver: iterations must be a positive integer, got '%s'\n",
                argv[2]);
        return 2;
    }

    FILE *f = fopen(path, "rb");
    if (!f) {
        perror(path);
        return 2;
    }
    if (fseek(f, 0, SEEK_END) != 0) {
        perror(path);
        fclose(f);
        return 2;
    }
    long fsize = ftell(f);
    if (fsize < 0) {
        perror(path);
        fclose(f);
        return 2;
    }
    if (fseek(f, 0, SEEK_SET) != 0) {
        perror(path);
        fclose(f);
        return 2;
    }

    size_t n = (size_t)fsize;
    unsigned char *buf = malloc(n > 0 ? n : 1);
    if (!buf) {
        fprintf(stderr, "bdriver: out of memory (%zu bytes)\n", n);
        fclose(f);
        return 2;
    }

    size_t got = fread(buf, 1, n, f);
    fclose(f);
    if (got != n) {
        fprintf(stderr, "bdriver: short read on %s (%zu of %zu bytes)\n",
                path, got, n);
        free(buf);
        return 2;
    }

    ptrdiff_t caps[RX_NCAPS][2];
    caps[0][0] = 0;
    caps[0][1] = 0;
    int found = 0;
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < iters; i++) {
        found = rx_search(buf, n, 0, caps);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    free(buf);

    double secs = (double)(t1.tv_sec - t0.tv_sec) +
                  (double)(t1.tv_nsec - t0.tv_nsec) / 1e9;
    double mb = ((double)n * (double)iters) / (1024.0 * 1024.0);
    double mbps = secs > 0.0 ? mb / secs : 0.0;

    printf("bytes=%zu iters=%ld secs=%.6f mbps=%.3f match=%d",
           n, iters, secs, mbps, found);
    if (found) {
        printf(" start=%td end=%td", caps[0][0], caps[0][1]);
    }
    printf("\n");

    return 0;
}
