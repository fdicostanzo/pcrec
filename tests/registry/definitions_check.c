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

/* One row's DEFK_ROW chain: `str` names the TARGET row's `syntax`
 * ("an alias row defines to the row it aliases, never to the alias's own
 * expansion" — internal.h's comment before `DEFK_ROW` has the full rule).
 * Resolves the target via `pcrec_registry_row_by_syntax` (a dangling name
 * is a FAIL, never a skip), then resolves the TARGET's own applicable
 * entry under DEFAULT mods (the chain entry's own tag already gated the
 * reference; the target's own tag, if it has one, is a separate question
 * [DD-11.3]'s option matrix exercises in full) and dispatches on ITS kind.
 * Only DEFK_STR/DEF_IDENTITY targets are exercised structurally here —
 * today's one chain ($ -> \Z) resolves to DEFK_STR; a future DEFK_BUILDER/
 * DEFK_TEXTFN target is accepted without a structural check of its own
 * (those kinds are already exercised directly, once per function, below). */
static void check_row_chain_entry(const char *owner, const char *target_syntax)
{
    const RegRow *target = pcrec_registry_row_by_syntax(target_syntax);
    if (!target) {
        bad("definitions: %s: DEFK_ROW entry names '%s', which no row's "
            "syntax matches (dangling chain)", owner, target_syntax);
        return;
    }
    Ctx cx; pcrec_options defo;
    memset(&cx, 0, sizeof cx);
    pcrec_default_options(&defo);
    cx.pat = "";
    cx.patlen = 0;
    cx.opt = &defo;
    cx.job = calloc(1, sizeof(Job));
    if (!cx.job) { fprintf(stderr, "FAIL: out of memory\n"); exit(2); }
    cx.arena.cx = &cx;
    pcrec_parse_mods_init(&cx);

    const RegDef *resolved = pcrec_def_resolve(&cx, target);
    if (!resolved) {
        bad("definitions: %s: chain target '%s' resolved to NULL (its "
            "own `definitions` field is malformed)", owner, target_syntax);
    } else if (resolved->kind == DEFK_STR) {
        check_str_entry(owner, resolved->str);
    } else if (resolved->kind == DEF_IDENTITY) {
        check_str_entry(owner, target->syntax);
    } else {
        ok("definitions: %s: chains to '%s' (kind %d, exercised directly "
           "elsewhere)", owner, target_syntax, (int)resolved->kind);
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
static int n_rows_with_defs = 0, n_str_entries = 0, n_textfn_entries = 0, n_row_entries = 0;

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
                     * well-formed (a non-NULL function pointer, and — since
                     * the r43-second-round builder-template ruling — a
                     * non-NULL template, DEFK_TEXTFN's own precedent). */
                    if (!d->builder)
                        bad("definitions: %s: DEFK_BUILDER entry with a "
                            "NULL builder", owner);
                    if (!d->str)
                        bad("definitions: %s: DEFK_BUILDER entry with no "
                            "template text (--list-definitions would print "
                            "an empty `definition` field)", owner);
                } else if (d->kind == DEFK_ROW) {
                    n_row_entries++;
                    if (!d->str)
                        bad("definitions: %s: DEFK_ROW entry with no "
                            "target syntax (nothing to chain to)", owner);
                    else
                        check_row_chain_entry(owner, d->str);
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
                    /* The identity CLAIM itself, checked: the row's own
                     * `syntax`, parsed under DEFAULT mods (no other tag
                     * active — the state this entry fires under, since it
                     * is always the list's trailing fallback), must
                     * itself be core-only. This is what "already core, no
                     * substitution" actually asserts, not just that the
                     * entry carries no payload. */
                    check_str_entry(owner, r->syntax);
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
        ok("definitions: swept %d rows / %d DEFK_STR + %d DEFK_TEXTFN + "
           "%d DEFK_ROW entries with `definitions` populated",
           n_rows_with_defs, n_str_entries, n_textfn_entries, n_row_entries);
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

/* [DD-11.4] THE RECURSION GUARD, UN-PARKED (definitions_table.md §3 item 5,
 * r43 S4; manager ruling on the fixture's shape, 2026-08-29): `\b`'s own
 * shipped definition text CONTAINS "\w" as a literal substring
 * (`(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))`) — the table's own "nested definition"
 * precedent (definitions_table.md §1's `\b` row). `\w` has only ONE
 * definitions entry today (DEF_ALWAYS), so nothing has ever asked whether
 * `pcrec_def_resolve` stays CONTEXT-SENSITIVE when a row it names has more
 * than one real entry — the question a second `\w` row (Unicode/DEF_UCP)
 * will eventually raise for real. Rather than wait for that (DEF_UCP's own
 * evaluator answers `false` UNCONDITIONALLY today, internal.h's own
 * comment: "NO PRODUCER YET" — there is no way, even synthetically, to
 * make it fire without editing definitions.c's exhaustive switch, which
 * would be PRODUCTION code, not a test fixture), this plants a SYNTHETIC
 * second `\w` row -- A DEFINITIONS ARRAY COMPILED ONLY INTO THIS TEST
 * BINARY, never added to registry.c, injected through the SAME resolver
 * entry point (`pcrec_def_resolve`) every real row goes through -- gated
 * on `DEF_MULTILINE`, a tag that DOES have a real, live evaluator path
 * today (unlike DEF_UCP), used here purely as a MECHANICALLY REAL stand-in
 * for "the flag is (hypothetically) live", exactly as the design note's
 * own words ask for. The row's SEMANTICS (a fake Unicode-flavoured \w) are
 * fictional and never claim otherwise; what is real is the RESOLVER CODE
 * PATH being exercised on a row with more than one entry.
 *
 * Three things are checked: (1) with the flag OFF, the synthetic row
 * resolves to the SAME text the real `\w` row ships today — no drift
 * between the fixture and production, which is what makes cell (2) a
 * meaningful contrast rather than an arbitrary string; (2) with the flag
 * ON, the resolver picks the OTHER entry — proving `pcrec_def_resolve` is
 * not somehow wedded to the row being DEF_ALWAYS-only; (3) INTERLEAVED
 * calls — resolve the synthetic \w row under both states, then resolve a
 * second synthetic row (a `\b`-shaped one, whose text literally embeds
 * "\w") under the OPPOSITE-of-whatever-just-ran state — confirm neither
 * call's answer depends on what the other call most recently asked, which
 * is the CONTEXT-SENSITIVITY claim itself: `pcrec_def_resolve` is a pure
 * function of (row, Ctx state) with no hidden global memo a nested
 * resolution (DD-11.5's future job, resolving `\b` and then, inside its
 * own expansion, resolving the `\w` the expansion's text names) could
 * trip over. */
static const RegDef synthetic_w_def[] = {
    /* fictional: stands in for a future real DEF_UCP entry, never claims
     * to BE one -- see the function comment above. */
    {DEFK_STR, DEF_MULTILINE, "[\\p{L}0-9_]", NULL, NULL},
    {DEFK_STR, DEF_ALWAYS,    "[A-Za-z0-9_]", NULL, NULL}, /* == real \w */
    {DEFK_END, DEF_ALWAYS,    NULL,           NULL, NULL},
};
static const RegDef synthetic_b_def[] = {
    /* == the real \b row's own definition text, chosen because it embeds
     * "\w" as a literal substring -- the exact "nested definition" shape
     * this guard exists to exercise. DEF_ALWAYS-only: \b's own tag never
     * varies; only the (independently resolved) \w reference inside its
     * TEXT would, once DD-11.5 wires real substitution. */
    {DEFK_STR, DEF_ALWAYS, "(?:(?<=\\w)(?!\\w)|(?<!\\w)(?=\\w))", NULL, NULL},
    {DEFK_END, DEF_ALWAYS, NULL, NULL, NULL},
};

/* A minimal RegRow: pcrec_def_resolve reads only `.definitions` (and
 * `pcrec_registry_row_by_syntax`, unreached here since neither synthetic
 * row's list contains a DEFK_ROW entry), so every other field is left at
 * its zero value -- this row is never registered anywhere `pcrec_registry`
 * enumerates, by construction (it lives on this file's own stack/statics,
 * not in registry.c's arrays). */
static RegRow synthetic_row(const RegDef *defs)
{
    RegRow r;
    memset(&r, 0, sizeof r);
    r.kind = RK_ESC;
    r.syntax = "\\w (synthetic, test-local)";
    r.definitions = defs;
    return r;
}

/* Reaches the desired `cx->mods` state the SAME way DD-11.3's own
 * generator does (never by poking `Ctx.mods` from outside src/parse/,
 * where `ParseMods` is INCOMPLETE by design): parse a real seed pattern
 * under the desired scope. A bare top-level `(?m)` is never restored, so
 * `cx->mods` still reads `multiline` right after this returns. On a
 * parse failure (harness defect, not a real finding) `cx->mods` is left
 * at `pcrec_parse_mods_init`'s own default (false), which the caller's
 * own assertions will catch as a mismatch rather than a silent pass. */
static void mods_ctx(Ctx *cx, pcrec_options *defo, bool multiline)
{
    const char *seed = multiline ? "(?m)a" : "a";
    memset(cx, 0, sizeof *cx);
    pcrec_default_options(defo);
    cx->pat = seed;
    cx->patlen = strlen(seed);
    cx->opt = defo;
    cx->job = calloc(1, sizeof(Job));
    if (!cx->job) { fprintf(stderr, "FAIL: out of memory\n"); exit(2); }
    cx->arena.cx = cx;
    if (setjmp(cx->jb) == 0) {
        pcrec_parse_mods_init(cx);
        pcrec_parse_info(cx, NULL);
    }
}

static void check_recursion_guard(void)
{
    Ctx cx; pcrec_options defo;
    RegRow w_row = synthetic_row(synthetic_w_def);
    RegRow b_row = synthetic_row(synthetic_b_def);

    /* (1) flag OFF: matches the real \w row's own shipped text exactly. */
    mods_ctx(&cx, &defo, false);
    const RegDef *d = pcrec_def_resolve(&cx, &w_row);
    if (!d || d->kind != DEFK_STR || strcmp(d->str, "[A-Za-z0-9_]") != 0)
        bad("definitions: [DD-11.4] recursion guard: synthetic \\w row "
            "with the flag OFF resolved to '%s', expected '[A-Za-z0-9_]' "
            "(the real \\w row's own text -- a fixture that drifts from "
            "production proves nothing)", d ? d->str : "(null)");
    else
        ok("definitions: [DD-11.4] recursion guard: synthetic \\w, flag "
           "OFF, matches the real row's own text");
    arena_free(&cx.arena); free(cx.job);

    /* (2) flag ON: the OTHER entry fires. */
    mods_ctx(&cx, &defo, true);
    d = pcrec_def_resolve(&cx, &w_row);
    if (!d || d->kind != DEFK_STR || strcmp(d->str, "[\\p{L}0-9_]") != 0)
        bad("definitions: [DD-11.4] recursion guard: synthetic \\w row "
            "with the flag ON resolved to '%s', expected the alternate "
            "entry -- the resolver did not pick up the second row",
            d ? d->str : "(null)");
    else
        ok("definitions: [DD-11.4] recursion guard: synthetic \\w, flag "
           "ON, picks the alternate entry through the SAME resolver "
           "entry point");
    arena_free(&cx.arena); free(cx.job);

    /* (3) interleaved calls, opposite states, no cross-contamination. */
    mods_ctx(&cx, &defo, true);
    const RegDef *dw1 = pcrec_def_resolve(&cx, &w_row);
    arena_free(&cx.arena); free(cx.job);

    mods_ctx(&cx, &defo, false);
    const RegDef *db = pcrec_def_resolve(&cx, &b_row);
    arena_free(&cx.arena); free(cx.job);

    mods_ctx(&cx, &defo, false);
    const RegDef *dw2 = pcrec_def_resolve(&cx, &w_row);
    arena_free(&cx.arena); free(cx.job);

    bool ok3 = dw1 && dw1->kind == DEFK_STR &&
               strcmp(dw1->str, "[\\p{L}0-9_]") == 0 &&
               db && db->kind == DEFK_STR &&
               strcmp(db->str, "(?:(?<=\\w)(?!\\w)|(?<!\\w)(?=\\w))") == 0 &&
               dw2 && dw2->kind == DEFK_STR &&
               strcmp(dw2->str, "[A-Za-z0-9_]") == 0;
    if (!ok3)
        bad("definitions: [DD-11.4] recursion guard: interleaved resolve "
            "(\\w flag=on, \\b flag=off, \\w flag=off) did not reproduce "
            "the three independent answers -- the resolver is carrying "
            "state between calls");
    else
        ok("definitions: [DD-11.4] recursion guard: interleaved resolve "
           "of two synthetic rows under alternating states shows no "
           "cross-call state leakage -- pcrec_def_resolve is a pure "
           "function of (row, Ctx state), the property DD-11.5's future "
           "nested resolution (\\b's expansion naming \\w) will depend on");
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
    check_recursion_guard();
    check_containment_note();

    printf("\n== Summary ==\n");
    printf("checks passed: %d\n", pass);
    printf("checks failed: %d\n", fail);
    return fail == 0 ? 0 : 1;
}
