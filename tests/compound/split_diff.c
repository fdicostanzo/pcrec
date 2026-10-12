/* tests/compound/split_diff.c -- [COMPOUND] B4's differential driver (G2,
 * docs/design/compound.md §E.2/§E.3; promoted from the twin's diff.c).
 *
 * Links three answers for ONE pattern under one option arm: the COMPOUND the
 * default build emits (prefix `ca`), the same pattern from the harness build
 * with the compound family declined (`pl`, today's plain artifact: the
 * lever), and libpcre2-8. For every subject (stdin, one hex line each) and
 * every startpos 0..n+1:
 *   - `ca_search` against `pl_search`: the code and every caps slot, exactly
 *     (refusals included);
 *   - `ca_match` and `ca_match_caps` against `pl_`'s, exactly;
 *   - `pl_search`'s whole-match span against libpcre2's where the plain
 *     artifact answered (not a refusal) and startpos <= n, a libpcre2 error
 *     other than NOMATCH counting as agreement (the twin's rule: it measures
 *     the plain artifact, which the corpus already holds to libpcre2);
 * and the match_api.md §3.1 find-all loop on both artifacts.
 * Prints one summary line; exit 0 (the runner reads the counts).
 *
 * Build: gcc -O1 -DUTF=0|1 split_diff.c ca.c pl.c -lpcre2-8 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ca.h"
#include "pl.h"
#ifndef UTF
#define UTF 0
#endif

/* Decodes hex `h` into `out`; its length. */
static size_t unhex(const char *h, unsigned char *out)
{
    size_t n = strlen(h) / 2;
    for (size_t i = 0; i < n; i++) {
        unsigned v;
        sscanf(h + 2 * i, "%2x", &v);
        out[i] = (unsigned char)v;
    }
    return n;
}

int main(int argc, char **argv)
{
    if (argc < 2) return 2;
    static unsigned char pat[65536];
    size_t plen = unhex(argv[1], pat);
    int ec;
    PCRE2_SIZE eo;
    pcre2_code *re = pcre2_compile(pat, plen, UTF ? PCRE2_UTF : 0, &ec, &eo, NULL);
    pcre2_match_data *md = re ? pcre2_match_data_create_from_pattern(re, NULL) : NULL;
    static char line[1 << 16];
    static unsigned char s[1 << 15];
    unsigned long long cells = 0, matches = 0, d_search = 0, d_match = 0, d_oracle = 0;
    unsigned long long fa = 0, d_fa = 0;
    char first[600] = "";
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\r\n")] = 0;
        size_t n = unhex(line, s);
        for (size_t sp = 0; sp <= n + 1; sp++) {
            ptrdiff_t a[PL_NCAPS][2], b[PL_NCAPS][2];
            memset(a, 0x5a, sizeof a);
            memset(b, 0x5a, sizeof b);
            int ra = ca_search(s, n, sp, a), rb = pl_search(s, n, sp, b);
            cells++;
            if (rb == 1) matches++;
            if (ra != rb || (ra == 1 && memcmp(a, b, sizeof a) != 0)) {
                if (!d_search++ && !first[0])
                    snprintf(first, sizeof first, "SEARCH subj=%.200s sp=%zu compound=%d(%td,%td) plain=%d(%td,%td)",
                             line, sp, ra, a[0][0], a[0][1], rb, b[0][0], b[0][1]);
            }
            rx_ctx c = { .subject = s, .len = n, .pos = sp };
            ptrdiff_t ma = ca_match(&c), mb = pl_match(&c);
            ptrdiff_t ka[PL_NCAPS][2], kb[PL_NCAPS][2];
            memset(ka, 0x5a, sizeof ka);
            memset(kb, 0x5a, sizeof kb);
            ptrdiff_t xa = ca_match_caps(&c, ka), xb = pl_match_caps(&c, kb);
            if (ma != mb || xa != xb || (xa >= 0 && memcmp(ka, kb, sizeof ka) != 0)) {
                if (!d_match++ && !first[0])
                    snprintf(first, sizeof first, "MATCH subj=%.200s pos=%zu compound=%td/%td plain=%td/%td",
                             line, sp, ma, xa, mb, xb);
            }
            if (re && sp <= n && rb >= 0) {
                int rc = pcre2_match(re, s, n, sp, 0, md, NULL);
                int ok;
                if (rc >= 0) {
                    PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
                    ok = rb == 1 && (size_t)b[0][0] == ov[0] && (size_t)b[0][1] == ov[1];
                } else {
                    ok = rb == 0 || rc != PCRE2_ERROR_NOMATCH;
                }
                if (!ok && !d_oracle++ && !first[0])
                    snprintf(first, sizeof first, "ORACLE subj=%.200s sp=%zu plain=%d(%td,%td) pcre2=%d",
                             line, sp, rb, b[0][0], b[0][1], rc);
            }
        }
        /* find-all, match_api.md §3.1 */
        size_t p = 0;
        for (;;) {
            ptrdiff_t a[PL_NCAPS][2], b[PL_NCAPS][2];
            int ra = ca_search(s, n, p, a), rb = pl_search(s, n, p, b);
            fa++;
            if (ra != rb || (ra == 1 && (a[0][0] != b[0][0] || a[0][1] != b[0][1]))) {
                d_fa++;
                break;
            }
            if (ra != 1) break;
            p = a[0][1] > a[0][0] ? pl_next_pos(s, n, (size_t)a[0][1] - 1)
                                  : pl_next_pos(s, n, (size_t)a[0][0]);
            if (p > n) break;
        }
    }
    printf("cells=%llu matches=%llu d_search=%llu d_match=%llu d_oracle=%llu findall=%llu d_findall=%llu%s%s\n",
           cells, matches, d_search, d_match, d_oracle, fa, d_fa, first[0] ? " FIRST: " : "", first);
    return 0;
}
