/* docs/design/kit_proof/z2/x1exh.c — X1's EXHAUSTIVE cell (z2build ruling 1).
 *
 * Linked with ONE built harness artifact and libpcre2-8: every subject of
 * length 0..MAXLEN over ALPHA, rx_search at every startoffset against an
 * unanchored pcre2_match at the same offset, then pcrec's find-all loop
 * (match_api.md §3.1.3, rx_next_pos) against PCRE2's (pos = end, +1 after
 * an empty match). Under FLAGS 'u' the
 * PCRE2 side is PCRE2_UTF|PCRE2_MATCH_INVALID_UTF (pcrec -e utf8's contract)
 * and a startoffset on a continuation byte is skipped (the K50 guard refuses
 * it first). The pattern is compiled from its own hex bytes.
 *
 *   x1exh FLAGS PATHEX ALPHAHEX MAXLEN   -> counts; first differences; rc 1 on any
 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>

static size_t unhex(const char *h, unsigned char *out)
{
    size_t n = 0;
    while (h[0] && h[1]) {
        unsigned v;
        sscanf(h, "%2x", &v);
        out[n++] = (unsigned char)v;
        h += 2;
    }
    return n;
}

static pcre2_code *code;
static pcre2_match_data *md;
static int utf;
static long long cells, diffs, subjects, pcre_err;

static int pm(const unsigned char *s, size_t n, size_t sf, long *a, long *b)
{
    int rc = pcre2_match(code, s, n, sf, 0, md, NULL);
    if (rc == PCRE2_ERROR_NOMATCH) return 0;
    if (rc < 0) { pcre_err++; return -1; }
    PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
    *a = (long)ov[0];
    *b = (long)ov[1];
    return 1;
}

static void report(const unsigned char *s, size_t n, const char *what, long sf,
                   int r1, long a1, long b1, int r2, long a2, long b2)
{
    diffs++;
    if (diffs > 12) return;
    printf("DIFF %s sf=%ld s=", what, sf);
    for (size_t i = 0; i < n; i++) printf("%02x", s[i]);
    printf(" pcrec=%d:%ld:%ld pcre=%d:%ld:%ld\n", r1, a1, b1, r2, a2, b2);
}

static void one(const unsigned char *s, size_t n)
{
    ptrdiff_t caps[64][2];
    subjects++;
    for (size_t sf = 0; sf <= n; sf++) {
        if (utf && sf < n && (s[sf] & 0xC0) == 0x80) continue;
        int r1 = rx_search(s, n, sf, caps);
        long a2 = 0, b2 = 0;
        int r2 = pm(s, n, sf, &a2, &b2);
        long a1 = r1 == 1 ? (long)caps[0][0] : 0, b1 = r1 == 1 ? (long)caps[0][1] : 0;
        cells++;
        if (r1 != r2 || (r1 == 1 && (a1 != a2 || b1 != b2)))
            report(s, n, "at", (long)sf, r1, a1, b1, r2, a2, b2);
    }
    /* find-all, both sides */
    size_t p1 = 0, p2 = 0;
    for (int it = 0; it < 64; it++) {
        int r1 = p1 <= n ? rx_search(s, n, p1, caps) : 0;
        long a2 = 0, b2 = 0;
        int r2 = p2 <= n ? pm(s, n, p2, &a2, &b2) : 0;
        long a1 = r1 == 1 ? (long)caps[0][0] : 0, b1 = r1 == 1 ? (long)caps[0][1] : 0;
        cells++;
        if (r1 != r2 || (r1 == 1 && (a1 != a2 || b1 != b2))) {
            report(s, n, "findall", it, r1, a1, b1, r2, a2, b2);
            break;
        }
        if (r1 != 1) break;
        p1 = b1 > a1 ? rx_next_pos(s, n, (size_t)b1 - 1) : rx_next_pos(s, n, (size_t)a1);
        p2 = b2 > a2 ? (size_t)b2 : (size_t)b2 + 1;
    }
}

int main(int argc, char **argv)
{
    if (argc != 5) { fprintf(stderr, "usage: x1exh FLAGS PATHEX ALPHAHEX MAXLEN\n"); return 2; }
    utf = strchr(argv[1], 'u') != NULL;
    unsigned char pat[4096], alpha[256];
    size_t pl = unhex(argv[2], pat), na = unhex(argv[3], alpha);
    int maxlen = atoi(argv[4]);
    int err; PCRE2_SIZE eo;
    uint32_t opt = utf ? (PCRE2_UTF | PCRE2_MATCH_INVALID_UTF) : 0;
    if (strchr(argv[1], 'i')) opt |= PCRE2_CASELESS;
    code = pcre2_compile(pat, pl, opt, &err, &eo, NULL);
    if (!code) { fprintf(stderr, "pcre2_compile failed %d\n", err); return 2; }
    md = pcre2_match_data_create_from_pattern(code, NULL);
    char ver[64];
    pcre2_config(PCRE2_CONFIG_VERSION, ver);
    unsigned char s[64];
    int idx[64];
    for (int len = 0; len <= maxlen; len++) {
        memset(idx, 0, sizeof idx);
        for (;;) {
            for (int i = 0; i < len; i++) s[i] = alpha[idx[i]];
            one(s, (size_t)len);
            int i = len - 1;
            while (i >= 0 && ++idx[i] == (int)na) idx[i--] = 0;
            if (i < 0) break;
        }
    }
    printf("libpcre2 %s alphabet=%zu maxlen=%d subjects=%lld cells=%lld diffs=%lld pcre_err=%lld\n",
           ver, na, maxlen, subjects, cells, diffs, pcre_err);
    return diffs || pcre_err ? 1 : 0;
}
