/* tests/callouts/co_oracle.c — the libpcre2 ORACLE for callout patterns
 * ([INLINE-C] stage 1b; docs/spec/match_api.md §11.6).
 *
 * Reads one question per stdin line,
 *     <pattern hex> TAB <subject hex> TAB <startpos>
 * and prints one answer line:
 *     match <s0> <e0> <s1> <e1> ...   every group, -1 -1 when unset
 *     nomatch
 *     error <pcre2 code> <message>    a compile or match error
 *
 * The pattern's callouts call the behaviours of behaviors.h, the same rows
 * pcrec's bindings call (stubs.c), with the view pcrec hands its callee
 * (§11.3): every group of the pattern, each its last closed value (PCRE2's
 * `capture_top` hides the rest, which read unset), pair 0 `{start_match,
 * -1}`. A callout's PCRE2 return is 0 to continue and 1 to fail the path, so
 * a behaviour's -1 maps to 1. A `consume` behaviour has no PCRE2 form: the
 * caller splices its `pcre2_equiv` in the site's place before asking.
 *
 * THE FLAGS ARE THE ORACLE'S DEFINITION: PCRE2_NO_AUTO_POSSESS |
 * PCRE2_NO_START_OPTIMIZE | PCRE2_NO_DOTSTAR_ANCHOR, the answer-moving
 * optimizations off, so libpcre2 computes the backtracking-order answer
 * pcrec promises (§11.6¶2). `--default` asks at PCRE2's default flags
 * instead, which only the sensitivity report reads. */
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "behaviors.h"

#define MAXG 64

typedef struct { uint32_t ngroups; } CoData;

static int co_row_by_name(PCRE2_SPTR s, PCRE2_SIZE n)
{
    PCRE2_SIZE k = 0;
    while (k < n && s[k] != ',') k++;
    for (size_t i = 0; i < CO_NROWS; i++)
        if (strlen(co_rows[i].name) == k && !memcmp(co_rows[i].name, s, k))
            return (int)i;
    return -1;
}

static int co_callout(pcre2_callout_block *b, void *data)
{
    const CoData *d = data;
    ptrdiff_t caps[MAXG + 1][2];
    caps[0][0] = (ptrdiff_t)b->start_match;
    caps[0][1] = -1;
    for (uint32_t g = 1; g <= d->ngroups && g <= MAXG; g++) {
        if (g < b->capture_top && b->offset_vector[2 * g] != PCRE2_UNSET) {
            caps[g][0] = (ptrdiff_t)b->offset_vector[2 * g];
            caps[g][1] = (ptrdiff_t)b->offset_vector[2 * g + 1];
        } else {
            caps[g][0] = caps[g][1] = -1;
        }
    }
    int row = b->callout_string
        ? co_row_by_name(b->callout_string, b->callout_string_length)
        : (int)(b->callout_number % CO_NCHECK);
    if (row < 0 || co_rows[row].pcre2_equiv) {
        fprintf(stderr, "co_oracle: callout with no check behaviour\n");
        exit(2);
    }
    const CoView v = { b->subject, b->subject_length, b->current_position,
                       (size_t)d->ngroups + 1,
                       (const ptrdiff_t (*)[2])caps };
    return co_rows[row].fn(&v) == -1 ? 1 : 0;
}

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

int main(int argc, char **argv)
{
    const uint32_t off = (argc > 1 && !strcmp(argv[1], "--default")) ? 0
        : PCRE2_NO_AUTO_POSSESS | PCRE2_NO_START_OPTIMIZE |
          PCRE2_NO_DOTSTAR_ANCHOR;
    static char line[1 << 16];
    static unsigned char pat[1 << 15], subj[1 << 15];
    while (fgets(line, sizeof line, stdin)) {
        char *t1 = strchr(line, '\t');
        char *t2 = t1 ? strchr(t1 + 1, '\t') : NULL;
        if (!t2) { puts("error 0 bad input line"); continue; }
        size_t plen = unhex(line, pat);
        size_t slen = unhex(t1 + 1, subj);
        size_t start = strtoul(t2 + 1, NULL, 10);
        int ec;
        PCRE2_SIZE eo;
        pcre2_code *re = pcre2_compile(pat, plen, off, &ec, &eo, NULL);
        if (!re) {
            PCRE2_UCHAR msg[256];
            pcre2_get_error_message(ec, msg, sizeof msg);
            printf("error %d %s\n", ec, (char *)msg);
            fflush(stdout);
            continue;
        }
        CoData d;
        pcre2_pattern_info(re, PCRE2_INFO_CAPTURECOUNT, &d.ngroups);
        pcre2_match_context *mc = pcre2_match_context_create(NULL);
        pcre2_set_callout(mc, co_callout, &d);
        pcre2_match_data *md = pcre2_match_data_create_from_pattern(re, NULL);
        int rc = pcre2_match(re, subj, slen, start, 0, md, mc);
        if (rc == PCRE2_ERROR_NOMATCH) {
            puts("nomatch");
        } else if (rc < 0) {
            PCRE2_UCHAR msg[256];
            pcre2_get_error_message(rc, msg, sizeof msg);
            printf("error %d %s\n", rc, (char *)msg);
        } else {
            PCRE2_SIZE *ov = pcre2_get_ovector_pointer(md);
            fputs("match", stdout);
            for (uint32_t g = 0; g <= d.ngroups; g++) {
                if ((int)g < rc && ov[2 * g] != PCRE2_UNSET)
                    printf(" %zu %zu", (size_t)ov[2 * g], (size_t)ov[2 * g + 1]);
                else
                    fputs(" -1 -1", stdout);
            }
            putchar('\n');
        }
        fflush(stdout);
        pcre2_match_data_free(md);
        pcre2_match_context_free(mc);
        pcre2_code_free(re);
    }
    return 0;
}
