/* oracle_probe.c — D27 quoting corpus oracle: a thin CLI wrapper over
 * libpcre2-8, used to derive every expectation in this corpus's .rxt files
 * from PCRE2 itself, never from reasoning about the documentation alone.
 *
 * Build:
 *   gcc -O2 -Wall -Wextra -o oracle_probe oracle_probe.c \
 *       $(pkg-config --cflags --libs libpcre2-8)
 * (or: gcc -O2 -Wall -Wextra -o oracle_probe oracle_probe.c -lpcre2-8)
 *
 * Usage:
 *   oracle_probe version
 *       -> prints the PCRE2_CONFIG_VERSION string
 *
 *   oracle_probe compile <pattern> [flags]
 *       -> "OK" if <pattern> compiles under the given flags (only 'i' is
 *          recognized, mapped to PCRE2_CASELESS — matches this project's
 *          .rxt `flags i` directive), or "ERROR <code> <offset>" giving
 *          PCRE2's own errorcode and erroroffset.
 *
 *   oracle_probe match <pattern> <flags> <subject> <startpos>
 *       -> "NOMATCH" or "MATCH <n> <s0> <e0> <s1> <e1> ..." for n =
 *          pcre2_get_ovector_count() pairs (n includes slot 0, the whole
 *          match, exactly like this project's caps[] convention); an unset
 *          slot (PCRE2_UNSET in either half) prints as "-1 -1", the same
 *          RX_UNSET spelling docs/spec/rxt_format.md's `g`/`gp` lines use.
 *          A compile failure in match mode also prints "ERROR <code>
 *          <offset>" (callers needing a match must pre-check "compile").
 *          startpos must be <= subject length (PCRE2 raises its own
 *          BADOFFSET above that, a startpos edge case this corpus does not
 *          exercise — it belongs to the base-search corpus, not \Q...\E).
 *
 * No options beyond PCRE2_CASELESS are ever set: (?x), (?i), (?-i) etc. are
 * driven entirely through the pattern text itself, exactly as a real .rxt
 * `pattern` line would carry them, so the oracle's option surface can never
 * silently diverge from what the corpus's block-level `flags i` maps to.
 */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint32_t parse_flags(const char *flags) {
    uint32_t options = 0;
    if (!flags) return options;
    for (const char *p = flags; *p; p++) {
        if (*p == 'i') options |= PCRE2_CASELESS;
        else {
            fprintf(stderr, "oracle_probe: unknown flag letter '%c'\n", *p);
            exit(2);
        }
    }
    return options;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "usage: oracle_probe version|compile <pattern> [flags]|match <pattern> <flags> <subject> <startpos>\n");
        return 2;
    }

    if (strcmp(argv[1], "version") == 0) {
        char buf[256];
        int n = pcre2_config(PCRE2_CONFIG_VERSION, buf);
        if (n < 0) { fprintf(stderr, "oracle_probe: pcre2_config failed: %d\n", n); return 2; }
        printf("%s", buf);
        return 0;
    }

    if (strcmp(argv[1], "errmsg") == 0) {
        if (argc < 3) { fprintf(stderr, "errmsg needs <code>\n"); return 2; }
        int code = atoi(argv[2]);
        PCRE2_UCHAR buf[256];
        int rc = pcre2_get_error_message(code, buf, sizeof(buf) / sizeof(PCRE2_UCHAR));
        if (rc < 0) { fprintf(stderr, "oracle_probe: pcre2_get_error_message failed: %d\n", rc); return 2; }
        printf("%s\n", (char *)buf);
        return 0;
    }

    if (strcmp(argv[1], "compile") == 0) {
        if (argc < 3) { fprintf(stderr, "compile needs <pattern>\n"); return 2; }
        const unsigned char *pattern = (const unsigned char *)argv[2];
        size_t patlen = strlen((const char *)pattern);
        uint32_t options = parse_flags(argc > 3 ? argv[3] : "");
        int errorcode;
        PCRE2_SIZE erroroffset;
        pcre2_code *re = pcre2_compile(pattern, patlen, options, &errorcode, &erroroffset, NULL);
        if (!re) {
            printf("ERROR %d %zu\n", errorcode, (size_t)erroroffset);
            return 0;
        }
        printf("OK\n");
        pcre2_code_free(re);
        return 0;
    }

    if (strcmp(argv[1], "match") == 0) {
        if (argc < 6) { fprintf(stderr, "match needs <pattern> <flags> <subject> <startpos>\n"); return 2; }
        const unsigned char *pattern = (const unsigned char *)argv[2];
        size_t patlen = strlen((const char *)pattern);
        uint32_t options = parse_flags(argv[3]);
        const unsigned char *subject = (const unsigned char *)argv[4];
        size_t sublen = strlen((const char *)subject);
        char *end = NULL;
        unsigned long long startpos = strtoull(argv[5], &end, 10);
        if (!argv[5][0] || (end && *end)) {
            fprintf(stderr, "oracle_probe: malformed startpos '%s'\n", argv[5]);
            return 2;
        }
        if (startpos > sublen) {
            fprintf(stderr, "oracle_probe: startpos %llu > subject length %zu (BADOFFSET territory; not exercised by this corpus)\n",
                    startpos, sublen);
            return 2;
        }

        int errorcode;
        PCRE2_SIZE erroroffset;
        pcre2_code *re = pcre2_compile(pattern, patlen, options, &errorcode, &erroroffset, NULL);
        if (!re) {
            printf("ERROR %d %zu\n", errorcode, (size_t)erroroffset);
            return 0;
        }

        pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
        int rc = pcre2_match(re, subject, sublen, (PCRE2_SIZE)startpos, 0, md, NULL);
        if (rc == PCRE2_ERROR_NOMATCH) {
            printf("NOMATCH\n");
        } else if (rc < 0) {
            printf("MATCHERROR %d\n", rc);
        } else {
            PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
            uint32_t n = pcre2_get_ovector_count(md);
            printf("MATCH %u", n);
            for (uint32_t i = 0; i < n; i++) {
                PCRE2_SIZE s = ov[2 * i], e = ov[2 * i + 1];
                if (s == PCRE2_UNSET || e == PCRE2_UNSET) printf(" -1 -1");
                else printf(" %zu %zu", (size_t)s, (size_t)e);
            }
            printf("\n");
        }
        pcre2_match_data_free(md);
        pcre2_code_free(re);
        return 0;
    }

    fprintf(stderr, "oracle_probe: unknown mode '%s'\n", argv[1]);
    return 2;
}
