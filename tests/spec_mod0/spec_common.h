/* spec_common.h — shared oracle harness for the SPEC-MOD0 (D27) checks.
 *
 * WHAT THIS IS. Every check in this directory asks libpcre2 a question and
 * compares the answer to a PREDICTOR stated in the check's own header before
 * the check ran. This header owns the three things all of them need and none
 * of them should re-describe:
 *
 *   1. the oracle       — libpcre2, via ../fuzz/pcre2_abi.h (dlopen; this box
 *                         has the runtime but no -dev package), plus the
 *                         pattern_info introspection the ABI struct omits;
 *   2. the registry     — pcrec's own `--list-syntax` TSV, parsed from a file
 *                         the runner dumps. Read as DATA UNDER TEST, never as
 *                         a source of expectations;
 *   3. populations      — every check counts what it actually compared and
 *                         prints it, and every count is pinned to a floor in
 *                         floors.txt.
 *
 * WHY POPULATIONS ARE A HARD FAILURE MODE HERE. An empty population is
 * indistinguishable from a pass: a sweep that compared nothing prints the same
 * "0 disagreements" as a sweep that compared everything. So spec_pop() fails
 * when a count drops below its pinned floor AND fails when a bucket has no
 * floor entry at all. A newly added bucket must be pinned before it counts as
 * checked; a bucket that silently empties is caught by its floor.
 *
 * THE ORACLE IS NOT OPTIONAL. pcre2_abi_load() leaves policy to the caller and
 * the repo's other consumers differ (the fuzzer fails hard, pcre2_check.c skips
 * loudly inside `make test`). This suite fails hard: libpcre2 IS the oracle for
 * every invariant here, so a missing library means every check is vacuous, and
 * a vacuous check is a sentence, not a check. It is not part of `make test`, so
 * failing hard costs a stranger nothing.
 *
 * Build any check:
 *   TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 -o /var/tmp/X X.c -ldl
 */

#ifndef PCREC_SPEC_MOD0_COMMON_H
#define PCREC_SPEC_MOD0_COMMON_H

#include "pcre2_abi.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ---------------------------------------------------------------- oracle */

#define SPEC_INFO_BACKREFMAX   2u
#define SPEC_INFO_CAPTURECOUNT 4u
typedef int (*spec_fn_pattern_info)(const pcre2_code_8 *, uint32_t, void *);

static Pcre2Abi spec_abi;
static spec_fn_pattern_info spec_pattern_info;
static const char *spec_check_name = "?";
static int spec_fails;

/* A verdict is the whole of what libpcre2 says about a pattern's validity:
 * it compiled, or it did not and this is the error number. Checks compare
 * verdicts, never error MESSAGES — D26 tiers message wording out of scope,
 * and the number is what "whose validity PCRE2 decides" turns on. */
typedef struct { int ok; int err; } SpecVerdict;

static inline SpecVerdict spec_compile_opt(const char *pat, size_t len, uint32_t opts)
{
    SpecVerdict v = {0, 0};
    PCRE2_SIZE eoff = 0;
    pcre2_code_8 *c = spec_abi.compile((PCRE2_SPTR)pat, len, opts,
                                       &v.err, &eoff, NULL);
    if (c) { v.ok = 1; v.err = 0; spec_abi.code_free(c); }
    return v;
}

static inline SpecVerdict spec_compile(const char *pat)
{
    return spec_compile_opt(pat, strlen(pat), 0);
}

/* Does `pat` match `subj` end to end? Used by the behavioural checks, where
 * "compiles" is not the question — binding is. */
/* Length is explicit because subjects here are not always C strings: an octal
 * escape's whole point can be a NUL byte, and a strlen-measured subject silently
 * becomes the empty string exactly there. (Measured: \00, \000 and \0000 all
 * "disagreed" on the first run of check05 for precisely this reason — the
 * harness, not libpcre2.) */
static inline int spec_matches_n(const char *pat, const char *subj, size_t len)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *c = spec_abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                       &err, &eoff, NULL);
    if (!c) return -1;
    pcre2_match_data_8 *md = spec_abi.match_data_create(16, NULL);
    int rc = spec_abi.match(c, (PCRE2_SPTR)subj, len, 0, 0, md, NULL);
    spec_abi.match_data_free(md);
    spec_abi.code_free(c);
    return rc >= 0 ? 1 : 0;
}

