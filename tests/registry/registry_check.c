/* tests/registry/registry_check.c — the syntax registry against the parser.
 *
 * WHY THIS EXISTS. SR-1 adds a declarative table describing every non-base
 * construct. A table that merely SITS THERE is not an improvement over the
 * five scattered copies it replaces — it is a sixth copy, and the newest one,
 * so it drifts first. `\v` shipped wrong precisely because two descriptions of
 * one construct sat ten lines apart with nothing checking that they agreed.
 * This file is that check, and it runs before SR-2 makes the parser consume
 * the table, so the table is proved faithful BEFORE it becomes load-bearing.
 *
 * It asserts in BOTH directions, which matters:
 *
 *   table -> parser   every row's `syntax` really is rejected (or accepted)
 *                     by the shipped compiler, with the EXACT diagnostic the
 *                     row describes. Substring matching would let a row claim
 *                     the wrong module and pass.
 *
 *   parser -> table   a 255-byte sweep of each doorway: if the parser says
 *                     "requires module" for a byte, a row MUST exist for it and
 *                     MUST name the same module. This is the direction that
 *                     catches a construct added to parse.c with no row — the
 *                     drift that produced `\v`. The first direction alone
 *                     cannot see it.
 *
 * The probe patterns come from each row's `syntax` field rather than from a
 * hand-written list, so a new row covers itself with no edit here. That is
 * safe because this is a CONFORMANCE check between two descriptions, not a
 * control: it is not asserting that the rejection is CORRECT, only that the
 * table and the parser say the same thing. Whether the rejection is correct is
 * tests/reject/'s job, and its accept-controls stay hand-written for exactly
 * the reason this file does not need to (SR-4).
 *
 * Build/run: bash tests/registry/run_registry_tests.sh */

#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "core/internal.h"

static int pass = 0, fail = 0;

static void ok(const char *what)  { printf("PASS: %s\n", what); pass++; }
static void bad(const char *fmt, ...) __attribute__((format(printf, 1, 2)));
static void bad(const char *fmt, ...)
{
    va_list ap;
    fflush(stdout);   /* stderr is unbuffered and stdout is not: without this a
                         PASS line and a FAIL line splice together when the
                         output is piped, and the spliced FAIL stops matching a
                         line-anchored grep. Found by sabotage-validating this
                         file, which is the sort of thing sabotage runs are for. */
    fputs("FAIL: ", stderr);
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    va_end(ap);
    fputc('\n', stderr);
    fail++;
}

/* Compile `pat`; return 0 on success, -1 on failure with the diagnostic in
 * `msg` (which is exactly pcrec_error.msg — no CLI decoration). */
static int try_compile(const char *pat, char *msg, size_t msgsz)
{
    pcrec_options opt;
    pcrec_output  out;
    pcrec_error   err;
    int rc;

    pcrec_default_options(&opt);
    memset(&out, 0, sizeof out);
    memset(&err, 0, sizeof err);

    rc = pcrec_compile(pat, &opt, &out, &err);
    if (rc == 0) { pcrec_output_free(&out); return 0; }
    snprintf(msg, msgsz, "%s", err.msg);
    return -1;
}

/* Assert that `pat` fails with EXACTLY `want`. */
static void expect_msg(const char *label, const char *pat, const char *want)
{
    char got[256];
    if (try_compile(pat, got, sizeof got) == 0) {
        bad("%s: '%s' COMPILED; expected the rejection \"%s\"", label, pat, want);
        return;
    }
    if (strcmp(got, want) != 0) {
        bad("%s: '%s'\n        want: \"%s\"\n        got:  \"%s\"", label, pat, want, got);
        return;
    }
    ok(label);
}

static void expect_compiles(const char *label, const char *pat)
{
    char got[256];
    if (try_compile(pat, got, sizeof got) != 0) {
        bad("%s: '%s' was REJECTED (\"%s\"); the table says it is supported", label, pat, got);
        return;
    }
    ok(label);
}

/* ---- part 1: the table is well-formed ---------------------------------- */

static const char *kind_name(RegKind k)
{
    switch (k) {
    case RK_ESC:          return "esc";
    case RK_GROUP:        return "group";
    case RK_VERB:         return "verb";
    case RK_CLASSBRACKET: return "classbracket";
    case RK_QUANTSUFFIX:  return "quantsuffix";
    default:              return "?";
    }
}

/* `sel_offset` lived here and is gone at SR-9. It returned a FIXED offset at
 * which a row's selector byte had to sit, which no longer holds: `(?-2)` needs
 * leading groups to compile under libpcre2, so its example is `(a)(a)(?-2)` and
 * the selector is at offset 8. check_wellformed now builds the row's whole
 * doorway text — prefix, selector and tail — and requires the example to
 * CONTAIN it, which also checks the tail the old offset test could not see. */

static void check_wellformed(void)
{
    size_t total = 0;

    for (int k = 0; k < RK_COUNT; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry((RegKind)k, &n);
        int nany = 0;
        char label[128];

        if (!rows || n == 0) { bad("kind %s: no rows", kind_name((RegKind)k)); continue; }
        total += n;

        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            const char *kn = kind_name((RegKind)k);

            if (r->kind != (RegKind)k)
                bad("%s row %zu: kind field says %s", kn, i, kind_name(r->kind));
            if (!r->syntax || !*r->syntax) bad("%s row %zu: empty syntax", kn, i);
            if (!r->note   || !*r->note)   bad("%s row %zu (%s): empty note", kn, i, r->syntax);
            if (!(r->flavours & FLAV_PCRE2))
                bad("%s row %zu (%s): not in the PCRE2 flavour; exactly one flavour exists today",
                    kn, i, r->syntax);

            /* K14 / design §17.2: the roadmap column's legal pairings, and
             * only these. ROADMAP_NONE is "unset" — legal exactly where the
             * question does not arise. */
            if (r->status == RS_BASE && r->roadmap != ROADMAP_NONE)
                bad("%s row %zu (%s): an RS_BASE row carries a roadmap value — supported "
                    "syntax has no disposition to declare", kn, i, r->syntax);
            if (r->status == RS_MODULE && r->roadmap == ROADMAP_NONE)
                bad("%s row %zu (%s): an RS_MODULE row must declare ROADMAP_PLANNED or "
                    "ROADMAP_NEVER — an unset value would silently read as a promise",
                    kn, i, r->syntax);
            if (r->status == RS_REJECTED && r->roadmap != ROADMAP_NEVER)
                bad("%s row %zu (%s): an RS_REJECTED row must pair with ROADMAP_NEVER — "
                    "PCRE2 rejects it too, so there is nothing a module could ever "
                    "implement (§17.2's required pairing)", kn, i, r->syntax);

            /* MOD-0.1 slice 2: the quantifiable column's legal pairings.
             * VALUES are checked against libpcre2 by tests/spec_mod0/check10;
             * what this asserts is only the shape — EVERY row carries one
             * (including RS_BASE: quantifiability is a real fact about
             * supported syntax, unlike roadmap), and the form-resolved value
             * is legal exactly where a family measurably spans both verdicts
             * (the option-run rows and the verb row — design §18.3). */
            if (r->quant == QF_NONE)
                bad("%s row %zu (%s): no quantifiable value — unset would silently "
                    "read as a fact, and unlike roadmap the question is real "
                    "for BASE rows too (a(?:...)* compiles; check10 demands an "
                    "answer for all 100)", kn, i, r->syntax);
            /* RF_OPTION_RUN retired at MOD-0.5b: the option-run family is now
             * identified by its row's `recognise` pointer (a MARKER identity,
             * not the check itself — see mod_modifiers.c) rather than a flag.
             * Moved with the surface, not deleted. */
            if (r->quant == QF_FORM &&
                r->recognise != pcrec_registry_option_run_recognise && r->kind != RK_VERB)
                bad("%s row %zu (%s): QF_FORM outside the two form-resolved "
                    "families (option-run rows, the verb row)", kn, i, r->syntax);

            /* MOD-0.1 slice 4 (design §13.3): the LEXICAL row kind, tied to
             * the measured column so the two homes cannot drift. RF_LEXICAL
             * is pcrec's own taxonomy (locus: the construct is lexer-owned;
             * no class port, no AST port when ports land) and no outside
             * authority can check a taxonomy — but its MEMBERSHIP criterion
             * is §13.3(d)'s, which is exactly what the quantifiable column
             * already measures: quantifying the syntax creates no quantifier
             * for the construct. So the flag must appear on precisely the
             * QF_LEXICAL rows, both directions — a fourth lexical construct
             * would arrive with a measured QF_LEXICAL cell (check10's sweep)
             * and this pairing would demand the flag the same day. */
            if ((r->flags & RF_LEXICAL) && r->quant != QF_LEXICAL)
                bad("%s row %zu (%s): RF_LEXICAL but quantifiable is not "
                    "'lexical' — the row kind claims a lexer-owned construct "
                    "the measured column does not see", kn, i, r->syntax);
            if (!(r->flags & RF_LEXICAL) && r->quant == QF_LEXICAL)
                bad("%s row %zu (%s): quantifiable='lexical' but the row does "
                    "not carry RF_LEXICAL — a measured lexical-mode construct "
                    "must be declared as the LEXICAL row kind (§13.3)",
                    kn, i, r->syntax);

            /* MOD-0.1 slice 3: the class_expect column's legal shape. VALUES
             * are checked against a live libpcre2 oracle by
             * tests/spec_mod0/check04; what this asserts is the pairing and
             * the vocabulary — the 44 class-reachable rows (kind esc or
             * class-bracket) each carry one, the 56 group/verb rows carry
             * NONE (`(` inside a class is an ordinary member, so a value
             * there is an invented fact), and a carried value must be one of
             * the three observable forms, because a cell outside the
             * vocabulary cannot be checked by anything. */
            {
                int reachable = (r->kind == RK_ESC || r->kind == RK_CLASSBRACKET);
                if (reachable && (!r->class_expect || !*r->class_expect))
                    bad("%s row %zu (%s): no class_expect value — every esc/"
                        "class-bracket row can reach a class position and must "
                        "state its measured expectation", kn, i, r->syntax);
                if (!reachable && r->class_expect)
                    bad("%s row %zu (%s): a group/verb row carries a "
                        "class_expect value ('%s') — the construct cannot reach "
                        "a class position, so the value is an invented fact",
                        kn, i, r->syntax, r->class_expect);
                if (reachable && r->class_expect) {
                    const char *ce = r->class_expect;
                    int n = -1, b = -1;
                    char trail = 0;
                    int ok = (sscanf(ce, "err %d%c", &n, &trail) == 1 && n > 0)
                          || (sscanf(ce, "set %d%c", &n, &trail) == 1 && n >= 0)
                          || (sscanf(ce, "char 0x%2x%c", &b, &trail) == 1 &&
                              strlen(ce) == 9);
                    if (!ok)
                        bad("%s row %zu (%s): class_expect '%s' is not in the "
                            "vocabulary {\"err N\", \"char 0xNN\", \"set N\"}",
                            kn, i, r->syntax, ce);
                }
            }

            /* [M6.6.2 wave F] AN INDEX ROW IS NOT A CATCH-ALL, and the two
             * are told apart by the flag rather than by the selector.
             * REG_SEL_ANY on an RF_INDEX row means "no byte selects me",
             * which is the opposite claim to "every byte selects me":
             * `pcrec_registry_arbitrate` skips such a row before it reaches
             * the catch-all arm at all (D71 item 3), so it can neither BE the
             * kind's catch-all nor displace one. `check_index_rows` asserts
             * that against the engine's own dispatch; what this arm must do
             * is stop counting them, or twelve rows that can never be reached
             * would read as twelve unreachable catch-alls. */
            if ((r->flags & RF_INDEX) != 0) {
                /* nothing to check here — see check_index_rows */
            } else if (r->sel == REG_SEL_ANY) {
                nany++;
                if (i != n - 1)
                    bad("%s row %zu (%s): the catch-all row must be LAST — as a "
                        "READABILITY invariant, not a correctness one (R6 F8: "
                        "moving it to first position leaves dispatch unchanged, "
                        "because find() returns an exact match immediately and "
                        "only falls back to the catch-all after the full scan)",
                        kn, i, r->syntax);
            } else {
                /* The row's example must really contain its own DOORWAY TEXT —
                 * the doorway prefix, the selector byte, and (SR-9) the tail.
                 *
                 * This was a fixed OFFSET until SR-9, which could not survive a
                 * row whose probe needs leading context: `(?-2)` is a relative
                 * subroutine call and its syntax has to be `(a)(a)(?-2)` for
                 * libpcre2 to compile it at all, so the selector is at offset 8.
                 * Searching for the constructed needle is strictly stronger than
                 * the old offset test, because it checks the TAIL too — a row
                 * claiming tail "=" whose example writes "<" now fails here
                 * rather than in whichever differential noticed later. */
                char needle[32];
                if (k == RK_QUANTSUFFIX) {
                    /* [M6.4.2] THERE IS NO DOORWAY PREFIX, so the invariant is
                     * the same one stated for the construct itself: a
                     * possessive suffix is a QUANTIFIER — whose first byte is
                     * this row's selector — followed by `+`, and the row's
                     * `syntax` must END with that pair. Ending, not merely
                     * containing, because `syntax` is EXECUTED by
                     * tests/reject/run_reject_tests.sh: a trailing atom after
                     * the suffix would still refuse and would still contain the
                     * needle while testing a longer pattern than the row
                     * describes.
                     *
                     * The brace family is spelled by its CLOSER: the selector
                     * is `{` (what `p_rep` dispatches on) and the `+` attaches
                     * after the `}`, so `a{1,2}+` must end "}+" and must
                     * contain a `{`. */
                    const char *end = r->sel == '{' ? "}+" : NULL;
                    char two[3];
                    if (!end) { two[0] = (char)r->sel; two[1] = '+'; two[2] = 0; end = two; }
                    size_t sl = strlen(r->syntax), nl = strlen(end);
                    snprintf(needle, sizeof needle, "%s", end);
                    if (sl < nl || strcmp(r->syntax + sl - nl, end) != 0 ||
                        !strchr(r->syntax, r->sel))
                        bad("%s row %zu (%s): the example is not this row's own "
                            "construct — it must contain the selector '%c' and "
                            "END with \"%s\"", kn, i, r->syntax, r->sel, end);
                } else {
                const char *pfx = k == RK_ESC ? "\\" : k == RK_GROUP ? "(?" : "[";
                snprintf(needle, sizeof needle, "%s%c%s", pfx, r->sel, r->tail ? r->tail : "");
                if (!strstr(r->syntax, needle))
                    bad("%s row %zu (%s): the example does not contain its own doorway text \"%s\"",
                        kn, i, r->syntax, needle);
                }
                /* Uniqueness is over the (sel, tail) PAIR since SR-9. Two rows
                 * MAY share a byte — that is the whole point of the tail — but
                 * two rows with the same byte AND the same tail are
                 * indistinguishable, and find() would silently answer whichever
                 * the scan reached first. The design doc calls this "stronger
                 * than today" and it is: the old check could not have caught two
                 * identical `(?P<` rows, because neither existed to collide. */
                /* [DD-14 wave F] AN INDEX ROW CANNOT COLLIDE, because it
                 * is never elected: `pcrec_registry_arbitrate` skips
                 * RF_INDEX before any arm runs (D71 item 3), so two rows
                 * sharing a (sel, tail) is only a defect when BOTH can be
                 * answered with. Module `recursion`'s index rows record the
                 * byte their spelling really enters at — `(?10)` at the `1`
                 * bucket, `\g<0>` at `\g` — which is the honest value and
                 * deliberately the same byte their primary claims. Skipping
                 * them here is the flag's contract, not an exemption:
                 * check_index_rows asserts the non-election against the
                 * ENGINE, over every (kind x selector x text). */
                if ((r->flags & RF_INDEX) != 0) continue;
                for (size_t j = 0; j < i; j++) {
                    if (rows[j].sel != r->sel) continue;
                    if ((rows[j].flags & RF_INDEX) != 0) continue;
                    bool same_tail = (!rows[j].tail && !r->tail) ||
                                     (rows[j].tail && r->tail &&
                                      strcmp(rows[j].tail, r->tail) == 0);
                    if (same_tail)
                        bad("%s: rows %zu and %zu both claim byte '%c' with tail %s%s%s "
                            "— indistinguishable, so lookup answers whichever comes first",
                            kn, j, i, r->sel,
                            r->tail ? "\"" : "", r->tail ? r->tail : "(none)", r->tail ? "\"" : "");
                }
            }

            /* `open_msg` is the class-open diagnostic (FIX-2/K3). Two things
             * make it well-formed, and both are cheap to get wrong: it is
             * meaningless outside the class-bracket doorway, and its whole
             * purpose is to NOT promise a module — a row that names one there
             * would be the over-promise the field exists to remove. */
            if (r->open_msg && r->kind != RK_CLASSBRACKET)
                bad("%s (%s): open_msg is only meaningful at the class-bracket "
                    "doorway, where a class's own bracket can be the opener", kn, r->syntax);
            if (r->open_msg && strstr(r->open_msg, "requires module"))
                bad("%s (%s): open_msg names a module (\"%s\"). At a class's own "
                    "bracket the construct is invalid in PCRE2, so no module can "
                    "make it legal and promising one is the bug this field fixes",
                    kn, r->syntax, r->open_msg);

            /* TWO PROPERTIES THE DOORWAY'S CODE RELIES ON AND CANNOT ASSERT
             * ITSELF, both added at R9 after critics showed each held by
             * accident rather than by construction.
             *
             * 1. No class-bracket row may use `]` as its selector. The scan in
             *    `pcrec_ext_class_bracket` treats "an unescaped `]` ends the
             *    class" and "delimiter followed by `]` closes the pair" as
             *    disjoint tests, which is only true while no delimiter IS `]`.
             *    A `]` row would make the two rules fight, and which won would
             *    depend on their order in the loop — an order a critic proved
             *    is otherwise arbitrary (R9/C2-1). */
            if (r->kind == RK_CLASSBRACKET && r->sel == ']')
                bad("%s (%s): `]` cannot be a class-bracket delimiter. The doorway's "
                    "scan assumes \"a `]` ends the class\" and \"delimiter + `]` closes "
                    "the pair\" are disjoint tests, and this row makes them overlap",
                    kn, r->syntax);

            /* 2. RF_CLASS_NAMED depends on RF_CLASS_DELIM having run the scan
             *    that sets `close_at`. Without the pairing the name length is
             *    computed from an unset `close_at`. That is now clamped at the
             *    call site too, but the pairing is the real invariant: a named
             *    construct whose extent is never measured is meaningless, not
             *    merely unsafe (R9/C3-1). */
            if ((r->flags & RF_CLASS_NAMED) && !(r->flags & RF_CLASS_DELIM))
                bad("%s (%s): RF_CLASS_NAMED without RF_CLASS_DELIM. The name is the "
                    "text between the delimiters, so the row that says \"this text is "
                    "a name\" must also be the row whose extent the scan measures",
                    kn, r->syntax);

            switch (r->status) {
            case RS_BASE:
                if (r->module) bad("%s (%s): RS_BASE must name no module", kn, r->syntax);
                if (r->diag != RD_NONE) bad("%s (%s): RS_BASE must not produce a diagnostic", kn, r->syntax);
                if (r->feature) bad("%s (%s): RS_BASE needs no module feature bit", kn, r->syntax);
                break;
            case RS_MODULE:
                if (!r->module) bad("%s (%s): RS_MODULE must name the module that would implement it", kn, r->syntax);
                if (!r->feature) bad("%s (%s): RS_MODULE must carry a feature bit", kn, r->syntax);
                if (r->diag == RD_NONE) bad("%s (%s): RS_MODULE must produce a diagnostic", kn, r->syntax);
                if (!r->engines) bad("%s (%s): no engine can lower it, yet it is not RS_REJECTED", kn, r->syntax);
                break;
            case RS_REJECTED:
                if (r->module) bad("%s (%s): RS_REJECTED names a module, but PCRE2 rejects it too — "
                                   "there is nothing to implement", kn, r->syntax);
                if (r->feature) bad("%s (%s): RS_REJECTED must carry no feature bit", kn, r->syntax);
                if (r->engines) bad("%s (%s): RS_REJECTED must lower to no engine", kn, r->syntax);
                break;
            default:
                bad("%s (%s): unknown status", kn, r->syntax);
            }

            if (r->diag == RD_FIXED) {
                if (!r->msg || !*r->msg) bad("%s (%s): RD_FIXED with no message", kn, r->syntax);
            } else if (r->msg) {
                bad("%s (%s): carries a fixed message but does not use RD_FIXED", kn, r->syntax);
            }
            if (r->diag == RD_MODULE_OCTAL && k != RK_ESC)
                bad("%s (%s): the octal/backref diagnostic shape is escape-only", kn, r->syntax);

            /* Which diagnostic SHAPES a row may carry is a property of its
             * DOORWAY, since ext.c renders each doorway's own template and
             * knows nothing of the others'. ext.c also carries a BAD_ROW guard
             * for the mismatch — a branch nothing can currently reach, which an
             * R5 critic correctly reported as untested. Asserting the invariant
             * is the right level to test it at: the runtime guard stays as
             * defence, and this is what keeps it unreachable. */
            switch ((RegKind)k) {
            /* RD_FIXED joined both of these at Q2/SR-9, and it is not a
             * loosening: ext.c has always rendered RD_FIXED at every doorway
             * (`if (r->diag == RD_FIXED) ctx_fail(cx, at, "%s", r->msg)`), and
             * the invariant is "this shape HAS a renderer here". The escape
             * doorway needs it for `\N{name}` and the (? doorway for `(?PX)`
             * and the catch-all — three rows saying what PCRE2 says, where a
             * module template would be the over-promise Q2 removes. */
            case RK_ESC:
                if (r->diag != RD_MODULE && r->diag != RD_MODULE_OCTAL &&
                    r->diag != RD_FIXED)
                    bad("%s (%s): the escape doorway renders only the module "
                        "templates and fixed text; this row's diagnostic shape "
                        "has no renderer", kn, r->syntax);
                break;
            case RK_GROUP:
                if (r->diag != RD_MODULE && r->diag != RD_NONE &&
                    r->diag != RD_FIXED)
                    bad("%s (%s): the (? doorway renders only the module "
                        "template and fixed text; this row's diagnostic shape "
                        "has no renderer", kn, r->syntax);
                break;
            /* [M6.4.2] The quant-suffix rows reach NO doorway; their
             * diagnostic is rendered by `p_rep` in src/parse/parse.c, from the
             * row's own `module`, using the module template's own shape. So
             * RD_MODULE is the only value with a renderer, exactly as
             * RD_FIXED is the only one for the two doorways below. */
            case RK_QUANTSUFFIX:
                if (r->diag != RD_MODULE)
                    bad("%s (%s): the possessive-suffix site renders only the "
                        "module template; this row's diagnostic shape has no "
                        "renderer", kn, r->syntax);
                break;
            /* [M6.6.2 wave F] THE `(*` DOORWAY GAINED A MODULE TEMPLATE, for
             * exactly the rows that need one. It had none while its ONE row
             * was RD_FIXED and answered "(*...) requires module 'verbs'" for
             * every name in both tables — the misattribution design §8.2
             * measured (P3). The twelve alpha lookaround rows are RD_MODULE
             * and mod_verbs.c renders the template from the row, which is
             * what puts the RIGHT module in the diagnostic; the doorway's own
             * row is still RD_FIXED and its sentence is unchanged byte for
             * byte. So the rule splits by KIND-and-shape rather than
             * loosening: a verb row is RD_FIXED unless it is an INDEX row,
             * and an index row must be RD_MODULE (a fixed text there would be
             * a second home for the sentence the template already renders). */
            case RK_VERB:
                if ((r->flags & RF_INDEX) != 0) {
                    if (r->diag != RD_MODULE)
                        bad("%s (%s): an INDEX row on the (* doorway renders "
                            "the MODULE template (mod_verbs.c resolves the name "
                            "to this row and prints its module); RD_FIXED here "
                            "would be a second home for that sentence",
                            kn, r->syntax);
                    break;
                }
                if (r->diag != RD_FIXED)
                    bad("%s (%s): this doorway's own row has no module template "
                        "— it must carry fixed text", kn, r->syntax);
                break;
            case RK_CLASSBRACKET:
                if (r->diag != RD_FIXED)
                    bad("%s (%s): this doorway has no module template — its rows "
                        "must carry fixed text", kn, r->syntax);
                break;
            default:
                break;
            }
        }

        if (nany > 1) bad("%s: %d catch-all rows; at most one can ever be reached", kind_name((RegKind)k), nany);

        /* Whether a doorway HAS a catch-all is load-bearing in both directions,
         * and both directions are dispatch behaviour rather than bookkeeping.
         * `(?` and `(*` must always resolve, which is why ext.c can treat a
         * missing row as an internal error; `\` and `[` must be able to DECLINE,
         * because an unknown escape is "unknown escape" and a `[` inside a class
         * is usually an ordinary member. A catch-all added to either of the
         * latter would silently turn every unmatched byte into a construct. */
        {
            int wants_any = (k == RK_GROUP || k == RK_VERB);
            if (wants_any && nany != 1)
                bad("%s: %d catch-all rows, needs exactly 1 — this doorway must "
                    "always resolve, and ext.c has no other answer for an "
                    "unrecognised byte", kind_name((RegKind)k), nany);
            /* [M6.4.2] RK_QUANTSUFFIX lands in the `needs 0` arm and belongs
             * there for a THIRD reason the message now names: it is not a
             * doorway at all, so there is no dispatch for a catch-all to
             * answer — a catch-all row here would be a row nothing can ever
             * elect. */
            if (!wants_any && nany != 0)
                bad("%s: %d catch-all rows, needs 0 — this doorway must be able "
                    "to DECLINE (or, for the non-doorway kinds, has no dispatch "
                    "for a catch-all to answer), or every unmatched byte becomes "
                    "a construct", kind_name((RegKind)k), nany);
        }
        snprintf(label, sizeof label, "well-formed: %s rows (%zu)", kind_name((RegKind)k), n);
        ok(label);
    }

    /* An EXACT count, not a floor. It was `total < 60` against 67 rows, and an
     * R5 critic used the seven rows of slack: deleting GROUP('3')..GROUP('9')
     * in one edit left all seven suites green. Recursion into capture groups
     * 3..9 silently stopped being described, and because the lookup then falls
     * back to the `(?i)` catch-all, the parser routed `(?3)` to 'modifiers'
     * and the table AGREED — in unison — that this was correct.
     *
     * A floor answers "did someone delete a lot"; it never answers "did someone
     * delete the right ones". The manifest below is the real defence and names
     * 8 rows; this makes the other 91 undeletable-by-accident. Adding a row is
     * a one-line bump here, in the same commit — which is the point, not the
     * cost.
     *
     * 68 -> 100 at Q2/SR-9. The 32 are: 11 option-setting bytes that used to
     * hide behind one catch-all, 10 `(?-<digit>)` relative subroutine calls,
     * 3 lookbehind tails on `<`, 3 python-style tails on `P`, `(?+`, `(?[`,
     * the `(?P` and `\N{` refusals, and `\N{U+`. Every one of them is a
     * MEASUREMENT against libpcre2 10.46, not a reading of pcre2syntax. */
    /* 100 -> 104 at [M6.4.2]: the four RK_QUANTSUFFIX rows (`a*+` `a++` `a?+`
     * `a{1,2}+`), module `atomic-groups`. They are the first rows in the table
     * that reach no doorway — see RK_QUANTSUFFIX's own comment in
     * src/core/internal.h for why they exist and what they cost. */
    /* 104 -> 106 at [M6.5.2]: the two new `RK_ESC` rows with tails `<` and
     * `'`, module `recursion`. The `\g` doorway carries TWO CONSTRUCTS and the
     * table had ONE row for it — a subroutine call re-runs the group's
     * PATTERN (`^(a|b)\g<1>$` matches "ab") where a backreference compares the
     * captured TEXT (`^(a|b)\g{1}$` does not), MEASURED. Module `backrefs`
     * claims the brace-and-bare-digit half and may not claim the other, so the
     * angle-bracket and quote tails get rows of their own, born unbuilt. */
    /* 106 -> 118 at [M6.6.2] WAVE F: the twelve `(*` alpha lookaround
     * spellings (Frank's ASK 3 ruling, 2026-08-23), module `lookaround`, all
     * twelve born `built`. They are the first rows in the table that reach no
     * doorway BY DISPATCH — RF_INDEX, D71 item 3 — which is a different fact
     * from RK_QUANTSUFFIX's "reaches no doorway at all": these DO reach the
     * `(*` doorway and produce there, they are simply found by NAME rather
     * than elected by a byte. `check_index_rows` below is what asserts that
     * distinction rather than leaving it to this number. */
    /* 118 -> 127 at [DD-14] WAVE F: module `recursion`'s NINE MISSING
     * SPELLINGS (design §8.1's four families, MEASURED legal on 10.46 and
     * MEASURED already compiling correctly here before this wave: `(?10)`,
     * `(?01)`, `(?00)`, `(?+2)(a)(b)`, `(a)x10(?-10)`, `\g<0>`, `\g<01>`,
     * `\g'0'`, `\g'01'`). They are the first BYTE-KEYED RF_INDEX rows: unlike
     * the twelve alpha spellings above they DO have a dispatching byte, and
     * it belongs to their primary — `(?10)` enters the `(?1)` row and
     * `\g<0>` the `\g<` row, which is why the behaviour was already right
     * and only the INVENTORY was missing. R6 stands: no row's dispatch
     * identity changed and no artifact byte moved. */
    /* 127 -> 128 at [DD-14] WAVE F, part 2: `(?(DEFINE)(?<w>a))`, module
     * `recursion`, tailed `DEFINE)` off the `(?(` doorway (D71 item 4). It is
     * the module's 36th row and the ONLY one that is not VM_ONLY — a DEFINE
     * defines, it does not call, and it lowers to the `{0}` shape that
     * compiles on both engines. */
    if (total != 128) {
        bad("registry ROW COUNT CHANGED: %zu rows, expected 128. If you added or "
            "removed a construct deliberately, update this number in the same "
            "commit; if not, coverage was removed", total);
    } else {
        printf("PASS: registry describes %zu constructs (exact)\n", total);
        pass++;
    }
}

