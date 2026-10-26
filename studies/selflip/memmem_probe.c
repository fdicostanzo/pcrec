/* memmem_probe: find-all of a literal via glibc memmem, as the lower bound for a kit-proven literal span.
   usage: memmem_probe LITERAL FILE ITERS */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[2], "rb"); static unsigned char buf[1 << 21];
    size_t n = fread(buf, 1, sizeof buf, f); fclose(f);
    size_t L = strlen(argv[1]); long it = atol(argv[3]), cnt = 0; double best = 1e18;
    for (int t = 0; t < 7; t++) {
        struct timespec a, b; clock_gettime(CLOCK_MONOTONIC, &a);
        for (long i = 0; i < it; i++) {
            size_t pos = 0; cnt = 0;
            for (;;) { unsigned char *q = memmem(buf + pos, n - pos, argv[1], L); if (!q) break; cnt++; pos = (size_t)(q - buf) + L; }
        }
        clock_gettime(CLOCK_MONOTONIC, &b);
        double ns = ((b.tv_sec - a.tv_sec) * 1e9 + (b.tv_nsec - a.tv_nsec)) / it; if (ns < best) best = ns;
    }
    printf("%.1f ns/findall matches=%ld\n", best, cnt); return 0;
}
