/* src/parse/rxt_schema.c — [DD-13b.W23.1] THE SCHEMA TABLE'S READER.
 *
 * `src/parse/rxt_schema.def` is the table (its header is the row shape and
 * the reasoning); this file is the only thing that knows how to read it, and
 * every other consumer — the parser's dispatch walk, `--list-schema`, the
 * spec's rendered tables — goes through here. `src/parse/definitions.c`'s
 * `pcrec_def_tag_applies` is the shape the design names
 * (format_design §2.25.1): ONE exhaustive, `default:`-less switch over the
 * constraint enum, so an eighth constraint kind is a compile error at
 * exactly the site that must handle it.
 *
 * WHAT THIS FILE PROVES AND WHAT IT DOES NOT. It proves the parser and the
 * dump read ONE table: both call `pcrec_rxt_schema_rows` and neither carries
 * a copy. It does NOT prove the table says anything true about what the
 * parser ENFORCES — a row could declare `cardinality: at-most-one` for a
 * kind nothing counts. `tests/rxtsource/`'s W23-S3 is the independent side
 * of that claim: it drives each row's own BEHAVIOUR and compares the
 * result against the dump, never the dump against the table, because the
 * table and the parser are one source and comparing them twice is comparing
 * it to itself (docs/dev/learnings.md §3).
 */

#include <stddef.h>
#include <string.h>

#include "pcrec.h"
#include "core/internal.h"

/* The table, expanded once. Every column token is pasted into its enum
 * spelling here and nowhere else, so the `.def`'s bare words (`FILE`,
 * `PROSE`, `AT_MOST_ONE`) are a table author's vocabulary rather than a
 * second set of names a reader has to reconcile with the C one. */
static const RxtSchemaRow g_rows[] = {
#define PCREC_RXT_SCHEMA(scope, kind, value, opens, children, card, cons, \
                         src, vb, wave)                                    \
    { RXT_SCOPE_##scope, kind, RXT_VAL_##value, opens, RXT_CH_##children,  \
      RXT_CARD_##card, cons, RXT_SRC_##src, RXT_VB_##vb, wave },
#include "parse/rxt_schema.def"
};

/* The schema table and its row count. */
const RxtSchemaRow *pcrec_rxt_schema_rows(size_t *n)
{
    if (n) *n = sizeof g_rows / sizeof *g_rows;
    return g_rows;
}

/* Row count alone, for a caller that does not need the table itself. */
size_t pcrec_rxt_schema_nrows(void)
{
    return sizeof g_rows / sizeof *g_rows;
}

/* Linear lookup of the row for `kind` (matched by exact length+bytes) within
 * `scope`, or NULL. */
const RxtSchemaRow *pcrec_rxt_schema_row(RxtSchemaScope scope, const char *kind,
                                         size_t klen)
{
    for (size_t i = 0; i < sizeof g_rows / sizeof *g_rows; i++) {
        const RxtSchemaRow *r = &g_rows[i];
        if (r->scope != scope) continue;
        if (strlen(r->kind) == klen && !strncmp(r->kind, kind, klen))
            return r;
    }
    return NULL;
}

/* ---- the three structure-layer parameters (format_design §1.2.1) ------
 *
 * Each is ONE column read. That is the property, not an implementation
 * detail: `--list-schema` answers all three as ROW SETS SELECTED BY A
 * COLUMN VALUE, so a generic reader fetches them out of one TSV and no
 * predicate escapes into a consumer. Parameter 1 (`opens_group`, a plain
 * column read) has no accessor here -- both readers (this file's own
 * block-scan loop, below, and `schema_dump.c`'s dump row) read
 * `r->opens_group` directly. */

/* PARAMETER 2 IS THE PAIR, and reading `value` alone is the bug S-R5's
 * plant (b) exists to catch: flipping a row's `children` from `prose` to
 * `none` while leaving `value: prose` would change nothing a reader can
 * observe — the region still opens, its lines are still bytes, so they
 * never reach a validity check either — leaving a normative column with no
 * detector anywhere. */
