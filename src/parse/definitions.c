/* src/parse/definitions.c — [DD-11.1] the replacement/definition table's
 * ONE evaluator, resolver, tag-name table, and the core-set structural
 * predicate (D85, docs/design/definitions_table.md, r43-revised).
 *
 * WHAT THIS FILE DOES NOT DO: it does not wire the table into real parsing.
 * `pcrec_def_resolve` exists so a test (the self-oracle, [DD-11.3]) and the
 * structural check below can ask "what would this row's definition be under
 * this ParseMods state", but no `p_atom`/module producer calls it yet — the
 * shipped code arms (the D62 field+fold for `$`/`^`, the possessive-suffix
 * desugar in parse.c, …) are UNCHANGED. Wiring is [DD-11.5], gated on M6.6's
 * exact one-byte-fixed-lookbehind lowering existing (definitions_table.md
 * §4's DFA-erasure hazard) — see that note before adding a call site here.
 *
 * THE PREDICATE IS A TAG, evaluated by exactly one exhaustive no-default
 * switch (`pcrec_def_tag_applies`, below) — internal.h's own comment before
 * `struct RegRow` has the full ruling (r43 K1/K2/K3/K9). Four of the seven
 * tags have NO PRODUCER yet (UCP, UTF-8 encoding, a non-LF newline
 * convention, a bound [LIB] name) and answer `false` unconditionally, which
 * is sound: a row whose only other entry is `DEF_ALWAYS` simply falls
 * through to it, reproducing today's byte/LF/no-library behaviour exactly.
 */

#include <assert.h>
#include <string.h>

#include "core/internal.h"
#include "parse_mods.h"

bool pcrec_def_tag_applies(DefTag tag, const Ctx *cx)
{
    switch (tag) {
    case DEF_ALWAYS:
        return true;
    case DEF_MULTILINE:
        return cx->mods->multiline;
    case DEF_NOCAP:
        return cx->mods->nocap;
    /* NO PRODUCER YET — see the file header. Each is the FUTURE second row
     * for a family this table already carries (class escapes' UCP, the
     * literal-escape family's encoding, `\N`/`\R`/`$`/`^`'s newline
     * convention, [LIB]'s name binding); until one exists the question can
     * never be true, which is the SOUND default (the row's DEF_ALWAYS entry
     * is what fires, matching today's shipped behaviour exactly). */
    case DEF_UCP:
    case DEF_ENCODING_UTF8:
    case DEF_NEWLINE_CONV:
    case DEF_LIB_NAME_BOUND:
        return false;
    }
    /* unreachable: no default arm, so a tag added to DefTag without an arm
     * here is a compile error (mrl.c's rule) rather than a silent `false`. */
    return false;
}

const RegDef *pcrec_def_resolve(const Ctx *cx, const RegRow *rw)
{
    if (!rw->definitions) return NULL;
    for (const RegDef *d = rw->definitions; d->kind != DEFK_END; d++) {
        if (pcrec_def_tag_applies(d->tag, cx))
            return d;
    }
    /* UNREACHABLE BY CONSTRUCTION (manager ruling, 2026-08-29, the identity
     * question): a well-formed `definitions` list always ends in a
     * DEF_ALWAYS entry — a real definition (the unconditional-replacement
     * rows: class escapes, \R, \b/\B, possessive, the fixed literal
     * escapes) or an explicit DEF_IDENTITY entry (^, $, the (?n)-scoped
     * capturing-group row) — and DEF_ALWAYS always answers true
     * (pcrec_def_tag_applies, above). Falling off this loop therefore means
     * the list itself is malformed (missing its DEF_ALWAYS terminal), which
     * is a defect in registry.c to fix, not a NULL this function should
     * hand back as if "no definition" were a legitimate answer — NULL as a
     * signal is exactly the ABSENCE-AS-DISCRIMINATOR hazard [DD-13]'s stamp
     * design already ruled out (a missing entry must not read the same as
     * a forgotten one). tests/registry/definitions_check.c's structural
     * check asserts every non-NULL list's construction directly, so this
     * assert should never fire outside a sabotage run. */
    assert(0 && "pcrec_def_resolve: definitions list has no DEF_ALWAYS "
                "terminal entry (malformed row in registry.c)");
    return NULL;
}

/* The tag's OWN name — `--list-definitions` prints this, never hand-authored
 * prose (r43's ruling: the predicate column and a stored callable were two
 * derivations of one fact; the tag name is the single one). */
