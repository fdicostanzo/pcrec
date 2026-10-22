/* libpcre2 reference: argv[1] pattern, argv[2..] subjects; per subject and start
 * position prints "sp=N r=R g..": one line per subject, matching pcdrv.c. */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <string.h>
int main(int argc, char **argv)
{
    int ec; PCRE2_SIZE eo; uint32_t nc;
    pcre2_code *re = pcre2_compile((PCRE2_SPTR)argv[1], PCRE2_ZERO_TERMINATED, 0, &ec, &eo, NULL);
    if (!re) { printf("COMPILE-ERROR\n"); return 0; }
    pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
    pcre2_pattern_info(re, PCRE2_INFO_CAPTURECOUNT, &nc);
    for (int i = 2; i < argc; i++) {
        const unsigned char *s = (const unsigned char *)argv[i]; size_t n = strlen(argv[i]);
        printf("'%s':", argv[i]);
        for (size_t sp = 0; sp <= n; sp++) {
            int r = pcre2_match(re, s, n, sp, 0, md, NULL);
            PCRE2_SIZE *o = pcre2_get_ovector_pointer(md);
            printf(" [%zu:%s", sp, r > 0 ? "" : r == PCRE2_ERROR_NOMATCH ? "-" : "ERR");
            if (r > 0) for (uint32_t g = 0; g <= nc; g++) {
                int set = (int)g < r && o[2*g] != PCRE2_UNSET;
                printf("%s%ld,%ld", g ? " " : "", set ? (long)o[2*g] : -1L, set ? (long)o[2*g+1] : -1L);
            }
            printf("]");
        }
        printf("\n");
    }
    return 0;
}
