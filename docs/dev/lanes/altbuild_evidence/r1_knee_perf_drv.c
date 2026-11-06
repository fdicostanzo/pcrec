#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include "k.h"
int main(int argc, char **argv)
{
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 2;
    fseek(f, 0, SEEK_END); long n = ftell(f); rewind(f);
    unsigned char *b = malloc((size_t)n);
    if (fread(b, 1, (size_t)n, f) != (size_t)n) return 2;
    int reps = atoi(argv[2]);
    long cnt = 0;
    ptrdiff_t sp[1][2];
    for (int r = 0; r < reps; r++) {
        size_t pos = 0;
        while (pos <= (size_t)n) {
            if (rx_search(b, (size_t)n, pos, sp) <= 0) break;
            cnt++;
            pos = sp[0][1] > sp[0][0] ? (size_t)sp[0][1] : (size_t)sp[0][0] + 1;
        }
    }
    printf("%ld\n", cnt);
    return 0;
}
