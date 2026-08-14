/*
 * tests/thread/ts3_driver.c -- [TS-3] concurrency test for the LIBRARY.
 *
 * Compiled together with every .c file under src/ (built WITH -fsanitize=thread by
 * run_thread_tests.sh, so the library code under test is actually
 * instrumented -- an uninstrumented .a would defeat the point) and linked
 * against lib/pcrec.h's public API.
 *
 * WHAT IT PROVES. Eight threads, each pinned to its OWN pattern (never
 * shared with another thread) call pcrec_compile() in a tight loop. This
 * guards against a future file-scope counter or cache in the compiler --
 * pcrec_compile() is currently designed to be fully self-contained (a
 * stack-local Ctx, an arena malloc'd per call, freed at the end of the
 * call; see src/core/compile.c and src/core/arena.c), so the property this
 * test establishes is that nothing has quietly attached shared mutable
 * state to that pipeline.
 *
 * Six of the eight jobs are patterns that compile; two are patterns the
 * reject table already knows must be refused ('\d' -> module 'classes',
 * '(?=a)' -> module 'lookaround'), to exercise the ctx_fail/longjmp error
 * path under concurrency too -- the jmp_buf and Ctx are both stack-local
 * per call, so this should be equally race-free, and now it is checked
 * rather than assumed. Each thread's SINGLE-THREADED baseline (the exact
 * c_src bytes for an accepting job, or the exact diagnostic for a rejecting
 * one) is captured before any thread is spawned; every threaded compile is
 * then checked for byte-identity against that baseline, so this test also
 * catches non-TSan-visible corruption from a benign race that a given run
 * of TSan might not happen to schedule into a report.
 *
 * WHY THIS DRIVER ITSELF CANNOT BE THE SOURCE OF A RACE REPORT: `jobs[]`
 * and `baseline[]` are populated once, single-threaded, before spawning;
 * each thread only ever reads its own `jobs[idx]`/`baseline[idx]` slot
 * (idx is fixed per thread) and writes only its own ThreadArg.mismatches,
 * which main reads only after pthread_join. See CLAUDE.md's sabotage
 * validation for a build where a real file-scope counter is planted in a
 * COPY of src/core/compile.c, to prove the harness would catch it.
 *
 * Usage: ts3 [iters_per_thread]  (default: 300)
 * Prints exactly one line to stdout and exits 0 iff every threaded compile
 * agreed with its single-threaded baseline:
 *   jobs=<n> iters_per_thread=<i> mismatches=<m>
 */

#include "pcrec.h"

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    const char *pattern;
    const char *prefix;
    int caseless;
    int expect_ok;   /* 1 = must compile, 0 = must be rejected */
} Job;

/* Distinct patterns AND distinct prefixes per job/thread -- the prefix is
 * caller-supplied text baked into every emitted identifier, so varying it
 * per thread also stresses the emitter's use of opt->prefix rather than
 * exercising only one fixed string across all eight threads. */
static const Job jobs[] = {
    { "abc",                  "t0", 0, 1 },
    { "a(b|c)+d",              "t1", 0, 1 },
    { "[a-z]+@[a-z]+",         "t2", 0, 1 },
    { "^abc$",                 "t3", 1, 1 },
    { "cat|dog|bird|catfish",  "t4", 0, 1 },
    { "a{2,4}?",                "t5", 0, 1 },
    { "\\d",                  "t6", 0, 0 },  /* rejected: requires module 'classes' */
    { "(?=a)",                "t7", 0, 0 },  /* rejected: requires module 'lookaround' */
};
#define NJOBS (sizeof(jobs) / sizeof(jobs[0]))

typedef struct {
    char *c_src;         /* baseline output for an accepting job */
    char  err_msg[256];  /* baseline diagnostic for a rejecting job */
} Baseline;
static Baseline baseline[NJOBS];   /* written once, single-threaded, before spawn */

static int run_one(const Job *j, pcrec_output *out, pcrec_error *err)
{
    pcrec_options opt;
    pcrec_default_options(&opt);
    opt.prefix = j->prefix;
    if (j->caseless) opt.flags |= PCREC_CASELESS;
    return pcrec_compile(j->pattern, &opt, out, err);
}

typedef struct {
    int  idx;      /* fixed index into jobs[]/baseline[] -- one thread, one job */
    long iters;
    long mismatches;   /* written only by the thread that owns this struct */
} ThreadArg;

static void *worker(void *argp)
{
    ThreadArg *ta = (ThreadArg *)argp;
    const Job *j = &jobs[ta->idx];
    for (long it = 0; it < ta->iters; it++) {
        pcrec_output out; pcrec_error err;
        int rc = run_one(j, &out, &err);
        int mismatch = 0;
        if (j->expect_ok) {
            if (rc != 0) mismatch = 1;
            else if (!out.c_src || strcmp(out.c_src, baseline[ta->idx].c_src) != 0) mismatch = 1;
        } else {
            if (rc != -1) mismatch = 1;
            else if (strcmp(err.msg, baseline[ta->idx].err_msg) != 0) mismatch = 1;
        }
        if (mismatch) ta->mismatches++;
        if (rc == 0) pcrec_output_free(&out);
    }
    return NULL;
}

int main(int argc, char **argv)
{
    long iters = argc > 1 ? atol(argv[1]) : 300;
    if (iters < 1) { fprintf(stderr, "usage: %s [iters_per_thread]\n", argv[0]); return 2; }

    for (size_t i = 0; i < NJOBS; i++) {
        pcrec_output out; pcrec_error err;
        int rc = run_one(&jobs[i], &out, &err);
        if (jobs[i].expect_ok) {
            if (rc != 0) {
                fprintf(stderr, "ts3_driver: baseline compile of '%s' FAILED unexpectedly: %s\n",
                        jobs[i].pattern, err.msg);
                return 2;
            }
            baseline[i].c_src = strdup(out.c_src);
            pcrec_output_free(&out);
        } else {
            if (rc != -1) {
                fprintf(stderr, "ts3_driver: baseline compile of '%s' SUCCEEDED unexpectedly\n",
                        jobs[i].pattern);
                if (rc == 0) pcrec_output_free(&out);
                return 2;
            }
            strncpy(baseline[i].err_msg, err.msg, sizeof(baseline[i].err_msg) - 1);
        }
    }

    pthread_t tids[NJOBS];
    ThreadArg args[NJOBS];
    for (size_t i = 0; i < NJOBS; i++) {
        args[i].idx = (int)i;
        args[i].iters = iters;
        args[i].mismatches = 0;
        if (pthread_create(&tids[i], NULL, worker, &args[i]) != 0) {
            fprintf(stderr, "ts3_driver: pthread_create failed\n");
            return 2;
        }
    }
    long total_mismatches = 0;
    for (size_t i = 0; i < NJOBS; i++) {
        pthread_join(tids[i], NULL);
        total_mismatches += args[i].mismatches;
    }
    for (size_t i = 0; i < NJOBS; i++) free(baseline[i].c_src);

    printf("jobs=%zu iters_per_thread=%ld mismatches=%ld\n", NJOBS, iters, total_mismatches);
    return total_mismatches != 0 ? 1 : 0;
}
