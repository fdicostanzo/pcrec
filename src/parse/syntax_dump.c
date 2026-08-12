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
    /* "class-base" retired at MOD-0.3d with its flag — base class
     * semantics are the row's port now, not a flag the dump can show */
    {RF_CLASS_DELIM, "class-delim"},
    {RF_LEXICAL, "lexical"},
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
    /* K14: a ROADMAP_NEVER row must not promise its module. The substring is
     * the template-free core both doorway templates share. */
    else if (r->status == RS_MODULE && r->roadmap == ROADMAP_NEVER)
        sb_puts(sb, "is outside pcrec's scope and no module will implement it");
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
                 "\tstatus\tdiag\tflags\texpect\tnote\troadmap\tquantifiable"
                 "\tclass_expect\n");

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
            put_str(&sb, r->note);                      sb_putc(&sb, '\t');
            /* 13th column, appended 2026-08-11 (MOD-0.1/K14) so existing
             * field indices survive: the ROADMAP disposition (design
             * Â§17.2). `-` = the question does not arise (base rows). */
            sb_puts(&sb, r->roadmap == ROADMAP_NEVER   ? "never"
                       : r->roadmap == ROADMAP_PLANNED ? "planned" : "-");
            sb_putc(&sb, '\t');
            /* 14th column (MOD-0.1 slice 2, design Â§18.3): the quantifiability
             * fact, populated from libpcre2's own `a<syntax>*` verdicts and
             * re-verified against them by tests/spec_mod0/check10. */
            sb_puts(&sb, r->quant == QF_YES     ? "yes"
                       : r->quant == QF_NO      ? "no"
                       : r->quant == QF_FORM    ? "form"
                       : r->quant == QF_LEXICAL ? "lexical" : "-");
            sb_putc(&sb, '\t');
            /* 15th column (MOD-0.1 slice 3): the class-position expectation,
             * measured from libpcre2 and re-verified against a live oracle by
             * tests/spec_mod0/check04. EMPTY — not "-" — on the 56 group/verb
             * rows: the construct cannot reach a class position, so there is
             * no fact to print (the header's "Empty field = none" rule). */
            put_str(&sb, r->class_expect);
            sb_putc(&sb, '\n');
        }
    }
    return sb_take(&sb);
}

/* `--list-verbs`. Q1 added fifty verb NAMES that no dump could show: they are
 * not RegRows, so `--list-syntax` cannot carry them and its format is frozen
 * (SR-4 generates a section of docs/pcre2_compliance.md from it, and the
 * compliance index would churn). A separate dump keeps that format byte-stable
 * and still gives the names an external view — which matters because a
 * stranger reading `--list-syntax` would otherwise see one `(*ACCEPT)` row and
 * conclude the doorway knows one thing.
 *
 * The `forms` column is the whole point and is worth reading carefully: it is
 * what libpcre2 ACCEPTS, measured, not what pcrec implements. pcrec implements
 * none of these — every row here still ends a compile. */
