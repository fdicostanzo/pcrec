/* probe_uprops.c — MOD-0.6 (module `unicode-props`) design probes against
 * libpcre2 10.46. Measures \p{...} / \P{...} / \pL / \PL and the K10
 * (\N{U+hhhh}-in-class) cell that this milestone also owns.
 *
 * THE OPTION SET IS BOUND AND STATED HERE (R10 disposition 3: "the mode
 * pcrec compiles for" is PCREC'S OWN decision, not a claim about PCRE2).
 * PRIMARY cell, used for every measurement unless a row says otherwise:
 *
 *     options = 0   (no PCRE2_UTF, no PCRE2_UCP, no PCRE2_CASELESS —
 *                    matches tests/registry/pcre2_check.c's own binding)
 *
 * SECONDARY, measured and LABELED, never silently mixed with the primary
 * column: options = 0 plus a compile-context extra-option bit equal to
 * PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL. That bit is ESTABLISHED BEHAVIOURALLY
 * below (`find_bad_escape_bit`, D30 §4's method — the R13/C5-F14 lesson was
 * "a bit taken from memory or documentation is a claim about a moving
 * target; a bit taken from watching \p{Foo} flip from ERR 147 to COMPILES
 * is a measurement") rather than hand-copied from a header we do not have
 * (`pcre2.h` is not installed on this box — see tests/fuzz/pcre2_abi.h's own
 * header for why the whole tree dlopens instead of linking).
 *
 * Build: TMPDIR=/var/tmp gcc -I tests/fuzz -o /var/tmp/probe_uprops \
 *          tests/probes/probe_uprops.c -ldl
 * Run:   /var/tmp/probe_uprops
 *
 * PREDICTOR, stated before the run (from docs/dev/plan.md's MOD-0.6 row and D33
 * §6's table, both themselves measured, never re-derived from documentation
 * here):
 *
 *   (a) \p{Foo} (unknown property): options=0 -> PCRE2 error 147.
 *       Under the bad-escape-is-literal bit -> COMPILES (three answers for
 *       one construct: REFUSE at options=0, COMPILES under the bit, and
 *       pcrec's own eventual CLAIM-and-implement — D28's axis, "did PCRE2
 *       DISPATCH", says 147 reads as CLAIM: PCRE2 recognised \p{...} as a
 *       property escape and then rejected the NAME, not the escape).
 *   (b) malformed tails: \p at EOF, \p!, \p9 should be SYN_NOT-shaped (no
 *       property syntax dispatched at all) -> some OTHER PCRE2 error, not
 *       147; \p{ at EOF / \p{} / \p{L (unterminated) should be
 *       SYN_MALFORMED-shaped (PCRE2 dispatched to the {...} form and then
 *       hit truncation) -> MEASURE whether that is also 147 or a distinct
 *       "missing terminating brace" number.
 *   (c) \p{^L} caret negation compiles (property negation, distinct from
 *       \P); \pX/\PX single-letter forms compile only for PCRE2's short
 *       general-category letters (a subset of A-Z, MEASURE which), never
 *       for lowercase (lowercase collides with nothing — MEASURE).
 *   (d) insignificant bytes in the body: space, hyphen, underscore, tab,
 *       ASCII case — MEASURE each independently against the \p{L} baseline
 *       (semantic check: matches "A", does not match "1"); a valid body
 *       survives huge insignificant padding (streaming, not truncation);
 *       the SIGNIFICANT-character boundary sits at 48 per R10 disposition
 *       5 — MEASURE the exact PCRE2 error code on both sides, both for a
 *       bare run of significant characters and for the same run padded
 *       with insignificant filler between each character (proves the
 *       count is of SIGNIFICANT characters, not of total body bytes).
 *   (e) in-class: [\p{L}] [\P{L}] [\pL] compile as sets; [\N{U+41}] is
 *       PCRE2 193 in every class position (K10's oracle cell) including as
 *       a range endpoint, where \p{L} (a certified SET shape) instead
 *       yields the RANGE error (150-family) and \p{Foo} (uncertifiable —
 *       the name is bad) yields its OWN 147, not the range error — the D33
 *       §6 shape-column claim, re-measured for the `unicode-props` bucket
 *       specifically rather than assumed from the `\d`/`\N` examples it was
 *       built on (D27's "a design measured on one example inherits that
 *       example's alphabet").
 *
 * MEASURED (2026-08-12, libpcre2 10.46; post-run notes — predictions above
 * are as stated before the run):
 *   - PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL established behaviourally as bit
 *     0x00000002 (not taken from a header — none is installed on this box).
 *   - \p{Foo}/\P{Foo}: ERR 147 at options=0, COMPILES under the bit — the
 *     predicted three-answers cell, confirmed.
 *   - THE HEADLINE FINDING, WIDER THAN PREDICTED: \p/\P have NO DECLINE-
 *     shaped tail at all. A full 256-byte sweep of the byte immediately
 *     after the selector lands EVERY byte on exactly one of {COMPILES (14),
 *     ERR 146 "malformed \P or \p sequence" (204), ERR 147 "unknown
 *     property..." (38)} — never any other code, never a code that would
 *     read as "not a \p construct, carry on". The two-way split: a single
 *     letter tail (52 of them) is ERR 147 if the letter is not one of the
 *     14 recognised short names (case-INSENSITIVE — see below), else
 *     COMPILES; every other single byte (204 = 256-52), including `{` with
 *     nothing/an incomplete body after it and end-of-pattern (avail=0), is
 *     ERR 146. A `{...}` body that IS terminated splits the same way:
 *     empty/unknown/malformed-caret name -> 147, unterminated (any content)
 *     -> 146.
 *   - Single-letter short names are CASE-INSENSITIVE and the recognised set
 *     is NOT all 26: only C L M N P S Z (both cases) compile as bare \pX;
 *     the other 19 letters, upper or lower, are ERR 147 (dispatched,
 *     unknown name) — not ERR 146. Corrects this file's own predictor,
 *     which expected lowercase to be uniformly refused.
 *   - insignificant in the body: space (leading/trailing/internal),
 *     hyphen, underscore, tab, and ASCII case are ALL insignificant —
 *     every variant of \p{L}/\p{Letter} tested normalises to the same
 *     property (verified semantically: matches 'A', not '1').
 *   - streaming confirmed: a body of 1 significant char + 100,000
 *     insignificant spaces (100,001 total body bytes) COMPILES.
 *   - the 48/49 boundary is EXACT and its offset is a STREAMING signature,
 *     not an end-of-body one: n=48 significant chars -> ERR 147 (unknown
 *     property, blamed at the END of the pattern); n=49 -> ERR 146
 *     (malformed, blamed immediately after the 49th significant character
 *     it consumed — NOT at the closing brace or end of pattern). Re-run
 *     with a space inserted after every significant character (so total
 *     body length roughly doubles): the n=49 blame offset moves in lockstep
 *     with "one past the 49th significant char", not with total body
 *     length — direct evidence the scanner counts significant characters
 *     as it streams, exactly as D30/R10 disposition 5 specifies, and does
 *     not buffer-then-normalise.
 *   - class position: [\p{L}] [\P{L}] [\pL] [\PL] all COMPILE (set-shaped).
 *     [\N{U+41}] is ERR 193 in every position tested (bare, leading,
 *     trailing, low endpoint, negated class) — K10's oracle cell, exactly
 *     as docs/dev/known_issues.md records. Bare [\N] stays ERR 171 (unaffected
 *     — this milestone does not touch that row).
 *   - the caret does NOT count toward the 48/49 boundary: \p{^ + 48 A's} is
 *     ERR 147 (unknown), \p{^ + 49 A's} is ERR 146 at offset "right after
 *     the 49th A", i.e. the same 48-significant-character cap applies to
 *     the NAME only, counted after any leading `^` is consumed separately.
 *   - endpoint shape column, `unicode-props`-specific re-measurement of D33
 *     §6: [0-\p{L}] (certifiable SET) -> ERR 150 "invalid range", PCRE2's
 *     endpoint rule, NOT \p{L}'s own text; [0-\p{Foo}] (bad name, cannot be
 *     certified) -> ITS OWN ERR 147, the range check never runs;
 *     [0-\N{U+41}] (SCALAR) -> its own ERR 193. Confirms D33 §6's shape
 *     column on this bucket rather than assuming it from \d/\N.
 *   - Script=/sc= forms and internal `=`-whitespace all compile
 *     (\p{Script=Latin}, \p{sc=Latin}, \p{ Script = Latin }); \p{Any}
 *     compiles; \p{^} and \p{^^L} are ERR 147 (caret-then-nothing / double
 *     caret read as part of an unknown name, not a distinct malformed-caret
 *     error); \p{...} is quantifiable (a\p{L}*, a\p{L}*?).
 */
