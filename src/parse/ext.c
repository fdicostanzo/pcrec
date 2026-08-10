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
 * cheap: a base-tier pattern reaches only the class-bracket one, once per
 * non-negated `[` (measured, R6 — the older claim of "none at all" was wrong).
 * `(?:` is the one
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
 * A NAME decides here, and since Q1 pcrec reads it. Until Q1 this function
 * ignored the name entirely and answered "requires module 'verbs'" for all of
 * them, which was wrong in three separate ways at once:
 *
 *   `(*NOTAVERB)`  was promised a module that will never implement it, because
 *                  PCRE2 has no such verb (error 160)
 *   `(*)`          was called a verb, when PCRE2 reads `(` then a `*` that
 *                  quantifies nothing (error 109)
 *   `a(*CR)`       was called a verb, when a start-of-pattern option anywhere
 *                  but the start is error 160
 *
 * and, worse than any single wrong answer, it made pcrec's answer INDEPENDENT
 * of the name — so no differential against libpcre2 over names could say
 * anything. That is what Q1 unlocks and PC-3 spends: see D25 and
 * tests/registry/pcre2_check.c.
 *
 * WHAT THIS FUNCTION DECIDES, and it is only ever one of four things: the
 * quantifier error, the table's "no such name" message, a name's own message
 * (`MARK` alone has one), or the row's "requires module 'verbs'". It does NOT
 * parse the argument — an accepted form still ends the compile here.
 *
 * The forms are read from the VerbName table in registry.c, every bit of which
 * is measured against libpcre2 rather than read from documentation. */