const char *pcrec_def_tag_name(DefTag tag)
{
    switch (tag) {
    case DEF_ALWAYS:          return "DEF_ALWAYS";
    case DEF_MULTILINE:       return "DEF_MULTILINE";
    case DEF_NOCAP:           return "DEF_NOCAP";
    case DEF_UCP:             return "DEF_UCP";
    case DEF_ENCODING_UTF8:   return "DEF_ENCODING_UTF8";
    case DEF_NEWLINE_CONV:    return "DEF_NEWLINE_CONV";
    case DEF_LIB_NAME_BOUND:  return "DEF_LIB_NAME_BOUND";
    }
    return "?"; /* unreachable, same discipline as pcrec_def_tag_applies */
}

/* [DD-11.1] §3 item 2's structural check: is `k` one of the constructs
 * `docs/dev/plan.md`'s [DD-11] addendum (f) names as the IRREDUCIBLE CORE
 * ("classes, cat, alt, {m,n}+preference, atomic cut, capture, \A, \z,
 * lookaround, and the path-fact family (\K, backrefs, DD-14 call) — \G
 * stays primitive")? A definition's OWN core-syntax text must never contain
 * `A_EOL`/`A_WORDB`/`A_NWORDB` — those are exactly the three kinds full
 * reduction REMOVES (`\Z`/`(?m)$`/`\b`/`\B` all reduce to `A_LOOK`+`A_END`
 * or `A_LOOK` alone, definitions_table.md §2), so their appearance inside a
 * definition's expansion is the regression this check exists to catch.
 *
 * EXHAUSTIVE, NO DEFAULT (mrl.c's rule): a new `AKind` is a compile error
 * here until this function states which side of the reduction it falls on. */
bool pcrec_ast_is_core(AKind k)
{
    switch (k) {
    case A_CLASS:
    case A_CAT:
    case A_ALT:
    case A_REP:
    case A_EMPTY:
    case A_BOL:      /* \A only, in the fully-reduced target — see the note
                      * at definitions_table.md §2 ("\A is core") */
    case A_END:      /* \z */
    case A_GSTART:   /* \G "stays primitive" (D66) — still core vocabulary */
    case A_KRESET:   /* \K, the path-fact family */
    case A_CAP:
    case A_ATOMIC:
    case A_BREF:     /* backrefs, the path-fact family */
    case A_LOOK:     /* lookaround */
    case A_CALL:     /* DD-14 call, the path-fact family */
        return true;
    case A_EOL:      /* $/\Z's shipped alias — replaced away under full
                      * reduction (definitions_table.md §2) */
    case A_WORDB:    /* \b — replaced away */
    case A_NWORDB:   /* \B — replaced away */
        return false;
    }
    return false; /* unreachable */
}

/* The whole-tree walk, in the shape every other whole-tree predicate in this
 * codebase already takes (src/opt/atomic.c's header: "SEVEN switches over
 * AKind with NO default arm... a node kind added later is a compile error").
 * Placed HERE rather than in atomic.c because it is [DD-11]-specific TOOLING
 * — nothing on the compile path calls it, only the structural check below —
 * and atomic.c's own predicates are all live compile-path consumers.
 *
 * Follows `l`/`r` only, NEVER `u.call.body` (the AST's one back edge —
 * `subroutines_design.md` §4.4's rule, restated at every such walker in this
 * tree): a whole-tree walk already visits a callee at its own lexical
 * position, and following the edge is a non-terminating compile on a
 * self-referential pattern. None of today's definitions produce an A_CALL,
 * so this is a forward-looking guard, not a reachable path. */
bool pcrec_ast_all_core(const Ast *a)
{
    if (!a) return true;
    if (!pcrec_ast_is_core(a->k)) return false;
    return pcrec_ast_all_core(a->l) && pcrec_ast_all_core(a->r);
}

/* ---- DEFK_BUILDER entries (definitions_table.md §3's operand-taking
 * shape) — used by [DD-11.1]'s structural check today; [DD-11.5] is what
 * would call these from a real parse hook. Both take the body the
 * construct already built and return the core-syntax equivalent; neither
 * is reachable from parse.c yet. */

/* The possessive-suffix family's shared definition: `X*+`/`X++`/`X?+`/
 * `X{n,m}+` all become `(?>X{...})` — PCRE2's own definition, already
 * stated as prose in the four RK_QUANTSUFFIX rows' `note` field
 * (registry.c). `body` is the already-built `A_REP` node (the quantifier
 * itself is not part of the DEFINITION — only the atomic wrap is). */
Ast *pcrec_def_build_atomic(Ctx *cx, Ast *body)
{
    Ast *a = pcrec_ast_node(cx, A_ATOMIC);
    a->l = body;
    return a;
}

