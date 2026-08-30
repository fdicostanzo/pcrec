/* definitions_oracle_gen.c — [DD-11.3]'s CELL GENERATOR: walks the live
 * `RegRow.definitions` table through the REAL tag evaluator
 * (`pcrec_def_resolve`, src/parse/definitions.c) and emits, one line per
 * TSV `cell_id\tpattern_a\tpattern_b\tdescription`, the option-matrix
 * self-oracle's own input: Pattern A (the row's construct in the option
 * context that selects this entry) and Pattern B (the resolved
 * definition's OWN core-syntax text). Both are then compiled and run by
 * run_definitions_oracle.sh's differential (definitions_oracle_driver.c
 * for the A==B leg, definitions_oracle_check.c for the A==C libpcre2 leg)
 * — this program only computes WHAT to compare, never runs a match
 * itself, the same division PC-4's patterns.tsv generation (inline in
 * run_pc4.sh) and its check binary keep.
 *
 * WHY THIS MUST LINK libpcrec.a RATHER THAN SHELL OUT TO `--list-
 * definitions`: the dump prints every entry in a row's list regardless of
 * whether it FIRES under a given option state; only `pcrec_def_resolve`,
 * called with a real `Ctx` under a real `(multiline, nocap)` state,
 * authoritatively answers "which entry applies here" — including walking
 * a `DEFK_ROW` chain to its final resolved entry, which this program never
 * has to know about (`pcrec_def_resolve` does it once, internally).
 *
 * SCOPE (r43-third-round follow-up, team-lead ruling 2026-08-29, CLOSED —
 * the two paragraphs below describe how, replacing the original "deferred"
 * scope notes for both families):
 *
 * `DEFK_TEXTFN` rows (`\c`, `\o{}`, octal/`\0`, `\N{U+}`, bare `\x`) join
 * the sweep via `textfn_cells()`. Pattern B is the decoded byte RE-SPELLED
 * in a DIFFERENT escape family than the construct under test (the ruling's
 * own examples: `\cA` -> `\x01`, `\o{101}` -> `\x41`, `\0`/`\012` ->
 * `\x0a`, `\N{U+41}` -> `\x41`; the bare-`\x` row's own respelling is a
 * printable LITERAL instead, since hex-for-hex would be no respelling at
 * all -- `\x41` -> `A`, falling back to `\xHH` only where the byte has no
 * safe literal). The decoded byte comes off the textfn's OWN output AST
 * bitmap (`textfn_byte`, below) rather than a second hex/octal/xor
 * decode written here -- "the point is that the textfn's decode and
 * libpcre2's agree on the byte" (the ruling's own words), which a
 * parallel arithmetic implementation in this file could not prove even if
 * it agreed. Three of the five rows (`\c`, `\o{}`, `\N{U+`) are UNBUILT
 * (module misc/unicode-props, confirmed live via
 * `pcrec_construct_built_status` — `build/pcrec --features all
 * --list-syntax` reads `unbuilt` for all three): pcrec cannot compile
 * their real spelling at all, so for those three the CELL's Pattern A is
 * Pattern B repeated (a harmless, always-equal tautology — never a
 * REFUSED-A) and the real spelling travels in a FIFTH TSV column,
 * `oracle_a`, which `definitions_oracle_check.c`'s libpcre2 leg reads
 * INSTEAD OF Pattern A for those cells only (a `-` in that column means
 * "use Pattern A", the ordinary case). The other two (bare `\x`, `\0`) are
 * built, so their real spelling compiles normally and takes the ordinary
 * Pattern-A slot exactly like every DEFK_STR row above.
 *
 * The 14-name POSIX class-name family shares ONE row
 * (`[[:alpha:]]`'s row carries all 14 as separate DEF_ALWAYS entries,
 * selected by which NAME LITERAL appears in the probe text, never by
 * option state — `pcrec_def_resolve`'s first-applicable-wins walk over an
 * all-DEF_ALWAYS list still always returns entry 1, "alnum"). The
 * r43-third-round ruling gave each entry an `operand` field (the name
 * itself, registry.c's `posix_def[]`) precisely so this pass need not go
 * through `pcrec_def_resolve` for this row at all: `operand_cells()`
 * walks every entry directly, builds Pattern A as `[[:<operand>:]]`, and
 * emits 14 real cells rather than the previous single-entry skip. */

