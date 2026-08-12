/* tests/parse/branch_count_check.c — PARSE-1's branch count, checked.
 *
 * WHY THIS EXISTS, and it is the whole reason PARSE-1 is checkable at all.
 *
 * PARSE-1 makes `p_alt` report the top-level branch count it always computed
 * and used to discard. Candidate B was adopted precisely BECAUSE it leaves the
 * AST alone — which means no output-shaped test can see it. Measured on the
 * unmodified tree before PARSE-1 landed: `(a|b)|c`, `((a|b)|c)|d`, `(a)|b`,
 * `a|(b|c)` and `(a|a)|a` are ALREADY byte-identical to their flat forms. So a
 * codegen check asserting that identity is passed by a build containing NONE of
 * PARSE-1, and it cannot distinguish "counted correctly" from "always returns
 * 1" either, because nothing consumes the count yet. The count and the emitted
 * C are on orthogonal axes; this file reads the axis the codegen checks cannot.
 *
 * THE CONTROL PROBLEM, which is this project's signature defect. Checking
 * pcrec's count against pcrec's own parser is a self-join. So the count is
 * compared against a REFERENCE COUNTER written in this file as a deliberately
 * DIFFERENT ALGORITHM: a flat left-to-right byte scan tracking paren depth,
 * versus the parser's recursive descent. Different algorithm, different code,
 * different failure modes. It is not a transcription of p_alt.
 *
 * AND THE REFERENCE ITSELF IS CHECKED AGAINST AN OUTSIDE AUTHORITY. A reference
 * nobody validated is just a second opinion. libpcre2 supplies thresholds that
 * are functions of exactly this number and nothing else, measured 2026-08-11
 * over 928 generated probes:
 *
 *     (a)(?(1)BODY)     error 127 iff BODY has MORE THAN TWO top-level branches
 *     (?(DEFINE)BODY)   error 154 iff BODY has MORE THAN ONE top-level branch
 *
 * pcrec implements NEITHER construct, and that is the point — libpcre2 stands in
 * for the module PARSE-1 does not have yet, exactly as PC-3 checked the registry
 * before any module it describes existed. Two different thresholds cross-check
 * the same number, so a reference that is uniformly off by one fails one of
 * them.
 *
 * SKIPPING IS LOUD AND IS NOT A PASS (pcre2_check.c's rule). Without
 * libpcre2-8-0 the reference-validation stage prints a SKIP banner and the
 * pcrec-vs-reference comparison still runs; a stranger's `make test` stays
 * green without the outside authority silently vanishing.
 *
 * PROVE THE SABOTAGE IS LIVE. PCREC_BC_SABOTAGE={class,escape,off-by-one}
 * corrupts the REFERENCE counter; run_parse_tests.sh runs each and REQUIRES a
 * non-zero exit. An unsabotaged green check is worth nothing here.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <dlfcn.h>
#include <stdint.h>

#include "core/internal.h"

static int pass_n, fail_n;
static void ok(const char *w)  { (void)w; pass_n++; }
static void bad(const char *fmt, ...)
{
    va_list ap; va_start(ap, fmt);
    fprintf(stderr, "FAIL: "); vfprintf(stderr, fmt, ap); fprintf(stderr, "\n");
    va_end(ap); fail_n++;
}

/* ---- the REFERENCE counter -------------------------------------------------
 *
 * A flat byte scan, NOT a recursive descent, and not derived from parse.c.
 * Rules, each of which exists because a `|` that is not a top-level separator
 * lives there:
 *   - a backslash escapes the next byte outright              a\|b   -> 1
 *   - `[...]` is opaque; `]` first or after `^` is a member   [a|b]  -> 1
 *   - `(...)` nests; only depth 0 counts                      (a|b)|c-> 2
 * Everything else is a byte. */
static int ref_branch_count(const char *p, size_t n)
{
    const char *sab = getenv("PCREC_BC_SABOTAGE");
    int skip_class  = !(sab && !strcmp(sab, "class"));
    int skip_escape = !(sab && !strcmp(sab, "escape"));
    int bias        =  (sab && !strcmp(sab, "off-by-one")) ? 1 : 0;

    int count = 1, depth = 0;
    size_t i = 0;
    while (i < n) {
        char c = p[i];
        if (c == '\\' && skip_escape) { i += 2; continue; }
        if (c == '[' && skip_class) {
            i++;
            if (i < n && p[i] == '^') i++;
            if (i < n && p[i] == ']') i++;      /* leading ] is a member */
            while (i < n && p[i] != ']') {
                if (p[i] == '\\') i++;
                i++;
            }
            i++;                                 /* the closing ] */
            continue;
        }
        if (c == '(') depth++;
        else if (c == ')') { if (depth > 0) depth--; }
        else if (c == '|' && depth == 0) count++;
        i++;
    }
    return count + bias;
}

/* ---- pcrec's own count, read through the parser ---------------------------- */

/* Returns pcrec's top-level branch count, or -1 if pcrec rejects the pattern
 * (a construct it does not implement). Rejections are COUNTED AND REPORTED, not
 * silently dropped — a corpus that quietly shrinks to nothing would pass. */
static int pcrec_branch_count(const char *pat)
{
    Ctx cx;
    memset(&cx, 0, sizeof(cx));
    pcrec_options defo;
    pcrec_default_options(&defo);
    cx.pat = pat;
    cx.patlen = strlen(pat);
    cx.opt = &defo;
    cx.mods = (ModState){ .caseless = defo.caseless != 0 };
    cx.job = calloc(1, sizeof(Job));
    if (!cx.job) return -1;

    int result;
    if (setjmp(cx.jb)) {
        result = -1;
    } else {
        AltInfo info = { -1, 0 };
        pcrec_parse_info(&cx, &info);
        result = info.nbr;
    }
    arena_free(&cx.arena);
    free(cx.job);
    return result;
}

