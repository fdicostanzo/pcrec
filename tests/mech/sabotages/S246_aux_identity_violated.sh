# S246 — [DD-13b.W23.4] W23-S6 (format_design.md §2.27.3 clause 5): TWO
# VARIANTS, because the clause names two STRUCTURAL routes an aux body's
# CONTENT could reach pcrec's other outputs through, and each is a
# one-line corruption of shipped code rather than a feature anybody would
# write on purpose (r59-A-M2(c)'s own reason revision 1 declined this row
# and then §3.4 refuted two paragraphs later).
#
# (a) AN OPENER-ROW CARDINALITY: `ext`'s rows flip from `cardinality:
#     repeat` to `at-most-one`. `aux_identity_edited.rxtin` carries TWO
#     `ext` blocks in one pattern block on purpose (`bench` and `other`),
#     so the plant turns W23-S6's own second fixture into a hard parse
#     refusal — W23-S6 arm 1 fails naming "--list-source failed".
#
# (b) A DERIVED COUNT: `section_count()`'s own helper (this file) is
#     corrupted to fold an aux tree's `ext` OPENER rows into the
#     main-table population it reports for `want=""` — the shape §3.4's
#     own example names ("count aux openers into a_blocks"), landed
#     against the SHARED helper multiple W23.4 checks route through
#     rather than against the corpus-only `a_blocks` snippet, which the
#     corpus's own zero `ext` population cannot arm at all. The
#     `aux_deep_tree.rxtin` fixture's own `ext bench` opener is what
#     makes this reachable: `aux/deep-tree`'s main-table assertion moves
#     from 1 to 2 the moment the plant lands.
SAB_ID="S246-aux-identity-violated"
SAB_FILE="src/parse/rxt_schema.def"
SAB_SUITES="rxtsource"
SAB_DESC="(a) 'ext' loses its repeat cardinality, refusing a second ext block in one scope; (b) the section-row counting helper folds an aux tree's own ext-opener rows into the main-table population, so an aux edit moves a count it must not"
SAB_DOC_FIGURE="docs/design/dd13_format/format_design.md §2.27.3 clause 5; w23_impl.md §3.4/§3.5 (S246, revision 1.1)"
SAB_COUNT=1
# REACH: the row rests on `ext` declaring `cardinality: repeat` at BOTH
# scopes on the clean tree.
SAB_REACH='"$PCREC" --list-schema | awk -F"\t" "\$2 == \"ext\" { print \$6 }" | sort -u'
SAB_REACH_EXPECT='repeat'
SAB_BEFORE='PCREC_RXT_SCHEMA(BLOCK, "ext",        TOKEN,     0, TREE,       REPEAT,      "",                     FORMAT, PCREC, 23)'
SAB_AFTER='/* SABOTAGE S246 (1 of 2): the block-scope ext body loses repeat. */
PCREC_RXT_SCHEMA(BLOCK, "ext",        TOKEN,     0, TREE,       AT_MOST_ONE, "",                     FORMAT, PCREC, 23)'
SAB_FILE2="tests/rxtsource/run_rxtsource_tests.sh"
SAB_BEFORE2='        cur == want { n++ }'
SAB_AFTER2='        cur == want || (want == "" && cur == "aux" && $6 == "ext") { n++ }   # SABOTAGE S246 (2 of 2)'
SAB_COUNT2=1
