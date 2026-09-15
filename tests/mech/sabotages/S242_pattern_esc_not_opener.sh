# S242 — [DD-13b.W23.4] S-R4a (w23_impl.md §3.5): `pattern-esc` REMOVED
# FROM `opens_group`.
#
# The structure layer's OWN fixture: on the shipped schema `pattern` and
# `pattern-esc` are the block-opener set (S2), so a `pattern-esc` line
# always starts a NEW block. Under this plant `pattern-esc` stops
# opening anything at all — and since the FIRST `pattern-esc` line in a
# file only ever reaches BLOCK scope THROUGH the opener transition
# (`f->base == FILE` maps to BLOCK exclusively via `group_scope`'s
# FILE->BLOCK mapping, S2's own gate), a file whose first block is
# opened with `pattern-esc` refuses OUTRIGHT — MEASURED, not the silent
# misattribution a first reading predicts: `[unknown-token-in-scope]
# 'pattern-esc' is not a file-level directive`, because with no opener
# match `pattern-esc` is looked up as an ordinary FILE-scope row, which
# does not exist (it is BLOCK-scope only).
#
# THE DETECTOR IS `opener_pattern_esc_pair.rxtin` ([DD-13b.W23.4]'s own
# fixture) REFUSING TO PARSE AT ALL — a total refusal is the loudest
# possible symptom of a lost opener, and it is a stronger detector than
# the block_line-drift a first reading predicts (that drift is real for
# a SECOND `pattern-esc` line, once a file has some other way into BLOCK
# scope first, but this fixture's own first block already fails before
# that shape is ever reached).
SAB_ID="S242-pattern-esc-not-opener"
SAB_FILE="src/parse/rxt_schema.def"
SAB_SUITES="rxtsource"
SAB_DESC="'pattern-esc' loses opens_group, so a second pattern-esc line inside an already-open block is consumed as an ordinary directive of the FIRST block instead of starting a second one, and every case row after it reports the wrong block_line"
SAB_DOC_FIGURE="docs/design/dd13_format/w23_impl.md §3.5 S-R4a; format_design.md §1.2.1 (structure-layer parameter 1, opens_group)"
SAB_COUNT=1
# REACH: the row rests on `pattern-esc` declaring opens_group=true on the
# clean tree — the schema's own dump says so directly.
SAB_REACH='"$PCREC" --list-schema | awk -F"\t" "\$2 == \"pattern-esc\" { print \$4 }"'
SAB_REACH_EXPECT="true"
SAB_BEFORE='PCREC_RXT_SCHEMA(BLOCK, "pattern-esc",    RAW,   1, NONE,  REPEAT,      "", FORMAT, NONE,       23)'
SAB_AFTER='PCREC_RXT_SCHEMA(BLOCK, "pattern-esc",    RAW,   0, NONE,  REPEAT,      "", FORMAT, NONE,       23)   /* SABOTAGE S242 */'
