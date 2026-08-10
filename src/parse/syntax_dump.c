/* Rendering the syntax construct registry as text (D24, step SR-3).
 *
 * WHY THIS IS NOT A CONVENIENCE. `pcrec --list-syntax` exists so SR-4 can make
 * the table LOAD-BEARING: tests/reject/ iterates this dump instead of 93
 * hand-written entries, and docs/pcre2_compliance.md is rendered from it. A
 * construct then covers itself in both, the moment its row is added — which is
 * the only arrangement under which "one declarative home" survives a second
 * contributor. `--explain` reads the same rows through the same helpers, so it
 * cannot disagree with the dump it sits beside.
 *
 * TSV, one row per construct, `#` comment lines for consumers to skip, an empty
 * field for a NULL. Tabs and newlines inside a field would corrupt the format
 * silently, so tests/registry/ asserts that no field contains either: the dump
 * FORBIDS them rather than escaping them, because an escaping scheme is a thing
 * SR-4's readers would each have to implement identically.
 *
 * THREE NAME TABLES LIVE HERE, and one deliberately does not. `flavours`,
 * `engines` and `flags` are masks whose bits have no string anywhere else, so
 * rendering them needs names and this is their one home. `feature` is NOT given
 * one: registry.c's M_<module> macros already pair each feature bit with its
 * module name, and a second bit->name table here would be exactly the duplicate
 * home this design exists to prevent. So `feature` renders as a hex mask and
 * the human-readable answer is the `module` column beside it — which
 * tests/registry/ separately proves is a bijection with the mask. */

#include <stdlib.h>
#include <string.h>

#include "core/internal.h"

typedef struct { unsigned bit; const char *name; } MaskName;

static const MaskName flavour_names[] = {
    {FLAV_PCRE2, "pcre2"},
};
static const MaskName engine_names[] = {
    {ENGM_DFA, "dfa"}, {ENGM_VM, "vm"},
};
static const MaskName flag_names[] = {
    {RF_CLASS_BASE, "class-base"}, {RF_CLASS_DELIM, "class-delim"},
};

#define NELEMS(a) (sizeof (a) / sizeof (a)[0])

/* Look a flavour up by name. Returns 0 for an unknown name, which the CLI turns
 * into an error rather than a silent "no filter" — exactly one flavour exists
 * (D18's earn-its-axis rule applied to the front end), and a typo must not
 * quietly dump the whole table as though it had been honoured. */
unsigned pcrec_flavour_by_name(const char *name)
{
    for (size_t i = 0; i < NELEMS(flavour_names); i++)
        if (!strcmp(flavour_names[i].name, name)) return flavour_names[i].bit;
    return 0;
}

static void put_mask(StrBuf *sb, unsigned mask, const MaskName *t, size_t n)
{
    bool first = true;
    for (size_t i = 0; i < n; i++) {
        if (!(mask & t[i].bit)) continue;
        if (!first) sb_putc(sb, '|');
        sb_puts(sb, t[i].name);
        first = false;
    }
}

static const char *kind_name(RegKind k)
{
    switch (k) {
    case RK_ESC:          return "esc";
    case RK_GROUP:        return "group";
    case RK_VERB:         return "verb";
    case RK_CLASSBRACKET: return "class-bracket";
    default:              return "?";
    }
}

/* Where the construct is decided, in the words the registry's own header uses.
 * SR-4's reject-test iteration needs this to know how to PROBE a row. */
static const char *doorway_name(RegKind k)
{
    switch (k) {
    case RK_ESC:          return "after '\\'";
    case RK_GROUP:        return "after '(?'";
    case RK_VERB:         return "after '(*'";
    case RK_CLASSBRACKET: return "after '[' inside a class";
    default:              return "?";
    }
}

static const char *status_name(RegStatus s)
{
    switch (s) {
    case RS_BASE:     return "base";
    case RS_MODULE:   return "module";
    case RS_REJECTED: return "rejected";
    default:          return "?";
    }
}

static const char *diag_name(RegDiag d)
{
    switch (d) {
    case RD_NONE:         return "none";
    case RD_MODULE:       return "module";
    case RD_MODULE_OCTAL: return "module-octal";
    case RD_FIXED:        return "fixed";
    default:              return "?";
    }
}

static void put_selector(StrBuf *sb, int sel)
{
    if (sel == REG_SEL_ANY)             sb_puts(sb, "*");
    else if (sel >= 0x20 && sel < 0x7f) sb_putc(sb, (char)sel);
    else                                sb_printf(sb, "\\x%02x", sel & 0xff);
}

static void put_str(StrBuf *sb, const char *s) { if (s) sb_puts(sb, s); }

