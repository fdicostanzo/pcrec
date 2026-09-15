/* src/parse/schema_dump.c — [DD-13b.W23.1] `pcrec --list-schema`, the
 * `.rxt` format schema's TSV surface: the SEVENTH registry dump
 * (docs/spec/table_contract.md, docs/spec/registry.md, docs/spec/cli.md)
 * and the eighth conforming table producer.
 *
 * WHAT THIS DUMP PROVES AND WHAT IT DOES NOT. It `#include`s
 * `src/parse/rxt_schema.def` NOWHERE: it walks the table through
 * `pcrec_rxt_schema_rows()`, the SAME entry the parser's dispatch walk uses
 * — one derivation, two readers — so a dump that disagrees with the parser
 * about which rows exist is not expressible. It does NOT prove the parser
 * ENFORCES what a row declares; `tests/rxtsource/`'s W23-S3 is the
 * independent side, driving each row's own BEHAVIOUR and comparing that
 * against this output. Comparing this output to the table would be the same
 * source twice (docs/dev/learnings.md §3), which is the one thing a check
 * over this dump must not do. `src/parse/limits_dump.c` is the shape.
 *
 * THE THREE STRUCTURE-LAYER PARAMETERS ARE NOT THREE QUERIES HERE. Each is
 * a COLUMN VALUE a consumer selects on — `opens_group = true`;
 * `value = prose` AND `children = prose`; `children = tree` — so a generic
 * `.rxt` reader FETCHES the structure layer's parameters out of this one
 * TSV rather than hard-coding them, and no predicate escapes into the
 * consumer. That property is why the aux production's `children: tree`
 * became a schema COLUMN VALUE rather than an exception keyed on the token
 * `ext` (format_design §1.2.1's parameter table, §2.27.2 decision 2).
 *
 * TWO SECTIONS, BOTH NAMED. `#section schema` is the table;
 * `#section surface` is the DECLARED NON-COVERAGE — four rows saying what
 * this schema does not claim to validate, and why. An absence in a table
 * reads as something nobody got to; a declared non-coverage row reads as
 * something somebody decided, with the reason attached (§2.27.4). The main
 * table is NAMED rather than left anonymous so `tests/lib/table.sh` can
 * address it: a multi-section stream read with no section argument fails
 * loudly by that contract's Sections rule 4, and an unnameable first
 * section would leave the schema itself the one table no conforming
 * consumer could ask for.
 *
 * Wire format: docs/spec/table_contract.md (TSV, `#` comments, the last `#`
 * line before a section's data is that section's header, columns
 * append-only within a section). */

#include <stdio.h>
#include <string.h>

#include "core/internal.h"
#include "pcrec.h"

/* THE DECLARED NON-COVERAGE, four rows (format_design §2.24, §2.27.4).
 *
 * Two of them ARE (scope, line-kind) facts and carry `validated_by: none`
 * on their own schema rows as well — `scope`/`kind` below is the JOIN back
 * to them, so a consumer that meets a `none` cell can find out why without
 * a second mechanism. The other two are not row facts at all (a `config`
 * cascade's RESOLUTION is a whole-file question; an `ext` tree's contents
 * have no rows to carry a column), which is exactly why this is a sibling
 * SECTION and not a wider `validated_by` cell. */
typedef struct {
    const char *surface;
    const char *scope;
    const char *kind;
    const char *reason;
} SurfaceRow;

static const SurfaceRow g_surface[] = {
    /* [DD-13b.W23.3] THE SENTENCE USED TO END MID-CLAUSE — "the 64-hex-"
     * "digit SYNTAX is" — and what it was about to claim was false as
     * well as unfinished: this parser recognises every expectation kind
     * as `value: case` and reads NONE of them, so it checks neither the
     * digest nor its spelling. The harness legs check both, which is
     * where the claim belongs. A declared non-coverage that overstates
     * its own coverage is worse than one that does not exist. */
    { "subject-content", "block", "m/n/ms/ns/mc",
      "an expectation line is recognised and never read here, so neither "
      "a subject's sha256 digest nor its 64-hex spelling is checked by "
      "this parser; both are the harness legs' (docs/spec/rxt_format.md)" },
    { "pattern-text", "block", "pattern/pattern-esc",
      "the dump is parse-only; pattern text is the compiler's" },
    { "config-resolution", "", "",
      "`--list-source` reports the file AS WRITTEN; which settings a block "
      "ends up under is `--source`'s own resolution and is not a "
      "(scope, line-kind) fact" },
    { "ext-tree-contents", "", "",
      "the contents of an `ext` tree are never schema-checked and never "
      "interpreted; reason: semantically uninterpreted by design (the "
      "graduation rule, format_design §2.27.3). The `ext` OPENER's own row "
      "is ordinary — the structure is checked, the content by nobody" },
};

