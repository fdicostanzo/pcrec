/* tests/findall/iter_drv.c -- [FINDALL-NEXT] the find-all iterator's answer
 * driver (findall_iter.md §6.7). Built against ONE artifact with
 * -DPFX=<prefix> -DPFXU=<PREFIX> -DHDR="<prefix>.h" and linked with
 * libpcre2-8, the independent oracle.
 *
 * argv[1] is the pattern as written (the bytes `pcrec --pattern` compiled),
 * argv[2] the oracle's options ("byte" or "utf"), argv[3] "1" when the
 * artifact can report an empty span (its retry is emitted) and "0" otherwise.
 * Each stdin line is one subject in the same vocabulary. For each subject it
 * prints one line, TAB-separated, verdict first:
 *
 *   OK|DIFF|GIVEUP|SKIP  then I=, G=, L= and the failed arms' names
 *
 *   I   <p>_next with a caps buffer, every pair (`(s,e)`, groups after `/`)
 *   G   libpcre2's global loop over the same subject (pcre2demo.c's: after an
 *       empty match retry at its position with NOTEMPTY_ATSTART|ANCHORED, on
 *       no match advance one character), the same pairs -- the expectation
 *   L   match_api.md §3.1.3's loop over <p>_search + <p>_next_pos, which the
 *       iterator must equal on an artifact that cannot report an empty span
 *       (a REGRESSION control: it shares the engine with the iterator)
 *
 * and, every subject, the state-machine arms (their names print on failure):
 *   sticky   a call after the end returns 0 and leaves rc as it was
 *   endset   a setter on the ENDED iterator changes nothing (IT8)
 *   nullcaps <p>_next with caps == NULL counts what I listed (IT10)
 *   poison   a setter on a BOUND iterator makes the next call refuse with
 *            PCREC_ERR_ITER; a zeroed header refuses too
 *   dirty    every field RX_ITER_INIT does not write holds 0xA5 garbage, and
 *            the answers are I's (bind normalizes them, IT1)
 *   info     rx_info.next is this artifact's <p>_next
 *   at1      rx_iter_at(&it, 1) answers libpcre2's global loop started at 1
 *            (or, on a no-retry artifact, the loop from 1)
 *
 * ILLFORMED: a utf subject that is not well-formed UTF-8, where the iterator
 * answers what match_api.md §3.1.3's loop answers and libpcre2 (under
 * MATCH_INVALID_UTF) answers otherwise: the documented boundary difference
 * over ill-formed input (match_api.md §9), not the iterator's; counted.
 * GIVEUP: the iterator ended with a give-up code where libpcre2 answered; the
 * loop must then give up at the same match (checked), and the cell is counted
 * apart, never as a pass. SKIP: libpcre2 refused the subject or the pattern.
 * A DIFF line's I/G/L are what the runner reports.
 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CAT2(a, b) a##b
#define CAT(a, b) CAT2(a, b)
#define F(x) CAT(PFX, x)
#include HDR

#define NCAPS CAT(PFXU, _NCAPS)
#define MAXM 4096

static size_t unesc(const char *in, size_t len, unsigned char *out)
{
    size_t o = 0;
    for (size_t i = 0; i < len; i++) {
        if (in[i] == '\\' && i + 1 < len) {
            char c = in[i + 1];
            if (c == 't') { out[o++] = '\t'; i++; continue; }
            if (c == 'n') { out[o++] = '\n'; i++; continue; }
            if (c == 'r') { out[o++] = '\r'; i++; continue; }
            if (c == '\\') { out[o++] = '\\'; i++; continue; }
            if (c == 'x' && i + 3 < len) {
                char h[3] = { in[i + 2], in[i + 3], 0 };
                out[o++] = (unsigned char)strtoul(h, NULL, 16);
                i += 3;
                continue;
            }
        }
        out[o++] = (unsigned char)in[i];
    }
    return o;
}

typedef struct { char *p; size_t len, cap; int k; int code; } Out;

static void out_reset(Out *o)
{
    if (!o->p) {
        o->cap = 256;
        o->p = malloc(o->cap);
        if (!o->p) abort();
    }
    o->len = 0; o->k = 0; o->code = 0; o->p[0] = 0;
}

static void out_put(Out *o, const char *s)
{
    size_t l = strlen(s);
    if (o->len + l + 1 > o->cap) {
        o->cap = (o->len + l + 1) * 2;
        o->p = realloc(o->p, o->cap);
        if (!o->p) abort();
    }
    memcpy(o->p + o->len, s, l + 1);
    o->len += l;
}

/* One match: its pairs, groups after a `/`, unset as -1. */
static void out_match(Out *o, const ptrdiff_t (*c)[2], int ng)
{
    char b[64];
    snprintf(b, sizeof b, "%s(%td,%td)", o->k++ ? " " : "", c[0][0], c[0][1]);
    out_put(o, b);
    for (int g = 1; g < ng; g++) {
        snprintf(b, sizeof b, "%s%td,%td", g == 1 ? "/" : ";", c[g][0], c[g][1]);
        out_put(o, b);
    }
}

