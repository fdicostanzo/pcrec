/* mod_recursion.c — module `recursion` ([DD-14] wave B+C): the SUBROUTINE-CALL
 * ports at the `(?` doorway, and the call half of the end-of-parse resolver
 * `src/parse/mod_backrefs.c` owns.
 *
 * Design: docs/design/subroutines_design.md §2 (the construct table), §4.1
 * (the node), §4.2 (one resolver, two rules). Rulings: docs/dev/decisions.md
 * D71 (all six), D70 (the union), D62 (parse-resolved state).
 *
 * WHAT A SUBROUTINE CALL IS, in one cell, because every consequence follows
 * from it: `(a|b)\1` on "ab" is NOMATCH and `(a|b)(?1)` on "ab" is (0,2). A
 * BACKREFERENCE wants the same TEXT; a CALL re-RUNS the group's pattern
 * (design §2.1, MEASURED on 10.46). So the two constructs share a resolution
 * PASS and share nothing else: `A_BREF.u.bref.refs` is a SET resolved at match
 * time, `A_CALL.u.call.target` is ONE NUMBER resolved at parse time.
 *
 * THREE PORTS HERE AND A FOURTH ELSEWHERE. `pcrec_rcport_num` serves `(?N)`
 * and `(?R)`, `pcrec_rcport_rel` the relative `(?+N)`/`(?-N)` family, and
 * `pcrec_rcport_name` the two by-name spellings `(?&name)` and `(?P>name)`.
 * The fourth doorway is `\g<...>`/`\g'...'`, which is module `backrefs`'
 * `\g` escape shared with this module by TAIL (P3) — those two rows carry
 * `NO_PORT` at wave B+C and therefore refuse ENABLED-BUT-UNBUILT through
 * ext.c's own epilogue, which is what keeps their D65 `built` column honest
 * until wave D wires them. See the note at the bottom of this file.
 *
 * NOTHING HERE RESOLVES A CALL — with ONE exception that is not a split.
 * Every port records a `PendingRef` (kind `PEND_CALL`) and
 * `pcrec_bref_resolve` settles it at end of parse, which is what makes a
 * FORWARD call legal by construction (`^(?+1)(a|b)$` on "ab" MATCHES, design
 * §2.3 — a forward *reference* can only read an unset group, a forward *call*
 * runs the group's pattern) and what gives the numeric, relative and by-name
 * spellings ONE definition of "group k exists".
 *
 * THE EXCEPTION IS THE ROOT, AND IT IS AN ABSENCE OF A QUESTION RATHER THAN A
 * SECOND ANSWER TO ONE. `(?R)`, `(?0)`, `(?00)` and (wave D) `\g<0>` target
 * THE WHOLE PATTERN (design §2.4, MEASURED: `^(a(?R)?b)$` on "aabb" is
 * NOMATCH because `(?R)` re-runs the anchors, while `^(a(?1)?b)$` is (0,4)).
 * The root always exists — it needs no group count, no name table and no
 * declaration — so there is nothing to defer, and the port sets
 * `u.call.target = 0` and queues NO pending record at all.
 *
 * THAT IS ALSO WHAT KEEPS `(a)(?-2)` HONEST WITHOUT A SECOND FIELD. A
 * relative offset can compute to zero — `(a)(?-2)` gives `1 - 2 + 1 == 0` —
 * and zero is a LEGAL ABSOLUTE TARGET while being an out-of-range relative
 * one (PCRE2: error 115). If the resolver read "number 0 means the root" it
 * would compile `(a)(?-2)` as `(?R)`. Because the root never reaches the
 * resolver, the resolver's numeric rule is exactly `A_BREF`'s — `1 <= n <=
 * ncap` or error 115 — and the two kinds differ in the NAME rule alone.
 *
 * THE LEADING-ZERO RULE IS THIS FILE'S SHARPEST TRAP (design §2.4a, R34
 * LENS1-4). The registry keys the `(?` doorway on THE CHARACTER AFTER `(?`,
 * and it has a row whose selector is `0` described as "recurse the whole
 * pattern (synonym for (?R))". A port wired to that DESCRIPTION compiles
 * `(?01)` as the root, and `^(a(?01)?b)$` on "aabb" answers NOMATCH where
 * 10.46 answers (0,4). MEASURED, on the ANCHORED discriminator, because the
 * unanchored form answers (0,4) either way:
 *
 *     ^(a(?1)?b)$    (0,4)   group 1
 *     ^(a(?01)?b)$   (0,4)   group 1     <- the whole digit run, as decimal
 *     ^(a(?001)?b)$  (0,4)   group 1
 *     ^(a(?0)?b)$    nomatch the root
 *     ^(a(?00)?b)$   nomatch the root    <- a run of zeros IS zero
 *
 * So every numeric port here re-reads THE WHOLE DIGIT RUN from the selector
 * byte, and the row that dispatched is used only to say which FAMILY the
 * construct belongs to. A RELATIVE value of zero stays error 126 in every
 * spelling (`(?-0)`, `(?+0)`, `(?-00)`, `(?+00)`).
 */

