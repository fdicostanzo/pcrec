/* tests/kitproof/oracle.c — the libpcre2 side of answers.tsv ([KIT-VERIFY] Z2).
 *
 * Writes the EXPECTED answers run_cover.sh holds the harness-routed `cover`
 * artifacts to. It knows nothing of pcrec. Run only by gen_answers.sh, never
 * by `make test`: the expectations are committed, so the check needs no
 * libpcre2.
 *
 * stdin, one case per line: FLAGS TAB PATTERN_HEX TAB SUBJECT_HEX ("" = empty).
 * FLAGS is `-` or any of i (PCRE2_CASELESS), u (PCRE2_UTF |
 * PCRE2_MATCH_INVALID_UTF, pcrec -e utf8's contract); other letters (R) name a
 * pcrec arm and do not change PCRE2's answer.
 * stdout: the line, a TAB, the answer:
 *   an unanchored pcre2_match at every startoffset 0..n, comma-separated:
 *   "-" no match, "x" a startoffset on a UTF-8 continuation byte under u
 *   (pcrec's boundary guard refuses it; never compared), or every group's
 *   span "s:e" joined by "/" (an unset group "-1:-1");
 *   then "|" and the find-all loop's matches in the same span form
 *   (pos = end, +1 after an empty match).
 *
 *   gcc -O2 -std=gnu11 -o build/kitproof_oracle tests/kitproof/oracle.c -lpcre2-8
 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static size_t unhex(const char *h, unsigned char *out)
{
    size_t n = 0;
    while (h[0] && h[1] && h[0] != '\t' && h[0] != '\n') {
        unsigned v;
        sscanf(h, "%2x", &v);
        out[n++] = (unsigned char)v;
        h += 2;
    }
    return n;
}

static void spans(pcre2_match_data *md, int ng)
{
    PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
    for (int g = 0; g < ng; g++) {
        long a = ov[2 * g] == PCRE2_UNSET ? -1 : (long)ov[2 * g];
        long b = ov[2 * g + 1] == PCRE2_UNSET ? -1 : (long)ov[2 * g + 1];
        printf("%s%ld:%ld", g ? "/" : "", a, b);
    }
}

int main(void)
{
    static char line[1 << 16];
    static unsigned char pat[1 << 14], s[1 << 14];
    while (fgets(line, sizeof line, stdin)) {
        line[strcspn(line, "\n")] = 0;
        char *f1 = strchr(line, '\t'), *f2 = f1 ? strchr(f1 + 1, '\t') : NULL;
        if (!f2) { fprintf(stderr, "bad line: %s\n", line); return 2; }
        int utf = memchr(line, 'u', (size_t)(f1 - line)) != NULL;
        uint32_t opt = utf ? (PCRE2_UTF | PCRE2_MATCH_INVALID_UTF) : 0;
        if (memchr(line, 'i', (size_t)(f1 - line))) opt |= PCRE2_CASELESS;
        size_t pl = unhex(f1 + 1, pat), n = unhex(f2 + 1, s);
        int err; PCRE2_SIZE eo;
        pcre2_code *code = pcre2_compile(pat, pl, opt, &err, &eo, NULL);
        if (!code) { fprintf(stderr, "compile failed (%d): %s\n", err, line); return 2; }
        uint32_t cc;
        pcre2_pattern_info(code, PCRE2_INFO_CAPTURECOUNT, &cc);
        int ng = (int)cc + 1;
        pcre2_match_data *md = pcre2_match_data_create_from_pattern(code, NULL);
        printf("%s\t", line);
        for (size_t sf = 0; sf <= n; sf++) {
            if (sf) putchar(',');
            if (utf && sf < n && (s[sf] & 0xC0) == 0x80) { putchar('x'); continue; }
            int rc = pcre2_match(code, s, n, sf, 0, md, NULL);
            if (rc == PCRE2_ERROR_NOMATCH) putchar('-');
            else if (rc < 0) { fprintf(stderr, "match error %d: %s\n", rc, line); return 2; }
            else spans(md, ng);
        }
        putchar('|');
        size_t pos = 0;
        for (int it = 0; pos <= n; it++) {
            int rc = pcre2_match(code, s, n, pos, 0, md, NULL);
            if (rc < 0) break;
            PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
            if (it) putchar(',');
            spans(md, ng);
            pos = ov[1] > ov[0] ? ov[1] : ov[1] + 1;
        }
        putchar('\n');
        pcre2_match_data_free(md);
        pcre2_code_free(code);
    }
    return 0;
}
