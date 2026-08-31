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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/internal.h"
#include "parse/parse_mods.h"

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
    /* [M6.4.2] the fifth kind, and the one that is NOT a doorway. This name is
     * a frozen column value in `--list-syntax`'s TSV: consumers key on it. */
    case RK_QUANTSUFFIX:  return "quant-suffix";
    /* [DD-11.1] the sixth kind, ALSO not a doorway — RK_QUANTSUFFIX's own
     * precedent, a second time (internal.h's comment on RK_BARE has the
     * full ruling). Frozen column value, same as above. */
    case RK_BARE:         return "bare";
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
    /* [M6.4.2] There is no doorway. The possessive suffix is recognised inside
     * `p_rep` (src/parse/parse.c), after `try_quant` has already accepted the
     * quantifier — registry.c's header records why giving it one would cost
     * the base tier a lookup on every quantifier. The word says so rather than
     * naming a place that does not exist. */
    case RK_QUANTSUFFIX:  return "a quantifier suffix (no doorway)";
    /* [DD-11.1] `^`/`$`/plain `(` are parsed directly in `p_atom`/
     * `p_group_body` (parse.c) — base grammar, no doorway, same shape as
     * the possessive suffix above. */
    case RK_BARE:         return "base grammar (no doorway)";
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

/* [M6.4.2] THE ARRAY A FIFTH KIND IS INVISIBLE TO. Every `RegKind` switch in
 * the tree carries a `default:` — measured, 28 files offered / 28 clean / 0
 * `-Wswitch` diagnostics for a new enumerator
 * (atomic_groups_measurements/probes/probe_rk_alarm.sh) — so the compiler
 * cannot see an omission from THIS list, and neither could any check before
 * [M6.4.2]. `tests/registry/registry_check.c`'s `check_kind_coverage` now
 * parses THIS DUMP'S OUTPUT and asserts every `RegKind` name appears in it,
 * which is the only formulation that can see an omission here at all: a check
 * that iterated `RK_COUNT` over registry.c would share a source with the thing
 * it checks, which is this project's signature check-design failure. */
static const RegKind all_kinds[] = { RK_ESC, RK_GROUP, RK_VERB, RK_CLASSBRACKET,
                                     RK_QUANTSUFFIX, RK_BARE };

char *pcrec_syntax_tsv(unsigned flavours)
{
    StrBuf sb = {0};

    sb_puts(&sb, "# pcrec syntax construct registry (D24). Empty field = none.\n"
                 "# `syntax` is a valid probe pattern for the construct.\n"
                 "# `expect` is the text the diagnostic must contain, for the "
                 "rows that reject.\n"
                 "# `built` (D65): has the owning module's producer landed for "
                 "THIS construct, derived live by driving `syntax` through a "
                 "gate-forced-open doorway call — 'built'/'unbuilt' for "
                 "RS_MODULE rows, '-' where the question does not arise "
                 "(RS_BASE/RS_REJECTED). Orthogonal to `status`/`roadmap`, "
                 "which stay PCRE2/base-grammar facts.\n"
                 "# `family` (D71 item 3): the CANONICAL SYNTAX of the family "
                 "this row is a spelling of, empty when the row is its own "
                 "family. Members of a family are the rows sharing a key, "
                 "where a row's key is its `family` if it has one and its own "
                 "`syntax` otherwise; `--list-families` prints one line per "
                 "family with `built` ANDed across the members. Grouping is "
                 "an INDEX-layer fact and never dispatch: a row's dispatch "
                 "identity is unchanged (R6).\n"
                 "#kind\tselector\tsyntax\tmodule\tfeature\tflavours\tengines"
                 "\tstatus\tdiag\tflags\texpect\tnote\troadmap\tquantifiable"
                 "\tclass_expect\tbuilt\tfamily\n");

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
            sb_putc(&sb, '\t');
            /* 16th column (D65, 2026-08-21): the built-status derivation —
             * see pcrec_construct_built_status's own comment. PCREC_BUILT_
             * DEFECT renders visibly rather than being coerced into "unbuilt"
             * (a worse lie): tests/registry/registry_check.c's defect
             * assertion is what turns it into a hard `make test` failure
             * before this ever reaches a committed doc. */
            {
                PcrecBuiltStatus bs = pcrec_construct_built_status(r);
                sb_puts(&sb, bs == PCREC_BUILT_YES    ? "built"
                           : bs == PCREC_BUILT_NO     ? "unbuilt"
                           : bs == PCREC_BUILT_DEFECT ? "defect" : "-");
            }
            sb_putc(&sb, '\t');
            /* 17th column ([M6.6.2] wave F, D71 item 3): the family's
             * canonical syntax, EMPTY — not "-" — for a row that is its own
             * family, per this dump's own "Empty field = none" rule. APPENDED
             * for the reason the 13th, 15th and 16th columns were: consumers
             * key on field index, and [SR-11]'s table contract resolves by
             * NAME precisely so an appended column costs them nothing. */
            put_str(&sb, r->family);
            sb_putc(&sb, '\n');
        }
    }
    return sb_take(&sb);
}

/* `--list-definitions` — [DD-11.2], the FIFTH registry surface (D85,
 * docs/design/definitions_table.md §5). Walks the SAME `RegRow`s
 * `pcrec_syntax_tsv` above prints, through the SAME `kind_name`/
 * `put_selector`/`put_str` helpers, so `kind`/`selector`/`syntax` are
 * guaranteed to join the two dumps rather than merely happening to agree —
 * "the same three columns... so a reader can join the two dumps" is the
 * note's own requirement, discharged by construction rather than by two
 * independent renderings that could drift.
 *
 * A row with `definitions == NULL` contributes NOTHING — this dump is
 * per-DEFINITION, not per-row, the same way `pcrec_axes_tsv` is per-
 * CANDIDATE rather than per-axis. `order` is 1-based and DENSE per row (an
 * N-entry array prints 1..N), read directly off the array position rather
 * than carried as a second field on `RegDef` — one more instance of "one
 * derivation" (the array's own order IS the fact).
 *
 * `predicate` is the tag's OWN NAME (`pcrec_def_tag_name`, definitions.c) —
 * never hand-authored prose, per the r43 ruling folded into the design note:
 * the predicate column and a stored callable were two derivations of one
 * fact, and the tag name is the one that survives.
 *
 * `definition` is the DEFK_STR/DEFK_TEXTFN/DEFK_BUILDER text verbatim (a
 * core-syntax splice for the first, a human-readable TEMPLATE for the other
 * two — never a live evaluation, the same "proves what the compiler
 * THINKS" boundary `--list-axes`'s own header states, axes_dump.c), the
 * row's OWN `syntax` for a DEF_IDENTITY entry, or `= <target syntax>` for a
 * DEFK_ROW entry — a REFERENCE, never the target's own resolved text (D24's
 * one-fact-one-row argument applied to this table: `$`'s non-multiline
 * entry prints `= \Z`, not `(?=\n?\z)`, which is `\Z`'s OWN row's line to
 * print). `DEFK_END` never reaches this loop (it terminates the walk, same
 * convention `pcrec_def_resolve` uses in definitions.c).
 *
 * An entry carrying `operand` (r43-third-round follow-up, team-lead ruling
 * 2026-08-29 — today's only user is the 14-name POSIX class family) prints
 * `[[:<operand>:]] ≡ <definition text>` instead of the row's fixed `syntax`
 * example: the row's own `syntax` field is a single FIXED example
 * ("[[:alpha:]]") that does not vary per entry, so printing it 14 times
 * over would repeat the same construct while the `definition` column
 * changed underneath it — a misleading table, not a partial one. The
 * `[[:%s:]]` wrapper is this ONE row's own construct shape, hand-written
 * here rather than derived, on the same "no measured need to generalise a
 * one-user mechanism" reasoning definitions_oracle_gen.c's own comment
 * states for its twin.
 *
 * `applies` is `active` (a real substitution, including a DEFK_ROW chain —
 * chaining IS substituting, just by reference) or `identity` (DEF_IDENTITY:
 * the row restates its own primitive form, nothing to splice). */