/* ---- the generated corpus --------------------------------------------------
 *
 * GENERATED, never hand-listed (wake §8). The alphabet is chosen so that every
 * rule the reference counter implements is exercised by some body: bare atoms,
 * an escaped pipe, a pipe inside a class, a negated class, a leading-`]` class,
 * groups both capturing and not, nesting to depth 2, and quantified groups. */
static const char *ATOMS[] = {
    "a", "b", "", "\\|", "[a|b]", "[^|]", "[]|a]", "(x|y)", "(?:p|q)",
    "(m)", "a*", "(a|b)*", "((s|t)|u)", "\\\\", "[a-c]", ".",
};
#define NATOMS ((int)(sizeof(ATOMS) / sizeof(ATOMS[0])))

int main(void)
{
    printf("=== PARSE-1 branch count: pcrec's parser vs an independent reference ===\n");

    /* ---- stage 1: validate the REFERENCE against libpcre2 ---------------- */
    void *h = dlopen("libpcre2-8.so.0", RTLD_NOW);
    if (!h) {
        printf("\n  *** SKIP: libpcre2-8-0 not present — the reference counter is\n");
        printf("  *** NOT validated against an outside authority in this run.\n");
        printf("  *** This is a SKIP, not a PASS. Install libpcre2-8-0 to close it.\n\n");
    }
    void *(*p2_compile)(const char *, size_t, uint32_t, int *, size_t *, void *) =
        h ? (void *(*)(const char *, size_t, uint32_t, int *, size_t *, void *))
            dlsym(h, "pcre2_compile_8") : NULL;
    void (*p2_free)(void *) =
        h ? (void (*)(void *))dlsym(h, "pcre2_code_free_8") : NULL;
    int oracle_cases = 0, oracle_bad = 0;

    /* ---- the sweep ------------------------------------------------------- */
    int cases = 0, agreed = 0, rejected = 0;
    char body[512], probe[600];

    for (int i = 0; i < NATOMS; i++)
    for (int j = 0; j < NATOMS; j++)
    for (int k = 0; k < NATOMS; k++)
    for (int nb = 1; nb <= 4; nb++) {
        /* build a body of `nb` top-level branches from the atom triple */
        body[0] = 0;
        for (int b = 0; b < nb; b++) {
            if (b) strncat(body, "|", sizeof(body) - strlen(body) - 1);
            const char *piece = (b == 0) ? ATOMS[i] : (b == 1) ? ATOMS[j] : ATOMS[k];
            strncat(body, piece, sizeof(body) - strlen(body) - 1);
        }

        int want = ref_branch_count(body, strlen(body));
        int got  = pcrec_branch_count(body);
        cases++;
        if (got < 0) { rejected++; continue; }
        if (got == want) agreed++;
        else bad("branch count: pattern '%s' — pcrec says %d, reference says %d",
                 body, got, want);

        /* stage 1, run on the SAME bodies the comparison uses: libpcre2's two
         * thresholds must agree with the reference. Only bodies libpcre2 finds
         * otherwise-valid can arbitrate, so anything outside {0, 127} / {0, 154}
         * is excluded and counted. */
        if (p2_compile) {
            int errc; size_t erro;
            snprintf(probe, sizeof(probe), "(a)(?(1)%s)", body);
            void *c1 = p2_compile(probe, strlen(probe), 0, &errc, &erro, NULL);
            int rc1 = c1 ? 0 : errc;
            if (c1) p2_free(c1);
            if (rc1 == 0 || rc1 == 127) {
                oracle_cases++;
                if ((rc1 == 127) != (want > 2))
                    { oracle_bad++;
                      bad("oracle(127): body '%s' ref=%d but libpcre2 rc=%d", body, want, rc1); }
            }
            snprintf(probe, sizeof(probe), "(?(DEFINE)%s)", body);
            void *c2 = p2_compile(probe, strlen(probe), 0, &errc, &erro, NULL);
            int rc2 = c2 ? 0 : errc;
            if (c2) p2_free(c2);
            if (rc2 == 0 || rc2 == 154) {
                oracle_cases++;
                if ((rc2 == 154) != (want > 1))
                    { oracle_bad++;
                      bad("oracle(154): body '%s' ref=%d but libpcre2 rc=%d", body, want, rc2); }
            }
        }
    }

    printf("  bodies generated:              %d\n", cases);
    printf("  pcrec agreed with reference:   %d\n", agreed);
    printf("  pcrec rejected (not base tier):%d\n", rejected);
    if (p2_compile)
        printf("  libpcre2 arbitrations of the reference: %d (%d disagreements)\n",
               oracle_cases, oracle_bad);

    /* A corpus that shrank to nothing would pass every assertion above. */
    if (agreed == 0)
        bad("NOTHING WAS COMPARED: every generated body was rejected by pcrec. "
            "The check asserted nothing.");
    else ok("compared");
    if (p2_compile && oracle_cases == 0)
        bad("libpcre2 loaded but arbitrated NOTHING — the outside authority "
            "asserted nothing.");
    else if (p2_compile) ok("oracle");

    printf("checks passed: %d\n", pass_n);
    if (fail_n) printf("checks FAILED: %d\n", fail_n);
    if (h) dlclose(h);
    return fail_n == 0 ? 0 : 1;
}
