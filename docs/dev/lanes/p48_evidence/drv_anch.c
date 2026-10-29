/* p48 break-even driver: rx_match (anchored) at every 'x' of the subject, ITERS times. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb"); if (!f) return 2;
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc((size_t)n + 1);
    if (fread(b, 1, (size_t)n, f) != (size_t)n) return 2;
    fclose(f);
    long iters = atol(argv[2]); long tot = 0, calls = 0;
    size_t *at = malloc(sizeof(size_t) * (size_t)n); size_t na = 0;
    for (long i = 0; i < n; i++) if (b[i] == 'x') at[na++] = (size_t)i;
    rx_ctx c; memset(&c, 0, sizeof c); c.subject = b; c.len = (size_t)n;
    for (long it = 0; it < iters; it++)
        for (size_t k = 0; k < na; k++) { c.pos = at[k]; tot += rx_match(&c); calls++; }
    printf("%ld %ld\n", tot, calls);
    return 0;
}
