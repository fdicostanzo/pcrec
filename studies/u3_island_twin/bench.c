/* bench.c -- ns/char of every arm's P_search, find-all over one subject.
 *
 * House protocol (studies/cls_tree_study/bench.py, docs/dev/lanes/isl1_report.md
 * s12): ROUNDS rounds, arms INTERLEAVED round by round (start arm rotated each
 * round so no arm always runs first), every round's answer checksummed
 * (match count + positional sum) so a timing run that stops measuring the
 * right answer reports nothing.  arms_gen.h names the arms.
 *
 *   bench SUBJECT.bin REPS ROUNDS
 * prints `arm round ns_per_char matches checksum`.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>
#include <time.h>
#include "arms_gen.h"

static double now_s(void)
{ struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return (double)t.tv_sec + 1e-9 * (double)t.tv_nsec; }

static unsigned long run_one(sfn fn, const unsigned char *s, size_t n, unsigned long *cnt)
{
    size_t pos = 0;
    unsigned long c = 0, sum = 0;
    for (;;) {
        ptrdiff_t caps[1][2];
        int rc = fn(s, n, pos, caps);
        if (rc != 1) break;
        c++;
        sum = sum * 1000003UL + (unsigned long)caps[0][0] * 31UL + (unsigned long)caps[0][1];
        pos = (size_t)caps[0][1];
        if (caps[0][1] == caps[0][0]) { pos++; while (pos < n && (s[pos] & 0xC0) == 0x80) pos++; }
        if (pos > n) break;
    }
    *cnt = c;
    return sum;
}

int main(int argc, char **argv)
{
    if (argc < 4) { fprintf(stderr, "usage: bench SUBJECT REPS ROUNDS\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    fseek(f, 0, SEEK_END); long fl = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc((size_t)fl + 64);
    if (fread(s, 1, (size_t)fl, f) != (size_t)fl) return 2;
    fclose(f);
    size_t n = (size_t)fl;
    size_t chars = 0;
    for (size_t i = 0; i < n; i++) chars += ((s[i] & 0xC0) != 0x80);
    int reps = atoi(argv[2]), rounds = atoi(argv[3]);
    /* warm every arm once (page in tables) and fix the reference checksum */
    unsigned long refsum = 0, refcnt = 0;
    for (int a = 0; a < NARMS; a++) {
        unsigned long c, sum = run_one(arms[a].fn, s, n, &c);
        if (a == 0) { refsum = sum; refcnt = c; }
        else if (sum != refsum || c != refcnt) {
            fprintf(stderr, "ANSWER MISMATCH: arm %s count=%lu sum=%lu vs %s count=%lu sum=%lu\n",
                    arms[a].name, c, sum, arms[0].name, refcnt, refsum);
            return 3;
        }
    }
    if (reps <= 0) {   /* auto: about 80 ms per timed unit, from arm 0's median of three passes */
        double t[3];
        for (int i = 0; i < 3; i++) { unsigned long c; double t0 = now_s(); run_one(arms[0].fn, s, n, &c); t[i] = now_s() - t0; }
        double m = t[0] < t[1] ? (t[1] < t[2] ? t[1] : (t[0] < t[2] ? t[2] : t[0])) : (t[0] < t[2] ? t[0] : (t[1] < t[2] ? t[2] : t[1]));
        reps = (int)(0.08 / (m > 1e-6 ? m : 1e-6));
        if (reps < 1) reps = 1;
        if (reps > 400) reps = 400;
    }
    fprintf(stdout, "#subject bytes=%zu chars=%zu reps=%d rounds=%d matches=%lu\n", n, chars, reps, rounds, refcnt);
    for (int r = 0; r < rounds; r++) {
        for (int k = 0; k < NARMS; k++) {
            int a = (k + r) % NARMS;
            unsigned long c = 0, sum = 0;
            double t0 = now_s();
            for (int i = 0; i < reps; i++) sum = run_one(arms[a].fn, s, n, &c);
            double el = now_s() - t0;
            if (sum != refsum || c != refcnt) { fprintf(stderr, "ANSWER DRIFT in arm %s round %d\n", arms[a].name, r); return 3; }
            printf("%s\t%d\t%.4f\t%lu\t%lu\n", arms[a].name, r, 1e9 * el / ((double)reps * (double)chars), c, sum);
            fflush(stdout);
        }
    }
    return 0;
}
