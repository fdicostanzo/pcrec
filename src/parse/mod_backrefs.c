/* mod_backrefs.c — module `backrefs` ([M6.5.2]): every backreference
 * spelling, PCRE2's octal disambiguation, and the end-of-parse resolution
 * pass the three of them share.
 *
 * Design: docs/design/backrefs_design.md, panel-approved at R32
 * (docs/dev/reviews/2026-08-22-r32-backrefs-design.md). Read §3.1, §5 and
 * §8.3 before touching this file; everything below is one of their rules.
 *
 * WHAT A BACKREFERENCE IS, in one sentence, because every consequence follows
 * from it: it compares SUBJECT TEXT against SUBJECT TEXT, at a pair of
 * positions the backtracking state holds at that instant. Everything else
 * pcrec compiles is a 256-bit bitmap or a position predicate, which is why
 * caselessness folds away at parse time (D23) and why the DFA can carry every
 * other construct. A backreference is neither, so it needs a new node kind
 * (`A_BREF`), a new emitted operation, the encoding seam's second residual
 * entry, and no prefilter at all.
 *
 * FOUR PORTS, ONE NODE KIND, AND ONE OF THEM ALSO PRODUCES CHARACTERS.
 * `pcrec_brport_digit` owns the ten digit rows, and PCRE2's rule 1 (`\0` is
 * always octal) and rule 3 (a multi-digit run re-read as octal when the count
 * so far does not reach it) make it the only port here that can return
 * something that is not a reference at all.
 *
 * THE STAMP GOES ON THE `A_BREF` AND NOWHERE ELSE, and that is a per-NODE
 * answer to a per-ROW question rather than a forgotten stamp (SR-8/D67
 * contract note 2 is about the UNSOUND direction; this is the sound one, and
 * it is deliberate). `\1`'s registry row is VM_ONLY, but `(a)\10` is the octal
 * byte 0x08 — an ordinary character with no VM requirement whatsoever — so
 * stamping the character node the octal re-read produces would refuse
 * `--engine=dfa '(a)\10'` for a construct that is not there. Measured both
 * ways in tests/backrefs/: `(a)\1` refuses under `--engine=dfa` naming `\1`,
 * and `(a)\10` compiles to a pure DFA. `\0`'s own row is ANY_ENGINE and
 * produces a character too, so it could be stamped harmlessly; it is not, for
 * the same reason — the octal reading is not the row's VM_ONLY construct.
 *
 * NOTHING HERE RESOLVES A REFERENCE. Every port RECORDS one (`PendingRef`,
 * core/internal.h) and `pcrec_bref_resolve` below settles all of them at end
 * of parse, which is what makes forward references legal by construction
 * rather than by an exception and what gives the numeric, relative and
 * by-name spellings ONE definition of "group k exists". The one thing that
 * cannot be deferred is rule 3's backref-vs-octal decision: deferring it would
 * let a later group retroactively turn an octal literal into a reference, and
 * `\10(a)..(j)` — measured OCTAL — is exactly that boundary.
 *
 * THE `(?J)` LETTER IS NOT HERE. It lives in mod_modifiers.c's option-run
 * dispatch, gated on FEAT_BACKREFS, because that is where every inline letter
 * lives; the duplicate CHECK it governs is mod_named_groups.c's. The split is
 * the one ASK-1 ruled and the compliance page now records: DECLARING a
 * duplicate name is `named-groups`; RESOLVING a reference to one, and the
 * letter itself, is `backrefs`. */

#include <ctype.h>
#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "parse/parse_mods.h"

/* A group number well above anything PCRE2 can declare, used to saturate the
 * decimal accumulator. A run of 40 digits must not wrap into a small positive
 * value that happens to name a real group — the same saturation discipline
 * src/opt/mrl.c applies to its own arithmetic, for the same reason. */
#define BR_NUMBER_MAX 1000000L

static long br_decimal(const char *p, size_t from, size_t to)
{
    long v = 0;
    for (size_t i = from; i < to; i++) {
        v = v * 10 + (p[i] - '0');
        if (v > BR_NUMBER_MAX) return BR_NUMBER_MAX;
    }
    return v;
}

