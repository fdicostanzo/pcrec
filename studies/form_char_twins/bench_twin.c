/* form0 -- timing driver for the form_char_twins hand-twins (Family B/C/D).
 * Modelled on studies/scan_edge_ladder/bench.c: spec 3.1 find-all loop over
 * a subject read from a file, one warm untimed sweep then SWEEPS timed
 * sweeps. Reports ns/call, ns/byte, hit count and a checksum (so the
 * harness can compare arms/rounds without re-deriving positions by hand).
 *
 * The search entry point is selected at compile time via RX_SEARCH
 * (-DRX_SEARCH=rxG_search etc.) so this one driver serves every twin --
 * every artifact it links against is generated WITHOUT --emit-main
 * (timing_base directory), so there is no main()/argv[1] conflict with
 * this file's own main.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <time.h>

#ifndef RX_SEARCH
#error "compile with -DRX_SEARCH=<prefix>_search"
#endif

int RX_SEARCH(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);

static double now(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + 1e-9 * t.tv_nsec;
}

int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: bench_twin SUBJECTFILE SWEEPS\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("open"); return 2; }
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc((size_t)n + 1);
    if (fread(s, 1, (size_t)n, f) != (size_t)n) { fprintf(stderr, "short read\n"); return 2; }
    fclose(f);
    int sweeps = atoi(argv[2]);
    ptrdiff_t caps[64][2];

    /* one untimed warm sweep */
    for (size_t from = 0; from <= (size_t)n; ) {
        if (RX_SEARCH(s, (size_t)n, from, caps) <= 0) break;
        from = (size_t)caps[0][1] > from ? (size_t)caps[0][1] : from + 1;
    }

    long hits = 0, calls = 0;
    unsigned long long checksum = 0;
    double t0 = now();
    for (int k = 0; k < sweeps; k++) {
        for (size_t from = 0; from <= (size_t)n; ) {
            int rc = RX_SEARCH(s, (size_t)n, from, caps);
            calls++;
            if (rc <= 0) break;
            hits++;
            /* fold start/end into a running checksum -- catches "same hit
             * count, different positions" the way isl1's protocol requires */
            checksum = checksum * 1000003ULL
                     + (unsigned long long)(caps[0][0] + 1)
                     + (unsigned long long)(caps[0][1] + 1) * 7919ULL;
            from = (size_t)caps[0][1] > from ? (size_t)caps[0][1] : from + 1;
        }
    }
    double el = now() - t0;
    printf("%.6f %.6f %ld %ld %llu\n",
           el * 1e9 / (double)calls,          /* ns/call */
           el * 1e9 / ((double)n * sweeps),   /* ns/byte */
           hits, calls, checksum);
    free(s);
    return 0;
}