char *pcrec_definitions_tsv(unsigned flavours)
{
    StrBuf sb = {0};

    sb_puts(&sb, "# pcrec definitions table (D85, docs/design/definitions_table.md). "
                 "Empty field = none.\n"
                 "# `kind`/`selector`/`syntax` are the SAME three columns "
                 "--list-syntax prints for the owning row, so the two dumps "
                 "join on them.\n"
                 "# `order` is 1-based, dense per row (this row's Nth "
                 "definitions-array entry).\n"
                 "# `predicate` is the option-scope tag's OWN NAME (a closed, "
                 "stable vocabulary a consumer may switch on), never "
                 "hand-authored prose.\n"
                 "# `definition` is the core-syntax TEXT for a string-kind "
                 "entry, or the literal `<builder>` for an operand-taking "
                 "one — never a live evaluation.\n"
                 "# `applies` is `active` (this entry substitutes a "
                 "different construct) or `identity` (restates the row's "
                 "own primitive form).\n"
                 "#kind\tselector\tsyntax\torder\tpredicate\tdefinition\tapplies\n");

    for (size_t k = 0; k < NELEMS(all_kinds); k++) {
        size_t n;
        const RegRow *rows = pcrec_registry(all_kinds[k], &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            if (!r->definitions) continue;
            if (flavours && !(r->flavours & flavours)) continue;

            int order = 0;
            for (const RegDef *d = r->definitions; d->kind != DEFK_END; d++) {
                order++;
                sb_puts(&sb, kind_name(r->kind));      sb_putc(&sb, '\t');
                put_selector(&sb, r->sel);              sb_putc(&sb, '\t');
                put_str(&sb, r->syntax);                sb_putc(&sb, '\t');
                sb_printf(&sb, "%d", order);            sb_putc(&sb, '\t');
                sb_puts(&sb, pcrec_def_tag_name(d->tag)); sb_putc(&sb, '\t');
                /* [DD-11.1]/[DD-11.4b]/[r43-second-round] five DefKinds
                 * reach this dump now: DEFK_STR (the definition itself),
                 * DEFK_TEXTFN and DEFK_BUILDER (`str` is a human-readable
                 * TEMPLATE for both, never a splice-ready string —
                 * definitions.c's/internal.h's own header on those blocks),
                 * DEF_IDENTITY (the row's OWN `syntax` restated — there is
                 * no substitution text because there is no substitution),
                 * and DEFK_ROW (`= ` plus the TARGET row's `syntax` — a
                 * reference the reader follows to that row's own line,
                 * never the target's resolved text printed here a second
                 * time). */
                if (d->kind == DEF_IDENTITY)
                    put_str(&sb, r->syntax);
                else if (d->kind == DEFK_ROW) {
                    sb_puts(&sb, "= ");
                    put_str(&sb, d->str);
                } else if (d->operand) {
                    sb_printf(&sb, "[[:%s:]] \xe2\x89\xa1 %s",
                              d->operand, d->str);
                } else
                    put_str(&sb, d->str);
                sb_putc(&sb, '\t');
                /* `applies` comes FROM THE KIND, never inferred (the
                 * manager's identity ruling) — DEF_IDENTITY is the only
                 * kind that restates the row's own primitive form; a
                 * DEFK_ROW chain is still `active` (it substitutes, just by
                 * reference rather than by inline text). */
                sb_puts(&sb, d->kind == DEF_IDENTITY ? "identity" : "active");
                sb_putc(&sb, '\n');
            }
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

/* ---- `--list-families`: THE INDEX LAYER (D71 item 3) ---------------------
 *
 * ONE LINE PER FAMILY, where a family is the set of rows sharing a KEY and a
 * row's key is its `family` when it has one and its own `syntax` otherwise.
 * So a row with no `family` and no aliases pointing at it is a family of one
 * and prints exactly what `--list-syntax` prints for it — which is every row
 * in the table but eighteen today.
 *
 * WHY THIS IS A SECOND DUMP RATHER THAN A CHANGE TO THE FIRST, and it is the
 * same reason `--list-verbs` is a second dump: `--list-syntax`'s format is
 * frozen and its consumers are per-ROW. `tests/reject/run_reject_tests.sh`
 * probes EVERY non-base row with its own `syntax`, and that is exactly what
 * must keep happening for the twelve alpha spellings — each one is a distinct
 * thing a caller can write, and a collapsed dump would silently drop twelve
 * probes. So the row dump stays per-row (with `family` as its 17th column,
 * the fact) and the INDEX view is here (the grouping, derived).
 *
 * `built` IS ANDed ACROSS THE MEMBERS, which is D71 item 3's rule stated
 * exactly: a family reads `built` only if EVERY member does. The direction
 * matters — a family whose canonical spelling compiles while one of its
 * aliases does not is NOT a built family, and saying otherwise is the precise
 * lie D65's column exists to prevent, one layer up. A family with no member
 * the question arises for reads `-`.
 *
 * WHAT IT DOES NOT DO: derive the canonical syntax from anything. The key IS
 * the canonical syntax (internal.h's `family` comment on why the grouping key
 * and the printed spelling are one string), so there is nothing to elect and
 * no second home for it. `module`/`engines`/`status` are taken from the
 * family's FIRST member in table order; `tests/registry/registry_check.c`
 * asserts the members agree on all three, so which one is read cannot matter
 * — and if that assertion ever fails, it fails there, loudly, rather than
 * being papered over by a rule here about who wins. */
char *pcrec_syntax_families(void)
{
    StrBuf sb = {0};

    sb_puts(&sb, "# pcrec syntax FAMILIES (D71 item 3): one line per family,\n"
                 "# where a family is the rows sharing a key and a row's key is\n"
                 "# its `family` column if set and its own `syntax` otherwise.\n"
                 "# `built` is ANDed over the members: a family reads built only\n"
                 "# if EVERY member does. `members` lists every spelling, the\n"
                 "# canonical one first when it is itself a row.\n"
                 "# Grouping is an INDEX fact; every row keeps its own dispatch\n"
                 "# identity and its own line in --list-syntax (R6).\n"
                 "#syntax\tmodule\tengines\tstatus\tbuilt\tnmembers\tmembers\n");

    for (size_t k = 0; k < NELEMS(all_kinds); k++) {
        size_t n;
        const RegRow *rows = pcrec_registry(all_kinds[k], &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            const char *key = r->family ? r->family : r->syntax;
            if (!key) continue;

            /* EMIT ONCE PER FAMILY, at its first member in walk order —
             * decided by looking BACKWARD over the same walk rather than by
             * carrying a seen-set, because the walk is the only order this
             * dump has and a set would need its own ordering rule. */
            bool first = true;
            for (size_t k2 = 0; k2 <= k && first; k2++) {
                size_t n2;
                const RegRow *r2 = pcrec_registry(all_kinds[k2], &n2);
                size_t lim = (k2 == k) ? i : n2;
                for (size_t j = 0; j < lim; j++) {
                    const char *k3 = r2[j].family ? r2[j].family : r2[j].syntax;
                    if (k3 && strcmp(k3, key) == 0) { first = false; break; }
                }
            }
            if (!first) continue;

            /* THE MEMBERS, in table order, canonical first when it is a row:
             * a row whose own `syntax` IS the key sorts ahead of the aliases
             * by construction, because an alias's `family` names it and the
             * registry declares the primary before them. */
            int nmem = 0, nbuilt = 0, nna = 0;
            StrBuf mem = {0};
            for (size_t k2 = 0; k2 < NELEMS(all_kinds); k2++) {
                size_t n2;
                const RegRow *r2 = pcrec_registry(all_kinds[k2], &n2);
                for (size_t j = 0; j < n2; j++) {
                    const char *k3 = r2[j].family ? r2[j].family : r2[j].syntax;
                    if (!k3 || strcmp(k3, key) != 0) continue;
                    if (nmem) sb_putc(&mem, ' ');
                    put_str(&mem, r2[j].syntax);
                    nmem++;
                    PcrecBuiltStatus bs = pcrec_construct_built_status(&r2[j]);
                    if (bs == PCREC_BUILT_YES) nbuilt++;
                    else if (bs == PCREC_BUILT_NA) nna++;
                }
            }

            put_str(&sb, key);                          sb_putc(&sb, '\t');
            put_str(&sb, r->module);                    sb_putc(&sb, '\t');
            put_mask(&sb, r->engines, engine_names, NELEMS(engine_names));
            sb_putc(&sb, '\t');
            sb_puts(&sb, status_name(r->status));       sb_putc(&sb, '\t');
            sb_puts(&sb, nna == nmem      ? "-"
                       : nbuilt == nmem   ? "built" : "unbuilt");
            sb_putc(&sb, '\t');
            sb_printf(&sb, "%d", nmem);                 sb_putc(&sb, '\t');
            {
                char *m = sb_take(&mem);
                sb_puts(&sb, m);
                free(m);
            }
            sb_putc(&sb, '\n');
        }
    }
    return sb_take(&sb);
}

/* `--explain` lives at the END of this file since MOD-0.7: it is the shared
 * doorway router's second caller, so it must be defined below it. */

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

/* Place the cursor and make the ONE call.
 *
 * THE OBLIGATION THIS COMMENT USED TO DEFER IS DISCHARGED (R20/MOD07-1,
 * 2026-08-12). It said the zeroed Ctx was safe "while every doorway RETURNS
 * its answer (none may ctx_fail or allocate)" and named "the first enabled,
 * result-producing module port" as the event that must revisit it. That port
 * landed at MOD-0.3c/0.5c — two milestones before MOD-0.7 extracted this
 * function and carried the comment along unexamined — and the precondition
 * had been false ever since: a module port recurses into `pcrec_parse_body`,
 * whose `ctx_fail` longjmps, and both callers were handing over a `jmp_buf`
 * that had never been `setjmp`'d. `--features modifiers --explain '(?i:['`
 * SIGSEGVed (139), as did `--features all --probe-ask result -- '(?i:['`.
 *
 * SO BOTH CALLERS NOW GUARD THEIR OWN Ctx, and each renders a raise as its
 * surface's ordinary error (stderr + a nonzero exit, cli case12). This
 * function itself is unchanged and stays free of the guard on purpose: the
 * jmp target must be the frame that owns the buffers being abandoned, and
 * that frame is the caller's, not this one.
 *
 * BOTH CALLERS ALSO ARENA_FREE. A port that produces allocates from
 * `cx->arena`, and a port that raises allocates and then abandons — so the
 * arena is no longer the "no arena blocks" the old comment assumed either.
 *
 * The general lesson, recorded because R20 filed it as one of two: a
 * carried-forward comment is a carried-forward OBLIGATION. Moving code whose
 * comment names a future revisit is the moment to check whether the future
 * already happened. */
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
    /* [M6.4.2] Unreachable BY CONSTRUCTION rather than by omission:
     * `doorway_route` above recognises `\\`, `(?`, `(*` and `[` and can never
     * produce this kind, because there is no doorway to route to. Written out
     * so the switch stays exhaustive and so a future attempt to route here
     * says so at the compiler rather than falling into EXT_NOT_MINE. */
    case RK_QUANTSUFFIX: break;
    /* [DD-11.1] same unreachable-by-construction shape: `doorway_route`
     * recognises `\`, `(?`, `(*`, `[` and can never produce RK_BARE either
     * — there is no doorway for `^`/`$`/plain `(` any more than there is
     * for the possessive suffix. */
    case RK_BARE: break;
    default: break;
    }
    return (ExtResult){ .what = EXT_NOT_MINE, .at = 0, .msg = "",
                        .answered_at = WANT_CLAIM };
}

/* ---- D65: the BUILT-STATUS derivation ------------------------------------
 *
 * docs/design/registry_built_status_memo.md, ratified wholesale (D65,
 * 2026-08-21). Answers "has this construct's own producer actually
 * landed", per row, by driving the row's own `syntax` through the SAME
 * doorway machinery `--probe-ask`/`--explain` use above, at a gate FORCED
 * open (every module, not just the row's own — see
 * `pcrec_construct_built_status`'s own comment for the `(?m)` cross-module
 * dependency that forced the wider choice) — never a hand-declared column
 * (ext.c's UNBUILT macro comment already gives the reason: a second column
 * would have to be kept in sync with the ports by hand, the D24 two-homes
 * shape this whole registry exists to prevent). The isolated-`Ctx` shape
 * (memset, own `setjmp`, `pcrec_parse_mods_init`, `arena_free` on every
 * exit) is `pcrec_probe_ask`'s, ordered the same way for the same reason:
 * the guard is placed before any automatic object this function reads
 * AFTER a possible longjmp is live, so `-Wclobbered` stays silent.
 *
 * `probe` does the CLASSIFICATION at whatever gate the caller has already
 * installed; `pcrec_construct_built_status` (the exported entry, below) is
 * the one that FORCES the gate. Split so the gate-mutation is in exactly
 * one place. */
static PcrecBuiltStatus built_status_probe(const RegRow *r)
{
    Ctx cx;
    memset(&cx, 0, sizeof cx);
    cx.pat = r->syntax;
    cx.patlen = strlen(r->syntax);
    cx.arena.cx = &cx;
    if (setjmp(cx.jb)) {
        /* the row's own well-formed `syntax` (SR-1's own rule: every row's
         * `syntax` really reaches its doorway) RAISED instead of cleanly
         * producing or refusing — neither half of D65(3)'s vocabulary, so
         * this is a registry defect for tests/registry/registry_check.c to
         * fail on, never a status this dump may assert. */
        arena_free(&cx.arena);
        /* [M6.4.2] A NON-DOORWAY ROW RAISES INSTEAD OF RETURNING, and for it a
         * raise is the ORDINARY unbuilt answer rather than a defect: the
         * doorway arm below classifies on a RETURNED `ExtResult`, while the
         * quant-suffix arm runs a real parse whose refusal is a `ctx_fail`
         * that lands exactly here. See that arm for why a raise at a
         * forced-open gate can only be a missing producer, and where the
         * malformed-syntax half of the question is checked instead.
         *
         * [M4-QUOTING] `RF_LEXICAL` joins `RK_QUANTSUFFIX` here for the SAME
         * reason, not a new one: its own arm below runs an ordinary parse
         * too, and a raise there means the same thing — the construct's
         * producer (a lexer-mode transition, not a port) declined. See that
         * arm's own comment for why `PCREC_BUILT_DEFECT` (the "parsed but
         * stamped nothing" outcome `RK_QUANTSUFFIX` can reach) does not
         * apply to a lexical row at all. */
        return (r->kind == RK_QUANTSUFFIX || (r->flags & RF_LEXICAL))
               ? PCREC_BUILT_NO : PCREC_BUILT_DEFECT;
    }
    pcrec_parse_mods_init(&cx);

    /* [M6.4.2] THE NON-DOORWAY ARM, and R31 C1 is why it exists.
     *
     * The derivation above is `doorway_route` + `doorway_call`, and
     * `doorway_route` recognises exactly four prefixes — `\`, `(?`, `(*`, `[`.
     * A row whose `syntax` is `a*+` routes NOWHERE, so under the pre-[M6.4.2]
     * code every RK_QUANTSUFFIX row derived to `PCREC_BUILT_DEFECT`: not
     * "unbuilt", not "built", a registry defect. The first revision of the
     * atomic-groups design claimed the derivation for these rows "is simply a
     * compile of the syntax string"; measured on the shipped binary,
     * `--explain 'a*+'` answers "no construct matches". So the honest price of
     * giving the possessive suffixes rows is this arm.
     *
     * WHAT IT DOES: compiles the row's own `syntax` through an ORDINARY PARSE
     * in the same isolated, gate-forced-open `Ctx` the doorway arm uses, and
     * classifies on whether the ROW'S OWN PRODUCER STAMPED ANYTHING
     * (`Ast.reg`, SR-8/D67). Three values, all three reachable:
     *
     *   parsed, this row stamped a node  -> BUILT_YES
     *   parsed, this row stamped nothing -> BUILT_DEFECT: the row's `syntax`
     *                                      does not exercise its own construct
     *   the parse RAISED                 -> BUILT_NO
     *
     * WHY A RAISE IS `unbuilt` AND NOT `defect`, stated because it is the one
     * judgement here. With EVERY module forced open, the only thing that can
     * refuse a well-formed row `syntax` is the construct's own missing
     * producer. "Well-formed" is not assumed: `tests/reject/run_reject_tests.sh`
     * RUNS every non-base dump row's `syntax` at the CLOSED gate and requires a
     * clean exit-1 rejection containing the row's `expect` text — an
     * INDEPENDENT, hand-written second source for the same rows — so a row
     * whose syntax was malformed rather than merely unbuilt fails there, in a
     * check that does not share this one's source. The two halves are
     * deliberately not merged.
     *
     * MEASURED FALSIFIABLE, which is D33 §9.3's rule for a new outcome: with
     * `p_rep`'s desugaring reverted and everything else in place, all four rows
     * derive `unbuilt`; with it in place, all four derive `built`. The DEFECT
     * arm was demonstrated by pointing a row's `syntax` at `ab`. */
    if (r->kind == RK_QUANTSUFFIX) {
        Ast *root = pcrec_parse(&cx);
        PcrecBuiltStatus st = pcrec_ast_stamped_by(root, r) ? PCREC_BUILT_YES
                                                            : PCREC_BUILT_DEFECT;
        arena_free(&cx.arena);
        return st;
    }

    /* [M4-QUOTING] THE LEXICAL ARM, R31 C1's own reasoning applied to a
     * SECOND non-doorway population. `doorway_route` recognises `\`, `(?`,
     * `(*`, `[` and WOULD route an `RF_LEXICAL` row's `syntax` there
     * (`\Q` genuinely starts with `\`) — straight into `pcrec_ext_escape`/
     * `pcrec_ext_group`'s own port machinery, which an `RF_LEXICAL` row
     * deliberately has none of (the flag's own comment, internal.h: "the
     * construct is a TOKENIZER MODE, not an atom... its producer is the
     * mode transition itself"). That producer lives one layer below the
     * registry — in the LEXER (module `quoting`'s xskip/cls_skip/cat_ends
     * extensions and esc_atom's/p_class's own quote-mode dispatch,
     * src/parse/parse.c) — where the doorway arm below cannot see it at
     * all: calling it would read `\Q` back to its OLD unbuilt refusal
     * even once the module compiles the construct, because that refusal
     * is exactly what `pcrec_ext_escape` still answers on its own (the
     * lexer intercepts BEFORE the doorway is ever reached, not through it).
     *
     * So, like `RK_QUANTSUFFIX`, this needs an ORDINARY PARSE of the row's
     * own `syntax` — but the classification differs from that arm's: a
     * lexical construct never STAMPS a node (`Ast.reg`, SR-8/D67) — it
     * produces zero or more ORDINARY literal atoms, and stamping is a
     * PRODUCER's act, which a mode transition is not. `built` is simply
     * "the parse did not raise": the `setjmp` guard above already routes a
     * raise on an `RF_LEXICAL` row to `PCREC_BUILT_NO` (see its own
     * comment), so reaching this return means it did not, and there is no
     * `BUILT_DEFECT` outcome for this arm to reach — the module's own
     * `syntax` rows (`\Q`, `\E`) are SR-1's guarantee that every row's
     * `syntax` really reaches its own construct, same as every other row
     * this file classifies. MEASURED FALSIFIABLE the same way
     * `RK_QUANTSUFFIX`'s arm is: with the module disabled (the gate this
     * function forces open notwithstanding — see its own header, the gate
     * mutation is what makes that force meaningful) both rows derive
     * `unbuilt`; with esc_atom's/p_class's quote-mode dispatch removed and
     * everything else in place, both derive `unbuilt` again; with it in
     * place, both derive `built`. */
    if (r->flags & RF_LEXICAL) {
        Ast *root = pcrec_parse(&cx);
        (void)root;
        arena_free(&cx.arena);
        return PCREC_BUILT_YES;
    }

    Doorway d;
    if (!doorway_route(r->syntax, cx.patlen, &d)) {
        arena_free(&cx.arena);
        return PCREC_BUILT_DEFECT;
    }
    ExtResult res = doorway_call(&cx, &d, WANT_RESULT);

    /* THE CLASSIFICATION, and why it reads `answered_at` rather than the
     * refusal TEXT (a narrower first draft matched `PCREC_UNBUILT_MARKER`
     * here and MEASURED WRONG on three real rows — see the verification
     * notes in docs/design/registry_built_status_memo.md's implementation
     * record): `res.answered_at == WANT_RESULT` is exactly D33's own
     * "gate open, port missing" signal (ext.c's UNBUILT comment: "reaching
     * this point at WANT_RESULT means the gate was OPEN and the port block
     * declined"), and `--probe-ask` has reported it since MOD-0.1 slice 9 —
     * independent of WHAT the refusal says. Module `verbs` (a direct call,
     * not a port — mod_verbs.c) and module `unicode-props` (bypasses
     * `aport`/`cport` entirely, "no producer this phase" — mod_uprops.c)
     * both refuse with the CLOSED-gate wording ("requires module 'X'") even
     * with their gate forced open, because neither routes through ext.c's
     * shared UNBUILT epilogue at all; a marker-text match would have
     * wrongly scored both as registry defects. `answered_at` still reads
     * `result` for both (MEASURED: `--probe-ask result -- '(*ACCEPT)'` with
     * `--features verbs`, and the `\p{L}` analogue with `unicode-props`),
     * because the gate genuinely was open — it is the PORT that had nothing
     * to say, exactly the fact this column exists to report. Demoted
     * `answered_at` (< WANT_RESULT) cannot happen here since the gate below
     * forces EVERY module open, so a demotion would itself mean the
     * registry's own feature/module bijection is broken — a real defect. */
    PcrecBuiltStatus result;
    if (res.what == EXT_NODE || res.what == EXT_MEMBERS ||
        res.what == EXT_SCALAR)
        result = PCREC_BUILT_YES;
    else if (res.what == EXT_REFUSAL && res.answered_at == WANT_RESULT)
        result = PCREC_BUILT_NO;
    else
        result = PCREC_BUILT_DEFECT;
    arena_free(&cx.arena);
    return result;
}

PcrecBuiltStatus pcrec_construct_built_status(const RegRow *r)
{
    if (r->status != RS_MODULE || !r->module || !r->syntax) return PCREC_BUILT_NA;

    /* THE GATE MUTATION. `enabled.c`'s enabled set is process-global,
     * write-once-then-read-many by design (its own header comment) — the
     * SAME shape `tests/registry/pcre2_check.c`'s "gated pass" already uses
     * (install a focused set, run, restore, assert the restore — see
     * tests/registry/CLAUDE.md, "THE ENABLED SET IS FOCUSED"), and this is
     * `--list-syntax`'s one designed side effect on it: the printed table
     * returns the set to exactly what it found, so a caller running
     * `--features X --list-syntax` sees X's own gate-CLOSED diagnostics on
     * every OTHER row unaffected, in the same process.
     *
     * `pcrec_enabled_set_modules()` and `pcrec_enabled_set_spec()`'s
     * explicit-list form are exact inverses (the module column's own
     * comma-separated spelling), which is what lets this restore the
     * caller's set EXACTLY rather than merely to "none" — but that string
     * lives in the SAME static buffer `install()` overwrites, so it must be
     * copied out before this function's own `pcrec_enabled_set_spec` call
     * below overwrites it in place.
     *
     * FORCES "all" OPEN, not merely `r->module` — a first draft forced only
     * the row's own module and MEASURED WRONG on `(?m)`: the letter's own
     * semantic gate (mod_modifiers.c's case 'm') checks `FEAT_ASSERTIONS`,
     * not `FEAT_MODIFIERS`, even though the GROUP_OPT row it dispatches
     * through carries `FEAT_MODIFIERS` (the option-run family's shared
     * feature bit) — a real cross-module dependency this dump has no other
     * way to discover per row. Forcing every module open cannot turn an
     * unbuilt construct built (a row with no producer refuses no matter how
     * many OTHER modules are enabled, MEASURED for `verbs`/`unicode-props`
     * above), so the wider force costs nothing and fixes the one real gap
     * found while verifying this against the shipped compiler. */
    char saved[512];
    snprintf(saved, sizeof saved, "%s", pcrec_enabled_set_modules());

    char err[256];
    if (pcrec_enabled_set_spec("all", err, sizeof err) != 0)
        return PCREC_BUILT_DEFECT;   /* unreachable: "all" is always valid */

    PcrecBuiltStatus result = built_status_probe(r);

    pcrec_enabled_set_spec(saved[0] ? saved : "none", err, sizeof err);
    return result;
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
    /* [M6.4.2] `--probe-ask` and `--explain` route by SCANNING for a doorway
     * opener, so they never reach a quant-suffix row and never print this;
     * it exists so the mapping is total. */
    case RK_QUANTSUFFIX:  return "quant-suffix";
    /* [DD-11.1] same shape: --probe-ask/--explain never reach a RK_BARE
     * row either (no doorway to scan for), so the mapping is total for the
     * same reason. */
    case RK_BARE:         return "bare";
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
 * measured fact rather than a comment.
 *
 * TWO WAYS TO RETURN NULL, and `err` is what separates them (R20/MOD07-1):
 * `err->msg` empty means the CALLER asked a bad question (an unknown want
 * level, or text that reaches no doorway) — the misuse the CLI has always
 * answered with a usage sentence. `err->msg` non-empty means the doorway
 * RAISED: the construct reached an enabled port, the port ran a real parse,
 * and that parse failed. Telling an operator to fix their command line for
 * the second would be a lie, so the two exits print different things. */
char *pcrec_probe_ask(const char *want_name, const char *construct,
                      pcrec_error *err)
{
    static const char *const want_names[] = { "claim", "verdict", "result" };
    if (err) { err->msg[0] = '\0'; err->pos = 0; }

    /* THE GUARD (R20/MOD07-1), placed FIRST so that no automatic object in
     * this function is live across it. That is not style: `-Wclobbered`
     * flagged `w`, `doorway` and `before` when the guard sat lower, and each
     * warning was a real (if benign here) statement that a longjmp may
     * restore a stale register copy. The only object read after the branch is
     * `cx`, whose address escapes — the arrangement `src/core/compile.c` (the
     * tree's only other `setjmp`) uses for the same reason. Nothing between
     * here and `doorway_call` can raise, so guarding early costs nothing. */
    Ctx cx;
    memset(&cx, 0, sizeof cx);
    cx.err = err;
    cx.pat = construct;
    cx.patlen = strlen(construct);
    cx.arena.cx = &cx;   /* [M4.7b/K7] arena OOM -> this setjmp, not abort() */
    if (setjmp(cx.jb)) {
        arena_free(&cx.arena);      /* a raising port allocated, then left */
        return NULL;
    }
    /* [M6.2 wave A] A doorway call can reach module `modifiers`' producing
     * port, which reads and writes the scoped parse state; this surface never
     * runs a parse, so nothing else would have seeded it. */
    pcrec_parse_mods_init(&cx);

    int w = -1;
    for (int i = 0; i < 3; i++)
        if (!strcmp(want_name, want_names[i])) w = i;
    if (w < 0) return NULL;
    ExtWant want = (ExtWant)w;

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
    /* A PRODUCING port allocates its node from this arena and nothing below
     * reads it (`sb` holds only the rendered TSV, and `r.msg` is an inline
     * array). `--explain` has freed its arena since MOD-0.7; this call site
     * was the one that did not, which R20's critic noted while reading the
     * crash — the guard above makes the omission a leak on two paths instead
     * of one, so both are closed here. */
    arena_free(&cx.arena);
    return sb_take(&sb);
}

/* ---- `--explain QUERY` (SR-3; REWRITTEN at MOD-0.7) ---------------------
 *
 * A QUERY IS TEXT AT A DOORWAY, not a key into a column. That one sentence is
 * the rewrite. Until MOD-0.7 this was a mutual-prefix match against the
 * `syntax` column and nothing else — no `ext_`, no `registry_find`, no
 * arbitration — so D29's own worked example did not run (`--explain '(?i-m:'`
 * answered "no construct matches" while the doorway, asked the same text, said
 * "requires module 'modifiers'"), and R10/C4-2 refuted it as a control: a
 * table printing its own columns is a self-join, and swapping two rows'
 * module attributions left every assertion on it green (R10/C4-1, reproduced
 * at MOD-0.7a: docs/design/design_notes_mod07.md §0).
 *
 * WHAT THIS PRINTS, and the split is the design:
 *
 *   the QUERY's live answer   ONE doorway call on the text the user typed,
 *                             through the same router --probe-ask uses. It is
 *                             DATA and is never compared to anything: a query
 *                             legitimately gets an answer its bucket's rows do
 *                             not declare, measured in five cells ((?iZ),
 *                             (*NOTAVERB), [[:foo:]], [[:<:]], \p{Foo}).
 *                             Asserting agreement there would fire on a
 *                             CORRECT registry — R10/C1-1's refutation of D29.
 *   each ROW's live answer    one call per displayed row, on THAT ROW'S OWN
 *                             `syntax` (which registry.c already guarantees
 *                             reaches that row's doorway). DATA too — the
 *                             `own *` fields show it at the REQUESTED gate.
 *   each ROW's canonical      a SECOND call on the same syntax, pinned to the
 *   answer                    CLOSED gate. This one IS the assertion:
 *                             election, promise, attribution.
 *
 * THE CLAUSES ARE SCOPED TO THE CLOSED GATE, and that scope is the R20 fix
 * (MOD07-2/3, manager ruling). The agreement predicate is the CENSUSED claim
 * and §5.2's census was taken at the closed gate — so evaluating it anywhere
 * else asks a question it was never established over. Two defects lived in
 * the gap, both at the first open-gate cell: `--features modifiers --explain
 * '(?J)'` dissented on attribution ("declared 'modifiers', live names
 * 'named-groups'") for a tree tests/reject pins as CORRECT, because an
 * enabled port refuses per LETTER and the letter's module is not the row's;
 * and a producing answer short-circuited the other two clauses away, so
 * opening a gate SHRANK the coverage of the very rows it turned on. Judging
 * at the closed gate makes all three clauses total over the table at every
 * enabled set, and gives producing rows their dissent-capability back.
 *
 * HOW THE CLOSED GATE IS REACHED, and why it is not a global the code
 * temporarily rewrites: the canonical call asks WANT_VERDICT, which is the
 * exact ask §5.2's census used (`--probe-ask verdict` per row). It is
 * enabled-set-invariant BY CONSTRUCTION rather than by luck —
 * `pcrec_ext_gate` only ever DEMOTES and floors at VERDICT, so a VERDICT ask
 * cannot be promoted by any enabled set, and a BASE port (the one thing the
 * gate does not touch) answers at the level asked, which is also VERDICT.
 * Measured equivalent to a default-set RESULT ask on all 100 rows, every
 * field of `--probe-ask` compared.
 *
 * WHAT THE OPEN GATE STILL ASSERTS is one clause of its own, and it is a real
 * cross-check rather than a consolation: a row whose REQUESTED-gate answer
 * PRODUCES must have its declared module in the enabled set. That is the
 * question the old short-circuit walked past — it read `status` and stopped.
 *
 * AND THE HONEST LIMIT, stated here because the next reader will otherwise
 * assume the opposite: the attribution clause CANNOT dissent on a module-name
 * swap. ext.c renders "requires module '%s'" from `r->module`, the same field
 * this function prints, so the two agree by construction — measured, both
 * directions, 100 rows, zero census difference (§0). Module-name truth lives
 * in HAND-WRITTEN pins (tests/reject's 470, and cli case11's small named
 * subset), never here. What the live call adds that no table read can is
 * ELECTION: 13 rows share their rendered diagnostic with a bucket sibling, so
 * text cannot say which row answered.
 *
 * THIS IS NOT THE CHECK (R10 disposition 6: `--explain` may exist, it may not
 * be the control). registry_check's check_table_to_parser owns the row->parser
 * invariant over all 100 rows with no CLI in the loop; check_required_rows
 * owns row existence; tests/reject owns module names. This is a human surface
 * that shows both sources side by side and cannot silently print a
 * fabrication, plus one field nothing else reads.
 *
 * FORMAT (a strict grammar, so a test can assert per FIELD rather than per
 * blob — R10 §7: "not 'is there a reader' but 'can the reader dissent'"):
 * header lines are UNINDENTED `key<2+ spaces>value`; each row block starts
 * with the row's `syntax` unindented and continues with `  key<2+ spaces>value`
 * lines from a closed vocabulary; blocks are separated by one blank line. Keys
 * never contain two consecutive spaces, which is what makes the split
 * unambiguous. Row keys stay INDENTED because case10/case11 count `^  doorway`
 * lines to count rows, and a header key must not add one.
 *
 * CONTROL BYTES IN A VALUE ARE ESCAPED (R20/MOD07-8). Every value that can
 * carry bytes from the QUERY goes through `put_text`, which renders anything
 * below 0x20 and 0x7f as `\xHH`. Without it the grammar had no escaping at
 * all, and a query containing a newline injected a synthetic header line that
 * `explain_field` — the test helper that parses this very format — then read
 * as real: `--explain "$(printf '\\\nrows           99\n')"` reported
 * `rows 99` for an answer that displayed no rows. There is no attacker here
 * (it is the operator's own text), which is why the cure is a cheap rendering
 * rather than a quoting scheme.
 *
 * THE ESCAPE IS ONE-WAY, AND SAYS SO: `\` is NOT itself escaped, because
 * doing that would double every backslash on a surface whose whole subject is
 * backslash escapes, and would move every existing pin. So a literal
 * four-byte `\x0a` in a query and a real newline render alike. The ambiguity
 * is accepted deliberately — this is a human answer, not a wire format.
 * `--list-syntax` and `--probe-ask` are the surfaces with parsers, and both
 * FORBID these bytes rather than escape them (this file's own header says
 * why). Bytes >= 0x80 pass through untouched: they are not control bytes, and
 * R20/MOD07-B records that they are unreachable through argv anyway. */

/* Render `n` bytes with control bytes made visible. See the format grammar
 * above for why `\` is deliberately not escaped. */
static void put_text(StrBuf *sb, const char *s, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        unsigned char c = (unsigned char)s[i];
        if (c < 0x20 || c == 0x7f) sb_printf(sb, "\\x%02x", c);
        else                       sb_putc(sb, (char)c);
    }
}

/* Which module does a rendered answer PROMISE, if any? Derived in the CONSUMER
 * by looking for the `module 'NAME'` shape every doorway renders its promise
 * with — deliberately not a new `src` enum on ExtResult, which would mean
 * touching ~20 REFUSE sites and defaulting a new one to a wrong label. The
 * cost of deriving is stated rather than hidden: this can tell "promises a
 * module" from "does not", and it CANNOT tell whose text a non-promising
 * message is (the doorway's own, the verb name table's, a module port's).
 * The ROADMAP_NEVER wording contains "no module will implement it" and is
 * correctly read as promising nothing — the `'` is what makes that safe. */
static bool msg_module(const char *msg, char *out, size_t outsz)
{
    const char *p = strstr(msg, "module '");
    if (!p) return false;
    p += 8;
    const char *q = strchr(p, '\'');
    if (!q) return false;
    size_t n = (size_t)(q - p);
    if (n >= outsz) n = outsz - 1;
    memcpy(out, p, n);
    out[n] = '\0';
    return true;
}

typedef struct {
    bool      routed;
    Doorway   d;
    ExtResult r;
} Live;

/* ONE doorway call on `text`, through the shared router. The Ctx is the
 * CALLER'S and is reused across every call of one --explain invocation, so
 * the arena a producing port may allocate from is freed once at the end
 * rather than leaked per row (--probe-ask makes a single call and does not
 * face this). */
static Live live_answer(Ctx *cx, const char *text, ExtWant want)
{
    Live L;
    memset(&L, 0, sizeof L);
    cx->pat = text;
    cx->patlen = strlen(text);
    cx->pos = 0;
    if (!doorway_route(text, cx->patlen, &L.d)) return L;
    L.routed = true;
    L.r = doorway_call(cx, &L.d, want);
    return L;
}

/* The answer as one line. The producing outcomes get their own words: a
 * channel that reported them as a refusal would be the dump lying about the
 * one thing it exists to show (--probe-ask's own rule for its outcome
 * column). */
static void put_answer(StrBuf *sb, const Live *L)
{
    if (!L->routed) {
        sb_puts(sb, "—  (no doorway call: the base grammar answers this text "
                    "before the registry is consulted)");
        return;
    }
    switch (L->r.what) {
    /* ESCAPED (R20/MOD07-8): a refusal renders the selector byte into its
     * text ("unknown escape \%c"), so this value carries QUERY bytes just as
     * the `query` echo does. Escaping only the echo would have left the same
     * injection reachable one line down. */
    case EXT_REFUSAL:  put_text(sb, L->r.msg, strlen(L->r.msg)); break;
    case EXT_NOT_MINE: sb_puts(sb, "declines — no construct at this doorway"); break;
    case EXT_SCALAR:   sb_printf(sb, "produces one code point (0x%02X)",
                                 (unsigned)L->r.scalar); break;
    case EXT_MEMBERS:  sb_puts(sb, "produces a class member set"); break;
    case EXT_NODE:     sb_puts(sb, "produces an AST node"); break;
    default:           sb_puts(sb, "internal error: unknown doorway outcome"); break;
    }
}

static void put_names(StrBuf *sb, const Live *L)
{
    char mod[64];
    if (L->routed && L->r.what == EXT_REFUSAL && msg_module(L->r.msg, mod, sizeof mod))
        sb_puts(sb, mod);
    else
        sb_puts(sb, "—");
}

/* THE CLAUSES (design note §5.2, gate-scoped at R20/MOD07-2+3), evaluated on
 * the row's OWN syntax. Returns nonzero if this row dissents. The clause NAMES
 * are part of the format: a reader must be able to tell election from promise
 * from attribution from gate, so they are not free wording the way the rest of
 * the sentence is (D26 tier 3 covers the prose, not the clause identity).
 *
 * TWO ANSWERS COME IN, and which clause reads which is the whole R20 fix:
 *   `C`  the CANONICAL answer — WANT_VERDICT, enabled-set-invariant. Clauses
 *        1-3 read this and nothing else, because the closed gate is the
 *        population the predicate was censused over (see the file header).
 *   `own` the REQUESTED-gate answer, the one the `own *` fields display.
 *        Exactly one clause reads it: the gate cross-check below. */
static int put_agreement(StrBuf *sb, const RegRow *r, const Live *C,
                         const Live *own)
{
    /* `(?:...)` is the one row whose syntax reaches no doorway: the base
     * grammar answers it, so there is nothing to compare and saying so is the
     * honest answer rather than a fabricated pass. */
    if (!C->routed) {
        sb_puts(sb, "ok  (base grammar; no doorway call to compare)");
        return 0;
    }
    /* 0. GATE. The one clause about the REQUESTED enabled set, and the one
     * the old short-circuit was walking past: it read `status` and stopped,
     * so "this row produced" was never checked against "this row's module is
     * switched on". Producing with the gate shut would mean the gate is not
     * the thing deciding production — the single fact `--features` exists to
     * be true. (A BASE port produces gate-immune by design, but no row
     * reaches one through this surface: `--explain` routes escapes at ATOM
     * position and the base ports are all CLASS-position. If that changes,
     * this clause is where it must be taught the difference.) */
    bool produced = own->routed && own->r.what != EXT_NOT_MINE &&
                    own->r.what != EXT_REFUSAL;
    if (produced) {
        if (r->status != RS_MODULE) {
            sb_puts(sb, "DISSENT: gate: a row that is not RS_MODULE produced "
                        "a value");
            return 1;
        }
        if (!pcrec_feature_enabled(r->feature)) {
            sb_printf(sb, "DISSENT: gate: the row produced a value with its "
                          "module '%s' NOT in the enabled set", r->module);
            return 1;
        }
    }
    /* 1. ELECTION / REACHABILITY. A row's own canonical syntax must reach
     * THAT row. A decline is the same failure wearing a different hat: the
     * doorway walked away from a construct the table says is there. */
    if (C->r.what == EXT_NOT_MINE) {
        sb_puts(sb, "DISSENT: election: the row's own syntax DECLINES at its "
                    "own doorway");
        return 1;
    }
    /* [DD-14 wave F] A BYTE-KEYED INDEX ROW ELECTS ITS PRIMARY, AND THAT IS
     * THE CORRECT ANSWER RATHER THAN AN EXEMPTION.
     *
     * The clause above is right for every ordinary row: a row's own canonical
     * syntax must reach THAT row. An RF_INDEX row is the one shape for which
     * that sentence is false BY CONSTRUCTION — it exists to give a real PCRE2
     * spelling a line in the inventory, and `pcrec_registry_arbitrate` skips
     * it before any arm runs (D71 item 3), so it can never be elected
     * anywhere. Demanding it here would report a design decision as a defect.
     *
     * BUT NOTHING IS WEAKENED, because the honest claim is still checkable
     * and still specific: the spelling must reach a REAL row, and that row
     * must belong to the SAME MODULE. `(?10)` elects `(?1)`; `\g<0>` elects
     * `\g<1>`. A wrong `sel` on an index row would elect a different module's
     * row (or none) and fires here; so would an index row whose spelling
     * PCRE2 accepts but whose doorway pcrec never wired.
     *
     * THE ELECTED ROW IS NOT ALWAYS THE FAMILY'S PRIMARY, and that is why
     * this clause tests the MODULE rather than the `family` string: `(?01)`
     * belongs to the `(?1)` family (it means group 1) and dispatches on the
     * `(?0)` row (it enters on the zero byte). Both facts are true and they
     * are different facts — exactly the split D71 item 3 exists to make.
     *
     * The TWELVE `(*` alpha index rows do not reach this branch at all: their
     * doorway resolves them BY NAME through mod_verbs.c, so they really are
     * elected and the ordinary clause above passes for them. */
    if (C->r.row != r && (r->flags & RF_INDEX) != 0) {
        if (!C->r.row) {
            sb_printf(sb, "DISSENT: election: index row '%s' elected NO row "
                          "for its own syntax -- the spelling reaches no "
                          "doorway, so nothing can compile it", r->syntax);
            return 1;
        }
        if ((C->r.row->flags & RF_INDEX) != 0) {
            sb_printf(sb, "DISSENT: election: index row '%s' elected another "
                          "INDEX row '%s' -- an index row must never be "
                          "elected, so one of the two is reachable",
                      r->syntax, C->r.row->syntax);
            return 1;
        }
        if (!r->module || !C->r.row->module ||
            strcmp(r->module, C->r.row->module) != 0) {
            sb_printf(sb, "DISSENT: election: index row '%s' (module '%s') "
                          "elected '%s' (module '%s') -- an index row is a "
                          "SPELLING of its own module's construct, so a "
                          "cross-module election means its selector is wrong",
                      r->syntax, r->module ? r->module : "(none)",
                      C->r.row->syntax,
                      C->r.row->module ? C->r.row->module : "(none)");
            return 1;
        }
        sb_printf(sb, "ok  (index row; spelling elects '%s', same module)",
                  C->r.row->syntax);
        return 0;
    }
    if (C->r.row != r) {
        sb_printf(sb, "DISSENT: election: '%s' elected %s%s%s for its own syntax",
                  r->syntax,
                  C->r.row ? "'" : "no row",
                  C->r.row ? C->r.row->syntax : "",
                  C->r.row ? "'" : "");
        return 1;
    }
    /* A canonical answer CANNOT produce — WANT_VERDICT is below the level any
     * port answers at, and the gate never promotes. Reaching here with a
     * non-refusal would mean the ask contract itself is broken, which is not
     * a registry defect and must not be reported as one. */
    if (C->r.what != EXT_REFUSAL) {
        sb_puts(sb, "internal error: a WANT_VERDICT ask produced a value");
        return 1;
    }
    /* 2. PROMISE. A module is owed exactly when the row is a PLANNED module
     * row. K14's rule, and the one clause that fires on today's tree before
     * this milestone's own fix: a ROADMAP_NEVER row must not be promised. */
    char mod[64];
    bool named = msg_module(C->r.msg, mod, sizeof mod);
    bool owed  = (r->status == RS_MODULE && r->roadmap != ROADMAP_NEVER);
    if (named != owed) {
        sb_printf(sb, "DISSENT: promise: the row is %s%s and the live answer "
                      "promises %s",
                  r->status == RS_MODULE ? "a module row" : "not a module row",
                  r->status == RS_MODULE && r->roadmap == ROADMAP_NEVER
                      ? " marked NEVER" : "",
                  named ? mod : "none");
        return 1;
    }
    /* 3. ATTRIBUTION. Measured to be unable to dissent on a swap (§0); it is
     * here because it is cheap and because the OTHER sources of a module name
     * — the POSIX name table, the verb name tables — could put a different
     * one in this text without the row changing at all.
     *
     * IT READS THE CANONICAL ANSWER, and R20/MOD07-2 is why: at an open gate
     * the module's port refuses per LETTER, so `(?J)` renders module
     * 'named-groups' from the `(?J` GROUP_OPT row whose declared module is
     * 'modifiers'. Both are correct — the option-run row dispatches, the
     * letter decides who owes the feature — and comparing them fired on a
     * tree tests/reject pins as right. */
    if (named && strcmp(mod, r->module) != 0) {
        sb_printf(sb, "DISSENT: attribution: declared '%s', live names '%s'",
                  r->module, mod);
        return 1;
    }
    if (produced) {
        sb_puts(sb, "ok  (clauses at the closed gate; at this one the row "
                    "produces and its module is enabled)");
        return 0;
    }
    sb_puts(sb, "ok");
    return 0;
}

/* The `(*` doorway's SECOND SOURCE, shown beside the row (design note §4.3).
 * Doorway 3 has exactly one RegRow, so the row alone is a fiction: what
 * decides the answer is the VerbName tables, a separate schema whose every
 * bit PC-3 re-measures against libpcre2 on every run, and which carries a
 * PER-NAME roadmap the row does not. This block is DISPLAY, deliberately with
 * no `agree` line: a per-name roadmap DIFFERING from the row's is correct
 * ((*COMMIT) is NEVER while the row is PLANNED), so a clause here would fire
 * on correct data — the shape R10/C1-1 refuted. Consistency of these tables
 * with libpcre2 is PC-3's assertion, not this surface's. */
static void put_verb_block(StrBuf *sb, const char *query, const Doorway *d)
{
    size_t qlen = strlen(query);
    size_t nstart = d->at + 2;
    if (nstart > qlen) return;
    /* The scan returns the INDEX of the terminator (== patlen when the text
     * ends first), not a length — scans.c's own contract. */
    size_t namelen = pcrec_verb_name_extent_scan(query, qlen, nstart) - nstart;
    if (namelen == 0) return;
    const VerbTable *t = pcrec_registry_verb_table((unsigned char)query[nstart]);
    const VerbName *v = pcrec_registry_verb_find(t, query + nstart, namelen);
    const RegRow *row = pcrec_registry_find(RK_VERB, REG_SEL_ANY, NULL, 0);

    /* the NAME is query text; escaped for the same reason (R20/MOD07-8) */
    sb_puts(sb, "\nverb name ");
    put_text(sb, query + nstart, namelen);
    sb_putc(sb, '\n');
    sb_printf(sb, "  table        %s\n",
              t == pcrec_registry_verb_tables(0) ? "upper" : "lower");
    sb_printf(sb, "  known        %s\n", v ? "yes" : "no");
    if (!v) {
        sb_printf(sb, "  unknown      %s\n", t->unknown_msg);
        return;
    }
    sb_puts(sb, "  forms        ");
    {
        unsigned f = v->forms;
        if (f & VF_BARE)     sb_puts(sb, "(*N)");
        if (f & VF_ARG)      sb_puts(sb, (f & VF_BARE) ? "|(*N:a)" : "(*N:a)");
        if (f & VF_EMPTYARG) sb_puts(sb, "|(*N:)");
        if (f & VF_EQNUM)    sb_puts(sb, (f & (VF_BARE|VF_ARG|VF_EMPTYARG))
                                          ? "|(*N=d)" : "(*N=d)");
        if (f & VF_GROUPARG) sb_puts(sb, "|arg-is-subpattern");
        if (f & VF_ATSTART)  sb_puts(sb, "|start-of-pattern-only");
        sb_putc(sb, '\n');
    }
    /* The EFFECTIVE roadmap and where it came from — the cross-source pair
     * this block exists for. */
    sb_printf(sb, "  roadmap      %s\n",
              (v->roadmap ? v->roadmap : (row ? row->roadmap : ROADMAP_NONE))
                  == ROADMAP_NEVER ? "never" : "planned");
    sb_printf(sb, "  roadmap src  %s\n",
              v->roadmap ? "the verb NAME's own entry"
                         : "inherited from the (* row");
    sb_printf(sb, "  quant        %s\n",
              v->quant == QV_YES ? "yes" : v->quant == QV_NO ? "no"
                                                             : "not-askable");
}

char *pcrec_syntax_explain(const char *query, unsigned flavours, int *ndissent,
                           pcrec_error *err)
{
    StrBuf body = {0}, sb = {0};
    size_t qlen = strlen(query);
    volatile int rows_shown = 0, dissents = 0;

    /* ONE Ctx for the whole invocation, reused across every call, its arena
     * freed at the end — and GUARDED since R20/MOD07-1. The old comment here
     * asserted "no jmp target — every doorway RETURNS its answer, the D33 §5
     * contract"; §5's contract is about the doorway's own terminal answer and
     * says nothing about a PORT, which recurses into `pcrec_parse_body` and
     * can `ctx_fail` from arbitrarily deep. See `doorway_call`'s header for
     * the full history. */
    Ctx cx;
    memset(&cx, 0, sizeof cx);
    cx.err = err;
    cx.arena.cx = &cx;   /* [M4.7b/K7] arena OOM -> this setjmp, not abort() */
    if (err) { err->msg[0] = '\0'; err->pos = 0; }

    /* ABANDON THE WHOLE ANSWER, rather than render the raise per line and
     * carry on. The reason is not tidiness: after a longjmp out of a
     * half-finished parse this Ctx's own state (`depth`, `ncap`, `mods`, and
     * whatever the arena holds) is arbitrary, and every remaining row block
     * would be a further call THROUGH that Ctx. Continuing would be a fresh
     * instance of exactly the reasoning that produced this defect — safe
     * today, unmeasured, and load-bearing for whoever adds the next port. One
     * raise, one honest error, no partial table.
     *
     * `body`, `sb` and `cx` are declared above the `setjmp` and mutated only
     * through their escaped addresses; `rows_shown`/`dissents` are mutated
     * after it and are deliberately not read here. `volatile` on both (SAN-1
     * F1, manager triage 2026-08-13) is the setjmp/longjmp clobber contract
     * for exactly this invariant, not a threading concern. */
    if (setjmp(cx.jb)) {
        sb_free(&body);
        sb_free(&sb);
        arena_free(&cx.arena);
        if (ndissent) *ndissent = 0;
        return NULL;
    }

    /* [M6.2 wave A] see the sibling seed in pcrec_probe_ask. */
    pcrec_parse_mods_init(&cx);

    /* WANT_RESULT is what parse.c asks — the real ask — so `--explain` shows
     * what pcrec would actually DO with the text. With the default empty
     * enabled set the gate demotes every one of these to VERDICT, which is
     * why `live answered` reads `verdict` until a `--features` names the
     * row's module. */
    Live q = live_answer(&cx, query, WANT_RESULT);

    for (size_t k = 0; k < NELEMS(all_kinds); k++) {
        size_t n;
        const RegRow *rows = pcrec_registry(all_kinds[k], &n);
        for (size_t i = 0; i < n; i++) {
            const RegRow *r = &rows[i];
            if (flavours && !(r->flavours & flavours)) continue;
            if (!r->syntax) continue;

            /* SELECTION is two rules with two meanings, and the row says
             * which one put it here (design note §3.3):
             *
             *   candidate  the row is in the bucket the query's doorway
             *              arbitrates over — it COMPETED for this text. This
             *              is what makes `--explain '(?i-m:'` answer at all,
             *              and what shows `\N{U+0041}` its third row.
             *   listed     the mutual-prefix match, kept: it answers "which
             *              rows look like what I typed", which is a real use
             *              (`--explain '(?'` is a catalogue) and which cli
             *              case10 has depended on since SR-3.
             *
             * A row can be both; `candidate` wins the label. */
            size_t slen = strlen(r->syntax);
            size_t cmp = qlen < slen ? qlen : slen;
            bool listed = cmp != 0 && strncmp(query, r->syntax, cmp) == 0;
            /* [M6.4.2] A NON-DOORWAY ROW IS `listed` ONLY ON AN EXACT MATCH,
             * and that is the mutual-prefix rule read correctly rather than an
             * exception to it.
             *
             * The prefix half of `listed` is valuable because a DOORWAY row's
             * `syntax` begins with the doorway text you partially type:
             * `--explain '(?'` is a catalogue of the `(?` bucket, which is a
             * real use and one cli case10 has depended on since SR-3. An
             * RK_QUANTSUFFIX row has no such prefix — its `syntax` must be an
             * EXECUTABLE pattern (tests/reject/run_reject_tests.sh RUNS it), so
             * a possessive suffix has to carry an atom, and `a*+`'s leading `a`
             * is a CARRIER rather than part of the construct.
             *
             * Without this clause every one-letter base query matched all four
             * rows: `--explain 'a'` listed `a*+ a++ a?+ a{1,2}+` and EXITED 0,
             * where `--explain` on base syntax must exit 1 saying "no construct
             * matches" (cli case11). MEASURED as an 11-check `make test`
             * failure before this line existed. */
            /* [DD-11.1] RK_BARE joins the same exemption and for the same
             * reason: the plain capturing-group row's `syntax` needs a
             * CARRIER atom to be an executable probe (`(a)`, not bare `(`),
             * so a naive prefix match would let `--explain 'a'` list it —
             * measured the identical way RK_QUANTSUFFIX's carrier was.
             * `^`/`$` have no carrier (their `syntax` IS the whole
             * construct), so this clause is a no-op for them, but the rule
             * keys on the KIND, matching RK_QUANTSUFFIX's own discipline,
             * not on a per-row carrier flag. */
            if (listed && (r->kind == RK_QUANTSUFFIX || r->kind == RK_BARE)
                && qlen != slen)
                listed = false;
            bool candidate = q.routed && r->kind == q.d.kind &&
                             r->sel != REG_SEL_ANY && r->sel == q.d.sel;
            /* The bucket's catch-all is shown ONLY when the arbitration
             * actually elected it. Printing it for every query in its kind
             * would assert a reachability the arbitration denies: for `(?<`
             * the bare `<` row always answers, so the `(?` catch-all is
             * unreachable there. */
            bool fallback = q.routed && r->sel == REG_SEL_ANY && q.r.row == r;
            if (!listed && !candidate && !fallback) continue;

            /* TWO calls on the row's own syntax (R20/MOD07-2+3): `own` at
             * the REQUESTED gate is what the `own *` fields display, and
             * `canon` at WANT_VERDICT is what the clauses judge. They are the
             * same answer whenever the row's module is not enabled, which is
             * every row at the default set — the second call buys nothing
             * there and costs nothing either, and paying for it
             * unconditionally is what keeps the clause scope from depending
             * on a branch someone has to remember. */
            Live own   = live_answer(&cx, r->syntax, WANT_RESULT);
            Live canon = live_answer(&cx, r->syntax, WANT_VERDICT);

            if (rows_shown++) sb_putc(&body, '\n');
            sb_printf(&body, "%s\n", r->syntax);
            sb_printf(&body, "  select       %s\n",
                      candidate ? "candidate" : fallback ? "fallback" : "listed");
            sb_printf(&body, "  doorway      %s\n", doorway_name(r->kind));
            switch (r->status) {
            case RS_BASE:
                sb_puts(&body, "  status       implemented by the base grammar\n");
                break;
            case RS_MODULE:
                /* K14, ON THE QUERY SURFACE (design note §1 — the defect this
                 * milestone found by applying its own design to the first row
                 * it touched). A ROADMAP_NEVER row is real PCRE2 syntax pcrec
                 * has decided never to implement, and promising its module is
                 * the tier-2 defect D26 names in its own words: "Naming a
                 * module that will never implement a construct is a defect."
                 * ext.c has answered this correctly since MOD-0.1 and
                 * put_expect (100 lines above, same file) has rendered it
                 * correctly for --list-syntax's `expect` column since the same
                 * milestone; --explain kept promising, because it never read
                 * `roadmap`. Zero RS_MODULE ROADMAP_NEVER rows today —
                 * (?C1) carried it alone until [M4-CALLOUTS] step 1 (D36,
                 * 2026-08-14) flipped it to PLANNED; the branch is derived,
                 * so the next one is covered the day it exists.
                 *
                 * The `agree` clause CANNOT see this — both of its sides read
                 * the row — so cli case11's hand-written pin is the only net,
                 * which is §0's lesson recurring inside the milestone that
                 * found it. */
                if (r->roadmap == ROADMAP_NEVER)
                    sb_puts(&body, "  status       known, outside pcrec's scope "
                                   "— no module will implement it\n");
                else
                    sb_printf(&body, "  status       known, unimplemented — "
                                     "requires module '%s'\n", r->module);
                break;
            case RS_REJECTED:
                sb_puts(&body, "  status       rejected, as PCRE2 rejects it too\n");
                break;
            }
            sb_printf(&body, "  module       %s\n", r->module ? r->module : "—");
            sb_printf(&body, "  roadmap      %s\n",
                      r->roadmap == ROADMAP_NEVER   ? "never"
                    : r->roadmap == ROADMAP_PLANNED ? "planned" : "—");
            if (r->diag == RD_FIXED && r->msg)
                sb_printf(&body, "  error        %s\n", r->msg);
            sb_puts(&body, "  flavours     ");
            put_mask(&body, r->flavours, flavour_names, NELEMS(flavour_names));
            sb_puts(&body, "\n  engines      ");
            if (r->engines)
                put_mask(&body, r->engines, engine_names, NELEMS(engine_names));
            else
                sb_puts(&body, "none");
            sb_puts(&body, "  (design intent, unconsumed until SR-8)\n");
            /* DECLARED, never observed: `--explain` probes ATOM position only
             * (the router's first opener for `[\d]` is the `[`, so an
             * in-class escape query lands on the class-bracket doorway and
             * honestly declines). class_expect is libpcre2-measured and
             * check04 re-verifies it; in-class routing is a MOD-0.8 item. */
            sb_printf(&body, "  class        %s\n",
                      r->class_expect ? r->class_expect
                                      : "— (cannot reach a class position)");
            if (r->note) sb_printf(&body, "  note         %s\n", r->note);
            sb_puts(&body, "  own          "); put_answer(&body, &own);
            sb_putc(&body, '\n');
            if (own.routed)
                sb_printf(&body, "  own at       %zu\n", own.r.at);
            sb_printf(&body, "  own elected  %s\n",
                      !own.routed        ? "—"
                    : own.r.row == r     ? "self"
                    : own.r.row          ? own.r.row->syntax : "none");
            sb_puts(&body, "  own names    "); put_names(&body, &own);
            sb_putc(&body, '\n');
            sb_puts(&body, "  agree        ");
            dissents += put_agreement(&body, r, &canon, &own);
            sb_putc(&body, '\n');
        }
    }

    if (!rows_shown && !q.routed) {
        sb_free(&body);
        arena_free(&cx.arena);
        if (ndissent) *ndissent = 0;
        return NULL;      /* not doorway territory and no row looks like it */
    }

    /* the two ECHOES of query text, escaped (R20/MOD07-8) */
    sb_puts(&sb, "query          ");
    put_text(&sb, query, qlen);
    sb_putc(&sb, '\n');
    if (q.routed) {
        sb_printf(&sb, "route          %s", doorway_name(q.d.kind));
        if (q.d.kind == RK_VERB)
            sb_puts(&sb, "  (the NAME decides; see the verb block)");
        else if (q.d.sel < 0)
            sb_puts(&sb, "  selector none (the text ends at the doorway)");
        else {
            char selb = (char)q.d.sel;
            sb_puts(&sb, "  selector '");
            put_text(&sb, &selb, 1);
            sb_putc(&sb, '\'');
        }
        sb_putc(&sb, '\n');
    } else {
        sb_puts(&sb, "route          none — the base grammar answers this text "
                     "before any doorway is consulted\n");
    }
    sb_puts(&sb, "live           "); put_answer(&sb, &q); sb_putc(&sb, '\n');
    if (q.routed) {
        static const char *const want_names[] = { "claim", "verdict", "result" };
        sb_printf(&sb, "live at        %zu\n", q.r.at);
        sb_printf(&sb, "live elected   %s\n",
                  q.r.row ? q.r.row->syntax : "none");
        sb_printf(&sb, "live answered  %s\n", want_names[q.r.answered_at]);
        sb_puts(&sb, "live names     "); put_names(&sb, &q); sb_putc(&sb, '\n');
    }
    sb_printf(&sb, "rows           %d\n", rows_shown);
    sb_printf(&sb, "dissents       %d\n", dissents);
    if (q.routed && q.d.kind == RK_VERB)
        put_verb_block(&sb, query, &q.d);
    if (rows_shown) {
        char *b = sb_take(&body);
        sb_putc(&sb, '\n');
        sb_puts(&sb, b);
        free(b);
    }
    sb_free(&body);
    arena_free(&cx.arena);
    if (ndissent) *ndissent = dissents;
    return sb_take(&sb);
}
