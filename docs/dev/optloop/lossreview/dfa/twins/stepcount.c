/* stepcount.c — find-all over subjects with a mk_count.py artifact; prints
 * per subject: bytes, calls, matches, skip entries, skipped bytes, seeds,
 * forward steps. No clock. Build: gcc -O2 -I. stepcount.c CNT.c */
#include <stdio.h>
#include <stdlib.h>
#include RXH
extern unsigned long long lr_entries, lr_skipped, lr_seeds, lr_steps;
int main(int argc, char **argv)
{
    unsigned long long B = 0, C = 0, M = 0, E = 0, S = 0, D = 0, T = 0;
    for (int i = 1; i < argc; i++) {
        FILE *f = fopen(argv[i], "rb"); fseek(f, 0, SEEK_END); long n = ftell(f); rewind(f);
        unsigned char *b = malloc(n + 1); if (fread(b, 1, n, f) != (size_t)n) return 2; fclose(f);
        ptrdiff_t caps[64][2]; size_t pos = 0; lr_entries = lr_skipped = lr_seeds = lr_steps = 0;
        unsigned long long calls = 0, m = 0;
        for (;;) { int r = rx_search(b, n, pos, caps); calls++; if (r != 1) break; m++;
            size_t s = caps[0][0], e = caps[0][1]; pos = e > s ? e : s + 1; if (pos > (size_t)n) break; }
        B += n; C += calls; M += m; E += lr_entries; S += lr_skipped; D += lr_seeds; T += lr_steps; free(b);
    }
    printf("bytes=%llu calls=%llu matches=%llu entries=%llu (%.3f/B) skipped=%.3f/B mean_skip=%.2f seeds=%llu steps=%.3f/B\n",
           B, C, M, E, (double)E / B, (double)S / B, E ? (double)S / E : 0, D, (double)T / B);
    return 0;
}