#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

/* [DD-11.3]'s manager-specified body set for a DEFK_BUILDER template's `X`
 * placeholder. */
static const char *const BODIES[] = { "a", "(a)", "[ab]", "a|b", "\\d+" };
#define N_BODIES (sizeof BODIES / sizeof BODIES[0])

/* [DD-11.3 follow-up, r43-third-round, 2026-08-29] sampled operands per
 * DEFK_TEXTFN row -- team-lead's own list. Bare `\x` samples all 256
 * values instead (generated in `main`'s own loop, not listed here: a
 * 256-entry literal array would just be `main`'s loop written out by
 * hand). */
static const char *const CX_OPS[] = {
    "A", "B", "M", "Z", "a", "m", "z", "@", "^", "_", "?", "["
};
static const char *const OCTAL_BRACE_OPS[] = {
    "0", "1", "7", "10", "17", "77", "100", "101", "177", "200", "377"
};
static const char *const OCTAL_ZERO_OPS[] = {
    "0", "01", "07", "010", "012", "017", "077"
};
static const char *const UNICODE_OPS[] = {
    "0000", "0041", "007f", "00ff"
};
#define NOPS(a) (sizeof (a) / sizeof (a)[0])

static int n_cells = 0, n_deferred = 0;

/* `oracle_a` is the FIFTH TSV column (r43-third-round follow-up): "-"
 * means "definitions_oracle_check.c's libpcre2 leg uses Pattern A as-is",
 * the ordinary case every pre-existing caller below passes; a real pattern
 * text means "use THIS instead" (today: the three UNBUILT DEFK_TEXTFN
 * rows' real spelling, which Pattern A cannot itself be — see
 * `textfn_cells`). "-" rather than an empty string because `%[^\t]`-style
 * scanf field extraction cannot match a zero-length field, definitions_
 * oracle_check.c's own header will explain when the reader gets there. */
static void emit(const char *a, const char *b, const char *oracle_a,
                  const char *desc)
{
    printf("%d\t%s\t%s\t%s\t%s\n", n_cells, a, b, oracle_a, desc);
    n_cells++;
}

/* Replace every occurrence of the single byte `X` in `tmpl` with `body`,
 * into `out` (size `outsz`). The templates this table carries use `X` as
 * their ONLY metacharacter (internal.h's placeholder convention before
 * `DefBuilderFn`), so a byte-wise scan is exact — no need for a real
 * template-language parser over a two-row population. */
static void subst_x(char *out, size_t outsz, const char *tmpl, const char *body)
{
    size_t bl = strlen(body);
    size_t o = 0;
    for (const char *p = tmpl; *p && o + 1 < outsz; p++) {
        if (*p == 'X') {
            if (o + bl >= outsz) break;
            memcpy(out + o, body, bl);
            o += bl;
        } else {
            out[o++] = *p;
        }
    }
    out[o] = '\0';
}

/* The possessive-suffix family's four rows share ONE template
 * ("X<quant>+ \xe2\x89\xa1 (?>X<quant>)") that names the SHAPE, not
 * instantiable text — `<quant>` stands for whichever quantifier this
 * particular row is (`*`, `+`, `?`, `{1,2}`), which the template alone
 * cannot supply. The row's own `syntax` can: it is always ONE CHARACTER
 * of body ('a') followed by the row's real possessive suffix (e.g.
 * "a*+", "a{1,2}+"), so stripping that leading byte recovers the exact
 * suffix text, and stripping ITS trailing '+' recovers the atomic form's
 * bare quantifier. Dispatched on `d->builder`'s pointer identity — the
 * same "which shape is this" test `mod_uprops.c`'s marker fields and
 * `pcrec_registry_row_answers` use elsewhere in this tree — rather than
 * parsing `<quant>` out of the template text. */
