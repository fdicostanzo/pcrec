/* capdiff/pcre2_batch_oracle.c — batch libpcre2 oracle for the K18 capture
 * differential (docs/design/k18_memo_design.md §4.6's open item).
 *
 * WHY A NEW ORACLE PROGRAM rather than reusing tests/fuzz/pcre2_oracle.c: that
 * one is deliberately ONE (pattern, subject) CELL PER PROCESS (dlopen +
 * pcre2_compile_8 + match, each invocation) --- fine at the fuzzer's few
 * hundred patterns, prohibitive at this lane's tens of thousands of cells
 * (D45's own compile-budget lesson applies to test-INFRASTRUCTURE cost too).
 * This program amortises the one dlopen over an entire run and reports EVERY
 * capture slot's ovector pair, not just the whole-match span pcre2_oracle.c
 * prints -- this lane's whole point is per-slot agreement (D44's three-way
 * rule), so a single-pair oracle would not answer the question.
 *
 * It does NOT duplicate the PCRE2 ABI declarations: tests/fuzz/pcre2_abi.h is
 * the one hand-declared description of that ABI in this repo (extracted at
 * PC-3 for exactly this reason -- a second copy is the `\v` bug's shape), so
 * this file #includes it by relative path rather than re-typing it.
 *
 * Protocol: reads TSV lines from stdin,
 *
 *     PATTERN\tSTARTPOS\tSUBJECT_HEX
 *
 * where SUBJECT_HEX is the subject's bytes as lowercase hex pairs (never raw
 * bytes over a TSV field -- a subject may itself contain tabs, newlines or
 * NUL, which a delimited text protocol cannot carry safely; hex sidesteps
 * escaping entirely, matching the project's existing "subject via a file of
 * raw bytes" discipline in tests/fuzz/pcre2_oracle.c, done here as one
 * hex field per line instead of one file per cell). Compiles = 0 for every
 * pattern (D26's standing exclusion: the suite's oracle is pinned at
 * options=0 until a flag is deliberately adopted, docs/pcre2_options.md).
 *
 * Prints one line per input line, in order:
 *
 *     match S0 E0 S1 E1 ... Sk Ek      (k = the PATTERN's own group count,
 *                                        PCRE2_UNSET spelled -1 -1)
 *     nomatch
 *     cerr <code>                      pattern rejected at PCRE2 compile time
 *     mlimit <code>                    PCRE2's own match-time safeguard
 *                                       tripped -- not a verdict, never
 *                                       compared (see pcre2_oracle.c's header)
 *
 * Exit codes: 0 normal, 2 usage/protocol error, 3 failed to load libpcre2.
 */
#include "../../../../tests/fuzz/pcre2_abi.h"

#include <errno.h>
#include <stdlib.h>

static Pcre2Abi pcre2;

#define MAXPAT 8192
#define MAXSUBJ_HEX 65536
#define MAXOVEC 64   /* pairs pcre2_match_data_create reserves */
#define PRINT_PAIRS 20  /* pairs PRINTED per cell, fixed regardless of the
                          * pattern's own group count -- far more than any
                          * shape this lane generates needs (all are single
                          * digits of groups), so the comparator just takes
                          * the first (ngroups+1) pairs off the front rather
                          * than this oracle needing to know PCRE2's own
                          * capture count for the pattern. */