char *pcrec_syntax_verbs(void)
{
    StrBuf sb = {0};

    sb_puts(&sb, "# pcrec verb-name tables for the `(*` doorway (Q1, D25).\n"
                 "# PCRE2 keeps TWO tables and selects by the CASE of the first\n"
                 "# name byte; `table` is which, and `unknown` is what pcrec says\n"
                 "# for a name that table does not have.\n"
                 "# `forms` is what libpcre2 ACCEPTS, measured, not what pcrec\n"
                 "# implements — pcrec implements none of these yet.\n"
                 "#table\tname\tforms\tunknown\troadmap\tquantifiable\n");

    for (int w = 0; w < 2; w++) {
        const VerbTable *t = pcrec_registry_verb_tables(w);
        for (size_t i = 0; i < t->n; i++) {
            const VerbName *v = &t->rows[i];
            unsigned f = v->forms;
            sb_puts(&sb, w == 0 ? "upper" : "lower"); sb_putc(&sb, '\t');
            sb_puts(&sb, v->name);                    sb_putc(&sb, '\t');
            if (f & VF_BARE)     sb_puts(&sb, "(*N)");
            if (f & VF_ARG)      sb_puts(&sb, (f & VF_BARE) ? "|(*N:a)" : "(*N:a)");
            if (f & VF_EMPTYARG) sb_puts(&sb, "|(*N:)");
            if (f & VF_EQNUM)    sb_puts(&sb, (f & (VF_BARE|VF_ARG|VF_EMPTYARG))
                                              ? "|(*N=d)" : "(*N=d)");
            if (f & VF_GROUPARG) sb_puts(&sb, "|arg-is-subpattern");
            if (f & VF_ATSTART)  sb_puts(&sb, "|start-of-pattern-only");
            sb_putc(&sb, '\t');
            sb_puts(&sb, t->unknown_msg);
            sb_putc(&sb, '\t');
            /* 5th column (MOD-0.1/K14): the per-name ROADMAP disposition,
             * RESOLVED (a name without its own value inherits the RK_VERB
             * row's, which is PLANNED — module 'verbs'). */
            sb_puts(&sb, v->roadmap == ROADMAP_NEVER ? "never" : "planned");
            sb_putc(&sb, '\t');
            /* 6th column (MOD-0.1 slice 2): the verb row's QF_FORM resolved
             * per name. `not-askable` = the unquantified form does not
             * compile (start-only options away from position 0), a third
             * outcome that must not be folded into "no". */
            sb_puts(&sb, v->quant == QV_YES ? "yes"
                       : v->quant == QV_NO  ? "no" : "not-askable");
            sb_putc(&sb, '\n');
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

/* ---- THE ROUTER: text -> ONE doorway call (MOD-0.1 slice 8; extracted at
 *      MOD-0.7 slice 1) --------------------------------------------------
 *
 * Locate the construct: the FIRST byte that opens a doorway, found by a
 * bytewise scan, never a parse. Ten registry rows carry a plain-group prefix
 * in their syntax (`(a)(?-1)` — the probe must COMPILE in PCRE2, and a bare
 * `(?-1)` does not), and parse.c reaches their doorway with the cursor deep
 * in the pattern; the scan reproduces that placement and every reported
 * position is in the FULL text's coordinates, so `at`/tails line up exactly
 * as they would in a real parse. The scan does not decode escapes, so hand it
 * a construct (with at most a plain prefix), not an arbitrary pattern.
 *
 * ROUTING MIRRORS parse.c'S CALL CONVENTIONS and recognises nothing itself:
 * each branch places the cursor exactly where parse.c has it at that
 * doorway's call site (escape: `\` and selector consumed; group: AT the `?`;
 * verb: after `(`; class-bracket 4a/4b: after the class's `[`). It is a fifth
 * CALLER of the four doorways, not a fifth doorway.
 *
 * `(?:` is EXCLUDED exactly as parse.c excludes it: the base grammar answers
 * it before the doorway is consulted, so there is no doorway call to probe —
 * its row exists for the dump's completeness (SR-3), not because anything
 * looks it up.
 *
 * TWO CALLERS, ONE ROUTER (MOD-0.7 slice 1, design note §3.1).
 * `pcrec_probe_ask` and `pcrec_syntax_explain` both need "which doorway does
 * this text reach, with which arguments", and a second copy would be the D24
 * two-homes failure with a new coat: the two would drift, and the drift would
 * be invisible because each surface would be self-consistent with itself.
 * The extraction is behaviour-preserving by construction (the branches below
 * are the originals, unmoved) and the evidence is external: `--probe-ask`'s
 * ten TSV fields are read by check06 and pinned byte-exact by cli case10,
 * whose cursor sweep is floored at 198 probes.
 *
 * The router's FIDELITY — that an answer obtained through it is the answer
 * the compiler gives — is measured, not assumed: 99 of 99 routed registry-row
 * syntaxes and 11 of 11 hand-listed queries produce a (msg, at) pair
 * byte-identical to `pcrec -o - <text>`'s (design note §3.2). The boundary is
 * in the note: arbitrary query text has no compile to compare against. */
typedef struct {
    RegKind kind;
    int     sel;              /* the doorway's selector byte, or -1          */
    size_t  at;               /* the offset the doorway blames               */
    size_t  from;             /* class-bracket: just past the delimiter      */
    size_t  cursor;           /* where parse.c has cx->pos at this call site */
    bool    at_class_open;    /* class-bracket 4a                            */
    bool    at_content_start; /* class-bracket 4b                            */
} Doorway;

static bool doorway_route(const char *text, size_t n, Doorway *d)
{
    for (size_t i = 0; i < n; i++) {
        char c0 = text[i];
        int  c1 = i + 1 < n ? (unsigned char)text[i + 1] : -1;
        if (c0 == '\\' && c1 >= 0) {
            /* esc_atom's convention: `\` and the selector byte consumed */
            *d = (Doorway){ .kind = RK_ESC, .sel = c1, .at = i, .from = 0,
                            .cursor = i + 2, .at_class_open = false,
                            .at_content_start = false };
            return true;
        }
        if (c0 == '(' && c1 == '?' && !(i + 2 < n && text[i + 2] == ':')) {
            /* p_group_body's convention: cursor AT the '?' */
            *d = (Doorway){ .kind = RK_GROUP,
                            .sel = i + 2 < n ? (unsigned char)text[i + 2] : -1,
                            .at = i, .from = 0, .cursor = i + 1,
                            .at_class_open = false, .at_content_start = false };
            return true;
        }
        if (c0 == '(' && c1 == '*') {
            *d = (Doorway){ .kind = RK_VERB, .sel = -1, .at = i, .from = 0,
                            .cursor = i + 1, .at_class_open = false,
                            .at_content_start = false };
            return true;
        }
        if (c0 == '[' && c1 == '[') {
            /* doorway 4b: a bracket INSIDE the class — `[[:alpha:]]` */
            *d = (Doorway){ .kind = RK_CLASSBRACKET,
                            .sel = i + 2 < n ? (unsigned char)text[i + 2] : -1,
                            .at = i + 1, .from = i + 3, .cursor = i + 1,
                            .at_class_open = false, .at_content_start = true };
            return true;
        }
        if (c0 == '[') {
            /* doorway 4a: the class's OWN bracket as opener — `[:alpha:]` */
            *d = (Doorway){ .kind = RK_CLASSBRACKET, .sel = c1, .at = i,
                            .from = i + 2, .cursor = i + 1,
                            .at_class_open = true, .at_content_start = false };
            return true;
        }
    }
    return false;
}

/* Place the cursor and make the ONE call. The Ctx handed in is ZEROED by both
 * callers: no jmp target, no arena blocks. That is safe while every doorway
 * RETURNS its answer (none may ctx_fail or allocate — the D33 §5 contract),
 * and it is one of the things the first enabled, result-producing module port
 * must revisit here, with a probe that is false the day before (D33 §9.3): a
 * port that allocates needs this Ctx given a real arena before `result` asks
 * can be driven through it. */
static ExtResult doorway_call(Ctx *cx, const Doorway *d, ExtWant want)
{
    cx->pos = d->cursor;
    switch (d->kind) {
    case RK_ESC:   return pcrec_ext_escape(cx, want, d->sel, false, d->at);
    case RK_GROUP: return pcrec_ext_group(cx, want, d->sel, d->at);
    case RK_VERB:  return pcrec_ext_verb(cx, want, d->at);
    case RK_CLASSBRACKET:
        return pcrec_ext_class_bracket(cx, want, d->sel, d->at, d->from,
                                       d->at_class_open, d->at_content_start);
    default: break;
    }
    return (ExtResult){ .what = EXT_NOT_MINE, .at = 0, .msg = "",
                        .answered_at = WANT_CLAIM };
}

/* The TSV word for a doorway. Deliberately NOT `doorway_name`'s wording:
 * that one reads "after '(?'" for a human in `--explain`'s row blocks, this
 * one is a frozen column value in `--probe-ask`'s output (check06 parses it)
 * and in `--explain`'s route line. Two audiences, two spellings, one
 * mapping each. */
static const char *doorway_word(RegKind k)
{
    switch (k) {
    case RK_ESC:          return "escape";
    case RK_GROUP:        return "group";
    case RK_VERB:         return "verb";
    case RK_CLASSBRACKET: return "class-bracket";
    default:              return "?";
    }
}

/* ---- the --probe-ask channel (MOD-0.1, §18.2) ---------------------------
 *
 * ONE doorway call for a construct, at a caller-chosen ask level, with the
 * REAL cursor reported before and after. This is the surface the cursor rule
 * is measured over: check06 (tests/spec_mod0) drives every registry row's
 * syntax here twice — WANT_RESULT set and clear — and requires cx->pos
 * unchanged whenever RESULT was not asked. The positions printed are the Ctx
 * field the doorways actually use, read by this function before and after
 * the call; nothing here derives an "expected" position for the check to
 * echo, because a check fed from the implementation's own answer would be
 * the control-sharing-a-source failure this project keeps paying for.
 *
 * The routing moved to `doorway_route`/`doorway_call` above at MOD-0.7 slice
 * 1 — same branches, same order, now shared with `--explain`.
 *
 * TSV, one line, fields appended never reordered (the SR-4 rule):
 *   doorway  want  answered_at  pos_before  pos_after  outcome  at
 *   ep_set_certain  end  msg
 * `answered_at` is the post-gate level — `result` asks print `verdict`
 * until the first module is enabled, which makes the §5.4 demotion a
 * measured fact rather than a comment. */
char *pcrec_probe_ask(const char *want_name, const char *construct)
{
    static const char *const want_names[] = { "claim", "verdict", "result" };
    int w = -1;
    for (int i = 0; i < 3; i++)
        if (!strcmp(want_name, want_names[i])) w = i;
    if (w < 0) return NULL;
    ExtWant want = (ExtWant)w;

    Ctx cx;
    memset(&cx, 0, sizeof cx);
    cx.pat = construct;
    cx.patlen = strlen(construct);

    Doorway d;
    if (!doorway_route(construct, cx.patlen, &d))
        return NULL;    /* not doorway territory; the CLI says so and how */

    const char *doorway = doorway_word(d.kind);
    size_t before = d.cursor;
    ExtResult r = doorway_call(&cx, &d, want);

    /* The outcome word covers the FULL ExtWhat vocabulary (MOD-0.3c: the
     * producing values are constructable now, and a probe channel that
     * reported them as "refusal" would be the dump lying about the one
     * thing it exists to show). check06 never consults this field; it is
     * the human's and the future checks' window. */
    const char *outcome =
        r.what == EXT_NOT_MINE ? "not-mine" :
        r.what == EXT_REFUSAL  ? "refusal"  :
        r.what == EXT_SCALAR   ? "scalar"   :
        r.what == EXT_MEMBERS  ? "members"  :
        r.what == EXT_NODE     ? "node"     : "unknown";
    StrBuf sb = {0};
    sb_printf(&sb, "%s\t%s\t%s\t%zu\t%zu\t%s\t%zu\t%d\t%zu\t",
              doorway, want_names[w], want_names[r.answered_at],
              before, cx.pos, outcome,
              r.at, r.ep_set_certain ? 1 : 0, r.end);
    if (r.what == EXT_REFUSAL) sb_puts(&sb, r.msg);
    sb_putc(&sb, '\n');
    return sb_take(&sb);
}