static void possessive_cell(const RegRow *r, const char *opt_prefix)
{
    size_t slen = strlen(r->syntax);
    if (slen < 2) return; /* defensive; every shipped row is >= "a*+" */
    const char *suffix = r->syntax + 1;         /* e.g. "*+", "{1,2}+" */
    size_t suflen = strlen(suffix);
    char quant[32];
    if (suflen == 0 || suffix[suflen - 1] != '+' || suflen >= sizeof quant)
        return;
    memcpy(quant, suffix, suflen - 1);
    quant[suflen - 1] = '\0';                    /* e.g. "*", "{1,2}" */

    /* A possessive suffix attaches to an ATOM. "a" is one; "a|b" and
     * "\d+" (already quantified) are NOT, and applying the suffix
     * directly to either is a different construct (alternation with a
     * quantified last branch; a double-quantifier error) rather than a
     * quantified BODY. Wrapping every body in a non-capturing group is
     * uniformly safe (`(?:a)*+` matches exactly what `a*+` does) and
     * needs no per-body atomicity test. */
    char desc[192];
    for (size_t i = 0; i < N_BODIES; i++) {
        const char *body = BODIES[i];
        char a[256], b[256];
        snprintf(a, sizeof a, "%s(?:%s)%s", opt_prefix, body, suffix);
        snprintf(b, sizeof b, "(?>(?:%s)%s)", body, quant);
        snprintf(desc, sizeof desc, "%s (body=%s)", r->syntax, body);
        emit(a, b, "-", desc);
    }
}

static void builder_template_cell(const RegRow *r, const RegDef *d,
                                   const char *opt_prefix)
{
    if (d->builder == pcrec_def_build_atomic) {
        possessive_cell(r, opt_prefix);
        return;
    }
    /* Generic X-substitution: split the template on " \xe2\x89\xa1 " (the
     * literal "X ... \xe2\x89\xa1 ... X" shape internal.h's DEFK_BUILDER
     * comment states), instantiate each half over the body set. Today's
     * only user is `(?n)(X) \xe2\x89\xa1 (?:X)` — note its LHS is the
     * FULL Pattern A already, option-setting text and all, unlike the
     * possessive family's (whose suffix carries no option context at
     * all, since it is DEF_ALWAYS): `opt_prefix` is deliberately NOT
     * prepended here, or a `(?n)`-tagged row would double its own prefix
     * ("(?n)(?n)(a)"). */
    const char *sep = strstr(d->str, " \xe2\x89\xa1 ");
    if (!sep) {
        fprintf(stderr, "NOTE: %s: DEFK_BUILDER template '%s' has no "
                "' \xe2\x89\xa1 ' separator, skipping\n", r->syntax, d->str);
        n_deferred++;
        return;
    }
    (void)opt_prefix;
    char lhs[128], rhs[128], desc[192];
    size_t llen = (size_t)(sep - d->str);
    if (llen >= sizeof lhs) return;
    memcpy(lhs, d->str, llen);
    lhs[llen] = '\0';
    snprintf(rhs, sizeof rhs, "%s", sep + strlen(" \xe2\x89\xa1 "));

    for (size_t i = 0; i < N_BODIES; i++) {
        const char *body = BODIES[i];
        char a[256], b[256];
        subst_x(a, sizeof a, lhs, body);
        subst_x(b, sizeof b, rhs, body);
        snprintf(desc, sizeof desc, "%s (body=%s)", r->syntax, body);
        emit(a, b, "-", desc);
    }
}

/* [DD-11.3 follow-up] byte -> text, in a DIFFERENT escape family than the
 * construct under test (the ruling's own rule: `\cA` -> `\x01`, `\o{101}`
 * -> `\x41`, `\0`/`\012` -> `\x0a`, `\N{U+41}` -> `\x41`). `prefer_literal`
 * is true for exactly one row, bare `\x`, since a hex escape re-spelled as
 * a hex escape is no respelling at all; every other row falls back to
 * `\xHH` unconditionally, which IS a different family from `\c`/`\o{}`/
 * `\0`/`\N{U+}` regardless of the byte's own printability. */
