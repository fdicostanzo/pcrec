/* studies/start_landing/guard_timing/driver.c -- [START-LANDING] Q2 (4)'s
 * NO-GUARD TIMING ARM (D156 addendum 4): a find-all over a WELL-FORMED UTF-8
 * subject (argv[1], a file), REPS times, through `on_search`; prints the
 * match count and the median ns per full find-all over ROUNDS rounds. The same
 * driver is linked against the default artifact (the post-loop guard) and a
 * copy with the guard block deleted, so the difference is the guard's cost on
 * the happy path (one decode per reported match, predicted not taken). */
#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "on.h"

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e9 + t.tv_nsec; }
static int cmpd(const void *a, const void *b) { double x = *(const double *)a, y = *(const double *)b; return x < y ? -1 : x > y; }

int main(int argc, char **argv)
{
    if (argc != 4) { fprintf(stderr, "usage: %s SUBJECT REPS ROUNDS\n", argv[0]); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 2;
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc((size_t)n + 1);
    if (!s || fread(s, 1, (size_t)n, f) != (size_t)n) return 2;
    fclose(f);
    int reps = atoi(argv[2]), rounds = atoi(argv[3]);
    double *t = malloc(sizeof(double) * (size_t)rounds);
    long count = 0;
    for (int r = 0; r < rounds; r++) {
        double t0 = now();
        for (int k = 0; k < reps; k++) {
            size_t pos = 0; count = 0;
            while (pos <= (size_t)n) {
                ptrdiff_t caps[ON_NCAPS][2];
                if (on_search(s, (size_t)n, pos, caps) != 1) break;
                count++;
                pos = caps[0][1] > caps[0][0] ? (size_t)caps[0][1] : on_next_pos(s, (size_t)n, (size_t)caps[0][1]);
            }
        }
        t[r] = (now() - t0) / reps;
    }
    qsort(t, (size_t)rounds, sizeof(double), cmpd);
    printf("%ld %.0f\n", count, t[rounds / 2]);
    return 0;
}
