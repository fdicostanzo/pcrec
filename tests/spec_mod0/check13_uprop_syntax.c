/* check13_uprop_syntax.c — the UNICODE PROPERTY ESCAPES (`\p{...}` / `\P{...}`)
 * RECOGNITION BOUNDARY: which spellings are a construct at all, what pcrec is
 * allowed to say about them while it implements none of them, and where it is
 * allowed to point when it says it.
 *
 * THIS CHECK IS D27 (spec-first, blinded from src/, docs/ and the rest of
 * tests/). Its author had `build/pcrec` as a black box, `tests/probes/`'s
 * method note, `tests/fuzz/pcre2_abi.h`, and libpcre2 itself. No expectation
 * below was read off a pcrec source file, and the two expectations that ARE
 * pcrec's own output rather than PCRE2's are marked as such in place and claim
 * stability only (see "WHAT IS pcrec's OWN WORD" below).
 *
 * THE PROMISE. `\p{...}` and `\P{...}` are real PCRE2 constructs. pcrec
 * implements no Unicode property matching today, so for every one of them the
 * whole of what pcrec owes is: know it exists, attribute it to a module,
 * refuse, and emit nothing. Three obligations follow, at three D26 tiers:
 *
 *   T1 (exact) NEVER MISCOMPILE. pcrec must not accept a pattern libpcre2
 *      rejects, and must emit no C on any refusal. Both are checked on every
 *      cell in this file; the byte count of stdout is what makes the second
 *      an observation rather than a hope.
 *   T2 (exact) THE CONSTRUCT IS REAL, AND WHOSE IT IS. Where libpcre2 accepts
 *      the pattern, pcrec must refuse it as UNIMPLEMENTED (naming a module) or
 *      as OUT-OF-SCOPE — never as INVALID. Refusing a real construct as bad
 *      syntax is the "quieter grammar" defect: it is still a refusal, so no
 *      test that only looks at the exit code can see it.
 *   T3 (not exact, per D26) THE WORDING. Nothing here compares pcrec's
 *      sentence against PCRE2's. The error NUMBER is used as the oracle's
 *      verdict; the message text is used only to classify pcrec's refusal into
 *      the three classes above and to read the module name it printed.
 *
 * ---------------------------------------------------------------- generation
 *
 * Every population below is GENERATED. A hand-listed set stops at its author's
 * imagination, and this project has measured that failure four times; so where
 * a sweep is possible it is swept, and where a sweep had to be bounded the
 * boundary is stated at the family.
 *
 *   A after_byte      every byte 0x01..0xFF after `\p` and after `\P`, bare.
 *                     BOUNDARY: 0x00 is unreachable — a pattern arrives as one
 *                     argv element, and argv strings are NUL-terminated. There
 *                     is no CLI surface that can express a NUL in a pattern, so
 *                     this is a boundary of the INSTRUMENT, not a gap that
 *                     could be closed by sweeping harder.
 *   B braced_marginal every printable byte 0x20..0x7E in each of five
 *                     positions inside a braced body — alone, before a letter,
 *                     after a letter, after `^`, before `^` — for both `\p`
 *                     and `\P`. This is the POSITION-MARGINAL projection of the
 *                     two-character body space, chosen because the question the
 *                     family asks is whether a character's legality depends on
 *                     where it sits. BOUNDARY: the full 95x95 two-character
 *                     product (18,240 cells) was run once while this file was
 *                     written and produced no acceptance and no new refusal
 *                     class; build with -DSPEC_UPROP_FULL to run it here.
 *   C context         20 contexts x a construct set whose VALID half is
 *                     derived from family A's measured results (the single
 *                     letters libpcre2 actually accepts, not a remembered
 *                     list) and whose INVALID half is a fixed set of malformed
 *                     shapes. The swept dimension is the CONTEXT: class
 *                     interior, both range endpoints, quantified, alternation,
 *                     nested group, after a posix set, after an option run.
 *   D truncation      every prefix of every canonical construct, in three
 *                     contexts. A truncation sweep is the cheapest way to find
 *                     a recogniser that reads past the end of its input.
 *   E namelen         property-name bodies of every length from 0 to 79, in
 *                     four paddings. libpcre2 has a name-length limit; this
 *                     family finds it by sweeping rather than by knowing it,
 *                     and it is the family that exercises the second branch of
 *                     the offset rule below.
 *   F quote_mode      every canonical construct inside `\Q...\E`, where the
 *                     text is NOT a construct at all.
 *   G config          every canonical construct under --features none,
 *                     --features unicode-props and --features all.
 *   H case_flag       every canonical construct with and without -i.
 *
 * ------------------------------------------------------------- the predictor
 *
 * A generated sweep cannot carry a hand-written prediction per cell, so the
 * oracle verdict is MEASURED per cell at run time and the check asserts a
 * RELATION between the two verdicts (T1 and T2 above) rather than a literal.
 * To keep the oracle half from being vacuous, family A additionally asserts
 * literal ANCHORS that were measured while this file was written and are
 * recorded here as predictions: exactly 28 of the 510 single-byte forms
 * compile, they are `\p` and `\P` followed by one of C L M N P S Z in either
 * case, and every other byte lands on error 146 or error 147 — never on a
 * fourth outcome, and never on "compiles as something else". If libpcre2 ever
 * disagrees with those, the check says so against ITSELF first, loudly, before
 * any pcrec result is reported.
 *
 * ------------------------------------------------------------ the offset rule
 *
 * pcrec prints "(pattern offset N)" with its refusals. N is not wording — it is
 * a position, and a recogniser that stops in the wrong place is a recogniser
 * that would resume parsing in the wrong place the day the module lands. The
 * rule, DERIVED FROM THE PUBLIC GRAMMAR and then confirmed over 19,884 cells
 * while this file was written:
 *
 *     N == the construct's grammatical EXTENT — `\p`/`\P`, then either a
 *     braced body up to and including the first `}` (or to the end of the
 *     pattern if there is none), or exactly one following character —
 *     EXCEPT where libpcre2 itself stops earlier than that extent, in which
 *     case N is libpcre2's own error offset.
 *
 * Both branches are populated and both are floored: the second is the
 * over-length-name family, where libpcre2 abandons the name partway and pcrec
 * abandons it at the same byte. `uprop_extent()` computes the first branch
 * from the grammar with no reference to either implementation.
 *
 * BOUNDARY of the extent scanner: it walks escapes left to right and stops at
 * the first `\p`/`\P`, so it is correct only for patterns whose first property
 * escape is the one under test and which do not hide a `\p` inside quote mode.
 * The generators respect both conditions; family F (quote mode) asserts a
 * different thing and does not use it.
 *
 * ------------------------------------------------- what is pcrec's OWN word
 *
 * Two facts below come from pcrec's output rather than from PCRE2, and are
 * marked STABILITY-ONLY where they are used:
 *   - the module name is read from pcrec's own registry dump (`--list-syntax`),
 *     which is data under test; the check asserts the registry's `\p{L}` and
 *     `\P{L}` rows really do compile under libpcre2 first, so a registry that
 *     invented a construct is caught before its module name is trusted;
 *   - the "(pattern offset N)" spelling itself. If pcrec stops printing an
 *     offset the check fails, which is the intended direction: the offset is
 *     how this check sees the recognition extent at all.
 *
 * -------------------------------------------------------------- sabotage
 *
 * Validated 2026-08-12 against two stand-ins, each an executable script put in
 * PCREC's place:
 *
 *   accept-everything (exit 0, a stub translation unit on stdout) — 1,782
 *   disagreements across six families (after_byte 482, braced_marginal 840,
 *   context 260, truncation 90, namelen 79, config 31): the T1 clause on every
 *   cell libpcre2 rejects.
 *
 *   refuse-everything ("pcrec: syntax error", exit 1, no module named) — 856
 *   disagreements across the same six families (after_byte 28,
 *   braced_marginal 110, context 360, truncation 18, namelen 320, config 20):
 *   the T2 clause on every cell libpcre2 accepts.
 *
 * Two families are undetectable by either stand-in BY DESIGN and are named
 * here rather than left to be discovered: `case_flag` and `quote_mode` compare
 * pcrec against itself under two invocations, and a stand-in that answers
 * identically every time agrees with itself. Their guard is the population
 * floor, not the comparison.
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -I tests/spec_mod0 \
 *          -o /var/tmp/check13 check13_uprop_syntax.c -ldl
 * Run:   check13 floors.txt registry.tsv [pcrec-path]
 */