/* Feature bit and module name are two halves of one fact, and a row carrying
 * FEAT_CLASSES while printing "assertions" passed every check until a critic
 * tried it. registry.c's `M_<module>` macros now emit the pair together, so a
 * macro-built row cannot mismatch — but a row written LONGHAND still can, and
 * "correct by construction" is exactly the kind of claim this project keeps
 * losing when nothing tests it.
 *
 * Checked without an external list of modules, which would itself be a second
 * home: across the whole table the mask and the name must be a BIJECTION. One
 * mismatched row necessarily collides with the rows that use its mask and with
 * those that use its name, so it cannot hide. */
static void check_feature_module_bijection(void)
{
    /* [M6.4.2] `RK_COUNT`, NOT a literal 4 — and this is the TWELFTH registry
     * site the fifth kind touched, found by a SEGFAULT rather than by any
     * check. The loop below is `for (k = 0; k < RK_COUNT; k++)` and wrote past
     * the end of two four-element arrays the moment RK_COUNT became 5.
     *
     * atomic_groups_design.md §7.4's sweep extracts five defect SHAPES — exact
     * row counts, kind LISTS, doorway ROUTING-SET assertions, per-row FIELD
     * requirements, and enumeration-by-CALL. This is a SIXTH: an array whose
     * SIZE is the kind count, written as a literal. Its own closing line tells
     * the next reader to suspect a sixth shape before a seventh directory, and
     * that is exactly what this was. */
    const RegRow *all[RK_COUNT];
    size_t counts[RK_COUNT], nkinds = 0, total = 0;
    char label[128];
    int bad_pairs = 0;

    for (int k = 0; k < RK_COUNT; k++) {
        all[nkinds] = pcrec_registry((RegKind)k, &counts[nkinds]);
        if (all[nkinds]) { total += counts[nkinds]; nkinds++; }
    }

    for (size_t ki = 0; ki < nkinds; ki++)
        for (size_t i = 0; i < counts[ki]; i++) {
            const RegRow *a = &all[ki][i];
            if (!a->module || !a->feature) continue;

            for (size_t kj = 0; kj < nkinds; kj++)
                for (size_t j = 0; j < counts[kj]; j++) {
                    const RegRow *b = &all[kj][j];
                    if (!b->module || !b->feature || a == b) continue;

                    if (a->feature == b->feature && strcmp(a->module, b->module) != 0) {
                        bad("feature/module mismatch: %s and %s share a feature bit but print "
                            "'%s' and '%s'", a->syntax, b->syntax, a->module, b->module);
                        bad_pairs++;
                    } else if (strcmp(a->module, b->module) == 0 && a->feature != b->feature) {
                        bad("feature/module mismatch: %s and %s both print '%s' but carry "
                            "different feature bits", a->syntax, b->syntax, a->module);
                        bad_pairs++;
                    }
                }
        }

    if (bad_pairs == 0) {
        snprintf(label, sizeof label,
                 "feature bit <-> module name is a bijection across all %zu rows", total);
        ok(label);
    }
}

/* check_tail_precedence RETIRED (MOD-0.2, its own edit — the plan's rule).
 * It asserted SR-9's longest-tail-wins, an engine that no longer exists; its
 * two obligations have committed successors that were green BEFORE it went:
 * "a tailed row must beat its bucket fallback" -> check_row_ranks (static,
 * total), and its liveness clause ("no prefix pair left = the rule is
 * unobservable, say so") -> check_arbitration_liveness's floors and the
 * esc-'N' triple-answer assertion (R11/M3's counter, the successor D32 §9
 * required). The retired check's own history — first run ZERO failures
 * repository-wide because row order silently stood in for the rule — is in
 * tests/registry/CLAUDE.md and stays instructive. */

/* ---- MOD-0.2: recogniser + rank arbitration ----------------------------
 *
 * Selection stopped being tail interpretation at MOD-0.2 (design §2.2/D32):
 * each row's recogniser answers for itself and `rank` elects the winner.
 * These checks own the migrated rules. check_row_ranks succeeds the "tailed
 * row must beat its bucket fallback" half of check_tail_precedence;
 * check_arbitration_liveness re-homes its liveness clause (R11/M3's
 * more-than-one-answer counter, the committed successor D32 §9 requires
 * before that check may retire). The D32 §9.5 migration scaffold (arbitration
 * vs the retired longest-tail-wins engine, 261,193 probes, 0 mismatches,
 * 0 ambiguous) was DELETED with the engine it checked, in the same commit
 * — an equivalence check cannot outlive its oracle honestly. */


/* A tailed row at the fallback tier can never win against its bucket's
 * always-answering fallback, so its construct would be unreachable — the
 * exact defect the old check's second half guarded. Static and total.
 *
 * The 18 is a MEASURED count (R10's correction: 16 GROUP_T + 1 REJECTED_T +
 * the `\N{U+` longhand row a macro-name grep misses). It is an exact-count
 * tripwire with the R8/C4-10 caveat: it makes a change VISIBLE, it cannot
 * make a wrong one fail — do not satisfy it by editing the number without
 * re-deriving the population from the table. */
static void check_row_ranks(void)
{
    int tailed = 0, badrows = 0;

    for (int k = 0; k < RK_COUNT; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry((RegKind)k, &n);
        for (size_t i = 0; rows && i < n; i++) {
            if (!rows[i].tail) continue;
            /* [M6.6.2 wave F] AN INDEX ROW's `tail` IS A NAME, NOT A TAIL, and
             * both rules below are about ARBITRATION — which an index row
             * never enters (RF_INDEX, D71 item 3). Applying them here would
             * demand a rank for a row rank cannot reach and would call the
             * twelve alpha spellings unreachable, when they are reached every
             * time a caller writes one: mod_verbs.c's
             * `pcrec_registry_verb_name_row` matches the NAME, which is what
             * the `(*` doorway has dispatched on since D25/Q1.
             *
             * IT IS EXCLUDED HERE RATHER THAN EXCUSED, and the difference is
             * that the obligation MOVED rather than lapsed:
             * `check_index_rows` asserts the stronger property in its place —
             * that each name resolves back to its own row, and that no
             * arbitration anywhere can elect one. */
            if (rows[i].flags & RF_INDEX) continue;
            tailed++;
            if (rows[i].rank <= 0) {
                bad("%s: '%c' tail \"%s\" has rank %d — a tailed row at (or below) "
                    "the fallback tier loses every arbitration and its construct "
                    "is unreachable",
                    kind_name((RegKind)k), rows[i].sel, rows[i].tail, rows[i].rank);
                badrows++;
            }
            /* Tails live ONLY at the escape and group doorways (R15, checks
             * critic): the class-bracket and verb lookups ask the tail-less
             * question (at = NULL) and discard the ambiguity flag — a tailed
             * row there could never win its own probe AND a genuine tie
             * would be swallowed silently. scans.c states this as an
             * assumption in prose; this is the assertion, where the fact
             * lives (the R9 rule). */
            if ((RegKind)k != RK_ESC && (RegKind)k != RK_GROUP) {
                bad("%s: '%c' tail \"%s\" — a tailed row at a doorway that asks "
                    "the tail-less question and discards ambiguity; the construct "
                    "is unreachable and its clashes are silent",
                    kind_name((RegKind)k), rows[i].sel, rows[i].tail);
                badrows++;
            }
        }
    }
    /* [M6.5.2] 18 -> 20: the two `\g<` / `\g'` rows. Both are RK_ESC, both
     * carry rank 25 (the tailed tier), and both beat the base `\g` row's rank
     * 0 — which is exactly what the split needs, since that base row is the
     * bucket's fallback and would otherwise claim a construct it must not. */
    /* [DD-14 wave F] 20 -> 21: the `(?(DEFINE)` row, tail `DEFINE)`, rank 25.
     * The tail is what keeps the split honest at a byte that carries TWO
     * modules' constructs — it must beat the tail-less `(?(` row (rank 0,
     * module `conditionals`), which is the same arrangement the `\g` bucket
     * uses and the same reason it uses it. The NINE index rows this wave also
     * added are NOT tailed and do not appear here: an index row is never
     * elected, so it has no rank to lose a race with. */
    if (tailed != 21)
        bad("row ranks: %d tailed rows, 21 expected — the tailed population "
            "moved; re-derive it from the table (do NOT just edit this number)",
        tailed);
    else if (badrows == 0)
        ok("row ranks: all 21 tailed rows sit above the fallback tier");
}

/* The generated probe space for one bucket: every row's tail, every proper
 * prefix of every tail, every tail with a small suffix set appended, and all
 * 255 single bytes. Returns the number of texts, deduplicated. */
#define ARB_MAX_TEXTS 420
#define ARB_TEXT_LEN  24
static int bucket_probe_texts(const RegRow *rows, size_t n, int sel,
                              char texts[][ARB_TEXT_LEN])
{
    static const char *sufs[] = {"x", ")", "0041}", "U+0041}"};
    int nt = 0;
    char cand[ARB_TEXT_LEN];

    for (int b = 1; b < 256 && nt < ARB_MAX_TEXTS; b++) {
        texts[nt][0] = (char)b; texts[nt][1] = '\0'; nt++;
    }
    for (size_t i = 0; i < n; i++) {
        if (rows[i].sel != sel || !rows[i].tail) continue;
        size_t tl = strlen(rows[i].tail);
        /* the tail itself and every proper prefix */
        for (size_t p = 1; p <= tl && nt < ARB_MAX_TEXTS; p++) {
            snprintf(cand, sizeof cand, "%.*s", (int)p, rows[i].tail);
            int dup = 0;
            for (int t = 0; t < nt; t++) if (!strcmp(texts[t], cand)) { dup = 1; break; }
            if (!dup) { snprintf(texts[nt], ARB_TEXT_LEN, "%s", cand); nt++; }
        }
        for (size_t s = 0; s < sizeof sufs / sizeof sufs[0]; s++) {
            if (nt >= ARB_MAX_TEXTS) break;
            snprintf(cand, sizeof cand, "%s%s", rows[i].tail, sufs[s]);
            int dup = 0;
            for (int t = 0; t < nt; t++) if (!strcmp(texts[t], cand)) { dup = 1; break; }
            if (!dup) { snprintf(texts[nt], ARB_TEXT_LEN, "%s", cand); nt++; }
        }
    }
    return nt;
}

/* LIVENESS of the arbitration: per multi-row bucket, how many generated
 * probes make MORE THAN ONE recogniser answer? An arbitration nothing ever
 * contests is unobservable — the exact vacuity check_tail_precedence's
 * liveness clause guarded for longest-tail-wins (R11/M3 located this counter
 * as its natural successor; D32 §9 requires it committed before that check
 * retires). Floors MEASURED 2026-08-11 on the shipped table; a bucket
 * falling below its floor lost its clash population and must FAIL, not pass
 * quietly. The esc-'N' bucket must also keep a probe with three answers —
 * the prefix-related pair (`\N{`/`\N{U+`) plus the fallback — or the rank
 * ordering between two TAILED rows is no longer exercised anywhere. */
static void check_arbitration_liveness(void)
{
    static const struct { RegKind k; int sel; int floor_multi; } buckets[] = {
        /* 10 -> 9 at MOD-0.3f (R16): the \N{ row's recogniser now DECLINES
         * quantifier-shaped bodies (PCRE2's fallback rule — \N{2,3} is bare
         * \N quantified), so the generated text "{0041}" lost its second
         * answer — predicted as exactly one text before the run, confirmed
         * by this check firing at 9. The esc-'N' TRIPLE-answer floor below
         * is untouched: "{U+0041}" is not quantifier-shaped. */
        { RK_ESC,   'N', 9 },
        { RK_GROUP, '<', 15 },
        { RK_GROUP, 'P', 15 },
        { RK_GROUP, '-', 50 },
    };
    static char texts[ARB_MAX_TEXTS][ARB_TEXT_LEN];
    int bad_buckets = 0, total_multi = 0, triple_seen = 0;

    for (size_t bi = 0; bi < sizeof buckets / sizeof buckets[0]; bi++) {
        size_t n;
        const RegRow *rows = pcrec_registry(buckets[bi].k, &n);
        int nt = bucket_probe_texts(rows, n, buckets[bi].sel, texts);
        int multi = 0;

        for (int t = 0; t < nt; t++) {
            int answers = 0;
            for (size_t i = 0; i < n; i++) {
                if (rows[i].sel != buckets[bi].sel) continue;
                if (pcrec_registry_row_answers(&rows[i], texts[t], strlen(texts[t])))
                    answers++;
            }
            if (answers >= 2) multi++;
            if (buckets[bi].k == RK_ESC && buckets[bi].sel == 'N' && answers >= 3)
                triple_seen++;
        }
        total_multi += multi;
        if (multi < buckets[bi].floor_multi) {
            bad("arbitration liveness: bucket %s '%c' has %d multi-answer probes, "
                "floor %d — the clash population shrank, so rank is deciding less "
                "than this check was measured against",
                kind_name(buckets[bi].k), buckets[bi].sel, multi,
                buckets[bi].floor_multi);
            bad_buckets++;
        }
    }
    if (!triple_seen) {
        bad("arbitration liveness: no esc-'N' probe makes THREE recognisers "
            "answer — the prefix-related tail pair is gone, and the ordering "
            "between two TAILED ranks is unobservable (the re-homed liveness "
            "clause of check_tail_precedence)");
        bad_buckets++;
    }
    if (bad_buckets == 0) {
        char label[200];
        snprintf(label, sizeof label,
                 "arbitration liveness: %d multi-answer probes across the 4 "
                 "multi-row buckets (floors 10/15/15/50), %d triple-answer at "
                 "esc-'N'", total_multi, triple_seen);
        ok(label);
    }

    /* THE NO-AMBIGUITY SWEEP (R15, the engine critic's finding): after the
     * D32 §9.5 scaffold was deleted with the retired engine, NOTHING probed
     * the `ambiguous` out-param over a swept space — the defect could only
     * fire at runtime on a user's pattern, caught indirectly by whichever
     * string comparison it happened to break. This is the direct, total
     * form: every kind, every selector byte, every generated text (the same
     * space the floors above count over) must arbitrate WITHOUT a tie at
     * the winning rank. The invariant it pins is the one the whole
     * migration's equivalence rested on: same-rank tailed rows sharing a
     * bucket have mutually exclusive tails, so only the deliberately
     * rank-split \N pair ever clashes above the fallback. A future row
     * violating that fails HERE, at check time, not in a user's compile.
     * Validated in the failing direction: the equal-rank sabotage on the
     * \N pair (70 -> 25) trips this sweep directly. */
    {
        long ambprobes = 0;
        int  ambhits = 0;
        for (int k = 0; k < RK_COUNT; k++) {
            size_t n;
            const RegRow *rows = pcrec_registry((RegKind)k, &n);
            if (!rows) continue;
            for (int sel = 1; sel < 256; sel++) {
                int nt = bucket_probe_texts(rows, n, sel, texts);
                for (int t = 0; t < nt; t++) {
                    bool amb = false;
                    (void)pcrec_registry_arbitrate((RegKind)k, sel, texts[t],
                                                   strlen(texts[t]), &amb);
                    ambprobes++;
                    if (amb) {
                        if (ambhits < 8)
                            bad("no-ambiguity sweep: kind %s sel '%c' text \"%s\" "
                                "arbitrates AMBIGUOUS — two rows answer at the "
                                "winning rank; the winner would be declaration "
                                "order, which is not a rule anyone maintains",
                                kind_name((RegKind)k), sel, texts[t]);
                        ambhits++;
                    }
                }
                bool amb = false;
                (void)pcrec_registry_arbitrate((RegKind)k, sel, NULL, 0, &amb);
                ambprobes++;
                if (amb) ambhits++;
            }
        }
        if (ambprobes < 100000)
            bad("no-ambiguity sweep: only %ld probes — the generated space "
                "collapsed and this sweep is asserting less than it claims",
                ambprobes);
        else if (ambhits == 0) {
            char label[120];
            snprintf(label, sizeof label,
                     "no-ambiguity sweep: 0 winning-rank ties over %ld probes",
                     ambprobes);
            ok(label);
        } else if (ambhits > 8)
            bad("no-ambiguity sweep: %d ambiguous probes total", ambhits);
    }
}

