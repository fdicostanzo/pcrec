/* docs/design/kit_proof/x0/x0pcre.c — X0's libpcre2 side (kit_proof.md §6.4).
 *
 * A line-protocol server over libpcre2-8. It knows nothing of pcrec: no
 * table, no reading, no set the reading states. Every answer is a PCRE2
 * match call on a concrete subject, so it is the INDEPENDENT half of X0.
 * The Python driver (x0.py) asks it questions and compares the answers to
 * conj.py's reading.
 *
 *   gcc -O2 -std=gnu11 -o build/x0/x0pcre docs/design/kit_proof/x0/x0pcre.c -lpcre2-8
 *
 * Requests on stdin, one per line, fields TAB-separated, byte strings in hex
 * ("" = empty). One reply line each.
 *   V                        -> the library version string
 *   P FLAGS HEXPAT           -> "ok" | "err CODE"; FLAGS '-' or any of i, u
 *                               (u = PCRE2_UTF|PCRE2_MATCH_INVALID_UTF, the
 *                               invalid-tolerant contract pcrec's -e utf8 has)
 *   N HEXCTX HEXW            -> 64 hex digits: the 256-bit set of bytes b such
 *                               that W·b is a PREFIX of the match PCRE2 picks
 *                               anchored at offset |CTX| of CTX·W·b (hard
 *                               partial: PARTIAL, or a complete match ending
 *                               at the subject end). Under u a b that leaves a
 *                               character incomplete is completed: b is in the
 *                               set iff SOME well-formed completion of that
 *                               character is a prefix, every completion tried
 *                               (exhaustive over the code points that start
 *                               with the bytes so far).
 *   T HEXCTX HEXW TAILS      -> for each tail in the comma list TAILS (hex,
 *                               "" = the subject ends), the anchored match
 *                               length at |CTX| of CTX·W·tail, or -1; comma
 *                               list. A length is counted from the origin.
 *   F HEXSUBJ                -> unanchored pcre2_match at every startoffset
 *                               0..n: "a:b" or "-" (or "eRC"), comma list,
 *                               then "|" and the find-all loop's matches
 *                               (pos = end, +1 after an empty match).
 * Bounded: match limit 200000, depth limit 20000 (a limit is "eRC").
 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static pcre2_code *code;
static pcre2_match_data *md;
static pcre2_match_context *mctx;
static int utf;

static int hexval(int c)
{
    return c <= '9' ? c - '0' : (c | 0x20) - 'a' + 10;
}

static size_t unhex(const char *h, unsigned char *out)
{
    size_t n = 0;
    while (h[0] && h[1] && h[0] != '\t' && h[0] != ',' && h[0] != '\n') {
        out[n++] = (unsigned char)(hexval(h[0]) << 4 | hexval(h[1]));
        h += 2;
    }
    return n;
}

/* the anchored match: rc, and the end offset in *end */
static int am(const unsigned char *s, size_t n, size_t start, uint32_t opt, size_t *end)
{
    int rc = pcre2_match(code, s, n, start, PCRE2_ANCHORED | opt, md, mctx);
    if (rc >= 0)
        *end = pcre2_get_ovector_pointer(md)[1];
    return rc;
}

static int is_prefix(const unsigned char *s, size_t n, size_t start)
{
    size_t e = 0;
    int rc = am(s, n, start, PCRE2_PARTIAL_HARD, &e);
    if (rc == PCRE2_ERROR_PARTIAL)
        return 1;
    return rc >= 0 && e == n;
}

static int enc(unsigned c, unsigned char *o)
{
    if (c < 0x80) { o[0] = (unsigned char)c; return 1; }
    if (c < 0x800) { o[0] = 0xC0 | c >> 6; o[1] = 0x80 | (c & 63); return 2; }
    if (c < 0x10000) { o[0] = 0xE0 | c >> 12; o[1] = 0x80 | (c >> 6 & 63); o[2] = 0x80 | (c & 63); return 3; }
    o[0] = 0xF0 | c >> 18; o[1] = 0x80 | (c >> 12 & 63); o[2] = 0x80 | (c >> 6 & 63); o[3] = 0x80 | (c & 63);
    return 4;
}

/* the code-point range a lead byte opens (well-formed UTF-8 only) */
static int lead_range(unsigned L, unsigned *lo, unsigned *hi)
{
    if (L >= 0xC2 && L <= 0xDF) { *lo = (L & 0x1F) << 6; *hi = *lo + 63; return 1; }
    if (L >= 0xE0 && L <= 0xEF) { *lo = (L & 0x0F) << 12; *hi = *lo + 0xFFF; if (L == 0xE0) *lo = 0x800; return 1; }
    if (L >= 0xF0 && L <= 0xF4) { *lo = (L & 0x07) << 18; *hi = *lo + 0x3FFFF; if (L == 0xF0) *lo = 0x10000; if (L == 0xF4) *hi = 0x10FFFF; return 1; }
    return 0;
}

/* trailing incomplete character of w (under u): its byte count, 0 if w ends
   on a character boundary or in an ill-formed sequence */
static size_t partial_tail(const unsigned char *w, size_t n)
{
    for (size_t k = 1; k <= 3 && k <= n; k++) {
        unsigned c = w[n - k];
        if (c < 0x80) return 0;
        if (c >= 0xC0) {
            size_t need = c < 0xE0 ? 2 : c < 0xF0 ? 3 : 4;
            return (c >= 0xC2 && c <= 0xF4 && need > k) ? k : 0;
        }
    }
    return 0;
}

