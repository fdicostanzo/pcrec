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

/* Offset within `syntax` at which the selector byte must appear: "\\d" -> 1,
 * "(?=..." -> 2, "[[:alpha:]]" -> 2. Tying the probe to the selector is what
 * stops a row's example from drifting away from the byte it describes. */
static int sel_offset(RegKind k)
{
    return k == RK_ESC ? 1 : 2;
}

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

            if (r->sel == REG_SEL_ANY) {
                nany++;
                if (i != n - 1)
                    bad("%s row %zu (%s): the catch-all row must be LAST, or it shadows rows after it",
                        kn, i, r->syntax);
            } else {
                /* the selector byte must actually appear in the example */
                int off = sel_offset((RegKind)k);
                if ((int)strlen(r->syntax) <= off || (unsigned char)r->syntax[off] != (unsigned char)r->sel)
                    bad("%s row %zu (%s): syntax[%d] is not the selector '%c'",
                        kn, i, r->syntax, off, r->sel);
                for (size_t j = 0; j < i; j++)
                    if (rows[j].sel == r->sel)
                        bad("%s: duplicate selector '%c' in rows %zu and %zu — two rows claim one byte",
                            kn, r->sel, j, i);
            }

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
        }

        if (nany > 1) bad("%s: %d catch-all rows; at most one can ever be reached", kind_name((RegKind)k), nany);
        snprintf(label, sizeof label, "well-formed: %s rows (%zu)", kind_name((RegKind)k), n);
        ok(label);
    }

    /* Coverage floor, the same guard tests/reject/ carries: deleting rows must
     * not silently shrink what is described. */
    if (total < 60) {
        bad("registry TABLE SHRANK: %zu rows is below the floor of 60 — coverage was removed", total);
    } else {
        printf("PASS: registry describes %zu constructs (floor 60)\n", total);
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

/* ---- part 2: table -> parser ------------------------------------------- */

/* The exact diagnostic a row claims, at the atom (outside-a-class) site. */
static void esc_atom_msg(const RegRow *r, char *buf, size_t sz)
{
    if (r->diag == RD_MODULE_OCTAL)
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
        if (r->flags & RF_CLASS_BASE) {
            /* \b is backspace inside a class — base syntax, so the doorway is
             * NOT taken. A row that claims this must be right about it. */
            snprintf(label, sizeof label, "esc %s: base syntax inside a class, as the row claims", r->syntax);
            expect_compiles(label, pat);
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
        {RK_GROUP, REG_SEL_ANY, RS_MODULE, "the (?...) inline-option catch-all"},
    };
    char label[192];

    for (size_t i = 0; i < sizeof required / sizeof required[0]; i++) {
        const RegRow *r = pcrec_registry_find(required[i].kind, required[i].sel);

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
static void sweep(RegKind k, const char *fmt, const char *what, unsigned skip_flag)
{
    char pat[16], got[256], label[192];
    int mismatches = 0, routed = 0;

    for (int c = 1; c < 256; c++) {
        const RegRow *r;
        int rejected;

        snprintf(pat, sizeof pat, fmt, c, c);
        rejected = try_compile(pat, got, sizeof got) != 0;
        r = pcrec_registry_find(k, c);

        /* A row whose whole diagnostic is fixed text carries no "requires
         * module" marker, so the generic branches below cannot see it. Check it
         * directly: this is what makes the collating rows visible to the sweep
         * rather than to their two hand-written probes alone. */
        if (r && r->sel == c && r->diag == RD_FIXED) {
            if (!rejected || strcmp(got, r->msg) != 0) {
                bad("%s: byte 0x%02x ('%c') — the row promises \"%s\", parser %s",
                    what, c, c >= 32 && c < 127 ? c : '?', r->msg,
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
        } else if (r && r->status == RS_MODULE && r->sel == c && !(r->flags & skip_flag)) {
            /* skip_flag excuses a row that is deliberately NOT a doorway here —
             * RF_CLASS_BASE marks `\b`, which is backspace inside a class. */
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

int main(void)
{
    printf("== registry well-formedness ==\n");
    check_wellformed();
    check_feature_module_bijection();

    printf("\n== table -> parser (every row's own syntax) ==\n");
    check_table_to_parser();

    printf("\n== rows that must exist (hand-written manifest) ==\n");
    check_required_rows();

    /* ALL FOUR doorways, not two. The first version of this file swept only the
     * escape and group doorways while its own documentation claimed the sweep
     * caught "a construct added to parse.c with no row" — true for half the
     * doorways it was written to describe. A critic pass found it. */
    printf("\n== parser -> table (255-byte sweep of ALL FOUR doorways) ==\n");
    sweep(RK_ESC,          "\\%c",      "after a backslash", 0);
    sweep(RK_ESC,          "[\\%c]",    "after a backslash inside a class", RF_CLASS_BASE);
    sweep(RK_GROUP,        "(?%c",      "after (?", 0);
    /* LIMITATION, STATED BECAUSE IT IS EASY TO MISREAD AS COVERAGE: this
     * doorway is decided by a NAME, and a byte sweep can only prove that every
     * single byte after `(*` reaches the catch-all row. A name-conditional
     * branch added to parse.c — `(*script_run:` routed somewhere new, say —
     * would NOT be caught here. A critic demonstrated exactly that. Closing it
     * needs per-verb rows, which arrive with module 'verbs' (SR-6); until then
     * this sweep is weaker than its three neighbours and should be described
     * that way. */
    sweep(RK_VERB,         "(*%c)",     "after (* [single byte only — see note]", 0);
    sweep(RK_CLASSBRACKET, "[[%ca%c]]", "after [ inside a class", 0);

    printf("\n== Summary ==\n");
    printf("checks passed: %d\n", pass);
    printf("checks failed: %d\n", fail);
    return fail == 0 ? 0 : 1;
}