/* ---- [M6.4.2] R3: EVERY KIND REACHES THE DUMP -------------------------- */

/* THE ONLY CHECK IN THIS FILE THAT READS `--list-syntax`'s OUTPUT RATHER THAN
 * THE TABLE, and the formulation is the whole point.
 *
 * A fifth `RegKind` raises NO build alarm — MEASURED at 28 files offered / 28
 * compiled clean / 0 `-Wswitch` diagnostics naming the new enumerator
 * (atomic_groups_measurements/probes/probe_rk_alarm.sh), because every RegKind
 * switch in the tree carries a `default:`. The real exposure is therefore not
 * the switches at all: it is the hardcoded kind ARRAYS — `all_kinds[]` in
 * src/parse/syntax_dump.c, `kinds[]` in src/parse/enabled.c, `kinds[]` below in
 * this file — which no compiler and, before this check, nothing else could see.
 *
 * A CHECK THAT ITERATED `RK_COUNT` OVER `pcrec_registry` WOULD NOT SEE IT
 * EITHER, and would look like it did. That is this project's signature
 * check-design failure (memory: pcrec-check-design-lessons — a control sharing
 * a source with what it controls): `all_kinds[]` is a SECOND enumeration, and
 * only something that consumes the dump it produces can notice that the two
 * disagree. So this check calls `pcrec_syntax_tsv` — the same function
 * `--list-syntax` calls — and interrogates the TEXT.
 *
 * THREE ASSERTIONS, each catching a different half-done fifth kind:
 *
 *   (1) the dump's ROW COUNT equals the sum of `pcrec_registry`'s counts over
 *       RK_COUNT — a kind missing from `all_kinds[]` renders no rows at all;
 *   (2) the dump carries exactly RK_COUNT DISTINCT kind words — the same
 *       omission from the other side, and it also catches two kinds that
 *       render the same word;
 *   (3) no kind word is `?` — `kind_name`'s unknown-kind sentinel, which is
 *       what a kind present in `all_kinds[]` but missing from that switch
 *       renders, and which (1) and (2) both survive.
 *
 * FAILING DIRECTIONS DEMONSTRATED BEFORE THE CHECK WAS WRITTEN, on this tree:
 * dropping RK_QUANTSUFFIX from `all_kinds[]` fires (1) at 100 vs 104 and (2) at
 * 4 vs 5; dropping its arm from `kind_name` fires (3). */
static void check_kind_coverage(void)
{
    char *tsv = pcrec_syntax_tsv(0);
    if (!tsv) { bad("kind coverage: --list-syntax produced no dump"); return; }

    size_t table_rows = 0;
    for (int k = 0; k < RK_COUNT; k++) {
        size_t n = 0;
        if (pcrec_registry((RegKind)k, &n)) table_rows += n;
    }

    /* The dump's own kind words, collected from column 1. Bounded by RK_COUNT
     * plus slack, so an extra word is a named failure rather than an overflow
     * — the defect this very change found in check_feature_module_bijection. */
    char words[RK_COUNT + 4][32];
    int nwords = 0, dump_rows = 0, unknown = 0, overflow = 0;

    for (const char *p = tsv; *p; ) {
        const char *eol = strchr(p, '\n');
        size_t len = eol ? (size_t)(eol - p) : strlen(p);
        if (len && *p != '#') {
            const char *tab = memchr(p, '\t', len);
            size_t wl = tab ? (size_t)(tab - p) : len;
            dump_rows++;
            if (wl == 1 && *p == '?') unknown++;
            if (wl < sizeof words[0]) {
                char w[32];
                memcpy(w, p, wl); w[wl] = 0;
                int seen = 0;
                for (int i = 0; i < nwords; i++)
                    if (strcmp(words[i], w) == 0) { seen = 1; break; }
                if (!seen) {
                    if (nwords < (int)(sizeof words / sizeof words[0]))
                        snprintf(words[nwords++], sizeof words[0], "%s", w);
                    else
                        overflow++;
                }
            }
        }
        p = eol ? eol + 1 : p + len;
    }
    free(tsv);

    int bads = 0;
    if ((size_t)dump_rows != table_rows) {
        bad("kind coverage: the dump renders %d rows but pcrec_registry holds "
            "%zu across RK_COUNT — a RegKind is missing from syntax_dump.c's "
            "all_kinds[], which no -Wswitch can see", dump_rows, table_rows);
        bads++;
    }
    if (nwords != RK_COUNT || overflow) {
        bad("kind coverage: the dump carries %d distinct kind words (plus %d "
            "beyond this check's capacity), expected exactly RK_COUNT = %d",
            nwords, overflow, (int)RK_COUNT);
        bads++;
    }
    if (unknown) {
        bad("kind coverage: %d dump rows render the kind word '?' — "
            "syntax_dump.c's kind_name has no arm for their RegKind, so the "
            "TSV's frozen first column is lying about them", unknown);
        bads++;
    }
    if (bads == 0) {
        char label[192];
        snprintf(label, sizeof label,
                 "kind coverage: --list-syntax renders all %zu rows across "
                 "exactly %d named kinds, none unknown (read from the DUMP, "
                 "not from the table)", table_rows, nwords);
        ok(label);
    }
}

/* ---- part 2: table -> parser ------------------------------------------- */

/* The exact diagnostic a row claims, at the atom (outside-a-class) site. */
static void esc_atom_msg(const RegRow *r, char *buf, size_t sz)
{
    /* RD_FIXED says the whole diagnostic IS `msg` — no template, no module.
     * `\N{name}` is the first escape row of that shape (SR-9): PCRE2 states it
     * does not support the construct, so there is no module to name and the
     * module template would print "(null)". */
    if (r->diag == RD_FIXED)
        snprintf(buf, sz, "%s", r->msg);
    else if (r->diag == RD_MODULE_OCTAL)
        snprintf(buf, sz, "\\%c (backreference/octal) requires module '%s'", r->sel, r->module);
    else
        snprintf(buf, sz, "\\%c requires module '%s'", r->sel, r->module);
}

static void check_table_to_parser(void)
{
    size_t n;
    const RegRow *rows;
    char label[192], want[256], pat[64];
    /* [M6.4.2] r31chk final T2. THIS CHECK ENUMERATES KINDS BY EXPLICIT CALL —
     * `pcrec_registry(RK_ESC, ...)`, `(RK_GROUP, ...)`, and a loop over the two
     * doorway kinds below — so before this array existed a FIFTH `RegKind` was
     * not merely under-checked, it was NEVER COMPARED AT ALL and nothing went
     * red. That is §7.3's own "half-done invisibly" failure shape, sitting
     * inside the file whose job is to notice it.
     *
     * `covered[]` plus the RK_COUNT sweep at the end of this function is the
     * ruled fix: the enumeration is now over RK_COUNT, and a kind nothing
     * compares is a NAMED failure rather than silence. No `-Wswitch` can
     * substitute — every `RegKind` switch in the tree carries a `default:`,
     * measured. */
    bool covered[RK_COUNT];
    memset(covered, 0, sizeof covered);

    /* escapes: both sites — outside a class and inside one */
    rows = pcrec_registry(RK_ESC, &n);
    for (size_t i = 0; i < n; i++) {
        const RegRow *r = &rows[i];

        esc_atom_msg(r, want, sizeof want);
        snprintf(label, sizeof label, "esc %s: atom diagnostic matches the row", r->syntax);
        expect_msg(label, r->syntax, want);

        /* [DD-14 wave F] THE ATOM HALF ABOVE APPLIES TO AN INDEX ROW AND
         * THE CLASS HALF BELOW DOES NOT, and the asymmetry is the flag's
         * meaning rather than a convenience. `\g<0>` at the closed gate
         * really does answer "\g requires module 'recursion'" — the atom
         * assertion is about the SPELLING and holds — while every question
         * below is about which row DISPATCHES at class position, and an
         * RF_INDEX row dispatches nowhere (D71 item 3). Its in-class
         * behaviour is its primary's, asserted on the primary's own row;
         * its `class_expect` value is still measured and still re-derived
         * independently by tests/probes/probe_class_expect.c. */
        if ((r->flags & RF_INDEX) != 0) continue;

        snprintf(pat, sizeof pat, "[%s]", r->syntax);
        if (r->cport.base && r->cport.kind != PORT_NONE) {
            /* \b is backspace inside a class, and since FIX-3 the twelve
             * digit/\g/\k rows are octal or literal fallback there — BASE
             * semantics, since MOD-0.3d carried as the row's own base class
             * PORT (the doorway IS entered now; RF_CLASS_BASE retired). A
             * row that claims this must be right about it.
             *
             * Probe `[\%c]` — the SELECTOR BYTE — not `[%s]` from the row's
             * syntax. The flag's claim is about the byte; the syntax field is
             * the ATOM-position probe, and wrapping it in brackets can change
             * its meaning: `[\g{-1}]` is a class of g { - 1 } whose `{-1` is
             * an out-of-order RANGE, error 108 in libpcre2 too (measured,
             * tests/probes/probe_fix3.c), so demanding it compile asserted a
             * bug. Tail and endpoint behaviour is pinned where it can be
             * oracle-verified: tests/base/class_escape_fallbacks.rxt. */
            snprintf(pat, sizeof pat, "[\\%c]", r->sel);
            snprintf(label, sizeof label, "esc \\%c: base syntax inside a class, as the row claims", r->sel);
            expect_compiles(label, pat);
        } else if (r->flags & RF_CLASS_INVALID) {
            /* PCRE2 forbids the construct inside a class permanently, so the
             * in-class answer must promise NO module — the row's module is the
             * right answer for the ATOM and a lie for the class position
             * (R9/SPEC-classes-F1). Asserting the absence explicitly, because
             * "does not contain 'requires module'" is the property, not the
             * particular wording D26 leaves free. */
            snprintf(want, sizeof want, "\\%c is not valid inside a character class", r->sel);
            snprintf(label, sizeof label, "esc %s: in-class refusal promises no module", r->syntax);
            expect_msg(label, pat, want);
            continue;
        } else if (r->diag == RD_FIXED) {
            /* A fixed-text row says the same thing in both positions: it is
             * PCRE2's own refusal, and PCRE2 does not vary it by position. */
            snprintf(label, sizeof label, "esc %s: in-class diagnostic matches the row", r->syntax);
            expect_msg(label, pat, r->msg);
        } else if (r->recognise == pcrec_registry_uprops_recognise) {
            /* MOD-0.6: mod_uprops.c's refusal is POSITION-INVARIANT by
             * design (D26 tier 3 is free wording; same shape as an
             * RD_FIXED row's "PCRE2 does not vary it by position" above,
             * chosen deliberately rather than carrying the generic
             * "in a class requires module" phrasing). `want` still holds
             * esc_atom_msg's result from the top of this loop iteration —
             * the atom and class messages are the SAME text by
             * construction, so reusing it here is the assertion, not a
             * convenience. */
            snprintf(label, sizeof label, "esc %s: in-class diagnostic matches the row (position-invariant)", r->syntax);
            expect_msg(label, pat, want);
        } else {
            snprintf(want, sizeof want, "\\%c in a class requires module '%s'", r->sel, r->module);
            snprintf(label, sizeof label, "esc %s: in-class diagnostic matches the row", r->syntax);
            expect_msg(label, pat, want);
        }
    }

    covered[RK_ESC] = true;

    /* (?X groups */
    rows = pcrec_registry(RK_GROUP, &n);
    for (size_t i = 0; i < n; i++) {
        const RegRow *r = &rows[i];
        int byte = (r->sel == REG_SEL_ANY) ? (unsigned char)r->syntax[2] : r->sel;

        if (r->status == RS_BASE) {
            snprintf(label, sizeof label, "group %s: supported by the base grammar, as the row claims", r->syntax);
            expect_compiles(label, r->syntax);
            continue;
        }
        /* Since Q2 the (? doorway has fixed-text rows too — `(?PX)` and the
         * catch-all, which agree with PCRE2 that no construct begins there
         * rather than promising a module for it. */
        if (r->diag == RD_FIXED)
            snprintf(want, sizeof want, "%s", r->msg);
        else if (r->roadmap == ROADMAP_NEVER)
            /* K14: a NEVER row must not promise its module (zero at the GROUP
             * doorway today — the callouts row carried it alone until
             * [M4-CALLOUTS] step 1, D36, flipped it to PLANNED 2026-08-14;
             * this branch is derived, so the next one is covered the day it
             * exists). The independent pin of WHICH rows are NEVER is
             * hand-written in tests/reject/. */
            snprintf(want, sizeof want, "(?%c...) is outside pcrec's scope and no module will implement it (see docs/pcre2_compliance.md)", byte);
        else
            snprintf(want, sizeof want, "(?%c...) requires module '%s'", byte, r->module);
        snprintf(label, sizeof label, "group %s: diagnostic matches the row", r->syntax);
        expect_msg(label, r->syntax, want);
    }

    covered[RK_GROUP] = true;

    /* [M6.4.2] the possessive quantifier suffixes. NOT a doorway: `p_rep`
     * (src/parse/parse.c) recognises the `+` after a quantifier it has already
     * accepted, and renders the module template from the row it looks up.
     * With module `atomic-groups` OUT of the enabled set — which is this
     * binary's state, since nothing here installs one — the row's own `syntax`
     * must produce exactly that sentence. When the gate is OPEN the same
     * pattern COMPILES, which is what D65's `built` column reports and what
     * `check_built_status_defects` asserts; the two halves are deliberately
     * different questions asked at different gate states. */
    rows = pcrec_registry(RK_QUANTSUFFIX, &n);
    for (size_t i = 0; i < n; i++) {
        const RegRow *r = &rows[i];
        snprintf(want, sizeof want, "possessive quantifier requires module '%s'",
                 r->module);
        snprintf(label, sizeof label,
                 "quantsuffix %s: diagnostic matches the row", r->syntax);
        expect_msg(label, r->syntax, want);
    }
    covered[RK_QUANTSUFFIX] = true;

    /* verbs and class brackets: fixed messages, used verbatim — EXCEPT the
     * `(*` doorway's twelve INDEX rows ([M6.6.2] wave F), which are RD_MODULE
     * and render the module template from their own row.
     *
     * THIS ARM SEGFAULTED ON THEM BEFORE THE BRANCH BELOW EXISTED, which is
     * worth recording rather than quietly fixing: `r->msg` is NULL on an
     * RD_MODULE row and this loop passed it straight to `strcmp`. The comment
     * one line up ("fixed messages, used verbatim") was the whole
     * specification of that assumption and it stopped being true the moment
     * a verb name got a module of its own. A NULL-guard would have turned the
     * crash into a silent skip of twelve rows; the branch turns it into the
     * assertion those rows actually need.
     *
     * The template is spelled out here rather than derived, exactly as the
     * group arm above spells out its own: this check is the HAND-WRITTEN
     * second source for what a caller is told, and deriving the sentence from
     * the code that prints it would make the two agree in unison about a
     * wrong answer (this file's own header, and tests/reject/'s). */
    for (int k = RK_VERB; k <= RK_CLASSBRACKET; k++) {
        rows = pcrec_registry((RegKind)k, &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            snprintf(label, sizeof label, "%s %s: diagnostic matches the row",
                     kind_name((RegKind)k), r->syntax);
            if (r->diag == RD_MODULE && r->tail) {
                snprintf(want, sizeof want, "(*%s:...) requires module '%s'",
                         r->tail, r->module);
                expect_msg(label, r->syntax, want);
                continue;
            }
            if (!r->msg) {
                bad("%s %s: RD_%s row with a NULL msg reached the "
                    "fixed-text arm — a verb/class-bracket row must either "
                    "carry fixed text or be an RD_MODULE index row with a name",
                    kind_name((RegKind)k), r->syntax,
                    r->diag == RD_MODULE ? "MODULE" : "?");
                continue;
            }
            expect_msg(label, r->syntax, r->msg);
        }
        covered[k] = true;
    }

    /* The collating rows have a SECOND call site: the class-opening bracket
     * itself ("[.a.]", no inner '['). One row, two paths into it — which is
     * the whole point of having one row. Hand-written because the doorway
     * model does not describe this entry, so nothing derives it. */
    expect_msg("classbracket [.a.]: opening bracket reaches the same row",
               "[.a.]", "POSIX collating elements are not supported");
    expect_msg("classbracket [=a=]: opening bracket reaches the same row",
               "[=a=]", "POSIX collating elements are not supported");

    /* [M6.4.2] T2's assertion, and the reason `covered[]` exists: EVERY kind
     * must have been compared above. A kind added to the enum and to
     * registry.c but not to this function is now a named failure here instead
     * of a check that quietly stops covering it. */
    {
        int uncovered = 0;
        for (int k = 0; k < RK_COUNT; k++) {
            if (covered[k]) continue;
            uncovered++;
            bad("table -> parser: RegKind %s (%d) is NEVER COMPARED by this "
                "check — it enumerates kinds by explicit call, so a new kind "
                "is silently uncovered unless it is added here too",
                kind_name((RegKind)k), k);
        }
        if (uncovered == 0) {
            snprintf(label, sizeof label,
                     "table -> parser: all %d RegKinds compared (enumerated "
                     "over RK_COUNT, not by explicit call)", (int)RK_COUNT);
            ok(label);
        }
    }
}

/* ---- part 2b: rows that MUST exist -------------------------------------
 * Everything above iterates the rows that are present, so it is structurally
 * blind to a row being DELETED — and a critic pass demonstrated exactly that:
 * removing both collating rows left all 116 checks green. The per-kind empty
 * check did not fire (the POSIX ':' row survived), the coverage floor did not
 * fire (65 >= 60), and the two probes above kept passing because they exercise
 * the PARSER, not table membership.
 *
 * A coverage floor answers "did someone delete a lot", never "did someone
 * delete the right ones", and no floor low enough to tolerate ordinary row
 * churn can catch a two-row deletion. So this is a hand-written manifest, and
 * hand-written is the point: a control must not come from the same source as
 * the thing it controls. Keep it small — it names constructs whose ABSENCE
 * would be a silent regression of a specific past incident, not every row. */
static void check_required_rows(void)
{
    static const struct {
        RegKind     kind;
        int         sel;
        RegStatus   status;
        const char *why;
    } required[] = {
        {RK_CLASSBRACKET, '.', RS_REJECTED,
         "POSIX collating element — pcrec accepted these silently until 2026-08-09"},
        {RK_CLASSBRACKET, '=', RS_REJECTED,
         "POSIX equivalence class — same incident"},
        {RK_CLASSBRACKET, ':', RS_MODULE, "POSIX class [[:alpha:]]"},
        {RK_ESC,          'v', RS_MODULE,
         "\\v — the vertical-whitespace miscompile this whole file exists for"},
        {RK_ESC,          'b', RS_MODULE, "\\b — word boundary, and backspace in a class"},
        {RK_GROUP,        ':', RS_BASE,
         "(?: — the ONE doorway the base tier reaches; SR-5's guard is about this row"},
        {RK_VERB,  REG_SEL_ANY, RS_MODULE, "the (*...) verb catch-all"},
        /* Q2 INVERTED THIS ROW. It was RS_MODULE ("inline-option catch-all") and
         * promised module 'modifiers' for all 255 bytes; the eleven real option
         * bytes now have rows of their own and the catch-all AGREES WITH PCRE2
         * that there is no construct. Pinned as RS_REJECTED so restoring the
         * over-promise fails here as well as in PC-3's byte differential. */
        {RK_GROUP, REG_SEL_ANY, RS_REJECTED, "the (?...) catch-all: PCRE2 error 111, no module"},
    };
    char label[192];

    for (size_t i = 0; i < sizeof required / sizeof required[0]; i++) {
        /* The manifest names rows by SELECTOR, which is the tail-less question;
         * a manifest entry for a tailed row would need the tail too. None does
         * today, and check_wellformed's (sel, tail) uniqueness check is what
         * would notice a tailed row shadowing a manifest one. */
        const RegRow *r = pcrec_registry_find(required[i].kind, required[i].sel, NULL, 0);

        /* find() falls back to the catch-all, so an exact-selector row must be
         * confirmed to be exactly that row and not the fallback standing in */
        if (!r || (required[i].sel != REG_SEL_ANY && r->sel != required[i].sel)) {
            bad("required row MISSING: %s '%c' — %s",
                kind_name(required[i].kind),
                required[i].sel == REG_SEL_ANY ? '*' : required[i].sel, required[i].why);
            continue;
        }
        if (r->status != required[i].status) {
            bad("required row %s '%c' changed status — %s",
                kind_name(required[i].kind),
                required[i].sel == REG_SEL_ANY ? '*' : required[i].sel, required[i].why);
            continue;
        }
        snprintf(label, sizeof label, "required row present: %s (%s)", r->syntax, required[i].why);
        ok(label);
    }
}

