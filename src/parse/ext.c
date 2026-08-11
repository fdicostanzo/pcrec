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
 * THE CLAIM IS RETURNED, NOT RAISED (MOD-0.1, D33 §5). Every dispatch still
 * ends in a refusal — every row is RS_MODULE or RS_REJECTED — but the refusal
 * is now an ExtResult the CALLER receives and hands to pcrec_ext_finish, the
 * one epilogue below, instead of a ctx_fail that longjmps past it. The
 * diagnostic is formatted AT CLAIM TIME into the result (representability:
 * a diagnostic must outlive its handler or D33 §6 collapses and pair_opens'
 * deletion — later reversed by R14 anyway — comes back). Byte-identity: the
 * REFUSE macro runs the exact snprintf the old ctx_fail ran, into a buffer of
 * the same size, and the epilogue fires it at the same offset; no rendered
 * diagnostic moved. The `noreturn` era's R5 lesson (warn-not-error, no guard
 * without -Werror) is retired with the attributes themselves: falling off a
 * value-returning doorway is now an ordinary -Wreturn-type warning that
 * `make strict` promotes. */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"

/* Format a refusal at claim time and return it. The arguments are what the
 * pre-epilogue ctx_fail calls passed, verbatim, so the rendered text cannot
 * drift from what tests/reject/ pins. */
#define REFUSE(atpos, ...) do {                                              \
        ExtResult res_ = { .what = EXT_REFUSAL, .at = (atpos), .msg = "" };  \
        snprintf(res_.msg, sizeof res_.msg, __VA_ARGS__);                    \
        return res_;                                                         \
    } while (0)

/* No construct here; the cursor is unchanged. Only doorway 4 produces this. */
#define DECLINE() return (ExtResult){ .what = EXT_NOT_MINE, .at = 0, .msg = "" }

/* A row whose diag value does not belong to its kind is a registry defect, not
 * a pattern error. It is reported like any other failure because the parser has
 * no other channel, but the wording is deliberately not a "requires module"
 * diagnostic: nothing a caller writes can produce it. */
#define BAD_ROW(at, what) \
    REFUSE((at), "internal error: malformed registry row for " what)

/* The ONE epilogue (D33 §5/§8): a refusal fires here, and only here. A caller
 * that must override a claim — the endpoint rule, D33 §6 — looks at the
 * ExtResult BEFORE calling this; today no caller overrides. */
void pcrec_ext_finish(Ctx *cx, const ExtResult *r)
{
    if (r->what == EXT_NOT_MINE) return;
    ctx_fail(cx, r->at, "%s", r->msg);
}

/* SR-9's tail context, computed from the Ctx these functions already hold.
 * `after` is the offset of the first byte PAST the doorway's selector byte, so
 * a row's `tail` is compared against the text the pattern really has there.
 *
 * THE POINT OF DOING IT HERE is that parse.c does not change: the design's
 * comparison table claims "parse.c call sites changed: 0" against the string
 * selector alternative, and this is what makes that true. A truncated pattern
 * yields avail = 0, which matches no tail, so `(?P` at end-of-pattern falls to
 * the bare `P` row instead of reading past the buffer. */
static const char *tail_at(const Ctx *cx, size_t after, size_t *avail)
{
    if (after >= cx->patlen) { *avail = 0; return NULL; }
    *avail = cx->patlen - after;
    return cx->pat + after;
}

/* ---- doorway 1: after '\' ----------------------------------------------
 * `c` is the byte after the backslash and the cursor sits just past it. Called
 * only once parse.c's decoder has declined: the plain character escapes
 * (\n \t \r \f \a \e \xHH), escaped punctuation and class-context `\b` all
 * return a byte value and never arrive here.
 *
 * `in_class` selects the diagnostic, and it selects more than the wording:
 * RD_MODULE_OCTAL is the ATOM form only. Since FIX-3 (K13) the digit rows and
 * `\g`/`\k` never arrive here with in_class set at all — the class position is
 * base syntax (octal / literal fallback, RF_CLASS_BASE), decoded in parse.c. */