#define _GNU_SOURCE
#include "pcre2_abi.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

static Pcre2Abi abi;

/* ---- extras pcre2_abi.h does not carry (probe_digit_sweep.c's precedent:
 * dlsym straight off abi.handle rather than editing the shared header for
 * one consumer) ------------------------------------------------------- */
typedef pcre2_compile_context_8 *(*fn_cctx_create)(pcre2_general_context_8 *);
typedef void                     (*fn_cctx_free)(pcre2_compile_context_8 *);
typedef int                      (*fn_set_extra)(pcre2_compile_context_8 *, uint32_t);

static fn_cctx_create cctx_create;
static fn_cctx_free   cctx_free;
static fn_set_extra   set_extra;

/* ---- low-level compile/verdict helpers -------------------------------- */

/* Compile `pat[0..len)` at options=0, optionally with an extra-options
 * bitmask applied through a compile context (extra_bits == 0 means "no
 * context, plain options=0 compile" so the PRIMARY cell never depends on
 * the extras being resolvable). */
static pcre2_code_8 *comp_extra(const char *pat, size_t len, uint32_t extra_bits,
                                int *err, size_t *eoff)
{
    pcre2_compile_context_8 *cc = NULL;
    if (extra_bits && cctx_create && set_extra) {
        cc = cctx_create(NULL);
        set_extra(cc, extra_bits);
    }
    pcre2_code_8 *code = abi.compile((PCRE2_SPTR)pat, len, 0, err, eoff, cc);
    if (cc) cctx_free(cc);
    return code;
}

