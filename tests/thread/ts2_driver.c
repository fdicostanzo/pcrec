/*
 * tests/thread/ts2_driver.c -- [TS-2] concurrency test for GENERATED code.
 *
 * Compiled together with one gen.c/gen.h pair (produced by
 * `pcrec -p rx -o <dir>/gen.c -- PATTERN`, same fixed prefix convention
 * bdriver.c uses) and a per-pattern "subjects.inc" that defines:
 *
 *   static const char *const subjects[];
 *
 * This file always does `#include "gen.h"` and `#include "subjects.inc"` --
 * see run_thread_tests.sh, which generates both per pattern and always uses
 * the fixed basename "gen" so this driver never has to know the pattern or
 * prefix (same convention as tests/bench/bdriver.c).
 *
 * WHAT IT PROVES. TS-2 asks whether N threads calling <prefix>_search()
 * concurrently over the SAME compiled matcher, on DIFFERENT subjects, ever
 * produce a result that disagrees with a single-threaded run -- established
 * empirically under ThreadSanitizer rather than by reading the emitter. The
 * baseline is computed once, single-threaded, BEFORE any thread is spawned;
 * every threaded call is then checked against that recorded (found, start,
 * end) triple.
 *
 * WHY THIS DRIVER ITSELF CANNOT BE THE SOURCE OF A RACE REPORT. If it were,
 * a TSan warning here would be ambiguous -- generated code, or harness bug?
 * So the harness is built to have no shared mutable state at all:
 *   - `subjects[]` and `baseline[]` are written once, single-threaded,
 *     before pthread_create, and only READ during the threaded phase.
 *   - each ThreadArg's `mismatches` field is written ONLY by the thread that
 *     owns it and read by main only after pthread_join -- no two threads
 *     ever touch the same ThreadArg.
 * The only thing genuinely shared and concurrently exercised across threads
 * is the generated matcher's code and read-only tables (rodata), which is
 * exactly the property under test. See CLAUDE.md's sabotage validation for
 * a build where this property is deliberately broken, to prove the harness
 * would notice.
 *
 * Usage: ts2 [nthreads] [iters_per_thread]  (defaults: 8, 300)
 * Prints exactly one line to stdout and exits 0 iff every threaded call
 * agreed with the single-threaded baseline:
 *   subjects=<n> threads=<t> iters_per_thread=<i> mismatches=<m>
 */

#include "gen.h"
#include "subjects.inc"

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NSUBJ (sizeof(subjects) / sizeof(subjects[0]))

typedef struct { int found; size_t start, end; } Result;
static Result baseline[NSUBJ];   /* written once, single-threaded, before spawn */

typedef struct {
    long iters;
    long mismatches;   /* written only by the thread that owns this struct */
} ThreadArg;

static void *worker(void *argp)
{
    ThreadArg *ta = (ThreadArg *)argp;
    for (long it = 0; it < ta->iters; it++) {
        for (size_t i = 0; i < NSUBJ; i++) {
            rx_span m; m.start = 0; m.end = 0;
            size_t n = strlen(subjects[i]);
            int found = rx_search((const unsigned char *)subjects[i], n, 0, &m);
            if (found != baseline[i].found ||
                (found && (m.start != baseline[i].start || m.end != baseline[i].end)))
                ta->mismatches++;
        }
    }
    return NULL;
}

int main(int argc, char **argv)
{
    int nthreads = argc > 1 ? atoi(argv[1]) : 8;
    long iters   = argc > 2 ? atol(argv[2]) : 300;
    if (nthreads < 1 || iters < 1) {
        fprintf(stderr, "usage: %s [nthreads] [iters_per_thread]\n", argv[0]);
        return 2;
    }

    for (size_t i = 0; i < NSUBJ; i++) {
        rx_span m; m.start = 0; m.end = 0;
        size_t n = strlen(subjects[i]);
        baseline[i].found = rx_search((const unsigned char *)subjects[i], n, 0, &m);
        baseline[i].start = m.start;
        baseline[i].end   = m.end;
    }

    pthread_t *tids = malloc((size_t)nthreads * sizeof(pthread_t));
    ThreadArg *args = calloc((size_t)nthreads, sizeof(ThreadArg));
    if (!tids || !args) { fprintf(stderr, "ts2_driver: out of memory\n"); return 2; }

    for (int t = 0; t < nthreads; t++) {
        args[t].iters = iters;
        args[t].mismatches = 0;
        if (pthread_create(&tids[t], NULL, worker, &args[t]) != 0) {
            fprintf(stderr, "ts2_driver: pthread_create failed\n");
            return 2;
        }
    }
    long total_mismatches = 0;
    for (int t = 0; t < nthreads; t++) {
        pthread_join(tids[t], NULL);
        total_mismatches += args[t].mismatches;
    }
    free(tids); free(args);

    printf("subjects=%zu threads=%d iters_per_thread=%ld mismatches=%ld\n",
           NSUBJ, nthreads, iters, total_mismatches);
    return total_mismatches != 0 ? 1 : 0;
}