int pcrec_rxt_schema_prose_region(const RxtSchemaRow *r)
{
    return r && r->value == RXT_VAL_PROSE && r->children == RXT_CH_PROSE;
}

/* PARAMETER 3, the OPEN SUBTREE (r58 ruling R1). Inside the subtree rooted
 * at such a line, S2's opener set is EMPTY and S3 NEVER OPENS — both are
 * properties of the SUBTREE and never of the keyword `ext`, which is why a
 * reader fetches `children` for the line it is attaching under rather than
 * testing a token. format_design §1.2.1's parameter table is the normative
 * statement of the two effects and this comment points at it. */
int pcrec_rxt_schema_open_subtree(const RxtSchemaRow *r)
{
    return r && r->children == RXT_CH_TREE;
}

/* The RxtSchemaScope a row's children parse under, derived from `r->children`
 * (RXT_SCOPE_NSCOPES for a row with no child scope of its own --
 * NONE/PROSE/TREE). */
RxtSchemaScope pcrec_rxt_schema_child_scope(const RxtSchemaRow *r)
{
    if (!r) return RXT_SCOPE_NSCOPES;
    switch (r->children) {
        case RXT_CH_CONFIG:     return RXT_SCOPE_CONFIG;
        case RXT_CH_BUNDLE:     return RXT_SCOPE_BUNDLE;
        case RXT_CH_DATA:       return RXT_SCOPE_DATA;
        case RXT_CH_PROVENANCE: return RXT_SCOPE_PROVENANCE;
        case RXT_CH_VARIANT:    return RXT_SCOPE_VARIANT;
        case RXT_CH_NONE:
        case RXT_CH_PROSE:
        case RXT_CH_TREE:       break;
    }
    return RXT_SCOPE_NSCOPES;
}

/* THE ONE MAPPING THE TABLE DOES NOT CARRY, and it is a decision rather
 * than an omission: a group opened by a `pattern` line at FILE scope holds
 * BLOCK-scope lines. `opens_group` is a boolean by §2.25.2, and `children`
 * on an opener row means something else (nothing may be INDENTED under a
 * `pattern` line — that is still a structure error), so there is no column
 * this fact fits in today. D77's trigger for making one: a SECOND group
 * opener at a different scope, at which point "the group's scope" stops
 * being derivable from the opener's own and becomes a per-row fact. Both of
 * today's openers (`pattern`, `pattern-esc`) sit at file scope and open a
 * block. */
RxtSchemaScope pcrec_rxt_schema_group_scope(RxtSchemaScope opener_scope)
{
    return opener_scope == RXT_SCOPE_FILE ? RXT_SCOPE_BLOCK
                                          : RXT_SCOPE_NSCOPES;
}

/* ---- column renderings ------------------------------------------------
 *
 * Shared by the dump AND by every diagnostic that names a scope, so a
 * refusal ("'%s' is not a %s directive") and `--list-schema`'s own `scope`
 * column cannot drift into two vocabularies for one thing. */

/* The scope's name column ("file"/"block"/...), shared by every diagnostic and
 * by --list-schema's own `scope` column so the two cannot drift -- see the
 * banner above. */
const char *pcrec_rxt_scope_name(RxtSchemaScope s)
{
    switch (s) {
        case RXT_SCOPE_FILE:       return "file";
        case RXT_SCOPE_BLOCK:      return "block";
        case RXT_SCOPE_CONFIG:     return "config";
        case RXT_SCOPE_BUNDLE:     return "bundle";
        case RXT_SCOPE_DATA:       return "data";
        case RXT_SCOPE_PROVENANCE: return "provenance";
        case RXT_SCOPE_VARIANT:    return "variant";
        case RXT_SCOPE_NSCOPES:    break;
    }
    return "?";
}

