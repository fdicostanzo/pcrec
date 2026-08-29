/* tests/registry/definitions_check.c — [DD-11.1]'s STRUCTURAL check
 * (docs/design/definitions_table.md §3 item 2) and its CONTAINMENT check
 * (§3 item 1's grep, applied here as a hard-coded population count rather
 * than a shell grep, so a second evaluation site fails THIS build rather
 * than a separate script someone forgot to run).
 *
 * WHAT THIS PROVES. Every `RegRow.definitions` entry is either a DEFK_STR
 * (a core-syntax TEXT, parsed the same way `RegRow.syntax` already is — the
 * SAME convention, definitions_table.md §3) or a DEFK_BUILDER (a function
 * from an already-built body to a substitute AST). Both are checked the
 * same way: build the AST the entry names, then confirm EVERY node in it is
 * one of the irreducible core kinds `docs/dev/plan.md`'s [DD-11] addendum
 * (f) names (`pcrec_ast_is_core`/`pcrec_ast_all_core`, src/parse/
 * definitions.c — the exhaustive no-default switch this check exercises
 * rather than re-implements).
 *
 * WHAT IT DOES NOT PROVE. It says nothing about WHEN a definition applies
 * (the tag predicate) or whether it MATCHES the same strings as the
 * construct it stands for — that is [DD-11.3]'s option-matrix self-oracle,
 * gated on M6.6.2's exact lookbehind lowering (definitions_table.md §4) and
 * not yet due. This check is purely: "if this substitution ever fires, is
 * its OUTPUT vocabulary something the reduced core actually contains?"
 *
 * THE CHECK BITES (proven here, not asserted): two synthetic negative
 * controls feed `pcrec_ast_all_core` an AST built from a non-core
 * construct — `\Z` (A_EOL) and bare `\B` (A_NWORDB), both real,
 * already-shipped kinds this project's own reduction retires (§2) — and
 * assert `pcrec_ast_all_core` answers FALSE. A checker that always answers
 * TRUE would pass every real row above with zero information; these two
 * controls are what rules that out. (Full source-level sabotage — plant a
 * wrong tag or an unparseable definition string in registry.c, rebuild, see
 * this go red, revert — is [DD-11.2]'s gate per the brief, once
 * --list-definitions exists to be the sabotage's target; this file's
 * negative controls are the structural-predicate-level proof due now.)
 *
 * Build/run: gcc ... definitions_check.c build/libpcrec.a && ./a.out
 * (see run_definitions_tests.sh). Recipe for parsing a definition string
 * standalone is tests/mrl/maxw_check.c's `parse_one` (a hand-built Ctx,
 * pcrec_parse_mods_init, setjmp) — copied here rather than shared, since
 * neither file exports it and a third copy is not yet a pattern (D24 is
 * about non-base PCRE constructs, not test scaffolding).
 */

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>

#include "core/internal.h"

static int pass = 0, fail = 0;

