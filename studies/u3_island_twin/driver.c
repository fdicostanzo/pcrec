/* driver.c -- run every arm's P_search over subjects.bin x cases.tsv and print
 * `arm idx from rc start end` rows.  arms_gen.h (written by check.py) names
 * the arms. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>
#include "arms_gen.h"

int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: driver subjects.bin cases.tsv\n"); return 2; }
    FILE *f = fopen(argv[1], "rb");
    if (!f) { perror("subjects"); return 2; }
    uint32_t ns;
    if (fread(&ns, 4, 1, f) != 1) return 2;
    unsigned char **subj = malloc(ns * sizeof *subj);
    uint32_t *len = malloc(ns * sizeof *len);
    for (uint32_t i = 0; i < ns; i++) {
        if (fread(&len[i], 4, 1, f) != 1) return 2;
        subj[i] = malloc(len[i] + 8);
        if (len[i] && fread(subj[i], 1, len[i], f) != len[i]) return 2;
        memset(subj[i] + len[i], 0, 8);
    }
    fclose(f);
    FILE *c = fopen(argv[2], "r");
    if (!c) { perror("cases"); return 2; }
    unsigned idx, from;
    while (fscanf(c, "%u\t%u\n", &idx, &from) == 2) {
        for (int a = 0; a < NARMS; a++) {
            ptrdiff_t caps[4][2] = {{-1, -1}, {-1, -1}, {-1, -1}, {-1, -1}};
            /* a private copy of the exact-length subject so an out-of-bounds read is not hidden by padding */
            unsigned char *copy = malloc(len[idx] ? len[idx] : 1);
            memcpy(copy, subj[idx], len[idx]);
            int rc = arms[a].fn(copy, len[idx], from, caps);
            free(copy);
            printf("%s\t%u\t%u\t%d\t%td\t%td\n", arms[a].name, idx, from, rc,
                   rc == 1 ? caps[0][0] : (ptrdiff_t)-1, rc == 1 ? caps[0][1] : (ptrdiff_t)-1);
        }
    }
    return 0;
}