static void out_end(Out *o, int code)
{
    char b[32];
    o->code = code;
    if (code < 0) { snprintf(b, sizeof b, " GU%d", code); out_put(o, b); }
}

static int ngroups;   /* pairs compared: min(NCAPS, libpcre2's own) */

/* Drains an iterator into `o`. The caps buffer is heap-allocated at its
 * exact size, so a write past NCAPS pairs is an ASan error under the ASan
 * cells (a stack array would absorb it). */
static void iter_drain(rx_iter *it, Out *o)
{
    ptrdiff_t (*c)[2] = malloc(sizeof(*c) * NCAPS);
    if (!c) abort();
    out_reset(o);
    while (o->k < MAXM && F(_next)(it, c)) out_match(o, (const ptrdiff_t (*)[2])c, ngroups);
    out_end(o, it->rc);
    free(c);
}

/* match_api.md §3.1.3's loop from `p`. */
static void loop_from(const unsigned char *s, size_t n, size_t p, Out *o)
{
    ptrdiff_t c[NCAPS][2];
    out_reset(o);
    while (p <= n && o->k < MAXM) {
        int r = F(_search)(s, n, p, c);
        if (r != 1) { out_end(o, r < 0 ? r : 0); return; }
        out_match(o, (const ptrdiff_t (*)[2])c, ngroups);
        p = c[0][1] > c[0][0] ? F(_next_pos)(s, n, (size_t)c[0][1] - 1)
                              : F(_next_pos)(s, n, (size_t)c[0][0]);
    }
    out_end(o, 0);
}

static int utf;

static size_t next_char(const unsigned char *s, size_t n, size_t p)
{
    size_t i = p + 1;
    if (utf) while (i < n && (s[i] & 0xC0) == 0x80) i++;
    return i;
}

/* One libpcre2 match's pairs into `o`; false where \K made start > end. */
static int g_put(Out *o, pcre2_match_data *md, int rc)
{
    PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
    ptrdiff_t c[NCAPS][2];
    if (ov[0] > ov[1]) return 0;
    for (int g = 0; g < ngroups; g++) {
        int set = g < rc && ov[2 * g] != PCRE2_UNSET;
        c[g][0] = set ? (ptrdiff_t)ov[2 * g] : -1;
        c[g][1] = set ? (ptrdiff_t)ov[2 * g + 1] : -1;
    }
    out_match(o, (const ptrdiff_t (*)[2])c, ngroups);
    return 1;
}

/* pcre2demo.c's global loop from `from` (the CRLF arm omitted: pcrec refuses
 * the newline verbs, so the newline is LF). Returns -1 where libpcre2 refused. */
