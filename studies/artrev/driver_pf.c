/* driver_pf.c -- [ARTREV] window-start differential of ONE arm.
 *
 *   driver_pf SUBJECTS.bin
 * For every subject and every search_from (all of them up to 20000 bytes, every
 * 7th above, plus the end) prints `W idx from rc start`: what the artifact's own
 * internal prefilter returns and the window START it proposes.  Two arms must
 * print byte-identical transcripts.  A start that is too EARLY is invisible to
 * answer identity (the verifying attempt retries and the answer comes out the
 * same) and shows up only as work or as a livelock -- lane rvA09's L4 r2 "early"
 * control hung the identity driver for its whole 900 s timeout.  Needs an
 * artifact with a `static int <p>_prefilter(...)`; identity.py builds this
 * driver only for such artifacts (-DARTREV_HAVE_PF=1).
 */
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include "artrev_abi.h"

int main(int argc, char **argv)
{
    if (argc < 2) { fprintf(stderr, "usage: driver_pf subjects.bin\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("subjects"); return 2; }
    uint32_t ns;
    if (fread(&ns, 4, 1, f) != 1) return 2;
    for (uint32_t i = 0; i < ns; i++) {
        uint32_t n;
        if (fread(&n, 4, 1, f) != 1) return 2;
        unsigned char *s = malloc(n ? n : 1);        /* exact-length heap copy: ASan sees overreads */
        if (n && fread(s, 1, n, f) != n) return 2;
        size_t step = n > 20000 ? 7 : 1;
        for (size_t from = 0; from <= n; from += step) {
            ptrdiff_t w[1][2] = { { -9, -9 } };
            int rc = art_pf(s, n, from, w);
            printf("W\t%u\t%zu\t%d\t%td\n", i, from, rc, rc == 1 ? w[0][0] : (ptrdiff_t)-9);
        }
        free(s);
    }
    return 0;
}
