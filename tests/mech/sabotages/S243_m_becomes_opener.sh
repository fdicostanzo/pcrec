# S243 — [DD-13b.W23.4] S-R4b (w23_impl.md §3.5): A THIRD MEMBER ADDED TO
# `opens_group` (`m`).
#
# A DIFFERENT plant and a DIFFERENT detector from S242 — this row is why
# S-R4a and S-R4b are split rather than bundled (revision 3.1 bundled
# them and the pattern-esc half went SILENT: the opener set is a
# first-match-wins scope-free query, and a duplicate `pattern` row
# changes no answer at all, so a row planting two things where one does
# nothing scores DETECTED on the strength of the other alone. Splitting
# them is the only way to know THIS half is pulling its own weight).
#
# The mechanism: `pcrec_rxt_schema_opener` is a SCOPE-FREE kind lookup,
# and the code that consults it maps `f->base` — the ROOT frame's base,
# which stays FILE for the frame's whole lifetime, block after block —
# through `pcrec_rxt_schema_group_scope`. So making `m` an opener does
# not merely add a new construct at FILE scope; because `f->base` is
# FILE at every ordinary case-line position too, EVERY `m` line anywhere
# in the file starts closing and reopening "blocks".
#
# THE DETECTOR IS THE BLOCK COUNT AND `#section cases`'s OWN POPULATION
# (`opener_m_not_opener.rxtin`, [DD-13b.W23.4]'s own fixture): on the
# clean tree the file is ONE `pattern` block with two `m` case lines — 1
# main-table row, 2 `#section cases` rows. Under the plant each `m` line
# closes the block above it and opens a new one: 3 main-table `pattern`
# rows (`a`, then each `m` line's own rest-of-line text as a bogus
# "pattern"), and ZERO `#section cases` rows, because every `m` line was
# consumed as a block opener rather than dispatched as a case.
SAB_ID="S243-m-becomes-opener"
SAB_FILE="src/parse/rxt_schema.def"
SAB_SUITES="rxtsource"
SAB_DESC="'m' gains opens_group, so every 'm' case line anywhere in a pattern block closes the block above it and opens a new one — a file with 1 block and 2 case lines dumps as 3 blocks and 0 cases"
SAB_DOC_FIGURE="docs/design/dd13_format/w23_impl.md §3.5 S-R4b; format_design.md §1.2.1 (structure-layer parameter 1, opens_group)"
SAB_COUNT=1
# REACH: the row rests on `m` declaring opens_group=false on the clean
# tree — the schema's own dump says so directly.
SAB_REACH='"$PCREC" --list-schema | awk -F"\t" "\$2 == \"m\" { print \$4 }"'
SAB_REACH_EXPECT="false"
SAB_BEFORE='PCREC_RXT_SCHEMA(BLOCK, "m",              CASE,  0, NONE,  REPEAT,      "", FORMAT, NONE,        1)'
SAB_AFTER='PCREC_RXT_SCHEMA(BLOCK, "m",              CASE,  1, NONE,  REPEAT,      "", FORMAT, NONE,        1)   /* SABOTAGE S243 */'