/* ---- the node, and the pending record that outlives it ------------------ */

/* Build the `A_BREF` and queue its resolution. `name == NULL` means resolve
 * `number`, which is an absolute group number already computed — the numeric
 * and relative spellings both arrive here that way, because relative
 * resolution is a COMPILE-TIME question against the count AT THE ESCAPE
 * (§5.1 rule 5, measured in both directions: `(a)\g{-1}` is legal and
 * `(a)\g{-2}` is error 115, `\g{+1}(a)` is legal and `\g{+2}(a)` is not).
 *
 * `number` MAY BE ZERO OR NEGATIVE HERE, and that is deliberate rather than
 * sloppy: whether a computed number NAMES A GROUP is §5.3's one deferred
 * question, and answering it in two places — here for `\g{-1}` at a count of
 * zero, at end of parse for `\9` at a count of three — would be exactly the
 * second home §5.3 exists to prevent. It also showed up as a real defect: with
 * the check split, the `\g` registry row's own `syntax` (`\g{-1}`, standalone)
 * refused AT THE PORT, so D65's built-status derivation classified a construct
 * this module BUILDS as `unbuilt` and the generated compliance index would
 * have said so.
 *
 * `caseless` is read HERE, from the scoped state in force AT THE REFERENCE —
 * D62's rule, and MEASURED to be the right position: `^(a)(?i:\1)$` matches
 * "aA" while `^(?i:(a))\1$` does not. */
static Ast *br_node(Ctx *cx, const RegRow *rw, size_t at, int number,
                    const char *name, const char *what)
{
    Ast *a = pcrec_ast_node(cx, A_BREF);
    a->u.bref.caseless = cx->mods->caseless;
    pcrec_ast_stamp(cx, a, rw, at);

    PendingRef *pr = arena_alloc(&cx->arena, sizeof *pr);
    pr->node   = a;
    pr->number = number;
    pr->name   = name;   /* NULL: resolve `number` */
    pr->at     = at;
    pr->what   = what;
    pr->next   = cx->pending_refs;
    cx->pending_refs = pr;
    cx->n_pending_refs++;
    return a;
}

static ExtResult br_result_node(Ast *node, size_t at, size_t end, ExtWant want)
{
    ExtResult res = { .what = EXT_NODE, .at = at, .msg = "",
                      .answered_at = want };
    res.node = node;
    res.end  = end;
    return res;
}

/* An arena-owned NUL-terminated copy — the pending list is read long after
 * the port returned, so the name cannot be a pointer into the pattern's
 * lifetime assumptions any more than `NamedGroup.name` can. */
static const char *br_strndup(Ctx *cx, const char *s, size_t len)
{
    char *q = arena_alloc(&cx->arena, len + 1);
    memcpy(q, s, len);
    q[len] = '\0';
    return q;
}

/* ---- the digit rows: PCRE2's octal disambiguation (§5) ------------------
 *
 * FOUR ORDERED QUESTIONS, and stating them in this order is what makes rule 3'
 * fall out instead of being a special case (R32 E3 found the first draft's
 * rule 3 leaving an EMPTY octal run for an 8/9-led digit run):
 *
 *   1. does the run start with `0`?            -> OCTAL, at most three digits
 *   2. is it a single digit 1-9?               -> backref, WHOLE-pattern count
 *   3. does it have an octal reading (1-7)?    -> backref if that many groups
 *                                                 exist SO FAR, else OCTAL
 *   4. otherwise (it starts 8 or 9)            -> DECIMAL backref,
 *                                                 WHOLE-pattern count
 *
 * THE ASYMMETRY IN 2 vs 3 IS THE FINDING, and no test using only
 * groups-before will notice it: `\1`..`\9` see the WHOLE pattern (`\1(a)`
 * compiles), while `\10`+ see only what PRECEDES them (`\10(a)..(j)` is the
 * octal byte 0x08, and `(a)\10` is octal 010 rather than "group 1 then '0'").
 * Sabotage rows S112 and S113 are the two directions.
 *
 * THE OCTAL SCAN ITSELF IS NOT WRITTEN HERE. `pcrec_clsport_octal`
 * (src/parse/parse.c) is the base grammar's own measured rule — selector digit
 * plus up to two more octal digits, value <= \377, PCRE2 error 151 above with
 * the ran-out offset — and it is what the CLASS position uses. Calling it is
 * what keeps the atom and class positions from acquiring two implementations
 * of one PCRE2 fact, which is the shape §5.2 forbids the module to disturb and
 * sabotage S110 pins: with this module ENABLED every class cell must stay
 * byte-identical to the base tier's answer. */
