/* p2spans.c — libpcre2 10.46 find-all span oracle, the same print format as
 * waf/spans.c ("s e" lines then matches=N), the bench's find-all protocol
 * (resume at end, after an empty match at end+1; options=0, (?i) etc. in
 * the pattern text). Usage: p2spans PATTERN_FILE SUBJECT */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
static unsigned char *slurp(const char *p, size_t *n)
{
    FILE *f = fopen(p, "rb"); if (!f) exit(2);
    fseek(f, 0, SEEK_END); long l = ftell(f); rewind(f);
    unsigned char *b = malloc(l ? l : 1); if (fread(b, 1, l, f) != (size_t)l) exit(2); fclose(f);
    *n = (size_t)l; return b;
}
int main(int argc, char **argv)
{
    size_t pn, n; unsigned char *pat = slurp(argv[1], &pn), *b = slurp(argv[2], &n);
    if (pn && pat[pn - 1] == '\n') pn--;
    int err; PCRE2_SIZE eo;
    pcre2_code *re = pcre2_compile(pat, pn, 0, &err, &eo, NULL);
    if (!re) { printf("compile-error %d\n", err); return 3; }
    pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
    size_t pos = 0; long count = 0;
    for (;;) {
        int r = pcre2_match(re, b, n, pos, 0, md, NULL);
        if (r == PCRE2_ERROR_NOMATCH) break;
        if (r < 0) { printf("giveup %d\n", r); break; }
        PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
        size_t s = ov[0], e = ov[1];
        printf("%zu %zu\n", s, e); count++;
        pos = (e > s) ? e : s + 1; if (pos > n) break;
    }
    printf("matches=%ld\n", count); return 0;
}
