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
            if (r->quant == QF_FORM &&
                !(r->flags & RF_OPTION_RUN) && r->kind != RK_VERB)
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

            if (r->sel == REG_SEL_ANY) {
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
                const char *pfx = k == RK_ESC ? "\\" : k == RK_GROUP ? "(?" : "[";
                snprintf(needle, sizeof needle, "%s%c%s", pfx, r->sel, r->tail ? r->tail : "");
                if (!strstr(r->syntax, needle))
                    bad("%s row %zu (%s): the example does not contain its own doorway text \"%s\"",
                        kn, i, r->syntax, needle);
                /* Uniqueness is over the (sel, tail) PAIR since SR-9. Two rows
                 * MAY share a byte — that is the whole point of the tail — but
                 * two rows with the same byte AND the same tail are
                 * indistinguishable, and find() would silently answer whichever
                 * the scan reached first. The design doc calls this "stronger
                 * than today" and it is: the old check could not have caught two
                 * identical `(?P<` rows, because neither existed to collide. */
                for (size_t j = 0; j < i; j++) {
                    if (rows[j].sel != r->sel) continue;
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
            case RK_VERB:
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
            if (!wants_any && nany != 0)
                bad("%s: %d catch-all rows, needs 0 — this doorway must be able "
                    "to DECLINE, or every unmatched byte becomes a construct",
                    kind_name((RegKind)k), nany);
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
    if (total != 100) {
        bad("registry ROW COUNT CHANGED: %zu rows, expected 100. If you added or "
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
    const RegRow *all[4];
    size_t counts[4], nkinds = 0, total = 0;
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
    if (tailed != 18)
        bad("row ranks: %d tailed rows, 18 expected — the tailed population "
            "moved; re-derive it from the table (do NOT just edit this number)",
        tailed);
    else if (badrows == 0)
        ok("row ranks: all 18 tailed rows sit above the fallback tier");
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
        { RK_ESC,   'N', 10 },
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

    /* escapes: both sites — outside a class and inside one */
    rows = pcrec_registry(RK_ESC, &n);
    for (size_t i = 0; i < n; i++) {
        const RegRow *r = &rows[i];

        esc_atom_msg(r, want, sizeof want);
        snprintf(label, sizeof label, "esc %s: atom diagnostic matches the row", r->syntax);
        expect_msg(label, r->syntax, want);

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
        } else {
            snprintf(want, sizeof want, "\\%c in a class requires module '%s'", r->sel, r->module);
            snprintf(label, sizeof label, "esc %s: in-class diagnostic matches the row", r->syntax);
            expect_msg(label, pat, want);
        }
    }

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
            /* K14: a NEVER row must not promise its module (the callouts row
             * is the only one today; this branch is derived, so a second one
             * is covered the day it exists). The independent pin of WHICH
             * rows are NEVER is hand-written in tests/reject/. */
            snprintf(want, sizeof want, "(?%c...) is outside pcrec's scope and no module will implement it (see docs/pcre2_compliance.md)", byte);
        else
            snprintf(want, sizeof want, "(?%c...) requires module '%s'", byte, r->module);
        snprintf(label, sizeof label, "group %s: diagnostic matches the row", r->syntax);
        expect_msg(label, r->syntax, want);
    }

    /* verbs and class brackets: fixed messages, used verbatim */
    for (int k = RK_VERB; k <= RK_CLASSBRACKET; k++) {
        rows = pcrec_registry((RegKind)k, &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            snprintf(label, sizeof label, "%s %s: diagnostic matches the row",
                     kind_name((RegKind)k), r->syntax);
            expect_msg(label, r->syntax, r->msg);
        }
    }

    /* The collating rows have a SECOND call site: the class-opening bracket
     * itself ("[.a.]", no inner '['). One row, two paths into it — which is
     * the whole point of having one row. Hand-written because the doorway
     * model does not describe this entry, so nothing derives it. */
    expect_msg("classbracket [.a.]: opening bracket reaches the same row",
               "[.a.]", "POSIX collating elements are not supported");
    expect_msg("classbracket [=a=]: opening bracket reaches the same row",
               "[=a=]", "POSIX collating elements are not supported");
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

    if (scalar != 5 || set != 10 || fn != 9 || aports != 11)
        bad("class ports: populations moved — %d scalar (5: b g k 8 9), "
            "%d SET class ports (10: the char-types, slice 2), %d FN class "
            "ports (9: posix + the eight octal digits, slice 3), %d atom "
            "ports (11: the char-types + \\N). A deliberate move edits this "
            "check IN THE SAME CHANGE; a silent one is the defect",
            scalar, set, fn, aports);
    else if (bads == 0)
        ok("class ports: 5 scalar + 10 SET + 9 FN class ports, 11 atom "
           "ports; scalar and SET values oracle-tied (class_expect column / "
           "fallback law / census popcounts), as predicted for slice 3");
}

int main(void)
{
    printf("== registry well-formedness ==\n");
    check_wellformed();
    check_feature_module_bijection();
    check_class_ports();


    printf("\n== MOD-0.2 arbitration (recogniser + rank) ==\n");
    check_row_ranks();
    check_arbitration_liveness();

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

    printf("\n== Summary ==\n");
    printf("checks passed: %d\n", pass);
    printf("checks failed: %d\n", fail);
    return fail == 0 ? 0 : 1;
}
