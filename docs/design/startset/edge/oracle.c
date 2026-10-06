/* [START-SET] edge lane (ssedge): the libpcre2 ORACLE for the edge cells.
 * Built against whichever libpcre2-8 is local: the Mac's 10.48 (Homebrew)
 * and, over ssh, the 10.46 reference on ubuntubudu.  No pcrec code.
 *
 * In (stdin), one question per line, TAB-separated:
 *     key  opts  pattern_hex  subject_hex  startpos
 * opts letters: i PCRE2_CASELESS, u PCRE2_UCP, U PCRE2_UTF|PCRE2_MATCH_INVALID_UTF
 * (pcrec -e utf8's semantics: ill-formed bytes never match, never refuse),
 * C PCRE2_UTF with checking ON (pcrec -e utf8 -futf-check's semantics),
 * '-' none.
 * Out: a header line `# pcre2 <version>`, then per question
 *     key  rc  s0 e0 s1 e1 ...       (rc: 1 match, 0 no match, `utf` a
 * UTF-8 error code, `badoffset`, `cfail:<code>` compile failure, `err:<rc>`
 * anything else; -1 -1 for an unset group). */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static size_t unhex(const char *h, unsigned char *o)
{
    size_t n = strlen(h) / 2;
    for (size_t i = 0; i < n; i++) { unsigned v; sscanf(h + 2 * i, "%2x", &v); o[i] = (unsigned char)v; }
    return n;
}

int main(void)
{
    char ver[64]; pcre2_config(PCRE2_CONFIG_VERSION, ver);
    printf("# pcre2 %s\n", ver);
    static char line[1 << 16];
    static unsigned char pat[1 << 14], subj[1 << 14];
    char lastkey[1 << 15] = ""; pcre2_code *re = NULL; pcre2_match_data *md = NULL; int cerr = 0;
    while (fgets(line, sizeof line, stdin)) {
        size_t L = strlen(line); if (L && line[L - 1] == '\n') line[--L] = 0;
        char *f[5]; int k = 0; char *p = line;
        for (; k < 5; k++) { f[k] = p; char *t = strchr(p, '\t'); if (!t) { k++; break; } *t = 0; p = t + 1; }
        if (k < 5) continue;
        char ck[1 << 15]; snprintf(ck, sizeof ck, "%s|%s", f[1], f[2]);
        if (strcmp(ck, lastkey)) {
            if (md) pcre2_match_data_free(md); if (re) pcre2_code_free(re); md = NULL; re = NULL;
            strcpy(lastkey, ck);
            uint32_t o = 0;
            if (strchr(f[1], 'i')) o |= PCRE2_CASELESS;
            if (strchr(f[1], 'u')) o |= PCRE2_UCP;
            if (strchr(f[1], 'U')) o |= PCRE2_UTF | PCRE2_MATCH_INVALID_UTF;
            if (strchr(f[1], 'C')) o |= PCRE2_UTF;
            size_t pn = unhex(f[2], pat); PCRE2_SIZE eo;
            re = pcre2_compile(pat, pn, o, &cerr, &eo, NULL);
            if (re) md = pcre2_match_data_create_from_pattern(re, NULL);
        }
        if (!re) { printf("%s\tcfail:%d\n", f[0], cerr); continue; }
        size_t n = unhex(f[3], subj); size_t sp = strtoul(f[4], NULL, 10);
        int rc = pcre2_match(re, subj, n, sp, 0, md, NULL);
        if (rc == PCRE2_ERROR_NOMATCH) { printf("%s\t0\n", f[0]); continue; }
        if (rc <= PCRE2_ERROR_UTF8_ERR1 && rc >= PCRE2_ERROR_UTF8_ERR21) { printf("%s\tutf\n", f[0]); continue; }
        if (rc == PCRE2_ERROR_BADUTFOFFSET) { printf("%s\tbadoffset\n", f[0]); continue; }
        if (rc < 0) { printf("%s\terr:%d\n", f[0], rc); continue; }
        PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
        uint32_t np = pcre2_get_ovector_count(md), cap; pcre2_pattern_info(re, PCRE2_INFO_CAPTURECOUNT, &cap);
        printf("%s\t1", f[0]);
        for (uint32_t g = 0; g <= cap && g < np; g++) {
            if (ov[2 * g] == PCRE2_UNSET) printf(" -1 -1");
            else printf(" %zu %zu", (size_t)ov[2 * g], (size_t)ov[2 * g + 1]);
        }
        printf("\n");
    }
    return 0;
}