/* `(?n)`'s definition: `(...)` scoped by `(?n)` IS `(?:...)`, and pcrec's
 * own AST has no node for a non-capturing group at all (D31's erasure) —
 * so the definition is the IDENTITY on the group's inner AST, no `A_CAP`
 * wrapper. `cx` is unused; kept for signature parity with every other
 * DefBuilderFn (a builder that never needs `cx` today may need arena
 * allocation tomorrow, and a signature change then is a second place every
 * call site must move). */
Ast *pcrec_def_build_identity(Ctx *cx, Ast *body)
{
    (void)cx;
    return body;
}

/* ---- DEFK_TEXTFN entries (manager ruling, 2026-08-29: the general shape
 * for "a binding parameterized by text at the occurrence" — internal.h's
 * own comment before `DefKind` has the full ruling). Each is a pure
 * function of (operand, len, cx); none scans or moves a cursor. Each
 * CALLS THE EXISTING DECODER where one exists (bare `\x`'s per-digit value
 * is `pcrec_hexval`, parse.c's own exported hex-digit decode, the site
 * `esc_char_value`'s live 'x' case already uses); where none exists yet
 * (`\c`, `\o{}`, `\N{U+`, all module `misc`/`unicode-props`, UNBUILT
 * today), this function BECOMES that one site, on `\R`'s own precedent
 * (definitions_table.md: "the definitions table can carry an unbuilt
 * row's definition as data before any producer exists") — a future
 * producer calls the SAME function rather than growing a second
 * implementation beside it. NULL on a malformed operand (never reached
 * today: every construct these serve is either unbuilt, so nothing calls
 * this outside a test, or — bare `\x` — already validates its own digit
 * count before the definitions layer ever sees the operand). */

/* \cX ≡ X xor 0x40 (registry.c's own row note, ESC('c', ...)). `operand`
 * is exactly the one byte X. */
Ast *pcrec_def_text_cx(const char *operand, size_t len, Ctx *cx)
{
    if (len != 1) return NULL;
    return pcrec_ast_char(cx, (unsigned)((unsigned char)operand[0] ^ 0x40));
}

/* bare `\x` (2 hex digits, base tier, esc_char_value's own live rule) and
 * `\x{...}` (arbitrary-width hex, module unicode-props, UNBUILT — parked
 * in parse.c as a special case per src/parse/CLAUDE.md's registry section,
 * not given its own row by this pass; see the lane's report). `operand`
 * is the hex digit run with no `\x`/`{`/`}` — 1-2 digits for the bare
 * form. Values above 0xFF are refused (NULL) rather than truncated: a
 * malformed/out-of-range operand is the caller's defect to fix, not this
 * function's to paper over silently. */
Ast *pcrec_def_text_hex(const char *operand, size_t len, Ctx *cx)
{
    if (len == 0) return NULL;
    unsigned v = 0;
    for (size_t i = 0; i < len; i++) {
        int d = pcrec_hexval((unsigned char)operand[i]);
        if (d < 0) return NULL;
        v = v * 16 + (unsigned)d;
        if (v > 0xFF) return NULL;
    }
    return pcrec_ast_char(cx, v);
}

/* `\o{OOO}` (module misc, UNBUILT) — an arbitrary-length OCTAL run.
 * PCRE2's own construct; this function is its first decode site (see the
 * file-header note on this block). Values above 0xFF are refused for the
 * same reason `pcrec_def_text_hex` refuses them. */
Ast *pcrec_def_text_octal(const char *operand, size_t len, Ctx *cx)
{
    if (len == 0) return NULL;
    unsigned v = 0;
    for (size_t i = 0; i < len; i++) {
        unsigned char c = (unsigned char)operand[i];
        if (c < '0' || c > '7') return NULL;
        v = v * 8 + (unsigned)(c - '0');
        if (v > 0xFF) return NULL;
    }
    return pcrec_ast_char(cx, v);
}

/* `\N{U+HHHH}` (module unicode-props, UNBUILT) — a Unicode code point BY
 * NUMBER. `operand` is the hex digits after `U+`. Today's definition is
 * the BYTE-encoding reading: a code point in 0..0xFF is that literal
 * byte; anything wider has no byte-encoding meaning yet (refused, NULL) —
 * the "sequence under utf8" second row the ruling's own template text
 * names is the encoding tag's future second row (DEF_ENCODING_UTF8),
 * not something this function decides. */
Ast *pcrec_def_text_unicode(const char *operand, size_t len, Ctx *cx)
{
    if (len == 0) return NULL;
    unsigned v = 0;
    for (size_t i = 0; i < len; i++) {
        int d = pcrec_hexval((unsigned char)operand[i]);
        if (d < 0) return NULL;
        v = v * 16 + (unsigned)d;
        if (v > 0xFF) return NULL;
    }
    return pcrec_ast_char(cx, v);
}