ExtResult pcrec_brport_digit(Ctx *cx, const RegRow *rw, ExtWant want,
                             size_t at, size_t from)
{
    const char *p = cx->pat;
    const size_t n = cx->patlen;
    const int d0 = rw->sel - '0';

    size_t runend = from;
    while (runend < n && p[runend] >= '0' && p[runend] <= '9') runend++;
    const size_t runlen = 1 + (runend - from);
    const size_t runstart = from - 1;   /* the selector digit itself */

    /* Q1 — rule 1. `\0` is ALWAYS octal and can never be a backreference:
     * there is no group 0 to address, so no ambiguity exists. `(a)\0` is still
     * octal with a group in scope. */
    if (d0 == 0) goto octal;

    /* Q2 and Q4 — rules 2 and 3'. Both take the WHOLE-pattern count, which is
     * why both defer. `\8` and `\9` are in rule 2 and are neither octal nor
     * literal; a run BEGINNING 8 or 9 has no octal reading at all (8 and 9 are
     * not octal digits, so the re-read would consume zero digits and produce
     * nothing), so PCRE2 reads the whole decimal number instead. */
    if (runlen == 1 || d0 >= 8) {
        long v = br_decimal(p, runstart, runend);
        char what[32];
        snprintf(what, sizeof what, "\\%.*s", (int)(runend - runstart),
                 p + runstart);
        return br_result_node(br_node(cx, rw, at, (int)v, NULL,
                                      br_strndup(cx, what, strlen(what))),
                              at, runend, want);
    }

    /* Q3 — rule 3. The count SO FAR (`Ctx.ncap` at this escape), never the
     * total: this is the one decision §5.3 may not defer. */
    {
        long v = br_decimal(p, runstart, runend);
        if (v >= 1 && v <= (long)cx->ncap) {
            char what[32];
            snprintf(what, sizeof what, "\\%.*s", (int)(runend - runstart),
                     p + runstart);
            return br_result_node(br_node(cx, rw, at, (int)v, NULL,
                                          br_strndup(cx, what, strlen(what))),
                                  at, runend, want);
        }
    }

octal: {
        /* The re-read. Whatever digits the octal scan does not consume stand
         * for themselves — `(a)\18` is octal `\01` then a literal `'8'` — and
         * that falls out of the port reporting its own `end` rather than
         * needing a rule here. */
        ExtResult oct = pcrec_clsport_octal(cx, rw, want, at, from);
        if (oct.what != EXT_SCALAR) return oct;    /* the > \377 refusal */
        return br_result_node(pcrec_ast_char(cx, (unsigned)oct.scalar),
                              at, oct.end, want);
    }
}

/* ---- the by-name spellings' shared tail --------------------------------- */

/* HT and SP — and ONLY those two — are skipped at both ends of a `\g{...}` or
 * `\k{...}` body. MEASURED over all 256 bytes in both positions (the
 * angle-bracket, quote and `(?P=` forms skip NOTHING: `\k< n >`, `\k' n '` and
 * `(?P= n )` are all PCRE2 errors while `\k{ n }` is legal). Written as a
 * two-byte set rather than reusing the x-mode skip set, which is a different
 * and larger set for a different reason. */
static bool br_brace_space(int c) { return c == ' ' || c == '\t'; }