void pcrec_ext_verb(Ctx *cx, size_t at)
{
    const RegRow *r = pcrec_registry_find(RK_VERB, REG_SEL_ANY);
    const char *pat = cx->pat;
    size_t n = cx->patlen;
    size_t star = at + 1;           /* the '*'; `at` is the '(' */
    size_t nstart = star + 1;
    size_t i = nstart;

    if (!r) ctx_fail(cx, at, "internal error: no registry row for (*");
    if (r->diag != RD_FIXED)
        BAD_ROW(cx, at, "a (* verb");

    /* The name runs to the first of `)`, `:`, `=` or the end of the pattern.
     * Nothing else terminates it: `(*NO_JIT )` is not `NO_JIT` with a trailing
     * space, it is the name `NO_JIT ` and PCRE2 rejects it. */
    while (i < n && pat[i] != ')' && pat[i] != ':' && pat[i] != '=') i++;
    size_t nlen = i - nstart;
    int next = i < n ? (unsigned char)pat[i] : -1;

    /* An EMPTY name has three different answers, and the first version of this
     * code got one of them wrong until the PC-3 differential said so on its
     * first run — over a thousand probes, all of this shape.
     *
     *   `(*)`, `(*`     not this doorway at all: `(` followed by a quantifier
     *                   with nothing to quantify (PCRE2 error 109, and what
     *                   parse.c's own `case '*'` says for a bare `*`). Reported
     *                   at the `*`, matching both.
     *   `(*:NAME)`      a synonym for `(*MARK:NAME)`. It resolves to the MARK
     *                   row and inherits its rules, which is why `(*:)` reports
     *                   "(*MARK) must have an argument" and not a "no such name".
     *   `(*=1)`         an ordinary unrecognised name that happens to be empty:
     *                   PCRE2 error 160. Falling through with a zero-length name
     *                   gets that for free — no table contains "" — which is why
     *                   there is no third branch here. */
    const char *name;
    size_t      namelen;
    if (nlen)              { name = pat + nstart; namelen = nlen; }
    else if (next == ':')  { name = "MARK";       namelen = 4;    }
    else if (next == '=')  { name = "";           namelen = 0;    }
    else ctx_fail(cx, star, "quantifier does not follow a repeatable item");

    /* A name too long to be a name at all is a LENGTH complaint in PCRE2, not a
     * "no such name" one, and it is the same complaint in both tables. Measured
     * on libpcre2 10.46 (R8/C2-4): 128 bytes is error 160/195 as usual, 129 is
     * error 148, in every form and in both tables. The limit is on the NAME —
     * `(*MARK:` followed by 200 bytes of argument compiles fine. */
    size_t maxname;
    const char *toolong = pcrec_registry_verb_name_limit(&maxname);
    if (namelen > maxname) ctx_fail(cx, at, "%s", toolong);

    const VerbTable *t =
        pcrec_registry_verb_table(namelen ? (unsigned char)name[0] : -1);
    const VerbName  *v = pcrec_registry_verb_find(t, name, namelen);
    if (!v) ctx_fail(cx, at, "%s", t->unknown_msg);

    /* Which FORM was written. A form of 0 means "none of them", which is what a
     * truncated construct produces — and PCRE2 agrees: `(*CR` and `(*ACCEPT:x`
     * are both error 160, the same as an unknown name. */
    unsigned form = 0;
    if (next == ')') {
        form = VF_BARE;
    } else if (next == ':') {
        if (v->forms & VF_GROUPARG) {
            /* A subpattern argument. The doorway does not require the closing
             * `)` to be present — PCRE2 recognises `(*pla:x` and then reports a
             * missing parenthesis (error 114), a different complaint entirely. */
            form = (i + 1 < n && pat[i + 1] == ')') ? VF_EMPTYARG : VF_ARG;
        } else {
            /* A name-run argument, terminated by `)`, which must exist: without
             * it PCRE2 does not recognise the construct at all. `:` is an
             * ordinary character inside it (`(*MARK:a:b)` compiles). */
            size_t j = i + 1;
            while (j < n && pat[j] != ')') j++;
            if (j < n) form = (j == i + 1) ? VF_EMPTYARG : VF_ARG;
        }
    } else if (next == '=') {
        /* Digits only, at least one, then `)`. `(*LIMIT_MATCH= 1)` and
         * `(*LIMIT_MATCH=x)` are both error 160; `=01` is accepted.
         *
         * AND A MAGNITUDE RULE, which the first version of this code did not
         * have because the probes that measured it were one and two digits long
         * (R8/C2-3 — the sweep agreed because the axis it varied was the NAME).
         * PCRE2 refuses while ACCUMULATING, one digit before its 32-bit
         * accumulator would overflow, so the boundary is 4294967290 and not
         * 4294967296: `(*LIMIT_MATCH=4294967289)` compiles and
         * `(*LIMIT_MATCH=4294967290)` is error 160. LENGTH is not the rule —
         * `=00000000000000000001` compiles, because leading zeros never move
         * the accumulator. Reproduced here exactly, including that. */
        size_t j = i + 1;
        unsigned long long acc = 0;
        bool fits = true;
        while (j < n && pat[j] >= '0' && pat[j] <= '9') {
            if (acc > 429496728ull) fits = false;   /* UINT32_MAX/10 - 1 */
            /* `acc` keeps accumulating past that point and WRAPS on a long
             * enough digit run. That is defined behaviour for an unsigned type
             * and the wrapped value is never read, because `fits` is sticky —
             * it is only ever cleared. Said out loud rather than left for a
             * reader to re-derive, or for someone to "fix" by resetting it. */
            acc = acc * 10 + (unsigned)(pat[j] - '0');
            j++;
        }
        if (fits && j > i + 1 && j < n && pat[j] == ')') form = VF_EQNUM;
    }

    if (!(v->forms & form))
        ctx_fail(cx, at, "%s",
                 (v->own_forms & form) ? v->own_msg : t->unknown_msg);

    /* Start-of-pattern options are valid only at the start. PCRE2 allows a RUN
     * of them — `(*UTF)(*CR)` compiles — and pcrec's rule is `at == 0` exactly.
     *
     * That is equivalent TO THE GENERAL PREFIX-RUN RULE, as an implementation
     * choice inside pcrec, and to nothing else: any earlier verb would already
     * have ended this compile with "requires module 'verbs'", so a run can
     * never reach here with a non-zero offset, and the two rules cannot differ
     * on any pattern. Writing the general scan now would be code whose only
     * interesting branch nothing can execute. When module 'verbs' lands and
     * these constructs start being ACCEPTED, that stops being true and the scan
     * is what replaces this line.
     *
     * IT DOES NOT MEAN pcrec's message matches PCRE2's on every pattern with an
     * option in it (R8/C2). `(*UTF)a(*UTF)` is PCRE2 error 160 — about the
     * SECOND one — while pcrec answers about the first, because pcrec reports
     * the leftmost construct it cannot handle and stops. That is pcrec's rule
     * at every doorway (`\d{3,1}` is "requires module 'classes'" here and
     * "numbers out of order" in PCRE2), and the general prefix scan would not
     * change it. */
    if ((v->forms & VF_ATSTART) && at != 0)
        ctx_fail(cx, at, "%s", t->unknown_msg);

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
