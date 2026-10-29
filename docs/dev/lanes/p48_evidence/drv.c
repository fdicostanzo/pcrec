/* p48 twin driver: find-all over one subject file, ITERS times; the bench's
 * timed.c find-all advance (start+1 on empty, else end). */
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
int main(int argc, char **argv)
{
    if (argc < 3) return 2;
    FILE *f = fopen(argv[1], "rb"); if (!f) return 2;
    fseek(f, 0, SEEK_END); long n = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc((size_t)n + 1);
    if (fread(b, 1, (size_t)n, f) != (size_t)n) return 2;
    fclose(f);
    long iters = atol(argv[2]), total = 0;
    ptrdiff_t caps[16][2];
    for (long it = 0; it < iters; it++) {
        size_t pos = 0; long count = 0;
        for (;;) {
            int r = rx_search(b, (size_t)n, pos, caps);
            if (r <= 0) break;
            count++;
            size_t st = (size_t)caps[0][0], en = (size_t)caps[0][1];
            pos = en > st ? en : st + 1;
            if (pos > (size_t)n) break;
        }
        total = count;
    }
    printf("%ld\n", total);
    return 0;
}
