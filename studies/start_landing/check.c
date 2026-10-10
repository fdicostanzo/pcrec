/* [START-LANDING] hand-twin ANSWER-IDENTITY driver (STUDY; adapted from
 * studies/revend_twin/check.c).
 *
 *   check PATTERN_HEX ENC ICASE SUBJECTS.hex
 *
 * Links three answerers for one pattern: the UNMODIFIED artifact (prefix o),
 * its hand-twin (prefix t, mktwin.py) and libpcre2-8 (10.46 on this box).
 * For every subject and EVERY search_from in [0, n+1] (subjects over 512
 * bytes: 64 sampled positions plus the last 8) it compares the twin's
 * (rc, span) with the artifact's, and both with libpcre2 (rc 0/1; utf8 is
 * PCRE2_UTF | PCRE2_MATCH_INVALID_UTF, pcrec's default invalid-tolerant
 * contract; a mid-character startpos is a refusal on pcrec's side and is
 * compared twin vs artifact only). Then a find-all from 0 (the caller's
 * empty-match rule) artifact vs twin. In ASSERT mode the twin also counts,
 * per call of its DFA body (the search, or a hybrid's inlined prefilter),
 * how often the row's start differs from the reverse pass's: t_tw_diff.
 *
 * One line out; exit 1 on any twin/artifact disagreement, any assert-mode
 * per-call difference, or any cell where the twin disagrees with libpcre2
 * and the artifact does not (NEW_BAD). */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include "o.h"
#include "t.h"

extern long t_tw_calls, t_tw_diff;
static int hexv(int c) { return c <= '9' ? c - '0' : (c | 32) - 'a' + 10; }

static pcre2_code *re; static pcre2_match_data *md; static int utf;
static long n_cells, n_twin_bad, n_ora_cells, n_ora_bad_o, n_ora_bad_t, n_new_bad, n_fa, n_fa_bad;

static int oracle(const unsigned char *s, size_t n, size_t from, ptrdiff_t sp[2])
{
    int rc = pcre2_match(re, s, n, from, 0, md, NULL);
    if (rc >= 1) { PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md); sp[0] = ov[0]; sp[1] = ov[1]; return 1; }
    if (rc == PCRE2_ERROR_NOMATCH) return 0;
    if (rc == PCRE2_ERROR_BADUTFOFFSET) return -7;
    return 99;
}

static void one(const unsigned char *s, size_t n, size_t from, const char *hex, int ask_oracle)
{
    ptrdiff_t co[O_NCAPS][2], ct[T_NCAPS][2], cp[2] = {-1, -1};
    memset(co, 0xff, sizeof co); memset(ct, 0xff, sizeof ct);
    int ro = o_search(s, n, from, co), rt = t_search(s, n, from, ct);
    n_cells++;
    int same = ro == rt && (ro != 1 || (co[0][0] == ct[0][0] && co[0][1] == ct[0][1]));
    if (!same && n_twin_bad++ < 5)
        printf("  TWIN-DIFF from=%zu orig=%d(%td,%td) twin=%d(%td,%td) subj=%.80s\n",
               from, ro, co[0][0], co[0][1], rt, ct[0][0], ct[0][1], hex);
    if (from > n || !ask_oracle || ro == PCREC_ERR_STARTPOS) return;
    int rp = oracle(s, n, from, cp);
    if (rp == 99) return;
    n_ora_cells++;
    int ok_o = ro == rp && (ro != 1 || (co[0][0] == cp[0] && co[0][1] == cp[1]));
    int ok_t = rt == rp && (rt != 1 || (ct[0][0] == cp[0] && ct[0][1] == cp[1]));
    if (!ok_o) n_ora_bad_o++;
    if (!ok_t) n_ora_bad_t++;
    if (ok_o && !ok_t && n_new_bad++ < 5)
        printf("  NEW-BAD from=%zu twin=%d(%td,%td) pcre2=%d(%td,%td) subj=%.80s\n",
               from, rt, ct[0][0], ct[0][1], rp, cp[0], cp[1], hex);
}

static size_t next_char(const unsigned char *s, size_t n, size_t p)
{
    p++;
    if (utf) while (p < n && (s[p] & 0xC0) == 0x80) p++;
    return p;
}

static void findall(const unsigned char *s, size_t n)
{
    size_t from = 0;
    for (int k = 0; k < 200000 && from <= n; k++) {
        ptrdiff_t co[O_NCAPS][2], ct[T_NCAPS][2];
        int ro = o_search(s, n, from, co), rt = t_search(s, n, from, ct);
        n_fa++;
        if (ro != rt || (ro == 1 && (co[0][0] != ct[0][0] || co[0][1] != ct[0][1]))) { n_fa_bad++; return; }
        if (ro != 1) return;
        from = co[0][1] > co[0][0] ? (size_t)co[0][1] : next_char(s, n, (size_t)co[0][1]);
    }
}

int main(int argc, char **argv)
{
    if (argc != 5) { fprintf(stderr, "usage: check PATTERN_HEX byte|utf8 ICASE SUBJECTS.hex\n"); return 2; }
    utf = !strcmp(argv[2], "utf8");
    size_t pl = strlen(argv[1]) / 2; unsigned char *pat = malloc(pl + 1);
    for (size_t i = 0; i < pl; i++) pat[i] = (unsigned char)(hexv(argv[1][2 * i]) << 4 | hexv(argv[1][2 * i + 1]));
    int ec; PCRE2_SIZE eo;
    re = pcre2_compile((PCRE2_SPTR)pat, pl,
                       (utf ? PCRE2_UTF | PCRE2_MATCH_INVALID_UTF : 0) | (atoi(argv[3]) ? PCRE2_CASELESS : 0),
                       &ec, &eo, NULL);
    if (re) md = pcre2_match_data_create_from_pattern(re, NULL);
    FILE *f = fopen(argv[4], "r");
    if (!f) { perror(argv[4]); return 2; }
    static char line[1 << 25]; static unsigned char s[1 << 24];
    long nsubj = 0;
    while (fgets(line, sizeof line, f)) {
        size_t L = strcspn(line, "\r\n"); line[L] = 0;
        size_t n = L / 2;
        for (size_t i = 0; i < n; i++) s[i] = (unsigned char)(hexv(line[2 * i]) << 4 | hexv(line[2 * i + 1]));
        nsubj++;
        if (n <= 512) {
            for (size_t from = 0; from <= n + 1; from++) one(s, n, from, line, re != NULL);
        } else {
            for (size_t k = 0; k < 64; k++) one(s, n, k * (n / 64), line, re != NULL && k == 0);
            for (size_t from = n - 7; from <= n + 1; from++) one(s, n, from, line, re != NULL);
        }
        findall(s, n);
    }
    printf("subjects=%ld cells=%ld twin_diff=%ld calls=%ld call_diff=%ld | oracle_cells=%ld orig_vs_pcre2=%ld twin_vs_pcre2=%ld NEW_BAD=%ld | findall_calls=%ld findall_diff=%ld%s\n",
           nsubj, n_cells, n_twin_bad, t_tw_calls, t_tw_diff, n_ora_cells, n_ora_bad_o, n_ora_bad_t, n_new_bad,
           n_fa, n_fa_bad, re ? "" : " (pcre2 refused the pattern)");
    return n_twin_bad || n_fa_bad || t_tw_diff || n_new_bad ? 1 : 0;
}
