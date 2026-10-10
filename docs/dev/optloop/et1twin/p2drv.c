/* docs/dev/optloop/et1twin/p2drv.c -- the libpcre2-8 side of etdrv's
 * `ident` mode: the same find-all loop and the same every-startpos sweep,
 * answered by pcre2_match (unanchored, options 0, the reference oracle
 * on this box: 10.46). Output lines are byte-comparable with etdrv's.
 *
 *   p2drv PATTERN_FILE FILE...                                          */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static unsigned char *load(const char *path, size_t *n)
{
    FILE *f = fopen(path, "rb");
    if (!f) { perror(path); exit(2); }
    fseek(f, 0, SEEK_END); long len = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *b = malloc((size_t)len + 1);
    if (fread(b, 1, (size_t)len, f) != (size_t)len) exit(2);
    fclose(f);
    *n = (size_t)len;
    return b;
}
static unsigned long long fnv(unsigned long long h, long long v)
{
    for (int i = 0; i < 8; i++) { h ^= (unsigned char)(v >> (8 * i)); h *= 1099511628211ULL; }
    return h;
}
static pcre2_code *re;
static pcre2_match_data *md;
/* rc as rx_search reports it: 1 match, 0 none; anything else is fatal */
static int search(const unsigned char *b, size_t n, size_t pos, long long *s, long long *e)
{
    int rc = pcre2_match(re, b, n, pos, 0, md, NULL);
    if (rc == PCRE2_ERROR_NOMATCH) return 0;
    if (rc < 0) { fprintf(stderr, "pcre2_match rc=%d at %zu\n", rc, pos); exit(3); }
    PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
    *s = (long long)ov[0]; *e = (long long)ov[1];
    return 1;
}
int main(int argc, char **argv)
{
    if (argc < 3) return 2;
    size_t pl; unsigned char *pat = load(argv[1], &pl);
    while (pl && pat[pl - 1] == '\n') pl--;
    int err; PCRE2_SIZE eo;
    re = pcre2_compile(pat, pl, 0, &err, &eo, NULL);
    if (!re) { fprintf(stderr, "compile error %d at %zu\n", err, (size_t)eo); return 2; }
    md = pcre2_match_data_create_from_pattern(re, NULL);
    for (int a = 2; a < argc; a++) {
        size_t n; unsigned char *b = load(argv[a], &n);
        unsigned long long hf = 14695981039346656037ULL, hs = hf;
        long cnt = 0, hits = 0, tried = 0; long long s, e;
        size_t pos = 0;
        while (pos <= n) {
            int rc = search(b, n, pos, &s, &e);
            if (rc != 1) { hf = fnv(hf, rc); break; }
            cnt++; hf = fnv(hf, s); hf = fnv(hf, e);
            pos = e > s ? (size_t)e : (size_t)s + 1;
        }
        for (size_t p = 0; p <= n; p += p < 4096 ? 1 : 4099) {
            int rc = search(b, n, p, &s, &e);
            tried++;
            hs = fnv(hs, (long long)p); hs = fnv(hs, rc);
            if (rc == 1) { hits++; hs = fnv(hs, s); hs = fnv(hs, e); }
        }
        const char *base = strrchr(argv[a], '/');
        printf("%s\tn=%zu\tfa=%ld\tfa_h=%016llx\tsp=%ld/%ld\tsp_h=%016llx\n",
               base ? base + 1 : argv[a], n, cnt, hf, hits, tried, hs);
        free(b);
    }
    return 0;
}
