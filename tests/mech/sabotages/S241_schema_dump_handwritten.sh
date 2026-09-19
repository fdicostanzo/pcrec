# S241 — [DD-13b.W23.1] `--list-schema` PRINTS A HAND-WRITTEN TABLE
# INSTEAD OF WALKING THE ENFORCED ONE, AND THE COPY DISAGREES.
#
# The schema's whole claim is ONE DERIVATION, TWO READERS: the parser
# enforces `src/parse/rxt_schema.def` and the dump walks the same rows
# through `pcrec_rxt_schema_rows()`, so a dump that disagrees with the
# parser is not expressible. This row makes it expressible, and the plant
# is deliberately NOT a faithful hand-written copy: a faithful copy
# detects only DRIFT, and a sabotage row must fail on the tree it is
# planted into rather than on a later edit somebody else makes.
#
# THE DISAGREEMENT IS ON ONE ROW AND ONE LIVE COLUMN. The dump reports the
# block `name` row as `cardinality: repeat` while the parser (reading the
# real table) refuses a second `name` line. Nothing about the compile
# changes; what changes is that a consumer fetching the schema is told
# something the parser does not do.
#
# WHAT SEES IT: `tests/rxtsource/run_rxtsource_tests.sh`'s W23-S3 ARM 5,
# which drives the BEHAVIOUR each row's cardinality claims — in BOTH
# directions, per row — rather than comparing the dump to the table. The
# direction matters: an arm that only checked "at-most-one rows refuse a
# second" would MISS this plant entirely, because the plant moves a row
# OUT of the at-most-one set. The repeat half is what fires.
#
# WHY THE DETECTOR IS NOT "the dump equals the table": that is the same
# source twice (docs/dev/learnings.md §3), and it is the one comparison a
# check over this dump must never make.
SAB_ID="S241-schema-dump-handwritten"
SAB_FILE="src/dump/schema_dump.c"
SAB_SUITES="rxtsource"
SAB_DESC="--list-schema hand-writes one row instead of walking the enforced table, and the hand-written row's cardinality disagrees with what the parser enforces, so a consumer fetching the schema is told something pcrec does not do"
SAB_DOC_FIGURE="docs/spec/rxt_format.md's schema section; docs/design/dd13_format/format_design.md 2.25.1 (one table, one reader, one dump)"
SAB_COUNT=1
# REACH: the row rests on the dump emitting a `cardinality` column at all,
# and on the block `name` row being in it. If either goes, this row is
# certifying nothing and must say so rather than scoring.
SAB_REACH='"$PCREC" --list-schema | awk -F"\t" "\$1 == \"block\" && \$2 == \"name\" { print \$6 }"'
SAB_REACH_EXPECT='at-most-one'
# [REVW.1 wave 1, 2026-09-18] RE-AIMED. The dump's row emission moved from
# one `sb_printf` with a ten-conversion format to the text layer's `sb_row`
# over a named cell array (src/core/sb.c), so the anchor's quoted text no
# longer exists. RE-DERIVED from the live source, NOT weakened: the plant is
# the same one column on the same one row, spelled against the cell array
# instead of the vararg list, and it carries the rest of the array through
# verbatim exactly as the old form carried the rest of the format.
# INTENT RE-VERIFIED by applying it (the house rule, and the reason S10's
# re-anchor is the worked example): under the plant `--list-schema` reports
# `block name` as `cardinality: repeat` while the parser still refuses a
# second `name` line, which is the disagreement this row is named for. The
# reach probe is UNCHANGED and still reads the shipped `at-most-one`.
SAB_BEFORE='                                pcrec_rxt_children_name(r->children),
                                pcrec_rxt_cardinality_name(r->cardinality),'
SAB_AFTER='                                pcrec_rxt_children_name(r->children),
                                /* SABOTAGE S241: one row is hand-written,
                                 * and it disagrees. */
                                (r->scope == RXT_SCOPE_BLOCK && !strcmp(r->kind, "name"))
                                    ? "repeat"
                                    : pcrec_rxt_cardinality_name(r->cardinality),'