static void respell(unsigned byte, bool prefer_literal, char *out, size_t outsz)
{
    /* byte > 0x20, not >=: a bare SPACE as the entire field's text broke
     * definitions_oracle_check.c's `sscanf` on the first real run of this
     * sweep (a scanf field-separator gotcha, not a Pattern-B content
     * question — a literal whitespace character in a scanf FORMAT STRING
     * matches any amount of whitespace, including none, in the input, so
     * the format's own literal '\t' between fields silently absorbed a
     * lone-space field and misaligned everything after it). `\x20`, the
     * fallback below, is unaffected — it is never bare whitespace on the
     * wire. */
    if (prefer_literal && byte > 0x20 && byte < 0x7f) {
        char c = (char)byte;
        if (strchr(".^$*+?()[]{}|\\", c))
            snprintf(out, outsz, "\\%c", c);
        else
            snprintf(out, outsz, "%c", c);
        return;
    }
    snprintf(out, outsz, "\\x%02x", byte);
}

/* Reads the single byte a DEFK_TEXTFN's AST answer represents. Every
 * shipped textfn calls `pcrec_ast_char` (definitions.c's own header names
 * it as the one constructor each textfn calls), which builds an A_CLASS
 * with exactly one bit set (case-folding never applies here — the seed
 * Ctx below is never caseless). -1 on any other shape: a harness defect
 * this function's own caller reports rather than silently accepting.
 * "The decoded value comes off the textfn's own output AST bitmap" (the
 * ruling's own words) is this function, read literally — never a second
 * hex/octal/xor decode written here alongside the real one. */
static int textfn_byte(const Ast *out)
{
    if (!out || out->k != A_CLASS) return -1;
    int found = -1, count = 0;
    for (unsigned c = 0; c < 256; c++)
        if (cls_has(out->u.cls.bits, c)) { found = (int)c; count++; }
    return count == 1 ? found : -1;
}

/* One DEFK_TEXTFN row, over its sampled operand set (or all 256 for bare
 * `\x`, `main`'s own caller). `real_fmt` is a printf template with ONE
 * `%s` for the operand, producing the row's own REAL SPELLING (`\cA`,
 * `\x41`, `\o{101}`, `\012`, `\N{U+0041}`). For a BUILT row (bare `\x`,
 * `\0`) the real spelling takes the ordinary Pattern-A slot, exactly like
 * every DEFK_STR cell above. For an UNBUILT row (`\c`, `\o{}`, `\N{U+`)
 * pcrec cannot compile the real spelling at all, so Pattern A becomes
 * Pattern B repeated (an always-equal tautology, never a REFUSED-A) and
 * the real spelling travels in the `oracle_a` column instead — see the
 * file header and `emit`'s own comment.
 *
 * `oracle_reachable` (r43-third-round follow-up, found live on the first
 * real run of this sweep — not anticipated by the ruling, flagged to
 * team-lead rather than silently decided): FALSE for exactly one row,
 * `\N{U+`. Its real spelling only PARSES under PCRE2's UTF mode ("\N{U+
 * dddd} is supported only in Unicode (UTF) mode", measured: libpcre2 err
 * 193 on `\N{U+0041}` at options=0), and this whole suite's oracle is
 * PINNED at options=0 (docs/pcre2_options.md's own standing constraint —
 * adopting any flag is a deliberate re-measurement event this follow-up
 * is not). So there is no way to ask libpcre2 about this row's real
 * spelling at all under this project's testing discipline, structurally
 * distinct from "pcrec hasn't shipped a producer yet" (`\c`/`\o{}`, whose
 * real spelling DOES compile under options=0, confirmed live: only their
 * DECODED BYTE disagreed, never their compilability). When false, the
 * oracle column stays `-` (a tautology, exactly the built-row shape) and
 * one NOTE explains why, rather than a silent, uninformative "pass".
 *
 * TRIGGER TO REVISIT (team-lead ruling, 2026-08-29): once [DD-12]/[M5]
 * (the UTF/encoding axis) lands, this row's probe can move to UTF mode
 * for the A==C leg specifically — that is the re-measurement event
 * docs/pcre2_options.md's options=0 pin exists to gate, not something to
 * do ahead of it. Until then this row stays the one exception. */
