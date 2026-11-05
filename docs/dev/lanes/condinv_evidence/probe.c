/* condinv probe driver: libpcre2-8 (installed 10.46) as a LIBRARY, options 0.
 * stdin: one case per line, "PATTERN" or "PATTERN<TAB>SUBJECT"; the subject
 * understands \n and \\ only. stdout: the case, then ACCEPT/REJECT (compile
 * only) or NOMATCH / MATCH (s,e) g1=(s,e)|- ... for every capture group.
 * Build: gcc -O1 -o $PCREC_TMPDIR/scratch/condinv/probe probe.c -lpcre2-8 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
int main(void)
{
    char line[8192], subj[8192];
    while (fgets(line, sizeof line, stdin)) {
        size_t n = strlen(line);
        if (n && line[n - 1] == '\n') line[--n] = 0;
        if (n == 0 || line[0] == '#') continue;
        char *tab = strchr(line, '\t');
        size_t plen = tab ? (size_t)(tab - line) : n;
        size_t sl = 0;
        if (tab)
            for (const char *p = tab + 1; *p; p++) {
                if (p[0] == '\\' && p[1] == 'n') { subj[sl++] = '\n'; p++; }
                else if (p[0] == '\\' && p[1] == '\\') { subj[sl++] = '\\'; p++; }
                else subj[sl++] = *p;
            }
        int e; PCRE2_SIZE eo;
        pcre2_code *c = pcre2_compile((PCRE2_SPTR)line, plen, 0, &e, &eo, NULL);
        printf("%.*s\t%s\t", (int)plen, line, tab ? tab + 1 : "");
        if (!c) {
            PCRE2_UCHAR b[256]; pcre2_get_error_message(e, b, sizeof b);
            printf("REJECT %d @%zu %s\n", e, (size_t)eo, (char *)b);
            continue;
        }
        if (!tab) { printf("ACCEPT\n"); pcre2_code_free(c); continue; }
        pcre2_match_data *m = pcre2_match_data_create_from_pattern(c, NULL);
        int r = pcre2_match(c, (PCRE2_SPTR)subj, sl, 0, 0, m, NULL);
        if (r < 0) printf(r == PCRE2_ERROR_NOMATCH ? "NOMATCH\n" : "ERROR %d\n", r);
        else {
            uint32_t cnt = pcre2_get_ovector_count(m);
            PCRE2_SIZE *o = pcre2_get_ovector_pointer(m);
            uint32_t cap; pcre2_pattern_info(c, PCRE2_INFO_CAPTURECOUNT, &cap);
            printf("MATCH (%zu,%zu)", (size_t)o[0], (size_t)o[1]);
            for (uint32_t i = 1; i <= cap && i < cnt; i++) {
                if (o[2 * i] == PCRE2_UNSET) printf(" g%u=-", i);
                else printf(" g%u=(%zu,%zu)", i, (size_t)o[2 * i], (size_t)o[2 * i + 1]);
            }
            for (uint32_t i = cnt; i <= cap; i++) printf(" g%u=-", i);
            printf("\n");
        }
        pcre2_match_data_free(m); pcre2_code_free(c);
    }
    return 0;
}