#include "spec_common.h"
#include "spec_pcrec.h"

static const char *pcrec_path;
static char uprops_module[64];      /* from the registry's \p{L} row */

/* ------------------------------------------------------- disagreement budget
 * A generated sweep that goes wrong goes wrong in thousands of cells at once.
 * Printing all of them buries the one line a reader needs, so each family
 * prints its first few in full and then one aggregate line. Every one still
 * counts as a failure. */
typedef struct { const char *family; long shown, total; } Budget;
#define BUDGET_SHOW 6

static void budget_fail(Budget *b, const char *fmt, ...)
{
    b->total++;
    if (b->shown < BUDGET_SHOW) {
        b->shown++;
        va_list ap; va_start(ap, fmt);
        printf("  DISAGREE "); vprintf(fmt, ap); printf("\n");
        va_end(ap);
        spec_fails++;
    }
}

static void budget_close(Budget *b)
{
    if (b->total > b->shown) {
        printf("  DISAGREE [%s] ... and %ld more of the same family "
               "(%ld total; the first %ld are shown in full)\n",
               b->family, b->total - b->shown, b->total, b->shown);
        spec_fails++;
    }
}

/* ------------------------------------------------------------- extent, from
 * the public grammar. Returns -1 if there is no property escape. */
static long uprop_extent(const char *pat)
{
    long L = (long)strlen(pat), i = 0, start = -1;
    while (i < L) {
        if (pat[i] != '\\') { i++; continue; }
        if (i + 1 >= L) return -1;
        if (pat[i+1] == 'p' || pat[i+1] == 'P') { start = i; break; }
        i += 2;
    }
    if (start < 0) return -1;
    long k = start + 2;
    if (k >= L) return k;
    if (pat[k] != '{') return k + 1;
    const char *close = strchr(pat + k + 1, '}');
    return close ? (long)(close - pat) + 1 : L;
}