static void textfn_cells(const RegRow *r, const RegDef *d,
                          const char *real_fmt, bool prefer_literal,
                          const char *const *ops, size_t nops,
                          bool oracle_reachable)
{
    PcrecBuiltStatus bstat = pcrec_construct_built_status(r);
    bool built = (bstat != PCREC_BUILT_NO && bstat != PCREC_BUILT_DEFECT);

    if (!built && !oracle_reachable)
        fprintf(stderr, "NOTE: %s: unbuilt AND its real spelling cannot "
                "compile under this suite's options=0 oracle -- the "
                "A==C leg for this row is a tautology (oracle_a left as "
                "Pattern A), not a real libpcre2 comparison\n", r->syntax);

    for (size_t i = 0; i < nops; i++) {
        const char *op = ops[i];
        char real[64];
        snprintf(real, sizeof real, real_fmt, op);

        Ctx cx;
        pcrec_options defo;
        memset(&cx, 0, sizeof cx);
        pcrec_default_options(&defo);
        cx.pat = "";
        cx.patlen = 0;
        cx.opt = &defo;
        cx.job = calloc(1, sizeof(Job));
        if (!cx.job) { fprintf(stderr, "FAIL: out of memory\n"); exit(2); }
        cx.arena.cx = &cx;
        pcrec_parse_mods_init(&cx);

        Ast *out = d->textfn(op, strlen(op), &cx);
        int byte = textfn_byte(out);

        arena_free(&cx.arena);
        free(cx.job);

        if (byte < 0) {
            fprintf(stderr, "NOTE: %s: textfn('%s') did not return a "
                    "single-byte AST — skipping this operand\n",
                    r->syntax, op);
            n_deferred++;
            continue;
        }

        char b[16];
        respell((unsigned)byte, prefer_literal, b, sizeof b);

        char desc[192];
        snprintf(desc, sizeof desc, "%s (operand=%s, byte=0x%02x)",
                 r->syntax, op, (unsigned)byte);

        if (built)
            emit(real, b, "-", desc);
        else if (oracle_reachable)
            emit(b, b, real, desc);
        else
            emit(b, b, "-", desc);
    }
}

/* The 14-name POSIX class family, direct from each entry's own `operand`
 * field (registry.c's `posix_def[]`, r43-third-round) rather than through
 * `pcrec_def_resolve` — see the file header for why that walk can only
 * ever answer entry[0]. `[[:%s:]]` is this ONE row's own construct shape,
 * hand-written here rather than derived (no measured need to generalise a
 * one-user mechanism — D77). */
static void operand_cells(const RegRow *r)
{
    for (const RegDef *d = r->definitions; d->kind != DEFK_END; d++) {
        if (!d->operand) continue;
        if (d->kind != DEFK_STR) {
            fprintf(stderr, "NOTE: %s: operand '%s' on a non-DEFK_STR "
                    "entry — skipping (harness needs updating)\n",
                    r->syntax, d->operand);
            n_deferred++;
            continue;
        }
        char a[64], desc[192];
        snprintf(a, sizeof a, "[[:%s:]]", d->operand);
        snprintf(desc, sizeof desc, "%s (name=%s)", r->syntax, d->operand);
        emit(a, d->str, "-", desc);
    }
}

