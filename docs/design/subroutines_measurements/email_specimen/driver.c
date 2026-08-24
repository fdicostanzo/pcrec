/* driver.c -- generic match-check driver for a pcrec-generated artifact.
 * Parameterized at compile time via -DHDR='"artifact.h"' -DSEARCH=prefix_search
 * -DNCAPS=PREFIX_NCAPS. Reads the whole subject from a file (argv[1], raw
 * bytes, no escape decoding -- avoids shell/argv escaping entirely so
 * pathological/binary subjects work unmodified), calls SEARCH once at
 * startpos (argv[2], default 0), and prints:
 *   "match %td %td\n"  -- whole-match span
 *   "nomatch\n"
 *   "giveup %d\n"       -- any negative return other than a plain fail
 * exit 0 for match/nomatch, 3 for giveup, 2 for usage/IO error.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stddef.h>

#include HDR

int main(int argc, char **argv) {
    if (argc < 2 || argc > 3) {
        fprintf(stderr, "usage: %s subjectfile [startpos]\n", argc > 0 ? argv[0] : "driver");
        return 2;
    }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("fopen"); return 2; }
    if (fseek(f, 0, SEEK_END) != 0) { perror("fseek"); return 2; }
    long sz = ftell(f);
    if (sz < 0) { perror("ftell"); return 2; }
    if (fseek(f, 0, SEEK_SET) != 0) { perror("fseek"); return 2; }
    unsigned char *buf = malloc(sz > 0 ? (size_t)sz : 1);
    if (!buf) { fprintf(stderr, "driver: out of memory\n"); return 2; }
    if (sz > 0 && fread(buf, 1, (size_t)sz, f) != (size_t)sz) {
        fprintf(stderr, "driver: short read\n");
        return 2;
    }
    fclose(f);

    size_t startpos = 0;
    if (argc == 3) startpos = (size_t)strtoull(argv[2], NULL, 10);

    ptrdiff_t caps[NCAPS][2];
    int found = SEARCH(buf, (size_t)sz, startpos, caps);
    int rc;
    if (found == 1) {
        printf("match %td %td\n", caps[0][0], caps[0][1]);
        rc = 0;
    } else if (found == 0) {
        printf("nomatch\n");
        rc = 0;
    } else {
        printf("giveup %d\n", found);
        rc = 3;
    }
    free(buf);
    return rc;
}
