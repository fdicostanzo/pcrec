# S205 (r46sem finding 1, the panel's one BLOCKER) — tests/harness/run.sh's
# `rxt_escape` fallback re-derives a control byte's `\xNN` rendering from
# its POSITION in the loop rather than from the byte's own numeric VALUE.
#
# THIS IS THE EXACT CLASS OF DEFECT THE PANEL FOUND, reproduced against the
# fix rather than against the historical CTRL-table shape it replaced. The
# original bug (`index(CTRL, c)` — a byte's INDEX into a side table read as
# if it were the byte's own VALUE) coincided with the truth only for
# 0x01..0x08, and turned VT (0x0b) into a decoded TAB. The fix deleted the
# side table entirely and derives the escape straight from the byte's own
# ordinal (`printf -v n '%d' "'$c"`); this plant substitutes the loop's
# POSITION for that ordinal, which is the same "index confused with value"
# shape one line later. `d` — a repeated character three positions after
# the first control byte at index... the point is exactly that nobody
# should have to reason about which position lines up with which value:
# the check must catch it regardless.
#
# CAUGHT BY tests/rxtsource/'s sem1 witness (ctrl_bytes.rxtin): the
# sabotaged tree escapes VT/FF/DEL by their LOOP POSITION rather than their
# byte value, so leg B's dump disagrees with legs A and C, which still
# derive the correct `\x0b`/`\x0c`/`\x7f` render from the byte itself.
SAB_ID="S205-rxt-escape-index-not-value"
SAB_FILE="tests/harness/run.sh"
SAB_SUITES="rxtsource harness"
SAB_DESC="rxt_escape's fallback derives a control byte's \\xNN rendering from the loop's POSITION instead of the byte's own numeric value"
SAB_REACH='cp "$TREE/tests/rxtsource/fixtures/ctrl_bytes.rxtin" "$REACH_TMP/ctrl_bytes.rxt" && bash "$TREE/tests/harness/run.sh" --dump "$REACH_TMP/ctrl_bytes.rxt"'
SAB_REACH_EXPECT='a\x0bb\x0cc\x7fd'
SAB_COUNT=1
SAB_BEFORE="                printf -v n '%d' \"'\$c\""
SAB_AFTER="                n=\$i   # SABOTAGE S205: position substituted for the byte's own value"
SAB_DOC_FIGURE="predicted: rxtsource sem1 check goes red on ctrl_bytes.rxt (leg A/C escape VT/FF/DEL correctly, leg B does not); run_sabotage_matrix.sh S205 is the canonical figure, still owed"
