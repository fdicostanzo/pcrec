/* [COMPOSITE] design lane mscomp: the twin's in-process differential.
 * Links three things for ONE pattern: the plain artifact (prefix rxp, today's
 * compile), the hand-composed composite (exports rx_search, the controller in
 * ctrl.c over parts rxf = \G(?:P) and rxq = Q), and libpcre2-8 (the oracle).
 * For every subject (read from stdin, one hex line each) and every startpos
 * 0..n it compares rc + all caps slots of composite vs plain, and plain's
 * whole-match span vs pcre2's. Also runs the match_api.md §3.1.3 find-all loop
 * on composite and plain.  Prints one summary line.
 * Build: gcc -O1 -DUTF=0|1 -I<dir> diff.c ctrl.c floor.c q.c plain.c -lpcre2-8 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "plain.h"
int rx_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
#ifndef UTF
#define UTF 0
#endif
static size_t unhex(const char *h, unsigned char *out)
{
    size_t n = strlen(h) / 2;
    for (size_t i = 0; i < n; i++) { unsigned v; sscanf(h + 2 * i, "%2x", &v); out[i] = (unsigned char)v; }
    return n;
}
int main(int argc, char **argv)
{
    if (argc < 2) return 2;
    unsigned char pat[65536];
    size_t pl = unhex(argv[1], pat);
    int ec; PCRE2_SIZE eo;
    pcre2_code *re = pcre2_compile(pat, pl, UTF ? PCRE2_UTF : 0, &ec, &eo, NULL);
    pcre2_match_data *md = re ? pcre2_match_data_create_from_pattern(re, NULL) : NULL;
    char line[1 << 16];
    unsigned char s[1 << 15];
    unsigned long long cells = 0, diff_cp = 0, diff_po = 0, fa = 0, diff_fa = 0, matches = 0;
    char first[512] = "";
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\r\n")] = 0;
        size_t n = unhex(line, s);
        for (size_t sp = 0; sp <= n + 1; sp++) {
            ptrdiff_t a[RXP_NCAPS][2], b[RXP_NCAPS][2];
            memset(a, 0x5a, sizeof a); memset(b, 0x5a, sizeof b);
            int ra = rx_search(s, n, sp, a), rb = rxp_search(s, n, sp, b);
            cells++;
            if (rb == 1) matches++;
            int same = ra == rb && (ra != 1 || memcmp(a, b, sizeof a) == 0);
            if (!same) {
                if (!diff_cp++) snprintf(first, sizeof first, "CP subj=%s sp=%zu comp=%d(%td,%td) plain=%d(%td,%td)",
                                          line, sp, ra, a[0][0], a[0][1], rb, b[0][0], b[0][1]);
            }
            if (re && sp <= n && rb >= 0) {
                int rc = pcre2_match(re, s, n, sp, 0, md, NULL);
                int ok;
                if (rc >= 0) { PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
                    ok = rb == 1 && (size_t)b[0][0] == ov[0] && (size_t)b[0][1] == ov[1]; }
                else ok = rb == 0 || rc != PCRE2_ERROR_NOMATCH;
                if (!ok && !diff_po++ && !first[0])
                    snprintf(first, sizeof first, "PO subj=%s sp=%zu plain=%d(%td,%td) pcre2=%d", line, sp, rb, b[0][0], b[0][1], rc);
            }
        }
        /* find-all, match_api.md §3.1.3 (byte or utf8 advance via next_pos) */
        size_t pa = 0, pb = 0; int done_a = 0, done_b = 0;
        while (!done_a || !done_b) {
            ptrdiff_t a[RXP_NCAPS][2], b[RXP_NCAPS][2];
            int ra = done_a ? 0 : rx_search(s, n, pa, a), rb = done_b ? 0 : rxp_search(s, n, pb, b);
            fa++;
            if ((ra == 1) != (rb == 1) || (ra == 1 && (a[0][0] != b[0][0] || a[0][1] != b[0][1]))) { diff_fa++; break; }
            if (ra != 1) break;
            pa = a[0][1] > a[0][0] ? rxp_next_pos(s, n, (size_t)a[0][1] - 1) : rxp_next_pos(s, n, (size_t)a[0][0]);
            pb = pa;
            if (pa > n) break;
        }
    }
    printf("cells=%llu matches=%llu diff_comp_plain=%llu diff_plain_pcre2=%llu findall_steps=%llu diff_findall=%llu%s%s\n",
           cells, matches, diff_cp, diff_po, fa, diff_fa, first[0] ? " FIRST: " : "", first);
    return 0;
}
