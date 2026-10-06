/* driver_spans.c -- [ARTREV] the match spans of ONE arm over a subject file (the bench's find-all
 * loop), for `artrev.py variants`:   driver_spans SUBJECT  ->  `start<TAB>end` per match.  */
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include "artrev_abi.h"

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "usage: driver_spans SUBJECT\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror(argv[1]); return 2; }
    fseek(f, 0, SEEK_END); long fl = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc((size_t)fl + 64);
    if (fread(s, 1, (size_t)fl, f) != (size_t)fl) return 2;
    fclose(f);
    size_t n = (size_t)fl, pos = 0;
    ptrdiff_t (*caps)[2] = malloc((size_t)art_ncaps() * sizeof *caps);
    for (;;) {
        int rc = art_search(s, n, pos, caps);
        if (rc != 1) break;
        printf("%td\t%td\n", caps[0][0], caps[0][1]);
        pos = (size_t)caps[0][1];
        if (caps[0][1] == caps[0][0]) pos = art_next_pos(s, n, pos);
        if (pos > n) break;
    }
    return 0;
}