char *pcrec_rxt_schema_tsv(void)
{
    StrBuf sb = {0};
    size_t n = 0;
    const RxtSchemaRow *rows = pcrec_rxt_schema_rows(&n);

    sb_puts(&sb,
        "# pcrec .rxt FORMAT SCHEMA (docs/spec/rxt_format.md,\n"
        "# docs/spec/table_contract.md; the SEVENTH registry dump,\n"
        "# [DD-13b.W23.1]). One row per (scope, line-kind), walked out of\n"
        "# src/parse/rxt_schema.def — the same table the parser enforces.\n"
        "#\n"
        "# THE THREE STRUCTURE-LAYER PARAMETERS are column values, not\n"
        "# separate queries: a generic reader that wants to recover a file's\n"
        "# tree from syntax alone selects\n"
        "#   opens_group = true                   (S2, the block-opener set)\n"
        "#   value = prose AND children = prose   (S3, prose-region openers)\n"
        "#   children = tree                      (the OPEN SUBTREE)\n"
        "# and needs no other keyword knowledge. See rxt_format.md's lexical\n"
        "# rules for what each one does.\n"
        "#\n"
        "# value: the value shape (none/token/int/line/prose/list/pair/\n"
        "#   subject/case/qualified-line/raw).\n"
        "# children: what may be INDENTED under the line — none, prose (the\n"
        "#   indented lines ARE the value), tree (parsed, never validated,\n"
        "#   never interpreted), or the named scope they live in.\n"
        "# cardinality: one | at-most-one | repeat | accumulate.\n"
        "# constraints: `;`-separated, each `<kind> [argument]` from the\n"
        "#   seven-kind closed vocabulary.\n"
        "# source: format (pcrec declares the row) | file (a `vocabulary`\n"
        "#   line in the .rxt file declares it).\n"
        "# validated_by: pcrec | all-readers (pcrec, tests/harness/run.sh\n"
        "#   and tests/harness/verify_rxt.py, with a fixture proving they\n"
        "#   agree) | none (see #section surface for the reason).\n"
        "# wave: which delivery introduces the kind. A row whose wave is\n"
        "#   above this build's is RECOGNISED and refused BY NAME as NOT IN\n"
        "#   THIS BUILD, never as an unknown token. The one exception is the\n"
        "#   RESERVED sentinel (`# wave-reserved:` below): no delivery\n"
        "#   introduces such a kind, and it refuses BY NAME as RESERVED.\n"
        "#section schema\n"
        "#scope\tkind\tvalue\topens_group\tchildren\tcardinality"
        "\tconstraints\tsource\tvalidated_by\twave\n");

    for (size_t i = 0; i < n; i++) {
        const RxtSchemaRow *r = &rows[i];
        sb_printf(&sb, "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%d\n",
                  pcrec_rxt_scope_name(r->scope),
                  r->kind,
                  pcrec_rxt_value_name(r->value),
                  r->opens_group ? "true" : "false",
                  pcrec_rxt_children_name(r->children),
                  pcrec_rxt_cardinality_name(r->cardinality),
                  r->constraints,
                  pcrec_rxt_row_source_name(r->source),
                  pcrec_rxt_validated_by_name(r->validated_by),
                  r->wave);
    }

    sb_puts(&sb,
        "#\n"
        "# THE DECLARED NON-COVERAGE. Each row names something this schema\n"
        "# deliberately does NOT validate, and why. Two of the four are also\n"
        "# (scope, kind) facts and carry `validated_by: none` on their own\n"
        "# rows above — `scope`/`kind` here is the join back to them; the\n"
        "# other two are whole-file or content questions with no row to\n"
        "# carry a column, which is why this is a section and not a wider\n"
        "# cell.\n"
        "#section surface\n"
        "#surface\tscope\tkind\treason\n");
    for (size_t i = 0; i < sizeof g_surface / sizeof *g_surface; i++)
        sb_printf(&sb, "%s\t%s\t%s\t%s\n", g_surface[i].surface,
                  g_surface[i].scope, g_surface[i].kind, g_surface[i].reason);

    /* THE COMPILE-TIME ROW TOTAL, printed LAST and as a comment so it is
     * not a row of any section (w23_impl DECIDED (12), r59-A-M7).
     *
     * A check that ITERATES this dump's rows and probes each one's
     * behaviour cannot see a row that is MISSING: its population is defined
     * by the thing it is checking, so a truncated table agrees with it by
     * construction. This number comes from `sizeof` over the `.def`'s own
     * expansion — not from a count of what was printed, which would be the
     * same defect one line later — so W23-S3 asserts `rows printed ==
     * schema-rows` and a dropped row fails the check rather than shrinking
     * its population. The alternative, a pinned literal with a re-pin
     * ritual, is a number in a second place and this delivery has enough of
     * those. */
    sb_printf(&sb, "# schema-rows: %zu\n", pcrec_rxt_schema_nrows());
    sb_printf(&sb, "# wave-built: %d\n", PCREC_RXT_WAVE_BUILT);
    /* The RESERVED sentinel is printed for the same reason wave-built is:
     * a check that partitions the rows by wave needs both boundaries from
     * the dump itself, or it hardcodes a copy of internal.h's constant —
     * the control-sharing-a-source shape one number over. */
    sb_printf(&sb, "# wave-reserved: %d\n", PCREC_RXT_WAVE_RESERVED);

    return sb_take(&sb);
}
