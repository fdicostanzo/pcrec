/* The four doorways: dispatch from the base grammar into the construct
 * registry (D24, step SR-2).
 *
 * WHY THIS FILE EXISTS. SR-1 built registry.c — one declarative home for every
 * non-base construct — but parse.c did not read it, so the registry was a
 * SIXTH copy of knowledge that already lived in five places. This file is the
 * edge that makes it the only copy: parse.c now keeps the base grammar and
 * nothing else, and every non-base byte leaves it through one of four calls.
 *
 *     after `\`              pcrec_ext_escape        (\d \v \p \K \g \Q \1)
 *     after `(?`             pcrec_ext_group         ((?= (?< (?> (?# (?i)
 *     after `(*`             pcrec_ext_verb          ((*SKIP) (*CR))
 *     after `[` in a class   pcrec_ext_class_bracket ([[:alpha:]] [[.a.]])
 *
 * THE BASE SWITCH RUNS FIRST AND RETURNS. Every one of these is called only
 * after parse.c's own switch has declined, which is what keeps the common path
 * free of lookups: a base-tier pattern reaches none of them. `(?:` is the one
 * construct that shares a doorway with non-base syntax, and parse.c answers it
 * before the call — its registry row exists so the table is COMPLETE for SR-3's
 * dump, not because anything looks it up. SR-5 turns that from a claim into an
 * instrumented measurement.
 *
 * WHAT DOES NOT LIVE HERE. Base syntax, including two things that look like
 * they belong: `\x{...}` and the possessive `+` are sub-cases of BASE
 * constructs (the `\x` decoder and the quantifier suffix), not doorways, and
 * `\b` inside a character class is base syntax too — it decodes to backspace
 * without a lookup, which is what the row's RF_CLASS_BASE flag records.
 *
 * THESE FUNCTIONS DO NOT RETURN, TODAY. Every row is RS_MODULE or RS_REJECTED,
 * so every dispatch ends in a diagnostic. The `noreturn` attributes state
 * today's truth rather than the design's: when SR-6 lands the first real module
 * handler, one of these starts returning a value and gcc warns.
 *
 * WARNS, not errors — this comment claimed otherwise until an R5 critic
 * compiled SR-6's shape and watched `make` succeed. There is no -Werror in the
 * Makefile and no -W option controls this particular warning. Treat the
 * attribute as a loud hint whose promotion to a guard is R5-Q1. */

#include "core/internal.h"

/* A row whose diag value does not belong to its kind is a registry defect, not
 * a pattern error. It is reported like any other failure because the parser has
 * no other channel, but the wording is deliberately not a "requires module"
 * diagnostic: nothing a caller writes can produce it. */
#define BAD_ROW(cx, at, what) \
    ctx_fail((cx), (at), "internal error: malformed registry row for " what)

/* ---- doorway 1: after '\' ----------------------------------------------
 * `c` is the byte after the backslash and the cursor sits just past it. Called
 * only once parse.c's decoder has declined: the plain character escapes
 * (\n \t \r \f \a \e \xHH), escaped punctuation and class-context `\b` all
 * return a byte value and never arrive here.
 *
 * `in_class` selects the diagnostic, and it selects more than the wording:
 * RD_MODULE_OCTAL is the ATOM form only. Inside a class parse.c has always
 * printed the plain module template for `\1`, merging the digit case with every
 * other module-routed escape, and byte-identity requires reproducing that. */
void pcrec_ext_escape(Ctx *cx, int c, bool in_class, size_t at)
{
    const RegRow *r = pcrec_registry_find(RK_ESC, c);

    if (!r) {
        if (in_class) ctx_fail(cx, at, "unknown escape \\%c in class", c);
        ctx_fail(cx, at, "unknown escape \\%c", c);
    }
    if (r->diag == RD_FIXED)
        ctx_fail(cx, at, "%s", r->msg);
    if (r->diag != RD_MODULE && r->diag != RD_MODULE_OCTAL)
        BAD_ROW(cx, at, "an escape");

    if (in_class)
        ctx_fail(cx, at, "\\%c in a class requires module '%s'", c, r->module);
    if (r->diag == RD_MODULE_OCTAL)
        ctx_fail(cx, at, "\\%c (backreference/octal) requires module '%s'",
                 c, r->module);
    ctx_fail(cx, at, "\\%c requires module '%s'", c, r->module);
}

/* ---- doorway 2: after '(?' ----------------------------------------------
 * `c2` is the byte after the '?', or -1 when the pattern ends there. That -1 is
 * also REG_SEL_ANY's value, so the lookup lands on the catch-all row twice
 * over — once as an exact selector match, once as the fallback. It is the same
 * row and the same diagnostic either way, and parse.c printed '?' for the
 * missing byte, which is reproduced below. */