/* Print one row: label, then either "COMPILES" or "ERR nnn at N  message". */
static void verdict_n(const char *label, const char *pat, size_t len, uint32_t extra_bits)
{
    int err = 0; size_t eoff = 0;
    pcre2_code_8 *code = comp_extra(pat, len, extra_bits, &err, &eoff);
    printf("  %-46s ", label);
    if (!code) {
        unsigned char msg[120];
        abi.get_error_message(err, msg, sizeof msg);
        printf("ERR %3d at %2zu  %s\n", err, eoff, msg);
        return;
    }
    printf("COMPILES\n");
    abi.code_free(code);
}
static void verdict(const char *pat, uint32_t extra_bits)
{
    verdict_n(pat, pat, strlen(pat), extra_bits);
}

/* Does `pat` (options=0, plus extra_bits) match single-byte subject b? */
static int matches_byte(const char *pat, size_t len, uint32_t extra_bits, int b)
{
    int err = 0; size_t eoff = 0;
    pcre2_code_8 *code = comp_extra(pat, len, extra_bits, &err, &eoff);
    if (!code) return -1; /* did not compile */
    unsigned char s[1] = { (unsigned char)b };
    pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
    int rc = abi.match(code, s, 1, 0, 0, md, NULL);
    abi.match_data_free(md);
    abi.code_free(code);
    return rc >= 0;
}