#include <ctype.h>
#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "parse/parse_mods.h"

/* Saturation, `mod_backrefs.c`'s `BR_NUMBER_MAX` for its reason: a run of
 * forty digits must not wrap into a small positive value that happens to name
 * a real group. Spelled again rather than exported because the two files'
 * accumulators are independent and a shared constant would be the only thing
 * tying them together. */
#define RC_NUMBER_MAX 1000000L

static long rc_decimal(const char *p, size_t from, size_t to)
{
    long v = 0;
    for (size_t i = from; i < to; i++) {
        v = v * 10 + (p[i] - '0');
        if (v > RC_NUMBER_MAX) return RC_NUMBER_MAX;
    }
    return v;
}

static const char *rc_strndup(Ctx *cx, const char *s, size_t len)
{
    char *q = arena_alloc(&cx->arena, len + 1);
    memcpy(q, s, len);
    q[len] = '\0';
    return q;
}

static ExtResult rc_result_node(Ast *node, size_t at, size_t end, ExtWant want)
{
    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    res.node = node;
    res.end  = end;
    return res;
}

/* THE NODE. `target` is filled here ONLY for the root (see the header); every
 * other spelling leaves it at the arena's zero and lets the resolver write it,
 * which is why `queue` and `target` are never both meaningful.
 *
 * `link` is left at the arena's `CALL_SPLICE`, which is the WRONG default in
 * the unsound direction for a recursive callee — `src/opt/callgraph.c` sets it
 * for EVERY node before the emitter runs (design §6.3: wave B+C ships the CALL
 * linkage for every site). The parser does not have the graph and must not
 * guess: "is the target in a cycle" is the eligibility question and there is
 * no cycle to see until every call is resolved. */
static Ast *rc_node(Ctx *cx, const RegRow *rw, size_t at, bool root,
                    int number, const char *name, const char *what)
{
    Ast *a = pcrec_ast_node(cx, A_CALL);
    pcrec_ast_stamp(cx, a, rw, at);
    if (root) {
        a->u.call.target = 0;
        return a;
    }
    PendingRef *pr = arena_alloc(&cx->arena, sizeof *pr);
    pr->node   = a;
    pr->kind   = PEND_CALL;
    pr->number = number;
    pr->name   = name;          /* NULL: resolve `number` */
    pr->at     = at;
    pr->what   = what;
    pr->next   = cx->pending_refs;
    cx->pending_refs = pr;
    cx->n_pending_refs++;
    return a;
}

/* Every port ends the same way: the construct is `(?...)` and its own `)` is
 * the caller's `end`. A missing one is the base grammar's own sentence, which
 * `p_group_body` would otherwise raise — but the doorway CONSUMES the whole
 * construct (check06: the port reports `end`, the caller advances), so the
 * port owns the diagnostic for its own text. */
static bool rc_close(Ctx *cx, size_t p, size_t *end)
{
    if (p >= cx->patlen || cx->pat[p] != ')') return false;
    *end = p + 1;
    return true;
}

/* ---- `(?N)` and `(?R)` (design §2.2, §2.4, §2.4a) ----------------------- */

/* `from` is the byte after the row's selector; `at` is the `(`. The SELECTOR
 * itself is at `at + 2` (`p_group_body` calls the doorway with `cx->pos` on
 * the `?`), and the digit run starts THERE rather than at `from` — §2.4a's
 * rule, and the reason this port ignores `rw->sel`'s numeric value entirely.
 */