/* The oracle's whole answer, offset included. spec_compile() drops the offset
 * and this check needs it for the second branch of the offset rule, so the
 * compile happens once, here, rather than twice per cell. */
typedef struct { int ok; int err; long off; } Oracle;

static Oracle oracle(const char *pat)
{
    Oracle o = {0, 0, -1};
    PCRE2_SIZE eoff = 0;
    pcre2_code_8 *c = spec_abi.compile((PCRE2_SPTR)pat, strlen(pat), 0,
                                       &o.err, &eoff, NULL);
    if (c) { o.ok = 1; o.err = 0; spec_abi.code_free(c); }
    else o.off = (long)eoff;
    return o;
}

/* ------------------------------------------------------------- populations */
static long pop_oracle_accepts, pop_oracle_rejects;
static long pop_refused_module, pop_refused_scope, pop_refused_invalid, pop_accepted;
static long pop_off_at_extent, pop_off_at_oracle;

/* One cell. `attributable` says the context introduces no OTHER unimplemented
 * construct, so the module pcrec names must be the property escapes' own.
 * Returns pcrec's verdict class so callers can do family-specific work. */
static SpecVClass cell(Budget *b, const char *pat, int attributable)
{
    Oracle o = oracle(pat);
    if (o.ok) pop_oracle_accepts++; else pop_oracle_rejects++;

    SpecPcrecRun r = spec_pcrec_compile(pcrec_path, "all", pat, NULL);
    SpecVClass vc = spec_pcrec_classify(&r);
    if (vc == SPEC_VC_ERROR) {
        budget_fail(b, "[%s] pcrec neither accepted nor refused '%s' "
                       "(ran=%d timed_out=%d exit=%d stderr=%.120s)",
                    b->family, pat, r.ran, r.timed_out, r.exit_code, r.err);
        return vc;
    }

    /* T1a: accepting what PCRE2 rejects is the miscompile direction. */
    if (vc == SPEC_VC_ACCEPTED) {
        pop_accepted++;
        if (!o.ok)
            budget_fail(b, "[%s] MISCOMPILE RISK: pcrec ACCEPTED '%s' and wrote "
                           "%ld bytes of C; libpcre2 rejects it (error %d at "
                           "offset %ld)", b->family, pat, r.out_bytes, o.err, o.off);
        return vc;
    }

    /* T1b: a refusal must emit nothing at all. */
    if (r.out_bytes != 0)
        budget_fail(b, "[%s] pcrec refused '%s' but still wrote %ld bytes to "
                       "stdout — a refusal must emit no C", b->family, pat, r.out_bytes);

    if (vc == SPEC_VC_MODULE) pop_refused_module++;
    else if (vc == SPEC_VC_SCOPE) pop_refused_scope++;
    else pop_refused_invalid++;

    /* T2: a pattern libpcre2 compiles is real; refusing it as INVALID says
     * pcrec's grammar is quieter than PCRE2's. */
    if (o.ok && vc == SPEC_VC_INVALID)
        budget_fail(b, "[%s] '%s' compiles under libpcre2, but pcrec refused it "
                       "as INVALID rather than as unimplemented or out of scope "
                       "(stderr: %.140s)", b->family, pat, r.err);

    if (vc != SPEC_VC_MODULE) return vc;

    const char *mod = spec_pcrec_module(&r);
    if (attributable && strcmp(mod, uprops_module) != 0) {
        budget_fail(b, "[%s] '%s' was refused for module '%s'; the only "
                       "unimplemented construct in this pattern is the property "
                       "escape, which the registry attributes to '%s'",
                    b->family, pat, mod, uprops_module);
        return vc;
    }
    if (strcmp(mod, uprops_module) != 0) return vc;   /* another module spoke first */

    /* The offset rule. Both branches are oracle- or grammar-anchored. */
    long ext = uprop_extent(pat);
    long got = spec_pcrec_offset(&r);
    if (got < 0) {
        budget_fail(b, "[%s] '%s' was refused with no \"(pattern offset N)\" in "
                       "the diagnostic — this check reads the recognition extent "
                       "from there and cannot see it otherwise (stderr: %.120s)",
                    b->family, pat, r.err);
        return vc;
    }
    if (ext < 0) return vc;                      /* no property escape to measure */
    if (got == ext) { pop_off_at_extent++; return vc; }
    /* The only permitted shortfall is libpcre2 stopping earlier itself. */
    if (!o.ok && o.off == got) { pop_off_at_oracle++; return vc; }
    budget_fail(b, "[%s] '%s': pcrec blames offset %ld; the construct's "
                   "grammatical extent ends at %ld and libpcre2 %s",
                b->family, pat, got, ext,
                o.ok ? "compiles the pattern (so there is no earlier stop to "
                       "justify a different offset)" : "stopped elsewhere");
    return vc;
}

