/* tests/utfcheck/probe_pcre2.c -- the libpcre2 ORACLE for [UTF-VALID]
 * (docs/design/utf_valid_design.md §7): answers gen_cases.py's questions
 * under PCRE2_UTF with checking ON, the contract `-futf-check` reproduces.
 *
 * NOT built or run by `make test`: it was run ONCE, on ubuntubudu's
 * libpcre2 10.46 (the reference oracle), and its output is the committed
 * cases_10.46.tsv. To re-derive (light: one process, a few thousand calls):
 *
 *   python3 gen_cases.py > q.tsv
 *   cc -O1 -o probe probe_pcre2.c $(pcre2-config --cflags --libs8)
 *   ./probe < q.tsv > cases_<version>.tsv
 *
 * Reads the question TSV on stdin; writes each question line back with five
 * answer columns appended: rc, ovector[0], ovector[1], pcre2_get_startchar
 * (meaningful on a UTF error) and PCRE2_INFO_MAXLOOKBEHIND. A pattern that
 * fails to compile answers rc = "compile". Mode A adds PCRE2_ANCHORED. */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static size_t unhex(const char *h, unsigned char *o)
{
    size_t n = 0;
    if (!strcmp(h, "-")) return 0;
    while (h[0] && h[1]) { unsigned v; sscanf(h, "%2x", &v); o[n++] = (unsigned char)v; h += 2; }
    return n;
}

int main(void)
{
    char line[8192], lastpat[4096] = "";
    pcre2_code *re = NULL;
    pcre2_match_data *md = NULL;
    uint32_t mlb = 0;
    printf("# libpcre2 %d.%d, PCRE2_UTF (checking ON)\n", PCRE2_MAJOR, PCRE2_MINOR);
    while (fgets(line, sizeof line, stdin)) {
        if (line[0] == '#') continue;
        line[strcspn(line, "\n")] = 0;
        char copy[8192];
        strcpy(copy, line);
        char *f[6];
        char *p = copy;
        for (int i = 0; i < 6; i++) { f[i] = p; p = strchr(p, '\t'); if (p) *p++ = 0; else if (i < 5) { f[i+1] = NULL; } }
        if (strcmp(f[1], lastpat) != 0) {
            int err; PCRE2_SIZE eo;
            if (md) pcre2_match_data_free(md);
            if (re) pcre2_code_free(re);
            md = NULL;
            re = pcre2_compile((PCRE2_SPTR)f[1], PCRE2_ZERO_TERMINATED, PCRE2_UTF, &err, &eo, NULL);
            snprintf(lastpat, sizeof lastpat, "%s", f[1]);
            if (re) {
                md = pcre2_match_data_create_from_pattern(re, NULL);
                pcre2_pattern_info(re, PCRE2_INFO_MAXLOOKBEHIND, &mlb);
            }
        }
        if (!re) { printf("%s\tcompile\t-\t-\t-\t-\n", line); continue; }
        unsigned char s[4096];
        size_t n = unhex(f[2], s);
        size_t qpos = strtoul(f[5], NULL, 10);
        int rc = pcre2_match(re, s, n, qpos, f[4][0] == 'A' ? PCRE2_ANCHORED : 0, md, NULL);
        PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
        if (rc >= 0)
            printf("%s\t%d\t%zu\t%zu\t-\t%u\n", line, rc, (size_t)ov[0], (size_t)ov[1], mlb);
        else
            printf("%s\t%d\t-\t-\t%zu\t%u\n", line, rc, (size_t)pcre2_get_startchar(md), mlb);
    }
    return 0;
}