static inline int spec_matches(const char *pat, const char *subj)
{
    return spec_matches_n(pat, subj, strlen(subj));
}

/* Capture count straight from libpcre2's own introspection. Returns -1 if the
 * pattern does not compile — callers that need the count of a NON-COMPILING
 * pattern (invariant 2's failure direction) must get it another way; see
 * check02's comment on why that direction exists and how it is reached. */
static inline int spec_capture_count(const char *pat)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *c = spec_abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                       &err, &eoff, NULL);
    if (!c) return -1;
    uint32_t cc = 0;
    spec_pattern_info(c, SPEC_INFO_CAPTURECOUNT, &cc);
    spec_abi.code_free(c);
    return (int)cc;
}

static inline int spec_backrefmax(const char *pat)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    pcre2_code_8 *c = spec_abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                       &err, &eoff, NULL);
    if (!c) return -1;
    uint32_t bm = 0;
    spec_pattern_info(c, SPEC_INFO_BACKREFMAX, &bm);
    spec_abi.code_free(c);
    return (int)bm;
}

/* ---- compile once, match many ------------------------------------------
 * spec_matches() recompiles for every subject, which is fine for a handful of
 * probes and ruinous for a language comparison: the star-is-literal
 * discriminator below runs a few hundred subjects against two patterns per
 * row. These keep the compile out of the inner loop. */
typedef struct { pcre2_code_8 *code; } SpecPat;

static inline int spec_pat_open(SpecPat *p, const char *pat)
{
    int err = 0; PCRE2_SIZE eoff = 0;
    p->code = spec_abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                               &err, &eoff, NULL);
    return p->code != NULL;
}

static inline int spec_pat_match(const SpecPat *p, const char *s, size_t len)
{
    pcre2_match_data_8 *md = spec_abi.match_data_create(16, NULL);
    int rc = spec_abi.match(p->code, (PCRE2_SPTR)s, len, 0, 0, md, NULL);
    spec_abi.match_data_free(md);
    return rc >= 0;
}

static inline void spec_pat_close(SpecPat *p)
{
    if (p->code) spec_abi.code_free(p->code);
    p->code = NULL;
}

/* Is S a LEXICAL construct — one that contributes no atom, so that a following
 * quantifier binds the atom BEFORE it? Defined operationally, exactly as
 * invariant 3 states it:
 *      `a S *` compiles, AND `^Z S *$` accepts "ZZ" (the `*` reached the Z),
 *      AND the control `^Z S $` does NOT accept "ZZ" (S did not eat the second
 *      Z on its own — without this, every construct that happens to match one
 *      character looks lexical).
 *
 * Lives here rather than in check03 because check08 needs the same fact for
 * the endpoint model's first step, and two descriptions of one fact ten lines
 * or two files apart is the failure shape this repo has already paid for.
 * check03 owns the census and the pinned membership; this is just the test. */
static inline int spec_is_lexical(const char *S)
{
    char q[512], starred[512], plain[512];
    snprintf(q, sizeof q, "a%s*", S);
    snprintf(starred, sizeof starred, "^Z%s*$", S);
    snprintf(plain, sizeof plain, "^Z%s$", S);
    if (!spec_compile(q).ok) return 0;
    if (spec_matches(starred, "ZZ") != 1) return 0;
    if (spec_matches(plain, "ZZ") != 0) return 0;
    return 1;
}

static inline void spec_fail(const char *fmt, ...);

/* --------------------------------------------------------------- floors */

/* floors.txt: "<bucket> <minimum>" per line, '#' comments. One file for the
 * whole suite so a reader sees every pinned number in one place, and so
 * ratcheting a floor is a one-line diff that shows up in review. */
typedef struct { char name[64]; long floor; int seen; long got; } SpecFloor;
static SpecFloor spec_floors[256];
static int spec_nfloors;
static int spec_floors_loaded;