static void one_state(const RegRow *r, bool multiline, bool nocap)
{
    /* Reach the desired ParseMods state through the REAL PARSER, never by
     * poking `cx.mods` directly: `ParseMods` is INCOMPLETE outside
     * src/parse/ by design (D62/parse_mods.h — "no post-parse pass reads
     * cx->mods" is a compile error outside that directory, and this file
     * is outside it on purpose), so this TU cannot dereference it even if
     * it wanted to. A bare top-level `(?m)`/`(?n)` is never restored
     * (parse.c's own measured rule, cited throughout this table's design
     * note), so `cx.mods` still reads the state right after this parse
     * returns — which is MORE faithful to "through the real tag
     * evaluator" than hand-setting a field would have been, since the
     * option-setting mechanism itself (mod_modifiers.c) is exercised too. */
    /* volatile: read after a potential longjmp below (-Wclobbered,
     * src/core/compile.c's [SEL-1] precedent for the identical warning). */
    const char *volatile seed = multiline ? "(?m)a" : nocap ? "(?n)a" : "a";
    Ctx cx;
    pcrec_options defo;
    memset(&cx, 0, sizeof cx);
    pcrec_default_options(&defo);
    cx.pat = seed;
    cx.patlen = strlen(seed);
    cx.opt = &defo;
    cx.job = calloc(1, sizeof(Job));
    if (!cx.job) { fprintf(stderr, "FAIL: out of memory\n"); exit(2); }
    cx.arena.cx = &cx;

    if (setjmp(cx.jb) != 0) {
        fprintf(stderr, "FAIL: %s: seed pattern '%s' failed to parse "
                "(harness defect, not a real finding)\n", r->syntax, seed);
        arena_free(&cx.arena);
        free(cx.job);
        return;
    }
    pcrec_parse_mods_init(&cx);
    pcrec_parse_info(&cx, NULL);

    const RegDef *d = pcrec_def_resolve(&cx, r);
    const char *opt_prefix = multiline ? "(?m)" : nocap ? "(?n)" : "";

    if (!d) {
        fprintf(stderr, "NOTE: %s: pcrec_def_resolve returned NULL "
                "(should be unreachable)\n", r->syntax);
        n_deferred++;
    } else if (d->kind == DEFK_TEXTFN) {
        /* Unreachable since the r43-third-round follow-up: main()'s own
         * loop dispatches every DEFK_TEXTFN row to `textfn_cells` BEFORE
         * this function is ever called for one (a DEFK_TEXTFN row has no
         * multiline/nocap tag to select through `pcrec_def_resolve` in
         * the first place — its predicate axis is operand text, not
         * option scope, `\c`/`\o{}`/octal/`\N{U+}`'s own DEF_ALWAYS-only
         * lists). Kept as a defensive net, never a silent pass. */
        fprintf(stderr, "NOTE: %s: DEFK_TEXTFN reached one_state() -- "
                "should be unreachable, main() dispatches these to "
                "textfn_cells() first\n", r->syntax);
        n_deferred++;
    } else if (d->kind == DEFK_BUILDER) {
        builder_template_cell(r, d, opt_prefix);
    } else {
        /* DEFK_STR (including a resolved DEFK_ROW chain, which
         * pcrec_def_resolve already followed to its DEFK_STR/DEF_IDENTITY
         * leaf) or DEF_IDENTITY. */
        char a[256], b[256], desc[192];
        snprintf(a, sizeof a, "%s%s", opt_prefix, r->syntax);
        if (d->kind == DEFK_STR)
            snprintf(b, sizeof b, "%s", d->str);
        else
            snprintf(b, sizeof b, "%s", r->syntax); /* DEF_IDENTITY */
        snprintf(desc, sizeof desc, "%s (multiline=%d nocap=%d)",
                 r->syntax, (int)multiline, (int)nocap);
        emit(a, b, "-", desc);
    }

    arena_free(&cx.arena);
    free(cx.job);
}