/* ------------------------------------------------------------------- main */

int main(int argc, char **argv)
{
    const char *rp = NULL;
    spec_start("check13_uprop_syntax", argc, argv, &rp);
    pcrec_path = (argc >= 4 && argv[3][0]) ? argv[3] : getenv("PCREC");
    if (!pcrec_path || !*pcrec_path) pcrec_path = "build/pcrec";

    /* ---- the registry's own claim about these constructs ------------------
     * Read from a RUN of pcrec, and checked before it is used: a registry row
     * whose syntax probe does not compile under libpcre2 is claiming a fake
     * construct is real, and its module name would then be worthless here. */
    long registry_rows = 0;
    uprops_module[0] = 0;
    for (int i = 0; i < spec_nrows; i++) {
        const SpecRow *r = &spec_rows[i];
        const char *sel = spec_col(r, SPEC_COL_SELECTOR);
        if (strcmp(spec_col(r, SPEC_COL_KIND), "esc") != 0) continue;
        if (!sel || (strcmp(sel, "p") != 0 && strcmp(sel, "P") != 0)) continue;
        registry_rows++;
        const char *S = spec_col(r, SPEC_COL_SYNTAX);
        if (!spec_compile(S).ok)
            spec_fail("the registry's row for '%s' claims a construct libpcre2 "
                      "does not compile — a fake construct declared real", S);
        const char *m = spec_col(r, SPEC_COL_MODULE);
        if (!uprops_module[0]) snprintf(uprops_module, sizeof uprops_module, "%s", m);
        else if (strcmp(uprops_module, m) != 0)
            spec_fail("the \\p and \\P rows are attributed to different modules "
                      "('%s' and '%s'); they are one construct family",
                      uprops_module, m);
    }
    if (registry_rows != 2)
        spec_fail("expected exactly two registry rows selected by 'p' and 'P' "
                  "(the property escape and its negation); found %ld", registry_rows);
    if (!uprops_module[0]) { printf("FAIL: no module for \\p in the registry\n"); return 1; }
    printf("  \\p / \\P are attributed by the registry to module '%s'\n", uprops_module);
    spec_pop("uprop.registry_rows", registry_rows);

    /* ---- family A: the byte after \p / \P -------------------------------- */
    Budget bA = { "after_byte", 0, 0 };
    long fA = 0, anchor_compiles = 0;
    char valid_letters[64]; int nvalid = 0;
    for (int e = 0; e < 2; e++) {
        for (int by = 1; by < 256; by++) {
            char pat[8];
            pat[0] = '\\'; pat[1] = e ? 'P' : 'p'; pat[2] = (char)by; pat[3] = 0;
            SpecVerdict o = spec_compile(pat);
            if (o.ok) {
                anchor_compiles++;
                if (!e && nvalid < (int)sizeof valid_letters - 1)
                    valid_letters[nvalid++] = (char)by;
            } else if (o.err != 146 && o.err != 147) {
                spec_fail("ANCHOR: '\\%c' + byte 0x%02x is libpcre2 error %d; the "
                          "predicted outcome set for this family is {compiles, "
                          "146, 147} and a fourth outcome invalidates the family",
                          e ? 'P' : 'p', by, o.err);
            }
            cell(&bA, pat, 1);
            fA++;
        }
    }
    valid_letters[nvalid] = 0;
    budget_close(&bA);
    printf("  single-letter property codes libpcre2 accepts after \\p: \"%s\"\n",
           valid_letters);
    if (anchor_compiles != 28)
        spec_fail("ANCHOR: %ld of the 510 single-byte forms compile; the "
                  "prediction recorded in this file's header is 28. Either the "
                  "oracle changed or this family is measuring something else",
                  anchor_compiles);
    if (nvalid != 14)
        spec_fail("ANCHOR: %d distinct one-letter property codes after \\p; "
                  "the prediction is 14 (C L M N P S Z in both cases)", nvalid);
    spec_pop("uprop.after_byte", fA);

    /* ---- family B: printable bytes in five braced-body positions ---------- */
    Budget bB = { "braced_marginal", 0, 0 };
    long fB = 0;
    static const char *const body_shapes[] = { "%c", "L%c", "%cL", "^%c", "%c^" };
    for (int e = 0; e < 2; e++) {
        for (int by = 0x20; by <= 0x7e; by++) {
            for (size_t s = 0; s < sizeof body_shapes / sizeof body_shapes[0]; s++) {
                char body[8], pat[16];
                snprintf(body, sizeof body, body_shapes[s], (char)by);
                snprintf(pat, sizeof pat, "\\%c{%s}", e ? 'P' : 'p', body);
                cell(&bB, pat, 1);
                fB++;
            }
        }
    }
#ifdef SPEC_UPROP_FULL
    /* The full two-character product. Off by default only for runtime: it adds
     * 18,240 pcrec invocations (about twenty seconds) and, when this file was
     * written, no cell it reached was reachable only by it. */
    for (int e = 0; e < 2; e++)
        for (int c1 = 0x20; c1 <= 0x7e; c1++)
            for (int c2 = 0x20; c2 <= 0x7e; c2++) {
                char pat[16];
                snprintf(pat, sizeof pat, "\\%c{%c%c}", e ? 'P' : 'p', (char)c1, (char)c2);
                cell(&bB, pat, 1);
                fB++;
            }
#endif
    budget_close(&bB);
    spec_pop("uprop.braced_marginal", fB);

    /* ---- the construct set families C, D, F, G, H share --------------------
     * The VALID half is built from family A's measured letters (strided so the
     * table stays small), not from a remembered list of property names. The
     * INVALID half is the malformed shapes: a truncation, an empty body, a
     * body that is only the negation marker, an illegal body character, and a
     * doubled negation marker. */
    char cons[40][24]; int ncons = 0;
    for (int i = 0; i < nvalid && ncons < 24; i += 3) {
        snprintf(cons[ncons++], 24, "\\p%c", valid_letters[i]);
        snprintf(cons[ncons++], 24, "\\p{%c}", valid_letters[i]);
        snprintf(cons[ncons++], 24, "\\P{%c}", valid_letters[i]);
        snprintf(cons[ncons++], 24, "\\p{^%c}", valid_letters[i]);
    }
    static const char *const malformed[] = {
        "\\p", "\\P", "\\p{", "\\p{L", "\\p{}", "\\p{^}", "\\px", "\\p{!}",
        "\\p{L!}", "\\p{^^L}", "\\p{Foo}"
    };
    for (size_t i = 0; i < sizeof malformed / sizeof malformed[0] && ncons < 40; i++)
        snprintf(cons[ncons++], 24, "%s", malformed[i]);
    printf("  construct set: %d spellings (%d generated from measured letters, "
           "%d malformed shapes)\n", ncons,
           ncons - (int)(sizeof malformed / sizeof malformed[0]),
           (int)(sizeof malformed / sizeof malformed[0]));

    /* ---- family C: contexts ------------------------------------------------
     * ATTRIBUTABLE contexts contain no other construct pcrec has not
     * implemented, so the module named must be the property escapes' own.
     * The named-group context does contain one, and only the universal
     * clauses apply there. */
    static const struct { const char *tpl; int attributable; } ctxs[] = {
        { "%s",                1 }, { "a%sb",              1 },
        { "[%s]",              1 }, { "[a%sb]",            1 },
        { "[^%s]",             1 }, { "%s*",               1 },
        { "%s{2,3}",           1 }, { "(%s)",              1 },
        { "(?:%s)+",           1 }, { "[%s-z]",            1 },
        { "[a-%s]",            1 }, { "^%s$",              1 },
        { "%s|x",              1 }, { "x|%s",              1 },
        { "(%s|b)",            1 }, { "[0-9%s]",           1 },
        { "[[:alpha:]%s]",     1 }, { "(?i)%s",            1 },
        { "((%s))",            1 }, { "(?<n>%s)",          0 },
    };
    Budget bC = { "context", 0, 0 };
    long fC = 0;
    for (size_t t = 0; t < sizeof ctxs / sizeof ctxs[0]; t++)
        for (int i = 0; i < ncons; i++) {
            char pat[64];
            snprintf(pat, sizeof pat, ctxs[t].tpl, cons[i]);
            cell(&bC, pat, ctxs[t].attributable);
            fC++;
        }
    budget_close(&bC);
    spec_pop("uprop.context", fC);

    /* ---- family D: every prefix of a canonical construct ------------------ */
    Budget bD = { "truncation", 0, 0 };
    long fD = 0;
    static const char *const full[] = {
        "\\p{Latin}", "\\P{^Greek}", "\\p{Lu}", "\\pL", "\\P{L}", "\\p{  L  }"
    };
    static const char *const tctx[] = { "%s", "a%sb", "[%s]" };
    for (size_t f = 0; f < sizeof full / sizeof full[0]; f++)
        for (size_t k = 1; k <= strlen(full[f]); k++)
            for (size_t t = 0; t < sizeof tctx / sizeof tctx[0]; t++) {
                char trunc[32], pat[64];
                snprintf(trunc, k + 1, "%s", full[f]);
                snprintf(pat, sizeof pat, tctx[t], trunc);
                /* A prefix that stops before the `\p` is not a cell of this
                 * family — it contains no property escape at all. */
                if (uprop_extent(pat) < 0) continue;
                cell(&bD, pat, 1);
                fD++;
            }
    budget_close(&bD);
    spec_pop("uprop.truncation", fD);

    /* ---- family E: name length, swept rather than known -------------------
     * The second branch of the offset rule lives here: past libpcre2's own
     * name-length limit it stops before the closing brace, and pcrec must stop
     * at the same byte rather than at the extent. */
    Budget bE = { "namelen", 0, 0 };
    long fE = 0;
    static const char pads[] = { ' ', '_', '-', '\t' };
    for (size_t p = 0; p < sizeof pads; p++)
        for (int k = 0; k <= 79; k++) {
            char pat[128]; int n = 0;
            n += snprintf(pat + n, sizeof pat - n, "\\p{L");
            for (int j = 0; j < k && n < (int)sizeof pat - 2; j++) pat[n++] = pads[p];
            pat[n] = 0;
            snprintf(pat + n, sizeof pat - n, "}");
            cell(&bE, pat, 1);
            fE++;
        }
    for (int k = 1; k <= 79; k++) {
        char pat[128]; int n = 0;
        n += snprintf(pat + n, sizeof pat - n, "\\p{");
        for (int j = 0; j < k && n < (int)sizeof pat - 2; j++) pat[n++] = 'X';
        pat[n] = 0;
        snprintf(pat + n, sizeof pat - n, "}");
        cell(&bE, pat, 1);
        fE++;
    }
    budget_close(&bE);
    spec_pop("uprop.namelen", fE);

    /* ---- family F: quote mode ---------------------------------------------
     * Inside `\Q...\E` the text `\p{L}` is five literal characters and no
     * construct at all. pcrec must therefore never blame the property escapes'
     * module for it. Today it refuses earlier, for quote mode's own module,
     * which satisfies the clause; the day quoting is implemented these cells
     * must be ACCEPTED, and the same clause still holds without an edit.
     * That is the whole assertion: not which module, but never THIS one. */
    Budget bF = { "quote_mode", 0, 0 };
    long fF = 0, quoted_named_uprops = 0;
    for (int i = 0; i < ncons; i++)
        for (int w = 0; w < 2; w++) {
            char pat[64];
            snprintf(pat, sizeof pat, w ? "x\\Q%s\\Ey" : "\\Q%s\\E", cons[i]);
            SpecVerdict o = spec_compile(pat);
            SpecPcrecRun r = spec_pcrec_compile(pcrec_path, "all", pat, NULL);
            SpecVClass vc = spec_pcrec_classify(&r);
            fF++;
            if (vc == SPEC_VC_ERROR) {
                budget_fail(&bF, "[quote_mode] pcrec neither accepted nor refused '%s'", pat);
                continue;
            }
            if (vc == SPEC_VC_ACCEPTED && !o.ok)
                budget_fail(&bF, "[quote_mode] MISCOMPILE RISK: pcrec ACCEPTED '%s'; "
                                 "libpcre2 rejects it (error %d)", pat, o.err);
            if (vc != SPEC_VC_MODULE) continue;
            if (strcmp(spec_pcrec_module(&r), uprops_module) == 0) {
                quoted_named_uprops++;
                budget_fail(&bF, "[quote_mode] '%s' was refused for module '%s', but "
                                 "the property escape here is inside \\Q...\\E and is "
                                 "literal text — quote mode was not scanned",
                            pat, uprops_module);
            }
        }
    budget_close(&bF);
    printf("  quote_mode: %ld cell(s) blamed on '%s' (must be 0)\n",
           quoted_named_uprops, uprops_module);
    spec_pop("uprop.quote_mode", fF);

    /* ---- family G: --features cross-configuration --------------------------
     * While the module is unimplemented, --features cannot change any verdict
     * here; the day it is implemented, `none` must still refuse and name it.
     * The durable clause is the one about `none`, and it is what is asserted;
     * `all` is the configuration every other family already uses, and the two
     * are compared so a divergence shows up as a named cell rather than as a
     * quiet difference between two checks. */
    Budget bG = { "config", 0, 0 };
    long fG = 0, config_same = 0, config_differ = 0;
    for (int i = 0; i < ncons; i++) {
        const char *pat = cons[i];
        SpecPcrecRun rn = spec_pcrec_compile(pcrec_path, "none", pat, NULL);
        SpecPcrecRun rm = spec_pcrec_compile(pcrec_path, uprops_module, pat, NULL);
        SpecPcrecRun ra = spec_pcrec_compile(pcrec_path, "all", pat, NULL);
        fG += 3;
        SpecVClass cn = spec_pcrec_classify(&rn), ca = spec_pcrec_classify(&ra);
        if (cn == SPEC_VC_ACCEPTED)
            budget_fail(&bG, "[config] pcrec ACCEPTED '%s' under --features none; "
                             "the property escapes belong to module '%s' and "
                             "cannot be compiled with every module off",
                        pat, uprops_module);
        else if (cn == SPEC_VC_INVALID && spec_compile(pat).ok)
            budget_fail(&bG, "[config] '%s' compiles under libpcre2 but --features "
                             "none refuses it as INVALID rather than naming a module",
                        pat);
        if (cn == ca && spec_pcrec_classify(&rm) == ca) config_same++;
        else config_differ++;
    }
    budget_close(&bG);
    printf("  config: %ld construct(s) answered identically under none / %s / all, "
           "%ld differently\n", config_same, uprops_module, config_differ);
    spec_pop("uprop.config", fG);

    /* ---- family H: the -i flag --------------------------------------------
     * Case folding is pcrec's own flag rather than an inline option, and it is
     * applied to a pattern the compiler has not finished recognising. The
     * clause is that recognition does not depend on it: same verdict class,
     * same offset, with and without. */
    Budget bH = { "case_flag", 0, 0 };
    long fH = 0, case_same = 0;
    for (int i = 0; i < ncons; i++) {
        SpecPcrecRun r0 = spec_pcrec_compile(pcrec_path, "all", cons[i], NULL);
        SpecPcrecRun r1 = spec_pcrec_compile(pcrec_path, "all", cons[i], "-i");
        fH += 2;
        SpecVClass c0 = spec_pcrec_classify(&r0), c1 = spec_pcrec_classify(&r1);
        if (c0 != c1 || spec_pcrec_offset(&r0) != spec_pcrec_offset(&r1))
            budget_fail(&bH, "[case_flag] '%s': without -i pcrec says %s at offset "
                             "%ld, with -i it says %s at offset %ld — recognition "
                             "must not depend on the case flag",
                        cons[i], spec_vclass_name(c0), spec_pcrec_offset(&r0),
                        spec_vclass_name(c1), spec_pcrec_offset(&r1));
        else case_same++;
    }
    budget_close(&bH);
    printf("  case_flag: %ld/%d construct(s) recognised identically with and "
           "without -i\n", case_same, ncons);
    spec_pop("uprop.case_flag", fH);

    /* ---- what the sweep saw ------------------------------------------------ */
    printf("  oracle: %ld accept, %ld reject\n", pop_oracle_accepts, pop_oracle_rejects);
    printf("  pcrec:  %ld accepted, %ld refused-as-unimplemented, %ld "
           "refused-as-out-of-scope, %ld refused-as-invalid\n",
           pop_accepted, pop_refused_module, pop_refused_scope, pop_refused_invalid);
    printf("  offset: %ld at the grammatical extent, %ld at libpcre2's own "
           "earlier stop\n", pop_off_at_extent, pop_off_at_oracle);
    spec_pop("uprop.oracle_accepts", pop_oracle_accepts);
    spec_pop("uprop.oracle_rejects", pop_oracle_rejects);
    spec_pop("uprop.refused_module", pop_refused_module);
    spec_pop("uprop.offset_at_extent", pop_off_at_extent);
    spec_pop("uprop.offset_at_oracle_stop", pop_off_at_oracle);

    static const char *const owned[] = {
        "uprop.registry_rows", "uprop.after_byte", "uprop.braced_marginal",
        "uprop.context", "uprop.truncation", "uprop.namelen", "uprop.quote_mode",
        "uprop.config", "uprop.case_flag", "uprop.oracle_accepts",
        "uprop.oracle_rejects", "uprop.refused_module", "uprop.offset_at_extent",
        "uprop.offset_at_oracle_stop"
    };
    spec_floors_require(owned, (int)(sizeof owned / sizeof owned[0]));
    return spec_finish();
}