/* ---- part 3: parser -> table (the sweep) -------------------------------- */

/* For every byte, ask the parser what it does at each doorway. Anything the
 * parser routes to a module MUST have a row naming that same module; anything
 * the table calls RS_MODULE must really be routed. This is the direction that
 * catches a construct with no row at all. */
/* `fmt` receives the byte TWICE, so a doorway needing the selector in two
 * places can ask for it ("[[%ca%c]]" builds the collating form). Formats using
 * one %c simply ignore the second argument, which C defines as well-formed. */
/* `at_open` says the template puts the construct at a CLASS'S OWN bracket, so a
 * row with an `open_msg` answers with that one instead of `msg` (FIX-2/K3). The
 * 4a sweep caught this on its first run, which is the sweep doing its job: the
 * `:` row genuinely says two different things in two positions, and a sweep
 * that could not tell them apart would have been asserting the wrong string. */
/* `selpos` is the index of the SELECTOR BYTE inside the pattern `fmt` builds,
 * and it exists so this sweep asks the registry the same question the PARSER
 * asks (SR-9). A tail row matches on the bytes FOLLOWING the selector, so a
 * lookup that passed NULL here would be asking a different question than the
 * one the parser answered — and would agree with it only by luck. `[\%c]`
 * is the live case: the parser sees `]` after the selector, so a future row
 * with tail "]" would make the two disagree silently.
 *
 * It is checked, not trusted: `pat[selpos] != c` fails the sweep. Change a
 * format and forget this number and you get a loud failure rather than a check
 * quietly asking about the wrong byte. That is deliberate — R9 spent two
 * findings on guards that were wrong in the same way as the bug they answered. */
/* Does this bucket decide anything by a TAIL? Mirrors ext.c's helper of the
 * same shape and exists for the same one caller — the truncation exception
 * below. */
static bool sweep_bucket_has_tail(RegKind k, int sel)
{
    size_t n;
    const RegRow *rows = pcrec_registry(k, &n);
    for (size_t i = 0; i < n; i++)
        if (rows[i].sel == sel && rows[i].tail) return true;
    return false;
}

static void sweep(RegKind k, const char *fmt, size_t selpos, const char *what,
                  unsigned skip_flag, bool at_open, bool excuse_base_cport)
{
    char pat[16], got[256], label[192];
    int mismatches = 0, routed = 0;

    for (int c = 1; c < 256; c++) {
        const RegRow *r;
        int rejected;

        snprintf(pat, sizeof pat, fmt, c, c);
        size_t plen = strlen(pat);
        if (selpos >= plen || (unsigned char)pat[selpos] != (unsigned char)c) {
            bad("%s: selpos %zu does not point at the selector byte 0x%02x in \"%s\" "
                "— the sweep would ask the registry about the wrong position",
                what, selpos, c, pat);
            mismatches++;
            break;
        }
        rejected = try_compile(pat, got, sizeof got) != 0;
        r = pcrec_registry_find(k, c, pat + selpos + 1, plen - selpos - 1);

        /* A row whose whole diagnostic is fixed text carries no "requires
         * module" marker, so the generic branches below cannot see it. Check it
         * directly: this is what makes the collating rows visible to the sweep
         * rather than to their two hand-written probes alone. */
        if (r && r->sel == c && r->diag == RD_FIXED) {
            const char *want = (at_open && r->open_msg) ? r->open_msg : r->msg;
            /* THE TRUNCATION EXCEPTION (R20/OPTRUN-1). Every pattern this
             * sweep builds for the `(?` doorway is `(?X` — it ENDS at the
             * selector — and in a bucket decided by a TAIL that means the
             * fallback row was reached because the text ran out, not because
             * the byte is unrecognisable. Its fixed message ("unrecognized
             * character after (?P") is then a sentence about a byte the
             * pattern does not contain, and the parser answers the
             * unclosed-group family instead, as libpcre2 does (err 114).
             *
             * THE EXPECTATION IS HAND-WRITTEN HERE, NOT READ FROM THE ROW,
             * and that is deliberate: the row's own message is precisely the
             * wrong answer in this cell, so deriving it would re-assert the
             * defect. This string can therefore dissent if the parser
             * reverts. Its ORACLE is elsewhere, as it must be — tests/reject
             * pins `(?P` by hand, and PC-3's tail sweep now generates
             * truncated completions against libpcre2. */
            if (selpos + 1 == plen && sweep_bucket_has_tail(k, c))
                want = "missing closing ) for group";
            if (!rejected || strcmp(got, want) != 0) {
                bad("%s: byte 0x%02x ('%c') — the row promises \"%s\", parser %s",
                    what, c, c >= 32 && c < 127 ? c : '?', want,
                    rejected ? got : "COMPILED it");
                mismatches++;
            } else {
                routed++;
            }
            continue;
        }

        if (rejected && strstr(got, "requires module")) {
            routed++;
            if (!r || r->status != RS_MODULE) {
                bad("%s: the parser routes byte 0x%02x ('%c') to a module (\"%s\") "
                    "but the registry has no such row", what, c, c >= 32 && c < 127 ? c : '?', got);
                mismatches++;
            } else if (!strstr(got, r->module)) {
                bad("%s: byte 0x%02x ('%c') — parser says \"%s\", registry says module '%s'",
                    what, c, c >= 32 && c < 127 ? c : '?', got, r->module);
                mismatches++;
            }
        } else if (r && r->status == RS_MODULE && r->sel == c && !(r->flags & skip_flag)
                   && !(excuse_base_cport && r->cport.base && r->cport.kind != PORT_NONE)
                   && r->roadmap != ROADMAP_NEVER) {
            /* NEVER rows are excused like skip_flag rows: they reject WITHOUT
             * naming a module by design (K14), and check_table_to_parser
             * asserts their exact text positively, so this is not an escape
             * from being checked. */
            /* skip_flag excuses a row that is deliberately NOT a "requires
             * module" answer here; since MOD-0.3d the base-class-semantics
             * excuse is the row's own BASE PORT (excuse_base_cport, set only
             * by the in-class sweep — [\b] compiles as backspace THROUGH the
             * doorway now, and check_class_ports/check_table_to_parser assert
             * that positively). */
            bad("%s: the registry claims byte 0x%02x ('%c') needs module '%s', but the parser %s",
                what, c, c >= 32 && c < 127 ? c : '?', r->module,
                rejected ? "rejects it for another reason" : "compiles it");
            mismatches++;
        }
    }

    if (mismatches == 0) {
        snprintf(label, sizeof label, "sweep %s: all 255 bytes agree (%d routed to a module)", what, routed);
        ok(label);
    }
}

/* The `(*` doorway needs its own sweep since Q1, and the reason is a measured
 * near-miss worth recording rather than quietly fixing.
 *
 * The generic sweep asks "did the parser say 'requires module', and if so does
 * a row agree". Before Q1 all 255 bytes after `(*` said exactly that, so the
 * sweep exercised all 255. Q1 made most of them say "not recognized" instead —
 * correctly — and the generic sweep went from 255 bytes asserted to ONE, while
 * staying green and still printing a PASS line reading "all 255 bytes agree".
 * A check that narrows to nothing without failing is the exact shape this
 * directory keeps warning about, one level down.
 *
 * So this asserts what is now true for every byte: the doorway is REACHED, it
 * rejects, and its answer is one the registry can account for — the row's own
 * "requires module", one of the two tables' "not recognized" messages, MARK's
 * message, or the quantifier error for an empty name. Plus the case rule:
 * PCRE2's lower table is selected by a lowercase first byte and nothing else,
 * which is the one thing the byte sweep is genuinely well shaped to prove.
 *
 * It does NOT check which name is which — a byte sweep never could, since names
 * are longer than a byte. That is tests/registry/pcre2_check.c's job (PC-3),
 * and it does it against libpcre2 over ~75k generated names.
 *
 * AND IT READS THE MESSAGES FROM THE TABLE IT IS CHECKING, so SWAPPING the two
 * `unknown_msg` strings moves both sides together and this sweep stays green
 * (measured, R8/C3-F2). The case rule is therefore proved relative to the
 * table, not against PCRE2's wording — PC-3 and tests/reject/ are what catch
 * the swap. That is this whole file's standing limitation, not a new one, but
 * the sentence above would otherwise read as more than it is. */
static void sweep_verb(void)
{
    const RegRow    *row   = pcrec_registry_find(RK_VERB, REG_SEL_ANY, NULL, 0);
    const VerbTable *upper = pcrec_registry_verb_tables(0);
    const VerbTable *lower = pcrec_registry_verb_tables(1);
    const VerbName  *mark  = pcrec_registry_verb_find(upper, "MARK", 4);
    const char *quant = "quantifier does not follow a repeatable item";
    int n_module = 0, n_upper = 0, n_lower = 0, n_other = 0, mismatches = 0;
    char label[192];

    if (!row || !upper || !lower || !mark || !mark->own_msg) {
        bad("sweep after (*: the registry no longer supplies the rows this sweep "
            "reads (row=%p upper=%p lower=%p MARK=%p)",
            (void *)row, (void *)upper, (void *)lower, (void *)mark);
        return;
    }

    for (int c = 1; c < 256; c++) {
        char pat[16], got[256];
        snprintf(pat, sizeof pat, "(*%c)", c);
        if (try_compile(pat, got, sizeof got) == 0) {
            bad("sweep after (*: byte 0x%02x ('%c') COMPILED — the doorway was "
                "not reached at all", c, c >= 32 && c < 127 ? c : '?');
            mismatches++;
            continue;
        }
        if      (strcmp(got, row->msg)          == 0) n_module++;
        else if (strcmp(got, upper->unknown_msg) == 0) n_upper++;
        else if (strcmp(got, lower->unknown_msg) == 0) n_lower++;
        else if (strcmp(got, mark->own_msg)      == 0) n_other++;
        else if (strcmp(got, quant)              == 0) n_other++;
        else {
            bad("sweep after (*: byte 0x%02x ('%c') produced \"%s\", which is not "
                "any answer this doorway is supposed to have", c,
                c >= 32 && c < 127 ? c : '?', got);
            mismatches++;
            continue;
        }
        /* The case rule, both ways. */
        int is_lower_byte = c >= 'a' && c <= 'z';
        if (!is_lower_byte && strcmp(got, lower->unknown_msg) == 0) {
            bad("sweep after (*: byte 0x%02x ('%c') is not lowercase but was "
                "answered from the LOWER name table", c, c >= 32 && c < 127 ? c : '?');
            mismatches++;
        }
        if (is_lower_byte && strcmp(got, upper->unknown_msg) == 0) {
            bad("sweep after (*: byte 0x%02x ('%c') is lowercase but was answered "
                "from the UPPER name table", c, c >= 32 && c < 127 ? c : '?');
            mismatches++;
        }
    }

    /* Liveness. Without these the sweep could pass by producing one answer for
     * everything — which is precisely what it did before Q1. */
    if (!n_module) { bad("sweep after (*: no byte reached a module — the doorway "
                         "never routes anywhere"); mismatches++; }
    if (!n_upper)  { bad("sweep after (*: no byte was an unknown UPPER-table name"); mismatches++; }
    if (!n_lower)  { bad("sweep after (*: no byte was an unknown LOWER-table name"); mismatches++; }

    if (mismatches == 0) {
        snprintf(label, sizeof label,
                 "sweep after (*: all 255 bytes accounted for (%d module, "
                 "%d unknown-upper, %d unknown-lower, %d other)",
                 n_module, n_upper, n_lower, n_other);
        ok(label);
    }
}

/* MOD-0.3b: the port DATA, checked before anything consumes it. Slice 1
 * lands the two port columns UNWIRED, so the checkable facts are
 * data-consistency facts, each with its population stated as a PREDICTION
 * before the first run (the MOD-0.2 floors rule): exactly 5 scalar class
 * ports (\b \g \k \8 \9), 0 SET, 0 FN, 0 non-NONE atom ports. Slices 2-3
 * move those counts DELIBERATELY — a silent move is the defect this pins.
 *
 * Value rules, one per syntax shape:
 *   - bare-escape syntax ("\X"): the scalar must equal the class_expect
 *     column's measured byte. That column is libpcre2-fed (probe_class_
 *     expect.c) and re-verified live by spec check04, so the port cannot
 *     drift from the oracle without this failing — the port does NOT get
 *     to be its own authority.
 *   - body-carrying syntax (\k<name>, \g{-1}): class_expect measures the
 *     whole probe, so the tie is §14.3's literal-fallback law instead —
 *     the port produces the row's own selector letter (measured at FIX-3
 *     over all 62 [\c] probes; the corpus pins the behaviour, this pins
 *     the data). */
static void check_class_ports(void)
{
    int scalar = 0, set = 0, fn = 0, aports = 0, bads = 0;

    for (int k = 0; k < RK_COUNT; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry((RegKind)k, &n);
        for (size_t i = 0; rows && i < n; i++) {
            const RegRow *r = &rows[i];
            if (r->aport.kind != PORT_NONE) aports++;
            if (r->cport.kind == PORT_SET) {
                set++;
                /* the SET tie (slice 2): a bare-escape row's produced census
                 * must equal the libpcre2-fed class_expect count, with the
                 * PORT's negate flag applied — the bitmap is generated data,
                 * and this is what notices a stale or mis-negated table
                 * before PC-4's live oracle does */
                char bare[8];
                snprintf(bare, sizeof bare, "\\%c", r->sel);
                if (strcmp(r->syntax, bare) == 0) {
                    int pop = 0;
                    for (int b = 0; b < 32; b++)
                        for (int bit = 0; bit < 8; bit++)
                            if (r->cport.set[b] & (1 << bit)) pop++;
                    if (r->cport.scalar) pop = 256 - pop;
                    unsigned want_n = 0;
                    if (!r->class_expect ||
                        sscanf(r->class_expect, "set %u", &want_n) != 1) {
                        bad("class ports: '%s' carries a SET class port but "
                            "class_expect is '%s', not 'set N'", r->syntax,
                            r->class_expect ? r->class_expect : "(null)");
                        bads++;
                    } else if ((unsigned)pop != want_n) {
                        bad("class ports: '%s' produced census %d != measured "
                            "class_expect %u — the generated bitmap (or its "
                            "negate flag) drifted from the oracle column",
                            r->syntax, pop, want_n);
                        bads++;
                    }
                }
            }
            if (r->cport.kind == PORT_FN)  fn++;
            if (r->cport.kind != PORT_SCALAR) continue;
            scalar++;

            char bare[8];
            snprintf(bare, sizeof bare, "\\%c", r->sel);
            if (strcmp(r->syntax, bare) == 0) {
                unsigned v = 0;
                if (!r->class_expect ||
                    sscanf(r->class_expect, "char 0x%x", &v) != 1) {
                    bad("class ports: '%s' carries a scalar class port but its "
                        "class_expect is '%s', not a measured 'char 0xNN' — the "
                        "port has no oracle-fed value to be checked against",
                        r->syntax, r->class_expect ? r->class_expect : "(null)");
                    bads++;
                } else if ((int)v != r->cport.scalar) {
                    bad("class ports: '%s' port scalar 0x%02x != measured "
                        "class_expect byte 0x%02x — the port drifted from the "
                        "libpcre2-fed column",
                        r->syntax, (unsigned)r->cport.scalar, v);
                    bads++;
                }
            } else if (r->cport.scalar != r->sel) {
                bad("class ports: '%s' (body-carrying syntax) port scalar "
                    "0x%02x != its selector '%c' — §14.3's literal-fallback "
                    "law is the value rule for these rows",
                    r->syntax, (unsigned)r->cport.scalar, r->sel);
                bads++;
            }
        }
    }

    /* The generated posix map vs posix_names[] (R16 follow-up): the map's
     * name set must be EXACTLY the producible posix names — every
     * non-assertion name in posix_names[] present once, no extras. The
     * PAIRING inside the map is generated with the tables (same probe
     * run); this ties the two name LISTS, which have different owners
     * (PC-3 measures posix_names; the probe generates the map). */
    {
        size_t nn = 0;
        const PosixName *pn = pcrec_registry_posix_names(&nn);
        for (size_t i = 0; i < nn; i++) {
            if (pn[i].whole_class_only) continue;
            int hits = 0;
            for (size_t j = 0; j < pcrec_cls_posix_map_n; j++)
                if (strcmp(pcrec_cls_posix_map[j].name, pn[i].name) == 0)
                    hits++;
            if (hits != 1) {
                bad("class ports: posix name '%s' appears %d times in the "
                    "generated map (exactly 1 required) — regenerate "
                    "cls_bits.inc with probe_cls_bits --emit",
                    pn[i].name, hits);
                bads++;
            }
        }
        int producible = 0;
        for (size_t i = 0; i < nn; i++)
            if (!pn[i].whole_class_only) producible++;
        if ((size_t)producible != pcrec_cls_posix_map_n) {
            bad("class ports: generated map has %zu names, posix_names[] "
                "has %d producible — a name exists in one list only",
                pcrec_cls_posix_map_n, producible);
            bads++;
        }
    }

    /* [M6.3]: atom ports 23 -> 26, the three named-groups declaring rows'
     * new pcrec_ngport_declare producer.
     * [M6.2 wave A]: 26 -> 29, the `\\A`/`\\Z`/`\\z` rows' new
     * pcrec_asrtport_atom producer. Nothing else in this population moved —
     * no cport, no scalar/SET/FN class port touched, and in particular those
     * three rows KEEP RF_CLASS_INVALID and NO_PORT at class position, because
     * `[\\A]` is PCRE2 error 107 permanently and an atom producer must not
     * quietly become a class one.
     * [M6.2 wave B]: 29 -> 31, the `\\b`/`\\B` rows' atom producer. The
     * SCALAR population is UNMOVED at 5 and `\\b` is still one of them, which
     * is the part of this row worth reading: `\\b` gains an ATOM port while
     * KEEPING its scalar CLASS port, because inside a character class `\\b` is
     * not an assertion at all — it is base syntax for backspace (0x08). A
     * wave that had let the atom producer swallow the class position would
     * move `scalar` to 4 and be caught here. `\\B` keeps RF_CLASS_INVALID and
     * NO_PORT at class position for `\\A`'s reason above.
     * [M6.2 wave D]: 31 -> 32, the `\\G` row's atom producer. It keeps
     * RF_CLASS_INVALID and NO_PORT at class position for `\\A`'s reason
     * (`[\\G]` is PCRE2 error 107, re-measured by that wave), so the SCALAR
     * population is again UNMOVED at 5 — `\\b` remains the module's only
     * row with a live class port beside an atom one.
     * [M6.2 wave E]: 32 -> 33, the `\\K` row's atom producer, which CLOSES
     * module `assertions` — all eight of its constructs now have one. Same
     * two invariants as every wave since A: RF_CLASS_INVALID and NO_PORT at
     * class position (`[\\K]` is PCRE2 error 107, re-measured by wave E), so
     * the SCALAR population is UNMOVED at 5 for the fourth time running.
     * [M6.4.2]: 33 -> 34, the `(?>...)` row's `pcrec_agport_atomic` producer.
     * The SCALAR population is UNMOVED at 5 for the fifth time running, and
     * this row cannot move it for a structural reason rather than a measured
     * one: `(` inside a character class is an ordinary member, so no GROUP row
     * can reach a class position at all and every one of them carries NO_PORT
     * there by construction (check_wellformed asserts the matching
     * `class_expect == NULL`).
     *
     * THE FOUR RK_QUANTSUFFIX ROWS ADD NOTHING HERE, and that is the whole
     * shape of that kind: they carry NO_PORT at both positions because they
     * reach NO DOORWAY — `p_rep` (src/parse/parse.c) recognises the possessive
     * `+` directly and looks the row up only to STAMP from it. A port on one
     * of them would be a port nothing can ever call, so a future edit that
     * adds one moves this number and is caught here. */
    /* [M6.5.2]: SCALAR 5 -> 7 and ATOM PORTS 34 -> 47, and the two moves are
     * independent facts about one module.
     *
     * The SCALAR move is the two NEW `recursion` rows (`\g<1>`, `\g'1'`),
     * which carry the SAME base literal-fallback class port the base `\g` row
     * does — `[\g<]` is the letter `g` followed by ordinary members, and it
     * must stay that way. Giving them NO_PORT instead would have changed a
     * BASE fact the day these rows landed, because the class doorway
     * arbitrates on the same tail the atom doorway does.
     *
     * The ATOM move is THIRTEEN: the ten digit rows (`\0`..`\9`, whose port
     * owns PCRE2's octal disambiguation and is the only one here that can
     * produce a CHARACTER rather than a reference), plus `\k`, `\g` and
     * `(?P=n)`. The two new `recursion` rows add NONE — they are born unbuilt,
     * which is the whole point of splitting them out.
     *
     * [M6.6.2] wave B+C: ATOM PORTS 47 -> 53, and it is SIX rows sharing ONE
     * FUNCTION — module `lookaround`'s `pcrec_laport_group`, wired on all six
     * of `(?=...)` `(?!...)` `(?*a)` `(?<=...)` `(?<!...)` `(?<*a)`. This
     * count is of PORTS and not of built constructs, so all six move it even
     * though only three of them BUILD at this wave: the port's tail check
     * declines the three `(?<` tails at `WANT_RESULT` until wave D, which is
     * what keeps their `built` column reading `unbuilt`. The two facts are
     * counted separately on purpose, and `check_engine_capability` below is
     * where the OTHER one lives. Class ports are unmoved at 7/10/9: a
     * lookaround has no class position at all.
     *
     * [M6.6.2] WAVE F: ATOM PORTS 53 -> 65, and it is the SAME function again
     * — the twelve `(*` alpha spellings' rows carry `pcrec_laport_group` in
     * their own `aport`, which is what makes the `(*` doorway's producer call
     * generic ("this NAME's row has a port") instead of a lookaround special
     * case in mod_verbs.c. So one function is now wired on EIGHTEEN rows, and
     * all twelve new ones BUILD immediately (unlike wave B+C's six, three of
     * which did not) because the port has no tail to decline for them: an
     * alias resolves through `family` to a primary whose tail the port has
     * accepted since wave D. Class ports are unmoved at 7/10/9 for the same
     * reason as before, one spelling further out: `[(*pla:a)]` is a class of
     * ordinary members and there is no construct there to port.
     *
     * [DD-14] WAVE B+C: ATOM PORTS 65 -> 89, and it is TWENTY-FOUR rows over
     * THREE functions rather than one — module `recursion`'s
     * `pcrec_rcport_num` (the eleven absolute rows `(?0)`..`(?9)` and
     * `(?R)`), `_rel` (`(?+1)` and the ten `(?-N)` tails) and `_name`
     * (`(?&name)` and `(?P>n)`). Three and not one because the three serve
     * three FAMILIES and the family is what a reader of the table needs to
     * see at the row; the `(?0)` row in particular carries a description
     * saying the whole DIGIT RUN is read, because `(?0...)` is a
     * one-character prefix of two different targets and a port written from
     * the old unqualified "synonym for (?R)" MISCOMPILES `(?01)`.
     *
     * ALL TWENTY-FOUR BUILD IMMEDIATELY, unlike wave B+C's lookaround six:
     * these ports have no tail left to decline. The two `\g<` / `\g'` rows
     * stayed `unbuilt`, and they did it with NO PORT AT ALL (`NO_PORT`, so
     * ext.c's ENABLED-BUT-UNBUILT epilogue answered for them) — which is why
     * the SCALAR count above was unmoved at 7 and the atom count moved by
     * exactly 24 rather than 26.
     *
     * [DD-14] WAVE D: ATOM PORTS 89 -> 91. Both `\g<` / `\g'` rows' `aport`
     * now points at `pcrec_brport_g` (`src/parse/mod_backrefs.c`, gained the
     * `<`/`'` arms) rather than `NO_PORT`, so the atom count moves by exactly
     * the two rows that were the wave B+C gap. The SCALAR count is STILL
     * unmoved at 7: an atom-position wiring is orthogonal to the base scalar
     * CLASS port those two rows have carried since [M6.5.2] (the literal
     * letter `g`), which is what the "unmoved" clause below is about.
     *
     * CLASS PORTS ARE UNMOVED at 7/10/9 for the fourth wave running: a
     * subroutine call has no class position, and the two `\g` rows' BASE
     * scalar class ports (the literal letter `g`) were already counted. */
    if (scalar != 7 || set != 10 || fn != 9 || aports != 92)
        bad("class ports: populations moved — %d scalar (7: b g k 8 9 and the "
            "two \\g< / \\g' rows), "
            "%d SET class ports (10: the char-types, slice 2), %d FN class "
            "ports (9: posix + the eight octal digits, slice 3), %d atom "
            "ports (92: the char-types + \\N, the twelve GROUP_OPT rows' "
            "option-run producer since MOD-0.5c, the three "
            "named-groups declaring rows' producer since [M6.3], the "
            "three assertions rows \\A/\\Z/\\z since [M6.2] wave A, plus "
            "\\b and \\B since wave B, \\G since wave D, \\K since "
            "wave E, `(?>...)` since [M6.4.2], the thirteen backrefs rows "
            "since [M6.5.2], the EIGHTEEN lookaround rows sharing ONE port "
            "-- six at [M6.6.2] wave B+C, twelve more at wave F -- the "
            "TWENTY-FOUR recursion rows over THREE ports since [DD-14] wave "
            "B+C, the two \\g< / \\g' rows sharing `pcrec_brport_g` since "
            "[DD-14] wave D, and the `(?(DEFINE)` row's own port since "
            "[DD-14] wave F). A deliberate move edits this check IN THE SAME "
            "CHANGE; a silent one is the defect", scalar, set, fn, aports);
    else if (bads == 0)
        ok("class ports: 7 scalar + 10 SET + 9 FN class ports, 92 atom "
           "ports (11 + the 12 option-run rows, MOD-0.5c, + the 3 "
           "named-groups rows, [M6.3], + the 3 assertions rows, [M6.2] "
           "wave A, + \\b and \\B, wave B, + \\G, wave D, + \\K, wave E "
           "-- module `assertions` is now COMPLETE -- + `(?>...)`, "
           "[M6.4.2], + the ten digit rows and \\k \\g (?P=n), [M6.5.2] "
           "-- module `backrefs` -- + the EIGHTEEN lookaround rows through "
           "ONE shared port, six at [M6.6.2] wave B+C and the twelve alpha "
           "spellings at wave F, + the TWENTY-FOUR recursion rows over "
           "THREE ports since [DD-14] wave B+C, + the `(?(DEFINE)` row's "
           "own port at [DD-14] wave F "
           "-- while the two \\g< / \\g' rows added only their base "
           "literal-fallback CLASS port at [M6.5.2] and now ALSO share "
           "`pcrec_brport_g` at [DD-14] wave D; "
           "the four RK_QUANTSUFFIX rows add none, having no "
           "doorway to be called from); scalar and SET "
           "values oracle-tied "
           "(class_expect column / fallback law / census popcounts), as "
           "predicted for slice 3");
}

