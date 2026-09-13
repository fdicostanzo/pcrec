# S244 — [DD-13b.W23.1] THE PROSE PAIR IS BROKEN IN ONE COLUMN, AND THE
# ROW EXISTS TWICE BECAUSE ONE OF THE TWO PLANTS IS THE WHOLE ARGUMENT
# FOR READING A PAIR AT ALL.
#
# Structure-layer parameter 2 (format_design §1.2.1) is `value: prose` AND
# `children: prose`, read together. A row failing either half stops
# opening an S3 opaque region, so a `description |` becomes the literal
# two-byte value `|` and the indented lines below it become a structure
# error — which the prose fixtures see.
#
# PLANT (a), the obvious one: flip `value` from PROSE to LINE.
# PLANT (b), THE ONE THAT PAYS: flip `children` from PROSE to NONE. If the
# structure layer read `value` ALONE, (b) would change NOTHING a reader
# can observe — the region still opens, its lines are still bytes, and
# bytes reach no validity check — so a normative column would carry a
# corruption with NO DETECTOR ANYWHERE, which is the K35 shape this row
# exists to prevent. Reading the pair is what makes (b) visible, and (b)
# is what makes reading the pair worth the sentence.
#
# The row ships plant (b) for that reason. Plant (a) is recorded here and
# in the lane report so the pair's other half is not left implicit.
#
# WHAT SEES IT: `tests/rxtsource/run_rxtsource_tests.sh`'s
# `prose_hash.rxt`, `prose_ragged.rxt` and `prose_paragraph_break.rxt` —
# each asserts the DECODED VALUE of a region, so a reader that stopped
# opening one fails on the value rather than on a verdict. W23-S3 arm 3b
# fires too, from the dump's own claim.
SAB_ID="S244-prose-pair-broken"
SAB_FILE="src/parse/rxt_schema.def"
SAB_SUITES="rxtsource"
SAB_DESC="a prose row's children column is flipped from prose to none, so the value/children PAIR no longer qualifies the kind as prose-region-opening and a block scalar stops opening a region -- the plant that changes nothing observable if the structure layer reads value alone"
SAB_DOC_FIGURE="docs/design/dd13_format/format_design.md 1.2.1's parameter table (parameter 2 is the PAIR); docs/spec/rxt_format.md's lexical rules"
SAB_COUNT=1
# REACH: the row rests on there BEING a prose-region-opening kind this
# build implements. If the prose pair's live population goes to zero the
# plant has nothing to break and must score UNREACHED rather than pass.
SAB_REACH='"$PCREC" --list-schema | awk -F"\t" "\$1 == \"file\" && \$2 == \"description\" { print \$3 \"+\" \$5 }"'
SAB_REACH_EXPECT='prose+prose'
SAB_BEFORE='PCREC_RXT_SCHEMA(FILE, "description", PROSE, 0, PROSE,      AT_MOST_ONE, "", FORMAT, PCREC,       1)'
SAB_AFTER='/* SABOTAGE S244 plant (b): the PAIR is broken in the children column
 * only. With `value` alone read this edit is invisible everywhere. */
PCREC_RXT_SCHEMA(FILE, "description", PROSE, 0, NONE,       AT_MOST_ONE, "", FORMAT, PCREC,       1)'