static int hexval(unsigned char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

/* Decodes a hex string into a freshly malloc'd buffer. Returns NULL and sets
 * *ok=0 on a malformed (odd-length or non-hex) field. An all-empty hex field
 * (subject "") mallocs 1 byte and returns len 0, matching pcre2_oracle.c's
 * own zero-length handling. */
static unsigned char *hexdecode(const char *hex, size_t *outlen, int *ok)
{
    size_t hl = strlen(hex);
    *ok = 1;
    if (hl % 2 != 0) { *ok = 0; return NULL; }
    size_t n = hl / 2;
    unsigned char *buf = malloc(n > 0 ? n : 1);
    if (!buf) { *ok = 0; return NULL; }
    for (size_t i = 0; i < n; i++) {
        int hi = hexval((unsigned char)hex[2*i]);
        int lo = hexval((unsigned char)hex[2*i+1]);
        if (hi < 0 || lo < 0) { free(buf); *ok = 0; return NULL; }
        buf[i] = (unsigned char)((hi << 4) | lo);
    }
    *outlen = n;
    return buf;
}

static void load_pcre2(void)
{
    char why[512];
    if (pcre2_abi_load(&pcre2, why, sizeof why) == PCRE2_ABI_OK) return;
    fprintf(stderr, "pcre2_batch_oracle: %s\n", why);
    exit(3);
}

int main(void)
{
    load_pcre2();

    char verbuf[64];
    pcre2_abi_version(&pcre2, verbuf, sizeof verbuf);
    fprintf(stderr, "pcre2_batch_oracle: libpcre2 %s (%s)\n",
            verbuf, pcre2_abi_path(&pcre2) ? pcre2_abi_path(&pcre2) : "?");

    static char pat[MAXPAT];
    static char subjhex[MAXSUBJ_HEX];
    char line[MAXPAT + MAXSUBJ_HEX + 64];
    long lineno = 0;

    /* One-entry cache: consecutive lines sharing the same pattern text (the
     * python driver sorts/groups its cells by pattern) skip recompilation.
     * Correctness does not depend on the cache -- a miss just recompiles --
     * so a grouping assumption that turns out false costs speed, not
     * accuracy. */
    static char cached_pat[MAXPAT] = {0};
    pcre2_code_8 *code = NULL;

    while (fgets(line, sizeof line, stdin)) {
        lineno++;
        size_t ll = strlen(line);
        if (ll && line[ll-1] == '\n') line[--ll] = 0;
        if (ll == 0) continue;

        char *tab1 = strchr(line, '\t');
        if (!tab1) { fprintf(stderr, "pcre2_batch_oracle: line %ld: no TAB\n", lineno); return 2; }
        char *tab2 = strchr(tab1 + 1, '\t');
        if (!tab2) { fprintf(stderr, "pcre2_batch_oracle: line %ld: only one TAB\n", lineno); return 2; }

        size_t patlen = (size_t)(tab1 - line);
        if (patlen >= sizeof pat) { fprintf(stderr, "pcre2_batch_oracle: line %ld: pattern too long\n", lineno); return 2; }
        memcpy(pat, line, patlen); pat[patlen] = 0;

        char *spstr = tab1 + 1;
        *tab2 = 0;
        char *end;
        long startpos = strtol(spstr, &end, 10);
        if (*end != 0 || startpos < 0) { fprintf(stderr, "pcre2_batch_oracle: line %ld: bad startpos\n", lineno); return 2; }

        const char *hexfield = tab2 + 1;
        if (strlen(hexfield) >= sizeof subjhex) { fprintf(stderr, "pcre2_batch_oracle: line %ld: subject too long\n", lineno); return 2; }
        strcpy(subjhex, hexfield);

        if (code == NULL || strcmp(cached_pat, pat) != 0) {
            if (code) { pcre2.code_free(code); code = NULL; }
            int errorcode; PCRE2_SIZE erroffset;
            code = pcre2.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                  &errorcode, &erroffset, NULL);
            if (!code) {
                printf("cerr %d\n", errorcode);
                cached_pat[0] = 0;
                continue;
            }
            strcpy(cached_pat, pat);
        }

        size_t subjlen;
        int ok;
        unsigned char *subj = hexdecode(subjhex, &subjlen, &ok);
        if (!ok) { fprintf(stderr, "pcre2_batch_oracle: line %ld: bad hex subject\n", lineno); return 2; }

        if ((size_t)startpos > subjlen) {
            printf("nomatch\n");
            free(subj);
            continue;
        }

        pcre2_match_data_8 *md = pcre2.match_data_create(MAXOVEC, NULL);
        int rc = pcre2.match(code, (PCRE2_SPTR)subj, subjlen,
                              (PCRE2_SIZE)startpos, 0, md, NULL);
        if (rc == -1) {
            printf("nomatch\n");
        } else if (rc < 0) {
            printf("mlimit %d\n", rc);
        } else {
            /* PCRE2's own contract (pcre2demo.c, "the value returned by
             * pcre2_match() ... is one more than the highest numbered pair
             * that has been set"): only ov[0 .. 2*rc) was written by this
             * call. A slot >= rc is guaranteed NOT to have participated
             * (a higher-numbered group cannot match while a lower one it
             * nests inside/follows textually did not, for anything this
             * lane generates), so it is printed as UNSET WITHOUT reading
             * ov[] there -- reading past rc is exactly the uninitialised-
             * ovector mistake this project's own K21 entry is about, one
             * layer up (a printf reading memory pcre2_match never
             * promised to have written). */
            PCRE2_SIZE *ov = pcre2.get_ovector_pointer(md);
            printf("match");
            for (int k = 0; k < PRINT_PAIRS; k++) {
                if (k < rc) {
                    PCRE2_SIZE s = ov[2*k], e = ov[2*k+1];
                    if (s == (PCRE2_SIZE)-1) printf(" -1 -1");
                    else printf(" %zu %zu", (size_t)s, (size_t)e);
                } else {
                    printf(" -1 -1");
                }
            }
            printf("\n");
        }
        pcre2.match_data_free(md);
        free(subj);
    }

    if (code) pcre2.code_free(code);
    return 0;
}
