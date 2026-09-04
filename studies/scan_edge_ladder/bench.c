/* edge2 ladder/floor timing driver.  One artifact per arm, driven through the
 * spec 3.1 find-all loop over a subject read from a file.  Prints ns/byte.
 *
 * The subject is a NEAR-MISS corpus: the machine must ENTER the rung's own
 * chain and LEAVE it without completing a match, which is the entry cost this
 * row is about.  A rung whose subject never enters the chain measures nothing
 * and the harness refuses it (see the ENTRY FLOOR in run_ladder.sh). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <time.h>
int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
static double now(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t); return t.tv_sec+1e-9*t.tv_nsec; }
int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: bench SUBJECTFILE SWEEPS\n"); return 2; }
    FILE *f = fopen(argv[1], "rb"); if (!f) { perror("open"); return 2; }
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc((size_t)n + 1);
    if (fread(s, 1, (size_t)n, f) != (size_t)n) { fprintf(stderr,"short read\n"); return 2; }
    fclose(f);
    int sweeps = atoi(argv[2]);
    ptrdiff_t caps[64][2];
    long hits = 0;
    /* one untimed warm sweep */
    for (size_t from = 0; from <= (size_t)n; ) {
        if (rx_search(s, (size_t)n, from, caps) <= 0) break;
        from = (size_t)caps[0][1] > from ? (size_t)caps[0][1] : from + 1;
    }
    double t0 = now();
    for (int k = 0; k < sweeps; k++)
        for (size_t from = 0; from <= (size_t)n; ) {
            if (rx_search(s, (size_t)n, from, caps) <= 0) break;
            hits++;
            from = (size_t)caps[0][1] > from ? (size_t)caps[0][1] : from + 1;
        }
    double el = now() - t0;
    printf("%.6f %ld\n", el * 1e9 / ((double)n * sweeps), hits);
    free(s);
    return 0;
}