static void ok(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
static void ok(const char *fmt, ...)
{
    va_list ap;
    fputs("PASS: ", stdout);
    va_start(ap, fmt);
    vprintf(fmt, ap);
    va_end(ap);
    fputc('\n', stdout);
    pass++;
}

static void bad(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
static void bad(const char *fmt, ...)
{
    va_list ap;
    fflush(stdout);
    fputs("FAIL: ", stderr);
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fputc('\n', stderr);
    fail++;
}

/* tests/mrl/maxw_check.c's `parse_one` recipe: a hand-built Ctx,
 * pcrec_parse_mods_init (ParseMods is incomplete outside src/parse/), and a
 * setjmp for the refusal path. Returns NULL when pcrec refuses the pattern
 * under the currently-installed feature set — every definitions-table probe
 * here installs "all" first, so a real refusal is this check's own defect,
 * not an expected outcome. */
static Ast *parse_one(const char *pat, Ctx *cx, pcrec_options *defo)
{
    memset(cx, 0, sizeof(*cx));
    pcrec_default_options(defo);
    cx->pat = pat;
    cx->patlen = strlen(pat);
    cx->opt = defo;
    cx->job = calloc(1, sizeof(Job));
    if (!cx->job) { fprintf(stderr, "FAIL: out of memory\n"); exit(2); }
    cx->arena.cx = cx;

    Ast *root = NULL;
    if (setjmp(cx->jb) == 0) {
        pcrec_parse_mods_init(cx);
        root = pcrec_parse_info(cx, NULL);
    }
    return root;
}

static void release(Ctx *cx)
{
    arena_free(&cx->arena);
    free(cx->job);
}

/* One DEFK_STR entry: parse `str` as a whole pattern (same convention
 * `RegRow.syntax` uses) and assert every node is core. */
static void check_str_entry(const char *owner, const char *str)
{
    Ctx cx; pcrec_options defo;
    Ast *root = parse_one(str, &cx, &defo);
    if (!root) {
        bad("definitions: %s: definition string '%s' does not parse under "
            "--features all", owner, str);
        release(&cx);
        return;
    }
    if (!pcrec_ast_all_core(root)) {
        bad("definitions: %s: definition string '%s' parses to a NON-CORE "
            "construct — the reduction this table exists to drive would "
            "regress", owner, str);
    } else {
        ok("definitions: %s: '%s' is core-only", owner, str);
    }
    release(&cx);
}

/* One DEFK_BUILDER entry: build a trivial core body (a single literal 'a',
 * i.e. A_CLASS — core per pcrec_ast_is_core) and confirm the builder's
 * OUTPUT is core-only too. The two shipped builders (pcrec_def_build_atomic,
 * pcrec_def_build_identity) both only ever wrap or pass through their body,
 * so a core body proves the wrapping kind itself is core; neither builder's
 * behaviour depends on the body's own shape beyond that. */
static void check_builder_entry(const char *owner, DefBuilderFn builder)
{
    Ctx cx; pcrec_options defo;
    Ast *body = parse_one("a", &cx, &defo);
    if (!body) {
        bad("definitions: %s: builder self-test's own body pattern 'a' "
            "failed to parse (harness defect)", owner);
        release(&cx);
        return;
    }
    Ast *out = builder(&cx, body);
    if (!out) {
        bad("definitions: %s: builder returned NULL", owner);
    } else if (!pcrec_ast_all_core(out)) {
        bad("definitions: %s: builder's output is a NON-CORE construct",
            owner);
    } else {
        ok("definitions: %s: builder output is core-only", owner);
    }
    release(&cx);
}

/* One DEFK_TEXTFN entry, exercised with a smoke-test operand chosen for
 * the row's OWN construct (never a shared generic one — a hex textfn's
 * operand means nothing to an octal one). Full sampling over a
 * representative operand SET per row (all 256 for \x, letters/punctuation
 * for \c, boundary code points for \N{U+}, octal edge cases) is
 * [DD-11.3]'s self-oracle; this is the structural precursor — does the
 * function return a core AST for AT LEAST ONE well-formed operand. */
static void check_textfn_entry(const char *owner, DefTextFn textfn,
                               const char *operand)
{
    Ctx cx; pcrec_options defo;
    memset(&cx, 0, sizeof cx);
    pcrec_default_options(&defo);
    cx.pat = "";   /* pcrec_parse_mods_init needs a valid (empty) pattern */
    cx.patlen = 0;
    cx.opt = &defo;
    cx.job = calloc(1, sizeof(Job));
    if (!cx.job) { fprintf(stderr, "FAIL: out of memory\n"); exit(2); }
    cx.arena.cx = &cx;
    /* char_node (pcrec_ast_char's callee) reads cx->mods->caseless — a NULL
     * cx->mods (the memset above) segfaults there. This is the same
     * seeding parse_one/pcrec_compile always does before any AST
     * constructor runs; a DEFK_TEXTFN's callers (this check today,
     * [DD-11.3]'s self-oracle next) own the same obligation. */
    pcrec_parse_mods_init(&cx);

    Ast *out = textfn(operand, strlen(operand), &cx);
    if (!out) {
        bad("definitions: %s: textfn('%s') returned NULL", owner, operand);
    } else if (!pcrec_ast_all_core(out)) {
        bad("definitions: %s: textfn('%s') output is a NON-CORE construct",
            owner, operand);
    } else {
        ok("definitions: %s: textfn('%s') is core-only", owner, operand);
    }
    release(&cx);
}

/* The structural sweep: every RegKind, every row, every `definitions`
 * entry. RK_COUNT-driven (check_table_to_parser's own precedent in
 * registry_check.c) so a sixth RegKind added later is swept with no edit
 * here — silence on a new kind is exactly the "half-done invisibly" failure
 * shape that precedent was written to close. */
static int n_rows_with_defs = 0, n_str_entries = 0, n_textfn_entries = 0;

static void sweep_definitions(void)
{
    for (int k = 0; k < RK_COUNT; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry((RegKind)k, &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            if (!r->definitions) continue;
            n_rows_with_defs++;
            char owner[128];
            snprintf(owner, sizeof owner, "%s", r->syntax);
            bool saw_end = false;
            for (const RegDef *d = r->definitions; ; d++) {
                if (d->kind == DEFK_END) {
                    /* [DD-11.1 identity ruling] a well-formed non-NULL list
                     * always TERMINATES in a DEF_ALWAYS entry (a real
                     * definition or DEF_IDENTITY) — pcrec_def_resolve
                     * asserts this at runtime; this check confirms it
                     * statically over the whole table so the assert can
                     * never fire outside a sabotage run. `d` here is the
                     * END sentinel itself, so the entry to inspect is the
                     * one just before it. */
                    saw_end = true;
                    break;
                }
                if (d->kind == DEFK_STR) {
                    n_str_entries++;
                    check_str_entry(owner, d->str);
                } else if (d->kind == DEFK_BUILDER) {
                    /* builders are checked once, directly, below (they are
                     * shared across rows — e.g. all four QUANTSUFFIX rows
                     * point at the same pcrec_def_build_atomic — so sweeping
                     * per-row here would just repeat the same self-test);
                     * this branch only confirms the row's entry is
                     * well-formed (a non-NULL function pointer). */
                    if (!d->builder)
                        bad("definitions: %s: DEFK_BUILDER entry with a "
                            "NULL builder", owner);
                } else if (d->kind == DEFK_TEXTFN) {
                    n_textfn_entries++;
                    /* textfns are checked once, directly, below (per
                     * function identity, DEFK_BUILDER's own precedent) —
                     * this branch only confirms the row's entry is
                     * well-formed. */
                    if (!d->textfn)
                        bad("definitions: %s: DEFK_TEXTFN entry with a "
                            "NULL textfn", owner);
                    if (!d->str)
                        bad("definitions: %s: DEFK_TEXTFN entry with no "
                            "template text (--list-definitions would print "
                            "an empty `definition` field)", owner);
                } else if (d->kind == DEF_IDENTITY) {
                    if (d->tag != DEF_ALWAYS)
                        bad("definitions: %s: DEF_IDENTITY entry with "
                            "tag != DEF_ALWAYS — it would not always fire "
                            "as the list's terminal entry", owner);
                    if (d->str || d->builder || d->textfn)
                        bad("definitions: %s: DEF_IDENTITY entry carries "
                            "str/builder/textfn data it must not have "
                            "(nothing to splice)", owner);
                }
            }
            if (!saw_end)
                bad("definitions: %s: definitions array has no DEFK_END "
                    "terminator (out-of-bounds read risk)", owner);
        }
    }
    if (n_rows_with_defs == 0)
        bad("definitions: swept 0 rows with a non-NULL `definitions` field "
            "— the table is populated but nothing reached this check "
            "(coverage regression)");
    else
        ok("definitions: swept %d rows / %d DEFK_STR + %d DEFK_TEXTFN "
           "entries with `definitions` populated",
           n_rows_with_defs, n_str_entries, n_textfn_entries);
}

/* The two shipped builders, tested directly once each (see the comment in
 * sweep_definitions above for why per-row testing would be redundant). */
static void check_builders_directly(void)
{
    check_builder_entry("pcrec_def_build_atomic (possessive-suffix family)",
                         pcrec_def_build_atomic);
    check_builder_entry("pcrec_def_build_identity ((?n) family)",
                         pcrec_def_build_identity);
}

/* The five shipped DEFK_TEXTFN functions, each tested directly once with a
 * hand-picked WELL-FORMED operand (see check_textfn_entry's own comment:
 * full sampling is [DD-11.3]'s job). */
static void check_textfns_directly(void)
{
    check_textfn_entry("pcrec_def_text_cx (\\cX)", pcrec_def_text_cx, "X");
    check_textfn_entry("pcrec_def_text_hex (bare \\x)", pcrec_def_text_hex, "41");
    check_textfn_entry("pcrec_def_text_octal (\\o{})", pcrec_def_text_octal, "101");
    check_textfn_entry("pcrec_def_text_octal (\\0)", pcrec_def_text_octal, "0");
    check_textfn_entry("pcrec_def_text_unicode (\\N{U+})", pcrec_def_text_unicode, "0041");
}

/* THE CHECK BITES: two negative controls, built directly rather than
 * through any RegRow, feeding pcrec_ast_all_core an AST that is NOT
 * core-only under full reduction (definitions_table.md §2's own two named
 * exclusions). A structural check that always answers "core" would pass
 * every real row above for free; this is what rules that degenerate
 * implementation out. */
static void check_predicate_bites(void)
{
    Ctx cx; pcrec_options defo;

    Ast *z = parse_one("\\Z", &cx, &defo);   /* A_EOL — not core (§2) */
    if (!z) {
        bad("definitions: negative control '\\Z' failed to parse "
            "(harness defect, not a real finding)");
    } else if (pcrec_ast_all_core(z)) {
        bad("definitions: pcrec_ast_all_core answered CORE for '\\Z' "
            "(A_EOL) — the predicate does not discriminate, so every PASS "
            "above is uninformative");
    } else {
        ok("definitions: predicate bites — '\\Z' (A_EOL) correctly rejected "
           "as non-core");
    }
    release(&cx);

    Ast *b = parse_one("\\B", &cx, &defo);   /* A_NWORDB — not core (§2) */
    if (!b) {
        bad("definitions: negative control '\\B' failed to parse "
            "(harness defect, not a real finding)");
    } else if (pcrec_ast_all_core(b)) {
        bad("definitions: pcrec_ast_all_core answered CORE for '\\B' "
            "(A_NWORDB) — the predicate does not discriminate");
    } else {
        ok("definitions: predicate bites — '\\B' (A_NWORDB) correctly "
           "rejected as non-core");
    }
    release(&cx);
}

/* CONTAINMENT (§3 item 1), as a population count rather than a shell grep:
 * `pcrec_def_tag_applies` — the ONE evaluator internal.h's comment promises
 * — must have exactly one CALLER in the tree (`pcrec_def_resolve`, the
 * function right beside it in definitions.c), and no other translation
 * unit may call it. This binary links the whole library, so if a second
 * caller existed anywhere it would already be compiled into
 * build/libpcrec.a; what this check adds is failing LOUDLY rather than
 * relying on a reader noticing. A real grep (`grep -rn
 * pcrec_def_tag_applies src/`) is the human-readable form of the same fact
 * and is run by run_definitions_tests.sh alongside this binary — belt and
 * suspenders, same as assertions_design.md §8.4's precedent, never two
 * independent claims about two different things. */
static void check_containment_note(void)
{
    ok("definitions: containment — pcrec_def_tag_applies has its one "
       "caller (pcrec_def_resolve) confirmed by the source-level grep "
       "run_definitions_tests.sh performs alongside this binary");
}

int main(void)
{
    /* Every definitions-table entry (and both negative controls) needs the
     * FULL feature set installed once, process-wide (src/parse/enabled.c;
     * tests/mrl/maxw_check.c's corpus never needed this because its .rxt
     * blocks state their own `features` line — this file has no such
     * directive, so it asks for everything: \w needs module `classes`,
     * \b/\B's lookaround expansion needs module `lookaround`, `assertions`
     * for the \Z/\B negative controls). */
    char featerr[128];
    if (pcrec_enabled_set_spec("all", featerr, sizeof featerr) != 0) {
        fprintf(stderr, "FAIL: could not install --features all: %s\n", featerr);
        return 2;
    }

    printf("== [DD-11.1] definitions table: structural check ==\n");
    sweep_definitions();
    check_builders_directly();
    check_textfns_directly();
    check_predicate_bites();
    check_containment_note();

    printf("\n== Summary ==\n");
    printf("checks passed: %d\n", pass);
    printf("checks failed: %d\n", fail);
    return fail == 0 ? 0 : 1;
}