static int loop_G(pcre2_code *re, pcre2_match_data *md, const unsigned char *s,
                  size_t n, size_t from, Out *o)
{
    out_reset(o);
    int rc = pcre2_match(re, s, n, from, 0, md, NULL);
    if (rc == PCRE2_ERROR_NOMATCH) { out_end(o, 0); return 0; }
    if (rc < 0) return -1;
    if (!g_put(o, md, rc)) return -1;
    PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
    for (;;) {
        uint32_t options = 0;
        PCRE2_SIZE start_offset = ov[1];
        if (ov[0] == ov[1]) {
            if (ov[0] == n) break;
            options = PCRE2_NOTEMPTY_ATSTART | PCRE2_ANCHORED;
        } else {
            PCRE2_SIZE startchar = pcre2_get_startchar(md);
            if (start_offset <= startchar) {
                if (startchar >= n) break;
                start_offset = next_char(s, n, startchar);
            }
        }
        rc = pcre2_match(re, s, n, start_offset, options, md, NULL);
        if (rc == PCRE2_ERROR_NOMATCH) {
            if (options == 0) break;
            ov[1] = next_char(s, n, start_offset);
            ov[0] = ov[1] - 1;
            if (ov[1] > n) break;
            continue;
        }
        if (rc < 0) return -1;
        if (!g_put(o, md, rc)) return -1;
        if (o->k >= MAXM) break;
    }
    out_end(o, 0);
    return 0;
}

/* Is s[0, n) well-formed UTF-8 (RFC 3629: no overlongs, surrogates or
 * code points above U+10FFFF)? */
static int utf8_ok(const unsigned char *s, size_t n)
{
    size_t i = 0;
    while (i < n) {
        unsigned c = s[i];
        size_t k;
        unsigned lo = 0x80, hi = 0xBF;
        if (c < 0x80) { i++; continue; }
        if (c >= 0xC2 && c <= 0xDF) k = 1;
        else if (c >= 0xE0 && c <= 0xEF) { k = 2; if (c == 0xE0) lo = 0xA0; if (c == 0xED) hi = 0x9F; }
        else if (c >= 0xF0 && c <= 0xF4) { k = 3; if (c == 0xF0) lo = 0x90; if (c == 0xF4) hi = 0x8F; }
        else return 0;
        for (size_t j = 1; j <= k; j++) {
            if (i + j >= n) return 0;
            unsigned b = s[i + j];
            if (j == 1 ? (b < lo || b > hi) : (b < 0x80 || b > 0xBF)) return 0;
        }
        i += k + 1;
    }
    return 1;
}

/* `a` equals `b` up to `a`'s give-up: `a` is a prefix of `b`'s matches. */
static int prefix_of(const Out *a, const Out *b)
{
    const char *gu = strstr(a->p, " GU");
    size_t l = gu ? (size_t)(gu - a->p) : a->len;
    return strncmp(a->p, b->p, l) == 0;
}