int main(void)
{
    char featerr[128];
    if (pcrec_enabled_set_spec("all", featerr, sizeof featerr) != 0) {
        fprintf(stderr, "FAIL: could not install --features all: %s\n", featerr);
        return 2;
    }

    for (int k = 0; k < RK_COUNT; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry((RegKind)k, &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            if (!r->definitions) continue;

            PcrecBuiltStatus bstat = pcrec_construct_built_status(r);
            if (bstat == PCREC_BUILT_DEFECT) {
                fprintf(stderr, "NOTE: %s: pcrec_construct_built_status "
                        "reports DEFECT -- registry_check.c's own defect "
                        "assertion owns this, skipping here\n", r->syntax);
                n_deferred++;
                continue;
            }

            /* [DD-11.3 follow-up, r43-third-round] DEFK_TEXTFN rows
             * dispatch here, BEFORE the BUILT_NO skip below -- three of
             * the five (`\c`, `\o{}`, `\N{U+`) are genuinely unbuilt and
             * `textfn_cells` has its OWN accommodation for that (see the
             * file header and that function's own comment), so they must
             * not be filtered out by the same test that correctly removes
             * an unbuilt DEFK_STR row like `\R` below. Dispatched on the
             * row's own selector byte -- a small, closed, five-row set,
             * named individually rather than by `d->textfn`'s pointer
             * identity, since `\o{}` and `\0` SHARE one textfn
             * (`pcrec_def_text_octal`) but need different real-spelling
             * templates. */
            if (r->definitions[0].kind == DEFK_TEXTFN) {
                const RegDef *d0 = &r->definitions[0];
                switch (r->sel) {
                case 'c':
                    textfn_cells(r, d0, "\\c%s", false, CX_OPS, NOPS(CX_OPS),
                                 true);
                    break;
                case 'x': {
                    /* All 256 byte values, generated rather than listed
                     * (team-lead's own sample-set ruling for this row). */
                    static const char *ops[256];
                    static char bufs[256][4];
                    for (unsigned v = 0; v < 256; v++) {
                        snprintf(bufs[v], sizeof bufs[v], "%02X", v);
                        ops[v] = bufs[v];
                    }
                    textfn_cells(r, d0, "\\x%s", true, ops, 256, true);
                    break;
                }
                case 'o':
                    textfn_cells(r, d0, "\\o{%s}", false,
                                 OCTAL_BRACE_OPS, NOPS(OCTAL_BRACE_OPS), true);
                    break;
                case '0':
                    textfn_cells(r, d0, "\\%s", false,
                                 OCTAL_ZERO_OPS, NOPS(OCTAL_ZERO_OPS), true);
                    break;
                case 'N':
                    /* oracle_reachable = false: `\N{U+dddd}` only PARSES
                     * under PCRE2's UTF mode, and this suite's oracle is
                     * pinned at options=0 -- see textfn_cells' own
                     * comment. */
                    textfn_cells(r, d0, "\\N{U+%s}", false,
                                 UNICODE_OPS, NOPS(UNICODE_OPS), false);
                    break;
                default:
                    fprintf(stderr, "NOTE: %s: DEFK_TEXTFN row with "
                            "unrecognised selector '%c' -- textfn_cells "
                            "needs a case added for it\n",
                            r->syntax, r->sel);
                    n_deferred++;
                }
                continue;
            }

            /* An UNBUILT row (e.g. \R, module `misc`: a real registry row
             * with no producer yet, definitions_table.md's own "the table
             * may carry an unbuilt row's definition as data before any
             * producer exists" precedent) has no Pattern A to compile at
             * all -- `--features all` opens the gate but the port still
             * has nothing to say. Comparing against a construct that
             * cannot be shipped is vacuous, not a finding; skip and note.
             * D65's own derived classifier (`pcrec_construct_built_
             * status`) is the one true answer, never re-guessed from the
             * module name.
             *
             * PCREC_BUILT_NA (base-tier rows: `^`, the literal escapes,
             * the plain capturing group, ...) is NOT a reason to skip --
             * it means "the built/unbuilt question does not apply", not
             * "cannot compile"; base grammar is always available. Only a
             * real PCREC_BUILT_NO stops this cell existing. */
            if (bstat == PCREC_BUILT_NO) {
                fprintf(stderr, "NOTE: %s: row is `unbuilt` -- no shipped "
                        "Pattern A exists to compare against, skipping\n",
                        r->syntax);
                n_deferred++;
                continue;
            }

            /* [DD-11.3 follow-up, r43-third-round] the 14-name POSIX
             * class-name family, detected by an entry carrying `operand`
             * (registry.c's `posix_def[]`), dispatches to `operand_cells`
             * instead of the option-matrix `one_state` path below -- see
             * the file header for why `pcrec_def_resolve` cannot select a
             * NAMED entry at all. */
            bool has_operand = false;
            for (const RegDef *d = r->definitions; d->kind != DEFK_END; d++)
                if (d->operand) { has_operand = true; break; }
            if (has_operand) {
                operand_cells(r);
                continue;
            }

            bool has_ml = false, has_nc = false;
            for (const RegDef *d = r->definitions; d->kind != DEFK_END; d++) {
                if (d->tag == DEF_MULTILINE) has_ml = true;
                if (d->tag == DEF_NOCAP) has_nc = true;
            }

            if (has_ml) {
                one_state(r, false, false);
                one_state(r, true, false);
            } else if (has_nc) {
                one_state(r, false, false);
                one_state(r, false, true);
            } else {
                one_state(r, false, false);
            }
        }
    }

    fprintf(stderr, "definitions_oracle_gen: %d cells, %d deferred\n",
            n_cells, n_deferred);
    return 0;
}