/* ---- [M6.4.2 / D67] SR-8's TRIPWIRE, RETIRED INTO THE THING IT DEMANDED ----
 *
 * `check_engine_capability_tripwire` stood here from [M4.7a] to [M6.4.2]. Its
 * demand was that every RS_MODULE row whose `engines` mask excludes ENGM_DFA
 * has NO wired atom-position producer — the fact that made SR-8's absence safe
 * — and its failure message named src/opt/select_engine.c as the thing to build
 * BEFORE the first producer landed. It fired twice. [M6.2] wave E answered `\K`
 * with a NAMED exception that paid for itself behaviourally, and wrote down
 * what to do the next time, in advance:
 *
 *     "If a SECOND construct arrives here, do not add a second exception: two
 *      is when the generic consultation has earned its axis and SR-8 is the
 *      right build."
 *
 * `(?>` is the second. SR-8 IS BUILT (D67, src/opt/select_engine.c's
 * `forces_registry`), so the tripwire's own premise is DISCHARGED and it goes —
 * a deletion, not an addition, which is what D67 says a retirement looks like.
 * What replaces it is the tripwire's demand turned the right way round: not
 * "no VM_ONLY row has a producer" but "EVERY VM_ONLY row that HAS one refuses
 * `--engine=dfa` BY NAME".
 *
 * THREE LAYERS, and the split is `check_required_rows`' own argument:
 *
 *   ITERATION guarantees COVERAGE. The population is walked from the table, so
 *   a module that wires the next VM_ONLY producer cannot escape the check — and
 *   a producer with no witness below is a NAMED FAILURE, which is what makes
 *   this generic where a hand list alone would not be.
 *
 *   A HAND-WRITTEN WITNESS guarantees CORRECTNESS. A control must not share a
 *   source with the thing it controls, and the row's own `syntax` cannot serve
 *   here for a reason that is the module's whole point: `a*+` COMPILES under
 *   `--engine=dfa`, correctly, because the free discharge deletes a cut it
 *   proves is a no-op. So each producer-bearing row names a pattern whose cut
 *   genuinely BITES, written by a human from the construct's semantics.
 *
 *   BOTH DIRECTIONS, wave E's rule kept verbatim: the witness must REFUSE under
 *   `--engine=dfa` naming the construct, AND COMPILE under the default engine.
 *   A check that asserted only the refusal would go green on a compiler that
 *   had simply stopped accepting the construct at all.
 *
 * AND THE PER-PATTERN SPLIT IS ASSERTED TOO, in the other direction: `a*+b`
 * must COMPILE under `--engine=dfa`. That is what the `engines` column could
 * never say by itself — VM_ONLY is too strong for a possessive whose cut is
 * provably dead and ANY_ENGINE is too weak for one whose cut bites — and it is
 * the first evidence that column has had in BOTH directions. Sabotage row S91
 * (the discharge fires unconditionally) and S96 (the producer does not stamp)
 * are the two failing directions.
 *
 * THE MASK IS BORROWED AND GIVEN BACK, and the entry state is ASSERTED rather
 * than saved blind — the retired check's own rule, kept: every other check in
 * this file believes it runs at the default EMPTY set, which is what makes
 * their "requires module 'X'" expectations mean anything. */
static bool eng_refuses_by_name(const char *feats, const char *pat,
                                const char *name, char *msg, size_t msgsz)
{
    pcrec_options opt;
    pcrec_output  out;
    pcrec_error   perr;
    char err[256];

    if (pcrec_enabled_set_spec(feats, err, sizeof err) != 0) {
        snprintf(msg, msgsz, "could not enable '%s': %s", feats, err);
        return false;
    }
    pcrec_default_options(&opt);
    opt.engine = PCREC_ENGINE_DFA;
    /* [DD-14 wave G] `-fno-splice-calls`, AND IT IS A REFINEMENT OF THIS
     * CHECK'S CLAIM RATHER THAN A HOLE IN IT.
     *
     * The claim is "every VM_ONLY row with a producer refuses `--engine=dfa`
     * BY NAME". Wave G made that claim FALSE AS STATED for module
     * `recursion`, and the reason is the same one D67 already records for
     * `(?>`: the `engines` column is a per-ROW fact and the truth is per
     * PATTERN. `^(a(?1)?b)$` generates a^n b^n and is VM-only for ever; `(a)(?1)`
     * names an ACYCLIC callee, which `src/opt/callgraph.c` splices and
     * `src/ir/nfa.c` lowers EXACTLY, so it is as regular as `(a)a` and
     * compiles on the DFA. `(?>`'s version of this gap is closed by the free
     * discharge DELETING the node; a call's is closed by the LINKAGE, because
     * a call cannot be deleted without copying its callee's `A_CAP` nodes into
     * the tree.
     *
     * SO THE REFUSAL IS ASKED ON THE AXIS WHERE THE ROW'S COLUMN IS EXACTLY
     * TRUE. `-fno-splice-calls` forces the CALL linkage at every site, which
     * is the artifact wave B+C shipped and the configuration the column
     * describes. It changes NOTHING for any other row here — no other module's
     * construct has a linkage — so this is one uniform line rather than a
     * per-module carve-out, and every witness stays as sharp as it was: a row
     * whose producer stopped stamping still fails.
     *
     * AND IT IS NOT WHERE THE SPLICED BEHAVIOUR GOES UNCHECKED.
     * `tests/recursion/run_recursion_diff.sh` §4 asserts all three cells — the
     * RECURSIVE pattern still refuses by name, the SPLICEABLE one COMPILES,
     * and `-fno-splice-calls` puts the second back to a refusal — which is the
     * both-directions evidence that the line below is about the LINKAGE and
     * not about the construct having quietly stopped being VM-only.
     *
     * A MEASURED REASON THE WITNESSES WERE NOT SIMPLY MADE RECURSIVE INSTEAD,
     * which was tried first: it works for twenty of the twenty-two, and it
     * CANNOT work for `(?+N)`. A forward relative call's target lies to its
     * RIGHT, a cycle through that target needs a backward call INSIDE it —
     * therefore also to the right — and `first_dfa_excluding` walks an
     * `A_CAT` spine RIGHT TO LEFT, so it reaches the backward call first and
     * the refusal names THAT row every time. Verified on five shapes,
     * including `(?+1)((?-1)?a)` and `((?+1)?a((?-2)?b))`: every one names
     * `(a)(?-1)` or `(a)(a)(?-2)`. Two rows that could not be witnessed at all
     * is a worse outcome than one uniform axis. */
    opt.flags |= PCREC_NO_SPLICE_CALLS;
    memset(&out, 0, sizeof out);
    memset(&perr, 0, sizeof perr);
    bool okrefuse;
    if (pcrec_compile(pat, &opt, &out, &perr) == 0) {
        pcrec_output_free(&out);
        snprintf(msg, msgsz, "'%s' COMPILED under --engine=dfa", pat);
        okrefuse = false;
    } else if (!strstr(perr.msg, name) || !strstr(perr.msg, "--engine=dfa")) {
        snprintf(msg, msgsz,
                 "'%s' was refused under --engine=dfa but not BY ITS OWN NAME "
                 "('%s'): %.160s", pat, name, perr.msg);
        okrefuse = false;
    } else {
        /* The other direction: it must COMPILE on the default engine. */
        pcrec_default_options(&opt);
        memset(&out, 0, sizeof out);
        memset(&perr, 0, sizeof perr);
        if (pcrec_compile(pat, &opt, &out, &perr) != 0) {
            snprintf(msg, msgsz,
                     "'%s' does not compile on the DEFAULT engine (\"%.160s\"), "
                     "so the refusal proves nothing", pat, perr.msg);
            okrefuse = false;
        } else {
            pcrec_output_free(&out);
            okrefuse = true;
        }
    }
    pcrec_enabled_set_spec("none", err, sizeof err);
    return okrefuse;
}

