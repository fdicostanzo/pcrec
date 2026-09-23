/* [OPT-FIRSTSET] §4.5 — THE WITNESS DRIVER (lane fsreconcile, 2026-09-22).
 *
 * One subject per line of argv[1] (trailing newline stripped, no escape
 * vocabulary -- the witness set is ASCII by construction), run through the
 * artifact's own find-all loop, every SPAN printed.  Spans and not just a
 * count, because the question §4.5 asks has three possible answers and a
 * count separates only two of them: a LOST match, a SPURIOUS match, and a
 * match reported at the wrong span.
 *
 * ANSWERS ONLY.  Nothing here reads a clock -- this lane ran on darwin,
 * where D119's own mechanics rule timing uncitable.
 *
 * Build:  gcc -O2 -I<dir> -o <out> firstset_witness.c <artifact>.c
 *         with <dir>/art.h a copy of the artifact's own header. */
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include "art.h"

/* The artifact's emitted prefix is a BUILD parameter: the three variants are
 * emitted at three different `-p` values so they can also be linked together
 * by `firstset_exhaust.c`, and this driver takes whichever one it is given. */
#ifndef ART_SEARCH
# define ART_SEARCH rx_search
#endif
#ifndef ART_NCAPS
# define ART_NCAPS  RX_NCAPS
#endif

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "usage: %s SUBJECTS\n", argv[0]); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { fprintf(stderr, "cannot open %s\n", argv[1]); return 2; }
    char line[4096];
    while (fgets(line, sizeof line, f)) {
        size_t n = strlen(line);
        while (n && (line[n-1] == '\n' || line[n-1] == '\r')) line[--n] = 0;
        const unsigned char *b = (const unsigned char *)line;
        ptrdiff_t caps[ART_NCAPS][2];
        size_t pos = 0; long count = 0;
        printf("[%s]\t", line);
        for (;;) {
            int r = ART_SEARCH(b, n, pos, caps);
            if (r == 0) break;
            if (r < 0) { printf("giveup(%d) ", r); break; }
            size_t s = (size_t)caps[0][0], e = (size_t)caps[0][1];
            printf("(%zu,%zu) ", s, e);
            count++;
            pos = (e > s) ? e : s + 1;
            if (pos > n) break;
        }
        printf("\tmatches=%ld\n", count);
    }
    fclose(f);
    return 0;
}