/* THE RELATIVE ARITHMETIC, and only the arithmetic (§5.1 rule 5): `-N` counts
 * back from the most recently OPENED group, `+N` forward from the next one.
 * Both are computed against `Ctx.ncap` AT THIS ESCAPE, which is what makes
 * `\g{+1}(a)` legal and `\g{+2}(a)` not.
 *
 * WHETHER THE RESULT NAMES A GROUP IS NOT ASKED HERE. A number out of range —
 * including zero and negative, which `\g{-1}` at a count of zero produces — is
 * carried to §5.3's single resolution site like any other. The saturation is
 * for the arithmetic's own sake, so a pathological `+999999999` cannot wrap
 * into a small positive value that happens to name a real group. */
static long br_relative(Ctx *cx, int sign, long v)
{
    long base = (long)cx->ncap;
    long num  = sign < 0 ? base - v + 1 : base + v;
    if (num > BR_NUMBER_MAX) num = BR_NUMBER_MAX;
    if (num < -BR_NUMBER_MAX) num = -BR_NUMBER_MAX;
    return num;
}

/* The name branch of `\g{...}`, `\k<...>` and `(?P=...)`. `named-groups` is
 * checked BEFORE the name grammar, deliberately: without that module there is
 * no such thing as a group NAME, so every further question about the spelling
 * is moot and "requires module 'named-groups'" is the answer that tells the
 * caller something they can act on. §10's matrix pins both cells — under
 * `--features backrefs` alone `\k<n>` refuses naming `named-groups`, and with
 * both modules on it refuses as an undeclared name. */
static ExtResult br_name_ref(Ctx *cx, const RegRow *rw, ExtWant want, size_t at,
                             const char *body, size_t blen, size_t end,
                             const char *what)
{
    if (!pcrec_feature_enabled(FEAT_NAMED_GROUPS))
        REFUSE(at, "%s names a capture group, which requires module "
                   "'named-groups'", what);
    if (blen == 0)
        REFUSE(at, "subpattern name expected after %s", what);
    if (isdigit((unsigned char)body[0]))
        REFUSE(at, "subpattern name must start with a non-digit (a "
                   "backreference BY NUMBER is spelled \\N or \\g{N})");
    {
        const char *why = NULL;
        size_t len = pcrec_group_name_scan(body, blen, 0, &why);
        if (len != blen)
            REFUSE(at, "%s", why ? why : "invalid subpattern name");
    }
    return br_result_node(br_node(cx, rw, at, 0, br_strndup(cx, body, blen),
                                  br_strndup(cx, what, strlen(what))),
                          at, end, want);
}

/* ---- `\g` (§2): the BACKREFERENCE half of a doorway that carries two -----
 *
 * `\g<name>` and `\g'name'` are SUBROUTINE CALLS, not backreferences — a
 * subroutine call re-runs the group's PATTERN, so `^(a|b)\g<1>$` matches "ab",
 * while `^(a|b)\g{1}$` and `^(a|b)\g1$` compare the captured TEXT and report
 * no match on the same subject (measured discriminator, §2). The split runs
 * exactly along the DELIMITER, and it is the REGISTRY that enforces it: two
 * `RK_ESC` rows with tails `<` and `'` and module `recursion` outrank this
 * row, so this port is never reached for either spelling. That is the same
 * arbitration `(?P=` / `(?P>` already uses, and the same shape `\N{` / `\N{U+`
 * measured before it. */