static void check_engine_capability(void)
{
    /* THE HAND-WRITTEN WITNESSES. One per (kind, sel) with a wired producer.
     * `bites` is a pattern whose cut/write genuinely changes the language, so
     * no rewrite can discharge it; `name` is the text the refusal must contain,
     * which is `select_engine.c`'s `why` for that row. */
    /* [M6.5.2] `tail` JOINS THE KEY, and it is not decoration: the `\g`
     * doorway now holds THREE rows in one (RK_ESC, 'g') bucket — the
     * backreference half (no tail, module `backrefs`, wired) and the two
     * subroutine halves (tails `<` and `'`, module `recursion`, unwired) — so
     * a (kind, sel) key alone would hand a `recursion` row the `backrefs`
     * witness the day someone wires it. NULL matches any tail, which is what
     * every pre-existing row wants. */
    static const struct {
        RegKind     kind;
        int         sel;
        const char *tail;
        const char *feats;
        const char *bites;
        const char *name;
    } WITNESS[] = {
        /* `\K` moves the REPORTED START, which a subset state (a set, not a
         * path) cannot carry. Nothing discharges it. */
        { RK_ESC,         'K', NULL, "assertions",    "a\\Kb",           "\\K" },
        /* `(?>a|ab)c` on "abc" is (2,3) and `(?:a|ab)c` is (0,3): the cut
         * changes the LANGUAGE, so the discharge must decline it. */
        { RK_GROUP,       '>', NULL, "atomic-groups", "(?>a|ab)c",       "(?>...)" },
        /* The four possessive spellings, each over a body whose iteration can
         * end in two places — §2.2 refuses those, so the discharge does too.
         * `(?:a|ab)*+c` on "abc" is NOMATCH where `(?:a|ab)*c` is (0,3). */
        { RK_QUANTSUFFIX, '*', NULL, "atomic-groups", "(?:a|ab)*+c",     "possessive quantifier" },
        { RK_QUANTSUFFIX, '+', NULL, "atomic-groups", "(?:a|ab)++c",     "possessive quantifier" },
        { RK_QUANTSUFFIX, '?', NULL, "atomic-groups", "(?:a|ab)?+c",     "possessive quantifier" },
        { RK_QUANTSUFFIX, '{', NULL, "atomic-groups", "(?:a|ab){1,3}+c", "possessive quantifier" },
        /* [M6.5.2] THE TWELVE BACKREFS ROWS. Every witness here bites for the
         * same reason and it needs no cleverness: a backreference compares
         * SUBJECT TEXT to SUBJECT TEXT at a pair of positions the backtracking
         * state holds, which is not a regular construct at all — there is no
         * rewrite that discharges it (§6.3 measured the finite-language
         * expansion and DECLINED to ship it) and no flag that makes one
         * DFA-compilable.
         *
         * THE REFUSAL MUST NAME THE ROW, NOT THE CAPTURES, and that is the
         * property this check is really asserting for this module. Every
         * backreference pattern has `ncap > 0` by construction, so before
         * [M6.4.2]'s second-why fix `--engine=dfa '(a)\1'` would have taken
         * the CAPTURES branch and advised `--no-captures` — advice that does
         * not help, since `\1` still forces the VM after the captures are
         * gone. D67 contract note 1 is what makes these twelve name
         * themselves; twelve rows is also what made SR-8 the right build
         * rather than a third named exception.
         *
         * The digit witnesses declare exactly as many groups as they
         * reference, so each row's OWN number is the one that forces. */
        { RK_ESC, '1', NULL, "backrefs", "(a)\\1",                        "\\1" },
        { RK_ESC, '2', NULL, "backrefs", "(a)(b)\\2",                     "\\2" },
        { RK_ESC, '3', NULL, "backrefs", "(a)(b)(c)\\3",                  "\\3" },
        { RK_ESC, '4', NULL, "backrefs", "(a)(b)(c)(d)\\4",               "\\4" },
        { RK_ESC, '5', NULL, "backrefs", "(a)(b)(c)(d)(e)\\5",            "\\5" },
        { RK_ESC, '6', NULL, "backrefs", "(a)(b)(c)(d)(e)(f)\\6",         "\\6" },
        { RK_ESC, '7', NULL, "backrefs", "(a)(b)(c)(d)(e)(f)(g)\\7",      "\\7" },
        { RK_ESC, '8', NULL, "backrefs", "(a)(b)(c)(d)(e)(f)(g)(h)\\8",   "\\8" },
        { RK_ESC, '9', NULL, "backrefs", "(a)(b)(c)(d)(e)(f)(g)(h)(i)\\9", "\\9" },
        /* `\g` with NO tail is the backreference half; the two tailed rows in
         * this bucket are `recursion`'s. [DD-14 wave D] wired `pcrec_brport_g`
         * onto both, and they BITE for the same structural reason the `(?`
         * family below does — `\g<1>`/`\g'1'` re-run a group's pattern
         * dynamically, which is not a regular construct, so `select_engine.c`
         * refuses them by their own `syntax` and no rewrite discharges it. */
        { RK_ESC, 'g', "<", "recursion", "(a)\\g<1>", "\\g<1>" },
        { RK_ESC, 'g', "'", "recursion", "(a)\\g'1'", "\\g'1'" },
        /* [M6.6.2] THE THREE LOOKAHEAD ROWS. A lookaround BITES for a reason
         * that is not the cut's and not `\K`'s: it is a SUB-MATCH whose
         * verdict is kept and whose position is discarded, and a subset state
         * is a SET of positions with no way to run one and come back. Nothing
         * rewrites it away — `src/ir/nfa.c` lowers an `A_LOOK` to an EPSILON,
         * which is SOUND AS A PREFILTER and a MISCOMPILE AS A MACHINE, and
         * SR-8's stamp is the only thing that keeps those two readings apart
         * (lookaround_design.md §5.2).
         *
         * EVERY WITNESS IS CAPTURE-FREE, and that is required rather than
         * tidy: a capture-bearing pattern is VM-forced by the pre-existing
         * generic capture rule whatever this row's `engines` mask says, so
         * `(a)(?=b)c` would go green on a compiler whose stamp was gone. It
         * is the same masking `run_backref_diff.sh` had to design around one
         * module earlier, in the other direction. Sabotage row S126 flips the
         * `(?=...)` row's mask and `(?=a)b` is what sees it.
         *
         * AND WAVE D ADDED THE THREE LOOKBEHIND ROWS, WITH NO EDIT TO THE
         * GATE. At wave B+C these rows had no witness and MUST NOT have had
         * one: their shared port declined at `WANT_RESULT`, so there was no
         * artifact for `--engine=dfa` to refuse and no default-engine compile
         * to assert. The `built` gate excused them — and un-excused them the
         * moment the decline was deleted, which is exactly the property a
         * hand allowlist here would not have had. The three rows below are
         * what that demand was answered with. They are capture-free for the
         * same reason the lookahead witnesses are, and each one BITES: a
         * subset state is a set of positions, and there is no more a way to
         * run a body BACKWARD from one and come back than there is to run one
         * forward. `(?<*a)b` is the non-atomic spelling and bites identically
         * — atomicity is not what makes a lookaround VM-only. */
        { RK_GROUP, '=', NULL, "lookaround", "(?=a)b",   "(?=...)" },
        { RK_GROUP, '!', NULL, "lookaround", "(?!a)b",   "(?!...)" },
        { RK_GROUP, '*', NULL, "lookaround", "(?*a)b",   "(?*a)" },
        { RK_GROUP, '<', "=",  "lookaround", "(?<=a)b",  "(?<=...)" },
        { RK_GROUP, '<', "!",  "lookaround", "(?<!a)b",  "(?<!...)" },
        { RK_GROUP, '<', "*",  "lookaround", "(?<*a)b",  "(?<*a)" },
        /* [M6.6.2] WAVE F: THE TWELVE ALPHA SPELLINGS, one witness each, and
         * per-member is the requirement rather than per-family (D71 item 3
         * spells this out: SR-8 witnesses are owed per MEMBER). The reason is
         * the one this whole check exists for — the stamp is what carries
         * VM_ONLY into `select_engine.c`, and each alias row is a SEPARATE
         * `Ast.reg` value. A family-level witness would assert the primary's
         * stamp twelve times and prove nothing about the aliases; an alias
         * whose row lost its `engines` mask, or whose port forgot to stamp
         * with the row it was dispatched on, would go green.
         *
         * `name` IS THE ALIAS's OWN SYNTAX, not its primary's, and that is
         * the sharp end of this table for this wave: `--engine=dfa
         * '(*pla:a)b'` must name `(*pla:a)`. It does BECAUSE
         * `pcrec_laport_group` stamps `rw` — the row the doorway dispatched
         * on — rather than the primary it resolved the flags from. Those two
         * are deliberately different objects (mod_lookaround.c's `la_kind`
         * resolves the FLAGS through `family` and never replaces `rw`), and
         * these twelve rows are what asserts the difference is real: point
         * the stamp at the primary and all twelve of these fail by naming the
         * wrong construct, while every other check in the tree stays green.
         *
         * EVERY WITNESS IS CAPTURE-FREE, for the six `(?` witnesses' reason,
         * which does not weaken with the spelling: a capture-bearing pattern
         * is VM-forced by the generic capture rule whatever the row's mask
         * says, so `(a)(*pla:b)c` would go green on a compiler whose stamp
         * was gone.
         *
         * AND EACH ONE BITES, by the SAME argument as its primary's and not a
         * new one — a lookaround is a sub-match whose verdict is kept and
         * whose position is discarded, and a subset state is a set of
         * positions with no way to run one and come back. The alpha spelling
         * changes the parse and nothing else. */
        { RK_VERB, REG_SEL_ANY, "pla", "lookaround",
          "(*pla:a)b", "(*pla:a)" },
        { RK_VERB, REG_SEL_ANY, "positive_lookahead", "lookaround",
          "(*positive_lookahead:a)b", "(*positive_lookahead:a)" },
        { RK_VERB, REG_SEL_ANY, "nla", "lookaround",
          "(*nla:a)b", "(*nla:a)" },
        { RK_VERB, REG_SEL_ANY, "negative_lookahead", "lookaround",
          "(*negative_lookahead:a)b", "(*negative_lookahead:a)" },
        { RK_VERB, REG_SEL_ANY, "plb", "lookaround",
          "(*plb:a)b", "(*plb:a)" },
        { RK_VERB, REG_SEL_ANY, "positive_lookbehind", "lookaround",
          "(*positive_lookbehind:a)b", "(*positive_lookbehind:a)" },
        { RK_VERB, REG_SEL_ANY, "nlb", "lookaround",
          "(*nlb:a)b", "(*nlb:a)" },
        { RK_VERB, REG_SEL_ANY, "negative_lookbehind", "lookaround",
          "(*negative_lookbehind:a)b", "(*negative_lookbehind:a)" },
        { RK_VERB, REG_SEL_ANY, "napla", "lookaround",
          "(*napla:a)b", "(*napla:a)" },
        { RK_VERB, REG_SEL_ANY, "non_atomic_positive_lookahead", "lookaround",
          "(*non_atomic_positive_lookahead:a)b",
          "(*non_atomic_positive_lookahead:a)" },
        { RK_VERB, REG_SEL_ANY, "naplb", "lookaround",
          "(*naplb:a)b", "(*naplb:a)" },
        { RK_VERB, REG_SEL_ANY, "non_atomic_positive_lookbehind", "lookaround",
          "(*non_atomic_positive_lookbehind:a)b",
          "(*non_atomic_positive_lookbehind:a)" },
        /* [DD-14] WAVE B+C: MODULE `recursion`'s TWENTY-FOUR WIRED ROWS, one
         * witness each, and per-member for the reason the twelve alpha rows
         * above are per-member: the stamp is what carries VM_ONLY into
         * `select_engine.c` and each row is a separate `Ast.reg` value.
         *
         * EVERY ONE BITES, AND THE ARGUMENT IS THE SHARPEST IN THIS TABLE.
         * A subroutine call is VM_ONLY STRUCTURALLY rather than by a design
         * choice: the language `^(a(?1)?b)$` generates is a^n b^n, MEASURED
         * matching at n = 400,000, which is not regular — so unlike the atomic
         * group, whose VM_ONLY is too strong for a possessive the free
         * discharge proves dead, there is no rewrite that could discharge this
         * one and no flag that makes it DFA-compilable. The refusal must
         * therefore name the CONSTRUCT and never advise `--no-captures`, which
         * is D44.6/§9.2 item 2's rule and what `EngineAnalysis.node_derived`
         * exists to keep true.
         *
         * TWO OF THEM ARE CAPTURE-FREE AND THE OTHER TWENTY-TWO CANNOT BE,
         * which is a departure from every witness above and is a property of
         * the CONSTRUCT rather than a weakening of the check. `(?R)` and
         * `(?0)` call the WHOLE PATTERN, so `a(?R)?b` has no capturing group
         * at all and is VM-forced by NOTHING BUT THE STAMP — the sharp form.
         * Every other spelling names a GROUP, so a witness for `(?1)` must
         * contain one by construction.
         *
         * THE TWENTY-TWO STILL FIRE, and the reason is worth stating because
         * the comment on the `(?` witnesses above says capture-freedom is
         * "required": what that paragraph is really about is the MESSAGE. A
         * capture-bearing pattern is VM-forced by the generic capture rule too,
         * but the two forcings produce DIFFERENT TEXT — the captures arm says
         * "pass --no-captures" and names no construct — so a compiler whose
         * stamp was gone fails `strstr(perr.msg, name)` and this check goes
         * RED rather than green. The capture-free pair above is what makes
         * that argument checkable rather than merely stated: if the stamp
         * vanished, those two would not be refused at all.
         *
         * `name` IS THE ROW'S OWN `syntax`, verbatim, because that is what
         * `select_engine.c` puts in `why` — which for the relative family
         * means the witness and the name are the same string (`(a)(?-1)`), and
         * for `(?N)` means the witness must supply N groups. */
        { RK_GROUP, 'R', NULL, "recursion", "a(?R)?b",      "(?R)" },
        { RK_GROUP, '0', NULL, "recursion", "a(?0)?b",      "(?0)" },
        { RK_GROUP, '1', NULL, "recursion", "(a)(?1)",      "(?1)" },
        { RK_GROUP, '2', NULL, "recursion", "(a)(b)(?2)",   "(?2)" },
        { RK_GROUP, '3', NULL, "recursion", "(a)(b)(c)(?3)", "(?3)" },
        { RK_GROUP, '4', NULL, "recursion", "(a)(b)(c)(d)(?4)", "(?4)" },
        { RK_GROUP, '5', NULL, "recursion", "(a)(b)(c)(d)(e)(?5)", "(?5)" },
        { RK_GROUP, '6', NULL, "recursion", "(a)(b)(c)(d)(e)(f)(?6)", "(?6)" },
        { RK_GROUP, '7', NULL, "recursion", "(a)(b)(c)(d)(e)(f)(g)(?7)", "(?7)" },
        { RK_GROUP, '8', NULL, "recursion", "(a)(b)(c)(d)(e)(f)(g)(h)(?8)", "(?8)" },
        { RK_GROUP, '9', NULL, "recursion", "(a)(b)(c)(d)(e)(f)(g)(h)(i)(?9)", "(?9)" },
        { RK_GROUP, '+', NULL, "recursion", "(?+1)(a)",     "(?+1)(a)" },
        { RK_GROUP, '-', "0",  "recursion", "(a)(?-01)",    "(a)(?-01)" },
        { RK_GROUP, '-', "1",  "recursion", "(a)(?-1)",     "(a)(?-1)" },
        { RK_GROUP, '-', "2",  "recursion", "(a)(a)(?-2)",  "(a)(a)(?-2)" },
        { RK_GROUP, '-', "3",  "recursion", "(a)(a)(a)(?-3)", "(a)(a)(a)(?-3)" },
        { RK_GROUP, '-', "4",  "recursion", "(a)(a)(a)(a)(?-4)",
          "(a)(a)(a)(a)(?-4)" },
        { RK_GROUP, '-', "5",  "recursion", "(a)(a)(a)(a)(a)(?-5)",
          "(a)(a)(a)(a)(a)(?-5)" },
        { RK_GROUP, '-', "6",  "recursion", "(a)(a)(a)(a)(a)(a)(?-6)",
          "(a)(a)(a)(a)(a)(a)(?-6)" },
        { RK_GROUP, '-', "7",  "recursion", "(a)(a)(a)(a)(a)(a)(a)(?-7)",
          "(a)(a)(a)(a)(a)(a)(a)(?-7)" },
        { RK_GROUP, '-', "8",  "recursion", "(a)(a)(a)(a)(a)(a)(a)(a)(?-8)",
          "(a)(a)(a)(a)(a)(a)(a)(a)(?-8)" },
        { RK_GROUP, '-', "9",  "recursion", "(a)(a)(a)(a)(a)(a)(a)(a)(a)(?-9)",
          "(a)(a)(a)(a)(a)(a)(a)(a)(a)(?-9)" },
        { RK_GROUP, '&', NULL, "recursion,named-groups", "(?<n>a)(?&n)",
          "(?&name)" },
        { RK_GROUP, 'P', ">",  "recursion,named-groups", "(?<n>a)(?P>n)",
          "(?P>n)" },
        { RK_ESC,   'g', NULL, "backrefs",              "(a)\\g{-1}",       "\\g{-1}" },
        { RK_ESC,   'k', NULL, "backrefs,named-groups", "(?<n>a)\\k<n>",    "\\k<name>" },
        { RK_GROUP, 'P', "=",  "backrefs,named-groups", "(?<n>a)(?P=n)",    "(?P=n)" },
    };

    int qualifying = 0, wired = 0, built_wired = 0, checked = 0, bads = 0;
    char msg[320];

    if (pcrec_enabled_mask() != 0) {
        bad("engine capability: the enabled mask was already non-empty (0x%x) "
            "before this check, so this file's other checks did not run at the "
            "default set they assume and it cannot safely restore it",
            pcrec_enabled_mask());
        return;
    }

    for (int k = 0; k < RK_COUNT; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry((RegKind)k, &n);
        if (!rows) continue;
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            if (r->status != RS_MODULE || (r->engines & ENGM_DFA)) continue;
            qualifying++;
            /* HAS A PRODUCER. `aport` is the wiring for a DOORWAY row; an
             * RK_QUANTSUFFIX row has no port BY DESIGN (it reaches no doorway)
             * and its producer is `p_rep`'s desugaring in src/parse/parse.c, so
             * the kind itself is the signal. Class-position ports are excluded
             * for the retired tripwire's own reason: a `cport` can never carry
             * a VM_ONLY construct into the AST. */
            bool has_producer = r->aport.kind != PORT_NONE
                             || r->kind == RK_QUANTSUFFIX;
            if (!has_producer) continue;
            wired++;

            /* [M6.6.2] A WIRED PORT IS NOT THE SAME FACT AS A BUILT
             * CONSTRUCT, and until this wave nothing in the tree could tell
             * them apart because no module had ever wired ONE port for
             * constructs it lands in TWO waves. Module `lookaround` does:
             * `pcrec_laport_group` serves all six rows and DECLINES the three
             * `(?<` tails at `WANT_RESULT` until wave D lands the back-step
             * (lookaround_design.md §8.3). A declining producer produces
             * nothing, so there is no artifact for `--engine=dfa` to refuse
             * and no default-engine compile to assert alongside it — a witness
             * for such a row could not be written, and demanding one would
             * make this check fire on a tree that is behaving exactly as
             * designed.
             *
             * SO THE WITNESS REQUIREMENT IS GATED ON D65's `built` COLUMN,
             * which is the tree's one authoritative answer to "does this
             * construct compile" and is DERIVED per row at call time rather
             * than declared (src/parse/syntax_dump.c). It is not a weakening:
             * the row is still walked and still counted, the gate is the same
             * derivation `--list-syntax` prints, and the day wave D deletes
             * the port's decline these three rows start demanding witnesses
             * again WITH NO EDIT HERE. A hand allowlist would not have had
             * that property, which is exactly the difference this file's own
             * header draws between iteration and a hand list. */
            if (pcrec_construct_built_status(r) != PCREC_BUILT_YES) continue;
            built_wired++;

            const char *bites = NULL, *name = NULL, *feats = NULL;
            for (size_t w = 0; w < sizeof WITNESS / sizeof WITNESS[0]; w++) {
                if (WITNESS[w].kind != r->kind || WITNESS[w].sel != r->sel)
                    continue;
                /* A witness with a tail matches only a row with that exact
                 * tail; a witness with none matches any. */
                if (WITNESS[w].tail &&
                    (!r->tail || strcmp(WITNESS[w].tail, r->tail) != 0))
                    continue;
                if (!WITNESS[w].tail && r->tail)
                    continue;
                bites = WITNESS[w].bites; name = WITNESS[w].name;
                feats = WITNESS[w].feats;
                break;
            }
            if (!bites) {
                bad("engine capability: '%s' (module '%s') is VM_ONLY and has "
                    "a WIRED PRODUCER, but no witness names it in this check. "
                    "SR-8's consultation (src/opt/select_engine.c's "
                    "forces_registry) is what refuses such a construct under "
                    "--engine=dfa; add a pattern whose cut/write genuinely "
                    "bites, so the refusal is asserted rather than assumed",
                    r->syntax, r->module ? r->module : "(none)");
                bads++;
                continue;
            }
            checked++;
            if (!eng_refuses_by_name(feats, bites, name, msg, sizeof msg)) {
                bad("engine capability: '%s' (module '%s'): %s", r->syntax,
                    r->module, msg);
                bads++;
            }
        }
    }

    /* EXACT, this file's own convention. 48 -> 52 at [M6.4.2] (the four
     * RK_QUANTSUFFIX rows, all VM_ONLY); 1 -> 6 wired (`\K` since [M6.2] wave
     * E, plus `(?>` and the four suffix rows).
     *
     * 52 -> 54 and 6 -> 18 at [M6.5.2]. The two ADDED rows are `\g<` and
     * `\g'`, module `recursion`, VM_ONLY and unwired. The TWELVE newly wired
     * are backrefs' — and they KEEP `VM_ONLY` rather than reclassifying the
     * way `named-groups`' three rows did (D59 part 2), because those rows
     * genuinely lower to both engines and these genuinely do not: a
     * backreference is not a regular construct, so the column cannot be made
     * true by editing it. That twelve, measured by this lane against its own
     * design, is what turned SR-8 from "a third named exception" into D67's
     * generic build.
     *
     * 18 -> 24 WIRED at [M6.6.2] wave B+C, of which 21 were BUILT. All six
     * added rows are module `lookaround`'s and all six share ONE port, so
     * `wired` moved by six while `built_wired` moved by three — the first time
     * this file had been able to tell those two facts apart, and the reason
     * the third number exists. `qualifying` did NOT move: the six rows were
     * already VM_ONLY and already RS_MODULE; that wave gave them a producer,
     * not a classification.
     *
     * 21 -> 24 BUILT at WAVE D, and `wired` does not move with it. Wave D
     * deleted the port's `<`-tail decline when the back-step seam entry
     * landed, so the three lookbehind rows became BUILT and started demanding
     * witnesses — automatically, with no edit to the gate — and the three
     * witnesses above are what answers that demand. `wired` staying at 24 and
     * `built_wired` moving to meet it is this check's own record of what the
     * wave did: the same six ports, three more of them producing.
     *
     * THE THIRD NUMBER IS WHAT KEEPS THE GATE HONEST. `built_wired` is the
     * count that must equal `checked`, so a `built` gate that quietly excused
     * a row it should have checked shows up as a MISSING WITNESS rather than
     * as a smaller pass. With `built_wired == wired` there is now nothing left
     * for the gate to excuse in this module, which is the state the split was
     * built to reach and to be able to assert.
     *
     * A deliberate move edits these numbers in the same change; a silent one
     * is the defect. */
    /* 54 -> 66 QUALIFYING, 24 -> 36 WIRED and 24 -> 36 BUILT at WAVE F, all
     * three by the same twelve rows and all three for the first time
     * together: the alpha spellings arrive VM_ONLY (qualifying), with the
     * shared port already in their `aport` (wired), and producing on their
     * first call (built). `built_wired == wired` still holds, which is the
     * state the third number was split out to be able to assert — there is
     * nothing left for the `built` gate to excuse in this module. */
    /* [DD-14] WAVE B+C: `wired` and `built_wired` 36 -> 60, `qualifying`
     * UNMOVED at 66 — and the three moving differently is the whole reason the
     * third number was split out. The twenty-four `(?` recursion rows were
     * ALREADY VM_ONLY and already RS_MODULE (P4 measured all 26 that way
     * before any of this module existed), so this wave gave them a PRODUCER
     * and not a classification. All twenty-four BUILD on their first call,
     * unlike wave B+C's lookaround six, because these ports have no tail left
     * to decline.
     *
     * AT WAVE B+C, THE TWO ROWS THAT DID NOT MOVE WERE THE INTERESTING HALF.
     * `\g<1>` and `\g'1'` are module `recursion`'s too, they are inside
     * `qualifying`, and they were deliberately NOT wired: design §8.1
     * required them to stay `unbuilt` until wave D, because D65 flips `built`
     * from the PORT's answer and a wave that flipped them while the emitter
     * could not compile the spelling would ship a compliance index that lies.
     * So `wired` and `built_wired` moved by 24 while `qualifying` held at 66.
     *
     * [DD-14] WAVE D: `wired` and `built_wired` 60 -> 62, `qualifying`
     * UNMOVED at 66. `pcrec_brport_g` gained the `<`/`'` arms
     * (`src/parse/mod_backrefs.c`) and both rows' `aport` now points at it
     * (`src/parse/registry.c`), so both WIRE and both BUILD on their first
     * call — no tail left to decline, the same shape wave B+C's other
     * twenty-four rows already had. The gap between `wired` and `qualifying`
     * is now only the unbuilt population outside this module. */
    /* [DD-14] WAVE F: `qualifying` 66 -> 75, `wired` and `built_wired`
     * UNMOVED at 62 — and this is the FIRST wave where qualifying moves alone.
     * The nine new rows are RS_MODULE and VM_ONLY (they are subroutine-call
     * spellings, so the structural argument is their primaries' verbatim), and
     * they have NO PORT: an RF_INDEX row is never elected, so it can have no
     * producer of its own and this check must not demand a witness for one.
     * The witness for what those spellings actually do is their PRIMARY's,
     * which is already in the table above, plus `check_index_shape_witnesses`
     * below — D71 item 3's per-RESOLVER-DISTINGUISHED-SHAPE requirement,
     * which is a different demand from this loop's per-wired-row one. */
    if (qualifying != 75 || wired != 62 || built_wired != 62)
        bad("engine capability: %d RS_MODULE rows exclude ENGM_DFA, %d of them "
            "have a wired producer and %d of THOSE are BUILT, expected 75, 62 "
            "and 62 -- the VM_ONLY population, its producer set or its built "
            "set moved", qualifying, wired, built_wired);
    else if (checked != built_wired)
        bad("engine capability: %d rows are VM_ONLY, wired AND built, but only "
            "%d were checked against a witness -- the difference is rows the "
            "`built` gate excused that it should not have", built_wired,
            checked);
    else if (bads == 0) {
        char label[512];
        snprintf(label, sizeof label,
                 "engine capability: all %d wired-AND-BUILT VM_ONLY producers "
                 "refuse --engine=dfa BY NAME on a witness whose cut bites, "
                 "and every witness compiles on the default engine (of %d "
                 "wired and %d VM_ONLY rows; %d wired-but-UNBUILT, since "
                 "[M6.6.2] wave D built module `lookaround`'s three "
                 "lookbehinds and they gained witnesses with no edit to the "
                 "`built` gate; SR-8 is BUILT, so the [M4.7a] tripwire and "
                 "its \\K exception are RETIRED -- D67)",
                 checked, qualifying, wired, wired - built_wired);
        ok(label);
    }

    if (pcrec_enabled_mask() != 0)
        bad("engine capability: the enabled set was not restored (0x%x)",
            pcrec_enabled_mask());
}

/* THE PER-PATTERN SPLIT, asserted in the direction the column cannot state.
 *
 * `engines` is a per-CONSTRUCT column and the answer is a per-PATTERN fact:
 * VM_ONLY is too STRONG for `a*+b`, whose cut the free discharge PROVES dead,
 * and ANY_ENGINE would be too WEAK for `(?>a|ab)c`, which nothing but the VM
 * can compile. The check above asserts the second half. This asserts the first,
 * which is the half that would silently disappear if the discharge stopped
 * firing — nothing else in the tree would notice, because every answer would
 * still be correct and only the ENGINE would change. Sabotage row S91 is the
 * other direction (the discharge firing unconditionally), which the corpus
 * catches. */