int main(int argc, char **argv)
{
    static char line[1 << 20];
    static unsigned char pat[1 << 18], s[1 << 19];
    if (argc < 4) { fprintf(stderr, "usage: iter_drv PATTERN byte|utf 0|1\n"); return 2; }
    size_t pl = strlen(argv[1]);
    memcpy(pat, argv[1], pl);
    utf = strcmp(argv[2], "utf") == 0;
    int retry = argv[3][0] == '1';
    int errc;
    PCRE2_SIZE erro;
    pcre2_code *re = pcre2_compile(pat, pl, utf ? (PCRE2_UTF | PCRE2_MATCH_INVALID_UTF) : 0,
                                   &errc, &erro, NULL);
    pcre2_match_data *md = re ? pcre2_match_data_create_from_pattern(re, NULL) : NULL;
    uint32_t pc = 0;
    if (re) pcre2_pattern_info(re, PCRE2_INFO_CAPTURECOUNT, &pc);
    ngroups = (int)pc + 1 < NCAPS ? (int)pc + 1 : NCAPS;
    Out oI = { 0 }, oG = { 0 }, oL = { 0 }, oX = { 0 }, oY = { 0 };
    ptrdiff_t c[NCAPS][2];
    while (fgets(line, sizeof line, stdin)) {
        size_t len = strlen(line);
        if (len && line[len - 1] == '\n') line[--len] = 0;
        size_t n = unesc(line, len, s);
        char fail[256] = "";

        rx_iter *itp = malloc(sizeof *itp);   /* heap: exact size, as the caps */
        if (!itp) abort();
        *itp = RX_ITER_INIT(s, n);
#define it (*itp)
        iter_drain(&it, &oI);
        int rc = it.rc;
        loop_from(s, n, 0, &oL);
        int g = re ? loop_G(re, md, s, n, 0, &oG) : -1;

        /* the state-machine arms */
        if (F(_next)(&it, c) || it.rc != rc) strcat(fail, " sticky");
        rx_iter_at(&it, 0);
        if (it.hdr != PCREC_ITER_ENDED || it.rc != rc || F(_next)(&it, c)) strcat(fail, " endset");
        {
            rx_iter iz = RX_ITER_INIT(s, n);
            int k = 0;
            while (k <= MAXM && F(_next)(&iz, NULL)) k++;
            if (k != oI.k || iz.rc != rc) strcat(fail, " nullcaps");
        }
        {
            int ok = 1;
            rx_iter ip = RX_ITER_INIT(s, n);
            if (F(_next)(&ip, c) && ip.hdr == PCREC_ITER_BOUND) {
                rx_iter_at(&ip, 0);
                if (F(_next)(&ip, c) || ip.rc != PCREC_ERR_ITER || ip.hdr != PCREC_ITER_ENDED) ok = 0;
            }
            rx_iter ig;
            memset(&ig, 0, sizeof ig);
            if (F(_next)(&ig, c) || ig.rc != PCREC_ERR_ITER) ok = 0;
            if (!ok) strcat(fail, " poison");
        }
        {
            rx_iter id;
            memset(&id, 0xA5, sizeof id);
            rx_iter fresh = RX_ITER_INIT(s, n);
            id.hdr = fresh.hdr; id.s = fresh.s; id.n = fresh.n;
            iter_drain(&id, &oX);
            if (strcmp(oX.p, oI.p) != 0) strcat(fail, " dirty");
        }
        if (n >= 1 && (!utf || (s[1 % (n + 1)] & 0xC0) != 0x80)) {
            rx_iter ia = RX_ITER_INIT(s, n);
            rx_iter_at(&ia, 1);
            iter_drain(&ia, &oX);
            int ok;
            if (retry) {
                ok = re && loop_G(re, md, s, n, 1, &oY) == 0 ? (strcmp(oX.p, oY.p) == 0 ||
                     (oX.code < 0 && prefix_of(&oX, &oY))) : 1;
            } else {
                loop_from(s, n, 1, &oY);
                ok = strcmp(oX.p, oY.p) == 0;
            }
            if (!ok) strcat(fail, " at1");
        }
        if (!retry && strcmp(oI.p, oL.p) != 0) strcat(fail, " loop");
        if (F(_info).next != F(_next)) strcat(fail, " info");   /* rx_info.next, match_api.md §6¶14b */

        const char *v;
        if (g < 0) v = "SKIP";
        else if (strcmp(oI.p, oG.p) == 0) v = fail[0] ? "DIFF" : "OK";
        else if (rc < 0 && prefix_of(&oI, &oG)) v = fail[0] ? "DIFF" : "GIVEUP";
        else if (utf && !utf8_ok(s, n) && strcmp(oI.p, oL.p) == 0) v = fail[0] ? "DIFF" : "ILLFORMED";
        else { v = "DIFF"; strcat(fail, " answer"); }
        printf("%s\tI=%s\tG=%s\tL=%s%s%s\n", v, oI.p, g < 0 ? "-" : oG.p, oL.p,
               fail[0] ? "\tFAIL=" : "", fail);
#undef it
        free(itp);
    }
    free(oI.p); free(oG.p); free(oL.p); free(oX.p); free(oY.p);
    pcre2_match_data_free(md);
    pcre2_code_free(re);
    return 0;
}