ExtResult pcrec_brport_g(Ctx *cx, const RegRow *rw, ExtWant want,
                         size_t at, size_t from)
{
    const char *p = cx->pat;
    const size_t n = cx->patlen;

    if (from >= n)
        REFUSE(at, "\\g must be followed by a number, a relative offset, or a "
                   "braced name or number");

    if (p[from] == '{') {
        size_t close = from + 1;
        while (close < n && p[close] != '}') close++;
        if (close >= n)
            REFUSE(at, "missing closing } after \\g{");
        size_t b = from + 1, e = close;
        while (b < e && br_brace_space((unsigned char)p[b])) b++;
        while (e > b && br_brace_space((unsigned char)p[e - 1])) e--;
        if (b == e)
            REFUSE(at, "subpattern name or number expected after \\g{");

        int sign = 0;
        size_t d = b;
        if (p[d] == '-') { sign = -1; d++; }
        else if (p[d] == '+') { sign = 1; d++; }

        if (sign != 0 || isdigit((unsigned char)p[d])) {
            if (d == e)
                REFUSE(at, "a number must follow the sign in \\g{}");
            for (size_t i = d; i < e; i++)
                if (!isdigit((unsigned char)p[i]))
                    REFUSE(at, "\\g{} takes a number, a relative offset, or a "
                               "subpattern name, not a mixture");
            long v = br_decimal(p, d, e);
            long num;
            if (sign == 0) {
                num = v;
            } else {
                /* A relative offset of ZERO is a grammar error about the
                 * OFFSET rather than a question about which group it names
                 * (PCRE2 error 126, a different number from 115's), so it is
                 * the one refusal this branch still makes itself. */
                if (v == 0)
                    REFUSE(at, "a relative reference of zero is not allowed");
                num = br_relative(cx, sign, v);
            }
            char what[32];
            snprintf(what, sizeof what, "\\g{%.*s}", (int)(e - b), p + b);
            return br_result_node(br_node(cx, rw, at, (int)num, NULL,
                                          br_strndup(cx, what, strlen(what))),
                                  at, close + 1, want);
        }
        {
            char what[32];
            snprintf(what, sizeof what, "\\g{%.*s}", (int)(e - b), p + b);
            return br_name_ref(cx, rw, want, at, p + b, e - b, close + 1,
                               br_strndup(cx, what, strlen(what)));
        }
    }

    /* The BARE forms `\g1`, `\g-1`, `\g+1`. Measured: `\g+1` really is a
     * relative FORWARD reference (`(a)\g+1(b)` compiles and `(a)\g+1` is
     * error 115), and a bare number is decimal with leading zeros allowed
     * (`\g01` is group 1, `\g00` is error 115). */
    {
        int sign = 0;
        size_t d = from;
        if (p[d] == '-') { sign = -1; d++; }
        else if (p[d] == '+') { sign = 1; d++; }
        size_t ds = d;
        while (d < n && isdigit((unsigned char)p[d])) d++;
        if (d == ds)
            REFUSE(at, "\\g must be followed by a number, a relative offset, "
                       "or a braced name or number");
        long v = br_decimal(p, ds, d);
        long num;
        if (sign == 0) {
            num = v;
        } else {
            if (v == 0)
                REFUSE(at, "a relative reference of zero is not allowed");
            num = br_relative(cx, sign, v);
        }
        char what[32];
        snprintf(what, sizeof what, "\\g%.*s", (int)(d - from), p + from);
        return br_result_node(br_node(cx, rw, at, (int)num, NULL,
                                      br_strndup(cx, what, strlen(what))),
                              at, d, want);
    }
}

/* ---- `\k<n>` `\k'n'` `\k{n}` (§2) --------------------------------------
 *
 * ALWAYS by name. `\k<1>` and `\k{1}` are PCRE2 error 144 ("a name may not
 * start with a digit") and `\kn` is error 169 ("a delimiter is required"), so
 * there is no numeric spelling of `\k` to support and the module gate for
 * `named-groups` covers every form. */
ExtResult pcrec_brport_k(Ctx *cx, const RegRow *rw, ExtWant want,
                         size_t at, size_t from)
{
    const char *p = cx->pat;
    const size_t n = cx->patlen;
    int close;

    if (from >= n)
        REFUSE(at, "\\k must be followed by a name in <>, '' or {}");
    switch (p[from]) {
    case '<':  close = '>';  break;
    case '\'': close = '\''; break;
    case '{':  close = '}';  break;
    default:
        REFUSE(at, "\\k must be followed by a name in <>, '' or {}");
    }
    size_t c = from + 1;
    while (c < n && p[c] != close) c++;
    if (c >= n)
        REFUSE(at, "missing closing %c after \\k%c", close, p[from]);
    size_t b = from + 1, e = c;
    if (close == '}') {
        while (b < e && br_brace_space((unsigned char)p[b])) b++;
        while (e > b && br_brace_space((unsigned char)p[e - 1])) e--;
    }
    {
        char what[32];
        snprintf(what, sizeof what, "\\k%c%.*s%c", p[from], (int)(e - b),
                 p + b, close);
        return br_name_ref(cx, rw, want, at, p + b, e - b, c + 1,
                           br_strndup(cx, what, strlen(what)));
    }
}