static inline void spec_floors_load(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) {
        fprintf(stderr, "FAIL[%s]: cannot open floors file '%s'\n",
                spec_check_name, path);
        exit(2);
    }
    char line[256];
    while (fgets(line, sizeof line, f)) {
        char name[64]; long v;
        if (line[0] == '#' || line[0] == '\n') continue;
        if (sscanf(line, "%63s %ld", name, &v) != 2) continue;
        if (spec_nfloors >= (int)(sizeof spec_floors / sizeof spec_floors[0]))
            continue;
        snprintf(spec_floors[spec_nfloors].name, 64, "%s", name);
        spec_floors[spec_nfloors].floor = v;
        spec_nfloors++;
    }
    fclose(f);
    spec_floors_loaded = 1;
}

/* Record and check one population. Two failure modes, both deliberate:
 *   - count below the pinned floor: the sweep shrank, so something stopped
 *     being compared and the "0 disagreements" line stopped meaning anything;
 *   - no floor entry: a bucket nobody pinned. Unpinned is unchecked. */
static inline void spec_pop(const char *bucket, long count)
{
    if (!spec_floors_loaded) {
        fprintf(stderr, "FAIL[%s]: spec_pop('%s') before floors loaded\n",
                spec_check_name, bucket);
        spec_fails++;
        return;
    }
    for (int i = 0; i < spec_nfloors; i++) {
        if (strcmp(spec_floors[i].name, bucket) != 0) continue;
        spec_floors[i].seen = 1;
        spec_floors[i].got = count;
        if (count < spec_floors[i].floor) {
            printf("  POPULATION %-38s %6ld  FAIL (floor %ld)\n",
                   bucket, count, spec_floors[i].floor);
            spec_fails++;
        } else {
            printf("  POPULATION %-38s %6ld  (floor %ld)\n",
                   bucket, count, spec_floors[i].floor);
        }
        return;
    }
    printf("  POPULATION %-38s %6ld  FAIL (NO FLOOR PINNED — "
           "add it to floors.txt; unpinned is unchecked)\n", bucket, count);
    spec_fails++;
}

/* Every floor whose bucket this check owns must have been reported. Catches
 * the sweep that stopped emitting a bucket entirely — which spec_pop() alone
 * cannot see, because it is never called for a bucket that vanished. */
static inline void spec_floors_require(const char *const *buckets, int n)
{
    for (int i = 0; i < n; i++) {
        int found = 0;
        for (int j = 0; j < spec_nfloors; j++)
            if (!strcmp(spec_floors[j].name, buckets[i]) && spec_floors[j].seen)
                found = 1;
        if (!found) {
            printf("  POPULATION %-38s  MISSING  FAIL (floor pinned but the "
                   "sweep never reported this bucket)\n", buckets[i]);
            spec_fails++;
        }
    }
}

/* -------------------------------------------------------------- failures */

#include <stdarg.h>
static inline void spec_fail(const char *fmt, ...)
{
    va_list ap;
    printf("  DISAGREE ");
    va_start(ap, fmt);
    vprintf(fmt, ap);
    va_end(ap);
    printf("\n");
    spec_fails++;
}

/* The awaited-surface exit. A check whose pcrec-side consumption does not
 * exist yet runs its whole oracle half (so the populations and the predictor
 * are live and a regression in the ORACLE side is caught today), then lands
 * here. It exits 3, distinct from a disagreement's 1, so the runner can say
 * AWAITING-SURFACE rather than FAIL — but it is still nonzero, because a
 * check that cannot fail must not report a pass. */
static inline int spec_await(const char *what, const char *how)
{
    printf("\n  SURFACE MISSING: %s\n", what);
    printf("  consumed how:    %s\n", how);
    printf("  ORACLE SIDE OK — populations above are live; the pcrec-side\n"
           "  comparison is what does not exist yet.\n");
    printf("AWAITING-SURFACE %s (oracle-side disagreements: %d)\n",
           spec_check_name, spec_fails);
    return spec_fails ? 1 : 3;
}

/* ------------------------------------------------------------- registry */

/* The 12 columns of `pcrec --list-syntax`, read from a run (never guessed):
 * kind selector syntax module feature flavours engines status diag flags
 * expect note */
enum { SPEC_COL_KIND, SPEC_COL_SELECTOR, SPEC_COL_SYNTAX, SPEC_COL_MODULE,
       SPEC_COL_FEATURE, SPEC_COL_FLAVOURS, SPEC_COL_ENGINES, SPEC_COL_STATUS,
       SPEC_COL_DIAG, SPEC_COL_FLAGS, SPEC_COL_EXPECT, SPEC_COL_NOTE,
       SPEC_NCOLS };

