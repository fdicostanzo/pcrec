/* pcre2_ref.c -- [ARTREV] libpcre2 answers for the SAME subjects/cases files
 * driver_id reads, in driver_id's own `S` line format (point cases only).
 *   pcre2_ref SUBJECTS.bin CASES.tsv NCAPS 'PATTERN-BYTES-FILE' FLAGS
 * FLAGS: letters i (caseless), u (UTF), c (UCP).  Prints `S idx from rc caps..`
 * with rc 1/0 or the pcre2 error code, unset groups -1.  Compile:
 *   cc pcre2_ref.c -DPCRE2_CODE_UNIT_WIDTH=8 -I<prefix>/include -L<prefix>/lib -lpcre2-8
 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdint.h>

int main(int argc, char **argv)
{
    if (argc < 6) { fprintf(stderr, "usage\n"); return 2; }
    FILE *f = fopen(argv[1], "rb"); if (!f) return 2;
    uint32_t ns; if (fread(&ns, 4, 1, f) != 1) return 2;
    unsigned char **subj = malloc((ns ? ns : 1) * sizeof *subj); uint32_t *slen = malloc((ns ? ns : 1) * sizeof *slen);
    for (uint32_t i = 0; i < ns; i++) {
        if (fread(&slen[i], 4, 1, f) != 1) return 2;
        subj[i] = malloc(slen[i] + 1);
        if (slen[i] && fread(subj[i], 1, slen[i], f) != slen[i]) return 2;
    }
    fclose(f);
    int ncaps = atoi(argv[3]);
    FILE *pf = fopen(argv[4], "rb"); if (!pf) return 2;
    unsigned char pat[65536]; size_t pl = fread(pat, 1, sizeof pat, pf); fclose(pf);
    uint32_t opts = 0;
    for (const char *p = argv[5]; *p; p++) {
        if (*p == 'i') opts |= PCRE2_CASELESS;
        if (*p == 'u') opts |= PCRE2_UTF;
        if (*p == 'c') opts |= PCRE2_UCP;
    }
    int err; PCRE2_SIZE eo;
    pcre2_code *re = pcre2_compile(pat, pl, opts, &err, &eo, NULL);
    if (!re) { fprintf(stderr, "pcre2_compile failed at %zu: %d\n", (size_t)eo, err); return 3; }
    pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
    FILE *c = fopen(argv[2], "r"); if (!c) return 2;
    unsigned idx; size_t from; char mode[8];
    while (fscanf(c, "%u\t%zu\t%7s\n", &idx, &from, mode) == 3) {
        if (mode[0] == 'f') continue;
        int rc = pcre2_match(re, subj[idx], slen[idx], from, 0, md, NULL);
        PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
        printf("S\t%u\t%zu\t%d", idx, from, rc > 0 ? 1 : (rc == PCRE2_ERROR_NOMATCH ? 0 : rc));
        for (int i = 0; i < ncaps; i++) {
            if (rc > 0 && i < rc && ov[2 * i] != PCRE2_UNSET) printf("\t%td\t%td", (ptrdiff_t)ov[2 * i], (ptrdiff_t)ov[2 * i + 1]);
            else if (rc > 0) printf("\t-1\t-1");
            else printf("\t-2\t-2");
        }
        printf("\n");
    }
    return 0;
}
