/* tests/revend/window_twin_driver.c -- [OPT-REVEND] L2 STAGE 2's WINDOW-IDENTITY
 * TWIN (locate_finish.md §4.3, §5 L3, LR-S2/LR-S4; lane revbuild).
 *
 * Links two builds of ONE pattern: A, the artifact with the `rev-end` walk
 * (the default compile), and B, the same pattern under `-fno-rev-end` (the
 * shipped composite). For every subject over ALPHABET up to MAXLEN characters
 * and every start offset at a character boundary it compares:
 *
 *   (1) the WINDOW: A's inlined `<p>_prefilter` against B's (rc, start, end),
 *       on a VM hybrid -- the hand the VM finisher reads;
 *   (2) the ANSWER: A's `<p>_search` against B's (rc and every capture slot);
 *   (3) the ORACLE: A's `<p>_search` against libpcre2's pcre2_match at the
 *       same offset (rc and every group), when an oracle pattern is given;
 *
 * and counts E-VR traversals: VM attempts that FAIL after the first attempt
 * of a search on A (the wrappers count `<p>_reset_for_next_attempt`, the
 * text every failed attempt runs). On an EXACT hybrid the window IS the
 * match, so the count must be 0 (LR-S4); `window_twin.py` asserts it.
 *
 * Usage: window_twin_driver ALPHABET MAXLEN ORACLE_PATTERN ORACLE_OPTS
 *   ALPHABET: the characters, UTF-8 encoded (each code point is one letter);
 *   ORACLE_PATTERN "-" skips (3). ORACLE_OPTS: a string of `i` (caseless) and
 *   `u` (UTF) letters, or "-".
 * Prints one line: `cells N win_diff N ans_diff N ora_diff N evr N
 * pf_cells N` (`pf_cells`: the cells where BOTH builds carry an inlined
 * prefilter, the window comparison's population: a size cap can drop B's
 * and keep A's smaller one) and the first few differences on stderr. Exit 0 always; the
 * caller reads the counts. */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int  twinA_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
int  twinB_search(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*caps)[2]);
int  twinA_pf(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*w)[2]);
int  twinB_pf(const unsigned char *s, size_t n, size_t from, ptrdiff_t (*w)[2]);
int  twinA_ncaps(void);
long twin_evr_A;

#define MAXC 64
static const char *letters[16];
static size_t letlen[16];
static int nlet;

static void split_alphabet(const char *a)
{
    while (*a && nlet < 16) {
        size_t k = 1;
        unsigned char c = (unsigned char)*a;
        if (c >= 0xF0) k = 4; else if (c >= 0xE0) k = 3; else if (c >= 0xC0) k = 2;
        letters[nlet] = a;
        letlen[nlet++] = k;
        a += k;
    }
}

int main(int argc, char **argv)
{
    if (argc < 5) { fprintf(stderr, "usage\n"); return 2; }
    split_alphabet(argv[1]);
    int maxlen = atoi(argv[2]);
    int ncaps = twinA_ncaps();
    pcre2_code *re = NULL;
    pcre2_match_data *md = NULL;
    if (strcmp(argv[3], "-")) {
        uint32_t opts = 0;
        int err; PCRE2_SIZE eoff;
        if (strchr(argv[4], 'i')) opts |= PCRE2_CASELESS;
        if (strchr(argv[4], 'u')) opts |= PCRE2_UTF;
        re = pcre2_compile((PCRE2_SPTR)argv[3], PCRE2_ZERO_TERMINATED, opts, &err, &eoff, NULL);
        if (!re) { fprintf(stderr, "oracle: pattern does not compile\n"); return 2; }
        md = pcre2_match_data_create_from_pattern(re, NULL);
    }
    long cells = 0, pfcells = 0, windiff = 0, ansdiff = 0, oradiff = 0, shown = 0;
    int idx[16];
    unsigned char subj[256];
    size_t bnd[64];
    for (int len = 0; len <= maxlen; len++) {
        long total = 1;
        for (int k = 0; k < len; k++) total *= nlet;
        for (long t = 0; t < total; t++) {
            long v = t;
            size_t n = 0;
            int nb = 0;
            for (int k = 0; k < len; k++) { idx[k] = (int)(v % nlet); v /= nlet; }
            for (int k = 0; k < len; k++) {
                bnd[nb++] = n;
                memcpy(subj + n, letters[idx[k]], letlen[idx[k]]);
                n += letlen[idx[k]];
            }
            bnd[nb++] = n;
            for (int b = 0; b < nb; b++) {
                size_t lo = bnd[b];
                ptrdiff_t wa[1][2] = {{-7, -7}}, wb[1][2] = {{-7, -7}};
                int pa = twinA_pf(subj, n, lo, wa), pb = twinB_pf(subj, n, lo, wb);
                cells++;
                if (pa != -9 && pb != -9) {
                    pfcells++;
                    if (pa != pb || (pa == 1 && (wa[0][0] != wb[0][0] || wa[0][1] != wb[0][1]))) {
                        windiff++;
                        if (shown++ < 5)
                            fprintf(stderr, "WIN len=%zu lo=%zu A=%d(%td,%td) B=%d(%td,%td)\n", n, lo,
                                    pa, wa[0][0], wa[0][1], pb, wb[0][0], wb[0][1]);
                    }
                }
                ptrdiff_t ca[MAXC][2], cb[MAXC][2];
                for (int g = 0; g < MAXC; g++) ca[g][0] = ca[g][1] = cb[g][0] = cb[g][1] = -5;
                long evr0 = twin_evr_A;
                int ra = twinA_search(subj, n, lo, ca), rb = twinB_search(subj, n, lo, cb);
                (void)evr0;
                int bad = ra != rb;
                if (ra == 1)
                    for (int g = 0; g < ncaps && g < MAXC; g++)
                        if (ca[g][0] != cb[g][0] || ca[g][1] != cb[g][1]) bad = 1;
                if (bad) {
                    ansdiff++;
                    if (shown++ < 5)
                        fprintf(stderr, "ANS len=%zu lo=%zu A=%d(%td,%td) B=%d(%td,%td)\n", n, lo,
                                ra, ca[0][0], ca[0][1], rb, cb[0][0], cb[0][1]);
                }
                if (re) {
                    int rc = pcre2_match(re, subj, n, lo, 0, md, NULL);
                    int obad = (rc >= 0) != (ra == 1);
                    if (rc >= 0 && ra == 1) {
                        PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
                        for (int g = 0; g < ncaps && g < MAXC; g++) {
                            ptrdiff_t s = g < rc ? (ov[2 * g] == PCRE2_UNSET ? -1 : (ptrdiff_t)ov[2 * g]) : -1;
                            ptrdiff_t e = g < rc ? (ov[2 * g + 1] == PCRE2_UNSET ? -1 : (ptrdiff_t)ov[2 * g + 1]) : -1;
                            if (s != ca[g][0] || e != ca[g][1]) obad = 1;
                        }
                    }
                    if (obad) {
                        oradiff++;
                        if (shown++ < 5)
                            fprintf(stderr, "ORA len=%zu lo=%zu A=%d(%td,%td) pcre2 rc=%d\n", n, lo,
                                    ra, ca[0][0], ca[0][1], rc);
                    }
                }
            }
        }
    }
    printf("cells %ld win_diff %ld ans_diff %ld ora_diff %ld evr %ld pf_cells %ld\n",
           cells, windiff, ansdiff, oradiff, twin_evr_A, pfcells);
    return 0;
}