/* Columns are also looked up BY NAME from the dump's own header line, not only
 * by the positional enum above. That is what makes "awaiting a surface" a
 * mechanical question instead of a judgement call: a check that needs a
 * `quantifiable` column asks for it by name, and either it is in the header
 * pcrec printed or it is not. When the column lands, the check starts
 * comparing with no edit here. */
#define SPEC_NCOLS_MAX 32
static char spec_hdr[SPEC_NCOLS_MAX][32];
static int spec_nhdr;

typedef struct {
    char raw[512];
    const char *col[SPEC_NCOLS_MAX];
    int ncol;
    int lineno;
} SpecRow;

static SpecRow spec_rows[256];
static int spec_nrows;

/* Index of a named column, or -1. */
static inline int spec_col_index(const char *name)
{
    for (int i = 0; i < spec_nhdr; i++)
        if (!strcmp(spec_hdr[i], name)) return i;
    return -1;
}

/* Parses the TSV. A row with the wrong column count is a hard error, not a
 * skip: this suite enumerates "all 100 rows" from this file, so a silently
 * dropped row would shrink every population at once — the exact shape the
 * floors exist to catch, caught earlier and with a better message. */
static inline void spec_registry_load(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) {
        fprintf(stderr, "FAIL[%s]: cannot open registry dump '%s' "
                "(runner should have written it from `pcrec --list-syntax`)\n",
                spec_check_name, path);
        exit(2);
    }
    char line[512];
    int lineno = 0;
    while (fgets(line, sizeof line, f)) {
        lineno++;
        /* The header line is the comment whose first field is "#kind". Parsed
         * for names so columns can be found by name; the positional enum is
         * checked against it below. */
        if (!strncmp(line, "#kind\t", 6)) {
            char h[512];
            snprintf(h, sizeof h, "%s", line + 1);
            spec_nhdr = 0;
            for (char *tok = strtok(h, "\t\r\n"); tok;
                 tok = strtok(NULL, "\t\r\n")) {
                if (spec_nhdr >= SPEC_NCOLS_MAX) break;
                snprintf(spec_hdr[spec_nhdr++], 32, "%s", tok);
            }
            continue;
        }
        if (line[0] == '#' || line[0] == '\n') continue;
        size_t L = strlen(line);
        while (L && (line[L-1] == '\n' || line[L-1] == '\r')) line[--L] = 0;
        if (!L) continue;
        if (spec_nrows >= (int)(sizeof spec_rows / sizeof spec_rows[0])) {
            fprintf(stderr, "FAIL[%s]: more registry rows than table\n",
                    spec_check_name);
            exit(2);
        }
        SpecRow *r = &spec_rows[spec_nrows];
        snprintf(r->raw, sizeof r->raw, "%s", line);
        r->lineno = lineno;
        int n = 0;
        char *p = r->raw;
        r->col[n++] = p;
        for (; *p; p++) {
            if (*p != '\t') continue;
            *p = 0;
            if (n < SPEC_NCOLS_MAX) r->col[n] = p + 1;
            n++;
        }
        r->ncol = n;
        /* A row must have exactly as many fields as the header has names.
         * Fewer or more is a dump-format change, and is fatal rather than
         * skipped: this suite enumerates "all 100 rows" from this file, so a
         * silently dropped row shrinks every population at once. */
        if (n != spec_nhdr) {
            fprintf(stderr, "FAIL[%s]: registry line %d has %d fields but the "
                    "header names %d columns — the dump format changed\n",
                    spec_check_name, lineno, n, spec_nhdr);
            exit(2);
        }
        spec_nrows++;
    }
    fclose(f);

    /* The positional enum is a transcription of a header pcrec prints, and a
     * transcription that stops matching its source is exactly the failure this
     * repo keeps paying for. So check it against the header rather than
     * trusting it: the first SPEC_NCOLS names must be these, in this order.
     * Columns APPENDED after them are fine — that is how an awaited surface
     * arrives — but a reorder or a rename is fatal. */
    static const char *const expect_hdr[SPEC_NCOLS] = {
        "kind", "selector", "syntax", "module", "feature", "flavours",
        "engines", "status", "diag", "flags", "expect", "note"
    };
    if (spec_nhdr < SPEC_NCOLS) {
        fprintf(stderr, "FAIL[%s]: registry header has %d columns, fewer than "
                "the %d this suite reads positionally\n",
                spec_check_name, spec_nhdr, SPEC_NCOLS);
        exit(2);
    }
    for (int i = 0; i < SPEC_NCOLS; i++) {
        if (!strcmp(spec_hdr[i], expect_hdr[i])) continue;
        fprintf(stderr, "FAIL[%s]: registry column %d is '%s', this suite's "
                "enum says '%s' — the dump was reordered or renamed; fix the "
                "enum in spec_common.h\n",
                spec_check_name, i, spec_hdr[i], expect_hdr[i]);
        exit(2);
    }
}