/* ---- `(?P=name)` (§2) --------------------------------------------------
 *
 * The python spelling, and the ONE by-name form python `re` also has — which
 * makes it the only `\k`-class row in this module with a base-tier oracle.
 * `from` is the byte after the `=`. */
ExtResult pcrec_brport_pname(Ctx *cx, const RegRow *rw, ExtWant want,
                             size_t at, size_t from)
{
    const char *p = cx->pat;
    const size_t n = cx->patlen;
    size_t c = from;

    while (c < n && p[c] != ')') c++;
    if (c >= n)
        REFUSE(at, "missing closing ) after (?P=");
    {
        char what[32];
        snprintf(what, sizeof what, "(?P=%.*s)", (int)(c - from), p + from);
        return br_name_ref(cx, rw, want, at, p + from, c - from, c + 1,
                           br_strndup(cx, what, strlen(what)));
    }
}

/* ---- the END-OF-PARSE PASS (§5.3, §8.3, §6.3) --------------------------- */

/* §8.3's RESOLUTION RULE, as the SET the emitted chain walks.
 *
 * MEASURED over eighteen cells designed to separate four candidate rules: the
 * reference takes the FIRST member of the name's run, IN ASCENDING GROUP
 * NUMBER, THAT IS SET. Not the first by number unconditionally (the "yy" cell:
 * `(?J)^(?:(?<a>x)|(?<a>y))\k<a>$` matches "yy", #1 unset and #2 used), not
 * the LAST set (the "xyy" cell: `(?J)^(?<a>x)(?<a>y)\k<a>$` matches "xyx" and
 * NOT "xyy"), not "any of them" (the "xy"/"yx" cells). "Set" includes set to
 * the EMPTY string.
 *
 * The CHOICE is made at MATCH time, so what this pass computes is the whole
 * run in ascending number and the emitted else-if chain does the choosing —
 * which is also why §3.2.4's marked set must contain EVERY member (R32
 * re-check E13): the chain reads them all.
 *
 * PCRE2 does NOT retry later members when the first SET one's compare fails,
 * which is what makes a frame-free chain the right emitted shape rather than a
 * choice point — measured by the R32 panel on its own battery. */
static void br_name_run(Ctx *cx, const char *name, int **out, int *nout)
{
    int count = 0;
    for (const NamedGroup *g = cx->named_groups; g; g = g->next)
        if (strcmp(g->name, name) == 0) count++;
    if (count == 0) { *out = NULL; *nout = 0; return; }

    int *v = arena_alloc(&cx->arena, (size_t)count * sizeof *v);
    int k = 0;
    for (const NamedGroup *g = cx->named_groups; g; g = g->next)
        if (strcmp(g->name, name) == 0) v[k++] = g->number;
    /* ASCENDING, by insertion sort over a run that is a handful of entries in
     * any realistic pattern. `Ctx.named_groups` is PREPENDED at declaration
     * (mod_named_groups.c), so the walk above delivers DESCENDING numbers and
     * "it is already sorted" would be exactly wrong. */
    for (int i = 1; i < count; i++) {
        int t = v[i], j = i - 1;
        while (j >= 0 && v[j] > t) { v[j + 1] = v[j]; j--; }
        v[j + 1] = t;
    }
    *out = v;
    *nout = count;
}

/* Splice out the `A_CAP` wrapper of every group `keep[]` does not mark. Only
 * ever called on a `--no-captures` build — see `pcrec_bref_resolve`. Returns
 * the (possibly new) subtree root.
 *
 * Both spines are walked ITERATIVELY (D10/DD-10): a flat concatenation is as
 * long as the pattern, and this project has paid for that lesson three times. */