/* ---- (a)/§bit — establish PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL behaviourally
 * -------------------------------------------------------------------- */
static uint32_t find_bad_escape_bit(void)
{
    if (!cctx_create || !set_extra) return 0;
    const char *pat = "\\p{Foo}";
    /* baseline at options=0, no extras: must be the known ERR 147. */
    int err = 0; size_t eoff = 0;
    pcre2_code_8 *base = comp_extra(pat, strlen(pat), 0, &err, &eoff);
    if (base) { abi.code_free(base); printf("  BASELINE UNEXPECTED: \\p{Foo} compiles at options=0 with no extras\n"); return 0; }
    if (err != 147)
        printf("  BASELINE NOTE: \\p{Foo} errs %d (plan predicted 147) — recording anyway\n", err);

    for (int b = 0; b < 32; b++) {
        uint32_t bit = 1u << b;
        int e2 = 0; size_t eo2 = 0;
        pcre2_code_8 *code = comp_extra(pat, strlen(pat), bit, &e2, &eo2);
        if (code) { abi.code_free(code); return bit; }
    }
    return 0;
}

/* ---- table-driven cells ------------------------------------------------ */

static void section(const char *title)
{
    printf("\n== %s ==\n", title);
}

int main(void)
{
    char why[256];
    if (pcre2_abi_load(&abi, why, sizeof why) != PCRE2_ABI_OK) {
        fprintf(stderr, "SKIP: %s\n", why);
        return 2;
    }
    cctx_create = (fn_cctx_create)dlsym(abi.handle, "pcre2_compile_context_create_8");
    cctx_free   = (fn_cctx_free)  dlsym(abi.handle, "pcre2_compile_context_free_8");
    set_extra   = (fn_set_extra)  dlsym(abi.handle, "pcre2_set_compile_extra_options_8");
    if (!cctx_create || !cctx_free || !set_extra)
        printf("NOTE: extra-options symbols not resolved — the "
               "EXTRA_BAD_ESCAPE_IS_LITERAL column will be skipped\n");

    uint32_t bad_escape_bit = find_bad_escape_bit();
    printf("PCRE2_EXTRA_BAD_ESCAPE_IS_LITERAL established behaviourally as "
           "bit 0x%08x (0 means: not found / symbols unavailable)\n",
           bad_escape_bit);

    /* ---- (a) three-answers inventory: \p{Foo} -------------------------- */
    section("(a) \\p{Foo} — the three-answers inventory");
    verdict("\\p{Foo}", 0);
    if (bad_escape_bit) verdict("\\p{Foo}", bad_escape_bit);
    verdict("\\P{Foo}", 0);
    if (bad_escape_bit) verdict("\\P{Foo}", bad_escape_bit);

    /* ---- (b) malformed-tail taxonomy, \p and \P ------------------------ */
    section("(b) malformed-tail taxonomy — \\p");
    verdict_n("\\p at EOF", "\\p", 2, 0);
    verdict("\\p!", 0);
    verdict("\\p9", 0);
    verdict_n("\\p{ unterminated at EOF", "\\p{", 3, 0);
    verdict("\\p{}", 0);
    verdict_n("\\p{L unterminated (valid prefix)", "\\p{L", 4, 0);
    verdict("\\pL", 0);
    verdict("\\p{L}", 0);
    section("(b) malformed-tail taxonomy — \\P");
    verdict_n("\\P at EOF", "\\P", 2, 0);
    verdict("\\P!", 0);
    verdict("\\P9", 0);
    verdict_n("\\P{ unterminated at EOF", "\\P{", 3, 0);
    verdict("\\P{}", 0);
    verdict_n("\\P{L unterminated (valid prefix)", "\\P{L", 4, 0);
    verdict("\\PL", 0);
    verdict("\\P{L}", 0);

    /* also under the bad-escape-is-literal bit, since a malformed tail
     * might read as a DIFFERENT escape altogether once \p can be literal */
    if (bad_escape_bit) {
        section("(b) malformed-tail taxonomy under EXTRA_BAD_ESCAPE_IS_LITERAL");
        verdict_n("\\p at EOF", "\\p", 2, bad_escape_bit);
        verdict("\\p!", bad_escape_bit);
        verdict("\\p9", bad_escape_bit);
        verdict_n("\\p{ unterminated at EOF", "\\p{", 3, bad_escape_bit);
        verdict("\\p{}", bad_escape_bit);
        verdict_n("\\p{L unterminated", "\\p{L", 4, bad_escape_bit);
    }

    /* ---- (c) caret negation, single-letter sweep ------------------------ */
    section("(c) \\p{^L} / \\P{^L} caret negation");
    verdict("\\p{^L}", 0);
    verdict("\\P{^L}", 0);
    verdict("\\p{^Foo}", 0);

    section("(c) \\pX single-letter sweep, X = A..Z");
    {
        int compiled_upper[26] = {0};
        for (int i = 0; i < 26; i++) {
            char pat[8]; snprintf(pat, sizeof pat, "\\p%c", 'A' + i);
            int err = 0; size_t eoff = 0;
            pcre2_code_8 *c = comp_extra(pat, strlen(pat), 0, &err, &eoff);
            compiled_upper[i] = c != NULL;
            if (c) abi.code_free(c);
        }
        printf("  \\pA..\\pZ compiling: ");
        for (int i = 0; i < 26; i++) if (compiled_upper[i]) putchar('A' + i);
        putchar('\n');
        printf("  \\pA..\\pZ NOT compiling: ");
        for (int i = 0; i < 26; i++) if (!compiled_upper[i]) putchar('A' + i);
        putchar('\n');
    }
    section("(c) \\pX single-letter sweep, X = a..z (lowercase)");
    {
        int compiled_lower[26] = {0};
        for (int i = 0; i < 26; i++) {
            char pat[8]; snprintf(pat, sizeof pat, "\\p%c", 'a' + i);
            int err = 0; size_t eoff = 0;
            pcre2_code_8 *c = comp_extra(pat, strlen(pat), 0, &err, &eoff);
            compiled_lower[i] = c != NULL;
            if (c) abi.code_free(c);
        }
        printf("  \\pa..\\pz compiling: ");
        for (int i = 0; i < 26; i++) if (compiled_lower[i]) putchar('a' + i);
        putchar('\n');
        printf("  \\pa..\\pz NOT compiling (should be all 26): ");
        int all_fail = 1;
        for (int i = 0; i < 26; i++) if (!compiled_lower[i]) putchar('a' + i); else all_fail = 0;
        putchar('\n');
        printf("  (all lowercase single-letter forms refused: %s)\n", all_fail ? "yes" : "NO — see above");
    }
    /* same sweep for \P */
    section("(c) \\PX single-letter sweep, X = A..Z");
    {
        int compiled_upper[26] = {0};
        for (int i = 0; i < 26; i++) {
            char pat[8]; snprintf(pat, sizeof pat, "\\P%c", 'A' + i);
            int err = 0; size_t eoff = 0;
            pcre2_code_8 *c = comp_extra(pat, strlen(pat), 0, &err, &eoff);
            compiled_upper[i] = c != NULL;
            if (c) abi.code_free(c);
        }
        printf("  \\PA..\\PZ compiling: ");
        for (int i = 0; i < 26; i++) if (compiled_upper[i]) putchar('A' + i);
        putchar('\n');
    }

    /* ---- (d) normalisation --------------------------------------------- */
    section("(d) insignificant-byte census against the \\p{L} baseline");
    {
        /* baseline semantics: matches 'A', does not match '1' */
        int base_a = matches_byte("^\\p{L}$", strlen("^\\p{L}$"), 0, 'A');
        int base_1 = matches_byte("^\\p{L}$", strlen("^\\p{L}$"), 0, '1');
        printf("  baseline ^\\p{L}$ vs 'A': %s   vs '1': %s\n",
               base_a == 1 ? "MATCH" : base_a == 0 ? "no match" : "no compile",
               base_1 == 1 ? "MATCH" : base_1 == 0 ? "no match" : "no compile");

        struct { const char *label; const char *body; } cells[] = {
            { "space around name:  \\p{ L }",     " L " },
            { "leading space:      \\p{ L}",      " L"  },
            { "trailing space:     \\p{L }",      "L "  },
            { "hyphen prefix:      \\p{-L}",      "-L"  },
            { "underscore prefix:  \\p{_L}",      "_L"  },
            { "hyphen+underscore:  \\p{_-L}",     "_-L" },
            { "tab prefix:         \\p{\\tL}",    "\tL" },
            { "lowercase name:     \\p{l}",       "l"   },
            { "mixed case (n/a for single letter, use Letter): \\p{Letter}", "Letter" },
            { "uppercase form:     \\p{LETTER}",  "LETTER" },
            { "lowercase form:     \\p{letter}",  "letter" },
            { "internal space:     \\p{L e t t e r}", "L e t t e r" },
            { "internal hyphen:    \\p{L-e-t-t-e-r}", "L-e-t-t-e-r" },
            { "internal underscore:\\p{L_e_t_t_e_r}", "L_e_t_t_e_r" },
        };
        for (size_t i = 0; i < sizeof cells / sizeof cells[0]; i++) {
            char pat[64]; size_t k = 0;
            pat[k++] = '^'; pat[k++] = '\\'; pat[k++] = 'p'; pat[k++] = '{';
            size_t bl = strlen(cells[i].body);
            memcpy(pat + k, cells[i].body, bl); k += bl;
            pat[k++] = '}'; pat[k++] = '$'; pat[k] = 0;
            int err = 0; size_t eoff = 0;
            pcre2_code_8 *code = comp_extra(pat, k, 0, &err, &eoff);
            if (!code) {
                unsigned char msg[120]; abi.get_error_message(err, msg, sizeof msg);
                printf("  %-58s ERR %3d at %2zu  %s\n", cells[i].label, err, eoff, msg);
                continue;
            }
            int m_a, m_1;
            {
                unsigned char s[1] = {'A'};
                pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
                m_a = abi.match(code, s, 1, 0, 0, md, NULL) >= 0;
                abi.match_data_free(md);
            }
            {
                unsigned char s[1] = {'1'};
                pcre2_match_data_8 *md = abi.match_data_create(4, NULL);
                m_1 = abi.match(code, s, 1, 0, 0, md, NULL) >= 0;
                abi.match_data_free(md);
            }
            abi.code_free(code);
            printf("  %-58s COMPILES  'A':%s  '1':%s  %s\n", cells[i].label,
                   m_a ? "MATCH" : "no", m_1 ? "MATCH" : "no",
                   (m_a && !m_1) ? "== \\p{L} semantics" : "DIFFERENT semantics");
        }
    }

    section("(d) streaming: a valid 1-significant-char body padded to ~100,006 bytes");
    {
        size_t pad = 100000;
        size_t total = 1 /*L*/ + pad + strlen("\\p{}");
        char *pat = malloc(total + 8);
        size_t k = 0;
        pat[k++] = '\\'; pat[k++] = 'p'; pat[k++] = '{';
        pat[k++] = 'L';
        for (size_t i = 0; i < pad; i++) pat[k++] = ' '; /* insignificant filler */
        pat[k++] = '}';
        pat[k] = 0;
        printf("  body length = %zu bytes (1 significant char, %zu spaces)\n", k - 4, pad);
        int err = 0; size_t eoff = 0;
        pcre2_code_8 *code = comp_extra(pat, k, 0, &err, &eoff);
        if (!code) {
            unsigned char msg[120]; abi.get_error_message(err, msg, sizeof msg);
            printf("  ERR %d at %zu  %s\n", err, eoff, msg);
        } else {
            printf("  COMPILES\n");
            abi.code_free(code);
        }
        free(pat);
    }

    section("(d) the 48/49 SIGNIFICANT-character boundary — plain run of 'A'");
    {
        for (int n = 40; n <= 55; n++) {
            char pat[80]; size_t k = 0;
            pat[k++] = '\\'; pat[k++] = 'p'; pat[k++] = '{';
            for (int i = 0; i < n; i++) pat[k++] = 'A';
            pat[k++] = '}'; pat[k] = 0;
            int err = 0; size_t eoff = 0;
            pcre2_code_8 *code = comp_extra(pat, k, 0, &err, &eoff);
            printf("  n=%2d significant 'A's: ", n);
            if (!code) {
                unsigned char msg[120]; abi.get_error_message(err, msg, sizeof msg);
                printf("ERR %3d at %2zu  %s\n", err, eoff, msg);
            } else {
                printf("COMPILES\n");
                abi.code_free(code);
            }
        }
    }

    section("(d) the same boundary, PADDED with an insignificant space after every "
            "significant char (proves the count is of SIGNIFICANT chars, not total bytes)");
    {
        for (int n = 40; n <= 55; n++) {
            char pat[160]; size_t k = 0;
            pat[k++] = '\\'; pat[k++] = 'p'; pat[k++] = '{';
            for (int i = 0; i < n; i++) { pat[k++] = 'A'; pat[k++] = ' '; }
            pat[k++] = '}'; pat[k] = 0;
            int err = 0; size_t eoff = 0;
            pcre2_code_8 *code = comp_extra(pat, k, 0, &err, &eoff);
            printf("  n=%2d significant 'A's, body %2zu bytes: ", n, k - 4);
            if (!code) {
                unsigned char msg[120]; abi.get_error_message(err, msg, sizeof msg);
                printf("ERR %3d at %2zu  %s\n", err, eoff, msg);
            } else {
                printf("COMPILES\n");
                abi.code_free(code);
            }
        }
    }

    section("(d) does the negation caret count toward the 48/49 boundary? "
            "\\p{^ + n A's}");
    {
        for (int n = 46; n <= 50; n++) {
            char pat[80]; size_t k = 0;
            pat[k++] = '\\'; pat[k++] = 'p'; pat[k++] = '{'; pat[k++] = '^';
            for (int i = 0; i < n; i++) pat[k++] = 'A';
            pat[k++] = '}'; pat[k] = 0;
            int err = 0; size_t eoff = 0;
            pcre2_code_8 *code = comp_extra(pat, k, 0, &err, &eoff);
            printf("  caret + n=%2d significant 'A's: ", n);
            if (!code) {
                unsigned char msg[120]; abi.get_error_message(err, msg, sizeof msg);
                printf("ERR %3d at %2zu  %s\n", err, eoff, msg);
            } else {
                printf("COMPILES\n");
                abi.code_free(code);
            }
        }
    }

    /* ---- (e) in-class cells --------------------------------------------- */
    section("(e) in-class: \\p{L} \\P{L} \\pL, and the K10 oracle \\N{U+41}");
    verdict("[\\p{L}]", 0);
    verdict("[\\P{L}]", 0);
    verdict("[\\pL]", 0);
    verdict("[\\PL]", 0);
    verdict("[\\N{U+41}]", 0);
    verdict("[x\\N{U+41}]", 0);
    verdict("[\\N{U+41}x]", 0);
    verdict("[a-\\N{U+41}]", 0);
    verdict("[^\\N{U+41}]", 0);
    verdict("[\\N]", 0); /* bare \N in class: must STAY refused (err 171), not this milestone's fix */

    section("(e) endpoint-rule shape check: \\p{L} (certifiable SET) vs \\p{Foo} (bad name) vs \\N{U+41} (SCALAR)");
    verdict("[0-\\p{L}]", 0);
    verdict("[0-\\p{Foo}]", 0);
    verdict("[0-\\N{U+41}]", 0);
    verdict("[\\p{L}-z]", 0);
    verdict("[\\N{U+41}-z]", 0);

    /* ---- (f) anything else worth a cell ---------------------------------- */
    section("(f) quantifiability, Script= form, and whitespace around '='");
    verdict("a\\p{L}*", 0);
    verdict("a\\p{L}*?", 0);
    verdict("\\p{Script=Latin}", 0);
    verdict("\\p{sc=Latin}", 0);
    verdict("\\p{ Script = Latin }", 0);
    verdict("\\p{Any}", 0);
    verdict("\\p{^}", 0);          /* caret with nothing after it */
    verdict("\\p{^^L}", 0);        /* double caret */
    verdict_n("\\p{L} then more pattern", "\\p{L}a+", strlen("\\p{L}a+"), 0);

    /* ---- (b), widened: a full 256-byte sweep of the byte immediately after
     * \p, to check for a DECLINE-shaped tail the curated cells above might
     * have missed (the reject/registry-check convention's own 255-byte
     * doorway sweep, applied here as a design measurement). If \p/\P really
     * dispatch on EVERY tail, every byte below lands on {COMPILES, ERR 146,
     * ERR 147} and nothing else. */
    section("(b) widened: 256-byte sweep of the byte after \\p — error-code census");
    {
        int census_compiles = 0, census_146 = 0, census_147 = 0, census_other = 0;
        char other_bytes[512]; size_t other_k = 0;
        for (int b = 0; b < 256; b++) {
            char pat[4] = { '\\', 'p', (char)b, 0 };
            int err = 0; size_t eoff = 0;
            pcre2_code_8 *code = comp_extra(pat, 3, 0, &err, &eoff);
            if (code) { census_compiles++; abi.code_free(code); }
            else if (err == 146) census_146++;
            else if (err == 147) census_147++;
            else {
                census_other++;
                other_k += (size_t)snprintf(other_bytes + other_k,
                    other_k < sizeof other_bytes ? sizeof other_bytes - other_k : 0,
                    "0x%02x(err%d) ", b, err);
            }
        }
        printf("  COMPILES: %d   ERR 146: %d   ERR 147: %d   OTHER: %d\n",
               census_compiles, census_146, census_147, census_other);
        if (census_other)
            printf("  OTHER bytes/codes: %s\n", other_bytes);
        else
            printf("  every one of the 256 tail bytes lands on {COMPILES, 146, 147} "
                   "— no DECLINE-shaped tail exists for \\p\n");
    }
    section("(b) widened: same 256-byte sweep for \\P");
    {
        int census_compiles = 0, census_146 = 0, census_147 = 0, census_other = 0;
        char other_bytes[512]; size_t other_k = 0;
        for (int b = 0; b < 256; b++) {
            char pat[4] = { '\\', 'P', (char)b, 0 };
            int err = 0; size_t eoff = 0;
            pcre2_code_8 *code = comp_extra(pat, 3, 0, &err, &eoff);
            if (code) { census_compiles++; abi.code_free(code); }
            else if (err == 146) census_146++;
            else if (err == 147) census_147++;
            else {
                census_other++;
                other_k += (size_t)snprintf(other_bytes + other_k,
                    other_k < sizeof other_bytes ? sizeof other_bytes - other_k : 0,
                    "0x%02x(err%d) ", b, err);
            }
        }
        printf("  COMPILES: %d   ERR 146: %d   ERR 147: %d   OTHER: %d\n",
               census_compiles, census_146, census_147, census_other);
        if (census_other)
            printf("  OTHER bytes/codes: %s\n", other_bytes);
        else
            printf("  every one of the 256 tail bytes lands on {COMPILES, 146, 147} "
                   "— no DECLINE-shaped tail exists for \\P\n");
    }
    /* also: is `avail == 0` (truncated pattern, no tail byte at all) always
     * 146, matching "\\p at EOF" above but stated as its own cell since the
     * doorway's tail-less question is a distinct code path (avail=0). */

    printf("\nDONE.\n");
    return 0;
}