/* The value-shape's name column ("none"/"token"/.../"raw"). */
const char *pcrec_rxt_value_name(RxtValueShape v)
{
    switch (v) {
        case RXT_VAL_NONE:      return "none";
        case RXT_VAL_TOKEN:     return "token";
        case RXT_VAL_INT:       return "int";
        case RXT_VAL_LINE:      return "line";
        case RXT_VAL_PROSE:     return "prose";
        case RXT_VAL_LIST:      return "list";
        case RXT_VAL_PAIR:      return "pair";
        case RXT_VAL_SUBJECT:   return "subject";
        case RXT_VAL_CASE:      return "case";
        case RXT_VAL_QUALIFIED: return "qualified-line";
        case RXT_VAL_RAW:       return "raw";
    }
    return "?";
}

/* The children-kind's name column ("none"/"prose"/.../"variant"). */
const char *pcrec_rxt_children_name(RxtChildren c)
{
    switch (c) {
        case RXT_CH_NONE:       return "none";
        case RXT_CH_PROSE:      return "prose";
        case RXT_CH_TREE:       return "tree";
        case RXT_CH_CONFIG:     return "config";
        case RXT_CH_BUNDLE:     return "bundle";
        case RXT_CH_DATA:       return "data";
        case RXT_CH_PROVENANCE: return "provenance";
        case RXT_CH_VARIANT:    return "variant";
    }
    return "?";
}

/* The cardinality's name column ("one"/"at-most-one"/"repeat"/"accumulate"). */
const char *pcrec_rxt_cardinality_name(RxtCardinality c)
{
    switch (c) {
        case RXT_CARD_ONE:          return "one";
        case RXT_CARD_AT_MOST_ONE:  return "at-most-one";
        case RXT_CARD_REPEAT:       return "repeat";
        case RXT_CARD_ACCUMULATE:   return "accumulate";
    }
    return "?";
}

/* The row-source's name column ("format"/"file"). */
const char *pcrec_rxt_row_source_name(RxtRowSource s)
{
    switch (s) {
        case RXT_SRC_FORMAT: return "format";
        case RXT_SRC_FILE:   return "file";
    }
    return "?";
}

/* The validated-by kind's name column ("pcrec"/"all-readers"/"none"). */
const char *pcrec_rxt_validated_by_name(RxtValidatedBy v)
{
    switch (v) {
        case RXT_VB_PCREC:       return "pcrec";
        case RXT_VB_ALL_READERS: return "all-readers";
        case RXT_VB_NONE:        return "none";
    }
    return "?";
}

/* ---- THE ONE EXHAUSTIVE SITE ------------------------------------------
 *
 * `default:` IS DELIBERATELY ABSENT, and it is the whole reason the
 * constraint vocabulary is an enum rather than a set of strings: adding an
 * eighth kind must be a COMPILE ERROR here, at the site that has to decide
 * what the new kind is called and therefore how it is spelled in a `.def`
 * row and in `--list-schema`. `src/opt/mrl.c:39-45` states the house rule;
 * `src/parse/definitions.c`'s `pcrec_def_tag_applies` is the precedent
 * format_design §2.25.1 names.
 *
 * SEVEN KINDS. `cross-scope` is not one of them (D99 withdrew its only
 * customer, `provides`); adding it back is this switch plus one enumerator
 * plus a `.def` column value, which is why waiting costs nothing. */
/* The constraint kind's name column ("required"/.../"functional-binding") --
 * the one place a new kind must be named, per the banner above's no-default
 * rule. */
static const char *pcrec_rxt_constraint_name(RxtConstraintKind k)
{
    switch (k) {
        case RXT_C_REQUIRED:           return "required";
        case RXT_C_REQUIRED_IF:        return "required-if";
        case RXT_C_FORBIDDEN_IF:       return "forbidden-if";
        case RXT_C_EXACTLY_ONE_OF:     return "exactly-one-of";
        case RXT_C_CLOSED:             return "closed";
        case RXT_C_UNIQUE_BY:          return "unique-by";
        case RXT_C_FUNCTIONAL_BINDING: return "functional-binding";
        case RXT_C_NKINDS:             break;
    }
    return "?";
}

/* The `constraints` column is `;`-separated clauses, each `<kind> [arg…]`.
 * A clause's kind is resolved by NAME against the switch above — so the
 * table's spelling and the enum cannot drift, because there is one place
 * a kind is named — and a clause naming nothing in it returns -1 rather
 * than being skipped, since a silently-ignored constraint is a rule the
 * schema claims to declare and does not. */