ExtResult pcrec_rcport_num(Ctx *cx, const RegRow *rw, ExtWant want,
                           size_t at, size_t from)
{
    const char *p = cx->pat;
    const size_t n = cx->patlen;
    size_t end;

    /* `(?R)` — the ROOT, and the one spelling here with no digits at all. */
    if (rw->sel == 'R') {
        if (!rc_close(cx, from, &end))
            REFUSE(at, "(?R) must be followed by ')'");
        return rc_result_node(rc_node(cx, rw, at, true, 0, NULL, "(?R)"),
                              at, end, want);
    }

    {
        size_t ds = at + 2;                 /* the selector digit itself */
        size_t d  = ds;
        while (d < n && isdigit((unsigned char)p[d])) d++;
        /* The row is only elected on a digit selector, so the run is at least
         * one byte; the assertion is the registry's, not this port's. */
        if (d == ds)
            REFUSE(at, "internal error: (?N) port reached with no digit");
        if (!rc_close(cx, d, &end))
            REFUSE(at, "a subroutine call (?N) must be followed by ')'");

        long v = rc_decimal(p, ds, d);
        char what[40];
        snprintf(what, sizeof what, "(?%.*s)", (int)(d - ds), p + ds);
        const char *wh = rc_strndup(cx, what, strlen(what));

        /* §2.4a: the whole run as decimal, and the value ZERO is the ROOT. */
        if (v == 0)
            return rc_result_node(rc_node(cx, rw, at, true, 0, NULL, wh),
                                  at, end, want);
        return rc_result_node(rc_node(cx, rw, at, false, (int)v, NULL, wh),
                              at, end, want);
    }
}

/* ---- `(?+N)` and `(?-N)` (design §2.3, §2.4a) --------------------------- */

/* THE RELATIVE ARITHMETIC IS AT THE CALL SITE'S OWN GROUP COUNT and is stored
 * as an ABSOLUTE number, exactly as `mod_backrefs.c`'s `br_relative` stores
 * `\g{-1}`'s computed value: `-N` counts back from the most recently OPENED
 * group, `+N` forward from the next one. MEASURED (design §2.3): `^(a)(b)(?-1)$`
 * on "abb" is (0,3) — the NEAREST group to the left — and `^(?+1)(a)$` on "aa"
 * is (0,2), a call that runs group 1's pattern BEFORE group 1 does.
 *
 * A RELATIVE VALUE OF ZERO IS ERROR 126 IN EVERY SPELLING and is this port's
 * own refusal rather than the resolver's, because it is a grammar error about
 * the OFFSET rather than a question about which group the offset names —
 * `mod_backrefs.c`'s `\g{+0}` arm draws the same line for the same reason.
 * `(?-0)`, `(?-00)`, `(?+0)`, `(?+00)` all take it (design §2.4a). */
ExtResult pcrec_rcport_rel(Ctx *cx, const RegRow *rw, ExtWant want,
                           size_t at, size_t from)
{
    const char *p = cx->pat;
    const size_t n = cx->patlen;
    size_t end;
    const int sign = rw->sel == '-' ? -1 : 1;
    (void)from;

    size_t ds = at + 3;                 /* past `(?` and the sign byte */
    size_t d  = ds;
    while (d < n && isdigit((unsigned char)p[d])) d++;
    if (d == ds)
        REFUSE(at, "a digit must follow (?%c", rw->sel);
    if (!rc_close(cx, d, &end))
        REFUSE(at, "a relative subroutine call (?%cN) must be followed by ')'",
               rw->sel);

    long v = rc_decimal(p, ds, d);
    if (v == 0)
        REFUSE(at, "a relative reference of zero is not allowed");

    char what[40];
    snprintf(what, sizeof what, "(?%c%.*s)", rw->sel, (int)(d - ds), p + ds);
    const char *wh = rc_strndup(cx, what, strlen(what));

    long base = (long)cx->ncap;
    long num  = sign < 0 ? base - v + 1 : base + v;
    if (num >  RC_NUMBER_MAX) num =  RC_NUMBER_MAX;
    if (num < -RC_NUMBER_MAX) num = -RC_NUMBER_MAX;

    /* WHETHER THE RESULT NAMES A GROUP IS NOT ASKED HERE — §5.3's one deferred
     * question, `mod_backrefs.c`'s rule inherited verbatim. A backward offset
     * that lands at or below zero cannot ever name a group and could be
     * refused here; it is NOT, because splitting the check would put the
     * error-115 sentence in two places, and that split has already cost this
     * project one D65 built-status defect (see `br_node`'s own comment). Zero
     * and negative numbers reach the resolver, which owns the answer. */
    return rc_result_node(rc_node(cx, rw, at, false, (int)num, NULL, wh),
                          at, end, want);
}