/* The expected diagnostic TEXT for a row, or nothing when the construct
 * compiles. This is the column SR-4 needs and the reason the dump is worth
 * having: tests/reject/ can assert against it without a human retyping it.
 *
 * It is a SUBSTRING of what the parser prints, not the whole line — the
 * doorway supplies the surrounding template ("\%c requires module '%s'"), and
 * reproducing those templates here would be a second home for them. What is
 * asserted is what a caller actually needs to be told: which module, or the
 * fixed text verbatim. */
static void put_expect(StrBuf *sb, const RegRow *r)
{
    if (r->diag == RD_FIXED)      put_str(sb, r->msg);
    else if (r->status == RS_MODULE) sb_printf(sb, "requires module '%s'", r->module);
}

static const RegKind all_kinds[] = { RK_ESC, RK_GROUP, RK_VERB, RK_CLASSBRACKET };

char *pcrec_syntax_tsv(unsigned flavours)
{
    StrBuf sb = {0};

    sb_puts(&sb, "# pcrec syntax construct registry (D24). Empty field = none.\n"
                 "# `syntax` is a valid probe pattern for the construct.\n"
                 "# `expect` is the text the diagnostic must contain, for the "
                 "rows that reject.\n"
                 "#kind\tselector\tsyntax\tmodule\tfeature\tflavours\tengines"
                 "\tstatus\tdiag\tflags\texpect\tnote\n");

    for (size_t k = 0; k < NELEMS(all_kinds); k++) {
        size_t n;
        const RegRow *rows = pcrec_registry(all_kinds[k], &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            if (flavours && !(r->flavours & flavours)) continue;

            sb_puts(&sb, kind_name(r->kind));           sb_putc(&sb, '\t');
            put_selector(&sb, r->sel);                  sb_putc(&sb, '\t');
            put_str(&sb, r->syntax);                    sb_putc(&sb, '\t');
            put_str(&sb, r->module);                    sb_putc(&sb, '\t');
            sb_printf(&sb, "0x%04x", r->feature);       sb_putc(&sb, '\t');
            put_mask(&sb, r->flavours, flavour_names, NELEMS(flavour_names));
            sb_putc(&sb, '\t');
            put_mask(&sb, r->engines, engine_names, NELEMS(engine_names));
            sb_putc(&sb, '\t');
            sb_puts(&sb, status_name(r->status));       sb_putc(&sb, '\t');
            sb_puts(&sb, diag_name(r->diag));           sb_putc(&sb, '\t');
            put_mask(&sb, r->flags, flag_names, NELEMS(flag_names));
            sb_putc(&sb, '\t');
            put_expect(&sb, r);                         sb_putc(&sb, '\t');
            put_str(&sb, r->note);                      sb_putc(&sb, '\n');
        }
    }
    return sb_take(&sb);
}

/* `--explain '\v'`. A row matches when the query and the row's `syntax` are a
 * prefix of one another, so `\k` finds `\k<name>` and `(?=...)` finds `(?=`.
 * Every match is printed: `(?<` is genuinely two constructs, and answering with
 * only the first would be the kind of half-truth this file exists to end. */
char *pcrec_syntax_explain(const char *query, unsigned flavours)
{
    StrBuf sb = {0};
    size_t qlen = strlen(query);
    int found = 0;

    for (size_t k = 0; k < NELEMS(all_kinds); k++) {
        size_t n;
        const RegRow *rows = pcrec_registry(all_kinds[k], &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            if (flavours && !(r->flavours & flavours)) continue;
            if (!r->syntax) continue;

            size_t slen = strlen(r->syntax);
            size_t cmp = qlen < slen ? qlen : slen;
            if (cmp == 0 || strncmp(query, r->syntax, cmp) != 0) continue;

            if (found++) sb_putc(&sb, '\n');
            sb_printf(&sb, "%s\n", r->syntax);
            sb_printf(&sb, "  doorway   %s\n", doorway_name(r->kind));
            switch (r->status) {
            case RS_BASE:
                sb_puts(&sb, "  status    implemented by the base grammar\n");
                break;
            case RS_MODULE:
                sb_printf(&sb, "  status    known, unimplemented — requires "
                               "module '%s'\n", r->module);
                break;
            case RS_REJECTED:
                sb_puts(&sb, "  status    rejected, as PCRE2 rejects it too\n");
                break;
            }
            if (r->diag == RD_FIXED && r->msg)
                sb_printf(&sb, "  error     %s\n", r->msg);
            sb_puts(&sb, "  flavours  ");
            put_mask(&sb, r->flavours, flavour_names, NELEMS(flavour_names));
            sb_puts(&sb, "\n  engines   ");
            if (r->engines)
                put_mask(&sb, r->engines, engine_names, NELEMS(engine_names));
            else
                sb_puts(&sb, "none");
            sb_puts(&sb, "  (design intent, unconsumed until SR-8)\n");
            if (r->note) sb_printf(&sb, "  note      %s\n", r->note);
        }
    }

    if (!found) { sb_free(&sb); return NULL; }
    return sb_take(&sb);
}