int pcrec_rxt_constraint_next(const char **cur, RxtConstraintKind *k,
                              const char **arg, size_t *arglen)
{
    const char *s = *cur;
    while (*s == ' ' || *s == ';') s++;
    if (!*s) { *cur = s; return 0; }

    const char *end = s;
    while (*end && *end != ';') end++;

    const char *word_end = s;
    while (word_end < end && *word_end != ' ') word_end++;
    size_t wlen = (size_t)(word_end - s);

    RxtConstraintKind found = RXT_C_NKINDS;
    for (int i = 0; i < (int)RXT_C_NKINDS; i++) {
        const char *nm = pcrec_rxt_constraint_name((RxtConstraintKind)i);
        if (strlen(nm) == wlen && !strncmp(nm, s, wlen)) {
            found = (RxtConstraintKind)i;
            break;
        }
    }
    *cur = end;
    if (found == RXT_C_NKINDS) return -1;

    const char *a = word_end;
    while (a < end && *a == ' ') a++;
    size_t alen = (size_t)(end - a);
    while (alen && a[alen - 1] == ' ') alen--;

    *k = found;
    *arg = a;
    *arglen = alen;
    return 1;
}

/* THE OPENER SET (structure-layer parameter 1) AS A SCOPE-FREE QUERY.
 * S2 reads "a line whose first token is a member of the BLOCK-OPENER SET",
 * and that set is not scoped: the opener's own row lives in the scope of
 * the group it opens (BLOCK), while the line itself sits among the head's
 * siblings. So a reader asks "is this token an opener" of the whole table
 * and gets the row back, which is also what makes the set a one-column
 * `--list-schema` query rather than a per-scope lookup a consumer would
 * have to repeat. */
const RxtSchemaRow *pcrec_rxt_schema_opener(const char *kind, size_t klen)
{
    for (size_t i = 0; i < sizeof g_rows / sizeof *g_rows; i++) {
        const RxtSchemaRow *r = &g_rows[i];
        if (!r->opens_group) continue;
        if (strlen(r->kind) == klen && !strncmp(r->kind, kind, klen))
            return r;
    }
    return NULL;
}

/* The diagnostic's name for a scope, beside the DUMP's name for it — two
 * renderings of one enum in one switch each, so a refusal ("'%s' is not a
 * %s directive") and `--list-schema`'s `scope` column cannot drift into two
 * vocabularies. They differ because they answer different questions: the
 * column is the scope's ADDRESS and the context is what a reader of a
 * diagnostic calls the region they are standing in. */
const char *pcrec_rxt_scope_context(RxtSchemaScope s)
{
    switch (s) {
        case RXT_SCOPE_FILE:       return "file-level";
        case RXT_SCOPE_BLOCK:      return "pattern-block";
        case RXT_SCOPE_CONFIG:     return "config-block";
        case RXT_SCOPE_BUNDLE:     return "analysis-bundle";
        case RXT_SCOPE_DATA:       return "data-block";
        case RXT_SCOPE_PROVENANCE: return "provenance";
        case RXT_SCOPE_VARIANT:    return "variant";
        case RXT_SCOPE_NSCOPES:    break;
    }
    return "?";
}

/* The NOUN a cardinality refusal uses for the thing that may hold one of
 * something ("a pattern block has one 'description'"). Third rendering,
 * same enum, same file — never a literal at the refusal site. */
const char *pcrec_rxt_scope_noun(RxtSchemaScope s)
{
    switch (s) {
        case RXT_SCOPE_FILE:       return "file";
        case RXT_SCOPE_BLOCK:      return "pattern block";
        case RXT_SCOPE_CONFIG:     return "config body";
        case RXT_SCOPE_BUNDLE:     return "bundle";
        case RXT_SCOPE_DATA:       return "data block";
        case RXT_SCOPE_PROVENANCE: return "provenance record";
        case RXT_SCOPE_VARIANT:    return "variant";
        case RXT_SCOPE_NSCOPES:    break;
    }
    return "?";
}
