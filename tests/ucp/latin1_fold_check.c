/* latin1_fold_check.c — [UCP] U1's byte-tier FOLD, checked as a RELATION
 * (docs/design/ucp_design.md §7 a4; stage 4's exhaustive-relation method).
 *
 * Under PCRE2_UCP without PCRE2_UTF, `(?i)` folds the 26 ASCII and 30 Latin-1
 * letter pairs (§1.5). pcrec's `pcrec_fold_latin1` (src/core/fold.c) DERIVES
 * that relation from the Unicode simple-fold table restricted to Latin-1; the
 * oracle is `latin1_fold_10.46.tsv` in this directory — libpcre2 10.46's own
 * answer over all 256 x 256 byte pairs, captured once from the reference box
 * (the file's own header line), a source the fold table did not come from.
 *
 * For every byte x, the partner set pcrec computes for {x} must equal the
 * row the oracle recorded (a byte with no row has no partner). Prints PASS/
 * FAIL lines; exits nonzero on any disagreement. Usage: latin1_fold_check TSV */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

int main(int argc, char **argv)
{
    if (argc != 2) { fprintf(stderr, "usage: %s ORACLE.tsv\n", argv[0]); return 2; }
    FILE *f = fopen(argv[1], "r");
    if (!f) { perror(argv[1]); return 2; }
    static unsigned char want[256][256];
    char line[2048];
    int nrows = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == '#' || line[0] == '\n') continue;
        unsigned x;
        char *p = line;
        if (sscanf(p, "%x", &x) != 1 || x > 255) { fprintf(stderr, "bad row: %s", line); return 2; }
        p = strchr(p, '\t');
        while (p && *p) {
            unsigned y; int used;
            if (sscanf(p, " %x%n", &y, &used) != 1) break;
            want[x][y & 0xFF] = 1;
            p += used;
        }
        nrows++;
    }
    fclose(f);
    if (nrows == 0) { printf("FAIL: latin1 fold: oracle file has no rows\n"); return 1; }

    Arena ar = { NULL, NULL };
    int bad = 0, pairs = 0;
    for (unsigned x = 0; x < 256; x++) {
        PcrecCpSet in, out;
        pcrec_cpset_init(&in, &ar);
        pcrec_cpset_init(&out, &ar);
        pcrec_cpset_add(&in, x, x);
        pcrec_fold_latin1.partners(&in, &out);
        for (unsigned y = 0; y < 256; y++) {
            int got = y != x && pcrec_cpset_has(&out, y);
            if (got) pairs++;
            if (got != want[x][y]) {
                if (bad++ < 10)
                    printf("FAIL: latin1 fold: %02x ~ %02x: pcrec %s, libpcre2 10.46 %s\n",
                           x, y, got ? "yes" : "no", want[x][y] ? "yes" : "no");
            }
        }
        for (int i = 0; i < out.n; i++)
            if (out.iv[i].hi > 0xFF) {
                printf("FAIL: latin1 fold: %02x has a partner above 0xFF\n", x);
                bad++;
            }
    }
    pcrec_arena_free(&ar);
    if (bad) { printf("FAIL: latin1 fold: %d disagreements over 256x256\n", bad); return 1; }
    printf("PASS: latin1 fold: pcrec_fold_latin1 == libpcre2 10.46 UCP|CASELESS over "
           "all 256x256 byte pairs (%d partner pairs, %d oracle rows)\n", pairs, nrows);
    return 0;
}