/* ---- [DD-14 wave F / D71 item 3] SR-8 PER RESOLVER-DISTINGUISHED SHAPE ----
 *
 * `check_engine_capability` above demands a witness PER WIRED ROW, and it is
 * right to: the stamp is what carries VM_ONLY into `select_engine.c` and each
 * wired row is a separate `Ast.reg` value. An RF_INDEX row has no producer, so
 * that loop skips it — correctly, since there is no stamp of its own to test.
 *
 * BUT D71 ITEM 3 MAKES A SECOND, DIFFERENT DEMAND, and it is the one this
 * wave's rows exist for: "SR-8 witnesses are required per RESOLVER-
 * DISTINGUISHED SHAPE (`(?1)` `(?01)` `(?10)` `(?00)`), not per digit". Those
 * four shapes are ONE row's worth of dispatch and FOUR different answers from
 * the port that reads the digit run, which is precisely the population a
 * per-row loop cannot see: `(?01)` and `(?00)` enter the SAME `(?0)` row and
 * mean GROUP 1 and THE ROOT respectively (design §2.4a's anchored
 * discriminator). A check keyed on rows would witness that byte once.
 *
 * THE EXPECTED NAME IS DERIVED, NOT WRITTEN, and that is the point of the
 * design. The hand-written half is only the WITNESS PATTERN — a compilable
 * context for a spelling that names groups. What the refusal must SAY is
 * asked of `pcrec_registry_arbitrate`, the same engine the doorway calls:
 * whichever row that elects for the spelling is the row `select_engine.c`
 * stamps, so its `syntax` is the text `why` must carry. A row whose index
 * `family` disagreed with where its spelling actually dispatches would be
 * invisible to a hand-written name and is caught here — which is exactly the
 * `(?01)` case, whose family is `(?1)` (it means group 1) while its dispatch
 * is `(?0)`'s (it enters on the zero byte). Both facts are true, they are
 * DIFFERENT facts, and D71 item 3's whole content is that the table had been
 * conflating them.
 *
 * BOTH DIRECTIONS, `eng_refuses_by_name`'s own rule: the witness must be
 * REFUSED by name under --engine=dfa AND must COMPILE on the default engine,
 * so a compiler that stopped accepting these spellings altogether goes RED
 * rather than green.
 *
 * THREE OF THE NINE ARE CAPTURE-FREE (`a(?00)?b`, `a\g<0>?b`, `a\g'0'?b`) and
 * that is the sharp form: a capture-bearing pattern is VM-forced by the
 * generic capture rule whatever the stamp says, so those three are the ones
 * that would not be refused AT ALL if the stamp vanished. The other six name
 * groups by construction and cannot be capture-free. */
static void check_index_shape_witnesses(void)
{
    /* The hand-written half: a COMPILABLE context per index-row spelling.
     * Keyed on the row's own `syntax` so a row added without a witness is a
     * named failure rather than a silently smaller pass. */
    static const struct { const char *syntax; const char *witness; } SHAPE[] = {
        { "(?10)",  "(a)(a)(a)(a)(a)(a)(a)(a)(a)(a)(?10)" },
        { "(?01)",  "(a)(?01)" },
        { "(?00)",  "a(?00)?b" },
        { "(?+2)(a)(b)", "(?+2)(a)(b)" },
        { "(a)(a)(a)(a)(a)(a)(a)(a)(a)(a)(?-10)",
          "(a)(a)(a)(a)(a)(a)(a)(a)(a)(a)(?-10)" },
        { "\\g<0>",  "a\\g<0>?b" },
        { "\\g<01>", "(a)\\g<01>" },
        { "\\g'0'",  "a\\g'0'?b" },
        { "\\g'01'", "(a)\\g'01'" },
    };

    int seen = 0, checked = 0, bads = 0, capfree = 0;
    char msg[320];

    for (int k = 0; k < RK_COUNT; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry((RegKind)k, &n);
        if (!rows) continue;
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            if (!(r->flags & RF_INDEX)) continue;
            if (!r->module || strcmp(r->module, "recursion") != 0) continue;
            seen++;

            const char *wit = NULL;
            for (size_t w = 0; w < sizeof SHAPE / sizeof SHAPE[0]; w++)
                if (strcmp(SHAPE[w].syntax, r->syntax) == 0)
                    { wit = SHAPE[w].witness; break; }
            if (!wit) {
                bad("index shape witness: row '%s' (module 'recursion') has no "
                    "witness here. D71 item 3 owes SR-8 a witness per "
                    "resolver-distinguished shape; add a compilable context "
                    "for this spelling", r->syntax);
                bads++;
                continue;
            }

            /* THE DERIVED NAME. Find the row's OWN doorway inside its syntax —
             * the LAST occurrence, since the relative spellings carry their
             * capture-group context in front of the construct — then ask the
             * arbitration engine which row that text elects. */
            char needle[4];
            if (r->kind == RK_GROUP) { needle[0]='('; needle[1]='?';
                                       needle[2]=(char)r->sel; needle[3]=0; }
            else                     { needle[0]='\\'; needle[1]=(char)r->sel;
                                       needle[2]=0; }
            const char *doorway = NULL;
            for (const char *q = r->syntax; (q = strstr(q, needle)) != NULL; q++)
                doorway = q;
            if (!doorway) {
                bad("index shape witness: row '%s' does not contain its own "
                    "doorway text \"%s\", so the dispatching row cannot be "
                    "derived", r->syntax, needle);
                bads++;
                continue;
            }
            const char *at = doorway + strlen(needle);
            bool amb = false;
            const RegRow *disp = pcrec_registry_arbitrate((RegKind)r->kind,
                                                          r->sel, at,
                                                          strlen(at), &amb);
            if (!disp || amb || (disp->flags & RF_INDEX)) {
                bad("index shape witness: '%s' arbitrates to %s -- an index "
                    "row's spelling must elect a REAL dispatching row (never "
                    "itself, never ambiguously), or there is no producer for "
                    "it and `built` is a lie", r->syntax,
                    amb ? "AMBIGUOUS" : disp ? "an index row" : "nothing");
                bads++;
                continue;
            }

            if (!strchr(wit, '('))              capfree++;
            else if (!strstr(wit, "(a)") && !strstr(wit, "(b)")) capfree++;

            checked++;
            if (!eng_refuses_by_name("recursion,named-groups", wit,
                                     disp->syntax, msg, sizeof msg)) {
                bad("index shape witness: '%s' (dispatches on '%s'): %s",
                    r->syntax, disp->syntax, msg);
                bads++;
            }
        }
    }

    /* EXACT, this file's convention: the nine spellings design §8.1's four
     * missing families are made of. A deliberate move edits this number in
     * the same change. */
    if (seen != 9)
        bad("index shape witness POPULATION MOVED: %d RF_INDEX rows in module "
            "`recursion`, expected 9 -- the four families design §8.1 named "
            "changed shape. Counted from the ROWS, not from the passes, so a "
            "witness that fails does not also report a moved population",
            seen);
    else if (bads == 0) {
        char label[288];
        snprintf(label, sizeof label,
                 "index shape witnesses: all %d of module `recursion`'s "
                 "resolver-distinguished spellings compile on the default "
                 "engine and are refused under --engine=dfa BY THE NAME THE "
                 "ARBITRATION ENGINE DERIVES for them (D71 item 3), %d of "
                 "them capture-free", checked, capfree);
        ok(label);
    }
}

static void check_free_discharge(void)
{
    static const char *const DISCHARGES[] = {
        "a*+b",       /* the canonical idiom family */
        "a++c",
        "[^\"]*+\"",
        "(?>a*)b",    /* the same thing spelled as a group */
    };
    char err[256], msg[256];
    int done = 0;

    if (pcrec_enabled_set_spec("atomic-groups", err, sizeof err) != 0) {
        bad("free discharge: could not enable module 'atomic-groups': %s", err);
        return;
    }
    for (size_t i = 0; i < sizeof DISCHARGES / sizeof DISCHARGES[0]; i++) {
        pcrec_options opt;
        pcrec_output  out;
        pcrec_error   perr;
        pcrec_default_options(&opt);
        opt.engine = PCREC_ENGINE_DFA;
        opt.flags |= PCREC_NO_CAPTURES;
        memset(&out, 0, sizeof out);
        memset(&perr, 0, sizeof perr);
        if (pcrec_compile(DISCHARGES[i], &opt, &out, &perr) != 0) {
            bad("free discharge: '%s' was REFUSED under --engine=dfa (\"%s\"). "
                "Its §2.2 verdict is positive, so pcrec_discharge_atomic must "
                "delete the cut BEFORE SR-8's consultation runs -- that is the "
                "whole per-pattern split, and without it the `engines` column's "
                "VM_ONLY is simply too strong", DISCHARGES[i], perr.msg);
        } else {
            pcrec_output_free(&out);
            done++;
        }
    }
    pcrec_enabled_set_spec("none", err, sizeof err);
    (void)msg;
    if (done == (int)(sizeof DISCHARGES / sizeof DISCHARGES[0])) {
        char label[224];
        snprintf(label, sizeof label,
                 "free discharge: all %d provably-dead cuts compile to a PURE "
                 "DFA under --engine=dfa, so VM_ONLY is a per-row fact and the "
                 "post-discharge tree is the per-pattern answer", done);
        ok(label);
    }
}

static void check_class_syntax_reach(void)
{
    size_t n;
    const RegRow *rows = pcrec_registry(RK_ESC, &n);
    int probed = 0, bads = 0;

    for (size_t i = 0; i < n; i++) {
        const RegRow *r = &rows[i];
        /* [DD-14 wave F] "which row does this text elect at class position"
         * is a dispatch question, and an RF_INDEX row is never elected
         * anywhere (D71 item 3) — it would fail this check by definition. */
        if ((r->flags & RF_INDEX) != 0) continue;
        if (r->cport.base) continue;
        if (r->status != RS_MODULE) continue;
        bool has_tail = r->tail != NULL;
        bool body_carrying = strlen(r->syntax) > 2;   /* not a bare "\X" */
        if (!has_tail && !body_carrying) continue;

        const char *body = r->syntax + 2;   /* skip "\<sel>" */
        size_t bodylen = strlen(body);

        bool amb = false;
        const RegRow *got = pcrec_registry_arbitrate(RK_ESC, r->sel, body,
                                                      bodylen, &amb);
        probed++;
        if (amb) {
            bad("class-position reach: '%s' arbitrates AMBIGUOUS at class "
                "position (two rows answer at the winning rank)", r->syntax);
            bads++;
            continue;
        }
        if (got != r) {
            bad("class-position reach: '%s' arbitrates to a DIFFERENT row "
                "(sel '%c') than the one whose syntax this is — a class "
                "probe using this text would be attributed to the wrong "
                "construct", r->syntax, r->sel);
            bads++;
            continue;
        }
        char pat[64], got_msg[256];
        snprintf(pat, sizeof pat, "[%s]", r->syntax);
        /* DELIBERATE TIME BOMB (R19 checks critic): `!rejected` below is
         * unconditional, correct while no unicode-props/ctrl/octal producer
         * exists. The FIRST real cport on any of these five rows makes its
         * probe COMPILE and this check fail — that failure is the signal to
         * rewrite this check for the produced path in the same change, not
         * to exempt the row. */
        int rejected = try_compile(pat, got_msg, sizeof got_msg) != 0;
        if (!rejected || !strstr(got_msg, "requires module") ||
            !strstr(got_msg, r->module)) {
            bad("class-position reach: '%s' arbitrates to the right row but "
                "the compiled diagnostic (\"%s\") does not promise module "
                "'%s'", r->syntax, rejected ? got_msg : "(compiled)", r->module);
            bads++;
        }
    }

    /* EXACT, not a floor (matching check_class_ports' own convention just
     * above): the population is small and every member is named here
     * rather than merely counted, so a silent add/remove is visible in a
     * diff of THIS number. Measured today (RK_ESC, RS_MODULE, non-base
     * cport, tail or body-carrying syntax): the `{U+` row, `\p`, `\P`,
     * `\c`, `\o`. `\g`/`\k` are correctly excluded — base class ports,
     * excused above with the reason. A deliberate table change edits this
     * count in the same commit; a silent one is the defect. */
    if (probed != 5)
        bad("class-position reach: %d rows probed, expected 5 (the `{U+` "
            "row, \\p, \\P, \\c, \\o) — the tailed/body-carrying population "
            "moved. If deliberate, update this number in the same change",
            probed);
    else if (bads == 0)
        ok("class-position reach: 5 tailed/body-carrying rows ({U+, \\p, "
           "\\P, \\c, \\o) all reach themselves and promise their own "
           "module in a class");
}

/* ---- D65: the BUILT-STATUS defect assertion ------------------------------
 *
 * docs/design/registry_built_status_memo.md, ratified wholesale (D65,
 * 2026-08-21), recommendation 3: a registry_check DEFECT ASSERTION, not a
 * rendered value. `pcrec_construct_built_status` (src/parse/syntax_dump.c)
 * classifies every RS_MODULE row's own well-formed `syntax` as built or
 * unbuilt by driving it through a gate-forced-open doorway call; a row that
 * lands in NEITHER bucket (`PCREC_BUILT_DEFECT`) means that call did not
 * behave the way every OTHER row's does, for a `syntax` SR-1's own rule
 * already requires to reach its doorway — a registry defect, not a status
 * `--list-syntax`/the generated compliance index may silently render.
 *
 * Sabotage-validated in both directions (docs/design/registry_built_status_memo.md's
 * implementation record carries the measurements): a row's `aport` forced to
 * `NO_PORT` flips its column to `unbuilt` (a real refusal, not a defect —
 * this check stays green, exactly as it should, since "not yet built" is
 * not a defect); a row's `syntax` corrupted so it no longer reaches its own
 * doorway (SR-1's own precondition broken) flips the column to `defect`,
 * which THIS check catches. */
static void check_built_status_defects(void)
{
    /* [M6.4.2] RK_QUANTSUFFIX joins, and the derivation needed a NEW ARM to
     * classify it at all: `doorway_route` recognises four prefixes and a row
     * whose syntax is `a*+` routes nowhere, so before that arm these four rows
     * derived to PCREC_BUILT_DEFECT — the failure this check reports. See
     * `built_status_probe`'s non-doorway arm in src/parse/syntax_dump.c. */
    static const RegKind kinds[] = { RK_ESC, RK_GROUP, RK_VERB, RK_CLASSBRACKET,
                                     RK_QUANTSUFFIX };
    unsigned mask_before = pcrec_enabled_mask();
    int checked = 0, built = 0, unbuilt = 0, na = 0, defects = 0;

    for (size_t k = 0; k < sizeof kinds / sizeof kinds[0]; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry(kinds[k], &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            PcrecBuiltStatus bs = pcrec_construct_built_status(r);
            checked++;
            switch (bs) {
            case PCREC_BUILT_NA:   na++;      break;
            case PCREC_BUILT_YES:  built++;   break;
            case PCREC_BUILT_NO:   unbuilt++; break;
            case PCREC_BUILT_DEFECT:
                defects++;
                bad("built-status defect: '%s' (module '%s') answers "
                    "NEITHER built nor unbuilt for its own syntax — "
                    "pcrec_construct_built_status could not classify a row "
                    "SR-1 requires to reach its own doorway", r->syntax,
                    r->module ? r->module : "(none)");
                break;
            default:
                defects++;
                bad("built-status defect: '%s' returned an unrecognised "
                    "PcrecBuiltStatus value", r->syntax);
            }
        }
    }

    /* THE RESTORE, asserted rather than trusted (pcre2_check.c's own "gated
     * pass" rule, tests/registry/CLAUDE.md's "THE ENABLED SET IS FOCUSED"):
     * `pcrec_construct_built_status` mutates the process-global enabled set
     * once per row and restores it before returning, so after CHECKED calls
     * the mask must read exactly what it did before the first one. */
    if (pcrec_enabled_mask() != mask_before)
        bad("built-status defect: the enabled set was 0x%x before %d "
            "pcrec_construct_built_status calls and is 0x%x after — a "
            "restore was lost", mask_before, checked, pcrec_enabled_mask());
    /* [M6.4.2] THE TALLIES ARE EXACT, not merely defect-free, and that is a
     * CROSS-MODULE obligation rather than this module's bookkeeping.
     *
     * "0 defects" is satisfied by a table in which a construct SILENTLY STOPPED
     * BEING BUILT: `built` drops, `unbuilt` rises, the sum is unchanged and
     * nothing goes red. That is the direction that matters here, because the
     * generated compliance index in docs/pcre2_compliance.md renders this
     * column, so a construct quietly reverting to `unbuilt` is a documentation
     * regression nothing else in the tree can see. Pinning the three numbers
     * makes any movement — in either direction, by any module — a named
     * failure in the commit that causes it.
     *
     * THE FIGURES ARE FROM A RUN, not derived: 104 rows = 38 built + 60
     * unbuilt + 6 n/a, measured on this tree after [M6.4.2]. The 38 is the
     * pre-module 33 plus five — `(?>...)` and the four RK_QUANTSUFFIX rows.
     * The 6 n/a are the RS_BASE/RS_REJECTED rows, where the question does not
     * arise. Bumping these is deliberate and belongs in the same commit as the
     * producer that moves them.
     *
     * [M6.5.2]: 106 rows = 52 built + 48 unbuilt + 6 n/a, re-derived from a
     * run rather than predicted. FOURTEEN rows flip to `built` — the twelve
     * VM_ONLY ones the engine-capability check counts, PLUS `\0` (module
     * `backrefs`, but ANY_ENGINE, because it produces an ordinary character
     * and is not one of the twelve) PLUS `(?J)` (module `modifiers`, whose
     * letter this module builds). TWO rows are ADDED born UNBUILT (`\g<`,
     * `\g'`), so unbuilt is 60 - 14 + 2 = 48.
     *
     * THE TWO POPULATIONS ARE DIFFERENT SETS and saying so is the point: the
     * engine-capability check counts RS_MODULE rows whose `engines` mask
     * EXCLUDES the DFA (54 of them), while this tally counts every RS_MODULE
     * row plus the 6 n/a. The first is a subset of the second, they move for
     * different reasons, and an earlier prediction that used one number for
     * both was wrong twice.
     *
     * FOUR OF THESE ROWS CLASSIFY `built` ONLY BECAUSE OF §5.3's DEFERRAL, and
     * that dependency is real rather than incidental: `\1`, `\g{-1}`,
     * `\k<name>` and `(?P=n)` are all error-115-class STANDALONE in PCRE2 (no
     * such group), and the derivation drives each row's `syntax` ALONE. They
     * produce a node because module `backrefs` defers reference VALIDITY to
     * end of parse, and the classifier reads `ExtResult.answered_at`, not the
     * eventual verdict. The `\g` row is where that stopped being theoretical:
     * while its relative resolution refused AT THE PORT it read `unbuilt`, and
     * the fix was to give "does this number name a group" ONE home. */
    /* [M6.6.2] wave B+C: 52 + 48 -> 55 + 45, and the SHAPE is what design §8.3
     * committed to in advance rather than the number. THREE rows move
     * `unbuilt -> built` — `(?=...)`, `(?!...)` and `(?*a)` — ZERO move the
     * other way, the total is unchanged at 106, and NO ROW OUTSIDE MODULE
     * `lookaround` MOVES. In particular the three lookbehind rows STAY
     * `unbuilt`: the module's one shared port declines their tails at
     * `WANT_RESULT`, which is precisely what D65 derives the column from, and
     * "all six at once" would have been a property of a port with no tail
     * check rather than of D65. The `(?(` conditional-group row stays unbuilt
     * too (R33 C1-9) — a reader must not take these three as unlocking
     * assertion-conditions.
     *
     * [M6.6.2] WAVE D: 55 + 45 -> 58 + 42, and the SHAPE is again what was
     * committed to in advance. The remaining THREE lookaround rows move
     * `unbuilt -> built` — `(?<=...)`, `(?<!...)`, `(?<*a)` — because the port
     * stopped declining their tails when the back-step seam entry landed, ZERO
     * move the other way, the total is unchanged at 106, and NO ROW OUTSIDE
     * MODULE `lookaround` MOVES. The `(?(` conditional-group row is still
     * `unbuilt`: nothing about a lookbehind unlocks assertion-conditions
     * either. Module `lookaround` now reads `built` on all six of its rows,
     * which is what makes the engine-capability check's `built_wired` meet its
     * `wired` above.
     *
     * [M6.6.2] WAVE F: 58 + 42 -> 70 + 42, and the total MOVES this time —
     * 106 -> 118 — because the twelve `(*` alpha spellings are twelve NEW
     * ROWS rather than a status change on existing ones. They are BORN
     * `built`, which design §8.3 also committed to in advance and which is
     * derived rather than declared: each row's own `syntax` really does
     * produce at the `(*` doorway. ZERO rows move `built -> unbuilt`, `na`
     * does not move, and NO ROW OUTSIDE MODULE `lookaround` MOVES — the `(?(`
     * conditional-group row is `unbuilt` for the third wave running, and an
     * alpha SPELLING of an assertion unlocks assertion-conditions no more
     * than the `(?` spelling did.
     *
     * [DD-14] WAVE B+C: 118 = 70 + 42 + 6 -> 118 = 94 + 18 + 6. TWENTY-FOUR
     * ROWS FLIP `unbuilt -> built` and NO ROW IS ADDED OR REMOVED, which is a
     * shape this column has not seen before: every previous wave either added
     * rows born `built` (wave F's twelve alpha spellings) or flipped a handful
     * (wave D's three lookbehinds). Here the whole `(?` half of module
     * `recursion` gains a producer at once, because D65 derives `built` from
     * the PORT's answer and this wave wires all three ports together.
     *
     * AT WAVE B+C THE TWO ROWS THAT DID NOT FLIP WERE THE ASSERTION. `\g<1>`
     * and `\g'1'` stayed `unbuilt` — design §8.1 required it until wave D,
     * since flipping them while the emitter could not compile the spelling
     * would have shipped a compliance index that lies — and they stayed
     * `unbuilt` with NO CODE AT ALL: their rows carried `NO_PORT`, so ext.c's
     * ENABLED-BUT-UNBUILT epilogue answered for them and D65's "gate open,
     * port missing" signal was exactly what the classifier read.
     *
     * [DD-14] WAVE D: 118 = 94 + 18 + 6 -> 118 = 96 + 16 + 6. THE SAME TWO
     * ROWS FLIP `unbuilt -> built`, and NO ROW IS ADDED OR REMOVED. Both
     * rows' `aport` now points at `pcrec_brport_g`
     * (`src/parse/mod_backrefs.c`, gained the `<`/`'` arms), and it has no
     * tail left to decline for either — the same "no code at all" shape that
     * kept them `unbuilt` now flips them the other way with no code at all
     * either, since D65 is derived from the port's live answer rather than
     * declared. A decline branch inside `pcrec_brport_g` would have been
     * unreachable code satisfying nothing, and the brief that asked for one
     * is corrected at `src/parse/mod_recursion.c`'s closing note.
     *
     * NO ROW OUTSIDE MODULE `recursion` MOVES. `(?(DEFINE)` is `conditionals`'
     * and stays `unbuilt` for the fourth wave running: D71 item 4 gives it to
     * this module as a tailed row, and that is wave F's. */
    /* [DD-14] WAVE F: 118 = 96 + 16 + 6 -> 127 = 105 + 16 + 6. All nine new
     * rows are `built` ON THE DAY THEY LAND and derived rather than declared
     * — D65 drives each row's own `syntax` through the doorway, which elects
     * the PRIMARY row and really does produce. That is the honest reading and
     * the reason this wave could not have shipped a lying column: a spelling
     * whose primary did not compile would read `unbuilt` here. */
    /* 127 = 105 + 16 + 6 -> 128 = 106 + 16 + 6: the DEFINE row, built on
     * the day it lands like every other row whose port really produces. */
    else if (checked != 128 || built != 106 || unbuilt != 16 || na != 6)
        bad("built-status POPULATION MOVED: %d rows = %d built + %d unbuilt + "
            "%d n/a, expected 128 = 106 + 16 + 6. Zero defects does NOT imply "
            "nothing changed — a construct that silently stopped being built "
            "moves `built` down and `unbuilt` up with the sum unchanged, and "
            "the generated compliance index renders this column. If the move "
            "is deliberate, update these numbers in the same commit",
            checked, built, unbuilt, na);
    else if (defects == 0) {
        char label[192];
        snprintf(label, sizeof label,
                 "built-status: %d rows classified with 0 defects (%d "
                 "built, %d unbuilt, %d n/a — RS_BASE/RS_REJECTED), exact, "
                 "enabled set restored exactly", checked, built, unbuilt, na);
        ok(label);
    }
}

