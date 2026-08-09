/*
 * eng_pcrec.c — iteration-timing driver for pcrec-generated matchers, used
 * by tests/bench/compare/compare.sh's cross-engine performance comparison.
 *
 * Same role as tests/bench/bdriver.c (see that file's header for the base
 * timing convention: clock_gettime(CLOCK_MONOTONIC) around a tight
 * rx_search loop, length tracked via fseek/ftell never strlen since
 * subjects may be arbitrary binary/no trailing NUL) but three differences,
 * all driven by compare.sh's needs rather than bdriver's:
 *
 *   1. iters is always caller-supplied (compare.sh calibrates it per case
 *      so every measurement accumulates >= 0.3s wall — see compare.sh's
 *      `calibrate_and_run`), never hardcoded.
 *   2. One untimed warmup call precedes the timed loop, so the first
 *      timed iteration isn't paying a one-off cold-cache tax (page-in,
 *      branch predictor warmup) that the other iterations don't pay.
 *      Since rx_search is a pure function of (buf, n, startpos) and the
 *      subject/pattern are fixed for the whole run, the warmup call's
 *      verdict is identical to every timed call's verdict, so it doubles
 *      as this engine's half of compare.sh's pre-timing cross-engine
 *      agreement check.
 *   3. Output uses a `status=` prefixed line shared across all engine
 *      drivers in this directory (eng_pcre2.c, eng_py.py) so compare.sh
 *      has exactly one line format to parse regardless of engine.
 *
 * This file always does `#include "gen.h"` — compare.sh compiles it fresh
 * per (case, and this engine only needs one build per case since pcrec has
 * no separate interp/jit split) against a gen.c/gen.h pair produced by
 * `pcrec -p rx -o <dir>/gen.c -- PATTERN`, always at the fixed basename
 * "gen" (same convention as run_bench.sh/bdriver.c) so this driver never
 * has to know the pattern or prefix.
 *
 * Usage: eng_pcrec <subject-file> <iters>
 * Prints exactly one line to stdout and exits 0:
 *   status=ok bytes=<n> iters=<k> secs=<s> mbps=<v> match=<0|1> start=<s> end=<e>
 * (start/end are 0 when match=0, always present so compare.sh's parser
 * doesn't need per-engine special-casing). Exits 2 on usage/IO error.
 */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "gen.h"

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "usage: %s <subject-file> <iters>\n",
                argc > 0 ? argv[0] : "eng_pcrec");
        return 2;
    }

    const char *path = argv[1];
    char *end = NULL;
    long iters = strtol(argv[2], &end, 10);
    if (end == argv[2] || iters <= 0) {
        fprintf(stderr, "eng_pcrec: iters must be a positive integer, got '%s'\n",
                argv[2]);
        return 2;
    }

    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); return 2; }
    if (fseek(f, 0, SEEK_END) != 0) { perror(path); fclose(f); return 2; }
    long fsize = ftell(f);
    if (fsize < 0) { perror(path); fclose(f); return 2; }
    if (fseek(f, 0, SEEK_SET) != 0) { perror(path); fclose(f); return 2; }

    size_t n = (size_t)fsize;
    unsigned char *buf = malloc(n > 0 ? n : 1);
    if (!buf) {
        fprintf(stderr, "eng_pcrec: out of memory (%zu bytes)\n", n);
        fclose(f);
        return 2;
    }

    size_t got = fread(buf, 1, n, f);
    fclose(f);
    if (got != n) {
        fprintf(stderr, "eng_pcrec: short read on %s (%zu of %zu bytes)\n",
                path, got, n);
        free(buf);
        return 2;
    }

    rx_span m;
    m.start = 0;
    m.end = 0;
    int found = rx_search(buf, n, 0, &m); /* untimed warmup, see header */

    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < iters; i++) {
        found = rx_search(buf, n, 0, &m);
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    free(buf);

    double secs = (double)(t1.tv_sec - t0.tv_sec) +
                  (double)(t1.tv_nsec - t0.tv_nsec) / 1e9;
    double mb = ((double)n * (double)iters) / (1024.0 * 1024.0);
    double mbps = secs > 0.0 ? mb / secs : 0.0;

    printf("status=ok bytes=%zu iters=%ld secs=%.6f mbps=%.3f match=%d start=%zu end=%zu\n",
           n, iters, secs, mbps, found,
           found ? m.start : (size_t)0, found ? m.end : (size_t)0);
    return 0;
}
