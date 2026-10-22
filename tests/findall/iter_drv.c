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
 *   info     rx_info.next / .next_n are this artifact's <p>_next / _next_n
 *   at1      rx_iter_at(&it, 1) answers libpcre2's global loop started at 1
 *            (or, on a no-retry artifact, the loop from 1)
 *
 * and the I4 arms (findall_iter_i2.md §5.1), each held to I's matches and
 * end code (I is held to G above, so they are held to G too):
 *   N1 N2 N3 N64  <p>_next_n at a fixed k, entries concatenated; the entries
 *            buffer is heap-allocated at exactly k * NCAPS pairs (an over-write
 *            is an ASan error in the ASan cells), every group compared
 *   nnnull   <p>_next_n with caps == NULL counts what I listed
 *   X        <p>_next and <p>_next_n(.., 2) alternating on one iterator
 *   F        RX_FOREACH(&<p>_info, ..), refused (no body, PCREC_ERR_ITER)
 *            where the record's ncaps exceeds RX_FOREACH_PAIRS
 *   Fstop    RX_FOREACH with a break after j = 1, 3, 5, 7: I's first j
 *   N0       <p>_next_n(.., 0) is inert on a FRESH (the setter after it
 *            still applies), a BOUND (the continuation is I's) and an ENDED
 *            (returns 0, rc kept) iterator
 *   Fcount   RX_FOREACH over a copy of the record whose next_n counts its
 *            calls: the count equals a simulation of the fills (1, 2, 4, ..
 *            capped at min(64, RX_FOREACH_PAIRS / ncaps)) over I's matches
 *   Fabi     RX_FOREACH over a copy with abi + 1: no body, rc ==
 *            PCREC_ERR_ITER, ENDED, lo untouched
 * R= lists the REACH tokens of the cell (run_iter_diff.sh counts them, K35):
 * the condition each sabotage row's witness needs (§5.4).
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

/* I4: drains `it` through <p>_next_n at a fixed k into `o`. `split` counts
 * the calls that returned k with the retry bit set (a batch boundary between
 * an empty match and its retry), `gumid` the calls that returned 1..k-1
 * entries and then a code. */
static void nn_drain(rx_iter *it, Out *o, size_t k, int *split, int *gumid)
{
    ptrdiff_t (*e)[2] = malloc(sizeof(*e) * NCAPS * k);
    if (!e) abort();
    out_reset(o);
    for (;;) {
        size_t r = F(_next_n)(it, e, k);
        for (size_t i = 0; i < r; i++)
            out_match(o, (const ptrdiff_t (*)[2])(e + i * NCAPS), ngroups);
        if (r == k && (it->flags & PCREC_ITER_F_RETRY)) (*split)++;
        if (r < k) { if (r >= 1 && it->rc < 0) (*gumid)++; break; }
        if (o->k >= MAXM) break;
    }
    out_end(o, it->rc);
    free(e);
}

/* I4: <p>_next and <p>_next_n(.., 2) alternating on one iterator. */
static void x_drain(rx_iter *it, Out *o)
{
    ptrdiff_t (*e)[2] = malloc(sizeof(*e) * NCAPS * 2);
    if (!e) abort();
    out_reset(o);
    for (int turn = 0; o->k < MAXM; turn ^= 1) {
        if (!turn) {
            if (!F(_next)(it, e)) break;
            out_match(o, (const ptrdiff_t (*)[2])e, ngroups);
        } else {
            size_t r = F(_next_n)(it, e, 2);
            for (size_t i = 0; i < r; i++)
                out_match(o, (const ptrdiff_t (*)[2])(e + i * NCAPS), ngroups);
            if (r < 2) break;
        }
    }
    out_end(o, it->rc);
    free(e);
}

/* I4: RX_FOREACH over `info`; `stop` > 0 breaks after that many matches and
 * then writes no end code (the iterator's rc is not meaningful after an early
 * exit, match_api.md §3.8.2¶4). Returns the number of bodies run. */
static int fe_drain(const struct rx_info *info, rx_iter *it, Out *o, int stop)
{
    int j = 0;
    out_reset(o);
    RX_FOREACH(info, it, m) {
        out_match(o, (const ptrdiff_t (*)[2])m, ngroups);
        if (++j == stop || o->k >= MAXM) break;
    }
    if (stop == 0) out_end(o, it->rc);
    return j;
}

static size_t fcount_calls;
static size_t fcount_next_n(struct rx_iter *it, ptrdiff_t (*c)[2], size_t k)
{
    fcount_calls++;
    return F(_next_n)(it, c, k);
}

/* The calls RX_FOREACH makes for `mm` matches, by simulating its fills: the
 * first asks 1, each full fill doubles up to kmax, and the first fill that
 * returns fewer than it asked is the last (0 where kmax is 0: refused). */
static size_t fills_for(size_t mm, size_t kmax)
{
    size_t calls = 0, got = 0, k = 1;
    if (kmax == 0) return 0;
    for (;;) {
        calls++;
        if (mm - got < k) return calls;
        got += k;
        if (k < kmax) k = 2 * k < kmax ? 2 * k : kmax;
    }
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
    size_t ncaps_rec = F(_info).ncaps > 0 ? (size_t)F(_info).ncaps : 0;
    size_t kmax = ncaps_rec && ncaps_rec <= RX_FOREACH_PAIRS ? RX_FOREACH_PAIRS / ncaps_rec : 0;
    if (kmax > 64) kmax = 64;
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
        if (F(_info).next != F(_next) || F(_info).next_n != F(_next_n))
            strcat(fail, " info");   /* rx_info.next / .next_n, match_api.md §6¶14b-c */

        /* ---- the I4 arms (findall_iter_i2.md §5.1) ---- */
        char reach[256] = "";
        size_t mI = (size_t)oI.k;
        int split = 0, gumid = 0;
        {
            static const size_t ks[] = { 1, 2, 3, 64 };
            static const char *const kn[] = { " N1", " N2", " N3", " N64" };
            for (int q = 0; q < 4; q++) {
                rx_iter in = RX_ITER_INIT(s, n);
                int gm = 0;
                nn_drain(&in, &oX, ks[q], &split, &gm);
                if (strcmp(oX.p, oI.p) != 0) strcat(fail, kn[q]);
                if (ks[q] == 64 && gm) gumid = 1;
                if (ks[q] == 3 && mI >= 4) strcat(reach, " n3m4");
            }
            rx_iter iz = RX_ITER_INIT(s, n);
            size_t cnt = 0, r = 0;
            while (cnt <= MAXM && (r = F(_next_n)(&iz, NULL, 3)) == 3) cnt += r;
            if (cnt <= MAXM) cnt += r;
            if (cnt != mI || iz.rc != rc) strcat(fail, " nnnull");
        }
        if (split) strcat(reach, " split");
        if (gumid) strcat(reach, " gumid");
        if (rc == 0 && mI >= 1 && mI <= 63) strcat(reach, " done63");
        if (NCAPS > 1 && F(_info).engine == PCREC_ENGINE_VM && mI >= 2) strcat(reach, " vmcaps2");
        {
            rx_iter ix = RX_ITER_INIT(s, n);
            x_drain(&ix, &oX);
            if (strcmp(oX.p, oI.p) != 0) strcat(fail, " X");
        }
        {
            rx_iter ifr = RX_ITER_INIT(s, n);
            int ran = fe_drain(&F(_info), &ifr, &oX, 0);
            if (kmax == 0) {
                if (ran || ifr.rc != PCREC_ERR_ITER || ifr.hdr != PCREC_ITER_ENDED) strcat(fail, " F");
                strcat(reach, " frefused");
            } else {
                if (strcmp(oX.p, oI.p) != 0) strcat(fail, " F");
                if (mI >= 1) strcat(reach, " f1");
                if (mI >= 2) strcat(reach, " f2");
                if (kmax < 64 && mI >= 3) strcat(reach, " kmaxcap");
            }
        }
        if (kmax) {
            static const int js[] = { 1, 3, 5, 7 };   /* 1, 3, 7 end the fills 1, 2, 4 */
            int atend = 0;
            for (int q = 0; q < 4; q++) {
                rx_iter is = RX_ITER_INIT(s, n), ij = RX_ITER_INIT(s, n);
                fe_drain(&F(_info), &is, &oX, js[q]);
                out_reset(&oY);
                for (int t = 0; t < js[q] && F(_next)(&ij, c); t++)
                    out_match(&oY, (const ptrdiff_t (*)[2])c, ngroups);
                if (strcmp(oX.p, oY.p) != 0) { strcat(fail, " Fstop"); break; }
                if (js[q] != 5 && mI > (size_t)js[q]) atend = 1;
            }
            if (atend) strcat(reach, " fstopend");
        }
        {
            ptrdiff_t (*e)[2] = malloc(sizeof(*e) * NCAPS);
            int ok = 1;
            if (!e) abort();
            rx_iter i0 = RX_ITER_INIT(s, n);                /* FRESH */
            if (F(_next_n)(&i0, e, 0) != 0) ok = 0;
            rx_iter_at(&i0, 0);
            iter_drain(&i0, &oX);
            if (strcmp(oX.p, oI.p) != 0) ok = 0;
            strcat(reach, " n0fresh");
            rx_iter i1 = RX_ITER_INIT(s, n);                /* BOUND */
            if (F(_next)(&i1, c)) {
                out_reset(&oY);
                out_match(&oY, (const ptrdiff_t (*)[2])c, ngroups);
                if (F(_next_n)(&i1, e, 0) != 0) ok = 0;
                while (oY.k < MAXM && F(_next)(&i1, c)) out_match(&oY, (const ptrdiff_t (*)[2])c, ngroups);
                out_end(&oY, i1.rc);
                if (strcmp(oY.p, oI.p) != 0) ok = 0;
                if (mI >= 2) strcat(reach, " n0bound");
            }
            if (F(_next_n)(&it, e, 0) != 0 || it.rc != rc ||       /* ENDED */
                F(_next_n)(&it, e, 3) != 0 || it.rc != rc) ok = 0;
            strcat(reach, " n0ended");
            if (!ok) strcat(fail, " N0");
            free(e);
        }
        if (kmax) {
            struct rx_info ci = F(_info);
            ci.next_n = fcount_next_n;
            rx_iter icn = RX_ITER_INIT(s, n);
            fcount_calls = 0;
            fe_drain(&ci, &icn, &oX, 0);
            if (strcmp(oX.p, oI.p) != 0 || fcount_calls != fills_for(mI, kmax)) strcat(fail, " Fcount");
            if (mI >= 2) strcat(reach, " fcount2");
            if (mI >= 63) strcat(reach, " fcount63");
        }
        {
            struct rx_info ca = F(_info);
            ca.abi += 1;
            rx_iter iab = RX_ITER_INIT(s, n);
            iab.lo = 0x5A5A;
            int ran = fe_drain(&ca, &iab, &oX, 0);
            if (ran || iab.rc != PCREC_ERR_ITER || iab.hdr != PCREC_ITER_ENDED || iab.lo != 0x5A5A)
                strcat(fail, " Fabi");
            strcat(reach, " fabi");
        }

        const char *v;
        if (g < 0) v = "SKIP";
        else if (strcmp(oI.p, oG.p) == 0) v = fail[0] ? "DIFF" : "OK";
        else if (rc < 0 && prefix_of(&oI, &oG)) v = fail[0] ? "DIFF" : "GIVEUP";
        else if (utf && !utf8_ok(s, n) && strcmp(oI.p, oL.p) == 0) v = fail[0] ? "DIFF" : "ILLFORMED";
        else { v = "DIFF"; strcat(fail, " answer"); }
        printf("%s\tI=%s\tG=%s\tL=%s\tR=%s%s%s\n", v, oI.p, g < 0 ? "-" : oG.p, oL.p,
               reach, fail[0] ? "\tFAIL=" : "", fail);
#undef it
        free(itp);
    }
    free(oI.p); free(oG.p); free(oL.p); free(oX.p); free(oY.p);
    pcre2_match_data_free(md);
    pcre2_code_free(re);
    return 0;
}
