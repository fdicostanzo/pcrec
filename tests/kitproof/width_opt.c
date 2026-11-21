/* tests/kitproof/width_opt.c -- the library side of `window_search_width`
 * ([COVER-CAP] stage 2, docs/design/cover_cap.md §11.2.1; limits.md §3.12,
 * tuning.md §2.56), run by run_cover.sh against build/libpcrec.a.
 *
 * Usage: width_opt CEILING  (PCREC_ANCHORED_MAX_STATES, read by the caller
 * from `pcrec --list-limits`, never from a pcrec header).
 *
 * Prints one line per check, `ok ...` or `FAIL ...`:
 *   - refusal: -1, CEILING and CEILING + 1 are malformed options:
 *     pcrec_compile returns -1 with "invalid window_search_width";
 *   - legal: 0 (the built-in default), 1 and CEILING - 1 compile;
 *   - the conjunct reads the field: `[0-9a-f]{24}` stamps
 *     RX_DFA_SCAN "cover" at width 24 and does not at width 23 (the
 *     default 0 is the run_cover.sh verdict rows' business);
 *   - the boundary past the default (review r32 F10): at width 40, between
 *     the default and the top, `[0-9a-f]{40}` is a cover and `[0-9a-f]{41}`
 *     is not (a width check exact at <= 32 but off by one above it reds). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "pcrec.h"

static int nfail;

/* Compiles PAT at width W; returns pcrec_compile's result, with the
 * artifact's text in *src (caller frees) and the error in *err. */
static int compile_at(const char *pat, int w, char **src, pcrec_error *err)
{
    pcrec_options o;
    pcrec_output out = { 0 };
    pcrec_default_options(&o);
    o.window_search_width = w;
    memset(err, 0, sizeof *err);
    int rc = pcrec_compile(pat, &o, &out, err);
    *src = NULL;
    if (rc == 0) {
        *src = out.c_src ? strdup(out.c_src) : NULL;
        pcrec_output_free(&out);
    }
    return rc;
}

static void refused(int w)
{
    char *src;
    pcrec_error err;
    int rc = compile_at("a", w, &src, &err);
    if (rc == -1 && strstr(err.msg, "invalid window_search_width"))
        printf("ok refused %d\n", w);
    else {
        printf("FAIL width %d: rc %d, msg '%s' (expected -1, invalid window_search_width)\n",
               w, rc, err.msg);
        nfail++;
    }
    free(src);
}

static void legal(int w)
{
    char *src;
    pcrec_error err;
    int rc = compile_at("a", w, &src, &err);
    if (rc == 0) printf("ok legal %d\n", w);
    else { printf("FAIL width %d: refused (%s)\n", w, err.msg); nfail++; }
    free(src);
}

static void route(const char *pat, int w, int want_cover)
{
    char *src;
    pcrec_error err;
    if (compile_at(pat, w, &src, &err) != 0 || !src) {
        printf("FAIL %s at width %d: compile failed (%s)\n", pat, w, err.msg);
        nfail++;
        free(src);
        return;
    }
    int cover = strstr(src, "#define RX_DFA_SCAN \"cover\"") != NULL;
    if (cover == want_cover) printf("ok %s at width %d: cover=%d\n", pat, w, cover);
    else {
        printf("FAIL %s at width %d: cover=%d, expected %d\n", pat, w, cover, want_cover);
        nfail++;
    }
    free(src);
}

int main(int argc, char **argv)
{
    int ceil = argc > 1 ? atoi(argv[1]) : 0;
    if (ceil < 3) { printf("FAIL usage: width_opt CEILING (got '%s')\n", argc > 1 ? argv[1] : ""); return 1; }
    refused(-1);
    refused(ceil);
    refused(ceil + 1);
    legal(0);
    legal(1);
    legal(ceil - 1);
    route("[0-9a-f]{24}", 24, 1);
    route("[0-9a-f]{24}", 23, 0);
    route("[0-9a-f]{40}", 40, 1);
    route("[0-9a-f]{41}", 40, 0);
    return nfail ? 1 : 0;
}