void pcrec_ext_group(Ctx *cx, int c2, size_t at)
{
    const RegRow *r = pcrec_registry_find(RK_GROUP, c2);
    int shown = c2 < 0 ? '?' : c2;

    /* Only reachable by deleting the catch-all row, which tests/registry's
     * hand-written manifest also refuses; a NULL deref is not an acceptable
     * second answer to that. */
    if (!r) ctx_fail(cx, at, "internal error: no registry row for (?%c", shown);

    if (r->diag == RD_FIXED)
        ctx_fail(cx, at, "%s", r->msg);
    if (r->diag != RD_MODULE)
        BAD_ROW(cx, at, "a (? construct");
    ctx_fail(cx, at, "(?%c...) requires module '%s'", shown, r->module);
}

/* ---- doorway 3: after '(*' ----------------------------------------------
 * A NAME decides here, but pcrec does not yet distinguish the names: a single
 * catch-all row carries the one blanket diagnostic. The sweep in
 * tests/registry/ is byte-keyed while this doorway is name-keyed, so it proves
 * every BYTE after `(*` reaches this call and proves nothing about a
 * name-conditional branch — per-verb rows arrive with module 'verbs' (SR-6). */
void pcrec_ext_verb(Ctx *cx, size_t at)
{
    const RegRow *r = pcrec_registry_find(RK_VERB, REG_SEL_ANY);

    if (!r) ctx_fail(cx, at, "internal error: no registry row for (*");
    if (r->diag != RD_FIXED)
        BAD_ROW(cx, at, "a (* verb");
    ctx_fail(cx, at, "%s", r->msg);
}

/* ---- doorway 4: after '[' inside a class --------------------------------
 * The only doorway that can decline. `[` is an ordinary class member most of
 * the time, so this returns false to mean "no construct here, carry on" — and
 * for the delimiter-pair constructs it returns false far more often than it
 * fails, because PCRE2 only reads `[.` as a collating element when the matching
 * `.]` appears later. `[[.]`, `[a[.b]` and `[.]` all compile.
 *
 * `at` is the offset to report, `from` the offset just past the delimiter, and
 * `at_class_open` says whether the CLASS's own bracket is acting as the opener
 * (`[.a.]`) rather than a bracket inside it (`[[.a.]]`). That distinction is
 * not decoration: `[.a.]` is an error at offset 0 while `[:alpha:]` is a
 * perfectly ordinary class of five characters, pinned against libpcre2 10.46.
 * RF_CLASS_DELIM is what separates them — see its definition in internal.h. */
void pcrec_ext_class_bracket(Ctx *cx, int c2, size_t at, size_t from,
                             bool at_class_open)
{
    /* No `if (c2 < 0)` guard: it was here, and it was redundant rather than
     * defensive. `find(RK_CLASSBRACKET, -1)` returns NULL because this kind has
     * no catch-all row — which registry_check.c now REQUIRES of it, since a
     * catch-all would turn every unmatched byte in a class into a construct. So
     * the end-of-pattern case is handled one line below, by the check that
     * handles every other unrecognised byte. */
    const RegRow *r = pcrec_registry_find(RK_CLASSBRACKET, c2);
    if (!r) return;

    if (r->flags & RF_CLASS_DELIM) {
        /* KNOWN WRONG, and deliberately unchanged here: this scan runs to the
         * end of the PATTERN rather than the end of the character class, so a
         * `.]` outside the class makes an ordinary `[.` look closed and pcrec
         * rejects patterns PCRE2 compiles. Carried across verbatim by SR-2 —
         * which is why the byte-identity proof correctly saw no change, an
         * identity proof being unable to see a bug both sides share. Measured
         * and recorded as K4, with PCRE2's three missing scan rules and the
         * warning that they must land together. */
        bool closed = false;
        for (size_t i = from; i + 1 < cx->patlen; i++)
            if (cx->pat[i] == (char)c2 && cx->pat[i + 1] == ']') { closed = true; break; }
        if (!closed) return;
    } else if (at_class_open) {
        /* The class's own bracket cannot open a `[X...X]` construct. This is
         * what keeps `[:alpha:]` compiling — which is K3's over-acceptance,
         * preserved on purpose so SR-2 stayed byte-identical. Its only live
         * consumer is the `:` row, and until R5 nothing in the repo entered
         * this doorway at all; `accept '[:]'` and `accept '[:a]'` in
         * tests/reject/ are what guard it now. */
        return;                               /* needs a bracket of its own */
    }

    if (r->diag != RD_FIXED)
        BAD_ROW(cx, at, "a [ construct in a class");
    ctx_fail(cx, at, "%s", r->msg);
}