static Ast *br_strip_caps(Ast *a, const bool *keep, int nkeep)
{
    for (;;) {
        switch (a->k) {
        case A_CLASS: case A_EMPTY: case A_BOL: case A_EOL: case A_END:
        case A_WORDB: case A_NWORDB: case A_GSTART: case A_KRESET:
        case A_BREF:
            return a;
        case A_CAP:
            a->l = br_strip_caps(a->l, keep, nkeep);
            if (a->u.cap.no > 0 && a->u.cap.no < nkeep && keep[a->u.cap.no]) return a;
            a = a->l;
            continue;
        case A_REP: case A_ATOMIC:
            a->l = br_strip_caps(a->l, keep, nkeep);
            return a;
        case A_CAT:
            for (Ast *t = a; t->k == A_CAT; t = t->l)
                t->r = br_strip_caps(t->r, keep, nkeep);
            {
                Ast *t = a;
                while (t->l->k == A_CAT) t = t->l;
                t->l = br_strip_caps(t->l, keep, nkeep);
            }
            return a;
        case A_ALT:
            for (Ast *t = a; t->k == A_ALT; t = t->l)
                t->r = br_strip_caps(t->r, keep, nkeep);
            {
                Ast *t = a;
                while (t->l->k == A_ALT) t = t->l;
                t->l = br_strip_caps(t->l, keep, nkeep);
            }
            return a;
        }
        return a;
    }
}

Ast *pcrec_bref_resolve(Ctx *cx, Ast *root)
{
    /* THE EARLY RETURN IS ON THE RESOLUTION HALF ONLY, and putting it in front
     * of BOTH halves was a real defect this module's own byte-identity gate
     * caught: a backref-FREE pattern has no pending references, so the strip
     * below never ran and every `--no-captures` artifact with a group kept the
     * `A_CAP` wrappers the parser now builds unconditionally. The answers were
     * unaffected — that is what makes it the kind of defect only an identity
     * sweep sees — but the emitted C moved for every such pattern, which is
     * exactly the claim §11.3 exists to make. */
    if (cx->pending_refs) {
    /* THE LEFTMOST FAILURE IS THE ONE REPORTED. The list is prepended, so it
     * is in reverse source order; a compile that has more than one bad
     * reference should name the first one a reader would reach. */
    const PendingRef *worst = NULL;
    for (PendingRef *pr = cx->pending_refs; pr; pr = pr->next) {
        if (!pr->name) {
            if (pr->number >= 1 && (unsigned long)pr->number <= cx->ncap) {
                int *v = arena_alloc(&cx->arena, sizeof *v);
                v[0] = pr->number;
                pr->node->u.bref.refs  = v;
                pr->node->u.bref.nrefs = 1;
                continue;
            }
        } else {
            int *v = NULL, nv = 0;
            br_name_run(cx, pr->name, &v, &nv);
            if (nv > 0) {
                pr->node->u.bref.refs  = v;
                pr->node->u.bref.nrefs = nv;
                continue;
            }
        }
        if (!worst || pr->at < worst->at) worst = pr;
    }
    if (worst) {
        if (!worst->name)
            ctx_fail(cx, worst->at,
                     "%s refers to capture group %d, but this pattern has %u",
                     worst->what, worst->number, cx->ncap);
        ctx_fail(cx, worst->at,
                 "%s refers to a capture group named '%s', which this pattern "
                 "does not declare", worst->what, worst->name);
    }
    }

    /* §6.3's `--no-captures` RULING. The flag drops the group slots a CALLER
     * can see, not the machinery a match needs — `\K`'s precedent exactly. So
     * a group some reference names keeps its `A_CAP` (and, at emission, its
     * three internal slots); every other one loses the wrapper it was given,
     * which restores the tree a `--no-captures` parse has always produced.
     *
     * A pattern with no reference marks NOTHING, so every wrapper goes and the
     * tree is what a `--no-captures` parse has always produced — which is the
     * stronger half of the same claim, and the half the early return above
     * used to skip. */
    if (!cx->want_caps && cx->ncap > 0) {
        int nkeep = (int)cx->ncap + 1;
        bool *keep = arena_alloc(&cx->arena, (size_t)nkeep * sizeof *keep);
        memset(keep, 0, (size_t)nkeep * sizeof *keep);
        pcrec_bref_mark(root, keep, nkeep);
        root = br_strip_caps(root, keep, nkeep);
    }
    return root;
}