static unsigned char buf[1 << 16];

/* is ctx·w·b (b possibly opening or continuing a character) a prefix, under u
   with every completion of the incomplete character tried */
static int next_has(size_t cn, size_t wn, unsigned b)
{
    unsigned char *s = buf;
    size_t q = utf ? partial_tail(s + cn, wn) : 0;
    s[cn + wn] = (unsigned char)b;
    if (!utf)
        return is_prefix(s, cn + wn + 1, cn);
    /* the partial character after appending b */
    size_t base = cn + wn - q;
    unsigned char pre[4];
    size_t pn = q + 1;
    memcpy(pre, s + base, pn);
    unsigned L = pre[0];
    if (pn == 1 && L < 0x80)
        return is_prefix(s, cn + wn + 1, cn);
    unsigned lo, hi;
    if (!lead_range(L, &lo, &hi) || (pn > 1 && (b & 0xC0) != 0x80))
        return is_prefix(s, cn + wn + 1, cn);   /* ill-formed: probed as it is */
    for (unsigned c = lo; c <= hi; c++) {
        if (c >= 0xD800 && c <= 0xDFFF) continue;
        unsigned char e[4];
        int k = enc(c, e);
        if ((size_t)k < pn || memcmp(e, pre, pn) != 0) continue;
        if ((size_t)k == pn) {
            if (is_prefix(s, base + k, cn)) return 1;
            continue;
        }
        memcpy(s + base, e, (size_t)k);
        int r = is_prefix(s, base + k, cn);
        memcpy(s + base, pre, pn);
        if (r) return 1;
    }
    return 0;
}

int main(void)
{
    static char line[1 << 18];
    mctx = pcre2_match_context_create(NULL);
    pcre2_set_match_limit(mctx, 200000);
    pcre2_set_depth_limit(mctx, 20000);
    setvbuf(stdout, NULL, _IOFBF, 1 << 16);
    while (fgets(line, sizeof line, stdin)) {
        char *f[8] = {0};
        int nf = 0;
        line[strcspn(line, "\n")] = 0;
        for (char *p = line; nf < 8;) {
            f[nf++] = p;
            char *t = strchr(p, '\t');
            if (!t) break;
            *t = 0;
            p = t + 1;
        }
        switch (line[0]) {
        case 'V': {
            char v[64];
            pcre2_config(PCRE2_CONFIG_VERSION, v);
            printf("%s\n", v);
            break;
        }
        case 'P': {
            static unsigned char pat[1 << 16];
            size_t pn = unhex(f[2], pat);
            uint32_t opt = 0;
            utf = strchr(f[1], 'u') != NULL;
            if (strchr(f[1], 'i')) opt |= PCRE2_CASELESS;
            if (utf) opt |= PCRE2_UTF | PCRE2_MATCH_INVALID_UTF;
            if (md) pcre2_match_data_free(md);
            if (code) pcre2_code_free(code);
            md = NULL;
            int e; PCRE2_SIZE eo;
            code = pcre2_compile(pat, pn, opt, &e, &eo, NULL);
            if (!code) { printf("err %d\n", e); break; }
            md = pcre2_match_data_create_from_pattern(code, NULL);
            printf("ok\n");
            break;
        }
        case 'N': {
            size_t cn = unhex(f[1], buf);
            size_t wn = unhex(f[2], buf + cn);
            unsigned char set[32] = {0};
            for (unsigned b = 0; b < 256; b++)
                if (next_has(cn, wn, b)) set[b >> 3] |= (unsigned char)(1u << (b & 7));
            for (int i = 0; i < 32; i++) printf("%02x", set[i]);
            printf("\n");
            break;
        }
        case 'T': {
            size_t cn = unhex(f[1], buf);
            size_t wn = unhex(f[2], buf + cn);
            const char *t = f[3] ? f[3] : "";
            int first = 1;
            for (;;) {
                size_t tn = unhex(t, buf + cn + wn), e = 0;
                int rc = am(buf, cn + wn + tn, cn, 0, &e);
                printf("%s%ld", first ? "" : ",", rc >= 0 ? (long)(e - cn) : rc == PCRE2_ERROR_NOMATCH ? -1L : (long)rc * 1000);
                first = 0;
                t = strchr(t, ',');
                if (!t) break;
                t++;
            }
            printf("\n");
            break;
        }
        case 'F': {
            size_t n = unhex(f[1], buf);
            for (size_t sf = 0; sf <= n; sf++) {
                int rc = pcre2_match(code, buf, n, sf, 0, md, mctx);
                if (sf) putchar(',');
                if (rc >= 0) {
                    PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
                    printf("%zu:%zu", (size_t)ov[0], (size_t)ov[1]);
                } else if (rc == PCRE2_ERROR_NOMATCH) putchar('-');
                else printf("e%d", rc);
            }
            putchar('|');
            for (size_t pos = 0, first = 1; pos <= n;) {
                int rc = pcre2_match(code, buf, n, pos, 0, md, mctx);
                if (rc < 0) { if (rc != PCRE2_ERROR_NOMATCH) printf("%se%d", first ? "" : ",", rc); break; }
                PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
                printf("%s%zu:%zu", first ? "" : ",", (size_t)ov[0], (size_t)ov[1]);
                first = 0;
                pos = ov[1] > ov[0] ? ov[1] : ov[1] + 1;
            }
            putchar('\n');
            break;
        }
        default:
            printf("?\n");
        }
        fflush(stdout);
    }
    return 0;
}