/* ---- `(?&name)` and `(?P>name)` (design §2.2, §3.4(c)) ------------------ */

/* `named-groups` IS CHECKED BEFORE THE NAME GRAMMAR, `br_name_ref`'s rule and
 * its reason: without that module there is no such thing as a group NAME, so
 * every further question about the spelling is moot and "requires module
 * 'named-groups'" is the answer a caller can act on. P2 MEASURED that
 * `(?<n>a)(?&n)` under the default set refuses for `named-groups` because the
 * DECLARATION is reached first; this line is what makes `(?&n)(?<n>a)` — where
 * the CALL is reached first — give the same answer instead of a `recursion`
 * one, which is design §9.3's own masking cell. */
static ExtResult rc_name_call(Ctx *cx, const RegRow *rw, ExtWant want, size_t at,
                              const char *body, size_t blen, size_t end,
                              const char *what)
{
    if (!pcrec_feature_enabled(FEAT_NAMED_GROUPS))
        REFUSE(at, "%s names a capture group, which requires module "
                   "'named-groups'", what);
    if (blen == 0)
        REFUSE(at, "subpattern name expected in %s", what);
    if (isdigit((unsigned char)body[0]))
        REFUSE(at, "subpattern name must start with a non-digit (a subroutine "
                   "call BY NUMBER is spelled (?N) or (?+N)/(?-N))");
    {
        const char *why = NULL;
        size_t len = pcrec_group_name_scan(body, blen, 0, &why);
        if (len != blen)
            REFUSE(at, "%s", why ? why : "invalid subpattern name");
    }
    return rc_result_node(rc_node(cx, rw, at, false, 0,
                                  rc_strndup(cx, body, blen),
                                  rc_strndup(cx, what, strlen(what))),
                          at, end, want);
}

ExtResult pcrec_rcport_name(Ctx *cx, const RegRow *rw, ExtWant want,
                            size_t at, size_t from)
{
    const char *p = cx->pat;
    const size_t n = cx->patlen;
    size_t c = from;

    while (c < n && p[c] != ')') c++;
    if (c >= n)
        REFUSE(at, "missing closing ) after (?%s", rw->sel == '&' ? "&" : "P>");
    {
        char what[160];
        snprintf(what, sizeof what, "(?%s%.*s)",
                 rw->sel == '&' ? "&" : "P>", (int)(c - from), p + from);
        return rc_name_call(cx, rw, want, at, p + from, c - from, c + 1,
                            rc_strndup(cx, what, strlen(what)));
    }
}

/* ---- THE `\g<` / `\g'` ROWS ARE NOT THIS FILE'S, AND NOT YET ANYBODY'S ---
 *
 * Design §4.2 assigns the two subroutine-call `\g` tails to `pcrec_brport_g`
 * (P3: `\g` is ONE escape doorway shared between two modules and the TAIL
 * decides), and §11's wave B+C brief asks for "ONE decline branch at
 * `WANT_RESULT`" there so those rows stay `unbuilt` until wave D.
 *
 * **NO SUCH BRANCH IS NEEDED AND NONE IS WRITTEN**, and this note is the
 * record of why rather than a silent omission. The two tails are their OWN
 * REGISTRY ROWS (`src/parse/registry.c`, module `recursion`, rank 25) with
 * `aport = NO_PORT`, so `pcrec_brport_g` is NEVER REACHED for `\g<1>` or
 * `\g'1'` — the arbitration elects the tailed row and the base `\g` row's port
 * never sees the text. A row with no atom port reaching post-gate
 * `WANT_RESULT` takes ext.c's ENABLED-BUT-UNBUILT epilogue, which is exactly
 * D65's "gate open, port missing" signal, so the `built` column reads
 * `unbuilt` with no code at all. A decline branch inside `pcrec_brport_g`
 * would be unreachable code satisfying nothing.
 *
 * WAVE D's edit is therefore to WIRE those two rows' `aport` (to
 * `pcrec_brport_g`, per §4.2's one-port ruling, or to a port here), not to
 * delete a decline. */