/* ---- [M6.6.2 wave F / D71 item 3] THE FAMILY LAYER, AND ITS TRIPWIRE ------
 *
 * `family` groups rows for the INDEX (`--list-families`, and the generated
 * construct index in docs/pcre2_compliance.md). A family's members are the
 * rows sharing a KEY, where a row's key is its `family` if set and its own
 * `syntax` otherwise. The index prints ONE line per family with `built` ANDed
 * over the members, so anything the members disagree about is a fact the
 * index has to pick a winner for — and picking one silently is exactly the
 * shape D71 item 3 was written against.
 *
 * SO THE MEMBERS MUST AGREE, AND DISAGREEMENT MUST FAIL LOUDLY. Four
 * assertions, each with a failure mode that has a name:
 *
 *   (1) a `family` that names NO ROW's syntax and no OTHER family member is a
 *       DANGLING REFERENCE. src/parse/mod_lookaround.c's `la_kind` resolves
 *       exactly this reference to reach the primary's three `u.look` flags,
 *       so a dangle is not a documentation defect: it is an alias with no
 *       construct, which reaches `BAD_ROW` at a doorway.
 *   (2) members that disagree on `module`, `engines` or `status` make the
 *       index's one line a lie whichever member it reads. `--list-families`
 *       reads the FIRST member and says so; this is what makes that safe.
 *   (3) a family of ONE that is not its own key — an alias pointing at a
 *       primary that does not exist as a row — is (1) said a second way, and
 *       is checked separately because the message a maintainer needs differs.
 *   (4) a CHAIN: a row whose `family` names a row that ITSELF has a `family`.
 *       `la_kind` resolves ONE level by design (its own comment says so), so
 *       a chain silently resolves to nothing. It is refused here rather than
 *       being made to work, because the index has no way to print a nested
 *       family and nobody has asked for one.
 *
 * THE `built` DISAGREEMENT IS NOT A FAILURE, and this is the one place the
 * check deliberately does NOT demand agreement: D71 item 3's rule is that a
 * family reads `built` only if EVERY member does, which is a statement about
 * how to COMBINE members that differ, not a prohibition on differing. What is
 * asserted instead is that the combination is what the dump prints — the
 * SABOTAGE SHAPE this check has (a member flipped `unbuilt` while its family
 * still reads `built`) is caught by that, and by nothing else in the tree. */
static const char *fam_key(const RegRow *r)
{
    return r->family ? r->family : r->syntax;
}

static void check_families(void)
{
    int families = 0, multi = 0, members_in_multi = 0, bads = 0;

    for (int k = 0; k < RK_COUNT; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry((RegKind)k, &n);
        if (!rows) continue;
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            const char *key = fam_key(r);
            if (!key) continue;

            /* (4) a chain: this row's family names a row that has one. */
            if (r->family) {
                for (int k2 = 0; k2 < RK_COUNT; k2++) {
                    size_t n2;
                    const RegRow *r2 = pcrec_registry((RegKind)k2, &n2);
                    if (!r2) continue;
                    for (size_t j = 0; j < n2; j++)
                        if (r2[j].syntax && strcmp(r2[j].syntax, r->family) == 0
                            && r2[j].family) {
                            bad("family: '%s' names '%s', which is ITSELF an "
                                "alias (family '%s'). Families are one level "
                                "deep -- mod_lookaround.c's la_kind resolves "
                                "exactly one -- so a chain resolves to nothing",
                                r->syntax, r->family, r2[j].family);
                            bads++;
                        }
                }
            }

            /* Emit once per family, at its first member in walk order. */
            bool first = true;
            for (int k2 = 0; k2 <= k && first; k2++) {
                size_t n2;
                const RegRow *r2 = pcrec_registry((RegKind)k2, &n2);
                if (!r2) continue;
                size_t lim = (k2 == k) ? i : n2;
                for (size_t j = 0; j < lim; j++) {
                    const char *k3 = fam_key(&r2[j]);
                    if (k3 && strcmp(k3, key) == 0) { first = false; break; }
                }
            }
            if (!first) continue;
            families++;

            int nmem = 0, nself = 0, nbuilt = 0, nna = 0;
            const RegRow *head = NULL;
            for (int k2 = 0; k2 < RK_COUNT; k2++) {
                size_t n2;
                const RegRow *r2 = pcrec_registry((RegKind)k2, &n2);
                if (!r2) continue;
                for (size_t j = 0; j < n2; j++) {
                    const char *k3 = fam_key(&r2[j]);
                    if (!k3 || strcmp(k3, key) != 0) continue;
                    if (!head) head = &r2[j];
                    nmem++;
                    if (r2[j].syntax && strcmp(r2[j].syntax, key) == 0) nself++;
                    PcrecBuiltStatus bs = pcrec_construct_built_status(&r2[j]);
                    if (bs == PCREC_BUILT_YES) nbuilt++;
                    else if (bs == PCREC_BUILT_NA) nna++;

                    /* (2) the members must agree on everything the index's
                     * single line states. */
                    if (nmem > 1) {
                        if ((head->module == NULL) != (r2[j].module == NULL) ||
                            (head->module && strcmp(head->module, r2[j].module) != 0))
                            { bad("family '%s': member '%s' is module '%s' but "
                                  "member '%s' is module '%s' -- the index prints "
                                  "ONE module for the family", key, head->syntax,
                                  head->module ? head->module : "(none)",
                                  r2[j].syntax,
                                  r2[j].module ? r2[j].module : "(none)"); bads++; }
                        if (head->engines != r2[j].engines)
                            { bad("family '%s': members '%s' and '%s' carry "
                                  "different `engines` masks (0x%x vs 0x%x) -- the "
                                  "index prints ONE", key, head->syntax,
                                  r2[j].syntax, head->engines, r2[j].engines);
                              bads++; }
                        if (head->status != r2[j].status)
                            { bad("family '%s': members '%s' and '%s' carry "
                                  "different RegStatus -- the index prints ONE",
                                  key, head->syntax, r2[j].syntax); bads++; }
                    }
                }
            }

            if (nmem > 1) { multi++; members_in_multi += nmem; }

            /* (1)/(3) the key must be SOME member's own syntax. A family of
             * one whose key is its own syntax is every ordinary row and is
             * fine; a key naming nothing is a dangling alias. */
            if (nself == 0) {
                bad("family '%s': no row's own `syntax` IS the key, so the "
                    "alias(es) pointing at it name a construct that does not "
                    "exist. mod_lookaround.c's la_kind resolves this exact "
                    "reference and would answer BAD_ROW at a doorway",
                    key);
                bads++;
            } else if (nself > 1) {
                bad("family '%s': %d rows claim that syntax -- the key must "
                    "name at most one canonical member", key, nself);
                bads++;
            }

            /* THE `built` COMBINATION, asserted against the DUMP rather than
             * recomputed here: this is the sabotage shape (a member flipped
             * `unbuilt` while the family line still reads `built`), and a
             * check that only recomputed the AND from the same members would
             * agree with a broken dump in unison -- this project's signature
             * check-design failure. `--list-families`' own output is read in
             * tests/registry/run_registry_tests.sh, which is a different
             * source from this loop. What is asserted HERE is only the fact
             * the rule needs to be well-defined: `built` is derivable for
             * every member of a multi-member family. */
            if (nmem > 1 && nna != 0 && nna != nmem) {
                bad("family '%s': %d of %d members have no `built` answer at "
                    "all (RS_BASE/RS_REJECTED) while the rest do -- the AND "
                    "rule has nothing to say about such a family",
                    key, nna, nmem);
                bads++;
            }
            (void)nbuilt;
        }
    }

    /* EXACT, this file's convention. 106 families over 118 rows: the twelve
     * `(*` alpha spellings collapse into their six primaries' families, so
     * SIX families have three members each and every other row is a family of
     * one. A deliberate move edits these numbers in the same change. */
    /* 106/6/18 -> 89/12/50 at [DD-14] WAVE F, and the FAMILY count going
     * DOWN while the ROW count goes UP is the whole point of the layer:
     * module `recursion`'s 26 rows were 26 one-member families and its 35
     * rows are now NINE index lines. Six new multi-member families —
     * `(?1)` (11), `(a)(?-1)` (11), `\g<1>` (3), `\g'1'` (3), `(?0)` (2),
     * `(?+1)(a)` (2) — which is 32 members joining the alpha spellings' 18. */
    /* 89 -> 90: the DEFINE row is a family of one (D71 item 4's "ONE row"). */
    if (families != 90 || multi != 12 || members_in_multi != 50)
        bad("family POPULATION MOVED: %d families, %d with more than one "
            "member, %d members in those -- expected 90 / 12 / 50. The index "
            "layer's grouping changed; if deliberately, update these numbers "
            "in the same commit", families, multi, members_in_multi);
    else if (bads == 0) {
        char label[224];
        snprintf(label, sizeof label,
                 "families: %d families over the table, %d of them multi-member "
                 "(%d members), every key naming exactly one canonical row, "
                 "every family agreeing on module/engines/status, no chains",
                 families, multi, members_in_multi);
        ok(label);
    }
}

/* ---- [M6.6.2 wave F] RF_INDEX: A ROW THAT DESCRIBES BUT NEVER FIRES -------
 *
 * The flag's whole contract is that `pcrec_registry_arbitrate` never returns
 * such a row. That is ONE line in registry.c, and one line is exactly what
 * gets deleted by a refactor that "tidies" an early `continue`, so it is
 * asserted here against the ENGINE'S OWN dispatch rather than by re-reading
 * the flag: every (kind, sel) an index row could plausibly be elected for is
 * arbitrated, and the answer must never be the index row.
 *
 * THE FAILING DIRECTION IS THE ONE THAT MATTERS AND IT IS SPECIFIC. An
 * RF_INDEX row carries REG_SEL_ANY, and `pcrec_registry_arbitrate`'s
 * REG_SEL_ANY arm assigns the kind's catch-all UNCONDITIONALLY, last one
 * wins. So without the skip the LAST alpha row would become the `(*`
 * doorway's catch-all and every verb in the tree would answer
 * "requires module 'lookaround'". The sweep below is what sees that. */
static void check_index_rows(void)
{
    int nindex = 0, bads = 0;

    for (int k = 0; k < RK_COUNT; k++) {
        size_t n;
        const RegRow *rows = pcrec_registry((RegKind)k, &n);
        if (!rows) continue;
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            if (!(r->flags & RF_INDEX)) continue;
            nindex++;

            /* Shape: an index row is a SPELLING of something, and it is found
             * by NAME. Both fields are what make it usable at all. */
            if (!r->family) {
                bad("index row '%s': RF_INDEX with no `family` -- an index row "
                    "exists to be a member of one, and with no family it is a "
                    "row nothing can ever reach", r->syntax);
                bads++;
            }
            /* [DD-14 wave F] `tail` IS THE NAME ON A VERB INDEX ROW AND
             * ONLY THERE, and the split is the one D71 item 3 draws between
             * the two reasons a row can be index-only.
             *
             * The twelve `(*` alpha spellings have NO byte-keyed dispatch
             * identity to keep: their doorway decides by NAME, so `tail`
             * carries that name and mod_verbs.c's
             * `pcrec_registry_verb_name_row` really does resolve it back to
             * the row. Requiring both halves is what makes those rows
             * reachable at all.
             *
             * Module `recursion`'s nine index rows are the OTHER shape. Their
             * spellings DO have a byte-keyed identity — `(?10)` is elected by
             * the `1` bucket and `\g<0>` by `\g` — and it belongs to the
             * PRIMARY row, which is exactly why these rows must not dispatch
             * and exactly why R6 stands for them. There is no name to
             * resolve; the row's identity is its `syntax` and its membership
             * is its `family`. Demanding a verb name here would have forced
             * nine fabricated names into the verb tables, which is a second
             * home for a fact (D24) and would have made
             * `pcrec_registry_verb_name_row` answer for constructs that are
             * not verbs.
             *
             * WHAT IS ASSERTED FOR BOTH, and it is the flag's whole contract:
             * a `family` (above) and NON-ELECTION (the sweep below). */
            if (r->kind == RK_VERB) {
                if (!r->tail || !*r->tail) {
                    bad("index row '%s': RK_VERB with RF_INDEX and no `tail` -- "
                        "the tail is the NAME mod_verbs.c's "
                        "pcrec_registry_verb_name_row matches, so without it "
                        "the doorway can never resolve to this row", r->syntax);
                    bads++;
                }
                if (r->tail &&
                    pcrec_registry_verb_name_row(r->tail, strlen(r->tail)) != r) {
                    bad("index row '%s': its own name '%s' resolves to a "
                        "DIFFERENT row (or none) -- two rows share a name, or "
                        "the lookup and the table disagree",
                        r->syntax, r->tail ? r->tail : "");
                    bads++;
                }
            } else if (r->sel == REG_SEL_ANY) {
                /* The failing direction for a BYTE-KEYED index row: it must
                 * record the byte its spelling really enters at, or the row
                 * is a claim about a doorway nobody can find. REG_SEL_ANY is
                 * the verb shape and means "no byte selects me", which for a
                 * `(?` or `\` spelling is false. */
                bad("index row '%s': REG_SEL_ANY on a %s index row -- a "
                    "byte-keyed spelling must record the selector its own "
                    "doorway dispatches on (its primary's), so the row says "
                    "where it enters even though it is never elected there",
                    r->syntax, kind_name(r->kind));
                bads++;
            }
        }
    }

    /* THE DISPATCH SWEEP, over every kind and every selector byte plus
     * REG_SEL_ANY, with and without text: no arbitration may ever elect an
     * index row. `pcrec_registry_arbitrate` is the ENGINE, called here
     * exactly as the doorways call it. */
    int probes = 0;
    for (int k = 0; k < RK_COUNT; k++) {
        for (int sel = -1; sel < 256; sel++) {
            static const char *texts[] = { NULL, "", "pla", "pla:a)",
                                           "positive_lookahead:a)", "ACCEPT)" };
            for (size_t t = 0; t < sizeof texts / sizeof texts[0]; t++) {
                const char *at = texts[t];
                size_t avail = at ? strlen(at) : 0;
                const RegRow *e = pcrec_registry_arbitrate((RegKind)k, sel, at,
                                                           avail, NULL);
                probes++;
                if (e && (e->flags & RF_INDEX)) {
                    bad("dispatch elected an INDEX row: kind %s sel %d text "
                        "'%s' -> '%s'. RF_INDEX rows must never be elected; "
                        "the skip in pcrec_registry_arbitrate is gone or was "
                        "moved AFTER the REG_SEL_ANY arm",
                        kind_name((RegKind)k), sel, at ? at : "(null)",
                        e->syntax);
                    bads++;
                    goto swept;   /* one report is enough; 257*6 would flood */
                }
            }
        }
    }
swept:
    /* AND THE POSITIVE CONTROL, because a sweep that elected nothing at all
     * would pass the loop above while proving nothing: the `(*` doorway's own
     * catch-all must STILL be reachable, and it must be the verbs row. That is
     * the exact thing a missing skip breaks. */
    {
        const RegRow *v = pcrec_registry_find(RK_VERB, REG_SEL_ANY, NULL, 0);
        if (!v || !v->module || strcmp(v->module, "verbs") != 0) {
            bad("the (* doorway's catch-all is '%s' (module '%s'), not the "
                "verbs row -- an index row has stolen it, which is what the "
                "arbitration skip exists to prevent",
                v ? v->syntax : "(none)",
                v && v->module ? v->module : "(none)");
            bads++;
        }
    }

    /* 12 -> 21 at [DD-14] WAVE F: module `recursion`'s NINE missing
     * spellings (design §8.1's four families — the multi-digit absolute and
     * relative calls, the eight `(?+N)` siblings, `\g<0>`/`\g'0'`, and the
     * leading-zero absolutes). They are the FIRST byte-keyed index rows and
     * the reason the verb-name assertions above are now RK_VERB's alone. */
    if (nindex != 21)
        bad("INDEX-ROW POPULATION MOVED: %d rows carry RF_INDEX, expected 21 "
            "(the twelve (* alpha lookaround spellings and module "
            "`recursion`'s nine missing spellings). If deliberate, update "
            "this number in the same commit", nindex);
    else if (bads == 0) {
        char label[288];
        snprintf(label, sizeof label,
                 "index rows: %d RF_INDEX rows, each with a family, a name and "
                 "a name that resolves back to it; %d arbitrations over every "
                 "kind x selector x 6 texts elected none of them, and the (* "
                 "doorway's catch-all is still module `verbs`", nindex, probes);
        ok(label);
    }
}

int main(void)
{
    printf("== registry well-formedness ==\n");
    check_wellformed();
    check_feature_module_bijection();
    check_class_ports();

    printf("\n== [M6.6.2 wave F / D71.3] the INDEX layer: families and RF_INDEX ==\n");
    check_families();
    check_index_rows();

    printf("\n== [M6.4.2/D67] SR-8 is BUILT: engine-capability refusal, per row ==\n");
    check_engine_capability();
    check_index_shape_witnesses();
    check_free_discharge();

    printf("\n== MOD-0.2 arbitration (recogniser + rank) ==\n");
    check_row_ranks();
    check_arbitration_liveness();

    printf("\n== [M6.4.2] R3: every RegKind reaches the dump ==\n");
    check_kind_coverage();

    printf("\n== table -> parser (every row's own syntax) ==\n");
    check_table_to_parser();

    printf("\n== rows that must exist (hand-written manifest) ==\n");
    check_required_rows();

    /* ALL FOUR doorways, not two. The first version of this file swept only the
     * escape and group doorways while its own documentation claimed the sweep
     * caught "a construct added to parse.c with no row" — true for half the
     * doorways it was written to describe. A critic pass found it. */
    printf("\n== parser -> table (255-byte sweep of ALL FOUR doorways) ==\n");
    sweep(RK_ESC,          "\\%c",      1, "after a backslash", 0, false, false);
    /* Two reasons a row is deliberately not a "requires module" answer in
     * the class position, both excused here and asserted POSITIVELY in
     * check_table_to_parser: a BASE class port (the byte is base syntax
     * there — [\b] is backspace; the port replaced RF_CLASS_BASE at
     * MOD-0.3d, hence excuse_base_cport) and RF_CLASS_INVALID (PCRE2
     * forbids the construct there permanently and a module must not be
     * promised, R9/SPEC-classes-F1 — the flag STAYS: D33 §3's NULL-port
     * retirement precondition is measurably false while the lexical rows
     * and unicode-props' rows carry honest NULLs that are NOT permanently
     * invalid; recorded in the 2026-08-12 journal). */
    sweep(RK_ESC,          "[\\%c]",    2, "after a backslash inside a class",
          RF_CLASS_INVALID, false, true);
    check_class_syntax_reach();
    sweep(RK_GROUP,        "(?%c",      2, "after (?", 0, false, false);
    /* LIMITATION, STATED BECAUSE IT IS EASY TO MISREAD AS COVERAGE: this
     * doorway is decided by a NAME and a byte sweep varies one byte. It proves
     * the doorway is reached and that PCRE2's two name tables are selected by
     * CASE; it says nothing about which name means what. Since Q1 the doorway
     * really does branch on the whole name, and the per-name coverage lives in
     * pcre2_check.c (PC-3) against libpcre2 — not here, and not in a byte
     * sweep, which could never have supplied it. */
    sweep_verb();
    /* The body is `alpha`, not `a`, and that is load-bearing since FIX-2: the
     * `:` row now checks the NAME between its delimiters, so `[[:a:]]` is
     * "unknown POSIX class name" and would make this sweep assert the wrong
     * string. `alpha` is a real POSIX class name and an ordinary run of letters
     * to the two collating rows, so one body serves all three. */
    sweep(RK_CLASSBRACKET, "[[%calpha%c]]", 2, "after [ inside a class (4b)", 0, false, false);
    /* DOORWAY 4a, which had NO sweep at all until FIX-2. The template above is
     * `[[%ca%c]]` — an inner bracket — so it only ever tested 4b, and the
     * CLASS'S OWN bracket went unswept even though it is a different code path
     * with (since K3) a different message. R6 spotted the gap and could not add
     * it: `[%ca%c]` would have FAILED until K3 was fixed, which is exactly why
     * it is landing in the same change as the fix. */
    sweep(RK_CLASSBRACKET, "[%calpha%c]", 1, "at a class's own bracket (4a)", 0, true, false);

    printf("\n== D65: built-status derivation (every row's own syntax classifies) ==\n");
    check_built_status_defects();

    printf("\n== Summary ==\n");
    printf("checks passed: %d\n", pass);
    printf("checks failed: %d\n", fail);
    return fail == 0 ? 0 : 1;
}