ExtResult pcrec_ext_escape(Ctx *cx, int c, bool in_class, size_t at)
{
    /* cx->pos sits just past the escape byte, so that IS the tail position. */
    size_t avail;
    const char *tl = tail_at(cx, cx->pos, &avail);
    const RegRow *r = pcrec_registry_find(RK_ESC, c, tl, avail);

    if (!r) {
        if (in_class) REFUSE(at, "unknown escape \\%c in class", c);
        REFUSE(at, "unknown escape \\%c", c);
    }
    if (r->diag == RD_FIXED)
        REFUSE(at, "%s", r->msg);
    if (r->diag != RD_MODULE && r->diag != RD_MODULE_OCTAL)
        BAD_ROW(at, "an escape");

    /* PCRE2 forbids some of these INSIDE a class and always will, so naming a
     * module there is the over-promise D26 calls a defect: module `assertions`
     * will implement `\A`, and will never implement `\A`-in-a-class, because
     * that is not a construct (error 107; 71 for `\N`). Ten rows carry the flag
     * — A B G K Z z C R X N — and it was found by a test writer reading the spec
     * with no sight of this file (R9/SPEC-classes-F1). The knowledge was already
     * HERE, in the `\N` row's own note, in a field no check reads.
     *
     * Distinct from RF_CLASS_BASE, where the doorway is never entered at all
     * (`[\b]` is backspace, base syntax). */
    if (in_class && (r->flags & RF_CLASS_INVALID))
        REFUSE(at, "\\%c is not valid inside a character class", c);
    if (in_class) {
        /* The K12 endpoint payload (§16.3(e), exercisable subset): certify
         * SET-shape only where the row's measured class_expect covers every
         * form that can reach it — the construct must BE its selector byte
         * (syntax "\X", length 2), which is the ten char-type escapes and
         * excludes every body-carrying row (\p{...} is "set 117" for the
         * probe form, but [0-\p{Foo}] is PCRE2 147, so the row cannot be
         * certified; see the ExtResult comment). */
        ExtResult res = { .what = EXT_REFUSAL, .at = at, .msg = "" };
        res.ep_set_certain = r->class_expect &&
                             strncmp(r->class_expect, "set ", 4) == 0 &&
                             r->syntax[0] == '\\' && r->syntax[1] != '\0' &&
                             r->syntax[2] == '\0';
        snprintf(res.msg, sizeof res.msg,
                 "\\%c in a class requires module '%s'", c, r->module);
        return res;
    }
    if (r->diag == RD_MODULE_OCTAL)
        REFUSE(at, "\\%c (backreference/octal) requires module '%s'",
               c, r->module);
    REFUSE(at, "\\%c requires module '%s'", c, r->module);
}

/* ---- doorway 2: after '(?' ----------------------------------------------
 * `c2` is the byte after the '?', or -1 when the pattern ends there. That -1 is
 * also REG_SEL_ANY's value, so the lookup lands on the catch-all row twice
 * over — once as an exact selector match, once as the fallback. It is the same
 * row and the same diagnostic either way, and parse.c printed '?' for the
 * missing byte, which is reproduced below. */
