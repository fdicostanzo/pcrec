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
 * SCOPE: `DEFK_TEXTFN` rows (`\c`, `\o{}`, octal/`\0`, `\N{U+}`, bare `\x`)
 * are DEFERRED — noted to stderr, not emitted as cells. Their definition
 * has no splice-ready pattern text at all (only a human template plus a
 * function from OPERAND TEXT to an AST), and rendering a Pattern B for
 * them needs byte-valued AST introspection (read the textfn's own output
 * bitmap back as a literal `\xHH`) that is a distinct enough sub-problem
 * from the option-matrix work this pass covers to be its own follow-on.
 *
 * SCOPE, second: UNBUILT rows (`\R`, module `misc` -- a real row with no
 * producer yet) are likewise skipped and noted: `pcrec_construct_built_
 * status` (D65) says so, never a hand-guessed module-name list, and there
 * is no shipped Pattern A to compile for one regardless of `--features`.
 *
 * SCOPE, third: the 14-name POSIX class-name family shares ONE row
 * (`[[:alpha:]]`'s row carries all 14 as separate DEF_ALWAYS entries,
 * selected by which NAME LITERAL appears in the probe text, never by
 * option state). `pcrec_def_resolve`'s first-applicable-wins walk over an
 * all-DEF_ALWAYS list always returns entry 1 ("alpha") — correct
 * behaviour for the OPTION-MATRIX question this pass asks, but it means
 * only that one entry becomes a cell here. The other 13 are not an
 * option-matrix question at all (no `(?m)`/`(?n)` scoping touches a POSIX
 * name), and they are already covered elsewhere: structurally, by every
 * entry, in tests/registry/definitions_check.c's sweep
 * (`check_str_entry` runs on all 14, index-blind); and BEHAVIOURALLY
 * against libpcre2, by PC-4's own "28 posix spellings x 6 shapes"
 * differential (tests/registry/pc4_check.c) — this pass adding a second,
 * name-keyed axis here would need the SAME 14-name list PC-4 already
 * carries, a second home for a fact this table does not itself store
 * (no per-entry name field). Left alone rather than duplicated. */

#include <setjmp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

/* [DD-11.3]'s manager-specified body set for a DEFK_BUILDER template's `X`
 * placeholder. */
static const char *const BODIES[] = { "a", "(a)", "[ab]", "a|b", "\\d+" };
#define N_BODIES (sizeof BODIES / sizeof BODIES[0])

static int n_cells = 0, n_deferred = 0;

static void emit(const char *a, const char *b, const char *desc)
{
    printf("%d\t%s\t%s\t%s\n", n_cells, a, b, desc);
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
        emit(a, b, desc);
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
        emit(a, b, desc);
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
        fprintf(stderr, "NOTE: %s: DEFK_TEXTFN deferred (see file header)\n",
                r->syntax);
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
        emit(a, b, desc);
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

            /* An UNBUILT row (e.g. \R, module `misc`: a real registry row
             * with no producer yet, definitions_table.md's own "the table
             * may carry an unbuilt row's definition as data before any
             * producer exists" precedent) has no Pattern A to compile at
             * all -- `--features all` opens the gate but the port still
             * has nothing to say. Comparing against a construct that
             * cannot be shipped is vacuous, not a finding; skip and note,
             * DEFK_TEXTFN's own precedent. D65's own derived classifier
             * (`pcrec_construct_built_status`) is the one true answer,
             * never re-guessed from the module name.
             *
             * PCREC_BUILT_NA (base-tier rows: `^`, the literal escapes,
             * the plain capturing group, ...) is NOT a reason to skip --
             * it means "the built/unbuilt question does not apply", not
             * "cannot compile"; base grammar is always available. Only a
             * real PCREC_BUILT_NO stops this cell existing. */
            PcrecBuiltStatus bstat = pcrec_construct_built_status(r);
            if (bstat == PCREC_BUILT_NO) {
                fprintf(stderr, "NOTE: %s: row is `unbuilt` -- no shipped "
                        "Pattern A exists to compare against, skipping\n",
                        r->syntax);
                n_deferred++;
                continue;
            }
            if (bstat == PCREC_BUILT_DEFECT) {
                fprintf(stderr, "NOTE: %s: pcrec_construct_built_status "
                        "reports DEFECT -- registry_check.c's own defect "
                        "assertion owns this, skipping here\n", r->syntax);
                n_deferred++;
                continue;
            }

            /* The 14-name POSIX class-name family shares ONE row whose
             * `syntax` is a FIXED example ("[[:alpha:]]") that does NOT
             * correspond to entry[0] -- `pcrec_def_resolve`'s first-
             * applicable-wins walk over an all-DEF_ALWAYS list returns
             * entry[0] regardless of what the row's own printed example
             * says, and entry[0] here is "alnum", not "alpha" (the
             * array's own declared order, registry.c's `posix_def[]`).
             * Pairing `r->syntax` with `pcrec_def_resolve`'s answer would
             * therefore compare TWO DIFFERENT CONSTRUCTS (alpha vs
             * alnum) and call the mismatch a finding -- caught exactly
             * this way on the first run of this generator. Detected
             * generically (more than one DEF_ALWAYS entry on one row,
             * the shape no other row in the table has) rather than by
             * naming this row specifically, and skipped for the same
             * reason the file header already excludes the other 13
             * names: no per-entry name field exists to construct a
             * correct Pattern A from, and this family is covered
             * elsewhere (structurally: definitions_check.c; behaviourally
             * against libpcre2: PC-4's own POSIX sweep). */
            int n_always = 0;
            for (const RegDef *d = r->definitions; d->kind != DEFK_END; d++)
                if (d->tag == DEF_ALWAYS) n_always++;
            if (n_always > 1) {
                fprintf(stderr, "NOTE: %s: %d DEF_ALWAYS entries on one row "
                        "(a finite-name family sharing a fixed `syntax` "
                        "example, POSIX's own shape) -- skipping, see file "
                        "header\n", r->syntax, n_always);
                n_deferred++;
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
