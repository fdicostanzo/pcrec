/* [OPT-VMFL] STEP 0 (b): answer-identity driver for a hand-twin.
 * Reads subject files named on argv, runs rx_search once per subject,
 * prints "match start end" or "nomatch" or "giveup N" per line -- one
 * line per subject, in argv order, so two builds (orig vs twin) can be
 * diffed textually. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "csv5_lib.h"

int main(int argc, char **argv)
{
    for (int i = 1; i < argc; i++) {
        FILE *f = fopen(argv[i], "rb");
        if (!f) { fprintf(stderr, "cannot open %s\n", argv[i]); return 2; }
        fseek(f, 0, SEEK_END);
        long n = ftell(f);
        fseek(f, 0, SEEK_SET);
        unsigned char *buf = malloc(n > 0 ? (size_t)n : 1);
        if (n > 0 && fread(buf, 1, (size_t)n, f) != (size_t)n) { fprintf(stderr, "short read\n"); return 2; }
        fclose(f);
        ptrdiff_t capture_spans[RX_NCAPS][2] = {{0}};
        int rc = rx_search(buf, (size_t)n, 0, capture_spans);
        if (rc == 1) printf("match %td %td\n", capture_spans[0][0], capture_spans[0][1]);
        else if (rc == 0) printf("nomatch\n");
        else printf("giveup %d\n", rc);
        free(buf);
    }
    return 0;
}