ExtResult pcrec_ext_group(Ctx *cx, int c2, size_t at)
{
    /* cx->pos is at the '?'; c2 is the byte after it; so the tail starts two
     * past the cursor. When the pattern ends at the '?' that is already beyond
     * patlen and tail_at reports avail = 0. */
    size_t avail;
    const char *tl = tail_at(cx, cx->pos + 2, &avail);
    const RegRow *r = pcrec_registry_find(RK_GROUP, c2, tl, avail);
    int shown = c2 < 0 ? '?' : c2;

    /* Only reachable by deleting the catch-all row, which tests/registry's
     * hand-written manifest also refuses; a NULL deref is not an acceptable
     * second answer to that. */
    if (!r) REFUSE(at, "internal error: no registry row for (?%c", shown);

    if (r->diag == RD_FIXED)
        REFUSE(at, "%s", r->msg);
    if (r->diag != RD_MODULE)
        BAD_ROW(at, "a (? construct");

    /* AN OPTION SETTING IS A RUN, NOT A BYTE (Q2). Splitting the old catch-all
     * into eleven letter rows fixed `(?q)` and left `(?iZ)` — PCRE2 error 111 —
     * still being promised module 'modifiers', because the row was chosen by the
     * first byte and nothing read the rest. Reading the run is what makes this
     * doorway's answer depend on the whole construct, exactly as Q1 made the
     * `(*` doorway depend on the whole name.
     *
     * The run starts AT the selector byte (`(?i-m:` has the run "i-m"), so this
     * asks about cx->pos + 1 rather than the tail position used above. On
     * failure the answer is the doorway's own catch-all row, so the rejection
     * has ONE home: rewording it there changes it here too, and a second copy of
     * PCRE2's sentence is exactly the drift this registry exists to prevent. */
    if (r->flags & RF_OPTION_RUN) {
        size_t oavail;
        const char *orun = tail_at(cx, cx->pos + 1, &oavail);
        if (!pcrec_registry_option_run_ok(orun, oavail)) {
            const RegRow *any = pcrec_registry_find(RK_GROUP, REG_SEL_ANY, NULL, 0);
            if (!any || any->diag != RD_FIXED)
                BAD_ROW(at, "the (? doorway's catch-all");
            REFUSE(at, "%s", any->msg);
        }
    }
    /* K14 (design §17.2): a ROADMAP_NEVER row is real PCRE2 syntax pcrec
     * deliberately excludes, and promising its module is the defect D26's
     * tier-2 row names. The module stays on the row as classification; it is
     * just never rendered as a promise. */
    if (r->roadmap == ROADMAP_NEVER)
        REFUSE(at, "(?%c...) is outside pcrec's scope and no module will implement it (see docs/pcre2_compliance.md)", shown);
    REFUSE(at, "(?%c...) requires module '%s'", shown, r->module);
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
ExtResult pcrec_ext_verb(Ctx *cx, size_t at)
{
    const RegRow *r = pcrec_registry_find(RK_VERB, REG_SEL_ANY, NULL, 0);
    const char *pat = cx->pat;
    size_t n = cx->patlen;
    size_t star = at + 1;           /* the '*'; `at` is the '(' */
    size_t nstart = star + 1;
    size_t i = nstart;

    if (!r) REFUSE(at, "internal error: no registry row for (*");
    if (r->diag != RD_FIXED)
        BAD_ROW(at, "a (* verb");

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
    else REFUSE(star, "quantifier does not follow a repeatable item");

    /* A name too long to be a name at all is a LENGTH complaint in PCRE2, not a
     * "no such name" one, and it is the same complaint in both tables. Measured
     * on libpcre2 10.46 (R8/C2-4): 128 bytes is error 160/195 as usual, 129 is
     * error 148, in every form and in both tables. The limit is on the NAME —
     * `(*MARK:` followed by 200 bytes of argument compiles fine. */
    size_t maxname;
    const char *toolong = pcrec_registry_verb_name_limit(&maxname);
    if (namelen > maxname) REFUSE(at, "%s", toolong);

    const VerbTable *t =
        pcrec_registry_verb_table(namelen ? (unsigned char)name[0] : -1);
    const VerbName  *v = pcrec_registry_verb_find(t, name, namelen);
    if (!v) REFUSE(at, "%s", t->unknown_msg);

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
            if (acc > PCREC_VERB_LIMIT_ACC_MAX) fits = false;
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
        REFUSE(at, "%s",
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
        REFUSE(at, "%s", t->unknown_msg);

    /* K14 (design §17.2): disposition is a PER-NAME fact — `(*COMMIT)` is
     * OUT-OF-SCOPE while `(*pla:...)` is a lookaround in verb spelling — with
     * the row's value as the default. It fires only for a form PCRE2 would
     * ACCEPT: a malformed form of a NEVER name keeps PCRE2's own form error
     * above, because the roadmap is an answer about the construct, not about
     * a typo. The `(*:x)` MARK synonym resolves to MARK's entry and inherits
     * its NEVER, which is why the message below prints the resolved name. */
    if ((v->roadmap ? v->roadmap : r->roadmap) == ROADMAP_NEVER)
        REFUSE(at, "(*%.*s) is outside pcrec's scope and no module will implement it (see docs/pcre2_compliance.md)",
               (int)namelen, name);

    REFUSE(at, "%s", r->msg);
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
/* Does a delimiter-pair construct actually OPEN at `from`, with `c2` as its
 * delimiter? This is K4's three-rule scan as a PREDICATE, so that a caller which
 * is not the doorway can ask the question without triggering a diagnostic.
 *
 * It exists for range endpoints (R9/SPEC-FA). PCRE2 refuses a range whose
 * endpoint is one of these constructs — `[0-[:digit:]]` is error 150, "invalid
 * range in character class" — and pcrec was reading the `[` as an ordinary
 * literal member and EMITTING A MATCHER. Measured against libpcre2 10.46, and
 * the boundary is exactly this scan rather than "the byte is `[`":
 *
 *   [0-[a]         compiles   `[a` opens nothing
 *   [0-[:]         compiles   `[:` with no `:]` after it opens nothing
 *   [0-[:digit]    compiles   same — the pair never closes
 *   [0-[:digit:]]  err 150    the pair closes, so a construct is the endpoint
 *   [0-[.a.]       err 150    ...even when the CLASS itself never closes
 *   [0-[:foo:]]    err 150    position beats name validity; not "unknown name"
 *
 * `rules 1-3` are documented at length in the doorway below; this shares them
 * rather than restating them, because two copies of that scan is exactly the
 * duplication SR-2 removed. */
bool pcrec_ext_class_pair_opens(Ctx *cx, int c2, size_t from)
{
    /* No class-bracket row carries a tail: this doorway's constructs are
     * decided by the delimiter byte plus the SCAN below, not by the next byte.
     * Passing NULL/0 asks the tail-less question explicitly rather than letting
     * a future tailed row here change this scan's meaning by accident. */
    const RegRow *r = pcrec_registry_find(RK_CLASSBRACKET, c2, NULL, 0);
    if (!r || !(r->flags & RF_CLASS_DELIM)) return false;
    for (size_t i = from; i < cx->patlen; i++) {
        char ch = cx->pat[i];
        if (ch == '\\' && i + 1 < cx->patlen &&
            (cx->pat[i + 1] == ']' || cx->pat[i + 1] == '\\')) { i++; continue; }
        if (ch == (char)c2 && i + 1 < cx->patlen && cx->pat[i + 1] == ']') return true;
        if (ch == '[' && i + 1 < cx->patlen && cx->pat[i + 1] == (char)c2) return false;
        if (ch == ']') return false;
    }
    return false;
}

ExtResult pcrec_ext_class_bracket(Ctx *cx, int c2, size_t at, size_t from,
                                  bool at_class_open, bool at_content_start)
{
    /* No `if (c2 < 0)` guard: it was here, and it was redundant rather than
     * defensive. `find(RK_CLASSBRACKET, -1)` returns NULL because this kind has
     * no catch-all row — which registry_check.c now REQUIRES of it, since a
     * catch-all would turn every unmatched byte in a class into a construct. So
     * the end-of-pattern case is handled one line below, by the check that
     * handles every other unrecognised byte. */
    const RegRow *r = pcrec_registry_find(RK_CLASSBRACKET, c2, NULL, 0);
    if (!r) DECLINE();

    /* K4, fixed 2026-08-10 (FIX-2). This scan used to run to the end of the
     * PATTERN rather than the end of the CLASS, so a `.]` anywhere later — even
     * well outside the class — made an ordinary `[.` look closed and pcrec
     * rejected patterns PCRE2 compiles. `[a[.b]c]d.]` was the sharpest: the
     * `.]` it matched sits at offset 9 and the class closed at offset 7.
     *
     * PCRE2's rule has THREE parts and they must land TOGETHER, which is not a
     * style preference — adding the `]` rule without the escape rule flips
     * `[a[.b\].]` from a correct rejection into an over-acceptance, because the
     * `]` that ends the scan is one the backslash was hiding:
     *
     *   1. an unescaped `]` ends the class, so the pair can no longer close
     *   2. a `[` followed by the SAME delimiter is a NESTED opener and WINS —
     *      PCRE2 abandons the outer one and recognises the inner. NOTE what
     *      this code actually does about that: it abandons the outer pair, and
     *      nothing more. Recognising the inner construct happens later, when
     *      p_class reaches that `[` and enters doorway 4b again. So the
     *      `return` below is behaviourally identical to `break` — `closed` is
     *      false on that path, so the `if (!closed) return;` after the loop
     *      takes the same exit. Measured byte-identical over 1,239,480 patterns
     *      and over a 172,246-pattern verdict+message+offset dump (R9/C2).
     *   3. `\]` and `\\` are skipped as a UNIT
     *
     * THE ORDER OF THE CLOSE CHECK IS ARBITRARY, and the comment that stood
     * here said otherwise. It claimed the close check must come first "because
     * a delimiter immediately before `]` IS the closer, and rule 1 must not
     * consume that `]` out from under it". That hazard cannot occur: rule 1
     * tests the byte AT `i` (`ch == ']'`) while the close check tests
     * `pat[i] == c2 && pat[i+1] == ']'`, so the two predicates are DISJOINT
     * whenever `c2 != ']'` — and `c2` is only ever `:`, `.` or `=`. A critic
     * moved the close block after rule 1 and got byte-identical results over
     * 1,239,480 generated patterns, including the liveness counts, while the
     * same battery's other five sabotages each produced thousands of
     * divergences (R9/C2-1). The stated reason was untestable, not merely
     * untested.
     *
     * What makes the disjointness true is a property of the TABLE, not of this
     * function, so registry_check.c now asserts it: no RK_CLASSBRACKET row may
     * have `]` as its selector. Keep the order as it is — it reads well — but
     * do not believe it is load-bearing. */
    /* Start at `from`, not 0, so that a row reaching the RF_CLASS_NAMED check
     * below without having run the scan asks about a ZERO-length name rather
     * than about `0 - from`, which wraps to a huge size_t. No shipped row does
     * that (the one RF_CLASS_NAMED row also carries RF_CLASS_DELIM, and
     * registry_check.c now requires that pairing), and a critic measured that
     * even the wrapped length was memory-safe — but only because
     * `pcrec_registry_posix_known` compares lengths before it compares bytes,
     * which is an implementation detail of a different function that nothing
     * ties to this one (R9/C3-1). Two guards, because the coupling was by
     * accident and the natural "optimisation" of that function removes it. */
    size_t close_at = from;              /* index of the closing delimiter */
    if (r->flags & RF_CLASS_DELIM) {
        bool closed = false;
        /* `i < patlen`, and the bound is not load-bearing either: every body
         * inside reads `pat[i + 1]` only after its own `i + 1 < patlen` test,
         * so `i + 1 < patlen` here is byte-identical over the same 1,239,480
         * patterns. Stated because the previous version of this function used
         * the tighter bound and it would be easy to assume the change mattered
         * (R9/C2). */
        for (size_t i = from; i < cx->patlen; i++) {
            char ch = cx->pat[i];
            /* RULE 3 FIRST, and it means EXACTLY what K4 wrote: `\]` and `\\`
             * are skipped AS UNITS. A backslash escapes a `]` or another
             * backslash and NOTHING ELSE. I generalised it twice — first to
             * "skip any `\X`", then to "suppress only a class-ending `]`" — and
             * PC-3's generated sweep refuted both within minutes. Four measured
             * patterns pin it, and no weaker rule gets all four:
             *
             *   [[.\.]]      REJECT  `\.` is NOT a unit, so `.]` closes the pair
             *   [[.a\\]x.]   accept  `\\` IS a unit, so the `]` is unescaped and
             *                        ends the class before `.]` is reached
             *   [a[.b\].]    REJECT  `\]` IS a unit, so that `]` does not end
             *                        the class and `.]` closes the pair
             *   [[.b].]      accept  a bare `]` ends the class
             *
             * Skip-any-`\X` gets the first wrong; suppress-only-`]` gets the
             * second wrong. Only the two-character rule gets all four. */
            if (ch == '\\' && i + 1 < cx->patlen &&
                (cx->pat[i + 1] == ']' || cx->pat[i + 1] == '\\')) {
                i++;
                continue;
            }
            if (ch == (char)c2 && i + 1 < cx->patlen && cx->pat[i + 1] == ']') {
                closed = true; close_at = i; break;             /* the closer */
            }
            if (ch == '[' && i + 1 < cx->patlen && cx->pat[i + 1] == (char)c2)
                DECLINE();                                      /* rule 2 */
            if (ch == ']') break;                               /* rule 1 */
        }
        if (!closed) DECLINE();
    }

    /* The `else if (at_class_open) return;` that stood here is GONE, and its
     * removal is K3's fix rather than a tidy-up: it was what kept `[:alpha:]`
     * compiling, because the `:` row was the only one without RF_CLASS_DELIM
     * and so the only one that reached it. All three rows carry the flag now,
     * which made the branch unreachable as well as wrong.
     *
     * R5's sabotage battery found K3 by observing that deleting that branch
     * changed 0 of 4173 emission cases and broke no test — an invisible branch
     * with a real divergence behind it. `at_class_open` survives, but it is no
     * longer invisible: it now SELECTS THE MESSAGE, and tests/reject/ pins both. */
    if (r->diag != RD_FIXED)
        BAD_ROW(at, "a [ construct in a class");

    /* POSITION FIRST, then the name — which is libpcre2's own order, measured:
     * `[:foo:]` is "POSIX named classes are supported only within a class" at
     * offset 0, NOT "unknown POSIX class name". The construct is in the wrong
     * place, so whether its name is real never comes up. */
    if (at_class_open && r->open_msg)
        REFUSE(at, "%s", r->open_msg);

    /* A name outside the known set is not this construct at all, so naming a
     * module for it would be the over-promise this flag exists to remove:
     * `[[:foo:]]` is an error libpcre2 will never accept, and module 'classes'
     * cannot make it one. See RF_CLASS_NAMED in internal.h. */
    if ((r->flags & RF_CLASS_NAMED) &&
        !pcrec_registry_posix_known(cx->pat + from, close_at - from))
        REFUSE(at, "%s", pcrec_registry_posix_unknown_msg());

    /* A REAL name in a position libpcre2 will not take is still not a construct
     * (R9/C3-4). `<` and `>` are word-boundary assertions rather than classes,
     * and libpcre2 recognises them only as a class's ENTIRE content — so
     * `[[:<:]]` compiles while `[x[:<:]]`, `[^[:<:]]` and `[[:<:]a]` are all
     * "unknown POSIX class name". Answering "requires module 'classes'" for
     * those is the over-promise this row exists to remove, surviving for the
     * two names FIX-2 itself added.
     *
     * Entire content means: nothing before it (`at_content_start`, which is
     * false after any member and false when a `^` negated the class) and the
     * class's `]` immediately after the construct's own. */
    if ((r->flags & RF_CLASS_NAMED) &&
        pcrec_registry_posix_whole_class_only(cx->pat + from, close_at - from) &&
        !(at_content_start && close_at + 2 < cx->patlen && cx->pat[close_at + 2] == ']'))
        REFUSE(at, "%s", pcrec_registry_posix_unknown_msg());

    /* The final refusal — reached only after every own-error check above
     * declined to fire, so for the `:` row this is a KNOWN POSIX name in a
     * legal position: certifiably SET-shaped for the K12 endpoint rule (the
     * collating rows' class_expect is "err 113", never certified). `end` is
     * where a low endpoint's range dash would sit. */
    {
        ExtResult res = { .what = EXT_REFUSAL, .at = at, .msg = "" };
        res.ep_set_certain = r->class_expect &&
                             strncmp(r->class_expect, "set ", 4) == 0;
        res.end = close_at + 2;
        snprintf(res.msg, sizeof res.msg, "%s", r->msg);
        return res;
    }
}
