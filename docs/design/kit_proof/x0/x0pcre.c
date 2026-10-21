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
 *   K                        -> how many anchored calls PCRE2 answered with a
 *                               match NOT starting at the origin (counted as
 *                               no match; MATCH_INVALID_UTF, see am())
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
 *   Q HEXCTX HEXW H [BUDGET] -> "SET UNKNOWN", two 256-bit sets: N's set with
 *                               every byte VALIDATED by a witness, a complete
 *                               match from the origin covering W·b within H
 *                               more bytes (see next_valid); UNKNOWN = the
 *                               witness search ran out of BUDGET match calls
 *                               (default 200000 per byte). A sixth field
 *                               "u": reaching H with no witness is UNKNOWN
 *                               too (used where H is not a known match width).
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

/* the anchored match: rc, and the end offset in *end. A match (or partial)
   that does not START at `start` is no match: libpcre2 10.46 under
   MATCH_INVALID_UTF returns an ANCHORED match that begins past a leading
   invalid sequence (`a` on "\x80a" from 0 gives (1,2)), measured here */
static long anchor_skips;
static int am(const unsigned char *s, size_t n, size_t start, uint32_t opt, size_t *end)
{
    int rc = pcre2_match(code, s, n, start, PCRE2_ANCHORED | opt, md, mctx);
    if (rc >= 0 || rc == PCRE2_ERROR_PARTIAL) {
        PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
        if (ov[0] != start) {
            anchor_skips++;
            return PCRE2_ERROR_NOMATCH;
        }
        *end = ov[1];
    }
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

/* ---- the VALIDATED next set (Q) -------------------------------------------
 * Hard partial matching over-approximates "a prefix of a match": PARTIAL is
 * returned whenever the subject ends while an assertion is still pending (`\b`,
 * `$`, a lookahead at the end; `(?:a*\b)*b` reads "a" as a prefix of a match
 * no string has), and under MATCH_INVALID_UTF at the end of every valid
 * FRAGMENT (`@é` reads "@\xC3@" as a prefix). So a byte is in Q's set only
 * with a WITNESS: a complete PCRE2 match, anchored at the origin, whose span
 * covers W·b (b's character completed under u), found by a depth-first
 * search through hard-partial prefixes within H more bytes. A search that
 * runs out of budget marks the byte UNKNOWN (the second set). */
static const unsigned char *tails_b[1024];
static size_t tails_n[1024];
static int ntails;
static unsigned char tailbuf[4096];
static long budget;
static int hz_unknown;   /* a horizon reached with no witness is UNKNOWN, not "no" */

static void build_tails(void)
{
    size_t o = 0;
    ntails = 0;
    tails_b[ntails] = tailbuf; tails_n[ntails++] = 0;
    for (unsigned b = 0; b < 256; b++) {
        tailbuf[o] = (unsigned char)b;
        tails_b[ntails] = tailbuf + o; tails_n[ntails++] = 1; o++;
    }
    if (!utf) return;
    for (unsigned L = 0xC2; L <= 0xF4; L++) {
        unsigned lo, hi;
        if (!lead_range(L, &lo, &hi)) continue;
        unsigned mid = (lo + hi) / 2;
        if (mid >= 0xD800 && mid <= 0xDFFF) mid = 0xE000;
        unsigned cs[3] = {lo, mid, hi};
        for (int i = 0; i < 3; i++) {
            int k = enc(cs[i], tailbuf + o);
            tails_b[ntails] = tailbuf + o; tails_n[ntails++] = (size_t)k; o += (size_t)k;
        }
    }
}

/* a complete match from the origin covering buf[cn .. cn+wn) */
static int covered(size_t cn, size_t wn)
{
    for (int i = 0; i < ntails; i++) {
        size_t e = 0;
        memcpy(buf + cn + wn, tails_b[i], tails_n[i]);
        budget--;
        int rc = am(buf, cn + wn + tails_n[i], cn, 0, &e);
        if (rc >= 0 && e >= cn + wn) return 1;
    }
    return 0;
}

/* 1 a witness exists within H more bytes, 0 none, -1 budget out. buf holds
   ctx·w with w ending on a character boundary (under u). */
static int valid(size_t cn, size_t wn, int H)
{
    if (budget <= 0) return -1;
    if (covered(cn, wn)) return 1;
    if (H <= 0) return hz_unknown ? -1 : 0;
    int unknown = 0;
    for (unsigned b = 0; b < (utf ? 0x80u : 256u); b++) {
        buf[cn + wn] = (unsigned char)b;
        budget--;
        if (!is_prefix(buf, cn + wn + 1, cn)) continue;
        int v = valid(cn, wn + 1, H - 1);
        if (v == 1) return 1;
        if (v < 0) unknown = 1;
        if (budget <= 0) return -1;
    }
    if (utf) {
        for (unsigned c = 0x80; c <= 0x10FFFF; c++) {
            if (c >= 0xD800 && c <= 0xDFFF) continue;
            int k = enc(c, buf + cn + wn);
            if (k > H) break;
            budget--;
            if (!is_prefix(buf, cn + wn + (size_t)k, cn)) continue;
            int v = valid(cn, wn + (size_t)k, H - k);
            if (v == 1) return 1;
            if (v < 0) unknown = 1;
            if (budget <= 0) return -1;
        }
    }
    return unknown ? -1 : 0;
}

/* Q's per-byte decision: 1 / 0 / -1, as next_has but with a witness */
static int next_valid(size_t cn, size_t wn, unsigned b, int H)
{
    unsigned char *s = buf;
    size_t q = utf ? partial_tail(s + cn, wn) : 0;
    s[cn + wn] = (unsigned char)b;
    if (!utf || (q == 0 && b < 0x80)) {
        if (!is_prefix(s, cn + wn + 1, cn)) return 0;
        return valid(cn, wn + 1, H - 1);
    }
    size_t base = cn + wn - q;
    unsigned char pre[4];
    size_t pn = q + 1;
    memcpy(pre, s + base, pn);
    unsigned lo, hi;
    if (!lead_range(pre[0], &lo, &hi) || (pn > 1 && (b & 0xC0) != 0x80)) {
        /* ill-formed: a witness must cover it as it stands */
        if (!is_prefix(s, cn + wn + 1, cn)) return 0;
        return covered(cn, wn + 1);
    }
    int unknown = 0;
    for (unsigned c = lo; c <= hi; c++) {
        if (c >= 0xD800 && c <= 0xDFFF) continue;
        unsigned char e[4];
        int k = enc(c, e);
        if ((size_t)k < pn || memcmp(e, pre, pn) != 0) continue;
        memcpy(s + base, e, (size_t)k);
        size_t wn2 = base + (size_t)k - cn;
        int v = 0;
        if (is_prefix(s, cn + wn2, cn))
            v = valid(cn, wn2, H - (int)(wn2 - wn));
        memcpy(s + base, pre, pn);
        if (v == 1) return 1;
        if (v < 0) unknown = 1;
        if (budget <= 0) return -1;
    }
    return unknown ? -1 : 0;
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
        case 'K':   /* the anchored-match-not-at-origin count so far */
            printf("%ld\n", anchor_skips);
            break;
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
            build_tails();
            printf("ok\n");
            break;
        }
        case 'Q': {
            size_t cn = unhex(f[1], buf);
            size_t wn = unhex(f[2], buf + cn);
            int H = f[3] ? atoi(f[3]) : 0;
            long per = f[4] ? atol(f[4]) : 200000;
            hz_unknown = f[5] && f[5][0] == 'u';
            unsigned char set[32] = {0}, unk[32] = {0};
            for (unsigned b = 0; b < 256; b++) {
                budget = per;
                int v = next_valid(cn, wn, b, H);
                if (v == 1) set[b >> 3] |= (unsigned char)(1u << (b & 7));
                if (v < 0) unk[b >> 3] |= (unsigned char)(1u << (b & 7));
            }
            for (int i = 0; i < 32; i++) printf("%02x", set[i]);
            putchar(' ');
            for (int i = 0; i < 32; i++) printf("%02x", unk[i]);
            printf("\n");
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