static inline const char *spec_col(const SpecRow *r, int c) { return r->col[c]; }
static inline int spec_col_empty(const SpecRow *r, int c)
{
    const char *s = r->col[c];
    return !s || !*s;
}

/* --------------------------------------------------------------- startup */

static inline void spec_start(const char *name, int argc, char **argv,
                       const char **registry_path_out)
{
    spec_check_name = name;
    char why[256];
    if (pcre2_abi_load(&spec_abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr,
            "FAIL[%s]: ORACLE MISSING — %s\n"
            "  Every invariant in tests/spec_mod0 is decided by libpcre2.\n"
            "  Without it these checks are vacuous, so this is a failure and\n"
            "  not a skip. Install libpcre2-8-0.\n", name, why);
        exit(2);
    }
    spec_pattern_info = (spec_fn_pattern_info)
        dlsym(spec_abi.handle, "pcre2_pattern_info_8");
    if (!spec_pattern_info) {
        fprintf(stderr, "FAIL[%s]: ORACLE MISSING pcre2_pattern_info_8\n", name);
        exit(2);
    }

    /* Sanity on the introspection constants BEFORE any result depends on
     * them. probe_digit_sweep.c's lesson: INFO_* are hand-declared here, and
     * a wrong constant reads some other field and silently agrees with
     * everything. (a)\1 must be capturecount 1, backrefmax 1. */
    {
        int err = 0; PCRE2_SIZE eo = 0;
        pcre2_code_8 *c = spec_abi.compile((PCRE2_SPTR)"(a)\\1", 5, 0,
                                           &err, &eo, NULL);
        uint32_t cc = 99, bm = 99;
        if (!c) { fprintf(stderr, "FAIL[%s]: sanity pattern failed\n", name); exit(2); }
        spec_pattern_info(c, SPEC_INFO_CAPTURECOUNT, &cc);
        spec_pattern_info(c, SPEC_INFO_BACKREFMAX, &bm);
        spec_abi.code_free(c);
        if (cc != 1 || bm != 1) {
            fprintf(stderr, "FAIL[%s]: SANITY cc=%u bm=%u — INFO constants "
                    "wrong; every count below would be meaningless\n",
                    name, cc, bm);
            exit(2);
        }
    }

    char ver[64];
    pcre2_abi_version(&spec_abi, ver, sizeof ver);
    const char *path = pcre2_abi_path(&spec_abi);
    printf("== %s ==\n", name);
    printf("  oracle: libpcre2 %s (%s)\n", ver, path ? path : "path unknown");

    /* argv[1] = floors.txt, argv[2] = registry dump (both from the runner). */
    if (argc < 2) {
        fprintf(stderr, "usage: %s FLOORS.txt [REGISTRY.tsv]\n", name);
        exit(2);
    }
    spec_floors_load(argv[1]);
    if (registry_path_out) {
        if (argc < 3) {
            fprintf(stderr, "FAIL[%s]: this check needs the registry dump\n", name);
            exit(2);
        }
        spec_registry_load(argv[2]);
        *registry_path_out = argv[2];
        printf("  registry: %d rows from %s\n", spec_nrows, argv[2]);
    }
}

static inline int spec_finish(void)
{
    if (spec_fails) {
        printf("FAIL %s: %d disagreement(s)\n", spec_check_name, spec_fails);
        return 1;
    }
    printf("PASS %s\n", spec_check_name);
    return 0;
}

#endif /* PCREC_SPEC_MOD0_COMMON_H */
