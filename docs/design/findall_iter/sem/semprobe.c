/* docs/design/findall_iter/sem/semprobe.c — lane iterdes, [FINDALL-NEXT]
 * design probe (NO timing; answers only).
 *
 * For each input line `PATTERN<TAB>SUBJECT` (both in the .rxt subject-escape
 * vocabulary: \t \n \r \\ \xNN), compiles PATTERN with libpcre2-8 at
 * options 0 (byte mode; or PCRE2_UTF when the line starts with "U\t") and
 * runs two find-all loops over SUBJECT:
 *
 *   L  match_api.md §3.1.3's loop, transcribed: resume at the non-empty
 *      match's END (byte mode: next_pos(end - 1) == end; UTF: the next
 *      non-continuation byte at or after end), or one character past an
 *      EMPTY match's REPORTED START; no empty-match retry.
 *   G  pcre2demo.c's global loop (PCRE2 10.46's own documented idiom):
 *      after an EMPTY match at q, retry at q with
 *      PCRE2_NOTEMPTY_ATSTART|PCRE2_ANCHORED; on NOMATCH advance one
 *      character and search on. This is the semantics an iterator that
 *      "matches PCRE2" reports.
 *
 * Output, one line per input: `SAME|DIFF|SKIP <nL> <nG> <pattern> <subject>
 * L=spans G=spans`. The L loop is libpcre2 driven through pcrec's protocol,
 * so L == pcrec's own §3.1.3 answer wherever pcrec agrees with libpcre2 per
 * call (the corpus's per-call oracle); G is the independent expectation an
 * iterator implementing the retry must reproduce.
 *
 * Build: gcc -O1 -o semprobe semprobe.c -lpcre2-8
 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

static size_t next_char(const unsigned char *s, size_t n, size_t p, int utf)
{
    size_t i = p + 1;
    if (utf) while (i < n && (s[i] & 0xC0) == 0x80) i++;
    return i;
}

#define MAXSP 4096
typedef struct { size_t a[MAXSP][2]; int k; int err; } spans;

static void put(spans *sp, size_t a, size_t b)
{
    if (sp->k < MAXSP) { sp->a[sp->k][0] = a; sp->a[sp->k][1] = b; }
    sp->k++;
}

/* L: match_api.md §3.1.3 */
static void loop_L(pcre2_code *re, pcre2_match_data *md, const unsigned char *s,
                   size_t n, int utf, spans *sp)
{
    size_t p = 0;
    sp->k = 0; sp->err = 0;
    while (p <= n) {
        int rc = pcre2_match(re, s, n, p, 0, md, NULL);
        if (rc == PCRE2_ERROR_NOMATCH) break;
        if (rc < 0) { sp->err = rc; break; }
        PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
        if (ov[0] > ov[1]) { sp->err = -999; break; }   /* \K in a lookaround */
        put(sp, ov[0], ov[1]);
        p = ov[1] > ov[0] ? next_char(s, n, ov[1] - 1, utf)   /* K75: aligned end */
                          : next_char(s, n, ov[0], utf);      /* EMPTY: past its start */
        if (sp->k > 100000) { sp->err = -998; break; }
    }
}

/* G: pcre2demo.c's global loop (CRLF arm omitted: newline is LF) */
static void loop_G(pcre2_code *re, pcre2_match_data *md, const unsigned char *s,
                   size_t n, int utf, spans *sp)
{
    sp->k = 0; sp->err = 0;
    int rc = pcre2_match(re, s, n, 0, 0, md, NULL);
    if (rc == PCRE2_ERROR_NOMATCH) return;
    if (rc < 0) { sp->err = rc; return; }
    PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
    if (ov[0] > ov[1]) { sp->err = -999; return; }
    put(sp, ov[0], ov[1]);
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
                start_offset = next_char(s, n, startchar, utf);
            }
        }
        rc = pcre2_match(re, s, n, start_offset, options, md, NULL);
        if (rc == PCRE2_ERROR_NOMATCH) {
            if (options == 0) break;
            ov[1] = next_char(s, n, start_offset, utf);
            ov[0] = ov[1] - 1;              /* not empty: the next turn searches unanchored */
            if (ov[1] > n) break;
            continue;
        }
        if (rc < 0) { sp->err = rc; break; }
        if (ov[0] > ov[1]) { sp->err = -999; break; }
        put(sp, ov[0], ov[1]);
        if (sp->k > 100000) { sp->err = -998; break; }
    }
}

static void pr_sp(const spans *sp)
{
    for (int i = 0; i < sp->k && i < MAXSP; i++)
        printf("%s(%zu,%zu)", i ? " " : "", sp->a[i][0], sp->a[i][1]);
    if (sp->err) printf(" ERR%d", sp->err);
}

int main(void)
{
    static char line[1 << 20];
    static unsigned char pat[1 << 19], sub[1 << 19];
    long same = 0, diff = 0, skip = 0;
    while (fgets(line, sizeof line, stdin)) {
        size_t L = strlen(line);
        if (L && line[L - 1] == '\n') line[--L] = 0;
        if (!L || line[0] == '#') continue;
        char *t = line;
        int utf = 0;
        if (!strncmp(t, "U\t", 2)) { utf = 1; t += 2; }
        char *tab = strchr(t, '\t');
        if (!tab) continue;
        size_t pl = unesc(t, (size_t)(tab - t), pat);
        size_t sl = unesc(tab + 1, strlen(tab + 1), sub);
        int ec; PCRE2_SIZE eo;
        pcre2_code *re = pcre2_compile(pat, pl, utf ? PCRE2_UTF | PCRE2_MATCH_INVALID_UTF : 0,
                                       &ec, &eo, NULL);
        if (!re) { skip++; printf("SKIP compile\t%s\n", t); continue; }
        pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
        static spans a, g;
        loop_L(re, md, sub, sl, utf, &a);
        loop_G(re, md, sub, sl, utf, &g);
        int eq = a.k == g.k && !a.err && !g.err;
        for (int i = 0; eq && i < a.k && i < MAXSP; i++)
            eq = a.a[i][0] == g.a[i][0] && a.a[i][1] == g.a[i][1];
        if (a.err || g.err) { skip++; printf("SKIP err"); }
        else if (eq) { same++; printf("SAME"); }
        else { diff++; printf("DIFF"); }
        printf("\t%d\t%d\t%s\tL=", a.k, g.k, t);
        pr_sp(&a);
        printf("\tG=");
        pr_sp(&g);
        printf("\n");
        pcre2_match_data_free(md);
        pcre2_code_free(re);
    }
    fprintf(stderr, "semprobe: same=%ld diff=%ld skip=%ld\n", same, diff, skip);
    return 0;
}
