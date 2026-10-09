/* [OPT-REVEND] hand-twin ANSWER-IDENTITY driver (STUDY).
 *
 *   check PATTERN ENC SUBJECTS.hex
 *
 * Links three answerers for one pattern: the UNMODIFIED artifact (prefix o),
 * its hand-twin (prefix t, mktwin.py) and libpcre2-8 (10.46 on this box).
 * SUBJECTS.hex: one subject per line, hex-encoded. For every subject and
 * every search_from in [0, n+1] (a sample of 64 positions plus the last 8
 * on subjects longer than 512 bytes, where libpcre2 -- an interpreter,
 * quadratic on the nullable shapes -- is asked only at 0 and the last 8) it compares the twin's (rc, span)
 * against the artifact's, and both against libpcre2 where libpcre2 answers
 * the same question (rc 0/1; under utf8 a mid-character startpos is a
 * refusal on both sides and is compared as such). Then a find-all loop
 * from 0 (the caller's empty-match rule: an empty match at e resumes at
 * the next character) is compared artifact vs twin.
 *
 * ENC is byte or utf8; utf8 compiles the oracle with PCRE2_UTF |
 * PCRE2_MATCH_INVALID_UTF (pcrec's default invalid-tolerant contract,
 * docs/spec/tuning.md §2.36; no UCP: `-e utf8` implies the ucp MODULE, not
 * UCP semantics, so `\w` stays ASCII as in PCRE2_UTF's own default). A
 * mid-character startpos is a refusal on pcrec's side (K50, -7) that
 * libpcre2 under MATCH_INVALID_UTF does not make; those cells are compared
 * twin vs artifact only. Prints one summary line; exit 1 on
 * any twin disagreement. */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include "o.h"
#include "t.h"

static int hexv(int c) { return c <= '9' ? c - '0' : (c | 32) - 'a' + 10; }

static pcre2_code *re; static pcre2_match_data *md; static int utf;
static long n_cells, n_twin_bad, n_ora_cells, n_ora_bad_o, n_ora_bad_t, n_fa, n_fa_bad;

/* libpcre2's answer in the artifact's vocabulary: 1/0, or -7 for a
 * refused mid-character startpos; 99 where it answers something else. */
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
    if (!same) {
        if (n_twin_bad++ < 10)
            printf("  TWIN-DIFF from=%zu orig=%d(%td,%td) twin=%d(%td,%td) subj=%.80s\n",
                   from, ro, co[0][0], co[0][1], rt, ct[0][0], ct[0][1], hex);
    }
    if (from > n || !ask_oracle || ro == PCREC_ERR_STARTPOS) return;
    int rp = oracle(s, n, from, cp);
    if (rp == 99) return;
    n_ora_cells++;
    if (!(ro == rp && (ro != 1 || (co[0][0] == cp[0] && co[0][1] == cp[1])))) {
        if (n_ora_bad_o++ < 5)
            printf("  ORACLE-DIFF(orig) from=%zu orig=%d(%td,%td) pcre2=%d(%td,%td) subj=%.80s\n",
                   from, ro, co[0][0], co[0][1], rp, cp[0], cp[1], hex);
    }
    if (!(rt == rp && (rt != 1 || (ct[0][0] == cp[0] && ct[0][1] == cp[1])))) n_ora_bad_t++;
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
    for (int k = 0; k < 100000 && from <= n; k++) {
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
    if (argc != 4) { fprintf(stderr, "usage: check PATTERN byte|utf8 SUBJECTS.hex\n"); return 2; }
    utf = !strcmp(argv[2], "utf8");
    int ec; PCRE2_SIZE eo;
    re = pcre2_compile((PCRE2_SPTR)argv[1], PCRE2_ZERO_TERMINATED,
                       utf ? PCRE2_UTF | PCRE2_MATCH_INVALID_UTF : 0, &ec, &eo, NULL);
    if (!re) { fprintf(stderr, "pcre2_compile failed at %zu\n", (size_t)eo); return 2; }
    md = pcre2_match_data_create_from_pattern(re, NULL);
    FILE *f = fopen(argv[3], "r");
    if (!f) { perror(argv[3]); return 2; }
    static char line[1 << 22]; static unsigned char s[1 << 21];
    long nsubj = 0;
    while (fgets(line, sizeof line, f)) {
        size_t L = strcspn(line, "\r\n"); line[L] = 0;
        size_t n = L / 2;
        for (size_t i = 0; i < n; i++) s[i] = (unsigned char)(hexv(line[2 * i]) << 4 | hexv(line[2 * i + 1]));
        nsubj++;
        if (n <= 512) {
            for (size_t from = 0; from <= n + 1; from++) one(s, n, from, line, 1);
        } else {
            for (size_t k = 0; k < 64; k++) one(s, n, k * (n / 64), line, k == 0);
            for (size_t from = n - 7; from <= n + 1; from++) one(s, n, from, line, 1);
        }
        findall(s, n);
    }
    printf("%-22s %-4s subjects=%ld cells=%ld twin_diff=%ld | oracle_cells=%ld orig_vs_pcre2=%ld twin_vs_pcre2=%ld | findall_calls=%ld findall_diff=%ld\n",
           argv[1], argv[2], nsubj, n_cells, n_twin_bad, n_ora_cells, n_ora_bad_o, n_ora_bad_t, n_fa, n_fa_bad);
    return n_twin_bad || n_fa_bad ? 1 : 0;
}
